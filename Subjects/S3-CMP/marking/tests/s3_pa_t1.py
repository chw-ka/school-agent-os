"""
S3 下學期實習試：任務一 — 智能播音員 (15 marks)
Students complete fill-in-the-blank blanks (a)-(d) in task1_2526.py using gTTS.
"""

RUBRIC = [
    {"key": "mark1", "name": "Imports (gtts, playsound, os)", "max_marks": 5},
    {"key": "mark2", "name": "TTS, save & cleanup", "max_marks": 10},
]

import os
import re
import aia_util as aia_utils


def test(submissions):
    for idx, row in submissions.iterrows():
        submissions.loc[idx, "marks"] = 0
        submissions.loc[idx, "comments"] = ""

        # filepath IS the student's submitted .py file (renamed with student/submission IDs)
        task1_file = str(row.get("filepath", "") or "")
        if not task1_file or not os.path.exists(task1_file):
            submissions.loc[idx, "comments"] = (
                "[O]: Correct\n[-]: Minor error\n[X]: Major error\n\n"
                "[X]: task1_2526.py not submitted\n"
            )
            continue

        try:
            with open(task1_file, encoding="utf-8") as f:
                code = f.read()
        except Exception:
            with open(task1_file, encoding="latin-1") as f:
                code = f.read()

        comments = "[O]: Correct\n[-]: Minor error\n[X]: Major error\n\n"
        mark1 = mark2 = 0

        # ==================== SECTION 1: Imports (5 marks) ====================
        # from gtts import gTTS
        if re.search(r"from\s+gtts\s+import\s+gTTS", code):
            mark1 += 2
            comments += "[O]: (a) from gtts import gTTS\n"
        else:
            comments += "[X]: (a) Missing: from gtts import gTTS\n"

        # from playsound import playsound (accept pygame or similar alternatives)
        if re.search(r"from\s+playsound\s+import\s+playsound", code):
            mark1 += 2
            comments += "[O]: (a) from playsound import playsound\n"
        elif re.search(r"import\s+playsound|pygame|pydub|simpleaudio|sounddevice", code):
            mark1 += 1
            comments += "[-]: (a) Alternative audio library used instead of playsound\n"
        else:
            comments += "[X]: (a) Missing: from playsound import playsound\n"

        # import os
        if re.search(r"import\s+os", code):
            mark1 += 1
            comments += "[O]: (a) import os\n"
        else:
            comments += "[X]: (a) Missing: import os\n"

        submissions.loc[idx, "mark1"] = mark1
        submissions.loc[idx, "marks"] += mark1
        comments += aia_utils.get_comments("Imports (gtts, playsound, os)", mark1, 5)

        # ==================== SECTION 2: TTS, Save & Cleanup (10 marks) ====================
        # gTTS(...) with text and lang arguments
        gtts_match = re.search(r"gTTS\s*\(", code)
        if gtts_match:
            # Extract the full gTTS() call
            call_start = gtts_match.start()
            paren_depth = 0
            end = call_start
            for i, ch in enumerate(code[call_start:]):
                if ch == "(":
                    paren_depth += 1
                elif ch == ")":
                    paren_depth -= 1
                    if paren_depth == 0:
                        end = call_start + i + 1
                        break
            gtts_call = code[call_start:end]

            has_text = re.search(r"text\s*=", gtts_call) or re.search(r"msg", gtts_call)
            has_lang = re.search(r"lang\s*=", gtts_call)

            if has_text and has_lang:
                mark2 += 4
                comments += "[O]: (d) gTTS(text=msg, lang=lang)\n"
            elif has_text or has_lang:
                mark2 += 2
                comments += "[-]: (d) gTTS called but missing text or lang argument\n"
            else:
                mark2 += 1
                comments += "[-]: (d) gTTS() called but arguments incorrect\n"
        else:
            comments += "[X]: (d) Missing gTTS(...) call\n"

        # audio.save("*.mp3") — question only requires saving an mp3, not a fixed filename
        if re.search(r'\.\s*save\s*\(\s*["\'][^"\']+\.mp3["\']\s*\)', code):
            mark2 += 3
            comments += "[O]: (d) audio.save(...mp3)\n"
        elif re.search(r"\.\s*save\s*\(", code):
            mark2 += 1
            comments += "[-]: (d) .save() called but target may not be an mp3 file\n"
        else:
            comments += "[X]: (d) Missing audio.save(...)\n"

        # os.remove("*.mp3")
        if re.search(r'os\s*\.\s*remove\s*\(\s*["\'][^"\']+\.mp3["\']\s*\)', code):
            mark2 += 3
            comments += "[O]: (d) os.remove(...mp3)\n"
        elif re.search(r"os\s*\.\s*remove\s*\(", code):
            mark2 += 1
            comments += "[-]: (d) os.remove() called but target may not be an mp3 file\n"
        else:
            comments += "[X]: (d) Missing os.remove(...)\n"

        submissions.loc[idx, "mark2"] = mark2
        submissions.loc[idx, "marks"] += mark2
        comments += aia_utils.get_comments("TTS, save & cleanup", mark2, 10)

        submissions.loc[idx, "comments"] = comments

    return submissions
