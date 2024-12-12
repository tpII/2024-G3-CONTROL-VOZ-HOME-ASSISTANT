import json
import socket
from datetime import datetime
import requests
from websocket import create_connection
import os

# Constantes para el webserver
API_URL = os.getenv("WEBSERVER_URL", "http://webserver")
WEBSOCKET_URL = os.getenv("WEBSOCKET_URL", "ws://webserver")
WEBSOCKET_PORT = int(os.getenv("WEBSOCKET_PORT", 8080))
REGISTER_ENDPOINT = "/auth"
LOGIN_ENDPOINT = "/auth/sign_in"
WEBSOCKET_URI = "/cable"

# Constantes para la Wemos
WEMOS_IP = os.getenv("WEMOS_IP", "192.168.1.65")
WEMOS_PORT = int(os.getenv("WEMOS_PORT", 44444))

# Constantes para UDP
UDP_PORT = 12345
UDP_UID = "udp@server.com"
UDP_PASSWORD = "123456789"


def log(message):
  print(f"{datetime.now().isoformat()} - {message}")

# Registra al usuario


def register_user():
  log("Registrando usuario...")
  url = f"{API_URL}{REGISTER_ENDPOINT}"
  payload = {
      "user": {
          "email": UDP_UID,
          "password": UDP_PASSWORD,
          "password_confirmation": UDP_PASSWORD,
      }
  }
  response = requests.post(url, json=payload)
  if response.status_code == 200:
    log("Registro exitoso.")
  else:
    log(f"Error al registrar usuario: {response.text}")

# Realiza login y obtiene los tokens


def login_user():
  log("Autenticando usuario...")
  url = f"{API_URL}{LOGIN_ENDPOINT}"
  payload = {"email": UDP_UID, "password": UDP_PASSWORD}
  response = requests.post(url, json=payload)
  if response.status_code == 200:
    log("Autenticación exitosa.")
    headers = response.headers
    return {
        "access_token": headers.get("access-token"),
        "client": headers.get("client"),
        "uid": headers.get("uid"),
    }
  else:
    log(f"Error en la autenticación: {response.text}")
    return None

# Conecta al WebSocket con autenticación


def connect_websocket(auth_tokens):
  log("Conectando al WebSocket...")
  websocket_url = f"{WEBSOCKET_URL}{WEBSOCKET_URI}:{WEBSOCKET_PORT}"
  query_params = f"access-token={auth_tokens['access_token']}&client={auth_tokens['client']}&uid={auth_tokens['uid']}"
  print(f"Conectando a WebSocket en: {websocket_url}?{query_params}")
  ws = create_connection(f"{websocket_url}?{query_params}")

  log("Conexión WebSocket establecida.")
  return ws

# Envía un mensaje UDP a la Wemos


def send_udp_message_to_wemos(message):

  print("Mensaje: " + message)
  datos = bytes.fromhex(message[2:])  # Skip '0x' prefix
        
  # Crear socket UDP
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  
  # Enviar datos
  sock.sendto(datos, (WEMOS_IP, WEMOS_PORT))

  log(f"Mensaje UDP enviado a Wemos: {datos}")


# Inicia el servidor UDP y reenvía mensajes al WebSocket


def start_udp_server(auth_tokens):
  ws = connect_websocket(auth_tokens)

  udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  udp_socket.bind(("0.0.0.0", UDP_PORT))

  log(f"Servidor UDP escuchando en el puerto {UDP_PORT}...")

  while True:
    message, sender = udp_socket.recvfrom(65507)
    sender_ip, sender_port = sender
    message = message.decode().strip()
    log(f"Mensaje recibido: '{message}' de {sender_ip}:{sender_port}")

    # Envía directamente el mensaje a la Wemos
    send_udp_message_to_wemos(message)


if __name__ == "__main__":
  # Registra y autentica al usuario
  register_user()
  auth_tokens = login_user()

  if auth_tokens:
    # Inicia el servidor UDP
    start_udp_server(auth_tokens)
  else:
    log("No se pudo autenticar al usuario. El servidor no se iniciará.")