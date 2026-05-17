from gtts import gTTS
from playsound import playsound
import os

text = input("Enter the text you want to convert to speech: ")

audio = gTTS(text=text, lang="en")
audio.save("output.mp3")
playsound("output.mp3")
os.remove("output.mp3")
