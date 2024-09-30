from pydub import AudioSegment
from pydub.silence import split_on_silence

# Elimina los silencios de un archivo .wav y guarda el archivo resultante.
def remove_silence(input_wav, output_wav):

    #silence_thresh: Umbral de silencio en dBFS (decibelios por debajo del nivel de pico).
    silence_thresh=-50 
    
    #min_silence_len: Duración mínima del silencio en milisegundos.
    min_silence_len=500 

    #keep_silence: Duración del silencio que se conservará en milisegundos entre fragmentos.
    keep_silence=100
    
    # Cargar el archivo de audio
    audio = AudioSegment.from_wav(input_wav)
    
    # Dividir el audio en fragmentos eliminando los silencios
    chunks = split_on_silence(audio, 
                              min_silence_len=min_silence_len, 
                              silence_thresh=silence_thresh, 
                              keep_silence=keep_silence)
    
    # Unir los fragmentos en un solo archivo de audio
    processed_audio = AudioSegment.silent(duration=0)
    for chunk in chunks:
        processed_audio += chunk
    
    # Exportar el archivo procesado
    processed_audio.export(output_wav, format="wav")
    print(f"Archivo exportado a: {output_wav}")


remove_silence()