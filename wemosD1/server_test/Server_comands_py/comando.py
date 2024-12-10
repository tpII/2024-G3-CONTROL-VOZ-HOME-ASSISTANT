#!/usr/bin/env python3
import socket
import sys

def enviar_bytes_udp(ip, puerto, datos_hex):
    """
    Envía bytes a través de un socket UDP a la IP y puerto especificados.
    
    :param ip: Dirección IP de destino
    :param puerto: Puerto de destino
    :param datos_hex: Cadena de bytes en formato hexadecimal (ej. '0500')
    """
    try:
        # Convertir la cadena hexadecimal a bytes
        datos = bytes.fromhex(datos_hex)
        
        # Crear socket UDP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Enviar datos
        sock.sendto(datos, (ip, puerto))
        
        print(f"Enviados {len(datos)} bytes a {ip}:{puerto}")
        print(f"Datos enviados (hex): {datos.hex()}")
    
    except ValueError as e:
        print(f"Error en el formato hexadecimal: {e}")
    except socket.error as e:
        print(f"Error de socket: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")

def main():
    # Verificar que se proporcionen todos los argumentos
    if len(sys.argv) != 4:
        print("Uso: python udp_sender.py <IP> <PUERTO> <DATOS_HEX>")
        print("Ejemplo: python udp_sender.py 192.168.1.65 12345 0500")
        sys.exit(1)
    
    # Obtener argumentos de la línea de comandos
    ip = sys.argv[1]
    
    try:
        puerto = int(sys.argv[2])
    except ValueError:
        print("El puerto debe ser un número entero válido")
        sys.exit(1)
    
    datos_hex = sys.argv[3]
    
    # Llamar a la función de envío
    enviar_bytes_udp(ip, puerto, datos_hex)

if __name__ == "__main__":
    main()