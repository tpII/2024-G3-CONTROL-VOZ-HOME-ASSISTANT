from flask import Flask, redirect, url_for, request, jsonify
from decode import decode_audio, remove_silence_librosa
from utils import array_to_wav
from actions import set_command
app = Flask(__name__)  # Crea una instancia de la aplicación Flask

# Define una ruta y una función de vista para la URL raíz
@app.route('/')
def index():
    return "Whisper server"

# Only JSON requirement request & response
@app.route('/decode', methods=['GET'])
def decode():

    # Obtener el parámetro opcional, con un valor por defecto
    array = request.get_json().get('array', [])
    file = 'input.wav' if array else './audio/dross_audio.wav'

    if array:
        array_to_wav(array , file)
        
        
    remove_silence_librosa(file, 'output.wav')
    output = decode_audio('output.wav')
    command_output = set_command(str(output))

    return command_output

# Ejecuta el servidor de desarrollo
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080) # El modo debug muestra errores y reinicia automáticamente el servidor al hacer cambios
