import socket
import logging
import numpy as np
import wave
from datetime import datetime
import os

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
        self.archivos_wav = [] 
        self.collected_data = []  
        self.tiempo_inicio = None
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

    def guardar_wav(self, datos, sample_rate=15000):
        """
        Guarda los datos de audio como archivo WAV si duran más de 2 segundos
        """
        try:
            if len(datos) < sample_rate * 2:  # Menos de 2 segundos
                logging.info("❌ Audio descartado por ser menor a 2 segundos")
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
