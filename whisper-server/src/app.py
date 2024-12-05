from flask import Flask, request
from decode import decode_audio, remove_silence_librosa
from utils import array_to_wav
from actions import set_command
import websocket
from udp import udp_client_receive_and_send 
import requests

app = Flask(__name__)  # Crea una instancia de la aplicación Flask

UDP_UID = "udp3@server.com" # os.get
UDP_PASSWORD = "123456789" # os.get

# Define una ruta y una función de vista para la URL raíz
@app.route('/')
def index():
    return "Whisper server"

# Only JSON requirement request & response
@app.route('/decode', methods=['GET'])
def decode():
    
    #sender_ip   = request.get_json().get('upd_ip')
    #sender_port = request.get_json().get('udp_port')
    
    # Obtener el parámetro opcional, con un valor por defecto
    array = request.get_json().get('array', [])
    file = 'input.wav' if array else './audio/dross_audio.wav'

    if array:
        array_to_wav(array , file)
        
        
    remove_silence_librosa(file, 'output.wav')
    output = decode_audio('output.wav')
    command_output = set_command(str(output))

    # Formatear el mensaje como JSON para enviar a través de WebSocket
    payload = {
        "message": command_output
        #"ip": sender_ip,
        #"port": sender_port
    }
    
    udp_client_receive_and_send('192.168.1.70', '4040', payload)

    return payload

# Ejecuta el servidor de desarrollo
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8082) # El modo debug muestra errores y reinicia automáticamente el servidor al hacer cambios
