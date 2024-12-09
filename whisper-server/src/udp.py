import socket
import logging

logging.basicConfig(
    filename='log/udp_server.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ServidorUDP:
    def __init__(self, host="192.168.1.66", port=12345):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((host, port))
        self.running = True
        self.host = host
        self.port = port
        logging.info(f"🎧 Servidor UDP iniciado en {host}:{port}")
        print(f"🎧 Servidor UDP escuchando en {host}:{port}")

    def send_command(self, ip, port, comando):
        """
        Envía un comando hexadecimal por UDP
        comando: debe ser un valor entero (ej: 0x0501, 0x0500)
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Convertir el comando a bytes (2 bytes, big endian)
            comando_bytes = comando.to_bytes(2, byteorder='big')
            sock.sendto(comando_bytes, (ip, int(port)))
            
            logging.info(f"✅ Comando 0x{comando:04X} enviado a {ip}:{port}")
            print(f"✅ Comando 0x{comando:04X} enviado a {ip}:{port}")
            
        except Exception as e:
            error_msg = f"❌ Error enviando comando UDP: {e}"
            logging.error(error_msg)
            print(error_msg)
        finally:
            sock.close()

    def receive_udp(self, ip='192.168.1.65', port=12345, buffer_size=1024):
        """
        Recibe paquetes UDP en la IP y puerto especificados de forma bloqueante
        """
        try:
            # Crear socket UDP
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((ip, port))
            logging.info(f"Escuchando paquetes UDP en {ip}:{port}")
            print(f"Escuchando paquetes UDP en {ip}:{port}")
            
            # Esperar datos (bloqueante)
            data, addr = sock.recvfrom(buffer_size)
            logging.info(f"Datos recibidos desde {addr}: {data}")
            print(f"Datos recibidos desde {addr}: {data}")
            return data, addr
                
        except Exception as e:
            logging.error(f"Error en recepción UDP: {e}")
            return None, None
        finally:
            sock.close()

    def stop(self):
        """Detiene el servidor UDP"""
        self.running = False
        self.sock.close()
    logging.info("Servidor UDP detenido")
    print("Servidor UDP detenido")
