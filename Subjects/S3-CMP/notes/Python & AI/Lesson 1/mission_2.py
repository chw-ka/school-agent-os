from google.cloud import translate_v2 as translate
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "password.json"

client = translate.Client()
while True:
    text = input("Enter Chinese text: ")
    if text == "Q":
        break
    else:
        result = client.translate(text, source_language="zh", target_language="en")
        print("Translation:", result["translatedText"])