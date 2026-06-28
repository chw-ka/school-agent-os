import aia_util as aia_utils
import difflib
from contextlib import redirect_stdout
from unittest.mock import patch, MagicMock
import multiprocessing
import io

def run_task9(student_code, return_dict):
    buffer = io.StringIO()

    with patch("cv2.VideoCapture") as mock_capture, \
         patch("cv2.CascadeClassifier") as mock_cascade, \
         patch("cv2.imshow"), patch("cv2.waitKey", return_value=1), \
         patch("cv2.cvtColor", return_value="gray_frame"), \
         patch("cv2.rectangle"):
        
        mock_capture.return_value.read.side_effect = [(True, "frame")] * 3 + [(False, None)]
        mock_cascade.return_value.detectMultiScale.return_value = [(10,10,50,50)]
        
        try:
            with redirect_stdout(buffer):
                exec(student_code, {})
            return_dict["runs"] = True
        except Exception as e:
            return_dict["runs"] = False
            return_dict["error"] = str(e)

def evaluate_task9(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            student_code = f.read()
    except:
        return 0, "❌ 無法讀取程式碼"

    # Mock 執行
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    p = multiprocessing.Process(target=run_task9, args=(student_code, return_dict))
    p.start()
    p.join(timeout=3)

    if p.is_alive():
        p.terminate()
        p.join()
        return 2, "⚠️ 執行超時（可能無限 loop）"

    score = 0
    explanation = []

    if return_dict.get("runs"):
        score += 2
        explanation.append("✅ 程式可成功執行 (+2)")
    else:
        explanation.append("❌ 程式執行失敗")

    # 靜態分析
    code = student_code
    if "VideoCapture" in code:
        score += 1
        explanation.append("✅ 使用 VideoCapture (+1)")
    if "CascadeClassifier" in code:
        score += 1
        explanation.append("✅ 使用 Haar Cascade (+1)")
    if "while True" in code:
        score += 1
        explanation.append("✅ 使用 while loop (+1)")
    if "cvtColor" in code and "COLOR_BGR2GRAY" in code:
        score += 1
        explanation.append("✅ 灰階轉換 (+1)")
    if "detectMultiScale" in code:
        score += 1
        explanation.append("✅ 使用 detectMultiScale (+1)")
    if "rectangle" in code:
        score += 1
        explanation.append("✅ 使用 rectangle (+1)")
    if "imshow" in code and "waitKey" in code:
        score += 2
        explanation.append("✅ 顯示畫面 (+2)")

    return min(score, 10), " | ".join(explanation)


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
        section_mark, remarks = evaluate_task9(filepath)

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