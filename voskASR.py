import speech_recognition as sr
import wave
import config

def are_nariks_speaking(words, sink, recognizer):
    with wave.open(config.AUDIO_FILE, mode='wb') as f:
        f.setparams(config.PARAMS)
        f.writeframes(sink.fp.read())
    with sr.AudioFile(config.AUDIO_FILE) as source:
        audio = recognizer.record(source)

    result = parse_voice_data(sink, recognizer, audio)
    for word in words:
        if word in result:
            return True


def parse_voice_data(sink, recognizer, audio):
    try:
        result = sink.filename + " " + recognizer.recognize_vosk(audio, language="ru")
        if result != "":
            print("Vosk: " + result)
            write_to_file(result)
            return result
    except sr.UnknownValueError:
        print("Unknown value Err")
    except sr.RequestError:
        print("Request Err")


def write_to_file(data):
    with open('results.txt', 'a') as f:
        f.write(data + '\n')
