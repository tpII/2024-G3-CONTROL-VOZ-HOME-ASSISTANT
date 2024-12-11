import socket
import time
import numpy as np
from datetime import datetime
import sys
import wave
import threading
import keyboard

class ServidorUDP:
    def __init__(self):
        # Configuración global
        self.CONFIG = {
            'UDP_IP': "0.0.0.0",
            'UDP_PORT': 12345,
            'SAMPLE_RATE': 10000,
            'MAX_RECORDING_DURATION': 30,  # máximo 30 segundos por grabación
            'SILENCE_DURATION': 1,  # 1 segundos de silencio para separar las grabaciones
            'TRIGGER_SILENCE': 32   # umbral de variación para considerar silencio
        }
        
        # Variables de estado
        self.running = False
        self.paused = False
        self.collected_data = []
        self.start_time = None
        self.last_signal_time = None
        self.local_ips = socket.gethostbyname_ex(socket.gethostname())[2]
        
        # Control de dispositivos conectados
        self.dispositivos_conectados = {}  # {(ip, puerto): último_tiempo_visto}
        self.tiempo_timeout = 5  # segundos sin datos para considerar desconectado
        
        # Inicializar socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.CONFIG['UDP_IP'], self.CONFIG['UDP_PORT']))
        self.sock.settimeout(1.0)  # timeout para permitir verificaciones periódicas
        
    def print_header(self):
        """Muestra la información inicial del servidor"""
        print("\n" + "=" * 50)
        print("💡 SERVIDOR UDP - MONITOREO DE DATOS CON DETECCIÓN DE SILENCIO 💡")
        print("=" * 50 + "\n")
        print("📍 Escuchando en las siguientes IPs:")
        for ip in self.local_ips:
            print(f"📍 {ip}:{self.CONFIG['UDP_PORT']}")
        print(f"📡 Puerto de escucha: {self.CONFIG['UDP_PORT']}")
        print(f"\n⚙️  Configuración de Silencio:")
        print(f"   - Umbral de Silencio: ±{self.CONFIG['TRIGGER_SILENCE']}")
        print(f"   - Duración de Silencio para Detener: {self.CONFIG['SILENCE_DURATION']} segundos")
        print(f"   - Duración Máxima de Grabación: {self.CONFIG['MAX_RECORDING_DURATION']} segundos")
        print("\nComandos disponibles:")
        print("'p' - Pausar/Reanudar grabación")
        print("'q' - Finalizar grabación actual y salir")
        print("'s' - Salir sin guardar")
        print("\n" + "=" * 50 + "\n")

    def verificar_silencio(self, datos):
        """
        Verifica si la señal está en estado de silencio
        
        Args:
            datos (list): Lista de datos recibidos
        
        Returns:
            bool: True si está en silencio, False en caso contrario
        """
        if not datos:
            return True
        
        # Calcular valor promedio
        promedio = np.mean(datos)
        
        # Verificar variación
        variacion = np.max(np.abs(np.array(datos) - promedio))
        
        return variacion < self.CONFIG['TRIGGER_SILENCE']

    def guardar_grabacion(self, filename=None):
        """Guarda la grabación actual como archivo WAV"""
        try:
            import soundfile as sf  # Agregar al inicio del archivo: pip install soundfile
            
            if not self.collected_data:
                return
            
            normalized_data = np.array(self.collected_data, dtype=np.int16)
            normalized_data = ((normalized_data-512) * 64)
            
            if filename is None:
                filename = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            
            sf.write(filename, normalized_data, self.CONFIG['SAMPLE_RATE'])
            
            print(f"\n🎵 Archivo WAV guardado: {filename}")
            self.collected_data = []
            
        except Exception as e:
            print(f"Error al guardar el archivo WAV: {e}")

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
                
            time.sleep(0.1)

    def mostrar_progreso(self, elapsed_time, buffer_length):
        """Muestra la barra de progreso de la grabación"""
        if not self.paused:
            progress_bar = '[' + '=' * min(elapsed_time, 50) + ' ' * max(50 - elapsed_time, 0) + ']'
            sys.stdout.write(f"⏳ Grabando {progress_bar} {elapsed_time}s | Buffer: {buffer_length} muestras\r")
            sys.stdout.flush()

    def iniciar(self):
        """Inicia el servidor y la grabación"""
        self.print_header()
        self.running = True
        
        # Iniciar thread para manejo de teclado
        keyboard_thread = threading.Thread(target=self.manejar_teclado)
        keyboard_thread.daemon = True
        keyboard_thread.start()
        
        buffer_actual = []
        inicio_grabacion = time.time()
        ultima_grabacion = time.time()
        
        try:
            while self.running:
                if not self.paused:
                    try:
                        data, _ = self.sock.recvfrom(1024*2+4)
                        
                        # Procesar datos recibidos
                        received_data = [int.from_bytes(data[i:i+2], 'little') 
                                       for i in range(0, len(data) - 2, 2)]
                        
                        buffer_actual.extend(received_data)
                        self.collected_data.extend(received_data)
                        
                        # Calcular tiempo transcurrido
                        tiempo_actual = time.time()
                        tiempo_transcurrido = int(tiempo_actual - inicio_grabacion)
                        
                        # Verificar condiciones de detención
                        if self.verificar_silencio(buffer_actual[-50:]):  # Verificar últimas 50 muestras
                            if tiempo_actual - ultima_grabacion > self.CONFIG['SILENCE_DURATION']:
                                print("\n🔇 Silencio detectado. Guardando grabación...")
                                self.guardar_grabacion()
                                buffer_actual = []
                                inicio_grabacion = tiempo_actual
                                ultima_grabacion = tiempo_actual
                        else:
                            ultima_grabacion = tiempo_actual
                        
                        # Reset buffer si es muy largo
                        buffer_actual = buffer_actual[-1000:]
                        
                        # Verificar tiempo máximo de grabación
                        if tiempo_transcurrido >= self.CONFIG['MAX_RECORDING_DURATION']:
                            print("\n⏰ Tiempo máximo de grabación alcanzado.")
                            self.guardar_grabacion()
                            buffer_actual = []
                            inicio_grabacion = tiempo_actual
                        
                        # Mostrar progreso
                        self.mostrar_progreso(tiempo_transcurrido, len(self.collected_data))
                        
                    except socket.timeout:
                        # Verificar silencio por timeout de socket
                        if time.time() - ultima_grabacion > self.CONFIG['SILENCE_DURATION']:
                            if self.collected_data:
                                print("\n📴 Sin señal. Guardando grabación...")
                                self.guardar_grabacion()
                                buffer_actual = []
                                inicio_grabacion = time.time()
                                ultima_grabacion = time.time()
                    
        except KeyboardInterrupt:
            print("\n🚨 Servidor detenido manualmente.")
            
        finally:
            # Guardar última grabación si hay datos
            if self.collected_data:
                self.guardar_grabacion()
            
            self.running = False
            keyboard_thread.join()
            self.sock.close()
            print("👋 Servidor cerrado.")

if __name__ == "__main__":
    servidor = ServidorUDP()
    servidor.iniciar()