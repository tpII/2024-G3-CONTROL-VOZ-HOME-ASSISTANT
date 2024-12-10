import soundfile as sf
import logging

logger = logging.getLogger(__name__)

def get_audio_metadata(audio_path):
    """
    Obtiene los metadatos del archivo de audio usando soundfile
    """
    try:
        with sf.SoundFile(audio_path) as audio_file:
            metadata = {
                "sample_rate": audio_file.samplerate,
                "channels": audio_file.channels,
                "format": audio_file.format,
                "subtype": audio_file.subtype,
                "frames": audio_file.frames,
                "duration": float(audio_file.frames) / float(audio_file.samplerate),
                "seekable": audio_file.seekable()
            }
            return metadata
    except Exception as e:
        logger.error(f"Error obteniendo metadatos: {str(e)}")
        return None

def array_to_wav(array, filename, sr=16000):
    """
    Convierte un array de numpy a un archivo WAV
    """
    sf.write(filename, array, sr)
