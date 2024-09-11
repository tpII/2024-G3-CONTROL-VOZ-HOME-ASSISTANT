import whisper
import time


def decode_audio():
    model = whisper.load_model("base")

    # load audio and pad/trim it to fit 30 seconds
    audio = whisper.load_audio("./audio/dross-audio.mp3")

    audio = whisper.pad_or_trim(audio)

    # make log-Mel spectrogram and move to the same device as the model
    mel = whisper.log_mel_spectrogram(audio).to(model.device)

    # detect the spoken language
    _, probs = model.detect_language(mel)
    print(f"Detected language: {max(probs, key=probs.get)}")

    # decode the audio
    options = whisper.DecodingOptions()

    start_time = time.time()


    result = whisper.decode(model, mel, options)

    # print the recognized text
    print(result.text)

    end_time = time.time()

    # Cálculo del tiempo transcurrido
    execution_time = round(end_time - start_time, 4)
    print(f"El resultado es: {result}")
    print(f"El tiempo de ejecución fue: {execution_time} segundos")
    return "El tiempo de ejecución fue: " + str(execution_time) + " segundos", 200