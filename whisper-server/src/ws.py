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

# Función para conectar al WebSocket con autenticación
async def connect_websocket(auth_tokens,API_URL='ws://localhost:8080'):
    websocket_endpoint = '/cable'
    websocket_url = API_URL + websocket_endpoint
    access_token = auth_tokens['access_token']
    client = auth_tokens['client']
    uid = auth_tokens['uid']
    websocket_params = "access-token={access_token}&client={client}&uid={uid}"
    
    def on_message(ws, message):
        print("Mensaje recibido en WebSocket: " + message)
        if message:
            print("Mensaje UDP enviado a Wemos: " + message)
        else:
            print("Acción no reconocida en WebSocket: " + message)

    def on_open(ws):
        print('Conexión WebSocket abierta')
    
    def on_close(ws):
        print('Conexión WebSocket cerrada')
    
    def on_error(ws, error):
        print("Error en WebSocket: " + error)

    #ws = websockets.connect(websocket_url) 

    # Conexión al WebSocket
    ws = WebSocketApp(
        websocket_url + "?" + websocket_params,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    ws.run_forever()

    return ws

# Función para enviar un mensaje UDP a la Wemos
#async def send_udp_message_to_wemos(message,wemos_host='192.168.1.70',wemos_port=8080):
#    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
#        udp_socket.sendto(message.encode(), (wemos_host, wemos_port))