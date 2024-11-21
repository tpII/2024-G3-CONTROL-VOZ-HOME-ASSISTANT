from flask import Flask, request
from decode import decode_audio, remove_silence_librosa
from utils import array_to_wav
from actions import set_command
from ws import register_user, login_user, connect_websocket, init_login
import asyncio

app = Flask(__name__)  # Crea una instancia de la aplicación Flask

# Define una ruta y una función de vista para la URL raíz
@app.route('/')
def index():
    #asyncio.run(test_websocket_connection("ws://ruby-server:8080"))
    init_login()
    udp_logger.info('Registrando y autenticando al usuario...')
    register_user("http://ruby-server:8080")
    auth_tokens = login_user("http://ruby-server:8080")

    # Conexión al WebSocket
    ws = connect_websocket(auth_tokens,"ws://ruby-server:8080")

    # Configura el socket UDP para escuchar en el puerto 12345
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(('0.0.0.0', 12345))

    # Límite de bytes para recibir
    MAX_BYTES = 65507

    udp_logger.info('UDP Server listening on port 12345...')

    return "Whisper server"

# Only JSON requirement request & response
@app.route('/decode', methods=['GET'])
def decode():

    sender_ip   = request.get_json().get('upd_ip')
    sender_port = request.get_json().get('udp_port')
    
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
        "message": command_output,
        "ip": sender_ip,
        "port": sender_port
    }
    
    # Enviar el mensaje al WebSocket
    ws.send(json.dumps(payload))

    return command_output

# Ejecuta el servidor de desarrollo
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8082) # El modo debug muestra errores y reinicia automáticamente el servidor al hacer cambios
