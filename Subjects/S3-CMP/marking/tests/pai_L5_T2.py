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

    # 1. Basic structure: tkinter import, main window, grid/buttons (2 marks)
    has_tkinter = "import tkinter" in code or "from tkinter" in code
    has_window = "Tk(" in code or "tkinter.Tk(" in code or "tk.Tk(" in code
    has_grid = "grid(" in code
    has_button = "Button(" in code
    struct_ok = has_tkinter and has_window and has_grid and has_button
    if struct_ok:
        total += 2
        comments += aia_utils.get_comments("Basic tkinter structure (import, window, grid, buttons)", 2, 2)
    else:
        comments += aia_utils.get_comments("Basic tkinter structure (import, window, grid, buttons)", 0, 2)
        comments += "[-] Missing tkinter import, window, grid, or Button\n"

    # 2. 2D list for board (1 mark)
    has_2d_list = re.search(r"\[\[.*\]\s*,\s*\[.*\]\s*,\s*\[.*\]\]", code) or "board" in code.lower()
    if has_2d_list:
        total += 1
        comments += aia_utils.get_comments("2D list board representation", 1, 1)
    else:
        comments += aia_utils.get_comments("2D list board representation", 0, 1)
        comments += "[-] No 2D list board found\n"

    # 3. Random move for computer (Task 2.1) (2 marks)
    has_random = "import random" in code or "from random" in code
    has_random_choice = "random.choice" in code or "random.randint" in code or "choice(" in code
    if has_random and has_random_choice:
        total += 2
        comments += aia_utils.get_comments("Random computer move (Task 2.1)", 2, 2)
    else:
        comments += aia_utils.get_comments("Random computer move (Task 2.1)", 0, 2)
        comments += "[-] Missing random import or random move logic\n"

    # 4. Minimax algorithm (Task 2.2) (3 marks)
    has_minimax = "minimax" in code.lower()
    has_alpha_beta = "alpha" in code.lower() and "beta" in code.lower()
    has_recursive = re.search(r"def\s+\w*minimax\w*\s*\(", code, re.IGNORECASE)
    if has_minimax and has_recursive:
        total += 3
        comments += aia_utils.get_comments("Minimax algorithm (Task 2.2)", 3, 3)
    elif has_minimax:
        total += 2
        comments += aia_utils.get_comments("Minimax algorithm (Task 2.2)", 2, 3)
        comments += "[-] Minimax mentioned but not implemented as a function\n"
    else:
        comments += aia_utils.get_comments("Minimax algorithm (Task 2.2)", 0, 3)
        comments += "[X] No Minimax algorithm found\n"

    # 5. Difficulty selection buttons (simple/normal/hard) (2 marks)
    has_difficulty = re.search(r"(simple|normal|hard|easy|medium|difficult|難度)", code, re.IGNORECASE)
    has_difficulty_button = re.search(r"Button\(.*(simple|normal|hard|easy|medium|difficult|難度)", code, re.IGNORECASE)
    if has_difficulty and has_difficulty_button:
        total += 2
        comments += aia_utils.get_comments("Difficulty selection buttons", 2, 2)
    elif has_difficulty:
        total += 1
        comments += aia_utils.get_comments("Difficulty selection buttons", 1, 2)
        comments += "[-] Difficulty mentioned but no button found\n"
    else:
        comments += aia_utils.get_comments("Difficulty selection buttons", 0, 2)
        comments += "[-] No difficulty selection found\n"

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