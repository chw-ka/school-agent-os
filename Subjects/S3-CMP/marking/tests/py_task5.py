import aia_util as aia_utils
import multiprocessing
from unittest.mock import patch, MagicMock
from contextlib import redirect_stdout
import io
import difflib

def run_task8(student_code, return_dict):
    buffer = io.StringIO()

    # 模擬物件
    class FakeRecognizer:
        def adjust_for_ambient_noise(self, source):
            pass
        def listen(self, source):
            return "audio_data"
        def recognize_google(self, audio_data, language="en"):
            return "apple"

    class FakeMicrophone:
        def __enter__(self):
            return "fake_source"
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    class FakeClient:
        def translate(self, text, source_language, target_language):
            return {"translatedText": "蘋果"}

    with patch("speech_recognition.Recognizer", return_value=FakeRecognizer()), \
         patch("speech_recognition.Microphone", FakeMicrophone), \
         patch("google.cloud.translate_v2.Client", return_value=FakeClient()), \
         patch("gtts.gTTS", return_value=MagicMock(save=lambda filename: None)), \
         patch("playsound.playsound", return_value=None), \
         patch("builtins.input", side_effect=["add", "list", "speech", "exit"]), \
         redirect_stdout(buffer):
        try:
            exec(student_code, {})
            return_dict["runs"] = True
            return_dict["output"] = buffer.getvalue()
        except Exception as e:
            return_dict["runs"] = False
            return_dict["error"] = str(e)

def evaluate_task8(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            student_code = f.read()
    except:
        return 0, "❌ 無法讀取程式碼"

    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    p = multiprocessing.Process(target=run_task8, args=(student_code, return_dict))
    p.start()
    p.join(timeout=5)

    if p.is_alive():
        p.terminate()
        p.join()
        return 2, "⚠️ 程式執行超時（可能無限 loop）"

    score = 0
    explanation = []

    if return_dict.get("runs"):
        score += 2
        explanation.append("✅ 程式可成功執行 (+2)")
    else:
        explanation.append("❌ 程式執行錯誤 (0)")

    # 靜態分析
    if any(mod in student_code for mod in ["import speech_recognition", "from speech_recognition"]):
        score += 1
    if any(mod in student_code for mod in ["import gtts", "from gtts"]):
        score += 1
    if any(mod in student_code for mod in ["import os", "os.environ"]):
        score += 1
    if any(mod in student_code for mod in ["from google.cloud", "translate_v2"]):
        score += 1
    explanation.append("✅ 導入模組 (+2)" if score >= 4 else "⚠️ 部分模組導入不齊")

    if "Recognizer()" in student_code and "Microphone()" in student_code:
        score += 2
        explanation.append("✅ 使用 sr.Recognizer() + Microphone() (+2)")

    if "=[]" in student_code or "= []" in student_code:
        score += 1
        explanation.append("✅ 有建立空列表 (+1)")

    if "while True" in student_code:
        score += 1
        explanation.append("✅ 有使用 while True (+1)")

    if "listen(" in student_code and "recognize_google" in student_code:
        score += 2
        explanation.append("✅ 語音輸入處理 (+2)")

    if "vocab_list +" in student_code or ".append(" in student_code:
        score += 2
        explanation.append("✅ 加入單字到列表 (+2)")

    if "Client()" in student_code and "translate" in student_code:
        score += 2
        explanation.append("✅ 有處理翻譯 (+2)")

    if "for" in student_code and "range" in student_code and "len(vocab_list)" in student_code:
        score += 2
        explanation.append("✅ 有對 vocab_list 進行迭代 (+2)")

    if "gTTS" in student_code and ("audio.save" in student_code or ".save(" in student_code):
        score += 2
        explanation.append("✅ 有語音輸出 (gTTS) (+2)")

    if "break" in student_code and "exit" in student_code:
        score += 2
        explanation.append("✅ 有結束指令和結束迴圈 (+2)")

    return min(score, 20), " | ".join(explanation)


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
        section_mark, remarks = evaluate_task8(filepath)

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
