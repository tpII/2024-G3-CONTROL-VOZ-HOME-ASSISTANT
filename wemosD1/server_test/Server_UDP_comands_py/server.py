import socket
import time
from datetime import datetime
import sys
import wave
import numpy as np
import threading
import keyboard

class ServidorUDP:
    def __init__(self):
        # Configuración global
        self.CONFIG = {
            'UDP_IP': "0.0.0.0",
            'UDP_PORT': 12345,
            'SAMPLE_RATE': 15000,
            'RECORDING_DURATION': 30  # segundos
        }
        
        # Variables de estado
        self.running = False
        self.paused = False
        self.collected_data = []
        self.start_time = None
        self.local_ips = socket.gethostbyname_ex(socket.gethostname())[2]
        
        # Control de dispositivos conectados
        self.dispositivos_conectados = {}  # {(ip, puerto): último_tiempo_visto}
        self.tiempo_timeout = 5  # segundos sin datos para considerar desconectado
        
        # Inicializar socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.CONFIG['UDP_IP'], self.CONFIG['UDP_PORT']))
        
    def print_header(self):
        """Muestra la información inicial del servidor"""
        print("\n" + "=" * 50)
        print("💡 SERVIDOR UDP - MONITOREO DE DATOS 💡")
        print("=" * 50 + "\n")
        print("📍 Escuchando en las siguientes IPs:")
        for ip in self.local_ips:
            print(f"📍 {ip}:{self.CONFIG['UDP_PORT']}")
        print(f"📡 Puerto de escucha: {self.CONFIG['UDP_PORT']}")
        print("\nComandos disponibles (activos solo con dispositivos conectados):")
        print("'p' - Pausar/Reanudar grabación")
        print("'q' - Finalizar grabación actual y salir")
        print("'s' - Salir sin guardar")
        print("'z' - Enviar comando 0x0501 (D5 alto)")
        print("'x' - Enviar comando 0x0500 (D5 bajo)")
        print("'c' - Enviar comando 0xFFFF (consultar estado)")
        print("\n" + "=" * 50 + "\n")

    def actualizar_dispositivos(self, addr):
        """Actualiza la lista de dispositivos conectados"""
        self.dispositivos_conectados[addr] = time.time()
        
    def limpiar_dispositivos_inactivos(self):
        """Elimina dispositivos que no han enviado datos en el tiempo_timeout"""
        tiempo_actual = time.time()
        dispositivos_a_eliminar = []
        
        for addr, ultimo_tiempo in self.dispositivos_conectados.items():
            if tiempo_actual - ultimo_tiempo > self.tiempo_timeout:
                dispositivos_a_eliminar.append(addr)
                
        for addr in dispositivos_a_eliminar:
            del self.dispositivos_conectados[addr]
            print(f"\n📴 Dispositivo desconectado: {addr}")

    def hay_dispositivos_conectados(self):
        """Verifica si hay dispositivos conectados"""
        self.limpiar_dispositivos_inactivos()
        return len(self.dispositivos_conectados) > 0

    def create_wav_file(self, filename):
        """Crear archivo WAV a partir de los datos recolectados"""
        if not self.collected_data:
            return
            
        normalized_data = np.array(self.collected_data, dtype=np.int16)
        normalized_data = ((normalized_data-512) * 64)
        
        with wave.open(filename, 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.CONFIG['SAMPLE_RATE'])
            wav_file.writeframes(normalized_data.tobytes())
            
    def enviar_comando(self, comando):
        """Envía un comando a todos los dispositivos conectados"""
        if not self.hay_dispositivos_conectados():
            print("\n⚠️  No hay dispositivos conectados para enviar comandos")
            return
            
        try:
            cmd_bytes = comando.to_bytes(2, byteorder='big')
            for addr in self.dispositivos_conectados.keys():
                self.sock.sendto(cmd_bytes, addr)
                print(f"\n📤 Comando 0x{comando:04X} enviado a {addr}")
                
            if comando == 0xFFFF:
                # Esperar respuestas para el comando de estado
                self.sock.settimeout(1.0)  # timeout de 1 segundo para respuestas
                try:
                    for _ in range(len(self.dispositivos_conectados)):
                        data, addr = self.sock.recvfrom(16)
                        self.procesar_estado_pines(data, addr)
                except socket.timeout:
                    print("⚠️  Algunos dispositivos no respondieron")
                finally:
                    self.sock.settimeout(None)
                    
        except Exception as e:
            print(f"❌ Error al enviar comando: {e}")
            
    def procesar_estado_pines(self, data, addr):
        """Procesa la respuesta del comando de estado de pines"""
        print(f"\n📊 Estado de pines del dispositivo {addr}:")
        for i in range(0, len(data), 2):
            num_pin = data[i]
            estado = data[i + 1]
            print(f"  Pin {num_pin}: {'Alto' if estado else 'Bajo'}")
            
    def manejar_teclado(self):
        """Maneja los eventos de teclado"""
        while self.running:
            if keyboard.is_pressed('p'):
                self.paused = not self.paused
                print("\n⏯️  Grabación {}".format("pausada" if self.paused else "reanudada"))
                time.sleep(0.2)
                
            elif keyboard.is_pressed('q'):
                self.running = False
                print("\n⏹️  Finalizando grabación...")
                break
                
            elif keyboard.is_pressed('s'):
                self.running = False
                self.collected_data = []
                print("\n🚫 Saliendo sin guardar...")
                break
                
            elif keyboard.is_pressed('z'):
                self.enviar_comando(0x0501)
                time.sleep(0.2)
                
            elif keyboard.is_pressed('x'):
                self.enviar_comando(0x0500)
                time.sleep(0.2)
                
            elif keyboard.is_pressed('c'):
                self.enviar_comando(0xFFFF)
                time.sleep(0.2)
                
    def mostrar_progreso(self, elapsed_time):
        """Muestra la barra de progreso de la grabación y dispositivos conectados"""
        if not self.paused:
            progress_bar = '[' + '=' * elapsed_time + ' ' * (self.CONFIG['RECORDING_DURATION'] - elapsed_time) + ']'
            dispositivos = len(self.dispositivos_conectados)
            sys.stdout.write(f"⏳ Grabando {progress_bar} {elapsed_time}s/{self.CONFIG['RECORDING_DURATION']}s 📱 {dispositivos} dispositivo{'s' if dispositivos != 1 else ''}\r")
            sys.stdout.flush()
            
    def iniciar(self):
        """Inicia el servidor y la grabación"""
        self.print_header()
        self.running = True
        self.start_time = time.time()
        
        # Iniciar thread para manejo de teclado
        keyboard_thread = threading.Thread(target=self.manejar_teclado)
        keyboard_thread.start()
        
        try:
            while self.running:
                if not self.paused:
                    # Recibir datos
                    data, addr = self.sock.recvfrom(1024*2+4)
                    
                    # Actualizar lista de dispositivos conectados
                    self.actualizar_dispositivos(addr)
                    
                    # Procesar datos recibidos
                    received_data = [int.from_bytes(data[i:i+2], 'little') 
                                   for i in range(0, len(data) - 2, 2)]
                    self.collected_data.extend(received_data)
                    
                    # Verificar tiempo transcurrido
                    elapsed_time = int(time.time() - self.start_time)
                    self.mostrar_progreso(elapsed_time)
                    
                    # Verificar si se completó el tiempo de grabación
                    if elapsed_time >= self.CONFIG['RECORDING_DURATION']:
                        file_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        wav_filename = f"audio_{file_timestamp}.wav"
                        
                        self.create_wav_file(wav_filename)
                        print(f"\n🎵 Archivo WAV guardado: {wav_filename}")
                        
                        # Reiniciar para nueva grabación
                        self.collected_data = []
                        self.start_time = time.time()
                
        except KeyboardInterrupt:
            print("\n🚨 Servidor detenido manualmente.")
            
        finally:
            self.running = False
            keyboard_thread.join()
            self.sock.close()
            print("👋 Servidor cerrado.")

if __name__ == "__main__":
    servidor = ServidorUDP()
    servidor.iniciar()