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
    
    # 1. Check cv2 import (1 mark)
    if re.search(r'import\s+cv2', code):
        total += 1
        comments += aia_utils.get_comments("Import cv2", 1, 1)
    else:
        comments += aia_utils.get_comments("Import cv2", 0, 1) + "[-]: Missing cv2 import\n"
    
    # 2. Check imread (1 mark)
    if re.search(r'cv2\.imread\s*\(', code):
        total += 1
        comments += aia_utils.get_comments("Read image with imread", 1, 1)
    else:
        comments += aia_utils.get_comments("Read image with imread", 0, 1) + "[X]: Missing cv2.imread\n"
    
    # 3. Check CascadeClassifier (1 mark)
    if re.search(r'CascadeClassifier', code):
        total += 1
        comments += aia_utils.get_comments("Load Haar Cascade", 1, 1)
    else:
        comments += aia_utils.get_comments("Load Haar Cascade", 0, 1) + "[X]: Missing CascadeClassifier\n"
    
    # 4. Check detectMultiScale (1 mark)
    if re.search(r'detectMultiScale', code):
        total += 1
        comments += aia_utils.get_comments("Face detection with detectMultiScale", 1, 1)
    else:
        comments += aia_utils.get_comments("Face detection with detectMultiScale", 0, 1) + "[X]: Missing detectMultiScale\n"
    
    # 5. Check rectangle drawing (1 mark)
    if re.search(r'cv2\.rectangle\s*\(', code):
        total += 1
        comments += aia_utils.get_comments("Draw rectangles on faces", 1, 1)
    else:
        comments += aia_utils.get_comments("Draw rectangles on faces", 0, 1) + "[X]: Missing cv2.rectangle\n"
    
    # 6. Check green color (0,255,0) (1 mark)
    if re.search(r'\(0\s*,\s*255\s*,\s*0\)', code):
        total += 1
        comments += aia_utils.get_comments("Green color for rectangles", 1, 1)
    else:
        comments += aia_utils.get_comments("Green color for rectangles", 0, 1) + "[-]: Rectangle color not green (0,255,0)\n"
    
    # 7. Check imshow with window title (1 mark)
    if re.search(r'cv2\.imshow\s*\(', code):
        total += 1
        comments += aia_utils.get_comments("Display result with imshow", 1, 1)
    else:
        comments += aia_utils.get_comments("Display result with imshow", 0, 1) + "[X]: Missing cv2.imshow\n"
    
    # 8. Check waitKey (1 mark)
    if re.search(r'cv2\.waitKey\s*\(', code):
        total += 1
        comments += aia_utils.get_comments("Wait for key press", 1, 1)
    else:
        comments += aia_utils.get_comments("Wait for key press", 0, 1) + "[-]: Missing cv2.waitKey\n"
    
    # 9. Check face count in window title (1 mark)
    if re.search(r'len\s*\(\s*faces\s*\)', code) or re.search(r'str\s*\(\s*len\s*\(\s*faces\s*\)\s*\)', code):
        total += 1
        comments += aia_utils.get_comments("Show face count in window title", 1, 1)
    else:
        comments += aia_utils.get_comments("Show face count in window title", 0, 1) + "[-]: Face count not shown in window title\n"
    
    # 10. Check cvtColor to gray (1 mark)
    if re.search(r'cv2\.cvtColor.*COLOR_BGR2GRAY', code) or re.search(r'cv2\.cvtColor.*COLOR_RGB2GRAY', code):
        total += 1
        comments += aia_utils.get_comments("Convert to grayscale", 1, 1)
    else:
        comments += aia_utils.get_comments("Convert to grayscale", 0, 1) + "[-]: Missing grayscale conversion\n"
    
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
        mark, comments = finalize_ch1_4_mark(mark, comments, str(filepath), chapter=3)
        submissions.loc[idx, "marks"] = mark
        submissions.loc[idx, "comments"] = comments
    return submissions