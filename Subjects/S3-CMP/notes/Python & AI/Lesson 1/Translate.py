from google.cloud import translate_v2 as translate
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "password.json"

client = translate.Client()
text = input("Enter English text: ")
result = client.translate(text, source_language="en", target_language="zh")
print("Translation:", result["translatedText"])