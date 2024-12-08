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
    Función que se ejecuta en un thread separado para escuchar UDP continuamente
    """
    while True:
        try:
            # Esperar datos UDP de forma bloqueante
            data, addr = servidor_udp.sock.recvfrom(1024*2+4)
            if data:
                logger.info(f"📦 Datos UDP recibidos desde {addr}")
                
                # Convertir datos a formato numérico
                received_data = [int.from_bytes(data[i:i+2], 'little') 
                               for i in range(0, len(data) - 2, 2)]
                
                # Agregar datos al buffer
                servidor_udp.collected_data.extend(received_data)
                
                # Si tenemos suficientes datos, intentar guardar
                if len(servidor_udp.collected_data) >= 15000 * 2:  # 2 segundos de audio
                    wav_path = servidor_udp.guardar_wav(servidor_udp.collected_data)
                    if wav_path:
                        logger.info(f"✅ Audio guardado: {wav_path}")
                    # Limpiar el buffer
                    servidor_udp.collected_data = []
                
        except Exception as e:
            logger.error(f"❌ Error en listener UDP: {e}")
            time.sleep(0.1)  # Pequeña pausa antes de reintentar

def process_audio(audio_path):
    """
    Procesa un archivo de audio y ejecuta el comando correspondiente
    """
    try:
        # Cargar y mejorar el audio
        metadata = get_audio_metadata(audio_path)
        sr = metadata["sample_rate"] if metadata else 16000
        
        # Cargar el audio
        audio, _ = librosa.load(audio_path, sr=sr, mono=True)
        
        # Aplicar mejoras
        enhance_audio(audio, sr)
        enhanced_path = './audio/enhanced_audio.wav'
        
        # Procesar el audio mejorado y obtener el texto
        command_output = decode_audio(enhanced_path)
        logger.info(f"🎯 Texto detectado: {command_output}")
        
        # Enviar el comando al dispositivo
        try:
            # Crear socket UDP para enviar el comando
            sock_comando = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Enviar el comando al dispositivo (ajusta IP y puerto según necesites)
            sock_comando.sendto(str(command_output).encode(), ("192.168.1.66", 12345))
            logger.info(f"📤 Comando enviado: {command_output}")
            sock_comando.close()
            
            # Ejecutar el comando localmente si es necesario
            command_output = set_command(str(command_output))
            
            # Eliminar el archivo procesado
            servidor_udp.eliminar_wav_antiguo()
            
            return {
                "texto": command_output,
                "comando_enviado": True,
                "resultado_local": command_output
            }
            
        except Exception as e:
            error_msg = f"❌ Error enviando comando: {str(e)}"
            logger.error(error_msg)
            return {
                "texto": command_output,
                "comando_enviado": False,
                "error": error_msg
            }
        
    except Exception as e:
        error_msg = f"❌ Error procesando audio {audio_path}: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}

@app.route('/', methods=['GET'])
def process_all_audio():
    """
    Procesa todos los archivos de audio pendientes
    """
    results = []
    try:
        # Procesar todos los archivos en la lista
        while servidor_udp.archivos_wav:
            audio_path = servidor_udp.archivos_wav[0]  # Tomar el primer archivo
            result = process_audio(audio_path)
            results.append({
                "audio": audio_path,
                "result": result
            })
        
        return jsonify({
            "status": "success",
            "processed_files": len(results),
            "results": results
        })
            
    except Exception as e:
        error_msg = f"❌ Error procesando audios: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            "status": "error",
            "message": error_msg,
            "processed_files": len(results),
            "results": results
        })

def iniciar_servidor_udp():
    global servidor_udp
    servidor_udp = ServidorUDP()
    
    # Iniciar thread para escuchar UDP
    udp_thread = threading.Thread(target=udp_listener)
    udp_thread.daemon = True
    udp_thread.start()
    
    logger.info("🚀 Servidor UDP iniciado y escuchando")

if __name__ == '__main__':
    iniciar_servidor_udp()
    app.run(host="localhost", port=8082)
