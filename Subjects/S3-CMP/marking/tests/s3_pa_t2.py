"""
S3 下學期實習試：任務二 — 物件追蹤 (15 marks)
Students complete fill-in-the-blank blanks (a)-(h) in task2_2526.py using OpenCV.
"""

RUBRIC = [
    {"key": "mark1", "name": "Setup (import, VideoCapture, first read)", "max_marks": 3},
    {"key": "mark2", "name": "ROI selection & tracker init", "max_marks": 4},
    {"key": "mark3", "name": "Main tracking loop", "max_marks": 8},
]

import os
import re
import aia_util as aia_utils


def test(submissions):
    for idx, row in submissions.iterrows():
        submissions.loc[idx, "marks"] = 0
        submissions.loc[idx, "comments"] = ""

        # filepath IS the student's submitted .py file (renamed with student/submission IDs)
        task2_file = str(row.get("filepath", "") or "")
        if not task2_file or not os.path.exists(task2_file):
            submissions.loc[idx, "comments"] = (
                "[O]: Correct\n[-]: Minor error\n[X]: Major error\n\n"
                "[X]: task2_2526.py not submitted\n"
            )
            continue

        try:
            with open(task2_file, encoding="utf-8") as f:
                code = f.read()
        except Exception:
            with open(task2_file, encoding="latin-1") as f:
                code = f.read()

        comments = "[O]: Correct\n[-]: Minor error\n[X]: Major error\n\n"
        mark1 = mark2 = mark3 = 0

        # ==================== SECTION 1: Import & Video Setup (3 marks) ====================
        # (a) import cv2
        if re.search(r"import\s+cv2", code):
            mark1 += 1
            comments += "[O]: (a) import cv2\n"
        else:
            comments += "[X]: (a) Missing import cv2\n"

        # (d) cv2.VideoCapture(...)
        if re.search(r"cv2\.VideoCapture\s*\(", code):
            mark1 += 1
            comments += "[O]: (d) cv2.VideoCapture(...)\n"
        else:
            comments += "[X]: (d) Missing cv2.VideoCapture\n"

        # (d) video.read() for first frame (before while loop)
        # Look for read() call before the while True block
        before_while = code.split("while")[0] if "while" in code else code
        if re.search(r"\.\s*read\s*\(\s*\)", before_while):
            mark1 += 1
            comments += "[O]: (d) video.read() for first frame\n"
        else:
            comments += "[X]: (d) Missing video.read() to get first frame\n"

        submissions.loc[idx, "mark1"] = mark1
        submissions.loc[idx, "marks"] += mark1
        comments += aia_utils.get_comments("Setup (import, VideoCapture, first read)", mark1, 3)

        # ==================== SECTION 2: ROI Selection & Tracker Init (4 marks) ====================
        # (e) cv2.selectROI(...)
        if re.search(r"cv2\.selectROI\s*\(", code):
            mark2 += 2
            comments += "[O]: (e) cv2.selectROI(...)\n"
        else:
            comments += "[X]: (e) Missing cv2.selectROI\n"

        # (e) tracker.init(frame, bbox)
        if re.search(r"tracker\s*\.\s*init\s*\(", code):
            mark2 += 2
            comments += "[O]: (e) tracker.init(frame, bbox)\n"
        else:
            comments += "[X]: (e) Missing tracker.init(...)\n"

        submissions.loc[idx, "mark2"] = mark2
        submissions.loc[idx, "marks"] += mark2
        comments += aia_utils.get_comments("ROI selection & tracker init", mark2, 4)

        # ==================== SECTION 3: Main Tracking Loop (8 marks) ====================
        # Extract the while loop body
        while_match = re.search(r"while\s+True\s*:(.*)", code, re.DOTALL)
        loop_body = while_match.group(1) if while_match else ""

        # (f) video.read() inside loop
        if re.search(r"\.\s*read\s*\(\s*\)", loop_body):
            mark3 += 1
            comments += "[O]: (f) video.read() in loop\n"
        else:
            comments += "[X]: (f) Missing video.read() inside loop\n"

        # (f) tracker.update(frame)
        if re.search(r"tracker\s*\.\s*update\s*\(", loop_body):
            mark3 += 2
            comments += "[O]: (f) tracker.update(frame)\n"
        else:
            comments += "[X]: (f) Missing tracker.update(...)\n"

        # (g) cv2.rectangle(...)
        rect_match = re.search(r"cv2\.rectangle\s*\(", loop_body)
        if rect_match:
            # Check args look reasonable: frame, point1, point2, color, thickness
            rect_call = loop_body[rect_match.start():]
            paren_depth = 0
            end = 0
            for i, ch in enumerate(rect_call):
                if ch == "(":
                    paren_depth += 1
                elif ch == ")":
                    paren_depth -= 1
                    if paren_depth == 0:
                        end = i + 1
                        break
            rect_full = rect_call[:end]
            # Check for x+w and y+h style (correct bounding box)
            if re.search(r"x\s*\+\s*w", rect_full) and re.search(r"y\s*\+\s*h", rect_full):
                mark3 += 3
                comments += "[O]: (g) cv2.rectangle with correct bbox coords\n"
            else:
                mark3 += 1
                comments += "[-]: (g) cv2.rectangle present but bbox coords may be incorrect\n"
        else:
            comments += "[X]: (g) Missing cv2.rectangle\n"

        # (h) cv2.imshow(...)
        if re.search(r"cv2\.imshow\s*\(", loop_body):
            mark3 += 2
            comments += "[O]: (h) cv2.imshow(...)\n"
        else:
            comments += "[X]: (h) Missing cv2.imshow\n"

        submissions.loc[idx, "mark3"] = mark3
        submissions.loc[idx, "marks"] += mark3
        comments += aia_utils.get_comments("Main tracking loop", mark3, 8)

        submissions.loc[idx, "comments"] = comments

    return submissions
