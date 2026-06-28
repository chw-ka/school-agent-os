import aia_util as aia_utils
import subprocess
import difflib
import re
import tempfile

def evaluate_task4(filepath):
    try:
        # 包裹學生程式碼，用 unittest.mock.patch 將 random.randint() 固定回傳 42
        with open(filepath, "r", encoding="utf-8") as f:
            student_code = f.read()

        wrapper_code = f'''
from unittest.mock import patch

with patch("random.randint", return_value=42):
{indent_code(student_code)}
'''

        # 儲存到臨時檔案中執行
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py") as temp_file:
            temp_file.write(wrapper_code)
            temp_path = temp_file.name

        inputs = ["30\n", "50\n", "42\n"]
        expected_responses = ["Too low", "Too high", "Bingo"]

        result = subprocess.run(
            ["python", temp_path],
            input="".join(inputs),
            capture_output=True,
            text=True,
            timeout=5
        )

        output = result.stdout.strip()
        passed = sum(msg in output for msg in expected_responses)

        if passed == 3:
            return 10, "✅ 完全正確，並正確使用 random.randint()"
        elif passed == 2:
            return 9, "⚠️ 大致正確，略有遺漏"
        elif passed == 1:
            return 7, "⚠️ 僅部分正確"
        else:
            # 程式可執行但無正確行為，進行結構分析
            structure_score = sum(kw in student_code for kw in ["input", "while", "print", "random.randint"])
            if structure_score >= 3:
                return 5, "⚠️ 結構合理但行為錯誤"
            elif structure_score >= 2:
                return 4, "⚠️ 結構部分正確"
            else:
                return 3, "⚠️ 結構不完整"

    except Exception:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                student_code = f.read()
        except:
            return 0, "❌ 無法讀取檔案"

        model_code = '''
import random
guess = int(random.randint(1,100))
while True:
    num = int(input("Enter a number: "))
    if num == guess:
        print("Bingo!")
        break
    elif num < guess:
        print("Too low")
    elif num > guess:
        print("Too high")
'''
        similarity = difflib.SequenceMatcher(None, student_code, model_code).ratio()
        if similarity > 0.9:
            return 3, "⚠️ 無法執行，但與標準答案非常相似"
        elif similarity > 0.6:
            return 2, "⚠️ 無法執行，但部分正確"
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
        section_mark, remarks = evaluate_task4(filepath)

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
