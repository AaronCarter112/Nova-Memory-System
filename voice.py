import os
from gtts import gTTS
import speech_recognition as sr

class STTEngine:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def transcribe_bytes(self, audio_bytes: bytes) -> str:
        with open("temp.wav", "wb") as f:
            f.write(audio_bytes)
        with sr.AudioFile("temp.wav") as source:
            audio = self.recognizer.record(source)
        try:
            return self.recognizer.recognize_google(audio)
        except:
            return ""

class TTSEngine:
    def speak(self, text: str):
        tts = gTTS(text=text, lang='en')
        tts.save("response.mp3")
        # Use 'start' for Windows
        os.system("start response.mp3")