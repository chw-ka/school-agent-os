#導入函數庫
import speech_recognition as sr

#使用函數庫的函數(FUNCTION)定義麥克風
recongizer = sr.Recognizer()
mic = sr.Microphone()
answer = "孤掌難鳴"

while True:
     with mic as source:
          #輸入語音
          print("一個巴掌拍不響,猜一成語:")
          recongizer.adjust_for_ambient_noise(source)
          audio = recongizer.listen(source)

          #轉文字
          try:
               text = recongizer.recognize_google(audio, language="yue")
               print("Your answer:", text)
               if (answer == text):
                    print("Correct!")
                    break
               else:
                    print("Wrong Answer, try again!")

          except sr.UnknownValueError:
               print("sorry, I could not understand what tou said")
          except sr.RequestError:
               print("There is an error with the speech recognition")