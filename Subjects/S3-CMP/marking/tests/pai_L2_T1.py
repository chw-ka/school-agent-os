import os
import re
import aia_util as aia_utils
from pai_util import read_student_code, finalize_ch1_4_mark


def evaluate(filepath):
    code = read_student_code(filepath)
    comments = "[O]: Correct\n[-]: Minor error\n[X]: Major error\n\n"
    total = 0

    if re.search(r"import\s+speech_recognition\s+as\s+sr", code):
        comments += aia_utils.get_comments("匯入 speech_recognition 模組", 2, 2)
        total += 2
    elif re.search(r"import\s+speech_recognition", code):
        comments += aia_utils.get_comments("匯入 speech_recognition 模組（別名非 sr）", 1, 2)
        total += 1
    else:
        comments += aia_utils.get_comments("缺少 speech_recognition 匯入", 0, 2)

    if re.search(r"(recognizer|recongizer)\s*=\s*sr\.Recognizer\(\)", code):
        comments += aia_utils.get_comments("建立 Recognizer 物件", 1, 1)
        total += 1
    else:
        comments += aia_utils.get_comments("缺少 Recognizer 物件", 0, 1)

    if re.search(r"sr\.Microphone\(\)", code):
        comments += aia_utils.get_comments("使用麥克風", 1, 1)
        total += 1
    else:
        comments += aia_utils.get_comments("未使用麥克風", 0, 1)

    has_while = bool(re.search(r"\bwhile\s+", code))
    has_finish = bool(re.search(r"finish", code, re.I)) and "break" in code
    has_listen_loop = has_while and bool(re.search(r"\.listen\s*\(", code))
    if has_while and (has_finish or has_listen_loop):
        comments += aia_utils.get_comments("使用迴圈直至 finish", 3, 3)
        total += 3
    elif has_while:
        comments += aia_utils.get_comments("有迴圈但未正確處理 finish 跳出", 1, 3)
        total += 1
    else:
        comments += aia_utils.get_comments("缺少迴圈結構", 0, 3)

    if re.search(r'print\(["\']Please speak something', code):
        comments += aia_utils.get_comments("輸出提示語句", 1, 1)
        total += 1
    else:
        comments += aia_utils.get_comments("缺少提示語句", 0, 1)

    if re.search(r'print\(["\']You said:', code):
        comments += aia_utils.get_comments("輸出辨識結果", 1, 1)
        total += 1
    else:
        comments += aia_utils.get_comments("缺少辨識結果輸出", 0, 1)

    has_unknown = bool(re.search(r"except\s+sr\.UnknownValueError", code))
    has_request = bool(re.search(r"except\s+sr\.RequestError", code))
    if has_unknown and has_request:
        comments += aia_utils.get_comments("包含錯誤處理", 1, 1)
        total += 1
    elif has_unknown or has_request:
        comments += aia_utils.get_comments("錯誤處理不完整", 0, 1)
    else:
        comments += aia_utils.get_comments("缺少錯誤處理", 0, 1)

    return min(total, 10), comments


def test(submissions):
    for idx, row in submissions.iterrows():
        submissions.loc[idx, "marks"] = 0
        submissions.loc[idx, "comments"] = ""
        filepath = row.get("filepath")
        if not filepath or not os.path.exists(str(filepath)):
            submissions.loc[idx, "comments"] = "No file found in the submission\n"
            continue
        mark, comments = evaluate(str(filepath))
        mark, comments = finalize_ch1_4_mark(mark, comments, str(filepath), chapter=2)
        submissions.loc[idx, "marks"] = int(mark)
        submissions.loc[idx, "comments"] = comments
    return submissions
