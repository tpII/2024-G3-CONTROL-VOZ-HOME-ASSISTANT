import whisper
import librosa
import logging
import os
from utils import get_audio_metadata, array_to_wav
import numpy as np
from scipy.signal import butter, filtfilt

# Configurar logging para stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Cargar el modelo una sola vez como variable global


def butter_highpass(cutoff, fs, order=5):
    """Diseña un filtro pasa alto Butterworth"""
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def enhance_audio(audio, sr):
    """
    Mejora el audio optimizando para la palabra 'Alexa'
    """
    enhancement_config = {
        "stft": {
            "n_fft": 1024,            # Ventana más pequeña para mejor resolución temporal
            "hop_length": 256,        
            "noise_reduction_factor": 2.0  # Más agresivo con el ruido
        },
        "highpass": {
            "cutoff": 200,           # Reducido para capturar mejor frecuencias vocales
            "order": 4               
        },
        "duration": 4.0
    }
    
    try:
        # Asegurar que el audio esté en float32
        audio = audio.astype(np.float32)
        
        # 1. Normalización inicial
        audio = librosa.util.normalize(audio)
        
        # 2. Reducción de ruido usando STFT
        D = librosa.stft(
            audio, 
            n_fft=enhancement_config["stft"]["n_fft"],
            hop_length=enhancement_config["stft"]["hop_length"]
        )
        D_mag, D_phase = librosa.magphase(D)
        
        # Calcular y aplicar umbral de ruido
        noise_thresh = np.median(np.abs(D_mag)) * enhancement_config["stft"]["noise_reduction_factor"]
        D_mag = np.maximum(0, np.abs(D_mag) - noise_thresh)
        
        # Reconstruir señal
        D = D_mag * D_phase
        audio_denoised = librosa.istft(
            D, 
            hop_length=enhancement_config["stft"]["hop_length"]
        )
        
        # 3. Filtro pasa alto para eliminar ruidos de baja frecuencia
        b, a = butter_highpass(
            cutoff=enhancement_config["highpass"]["cutoff"],
            fs=sr,
            order=enhancement_config["highpass"]["order"]
        )
        audio_filtered = filtfilt(b, a, audio_denoised)
        
        # 4. Guardar el audio mejorado
        array_to_wav(
            audio_filtered.astype(np.float32),
            './audio/enhanced_audio.wav',
            sr
        )
        logger.info("Audio mejorado guardado en ./audio/enhanced_audio.wav")
        
    except Exception as e:
        logger.error(f"Error en mejora de audio: {e}")

def decode_audio(audio_path):
    """
    Decodifica el audio optimizado para detectar la palabra 'Alexa'
    """
    try:
        # Cargar modelo
        model = whisper.load_model("base")
        
        # Configurar opciones específicas para detectar "Alexa"
        options = {
            "language": "es",
            "initial_prompt": "El audio contiene la palabra Alexa. Alexa es una palabra clave.",
            "temperature": 0,  # Reducir variabilidad
            "best_of": 5,     # Aumentar intentos de decodificación
            "beam_size": 5,   # Aumentar búsqueda de beam
            "compression_ratio_threshold": 1.5,  # Más permisivo con repeticiones
            "no_speech_threshold": 0.4,  # Más permisivo con audio poco claro
        }
        
        # Transcribir con las opciones optimizadas
        result = model.transcribe(audio_path, **options)
        
        logger.info(f"Texto reconocido: {result['text']}")
        # Retornar texto procesado
        return result["text"].strip().lower()
            
    except Exception as e:
        logger.error(f"Error en la decodificación: {str(e)}")
        return f"Error en la decodificación: {str(e)}"
