import whisper
import librosa
import logging
from scipy.signal import resample, butter, lfilter
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
    


def pre_enhance_audio(audio, sr):
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

def enhance_audio(audio, sr):
    """
    Mejora el audio optimizando para las palabras 'prender' y 'apagar'
    """
    enhancement_config = {
        "resample": {
            "original_frame": 8000,            # Ventana más pequeña para mejor resolución temporal
            "target_rate": 9000,        
            "noise_reduction_factor": 10.0  # Más agresivo con el ruido
        },
        "highpass": {
            "cutoff": 300,           # Reducido para capturar mejor frecuencias vocales
            "target_rate": 9000,              
        },
        "stft": {
            "n_fft": 256,
            "hop_length": 128,
            "noise_reduction_factor": 3

        },
        "butter": {
            "cutoff": 300,
            "fs": 10000
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
        
        
        # Procesamiento STFT con ventanas más pequeñas
        D = librosa.stft(
            audio, 
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

        # 4. Guardar el audio mejorado
        array_to_wav(
            audio_enhanced.astype(np.float32),
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
            "initial_prompt": "El audio contiene una de las palabras clave: 'Prender' y 'Apagar' seguido de Alexa",
            "temperature": 0,  # Reducir variabilidad
            "best_of": 5,     # Aumentar intentos de decodificación
            "beam_size": 5,   # Aumentar búsqueda de beam
            "compression_ratio_threshold": 1.5,  # Más permisivo con repeticiones
            "no_speech_threshold": 0.4,  # Más permisivo con audio poco claro
        }
        
        # Transcribir audio
        result = model.transcribe(audio_path, **options)
        texto_reconocido = result["text"].strip().lower()
        logger.info(f"Texto reconocido: '{texto_reconocido}'")
        
        # Procesar el comando
        comando = (
            "TURN_ON" if "prender" in texto_reconocido else
            "TURN_OFF" if "apagar" in texto_reconocido else
            "UNKNOWN"
        )
        logger.info(f"Comando identificado: {comando}")
        
        return comando
            
    except Exception as e:
        logger.error(f"Error en la decodificación: {str(e)}")
        return "ERROR"
