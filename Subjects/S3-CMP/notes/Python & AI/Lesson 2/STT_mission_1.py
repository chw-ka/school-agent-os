#導入函數庫
import speech_recognition as sr

#使用函數庫的函數(FUNCTION)定義麥克風
recongizer = sr.Recognizer()
mic = sr.Microphone()

while True:
    with mic as source:
        #輸入語音
        print("Please speak something..")
        recongizer.adjust_for_ambient_noise(source)
        audio = recongizer.listen(source)

    #轉文字
    try:
          text = recongizer.recognize_google(audio, language="en")
          print("You said:", text)
    except sr.UnknownValueError:
         print("sorry, I could not understand what you said")
    except sr.RequestError:
         print("There is an error with the speech recognition")
     
    if text == "finish":
        break