from gtts import gTTS
from playsound import playsound 

ip = input("Enter the text you want to convert to speech: ") 

audio = gTTS(text = ip,lang = "en") 
audio.save("audio.mp3") 
playsound("./audio.mp3")
