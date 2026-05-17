# (b) line 2
import speech_recognition as sr

# (c) line 6 - 7
# Set up recognizer and microphone
recognizer = sr.Recognizer()
mic = sr.Microphone()

# List to store sentences
spoken_sentences = []

while True:
    # (d) line 17, 18, 21
    # Record audio
    with mic as source:
        print("Please say a sentence in English (say 'stop' to finish):")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio, language="en")
            print("You said:", text)

            if text.lower() == "stop":
                break

            spoken_sentences.append(text)

        except sr.UnknownValueError:
            print("Sorry, I could not understand what you said.")
        except sr.RequestError:
            print("There was an error with the speech recognition service.")

# (e) line 35
print(spoken_sentences)
