import os
import re
import aia_util as aia_utils
from pai_util import read_student_code, finalize_ch1_4_mark


def evaluate(filepath):
    code = read_student_code(filepath)
    comments = ""
    total = 0

    has_import = bool(re.search(r"import\s+speech_recognition\s+as\s+sr", code))
    if has_import:
        comments += aia_utils.get_comments("匯入 speech_recognition 模組", 2, 2)
        total += 2
    else:
        comments += aia_utils.get_comments("匯入 speech_recognition 模組", 0, 2)

    has_recognizer = bool(re.search(r"\.Recognizer\s*\(", code))
    has_mic = bool(re.search(r"\.Microphone\s*\(", code))
    if has_recognizer and has_mic:
        comments += aia_utils.get_comments("使用 Recognizer 和 Microphone", 2, 2)
        total += 2
    else:
        comments += aia_utils.get_comments("使用 Recognizer 和 Microphone", 0, 2)

    has_answer = bool(re.search(r"answer\s*=|ans\s*=|孤掌|拍不響|成語", code, re.I))
    has_loop = bool(re.search(r"\bwhile\s+", code))
    has_break = "break" in code
    has_correct_exit = bool(re.search(r"if\s+.*text.*==|if\s+.*==.*孤掌", code, re.I))
    if has_loop and has_break and (has_answer or has_correct_exit):
        comments += aia_utils.get_comments("設定答案並循環直到正確", 3, 3)
        total += 3
    elif has_loop and has_break:
        comments += aia_utils.get_comments("設定答案並循環直到正確", 2, 3)
        total += 2
    elif has_loop:
        comments += aia_utils.get_comments("設定答案並循環直到正確", 1, 3)
        total += 1
    else:
        comments += aia_utils.get_comments("設定答案並循環直到正確", 0, 3)

    has_question = bool(re.search(r"print\s*\(.*猜|print\s*\(.*成語|print\s*\(.*一個巴掌", code))
    has_output = bool(re.search(r"print\s*\(.*text|print\s*\(.*You said|print\s*\(.*answer", code, re.I))
    if has_question and has_output:
        comments += aia_utils.get_comments("輸出問題和辨識結果", 2, 2)
        total += 2
    elif has_question or has_output:
        comments += aia_utils.get_comments("輸出問題和辨識結果", 1, 2)
        total += 1
    else:
        comments += aia_utils.get_comments("輸出問題和辨識結果", 0, 2)

    has_check = bool(re.search(r"if\s+.*text.*==|if\s+.*==.*孤掌|if\s+.*answer", code, re.I))
    has_wrong = bool(re.search(r"Wrong|錯誤|try again|再試|correct", code, re.I))
    if has_check and has_wrong:
        comments += aia_utils.get_comments("判斷正確/錯誤並重複", 1, 1)
        total += 1
    else:
        comments += aia_utils.get_comments("判斷正確/錯誤並重複", 0, 1)

    total = min(total, 10)
    comments = "[O]: Correct\n[-]: Minor error\n[X]: Major error\n\n" + comments
    return total, comments


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
        submissions.loc[idx, "marks"] = mark
        submissions.loc[idx, "comments"] = comments
    return submissions
