import aia_util as aia_utils
import io
import sys
import difflib
from unittest.mock import patch
from contextlib import redirect_stdout

def evaluate_task6(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            student_code = f.read()

        buffer = io.StringIO()

        class FakeClient:
            def translate(self, text, source_language, target_language):
                return {"translatedText": "模擬翻譯"}

        # ✅ 同時 patch input() + translate.Client()
        with patch("builtins.input", return_value="Hello"), \
             patch("google.cloud.translate_v2.Client", return_value=FakeClient()), \
             redirect_stdout(buffer):
            exec(student_code, {})

        output = buffer.getvalue().strip()
        buffer.close()

        features = {
            "import": "google.cloud.translate_v2" in student_code,
            "Client": "translate.Client" in student_code,
            "input": "input" in student_code,
            "translatedText": '["translatedText"]' in student_code or "['translatedText']" in student_code,
            "os_env": "GOOGLE_APPLICATION_CREDENTIALS" in student_code
        }

        if "模擬翻譯" in output or "Translation" in output or "translation" in output.lower():
            if all(features.values()):
                return 10, "✅ 功能與結構完整"
            elif sum(features.values()) >= 4:
                return 9, "⚠️ 功能正確但語句略有缺失"
            elif sum(features.values()) >= 3:
                return 7, "⚠️ 輸出正確但結構不足"
            else:
                return 5, "⚠️ 結構少，僅部分語句存在"
        else:
            return 3, "⚠️ 執行成功但無翻譯輸出"

    except Exception:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                student_code = f.read()
        except:
            return 0, "❌ 無法讀取檔案"

        model_code = '''
import os
from google.cloud import translate_v2 as translate

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "password.json"
Client = translate.Client()

text = input("Enter English text:")
result = Client.translate(text,source_language="en",target_language="zh")

print("Translation:"+result["translatedText"])
'''
        similarity = difflib.SequenceMatcher(None, student_code, model_code).ratio()
        if similarity > 0.9:
            return 3, "⚠️ 無法執行但與標準答案非常相似"
        elif similarity > 0.6:
            return 2, "⚠️ 有部分結構但不能執行"
        else:
            return 1, "❌ 完全錯誤"

def indent_code(code, indent="    "):
    return "\n".join(indent + line if line.strip() else line for line in code.splitlines())


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
        section_mark, remarks = evaluate_task6(filepath)

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
