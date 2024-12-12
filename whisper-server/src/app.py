from flask import Flask, jsonify
from decode import decode_audio, enhance_audio
from actions import set_command
from udp import ServidorUDP
import librosa
from utils import get_audio_metadata, array_to_wav
import threading
import logging
import os
import time
import socket

# Configurar logging para stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


def iniciar_servidor():
    global servidor_udp
    
    # Crear directorios si no existen
    os.makedirs('./audio', exist_ok=True)
    os.makedirs('./udp_audios', exist_ok=True)
    
    WHISPER_IP          = os.getenv("WHISPER_IP", "192.168.1.67")
    WHISPER_PORT        = os.getenv("WHISPER_PORT", 8082)
    WEMOS_IP            = os.getenv("WEMOS_IP", "192.168.1.65")
    WEMOS_PORT          = os.getenv("WEMOS_PORT", 4444)
    # Iniciar servidor UDP
    server_udp_config = {
        "host": str(WHISPER_IP),
        "port": int(WEMOS_PORT)
    }

    servidor_udp = ServidorUDP(**server_udp_config)
    udp_thread = threading.Thread(target=servidor_udp.udp_listener)
    udp_thread.daemon = True
    udp_thread.start()
    
    # Iniciar procesamiento de audio
    process_thread = threading.Thread(target=process_audio_loop)
    process_thread.daemon = True
    process_thread.start()
    
    # Iniciar garbage collector
    #gc_thread = threading.Thread(target=garbage_collector)
    #gc_thread.daemon = True
    #gc_thread.start()
    
    logging.info("🚀 Servidor iniciado y procesando")
    

def process_audio(audio_path):
    """
    Procesa un archivo de audio corto y ejecuta el comando correspondiente
    """
    try:
        # Cargar y mejorar el audio
        metadata = get_audio_metadata(audio_path)
        sr = metadata["sample_rate"] if metadata else 16000
        
        # Cargar el audio limitando a 3 segundos
        audio, _ = librosa.load(
            audio_path, 
            sr=sr, 
            mono=True
        )
        
        # Aplicar mejoras optimizadas para clips cortos
        enhance_audio(audio, sr)
        enhanced_path = './audio/enhanced_audio.wav'
        
        # Procesar el audio mejorado y obtener el texto
        decoded_audio = decode_audio(enhanced_path)
        logger.info(f"🎯 Texto detectado: {decoded_audio}")
        
        command_output = set_command(str(decoded_audio)).get('command')


        datos = bytes.fromhex(command_output)


        # Enviar el comando al dispositivo
        try:
            
            # Crear socket UDP
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # Enviar datos
            sock.sendto(datos, ("192.168.1.65", 4444))
            logger.info(f"📤 Comando enviado: {datos}")
            sock.close()
            
            # Ejecutar el comando localmente si es necesario
            
            
            # Eliminar el archivo procesado
            servidor_udp.eliminar_wav_antiguo()
            
            return {
                "texto": command_output,
                "comando_enviado": True,
                "comando_hex": f"0x{command_output}",
                "status": "success"
            }
            
        except Exception as e:
            error_msg = f"❌ Error enviando comando: {str(e)}"
            logger.error(error_msg)
            return {
                "texto": command_output,
                "comando_enviado": False,
                "comando_hex": f"0x{command_output}",
                "error": error_msg,
                "status": "error"
            }
        
    except Exception as e:
        error_msg = f"❌ Error procesando audio {audio_path}: {str(e)}"
        logger.error(error_msg)
        return {
            "error": error_msg,
            "status": "error"
        }

def process_audio_loop():
    """
    Thread dedicado a procesar archivos de audio continuamente
    """
    while True:
        try:
            # Esperar hasta que haya archivos para procesar
            while not servidor_udp.archivos_wav:
                time.sleep(0.5)
                logging.info("⏳ Esperando archivos de audio...")
            
            # Procesar el archivo más antiguo
            audio_path = servidor_udp.archivos_wav[0]
            result = process_audio(audio_path)
            logging.info(f"✅ Archivo procesado: {audio_path}")
            
        except Exception as e:
            error_msg = f"❌ Error procesando audio: {str(e)}"
            logger.error(error_msg)
            time.sleep(1)  # Esperar antes de reintentar

@app.route('/', methods=['GET'])
def get_status():
    """
    Endpoint para verificar el estado del servidor
    """
    return jsonify({
        "status": "running",
        "pending_files": len(servidor_udp.archivos_wav)
    })

def garbage_collector():
    """
    Thread dedicado a limpiar archivos de audio antiguos
    """
    DIRECTORIOS = ['./audio', './udp_audios']
    MAX_EDAD_ARCHIVO = 3000  # 5 minutos en segundos
    
    while True:
        try:
            tiempo_actual = time.time()
            
            for directorio in DIRECTORIOS:
                if not os.path.exists(directorio):
                    continue
                    
                for archivo in os.listdir(directorio):
                    ruta_archivo = os.path.join(directorio, archivo)
                    
                    # Verificar si es un archivo WAV
                    if not archivo.endswith('.wav'):
                        continue
                    
                    # Obtener edad del archivo
                    edad_archivo = tiempo_actual - os.path.getctime(ruta_archivo)
                    
                    # Eliminar si es muy antiguo
                    if edad_archivo > MAX_EDAD_ARCHIVO:
                        try:
                            #os.remove(ruta_archivo)
                            logging.info(f"🗑️ GC: Archivo eliminado por antigüedad: {ruta_archivo}")
                        except Exception as e:
                            logging.error(f"❌ GC: Error eliminando archivo {ruta_archivo}: {str(e)}")
            
            # Dormir por 60 segundos antes de la siguiente limpieza
            time.sleep(60)
            
        except Exception as e:
            logging.error(f"❌ Error en garbage collector: {str(e)}")
            time.sleep(60)


if __name__ == '__main__':
    iniciar_servidor()
    app.run(host="0.0.0.0", port=8082)
