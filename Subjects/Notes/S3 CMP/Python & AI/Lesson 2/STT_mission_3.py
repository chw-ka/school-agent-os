from gtts import gTTS
from playsound import playsound
from google.cloud import translate_v2 as translate
import os
import speech_recognition as sr

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "password.json"
recongizer = sr.Recognizer()
mic = sr.Microphone()
client = translate.Client()

with mic as source:
    print("Please speak something..")
    recongizer.adjust_for_ambient_noise(source)
    audio = recongizer.listen(source)

try:
    text = recongizer.recognize_google(audio, language="yue")
    print("You said:", text)
except sr.UnknownValueError:
    print("sorry, I could not understand what you said")
except sr.RequestError:
    print("There is an error with the speech recognition")

result = client.translate(text, source_language="yue", target_language="en")
print("Translation:", result["translatedText"])

audio = gTTS(text = result["translatedText"],lang = "en") 
audio.save("audio.mp3") 
playsound("./audio.mp3")
