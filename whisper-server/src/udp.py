import socket
import logging
import numpy as np
import wave
from datetime import datetime
import os
import time

# Configurar logging para stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class ServidorUDP:
    def __init__(self, host="192.168.1.65", port=12345):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((host, port))
        self.running = True
        self.host = host
        self.port = port
        self.archivos_wav = [] 
        self.collected_data = []  
        self.tiempo_inicio = None
        logging.info(f"🎧 Servidor UDP iniciado en {host}:{port}")
        print(f"🎧 Servidor UDP escuchando en {host}:{port}")

        # Actualizar configuración
        self.CONFIG = {
            'TRIGGER_SILENCE': 32,     # umbral de variación para considerar silencio
            'SILENCE_DURATION': 1,     # segundos de silencio para detener
            'SAMPLE_RATE': 15000,
            'MAX_DURATION': 5         # duración máxima en segundos
        }
        self.ultima_grabacion = time.time()
        self.inicio_grabacion = None

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

    def guardar_wav(self, datos, sample_rate=15000):
        """
        Guarda los datos de audio como archivo WAV si duran más de 2 segundos
        """
        try:
            if len(datos) < sample_rate * self.CONFIG['SILENCE_DURATION']:
                return None
                
            # Normalizar datos
            normalized_data = np.array(datos, dtype=np.int16)
            normalized_data = ((normalized_data-512) * 64)
            
            # Generar nombre de archivo
            filename = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            filepath = f"./udp_audios/{filename}"
            
            # Guardar archivo WAV
            with wave.open(filepath, 'w') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(normalized_data.tobytes())
            
            self.archivos_wav.append(filepath)
            logging.info(f"✅ Audio guardado: {filepath}")
            return filepath
            
        except Exception as e:
            logging.error(f"❌ Error guardando WAV: {e}")
            return None

    def eliminar_wav_antiguo(self):
        """
        Elimina el archivo WAV más antiguo de la lista
        """
        try:
            if self.archivos_wav:
                archivo_antiguo = self.archivos_wav.pop(0)  # Eliminar y obtener el más antiguo
                os.remove(archivo_antiguo)
                logging.info(f"🗑️ Archivo eliminado: {archivo_antiguo}")
        except Exception as e:
            logging.error(f"❌ Error eliminando archivo WAV: {e}")

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

    def udp_listener(self):
        """
        Función que se ejecuta en un thread separado para escuchar UDP continuamente
        """
        buffer_actual = []
        ultima_actividad = time.time()
        
        while True:
            try:
                data, addr = self.sock.recvfrom(1024*2+4)
                tiempo_actual = time.time()
                
                if data:
                    # Convertir datos a formato numérico
                    received_data = [int.from_bytes(data[i:i+2], 'little') 
                                   for i in range(0, len(data) - 2, 2)]
                    
                    buffer_actual.extend(received_data)
                    self.collected_data.extend(received_data)
                    
                    # Mantener buffer_actual con tamaño controlado
                    buffer_actual = buffer_actual[-50:]  # Últimas 50 muestras
                    
                    # Verificar si hay silencio
                    if self.verificar_silencio(buffer_actual):
                        if tiempo_actual - ultima_actividad > self.CONFIG['SILENCE_DURATION']:
                            if len(self.collected_data) > 0:
                                wav_path = self.guardar_wav(self.collected_data)
                                if wav_path:
                                    logging.info(f"✅ Audio guardado por silencio: {wav_path}")
                                self.collected_data = []
                                buffer_actual = []
                    else:
                        ultima_actividad = tiempo_actual
                    
                    # Segunda condición: guardar si tenemos suficientes datos
                    if len(self.collected_data) >= self.CONFIG['SAMPLE_RATE'] * self.CONFIG['MAX_DURATION']:
                        wav_path = self.guardar_wav(self.collected_data)
                        if wav_path:
                            logging.info(f"✅ Audio guardado por duración máxima: {wav_path}")
                        self.collected_data = []
                        buffer_actual = []
                
            except Exception as e:
                logging.error(f"❌ Error en listener UDP: {e}")
                time.sleep(0.1)