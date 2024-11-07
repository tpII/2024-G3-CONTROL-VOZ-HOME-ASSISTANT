import socket
import time
from datetime import datetime
import sys

# Configuración del servidor UDP
udp_ip = "0.0.0.0"  # Escuchar en todas las interfaces
udp_port = 12345     # Debe coincidir con el puerto usado por la ESP8266

# Crear socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((udp_ip, udp_port))

# Obtener la lista de IPs locales
local_ips = socket.gethostbyname_ex(socket.gethostname())[2]

# Contador de paquetes descartados
discarded_packets = 0

# Función para calcular el checksum de los datos recibidos
def calculate_checksum(data):
    checksum = sum(data[:]) & 0xFFFF  # Calcular el checksum excluyendo el último valor (el checksum recibido)
    return checksum

# Función para imprimir la interfaz de inicio
def print_header():
    print("\n" + "=" * 50)
    print("💡 SERVIDOR UDP - MONITOREO DE DATOS 💡")
    print("=" * 50 + "\n")
    print("📍 Escuchando en las siguientes IPs:")
    for ip in local_ips:
        print(f"📍 {ip}:{udp_port}")
    print(f"📡 Puerto de escucha: {udp_port}")
    print("\n" + "=" * 50 + "\n")

print_header()

start_time = time.time()
file_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"datos_{file_timestamp}.txt"
discard_filename = f"discard_{file_timestamp}.txt"

with open(filename, 'w') as file, open(discard_filename, 'w') as discard_file:
    while True:
        try:
            # Esperar datos (buffer de hasta 1028 bytes para el array de 512 uint16_t + 2 bytes checksum)
            data, addr = sock.recvfrom(1028)

            # Verificar si se recibieron datos suficientes
            if len(data) < 1026:
                print(f"🚫 Paquete de tamaño inesperado de {addr}, descartado.")
                discarded_packets += 1
                discard_file.write(','.join(map(str, data)) + '\n')
                continue

            # Reagrupar los datos de 8 bits en enteros de 16 bits (uint16_t)
            received_data = [int.from_bytes(data[i:i+2], 'little') for i in range(0, len(data) - 2, 2)]
            received_checksum = int.from_bytes(data[-2:], 'little')

            # Calcular el checksum de los datos recibidos
            calculated_checksum = calculate_checksum(received_data)

            # Verificar el checksum y mostrar ambos valores
            if calculated_checksum != received_checksum:
                print(f"🚫 Checksum incorrecto de {addr}")
                print(f"🧐 Checksum recibido: {received_checksum}")
                print(f"🛠️ Checksum calculado: {calculated_checksum}")
                discarded_packets += 1
                discard_file.write(','.join(map(str, received_data)) + '\n')
                continue


            # Guardar los datos en el archivo
            file.write(','.join(map(str, received_data)) + '\n')

            # Verificar si han pasado 10 segundos para crear un nuevo archivo
            if time.time() - start_time > 10:
                file.close()
                discard_file.close()
                print(f"💾 Archivo guardado: {filename}")
                file_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"datos_{file_timestamp}.txt"
                discard_filename = f"discard_{file_timestamp}.txt"
                file = open(filename, 'w')
                discard_file = open(discard_filename, 'w')
                start_time = time.time()

            # Mostrar progreso con una barra de progreso simple
            elapsed_time = int(time.time() - start_time)
            progress_bar = '[' + '=' * (elapsed_time % 10) + ' ' * (10 - (elapsed_time % 10)) + ']'
            sys.stdout.write(f"⏳ Recibiendo datos de {addr} {progress_bar} \r")
            sys.stdout.flush()
        except KeyboardInterrupt:
            print("\n🚨 Servidor detenido manualmente.")
            break

print(f"\n🚨 Paquetes descartados por checksum incorrecto: {discarded_packets}")
