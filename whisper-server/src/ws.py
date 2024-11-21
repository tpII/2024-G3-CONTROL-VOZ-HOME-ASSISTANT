import websockets
import json
import socket
import logging
import requests
import websocket

# Configuraciones del servidor
UDP_UID = 'udp@server.com' # os.get
UDP_PASSWORD = 123456789 # os.get
COMMANDS_TO_UDP = {
    'turn_on': {'word': 'C_connect'},
    'turn_off': {'word': 'C_disconnect'}
}


# Función para conectarse como cliente WebSocket
async def connect_to_server(uri):
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Conectado al servidor WebSocket: {uri}")
    except websockets.ConnectionClosed:
        print("Conexión cerrada por el servidor.")
    except Exception as e:
        print(f"Error: {e}")


async def test_websocket_connection(url):
    try:

        # Conectar al servidor
        print(f"Conectando a {url}...")
        async with websockets.connect(url) as websocket:
            print("Conexión WebSocket establecida.")

            # Enviar un mensaje de prueba
            test_message = "Mensaje de prueba desde el cliente Python."
            print("Enviando mensaje")
            websocket.send(test_message)

            # Recibir la respuesta del servidor
            response = websocket.recv()
            print(f"Respuesta recibida del servidor")

            # Cerrar la conexión
            websocket.close()
        print("Conexión WebSocket cerrada.")
    except Exception as e:
        print(f"Ocurrió un error: {e}")


def init_login():
    # Configuración de logging
    udp_logger = logging.getLogger('udp_logger')
    udp_logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler('log/udp_server.log')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    udp_logger.addHandler(file_handler)

# Función para registrar al usuario
def register_user(API_URL='http://localhost:8080'):
    register_endpoint='/auth'
    url = f"{API_URL}{register_endpoint}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "user": {
            "email": UDP_UID,
            "password": str(UDP_PASSWORD),
            "password_confirmation": str(UDP_PASSWORD)
        }
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# Función para realizar login y obtener los tokens
def login_user(API_URL='http://localhost:8080'):
    login_endpoint = '/auth/sign_in'
    url = f"{API_URL}{login_endpoint}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "email": UDP_UID,
        "password": str(UDP_PASSWORD)
    }
    response = requests.post(url, headers=headers, json=data)
    headers = response.headers
    return {
        "uid": headers.get('uid'),
        "client": headers.get('client'),
        "access_token": headers.get('access-token')
    }

# Función para conectar al WebSocket con autenticación
def connect_websocket(auth_tokens,API_URL='ws://localhost:8080'):
    websocket_endpoint = '/cable'
    websocket_url = f"{API_URL}{websocket_endpoint}"
    access_token = auth_tokens['access_token']
    client = auth_tokens['client']
    uid = auth_tokens['uid']
    websocket_params = f"access-token={access_token}&client={client}&uid={uid}"
    
    def on_message(ws, message):
        udp_logger.info(f"Mensaje recibido en WebSocket: {message}")
        try:
            data = json.loads(message)
            action = data.get('action')
            if action in COMMANDS_TO_UDP:
                udp_message = json.dumps(COMMANDS_TO_UDP[action])
                send_udp_message_to_wemos(udp_message)
                udp_logger.info(f"Mensaje UDP enviado a Wemos: {udp_message}")
            else:
                udp_logger.info(f"Acción no reconocida en WebSocket: {action}")
        except json.JSONDecodeError:
            udp_logger.info(f"Mensaje de WebSocket no válido: {message}")
    
    def on_open(ws):
        udp_logger.info('Conexión WebSocket abierta')
    
    def on_close(ws):
        udp_logger.info('Conexión WebSocket cerrada')
    
    def on_error(ws, error):
        udp_logger.info(f"Error en WebSocket: {error}")

    ws = websocket.WebSocketApp(f"{websocket_url}?{websocket_params}",
                                on_message=on_message,
                                on_open=on_open,
                                on_close=on_close,
                                on_error=on_error)
    return ws

# Función para enviar un mensaje UDP a la Wemos
def send_udp_message_to_wemos(message,wemos_host='192.168.1.70',wemos_port=8080):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.sendto(message.encode(), (wemos_host, wemos_port))

def final_test():
    # Inicia el registro y login para obtener los tokens
    udp_logger.info('Registrando y autenticando al usuario...')
    register_user()  # Registra el usuario
    auth_tokens = login_user()  # Realiza login y obtiene los tokens

    # Conexión al WebSocket
    ws = connect_websocket(auth_tokens)

    # Configura el socket UDP para escuchar en el puerto 12345
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(('0.0.0.0', 12345))

    # Límite de bytes para recibir
    MAX_BYTES = 65507

    udp_logger.info('UDP Server listening on port 12345...')

    # Loop infinito para recibir mensajes UDP y enviarlos por WebSocket
    # Este es el loop en el que funciona la APP
    #while True:
        #message, sender = udp_socket.recvfrom(MAX_BYTES)
        sender_ip = sender[0] # esto llega por request de rails
        sender_port = sender[1] # esto llega por request de rails

        udp_logger.info(f"Mensaje recibido: '{message.strip()}' de {sender_ip}:{sender_port}")

        # Formatear el mensaje como JSON para enviar a través de WebSocket
        payload = {
            "message": message.strip().decode(),
            "ip": sender_ip,
            "port": sender_port
        }
        
        # Enviar el mensaje al WebSocket
        ws.send(json.dumps(payload))