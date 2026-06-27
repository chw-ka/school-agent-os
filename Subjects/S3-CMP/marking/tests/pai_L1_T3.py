import os
import re
import aia_util as aia_utils
from pai_util import finalize_ch1_4_mark

def read_code(filepath):
    try:
        with open(filepath, encoding="utf-8") as f:
            return f.read()
    except Exception:
        with open(filepath, encoding="latin-1") as f:
            return f.read()

def evaluate(filepath):
    code = read_code(filepath)
    comments = "[O]: Correct\n[-]: Minor error\n[X]: Major error\n\n"
    total = 0
    max_total = 10

    # 1. Check for googletrans or translate import (or equivalent)
    has_translate_lib = bool(re.search(r'(from\s+googletrans\s+import|import\s+googletrans|from\s+translate\s+import|import\s+translate)', code, re.IGNORECASE))
    if has_translate_lib:
        total += 2
        comments += aia_utils.get_comments("Import translation library (googletrans/translate)", 2, 2)
    else:
        comments += aia_utils.get_comments("Import translation library (googletrans/translate)", 0, 2)

    # 2. Check for gTTS import (for text-to-speech)
    has_tts = bool(re.search(r'(from\s+gtts\s+import|import\s+gtts|gTTS)', code, re.IGNORECASE))
    if has_tts:
        total += 2
        comments += aia_utils.get_comments("Import gTTS for text-to-speech", 2, 2)
    else:
        comments += aia_utils.get_comments("Import gTTS for text-to-speech", 0, 2)

    # 3. Check for loop structure (while True or while with break on 'Q')
    has_loop = bool(re.search(r'while\s+(True|1|not\s+done|user_input\s*!=\s*["\']Q["\'])', code, re.IGNORECASE))
    has_break_q = bool(re.search(r'if\s+.*["\']Q["\'].*:\s*\n\s*break', code, re.IGNORECASE))
    if has_loop and has_break_q:
        total += 3
        comments += aia_utils.get_comments("Loop structure with break on 'Q'", 3, 3)
    elif has_loop:
        total += 1
        comments += aia_utils.get_comments("Loop structure present but break on 'Q' not clear", 1, 3)
    else:
        comments += aia_utils.get_comments("Loop structure with break on 'Q'", 0, 3)

    # 4. Check for translation call (translate.text or similar)
    has_translate_call = bool(re.search(r'\.translate\s*\(', code, re.IGNORECASE))
    if has_translate_call:
        total += 2
        comments += aia_utils.get_comments("Translation function called", 2, 2)
    else:
        comments += aia_utils.get_comments("Translation function called", 0, 2)

    # 5. Check for text-to-speech playback (gTTS save + playsound or os.system)
    has_tts_play = bool(re.search(r'(\.save\s*\(|playsound|os\.system.*mp3|os\.system.*wav)', code, re.IGNORECASE))
    if has_tts_play:
        total += 1
        comments += aia_utils.get_comments("Text-to-speech playback implemented", 1, 1)
    else:
        comments += aia_utils.get_comments("Text-to-speech playback implemented", 0, 1)

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