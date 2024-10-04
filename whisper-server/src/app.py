from flask import Flask
from decode import decode_audio, remove_silence_librosa
import time

app = Flask(__name__)  # Crea una instancia de la aplicación Flask

# Define una ruta y una función de vista para la URL raíz
@app.route('/')
def index():
    return "Servidor de Whisper."

@app.route('/decode')
def decode():
    start_time = time.time()

    remove_silence_librosa('./audio/dross_audio.wav', 'output.wav')
    output = decode_audio('output.wav')

    end_time = time.time()

    execution_time = round(end_time - start_time, 4)

    print(f"El tiempo de ejecución fue: {execution_time} segundos")
    
    return output

# Ejecuta el servidor de desarrollo
if __name__ == '__main__':
    app.run(port=8080) # El modo debug muestra errores y reinicia automáticamente el servidor al hacer cambios
