import json

import speech_recognition as sr
import wave
import config


def are_nariks_speaking(words, sink, recognizer):
    with wave.open(config.AUDIO_FILE, mode="wb") as f:
        f.setparams(config.PARAMS)
        f.writeframes(sink.fp.read())
    with sr.AudioFile(config.AUDIO_FILE) as source:
        audio = recognizer.record(source)

    phrase = parse_voice_data(sink, recognizer, audio)
    if phrase:
        for word in words:
            if word in phrase:
                return True


def parse_voice_data(sink, recognizer, audio):
    try:
        data = recognizer.recognize_vosk(audio, language="ru")
        parsed_data = json.loads(data)
        if parsed_data["text"] is not "":
            result = sink.filename + ": " + data
            print(result)
            # write_to_file(result)
            return result
    except sr.UnknownValueError:
        print("Unknown value Err")
    except sr.RequestError:
        print("Request Err")


def write_to_file(data):
    with open("results.txt", "a") as f:
        f.write(data + "\n")
