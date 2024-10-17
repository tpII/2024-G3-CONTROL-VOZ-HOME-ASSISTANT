import soundfile as sf
import numpy as np
from scipy.io.wavfile import write

def check_audio_metadata(audio_input):
    f = sf.SoundFile(audio_input)
    print("Metadatos del audio")
    print("Formato: " + str(f.format))
    print("Subtipo: " + str(f.subtype)) 
    print("Endian: " + str(f.endian))


def array_to_wav(array, file, sample_rate=44100):
    # Verificar que el array esté en el rango de -1 a 1
    if np.max(np.abs(array)) > 1.0:
        print("Los datos del array están fuera del rango [-1, 1]. Se escalarán automáticamente.")
        array = array / np.max(np.abs(array))
    audio_data = np.uint8((array + 1) * 127.5)  # Escalamos de [-1, 1] a [0, 255]. 8 bits de datos de entrada mulitplicado por factor de escala para acomodar a wav
    # Guardar el array como un archivo WAV
    write(file, sample_rate, audio_data)
