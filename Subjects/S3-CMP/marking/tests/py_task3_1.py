import aia_util as aia_utils
import subprocess
import difflib
import re
import tempfile

import subprocess
import difflib
import tempfile
import re

def evaluate_task5(filepath):
    try:
        # 原始學生 code
        with open(filepath, "r", encoding="utf-8") as f:
            student_code = f.read()

        # mock gTTS & playsound
        wrapper_code = f'''
from unittest.mock import patch, MagicMock

with patch("gtts.gTTS", return_value=MagicMock(save=lambda filename: None)), \\
     patch("playsound.playsound", return_value=None):
{indent_code(student_code)}
'''

        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py") as temp_file:
            temp_file.write(wrapper_code)
            temp_path = temp_file.name

        result = subprocess.run(
            ["python", temp_path],
            input="Hello world\n",
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            raise RuntimeError("Execution error")

        # 檢查用詞結構
        features = {
            "input": "input" in student_code,
            "gTTS": "gTTS" in student_code,
            "save": ".save" in student_code,
            "playsound": "playsound" in student_code
        }

        if all(features.values()):
            return 10, "✅ 成功 mock 並驗證語法完整"
        elif sum(features.values()) >= 3:
            return 8, f"⚠️ 可執行但缺少某些語句：缺少 {', '.join([k for k, v in features.items() if not v])}"
        elif sum(features.values()) >= 2:
            return 6, f"⚠️ 結構部分正確，缺少多項功能"
        else:
            return 4, f"⚠️ 結構過少，只用到 {', '.join([k for k, v in features.items() if v])}"

    except Exception as e:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                student_code = f.read()
        except:
            return 0, "❌ 無法讀取檔案"

        model_code = '''
from gtts import gTTS
from playsound import playsound
your_input = input("Enter the text you want to convert to speech.")
audio = gTTS(text = your_input,lang="en")
audio.save("audio.mp3")
playsound("./audio.mp3")
'''
        similarity = difflib.SequenceMatcher(None, student_code, model_code).ratio()

        if similarity > 0.9:
            return 3, "⚠️ 無法執行，但與標準答案非常相似"
        elif similarity > 0.6:
            return 2, "⚠️ 無法執行，但有部分結構"
        else:
            return 1, "❌ 完全錯誤，且不能執行"

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
        section_mark, remarks = evaluate_task5(filepath)

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
