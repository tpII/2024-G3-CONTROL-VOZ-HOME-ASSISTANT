import whisper
import librosa
import logging
from scipy.signal import resample, butter, lfilter
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


def resample_audio(audio_data, original_rate, target_rate):
    """Resample the audio to a higher frequency."""
    num_samples = int(len(audio_data) * (target_rate / original_rate))
    return resample(audio_data, num_samples)

def apply_highpass_filter(audio_data, cutoff_freq, sample_rate):
    """Apply a high-pass filter to remove low frequencies."""
    nyquist = sample_rate / 2
    normal_cutoff = cutoff_freq / nyquist
    b, a = butter(5, normal_cutoff, btype='high', analog=False)
    return lfilter(b, a, audio_data)
    

def enhance_audio(audio, sr):
    """
    Mejora el audio optimizando para la palabra 'Prender y Apagar'
    """
    enhancement_config = {
        "resample": {
            "original_frame": 12000,            # Ventana más pequeña para mejor resolución temporal
            "target_rate": 14000,        
            "noise_reduction_factor": 3.0  # Más agresivo con el ruido
        },
        "highpass": {
            "cutoff": 100,           # Reducido para capturar mejor frecuencias vocales
            "target_rate": 14000,              
        },
        "butter": {
            "cutoff": 300,
            "fs": 10000
        },
        "duration": 4.0
    }
    
    try:
        # Asegurar que el audio esté en float32
        audio = audio.astype(np.float32)
        
        resampled_audio = resample_audio(audio, enhancement_config["resample"]["original_frame"], enhancement_config["resample"]["target_rate"])

        filtered_audio = apply_highpass_filter(resampled_audio, enhancement_config["highpass"]["cutoff"], enhancement_config["highpass"]["target_rate"])

        normalized_audio = np.int16(butterd_audio / np.max(np.abs(filtered_audio)) * 32767)

        # 4. Guardar el audio mejorado
        array_to_wav(
            normalized_audio.astype(np.float32),
            './audio/enhanced_audio.wav',
            sr
        )
        logger.info("Audio mejorado guardado en ./audio/enhanced_audio.wav")
        
    except Exception as e:
        logger.error(f"Error en mejora de audio: {e}")

def decode_audio(audio_path):
    """
    Decodifica el audio optimizado para detectar las palabras 'Prender' o 'Apagar'
    """
    try:
        # Cargar modelo
        model = whisper.load_model("base")
        
        # Configurar opciones específicas para detectar "Prender" o "Apagar"
        options = {
            "language": "es",
            "initial_prompt": "El audio contiene una de las palabras clave: 'Prender'",
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
