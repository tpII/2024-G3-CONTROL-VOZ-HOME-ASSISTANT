from flask import Flask, redirect, url_for, request
from decode import decode_audio, remove_silence_librosa
from utils import array_to_wav
from actions import set_command


app = Flask(__name__)  # Crea una instancia de la aplicación Flask

# Define una ruta y una función de vista para la URL raíz
@app.route('/')
def index():
    return "Whisper server"

# Only JSON requirement request & response
@app.route('/decode', methods=['POST'])
def decode():

    # Obtener el parámetro opcional, con un valor por defecto
    array = request.get_json().get('array', [])

    file = 'input.wav' if array else './audio/dross_audio.wav'

    if array:
        array_to_wav(array, file)
        
    remove_silence_librosa(file, 'output.wav')
    output = decode_audio('input.wav')
    print(output)
    return redirect(url_for('actions', text=output))


# Dado el texto decodificado. Retorna la primer palabra clave y su respecitvo comando a enviar
@app.route('/actions/<text>', methods=['POST'])
def actions(text):

    command_output = set_command(text)
    
    # TODO: Enviar al server de luces
    return command_output

# Ejecuta el servidor de desarrollo
if __name__ == '__main__':
    app.run(port=8080) # El modo debug muestra errores y reinicia automáticamente el servidor al hacer cambios
