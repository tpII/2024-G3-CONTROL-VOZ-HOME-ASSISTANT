import serial
import time
from datetime import datetime
import wave
import struct
import os

def capture_serial_data(port='COM6', baud_rate=921600, duration=10):
    """
    Captura datos seriales y los guarda en archivos RAW y WAV
    
    Args:
        port (str): Puerto serial (ej: 'COM6' en Windows, '/dev/ttyUSB0' en Linux)
        baud_rate (int): Velocidad en baudios
        duration (int): Duración de la captura en segundos
    """
    try:
        # Configurar conexión serial
        ser = serial.Serial(port, baud_rate, timeout=1)
        print(f"Conectado a {port} a {baud_rate} baudios")
        
        # Crear nombre de archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        raw_filename = f"audio_capture_{timestamp}.raw"
        
        # Capturar datos
        samples = []  # Lista para almacenar las muestras
        
        # Abrir archivo en modo binario
        with open(raw_filename, 'wb') as file:
            start_time = time.time()
            samples_count = 0
            
            print(f"Iniciando captura por {duration} segundos...")
            
            while (time.time() - start_time) < duration:
                if ser.in_waiting:
                    # Leer línea y convertir a bytes
                    line = ser.readline().strip()
                    try:
                        # Convertir string a valor numérico
                        value = int(line)
                        # Guardar en archivo RAW
                        file.write(value.to_bytes(2, byteorder='little', signed=True))
                        # Guardar muestra para WAV
                        samples.append(value)
                        samples_count += 1
                        
                        # Mostrar progreso
                        elapsed = time.time() - start_time
                        print(f"\rProgreso: {elapsed:.1f}s / {duration}s - Muestras: {samples_count}", end='')
                    except ValueError:
                        continue
        
        # Calcular tasa de muestreo real
        sample_rate = int(samples_count/duration)
        
        # Crear nombre de archivo WAV incluyendo la tasa de muestreo
        wav_filename = f"audio_capture_{timestamp}_{sample_rate}Hz.wav"
        
        # Crear archivo WAV
        with wave.open(wav_filename, 'w') as wav_file:
            # Configurar parámetros del archivo WAV
            nchannels = 1
            sampwidth = 2  # 2 bytes por muestra (16 bits)
            framerate = sample_rate
            nframes = samples_count
            comptype = "NONE"
            compname = "not compressed"
            
            # Establecer parámetros
            wav_file.setparams((nchannels, sampwidth, framerate, nframes, comptype, compname))
            
            # Escribir muestras
            for sample in samples:
                wav_file.writeframes(struct.pack('<h', sample))
        
        print(f"\nCaptura completada:")
        print(f"- Archivo RAW: {raw_filename}")
        print(f"- Archivo WAV: {wav_filename}")
        print(f"- Muestras capturadas: {samples_count}")
        print(f"- Tasa de muestreo: {sample_rate} Hz")
        print(f"- Duración real: {samples_count/sample_rate:.2f} segundos")
        
    except serial.SerialException as e:
        print(f"Error al abrir el puerto serial: {e}")
    finally:
        if 'ser' in locals():
            ser.close()
            print("Puerto serial cerrado")

if __name__ == "__main__":
    # Puedes modificar estos parámetros según tu configuración
    PUERTO_SERIAL = 'COM6'  # Cambia esto según tu puerto
    BAUD_RATE = 921600     # Ajusta según la velocidad de tu ESP8266
    DURACION = 10          # Duración en segundos
    
    capture_serial_data(PUERTO_SERIAL, BAUD_RATE, DURACION)