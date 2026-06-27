import aia_util as aia_utils
import difflib
import multiprocessing
from unittest.mock import patch
from contextlib import redirect_stdout
import io

def run_task11(student_code, return_dict):
    buffer = io.StringIO()
    test_inputs = ["30", "50", "45", "-10", "-1"]

    with patch("builtins.input", side_effect=test_inputs), redirect_stdout(buffer):
        try:
            exec(student_code, {})
            return_dict["runs"] = True
            return_dict["output"] = buffer.getvalue().strip()
        except Exception as e:
            return_dict["runs"] = False
            return_dict["error"] = str(e)

def evaluate_task11(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            student_code = f.read()
    except:
        return 0, "❌ 無法讀取檔案"

    code = student_code
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    p = multiprocessing.Process(target=run_task11, args=(student_code, return_dict))
    p.start()
    p.join(timeout=4)

    if p.is_alive():
        p.terminate()
        p.join()
        return 4, "⚠️ 程式執行超時（但給結構分）"

    structure_score = 0
    explanation = []

    # 即使無法執行也給這些語法結構分
    if "while True" in code:
        structure_score += 1
        explanation.append("✅ 有 while True (+1)")
    if "break" in code:
        structure_score += 1
        explanation.append("✅ 有 break (+1)")
    if "scores" in code and "append" in code:
        structure_score += 1
        explanation.append("✅ 有 list 與 append (+1)")
    if "lower than 0" in code or ("print" in code and "<0" in code.replace(" ", "")):
        structure_score += 1
        explanation.append("✅ 處理負數 (+1)")
    if "max(" in code and "min(" in code and "sum(" in code:
        structure_score += 1
        explanation.append("✅ 使用 max/min/sum (+1)")
    if code.count("print") >= 3:
        structure_score += 1
        explanation.append("✅ 有三行 print 輸出結果 (+1)")

    logic_score = 0
    if return_dict.get("runs"):
        logic_score += 2
        explanation.append("✅ 程式成功執行 (+2)")
        output = return_dict.get("output", "")
        if "maximum" in output and "minimum" in output and "average" in output:
            logic_score += 2
            explanation.append("✅ 有正確 max/min/avg 輸出 (+2)")
        else:
            explanation.append("⚠️ 程式執行但輸出不完整")

    return min(structure_score + logic_score, 10), " | ".join(explanation)


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
        section_mark, remarks = evaluate_task11(filepath)

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