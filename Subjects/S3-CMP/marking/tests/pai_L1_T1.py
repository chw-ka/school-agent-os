import os
import re
import aia_util as aia_utils
from pai_util import read_student_code, finalize_ch1_4_mark


def evaluate(filepath):
    code = read_student_code(filepath)
    comments = ""
    total = 0

    has_gtts = bool(re.search(r"from\s+gtts\s+import\s+gTTS", code))
    has_playsound = bool(re.search(r"from\s+playsound\s+import\s+playsound", code))
    has_pyttsx3 = bool(re.search(r"import\s+pyttsx3", code))
    if has_gtts and has_playsound:
        comments += aia_utils.get_comments("匯入 gTTS 和 playsound", 2, 2)
        total += 2
    elif has_gtts or (has_pyttsx3 and has_playsound):
        comments += aia_utils.get_comments("匯入 gTTS 和 playsound", 1, 2)
        total += 1
    elif has_pyttsx3:
        comments += aia_utils.get_comments("匯入 gTTS 和 playsound (使用 pyttsx3 替代)", 1, 2)
        total += 1
    else:
        comments += aia_utils.get_comments("匯入 gTTS 和 playsound", 0, 2)

    has_while = bool(re.search(r"\bwhile\s+", code))
    has_q_exit = bool(re.search(r'["\']Q["\']', code, re.I)) and "break" in code
    if has_while and has_q_exit:
        comments += aia_utils.get_comments("循環結構 (while + break on Q)", 2, 2)
        total += 2
    elif has_while:
        comments += aia_utils.get_comments("循環結構 (while)", 1, 2)
        total += 1
    else:
        comments += aia_utils.get_comments("循環結構", 0, 2)

    has_input = bool(re.search(r"\binput\s*\(", code))
    if has_input:
        comments += aia_utils.get_comments("輸入提示", 2, 2)
        total += 2
    else:
        comments += aia_utils.get_comments("輸入提示", 0, 2)

    has_gtts_call = bool(re.search(r"gTTS\s*\(", code))
    has_chinese_lang = bool(re.search(r'lang\s*=\s*["\']zh', code))
    has_pyttsx_speak = bool(re.search(r"engine\.say\s*\(", code)) and bool(re.search(r"runAndWait\s*\(", code))
    if has_gtts_call and has_chinese_lang:
        comments += aia_utils.get_comments("gTTS 轉換 (中文語言)", 2, 2)
        total += 2
    elif has_gtts_call or has_pyttsx_speak:
        comments += aia_utils.get_comments("gTTS 轉換", 1, 2)
        total += 1
    else:
        comments += aia_utils.get_comments("gTTS 轉換", 0, 2)

    has_save = bool(re.search(r"\.save\s*\(", code))
    has_play = bool(re.search(r"playsound\s*\(", code))
    if has_save and has_play:
        comments += aia_utils.get_comments("儲存並播放音頻", 2, 2)
        total += 2
    elif has_play or has_pyttsx_speak:
        comments += aia_utils.get_comments("儲存或播放音頻", 1, 2)
        total += 1
    else:
        comments += aia_utils.get_comments("儲存並播放音頻", 0, 2)

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
        mark, comments = finalize_ch1_4_mark(mark, comments, str(filepath), chapter=1)
        submissions.loc[idx, "marks"] = mark
        submissions.loc[idx, "comments"] = comments
    return submissions
