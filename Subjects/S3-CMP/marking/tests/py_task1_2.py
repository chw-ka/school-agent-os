import aia_util as aia_utils
from py_util import test_student_code
import subprocess
import difflib

def evaluate_task2(filepath):
    model_outputs = {
        ("5", "3"): "Enter the width: Enter the height: The area is 15",
        ("10", "2"): "Enter the width: Enter the height: The area is 20",
        ("7", "7"): "Enter the width: Enter the height: The area is 49",
    }

    try:
        outputs = []
        for width_input, height_input in model_outputs:
            full_input = f"{width_input}\n{height_input}\n"
            result = subprocess.run(
                ["python", filepath],
                input=full_input,
                capture_output=True,
                text=True,
                timeout=3
            )

            output_lines = result.stdout.strip().splitlines()
            full_output = " ".join(line.strip() for line in output_lines)
            outputs.append(full_output)

        expected_outputs = list(model_outputs.values())

        score = 1  # 程式可執行的基本分

        # 判斷是否完全正確
        if outputs == expected_outputs:
            return 10, "✅ 完全正確（可執行 + 所有輸出正確）"

        # 判斷是否極為相近
        similarities = [
            difflib.SequenceMatcher(None, o, e).ratio()
            for o, e in zip(outputs, expected_outputs)
        ]
        if all(score >= 0.95 for score in similarities):
            return 9, "⚠️ 非常接近（小錯如空格／標點）"

        # 執行成功但輸出錯誤 → 檢查語法特徵
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()
            used_input = "input" in code
            used_print = "print" in code
            used_int = "int" in code

        score += used_input + used_print + used_int  # 每個元素加 1 分，總共最多 4
        reason = f"⚠️ 執行成功但輸出錯誤；使用 input: {used_input}, print: {used_print}, int: {used_int}"
        return score, reason

    except Exception:
        # 無法執行：根據 source 相似度給分
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                student_code = f.read()
        except:
            return 0, "❌ 無法讀取程式碼"

        model_code = 'width = int(input("Enter the width: "))\nheight = int(input("Enter the height: "))\nprint("The area is " + str(width*height))'
        similarity = difflib.SequenceMatcher(None, student_code, model_code).ratio()

        if similarity > 0.9:
            return 4, "⚠️ 無法執行；與標準答案非常相似"
        elif similarity > 0.6:
            return 3, "⚠️ 無法執行；部分類似"
        elif similarity > 0.3:
            return 2, "⚠️ 無法執行；略有概念"
        else:
            return 1, "❌ 完全錯誤，且不能執行"
        
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
        section_mark, remarks = evaluate_task2(filepath)

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
