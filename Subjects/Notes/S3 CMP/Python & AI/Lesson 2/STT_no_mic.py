#導入函數庫
import speech_recognition as sr

#使用函數庫的函數(FUNCTION)
recognizer = sr.Recognizer()

audio_file = "./audio.wav"
with sr.AudioFile(audio_file) as source:
    audio_data = recognizer.record(source)

#轉文字
try:
     text = recognizer.recognize_google(audio_data, language="yue")
     print("You said:", text)
except sr.UnknownValueError:
     print("sorry, I could not understand what you said")
except sr.RequestError:
     print("There is an error with the speech recognition")
