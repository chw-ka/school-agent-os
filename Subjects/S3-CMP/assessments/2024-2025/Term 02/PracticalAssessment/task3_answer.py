# task3_2425.py

# Step (b): Import the Text-to-Speech library and playsound
from gtts import gTTS
from playsound import playsound

# Step (c): Ask the user for a sentence to convert to speech
text = input("Please enter a sentence to convert to speech: ")

# Step (e): Save the audio output as an mp3 file
audio_file = "output.mp3"
tts = gTTS(text=text, lang='en')
tts.save(audio_file)

# Step (f): Play the mp3 file
playsound(audio_file)

# Step (g): Print a confirmation message after saving
print(f"{text} has been converted and played.")