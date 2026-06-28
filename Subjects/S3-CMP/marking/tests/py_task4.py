import aia_util as aia_utils
import multiprocessing
import difflib
from unittest.mock import patch
import io
import sys

from contextlib import redirect_stdout

def run_student_code(student_code, return_dict):
    buffer = io.StringIO()

    class FakeRecognizer:
        def record(self, source):
            return "audio_data"
        def recognize_google(self, audio_data, language="yue"):
            return "孤掌難鳴"

    class FakeAudioFile:
        def __init__(self, file):
            self.file = file
        def __enter__(self):
            return "fake_source"
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    try:
        with patch("speech_recognition.AudioFile", FakeAudioFile), \
             patch("speech_recognition.Recognizer", return_value=FakeRecognizer()), \
             patch("builtins.input", return_value="test"), \
             redirect_stdout(buffer):
            exec(student_code, {})

        return_dict["output"] = buffer.getvalue()

    except Exception as e:
        return_dict["output"] = f"ERROR: {str(e)}"


def evaluate_task7(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            student_code = f.read()

        manager = multiprocessing.Manager()
        return_dict = manager.dict()

        p = multiprocessing.Process(target=run_student_code, args=(student_code, return_dict))
        p.start()
        p.join(timeout=3)  # 最多跑 3 秒

        if p.is_alive():
            p.terminate()
            p.join()
            return 2, "❌ 執行超時（可能無限迴圈）"

        output = return_dict.get("output", "").strip()

        # 分析 code 結構
        features = {
            "Recognizer": "Recognizer" in student_code,
            "record": "record(" in student_code,
            "recognize_google": "recognize_google" in student_code,
            "AudioFile": "AudioFile" in student_code,
            "while": "while" in student_code
        }

        if "孤掌難鳴" in output or "Correct" in output:
            if all(features.values()):
                return 10, "✅ 功能與結構完整"
            elif sum(features.values()) >= 4:
                return 8, "⚠️ 功能正確但語句略有缺"
            elif sum(features.values()) >= 3:
                return 6, "⚠️ 可執行但語音結構不足"
            else:
                return 4, "⚠️ 輸出正確但幾乎無結構"
        else:
            return 3, "⚠️ 執行成功但無正確輸出"

    except Exception:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                student_code = f.read()
        except:
            return 0, "❌ 無法讀取檔案"

        model_code = '''
import speech_recognition as sr
recognizer = sr.Recognizer()
print("一個巴掌拍不響，猜一成語：")
audio_file = "./audio.wav"
with sr.AudioFile(audio_file) as source:
    audio_data = recognizer.record(source)
while True:
    text = recognizer.recognize_google(audio_data, language="yue")
    print("Your answer:", text)
    if text == "孤掌難鳴":
        print("Correct!")
        break
    else:
        print("Incorrect...")
'''
        similarity = difflib.SequenceMatcher(None, student_code, model_code).ratio()
        if similarity > 0.9:
            return 3, "⚠️ 無法執行，但與標準答案非常相似"
        elif similarity > 0.6:
            return 2, "⚠️ 有部分結構但不能執行"
        else:
            return 1, "❌ 完全錯誤"


def test(submissions):
    for idx, row in submissions.iterrows():
        print("=========================================")
        print(submissions.loc[idx, "class"], submissions.loc[idx, "classnumber"])
        print("=========================================")
        submissions.loc[idx, "marks"] = 0
        submissions.loc[idx, "comments"] = ""

        # (2 marks) No marks if no file found
        if row["filepath"] is None:
            submissions.loc[idx, "marks"] = 0
            submissions.loc[idx, "comments"] = "No file found in the submission\n"
            continue

        # (1 mark) The python code is runnable
        section_description = "The python code is runnable"
        filepath = row["filepath"]
        section_mark, remarks = evaluate_task7(filepath)

        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark, 5)

        if (remarks != ""):
            submissions.loc[idx, "comments"] += "\n" + remarks

        print("=========================================")
        print("Marks:", submissions.loc[idx, "marks"])
        print(submissions.loc[idx, "comments"])
        print("=========================================")

    return submissions


if __name__ == "__main__":
    submissions = aia_utils.read_teams_aias()
    submissions = test(submissions)
    print(submissions)
    submissions.to_csv("marksheets.csv")
