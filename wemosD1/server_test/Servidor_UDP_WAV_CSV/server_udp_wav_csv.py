import socket
import time
from datetime import datetime
import sys
import csv
import wave
import numpy as np

# Configuración del servidor UDP
udp_ip = "0.0.0.0"
udp_port = 12345

# Configuración del audio
SAMPLE_RATE = 44100  # Frecuencia de muestreo estándar
RECORDING_DURATION = 30  # Duración de grabación en segundos

# Crear socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((udp_ip, udp_port))

# Obtener la lista de IPs locales
local_ips = socket.gethostbyname_ex(socket.gethostname())[2]

def print_header():
    print("\n" + "=" * 50)
    print("💡 SERVIDOR UDP - MONITOREO DE DATOS 💡")
    print("=" * 50 + "\n")
    print("📍 Escuchando en las siguientes IPs:")
    for ip in local_ips:
        print(f"📍 {ip}:{udp_port}")
    print(f"📡 Puerto de escucha: {udp_port}")
    print("\n" + "=" * 50 + "\n")

def create_wav_file(data, filename):
    """
    Crear archivo WAV a partir de los datos recibidos
    """
    # Normalizar los datos al rango de 10bits a 16bits con signo 
    normalized_data = np.array(data, dtype=np.int16)
    normalized_data = (( normalized_data-512)  * 64) 
    
    # Crear archivo WAV
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes por muestra (16 bits)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(normalized_data.tobytes())

print_header()

start_time = time.time()
file_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_filename = f"datos_{file_timestamp}.csv"
wav_filename = f"audio_{file_timestamp}.wav"

collected_data = []

with open(csv_filename, 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['timestamp', 'value'])  # Encabezados CSV
    
    while True:
        try:
            # Esperar datos
            data, addr = sock.recvfrom(1028)
            
            # Verificar si se recibieron datos suficientes
            if len(data) < 1026:
                print(f"🚫 Paquete de tamaño inesperado de {addr}, descartado.")
                continue
            
            # Reagrupar los datos de 8 bits en enteros de 16 bits
            received_data = [int.from_bytes(data[i:i+2], 'little') 
                           for i in range(0, len(data) - 2, 2)]
            
            # Guardar datos en el array para el archivo WAV
            collected_data.extend(received_data)
            
            # Guardar en CSV con timestamp
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            for value in received_data:
                csv_writer.writerow([current_time, value])
            
            # Verificar si han pasado 30 segundos
            if time.time() - start_time > RECORDING_DURATION:
                # Cerrar archivo CSV actual
                csv_file.close()
                print(f"💾 Archivo CSV guardado: {csv_filename}")
                
                # Crear archivo WAV
                create_wav_file(collected_data, wav_filename)
                print(f"🎵 Archivo WAV guardado: {wav_filename}")
                
                # Reiniciar para nuevo ciclo de grabación
                file_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                csv_filename = f"datos_{file_timestamp}.csv"
                wav_filename = f"audio_{file_timestamp}.wav"
                collected_data = []
                csv_file = open(csv_filename, 'w', newline='')
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(['timestamp', 'value'])
                start_time = time.time()
            
            # Mostrar progreso
            elapsed_time = int(time.time() - start_time)
            progress_bar = '[' + '=' * (elapsed_time) + ' ' * (RECORDING_DURATION - elapsed_time) + ']'
            sys.stdout.write(f"⏳ Recibiendo datos de {addr} {progress_bar} {elapsed_time}s/{RECORDING_DURATION}s\r")
            sys.stdout.flush()
            
        except KeyboardInterrupt:
            print("\n🚨 Servidor detenido manualmente.")
            break