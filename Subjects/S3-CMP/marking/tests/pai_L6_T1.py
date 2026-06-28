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
    
    # Check 1: File named Task3_3X99.py (or similar) - 1 mark
    filename = os.path.basename(filepath)
    if re.search(r'Task3_3X99', filename, re.IGNORECASE):
        total += 1
        comments += aia_utils.get_comments("File named Task3_3X99.py", 1, 1)
    else:
        comments += aia_utils.get_comments("File named Task3_3X99.py", 0, 1)
    
    # Check 2: Has a main game loop (while True or while with break) - 2 marks
    has_while_true = bool(re.search(r'while\s+True', code))
    has_while_break = bool(re.search(r'while\s+.*:', code) and re.search(r'\bbreak\b', code))
    if has_while_true or has_while_break:
        total += 2
        comments += aia_utils.get_comments("Main game loop present (while True or while with break)", 2, 2)
    else:
        comments += aia_utils.get_comments("Main game loop present (while True or while with break)", 0, 2)
    
    # Check 3: Has at least one "psychological trap" element - 3 marks
    trap_patterns = [
        r'combo', r'連擊', r'multiplier', r'加倍',
        r'sound', r'音效', r'pygame\.mixer', r'playsound',
        r'timer', r'時間', r'countdown', r'deadline',
        r'leaderboard', r'排行榜', r'high.?score',
        r'level', r'關卡', r'difficulty', r'難度',
        r'achievement', r'成就', r'badge', r'徽章',
        r'streak', r'連勝', r'chain', r'連鎖',
        r'power.?up', r'道具', r'boost', r'加成',
        r'animation', r'動畫', r'effect', r'特效',
        r'random', r'隨機', r'surprise', r'驚喜'
    ]
    trap_found = False
    for pattern in trap_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            trap_found = True
            break
    if trap_found:
        total += 3
        comments += aia_utils.get_comments("Psychological trap element present (combo/sound/timer/etc.)", 3, 3)
    else:
        comments += aia_utils.get_comments("Psychological trap element present (combo/sound/timer/etc.)", 0, 3)
    
    # Check 4: Has user input/interaction - 2 marks
    input_patterns = [
        r'input\s*\(', r'pygame\.key', r'pygame\.MOUSEBUTTONDOWN',
        r'event\.key', r'get_pressed', r'keyboard\.read',
        r'tkinter.*Button', r'bind\s*\(', r'command\s*='
    ]
    has_input = any(re.search(p, code) for p in input_patterns)
    if has_input:
        total += 2
        comments += aia_utils.get_comments("User input/interaction present", 2, 2)
    else:
        comments += aia_utils.get_comments("User input/interaction present", 0, 2)
    
    # Check 5: Has scoring or progress tracking - 2 marks
    score_patterns = [
        r'score', r'分數', r'point', r'points',
        r'progress', r'進度', r'count', r'counter',
        r'level', r'關卡', r'wave', r'round'
    ]
    has_score = any(re.search(p, code, re.IGNORECASE) for p in score_patterns)
    if has_score:
        total += 2
        comments += aia_utils.get_comments("Scoring or progress tracking present", 2, 2)
    else:
        comments += aia_utils.get_comments("Scoring or progress tracking present", 0, 2)
    
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