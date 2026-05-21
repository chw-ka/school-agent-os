from gtts import gTTS
from playsound import playsound 

while True:
    ip = input("Enter the Chinese text you want to convert to speech: ") 
    
    if ip == "Q":
        break
    else:
        audio = gTTS(text = ip,lang = "zh-CN") 
        audio.save("audio.mp3") 
        playsound("./audio.mp3")
