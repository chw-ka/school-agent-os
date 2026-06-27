import os
import re
import aia_util as aia_utils
from pai_util import read_student_code


def evaluate(filepath):
    code = read_student_code(filepath)
    comments = ""
    total = 0

    # 1. tkinter import (1 mark)
    has_tkinter = bool(re.search(r'import\s+tkinter|from\s+tkinter\s+import', code))
    if has_tkinter:
        total += 1
        comments += aia_utils.get_comments("使用 tkinter 匯入", 1, 1)
    else:
        comments += aia_utils.get_comments("使用 tkinter 匯入", 0, 1)

    # 2. 9 buttons (2 marks) — literal Button() or nested loop creating 3x3 grid
    button_count = len(re.findall(r'\bButton\s*\(', code))
    has_grid = bool(re.search(r'\.grid\s*\(', code))
    has_3x3_loop = bool(re.search(r'for\s+\w+\s+in\s+range\s*\(\s*3\s*\)', code)) and \
                   button_count >= 1 and has_grid
    if (button_count >= 9 or has_3x3_loop) and has_grid:
        total += 2
        comments += aia_utils.get_comments("9 個按鈕與 grid 排版", 2, 2)
    elif button_count >= 9 or has_3x3_loop:
        total += 1
        comments += aia_utils.get_comments("9 個按鈕，但未使用 grid", 1, 2)
    else:
        comments += aia_utils.get_comments("9 個按鈕與 grid 排版", 0, 2)

    # 3. 2D list for board state (2 marks)
    has_2d_list = bool(re.search(r'\[\[.*\]\s*,\s*\[.*\]\s*,\s*\[.*\]\]', code)) or \
                  bool(re.search(r'\[\[["\']?\s*["\']?,\s*["\']?\s*["\']?,\s*["\']?\s*["\']?\]', code))
    # Also check for list comprehension or nested list creation
    has_nested_list = bool(re.search(r'\[\[.*for.*\]\s*for', code)) or \
                      bool(re.search(r'\[\[None\]\s*\*?\s*3\s*for', code))
    if has_2d_list or has_nested_list:
        total += 2
        comments += aia_utils.get_comments("使用二維列表儲存棋盤狀態", 2, 2)
    else:
        comments += aia_utils.get_comments("使用二維列表儲存棋盤狀態", 0, 2)

    # 4. Two players alternate X/O (2 marks)
    has_x = bool(re.search(r'["\']X["\']', code))
    has_o = bool(re.search(r'["\']O["\']', code))
    has_alternate = bool(re.search(r'(turn|player|count|current)\s*[=:]\s*(0|1|2|["\']X["\']|["\']O["\'])', code, re.I))
    if has_x and has_o and has_alternate:
        total += 2
        comments += aia_utils.get_comments("兩人輪流畫 X 或 O", 2, 2)
    elif has_x and has_o:
        total += 1
        comments += aia_utils.get_comments("兩人輪流畫 X 或 O（缺少輪流機制）", 1, 2)
    else:
        comments += aia_utils.get_comments("兩人輪流畫 X 或 O", 0, 2)

    # 5. Win detection with messagebox (2 marks)
    has_win_check = bool(re.search(r'(win|check|victory|三|連線|row|column|diag)', code, re.I))
    has_messagebox = bool(re.search(r'messagebox|showinfo|showwarning|showerror', code))
    if has_win_check and has_messagebox:
        total += 2
        comments += aia_utils.get_comments("贏家偵測與彈窗顯示", 2, 2)
    elif has_win_check or has_messagebox:
        total += 1
        comments += aia_utils.get_comments("贏家偵測與彈窗顯示（部分完成）", 1, 2)
    else:
        comments += aia_utils.get_comments("贏家偵測與彈窗顯示", 0, 2)

    # 6. UI customization (1 mark) - check for color or font changes
    has_color = bool(re.search(r'(bg|background|fg|foreground|font)\s*[=:]', code))
    if has_color:
        total += 1
        comments += aia_utils.get_comments("按鈕顏色或字體大小修改", 1, 1)
    else:
        comments += aia_utils.get_comments("按鈕顏色或字體大小修改", 0, 1)

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
        submissions.loc[idx, "marks"] = mark
        submissions.loc[idx, "comments"] = comments
    return submissions