import socket

def udp_client_receive_and_send(server_ip, server_port, message):
    # Crear un socket UDP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"Cliente UDP conectado al servidor {server_ip}:{server_port}")

    # Recibir respuesta del servidor
    data, server = client_socket.recvfrom(1024)  # Buffer de 1024 bytes
    print(f"Respuesta del servidor: {data.decode()}")

    # Enviar el mensaje al servidor
    client_socket.sendto(message.encode(), (server_ip, server_port))
    print("Mensaje enviado.")
    
    client_socket.close()
    print("Socket cerrado.")
