import socket
import subprocess
import ipaddress
import platform
import concurrent.futures
import re

class RedScanner:
    def __init__(self):
        self.dispositivos_red = []

    def obtener_interfaces_red(self):
        """Obtiene interfaces de red de manera multiplataforma"""
        interfaces = {}
        sistema = platform.system()

        try:
            if sistema == 'Windows':
                # Usar comando ipconfig para Windows
                salida = subprocess.check_output(['ipconfig'], universal_newlines=True)
                
                # Expresiones regulares para extraer IPs
                adaptadores = re.findall(r'Adaptador de ([^\n:]+):', salida)
                ips = re.findall(r'   Direcci[oó]n IPv4\. \. \. \. \. \. \. \. \. \.: (\d+\.\d+\.\d+\.\d+)', salida)
                mascaras = re.findall(r'   M[áa]scara de subred\. \. \. \. \. \. \. \.: (\d+\.\d+\.\d+\.\d+)', salida)
                
                for i in range(len(adaptadores)):
                    if len(ips) > i and len(mascaras) > i and not ips[i].startswith('127.'):
                        interfaces[adaptadores[i]] = {
                            'ip': ips[i],
                            'mascara': mascaras[i]
                        }
            
            elif sistema in ['Linux', 'Darwin']:
                # Usar comando ip o ifconfig para Linux/macOS
                try:
                    salida = subprocess.check_output(['ip', 'addr'], universal_newlines=True)
                    # Extraer IPs y nombres de interfaz
                    for linea in salida.split('\n'):
                        match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)/(\d+)', linea)
                        if match and not match.group(1).startswith('127.'):
                            interfaces[linea.split(':')[1].strip()] = {
                                'ip': match.group(1),
                                'mascara': str(ipaddress.IPv4Network(f"0.0.0.0/{match.group(2)}").netmask)
                            }
                except FileNotFoundError:
                    # Alternativa con ifconfig
                    salida = subprocess.check_output(['ifconfig'], universal_newlines=True)
                    for bloque in salida.split('\n\n'):
                        match_ip = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', bloque)
                        match_mascara = re.search(r'netmask (\d+\.\d+\.\d+\.\d+)', bloque)
                        if match_ip and match_mascara and not match_ip.group(1).startswith('127.'):
                            interfaces[bloque.split(':')[0]] = {
                                'ip': match_ip.group(1),
                                'mascara': match_mascara.group(1)
                            }
            
        except Exception as e:
            print(f"Error detectando interfaces: {e}")
        
        return interfaces

    def calcular_rango_red(self, ip, mascara):
        """Calcula el rango de IPs para escanear"""
        try:
            red = ipaddress.IPv4Network(f"{ip}/{mascara}", strict=False)
            # Limitar a 50 IPs para evitar escaneos muy largos
            return [str(ip) for ip in list(red.hosts())[:50]]
        except Exception as e:
            print(f"Error calculando rango de red: {e}")
            return []

    def ping_ip(self, ip, timeout=1):
        """Verifica si la IP responde a un ping"""
        sistemas = {
            'Windows': lambda ip: subprocess.run(['ping', '-n', '2', '-w', str(timeout*1000), ip], 
                                                 stdout=subprocess.PIPE, 
                                                 stderr=subprocess.PIPE).returncode == 0,
            'Linux': lambda ip: subprocess.run(['ping', '-c', '2', '-W', str(timeout), ip], 
                                               stdout=subprocess.PIPE, 
                                               stderr=subprocess.PIPE).returncode == 0,
            'Darwin': lambda ip: subprocess.run(['ping', '-c', '2', '-t', str(timeout), ip], 
                                                stdout=subprocess.PIPE, 
                                                stderr=subprocess.PIPE).returncode == 0
        }

        sistema = platform.system()
        ping_func = sistemas.get(sistema)
        
        return ping_func(ip) if ping_func else False

    def obtener_info_dispositivo(self, ip):
        """Obtiene información adicional de un dispositivo"""
        try:
            # Intentar resolver nombre de host
            try:
                nombre_host = socket.gethostbyaddr(ip)[0]
            except:
                nombre_host = "Desconocido"

            # Intentar obtener MAC (multiplataforma)
            try:
                # Método para Windows
                if platform.system() == 'Windows':
                    salida = subprocess.check_output(['arp', '-a', ip], universal_newlines=True)
                    mac = re.search(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', salida)
                    mac = mac.group(0) if mac else "N/A"
                # Método para Linux/macOS
                else:
                    salida = subprocess.check_output(['arp', '-n', ip], universal_newlines=True)
                    mac = re.search(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', salida)
                    mac = mac.group(0) if mac else "N/A"
            except:
                mac = "N/A"

            return {
                'ip': ip,
                'nombre': nombre_host,
                'mac': mac
            }
        except Exception as e:
            return None

    def escanear_red(self):
        """Escanea dispositivos en todas las redes disponibles"""
        self.dispositivos_red = []
        interfaces = self.obtener_interfaces_red()

        print("\n🌐 Interfaces de Red Detectadas:")
        for nombre, detalles in interfaces.items():
            print(f"- {nombre}: IP {detalles['ip']} | Máscara {detalles['mascara']}")

        for interfaz, detalles in interfaces.items():
            print(f"\n🔍 Escaneando red de {interfaz} ({detalles['ip']})...")
            
            # Calcular rango de IPs
            rango_ips = self.calcular_rango_red(detalles['ip'], detalles['mascara'])
            
            # Escaneo concurrente
            with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                # Primero hacer ping
                futures_ping = {executor.submit(self.ping_ip, ip): ip for ip in rango_ips}
                
                ips_activas = []
                for future in concurrent.futures.as_completed(futures_ping):
                    ip = futures_ping[future]
                    if future.result():
                        ips_activas.append(ip)
                
                # Obtener información de dispositivos
                futures_info = {executor.submit(self.obtener_info_dispositivo, ip): ip for ip in ips_activas}
                
                for future in concurrent.futures.as_completed(futures_info):
                    dispositivo = future.result()
                    if dispositivo:
                        self.dispositivos_red.append(dispositivo)

        return self.dispositivos_red

    def listar_dispositivos(self):
        """Lista los dispositivos encontrados en la red"""
        if not self.dispositivos_red:
            print("❌ No se encontraron dispositivos.")
            return None

        print("\n🌐 Dispositivos en la red:")
        for i, disp in enumerate(self.dispositivos_red, 1):
            print(f"{i}. IP: {disp['ip']} | Nombre: {disp['nombre']} | MAC: {disp['mac']}")
        
        return self.dispositivos_red

def main():
    scanner = RedScanner()
    scanner.escanear_red()
    scanner.listar_dispositivos()

if __name__ == "__main__":
    main()