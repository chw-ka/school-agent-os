import os
import re
import aia_util as aia_utils
from pai_util import read_student_code, finalize_ch1_4_mark


def evaluate(filepath):
    code = read_student_code(filepath)
    comments = ""
    total = 0

    lib_patterns = [
        r"from\s+google\.cloud\s+import\s+translate",
        r"from\s+translate\s+import\s+Translator",
        r"import\s+googletrans",
        r"from\s+googletrans\s+import",
        r"from\s+deep_translator\s+import",
    ]
    has_lib = any(re.search(p, code, re.I) for p in lib_patterns)
    if has_lib:
        comments += aia_utils.get_comments("Translation library imported", 2, 2)
        total += 2
    else:
        comments += aia_utils.get_comments("Translation library imported", 0, 2)

    client_patterns = [
        r"translate\.Client\s*\(",
        r"Translator\s*\(",
        r"GoogleTranslator\s*\(",
        r"googletrans\.Translator\s*\(",
    ]
    has_client = any(re.search(p, code) for p in client_patterns)
    if has_client:
        comments += aia_utils.get_comments("Translation client initialized", 2, 2)
        total += 2
    else:
        comments += aia_utils.get_comments("Translation client initialized", 0, 2)

    input_patterns = [
        r'input\s*\(\s*["\']Enter\s+Chinese\s+text',
        r'input\s*\(\s*["\'].*Chinese',
        r'input\s*\(\s*["\'].*中文',
    ]
    has_input = any(re.search(p, code, re.I) for p in input_patterns)
    if has_input:
        comments += aia_utils.get_comments("Input prompt for Chinese text", 2, 2)
        total += 2
    else:
        comments += aia_utils.get_comments("Input prompt for Chinese text", 0, 2)

    translate_patterns = [
        r"client\.translate\s*\(",
        r"translator\.translate\s*\(",
        r"\.translate\s*\(",
    ]
    lang_patterns = [
        r'source_language\s*=\s*["\']zh',
        r'target_language\s*=\s*["\']en',
        r'from_lang\s*=\s*["\']zh',
        r'to_lang\s*=\s*["\']en',
    ]
    has_translate = any(re.search(p, code) for p in translate_patterns)
    has_lang = any(re.search(p, code, re.I) for p in lang_patterns)
    if has_translate and has_lang:
        comments += aia_utils.get_comments("Translation call with correct language direction", 2, 2)
        total += 2
    elif has_translate:
        comments += aia_utils.get_comments("Translation call", 1, 2)
        total += 1
    else:
        comments += aia_utils.get_comments("Translation call with correct language direction", 0, 2)

    has_loop = bool(re.search(r"\bwhile\s+", code))
    has_q = bool(re.search(r'["\']Q["\']', code, re.I)) and "break" in code
    if has_loop and has_q:
        comments += aia_utils.get_comments("Loop until Q is entered", 2, 2)
        total += 2
    elif has_loop:
        comments += aia_utils.get_comments("Loop until Q is entered", 1, 2)
        total += 1
    else:
        comments += aia_utils.get_comments("Loop until Q is entered", 0, 2)

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
