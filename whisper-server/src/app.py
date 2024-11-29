from flask import Flask, request
from decode import decode_audio, remove_silence_librosa
from utils import array_to_wav
from actions import set_command
import websocket
from ws import register_user, login_user
import asyncio

app = Flask(__name__)  # Crea una instancia de la aplicación Flask
asyncio.run(register_user("http://ruby-server:8080"))


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
    

    # Conexión al WebSocket
    auth_tokens = login_user("http://ruby-server:8080")
    access_token = auth_tokens['access_token']
    client = auth_tokens['client']
    uid = auth_tokens['uid']
    print(access_token, client, uid)
    websocket_params = "access-token={access_token}&email={client}&uid={uid}"

    def on_message(ws, message):
        print("Mensaje recibido en WebSocket: " + message)
        if message:
            print("Mensaje UDP enviado a Wemos: " + message)
        else:
            print("Acción no reconocida en WebSocket: " + message)

    def on_open(ws):
        print('Conexión WebSocket abierta')
        #ws.send(payload)
    
    def on_close(ws):
        print('Conexión WebSocket cerrada')
    
    def on_error(ws, error):
        print("Error en WebSocket: " + str(error))

    
    ws = websocket.WebSocketApp(
        "ws://ruby-server:8080/cable?" + websocket_params,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    ws.run_forever()

    return command_output

# Ejecuta el servidor de desarrollo
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8082) # El modo debug muestra errores y reinicia automáticamente el servidor al hacer cambios
