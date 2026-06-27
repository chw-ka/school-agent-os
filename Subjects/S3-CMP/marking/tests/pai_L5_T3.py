import os
import re
import aia_util as aia_utils

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

    # 1. Basic structure and runnability (2 marks)
    has_main = bool(re.search(r'if\s+__name__\s*==\s*["\']__main__["\']', code))
    has_def = bool(re.search(r'def\s+\w+\s*\(', code))
    has_loop = bool(re.search(r'while\s+|for\s+\w+\s+in\s+', code))
    structure_score = 0
    if has_main and has_def and has_loop:
        structure_score = 2
    elif has_main and (has_def or has_loop):
        structure_score = 1
    else:
        structure_score = 0
    total += structure_score
    comments += aia_utils.get_comments("程式基本結構 (主程式、函數、迴圈)", structure_score, 2)

    # 2. Game interactivity (3 marks)
    # Check for input handling (user interaction)
    has_input = bool(re.search(r'input\s*\(', code))
    has_print = bool(re.search(r'print\s*\(', code))
    # Check for some kind of game loop with break condition
    has_break = bool(re.search(r'\bbreak\b', code))
    # Check for conditional logic
    has_if = bool(re.search(r'\bif\s+', code))
    interactivity_score = 0
    if has_input and has_print and has_break and has_if:
        interactivity_score = 3
    elif has_input and has_print and (has_break or has_if):
        interactivity_score = 2
    elif has_input or has_print:
        interactivity_score = 1
    total += interactivity_score
    comments += aia_utils.get_comments("遊戲互動性 (輸入、輸出、條件判斷)", interactivity_score, 3)

    # 3. Creative elements (3 marks)
    # Look for "popular" features: scoring, timer, sound, combo, levels, etc.
    creative_patterns = [
        r'\bscore\b', r'\bpoint\b', r'\btimer\b', r'\btime\b',
        r'\bsound\b', r'\bpygame\b', r'\bcombo\b', r'\blevel\b',
        r'\bdifficult\b', r'\bhigh.?score\b', r'\blife\b', r'\blives\b',
        r'\bpower.?up\b', r'\bmultiplier\b', r'\brandom\b'
    ]
    creative_count = sum(1 for pat in creative_patterns if re.search(pat, code, re.IGNORECASE))
    creative_score = min(3, creative_count)  # up to 3 marks
    total += creative_score
    comments += aia_utils.get_comments("創意元素 (計分、計時、音效、關卡等)", creative_score, 3)

    # 4. Code quality and comments (2 marks)
    has_comments = bool(re.search(r'#.*', code))
    has_variable_names = bool(re.search(r'[a-z_][a-z0-9_]*\s*=', code, re.IGNORECASE))
    # Check for reasonable length (at least 20 lines of meaningful code)
    lines = [l for l in code.split('\n') if l.strip() and not l.strip().startswith('#')]
    has_enough_code = len(lines) >= 20
    quality_score = 0
    if has_comments and has_variable_names and has_enough_code:
        quality_score = 2
    elif (has_comments or has_variable_names) and has_enough_code:
        quality_score = 1
    else:
        quality_score = 0
    total += quality_score
    comments += aia_utils.get_comments("程式碼品質 (註解、變數命名、程式量)", quality_score, 2)

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
        submissions.loc[idx, "marks"] = mark
        submissions.loc[idx, "comments"] = comments
    return submissions