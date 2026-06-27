import aia_util as aia_utils
import multiprocessing
from unittest.mock import patch
from contextlib import redirect_stdout
import io

def run_task10(code, return_dict):
    buffer = io.StringIO()
    inputs = ["70", "1.75"]

    with patch("builtins.input", side_effect=inputs), redirect_stdout(buffer):
        try:
            exec(code, {})
            return_dict["runs"] = True
            return_dict["output"] = buffer.getvalue().strip()
        except Exception as e:
            return_dict["runs"] = False
            return_dict["error"] = str(e)

def evaluate_task10(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()
    except:
        return 0, "❌ 無法讀取檔案"

    # 結構評分
    structure_score = 0
    if code.count("input") == 2:
        structure_score += 2
    elif code.count("input") == 1:
        structure_score += 1

    if "int(" in code:
        structure_score += 0.5
    if "float(" in code:
        structure_score += 0.5

    if "**2" in code or "pow(" in code:
        structure_score += 2

    if "print(" in code:
        structure_score += 1

    logic_score = 0
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    p = multiprocessing.Process(target=run_task10, args=(code, return_dict))
    p.start()
    p.join(timeout=3)

    if p.is_alive():
        p.terminate()
        p.join()
        return min(structure_score, 6) + 0, "⚠️ 程式超時，只評結構 | 結構分：" + str(structure_score)

    if return_dict.get("runs"):
        logic_score += 2
        output = return_dict.get("output", "")
        if "BMI" in output:
            logic_score += 2
            reason = "✅ 程式成功執行並輸出 BMI (+4)"
        else:
            reason = "✅ 程式成功執行 (+2)，但輸出不含 BMI (+0)"
    else:
        reason = f"❌ 執行失敗 ({return_dict.get('error')}) | 結構分：" + str(structure_score)

    total = min(10, structure_score + logic_score)
    return total, reason

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
        section_mark, remarks = evaluate_task10(filepath)

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