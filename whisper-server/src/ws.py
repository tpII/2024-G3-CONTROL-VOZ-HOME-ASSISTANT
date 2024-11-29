from websocket import WebSocketApp
import requests
import asyncio


# Configuraciones del servidor
UDP_UID = 'udp@server.com' # os.get
UDP_PASSWORD = 123456789 # os.get
COMMANDS_TO_UDP = {
    'turn_on': {'word': 'C_connect'},
    'turn_off': {'word': 'C_disconnect'}
}

        
# Función para registrar al usuario
async def register_user(API_URL='http://localhost:8080'):
    register_endpoint='/auth'
    url = API_URL + register_endpoint
    headers = {'Content-Type': 'application/json'}
    data = {
        "user": {
            "email": UDP_UID,
            "password": str(UDP_PASSWORD)        
            }
    }
    response = requests.post(url, headers=headers, json=data)
    return response

# Función para realizar login y obtener los tokens
def login_user(API_URL='http://localhost:8080'):
    login_endpoint = '/auth/sign_in'
    url = API_URL + login_endpoint
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

# Función para enviar un mensaje UDP a la Wemos
#async def send_udp_message_to_wemos(message,wemos_host='192.168.1.70',wemos_port=8080):
#    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
#        udp_socket.sendto(message.encode(), (wemos_host, wemos_port))