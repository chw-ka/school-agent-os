import aia_util as aia_utils
import multiprocessing
import io
from contextlib import redirect_stdout

def run_task13(code, return_dict):
    buffer = io.StringIO()
    try:
        with redirect_stdout(buffer):
            exec(code, {})
        return_dict["runs"] = True
        return_dict["output"] = buffer.getvalue()
    except Exception as e:
        return_dict["runs"] = False
        return_dict["error"] = str(e)

def evaluate_task13(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()
    except:
        return 0, "❌ 無法讀取檔案"

    structure_score = 0
    explanation = []

    if "import cv2" in code:
        structure_score += 1
        explanation.append("✅ 有 import cv2 (+1)")

    if "cv2.VideoCapture" in code:
        structure_score += 1
        explanation.append("✅ 有開啟影片 (+1)")

    if "while True" in code and ".read()" in code:
        structure_score += 2
        explanation.append("✅ 有使用 while loop 讀取影片 (+2)")

    if "cv2.cvtColor" in code and "COLOR_BGR2GRAY" in code:
        structure_score += 1
        explanation.append("✅ 有轉灰階 (+1)")

    if "detectMultiScale" in code:
        structure_score += 2
        explanation.append("✅ 有使用 detectMultiScale (+2)")

    if "cv2.rectangle" in code:
        structure_score += 2
        explanation.append("✅ 有畫框框 (+2)")

    if "cv2.imshow" in code:
        structure_score += 1
        explanation.append("✅ 有顯示畫面 (+1)")

    # 執行測試
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    p = multiprocessing.Process(target=run_task13, args=(code, return_dict))
    p.start()
    p.join(timeout=4)

    logic_score = 0
    if p.is_alive():
        p.terminate()
        p.join()
        return min(structure_score, 10), "⚠️ 執行超時，只評語法結構 | " + " | ".join(explanation)

    if return_dict.get("runs"):
        logic_score += 3
        explanation.append("✅ 程式成功執行 (+3)")
        if "rectangle" in code:
            logic_score += 2
            explanation.append("✅ 有畫框邏輯 (+2)")
    else:
        explanation.append(f"❌ 執行錯誤：{return_dict.get('error')}")

    return min(15, structure_score + logic_score), " | ".join(explanation)


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
        section_mark, remarks = evaluate_task13(filepath)

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