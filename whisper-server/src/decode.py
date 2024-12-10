import whisper
import librosa
import logging
import os
from utils import get_audio_metadata, array_to_wav
import numpy as np
from scipy.signal import butter, filtfilt

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Opciones de modelos:
# - "tiny": 39M parámetros
# - "base": 74M parámetros
# - "small": 244M parámetros
# - "medium": 769M parámetros
# - "large": 1550M parámetros

# Cargar modelo small para mejor balance entre precisión y recursos
model = whisper.load_model("base")

def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def enhance_audio(audio, sr):
    """
    Mejora el audio optimizando para las palabras 'prender' y 'apagar'
    """
    enhancement_config = {
        "stft": {
            "n_fft": 256,             # Ventana más grande para mejor frecuencia
            "hop_length": 128,        # Hop length ajustado
            "noise_reduction_factor": 3  # Menos agresivo con el ruido
        },
        "highpass": {
            "cutoff": 300,           # Frecuencia de corte más baja
            "order": 3               # Orden más bajo para menos distorsión
        },
        "duration": 10.0            # Duración máxima más larga
    }
    
    try:
        # Asegurar que el audio no exceda 3 segundos
        max_samples = int(sr * enhancement_config["duration"])
        if len(audio) > max_samples:
            audio = audio[:max_samples]
        
        # Normalización y preprocesamiento
        audio = audio.astype(np.float32)
        audio = librosa.util.normalize(audio)
        
        # Aplicar filtro pasa alto
        b, a = butter_highpass(
            cutoff=enhancement_config["highpass"]["cutoff"],
            fs=sr,
            order=enhancement_config["highpass"]["order"]
        )
        audio_filtered = filtfilt(b, a, audio)
        
        # Procesamiento STFT con ventanas más pequeñas
        D = librosa.stft(
            audio_filtered, 
            n_fft=enhancement_config["stft"]["n_fft"],
            hop_length=enhancement_config["stft"]["hop_length"]
        )
        D_mag, D_phase = librosa.magphase(D)
        
        # Reducción de ruido suave
        noise_thresh = np.median(np.abs(D_mag)) * enhancement_config["stft"]["noise_reduction_factor"]
        D_mag = np.maximum(0, np.abs(D_mag) - noise_thresh)
        
        # Reconstrucción
        D = D_mag * D_phase
        audio_enhanced = librosa.istft(
            D, 
            hop_length=enhancement_config["stft"]["hop_length"]
        )
        
        # Guardar el audio mejorado
        array_to_wav(
            audio_enhanced.astype(np.float32),
            './audio/enhanced_audio.wav',
            sr
        )
        logger.info("Audio mejorado guardado en ./audio/enhanced_audio.wav")
        
    except Exception as e:
        logger.error(f"Error en mejora de audio: {e}")

def process_command(text):
    """
    Procesa el texto reconocido para identificar comandos con más tolerancia
    """
    text = text.lower().strip()
    logger.info(f"Procesando texto: '{text}'")
    
    # Palabras clave para prender
    prender_keywords = ['prend', 'encend', 'prende', 'enciend']
    # Palabras clave para apagar
    apagar_keywords = ['apag', 'apague']
    
    # Buscar coincidencias para prender
    for keyword in prender_keywords:
        if keyword in text:
            logger.info(f"Comando PRENDER detectado (keyword: {keyword})")
            return "TURN_ON"
    
    # Buscar coincidencias para apagar
    for keyword in apagar_keywords:
        if keyword in text:
            logger.info(f"Comando APAGAR detectado (keyword: {keyword})")
            return "TURN_OFF"
    
    logger.info(f"No se reconoció el comando: {text}")
    return "UNKNOWN"

def decode_audio(audio_path):
    """
    Decodifica el audio optimizado para detectar la letra A
    """
    try:
        # Configurar opciones de Whisper optimizadas
        options = {
            "language": "es",
            "initial_prompt": "En este audio se escucha la palabra 'prender'."
        }
        
        # Transcribir audio
        result = model.transcribe(audio_path, **options)
        texto_reconocido = result["text"].strip().lower()
        logger.info(f"Texto reconocido: '{texto_reconocido}'")
        
        # Procesar el comando
        comando = "TURN_ON" if "prender" in texto_reconocido else "UNKNOWN"
        logger.info(f"Comando identificado: {comando}")
        
        return comando
            
    except Exception as e:
        logger.error(f"Error en la decodificación: {str(e)}")
        return "ERROR"
