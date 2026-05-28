from gtts import gTTS
from playsound import playsound
import os

print("=== 智能播音員 ===")
print('輸入 "Q" 退出。')

# 只詢問一次語言
lang = input("語言 (en/zh)：").strip().lower()
if lang not in ("en", "zh"):
    lang = "en"

while True:
    msg = input("訊息：").strip()
    if msg.upper() == "Q":
        break

    audio = gTTS(text=msg, lang=lang)
    audio.save("output.mp3")
    playsound("output.mp3")
    os.remove("output.mp3")

