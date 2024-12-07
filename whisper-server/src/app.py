from flask import Flask
from decode import decode_audio, enhance_audio
from actions import set_command
from udp import ServidorUDP
import librosa
from utils import get_audio_metadata, array_to_wav
import threading
import logging

# Configurar logging
logging.basicConfig(
    filename='./log/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def udp_listener():
    """
    Función que se ejecuta en un thread separado para escuchar UDP
    """
    while True:
        try:
            # Esperar datos UDP de forma bloqueante
            data, addr = servidor_udp.receive_udp("0.0.0.0", 12345)
            if data:
                print(f"Datos UDP recibidos desde {addr}: {data}")
                # Aquí puedes procesar los datos recibidos
        except Exception as e:
            print(f"Error en listener UDP: {e}")

def iniciar_servidor_udp():
    global servidor_udp
    servidor_udp = ServidorUDP()
    
    # Iniciar thread para escuchar UDP
    udp_thread = threading.Thread(target=udp_listener)
    udp_thread.daemon = True  # El thread se cerrará cuando el programa principal termine
    udp_thread.start()

@app.route('/', methods=['GET'])
def decode():
    audio_path = './audio/audio_1.wav'
    
    try:
        # Cargar y mejorar el audio
        metadata = get_audio_metadata(audio_path)
        sr = metadata["sample_rate"] if metadata else 16000
        
        # Cargar el audio
        audio, _ = librosa.load(audio_path, sr=sr, mono=True)
        
        # Aplicar mejoras
        enhance_audio(audio, sr)
        enhanced_path = './audio/enhanced_audio.wav'
        
        # Procesar el audio mejorado
        output = decode_audio(enhanced_path)
        
        command_output = set_command(str(output))
        
        # Obtener el comando hexadecimal directamente
        command = command_output["command"]
        
        return command_output
        
    except Exception as e:
        error_msg = f"Error procesando audio: {str(e)}"
        print(error_msg)
        return {"error": error_msg}

if __name__ == '__main__':
    iniciar_servidor_udp()
    app.run(host="localhost", port=8082)
