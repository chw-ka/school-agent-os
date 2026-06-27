import os
import re
import aia_util as aia_utils
from pai_util import read_student_code, finalize_ch1_4_mark


def evaluate(filepath):
    code = read_student_code(filepath)
    comments = "[O]: Correct\n[-]: Minor error\n[X]: Major error\n\n"
    total = 0

    if re.search(r"import\s+speech_recognition", code) or re.search(r"from\s+speech_recognition\s+import", code):
        comments += aia_utils.get_comments("Import speech_recognition library", 2, 2)
        total += 2
    elif re.search(r"import\s+pyttsx3|from\s+gtts|import\s+googletrans|from\s+googletrans", code):
        comments += aia_utils.get_comments("Import speech_recognition library (alternative approach)", 1, 2)
        total += 1
    else:
        comments += aia_utils.get_comments("Import speech_recognition library", 0, 2)

    has_recognizer = bool(re.search(r"[Rr]ecognizer\s*\(", code))
    has_mic = bool(re.search(r"[Mm]icrophone\s*\(", code))
    has_listen = bool(re.search(r"\.listen\s*\(", code))
    if has_recognizer and has_mic and has_listen:
        comments += aia_utils.get_comments("Use Recognizer, Microphone, and listen()", 2, 2)
        total += 2
    elif has_recognizer and has_listen:
        comments += aia_utils.get_comments("Use Recognizer, Microphone, and listen()", 1, 2)
        total += 1
    else:
        comments += aia_utils.get_comments("Use Recognizer, Microphone, and listen()", 0, 2)

    if re.search(r"recognize_google\s*\(", code):
        if re.search(r'language\s*=\s*["\']yue["\']', code):
            comments += aia_utils.get_comments("Use recognize_google with language='yue'", 2, 2)
            total += 2
        else:
            comments += aia_utils.get_comments("Use recognize_google with language='yue'", 1, 2)
            total += 1
    else:
        comments += aia_utils.get_comments("Use recognize_google with language='yue'", 0, 2)

    has_gtts = bool(re.search(r"from\s+gtts\s+import\s+gTTS", code) or re.search(r"import\s+gtts", code))
    has_playsound = bool(re.search(r"from\s+playsound\s+import\s+playsound", code) or re.search(r"import\s+playsound", code))
    if has_gtts and has_playsound:
        comments += aia_utils.get_comments("Import gTTS and playsound", 1, 1)
        total += 1
    else:
        comments += aia_utils.get_comments("Import gTTS and playsound", 0, 1)

    if re.search(r"gTTS\s*\(", code) and re.search(r"\.save\s*\(", code) and re.search(r"playsound\s*\(", code):
        comments += aia_utils.get_comments("Use gTTS to convert text to speech and play", 1, 1)
        total += 1
    else:
        comments += aia_utils.get_comments("Use gTTS to convert text to speech and play", 0, 1)

    translate_libs = [
        r"from\s+google\.cloud\s+import\s+translate",
        r"from\s+translate\s+import\s+Translator",
        r"import\s+googletrans",
        r"from\s+deep_translator\s+import",
    ]
    if any(re.search(p, code, re.I) for p in translate_libs):
        comments += aia_utils.get_comments("Import translation library", 1, 1)
        total += 1
    else:
        comments += aia_utils.get_comments("Import translation library", 0, 1)

    if re.search(r"\.translate\s*\(", code):
        lang_ok = bool(re.search(r'source_language\s*=\s*["\'](yue|zh)["\']', code)) or \
                  bool(re.search(r'target_language\s*=\s*["\']en["\']', code)) or \
                  bool(re.search(r'from_lang\s*=\s*["\'](yue|zh)', code, re.I))
        if lang_ok:
            comments += aia_utils.get_comments("Use translate function with appropriate language settings", 1, 1)
            total += 1
        else:
            comments += aia_utils.get_comments("Use translate function", 0, 1)
    else:
        comments += aia_utils.get_comments("Use translate function with appropriate language settings", 0, 1)

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
        submissions.loc[idx, "marks"] = mark
        submissions.loc[idx, "comments"] = comments
    return submissions
