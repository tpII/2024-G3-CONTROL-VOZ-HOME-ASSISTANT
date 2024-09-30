import soundfile as sf
import numpy as np
from scipy.io.wavfile import write

def check_audio_metadata(audio_input):
    f = sf.SoundFile(audio_input)
    print("Metadatos del audio")
    print("Formato: " + str(f.format))
    print("Subtipo: " + str(f.subtype)) 
    print("Endian: " + str(f.endian))


def __array_to_wav(array, file, sample_rate=44100, duration=2, frequency=440):
    # Verificar que el array esté en el rango de -1 a 1
    if np.max(np.abs(array)) > 1.0:
        print("Los datos del array están fuera del rango [-1, 1]. Se escalarán automáticamente.")
        array = array / np.max(np.abs(array))
    audio_data = np.int16(array * 32767)
    # Guardar el array como un archivo WAV
    write(file, sample_rate, audio_data)

