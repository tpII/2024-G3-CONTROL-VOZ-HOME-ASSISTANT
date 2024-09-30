import whisper
import librosa
import numpy as np
from utils import __array_to_wav

def decode_audio(audio):
    model = whisper.load_model("base")
    audio = whisper.load_audio(audio)
    result = model.transcribe(audio, language="es")["text"]
    print(f"El resultado es: {result}")
    return str(result), 200


def remove_silence_librosa(audio_path, output_name, top_db=30, frame_length=2048, hop_length=512):
    # Cargar el archivo de audio
    audio, sr = librosa.load(audio_path, sr=None)
    # Detectar los intervalos de sonido (donde no hay silencio)
    non_silent_intervals = librosa.effects.split(audio, top_db=top_db, frame_length=frame_length, hop_length=hop_length)
    # Unir los fragmentos de audio que no son silencio
    non_silent_audio = np.concatenate([audio[start:end] for start, end in non_silent_intervals])
    __array_to_wav(non_silent_audio, output_name)