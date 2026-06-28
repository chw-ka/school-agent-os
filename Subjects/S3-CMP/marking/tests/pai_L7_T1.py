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
    
    # Check 1: Has a main loop or interactive structure (2 marks)
    has_loop = bool(re.search(r'\bwhile\s+True\b|\bwhile\s+.*:', code))
    has_input = bool(re.search(r'\binput\s*\(', code))
    if has_loop and has_input:
        total += 2
        comments += aia_utils.get_comments("Interactive loop with input", 2, 2)
    elif has_loop or has_input:
        total += 1
        comments += aia_utils.get_comments("Interactive loop or input present", 1, 2)
    else:
        comments += aia_utils.get_comments("Missing interactive loop/input", 0, 2)
    
    # Check 2: Uses at least one external library (2 marks)
    libs = ['gtts', 'googletrans', 'speech_recognition', 'opencv', 'cv2', 'numpy', 'pandas', 'matplotlib', 'tkinter', 'random', 'datetime']
    found_libs = [lib for lib in libs if lib in code.lower()]
    if len(found_libs) >= 1:
        total += 2
        comments += aia_utils.get_comments(f"Uses external library: {', '.join(found_libs[:3])}", 2, 2)
    else:
        comments += aia_utils.get_comments("No external library found", 0, 2)
    
    # Check 3: Has function definitions (2 marks)
    func_count = len(re.findall(r'\bdef\s+\w+\s*\(', code))
    if func_count >= 2:
        total += 2
        comments += aia_utils.get_comments(f"Has {func_count} function definitions", 2, 2)
    elif func_count == 1:
        total += 1
        comments += aia_utils.get_comments("Has 1 function definition", 1, 2)
    else:
        comments += aia_utils.get_comments("No function definitions", 0, 2)
    
    # Check 4: Has conditional logic (if/elif/else) (2 marks)
    has_if = bool(re.search(r'\bif\s+.*:', code))
    has_elif = bool(re.search(r'\belif\s+.*:', code))
    has_else = bool(re.search(r'\belse\s*:', code))
    if has_if and (has_elif or has_else):
        total += 2
        comments += aia_utils.get_comments("Has if-elif-else conditional logic", 2, 2)
    elif has_if:
        total += 1
        comments += aia_utils.get_comments("Has if statement", 1, 2)
    else:
        comments += aia_utils.get_comments("No conditional logic", 0, 2)
    
    # Check 5: Has string formatting or f-strings (1 mark)
    has_fstring = bool(re.search(r'f["\']', code))
    has_format = bool(re.search(r'\.format\(', code))
    has_percent = bool(re.search(r'%[sd]', code))
    if has_fstring or has_format or has_percent:
        total += 1
        comments += aia_utils.get_comments("Uses string formatting", 1, 1)
    else:
        comments += aia_utils.get_comments("No string formatting", 0, 1)
    
    # Check 6: Has comments or docstrings (1 mark)
    has_comment = bool(re.search(r'#.*', code))
    has_docstring = bool(re.search(r'""".*?"""', code, re.DOTALL))
    if has_comment or has_docstring:
        total += 1
        comments += aia_utils.get_comments("Has comments/docstrings", 1, 1)
    else:
        comments += aia_utils.get_comments("No comments/docstrings", 0, 1)
    
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