from flask import Flask
from decode import decode_audio


app = Flask(__name__)  # Crea una instancia de la aplicación Flask

# Define una ruta y una función de vista para la URL raíz
@app.route('/')
def index():
    return "¡Hola, mundo! Este es mi servidor Flask básico."

@app.route('/decode')
def decode():
    return decode_audio()

# Ejecuta el servidor de desarrollo
if __name__ == '__main__':
    app.run(port=8080, debug=True) # El modo debug muestra errores y reinicia automáticamente el servidor al hacer cambios
