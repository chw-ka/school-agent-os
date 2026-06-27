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
    comments = ""
    total = 0
    
    # 1. Check cv2 import (1 mark)
    has_cv2 = bool(re.search(r'import\s+cv2', code))
    comments += aia_utils.get_comments("匯入 cv2 模組", 1 if has_cv2 else 0, 1)
    total += 1 if has_cv2 else 0
    
    # 2. Check VideoCapture with walkingGirl.mp4 (1 mark)
    has_videocapture = bool(re.search(r'cv2\.VideoCapture\s*\(\s*[\'"]walkingGirl\.mp4[\'"]\s*\)', code))
    comments += aia_utils.get_comments("開啟短片 walkingGirl.mp4", 1 if has_videocapture else 0, 1)
    total += 1 if has_videocapture else 0
    
    # 3. Check face detection using Haar cascade (2 marks)
    has_cascade = bool(re.search(r'cv2\.CascadeClassifier\s*\(', code))
    has_haar = bool(re.search(r'haarcascade_frontalface', code, re.IGNORECASE))
    has_detect = bool(re.search(r'detectMultiScale', code))
    face_detect_score = 0
    if has_cascade and has_detect:
        face_detect_score = 2
    elif has_cascade or has_detect:
        face_detect_score = 1
    comments += aia_utils.get_comments("使用 Haar Cascade 人臉偵測", face_detect_score, 2)
    total += face_detect_score
    
    # 4. Check purple rectangle (red+blue = purple) (2 marks)
    has_rectangle = bool(re.search(r'cv2\.rectangle', code))
    has_purple = bool(re.search(r'\(\s*255\s*,\s*0\s*,\s*255\s*\)', code))  # BGR purple
    has_red_blue = bool(re.search(r'\(\s*255\s*,\s*0\s*,\s*255\s*\)', code))
    purple_score = 0
    if has_rectangle and has_purple:
        purple_score = 2
    elif has_rectangle:
        purple_score = 1
    comments += aia_utils.get_comments("在臉部畫上紫色方框 (BGR: 255,0,255)", purple_score, 2)
    total += purple_score
    
    # 5. Check loop until 'q' key (2 marks)
    has_while = bool(re.search(r'while\s+True', code))
    has_break_q = bool(re.search(r'if\s+cv2\.waitKey.*ord\([\'"]q[\'"]\)', code))
    has_break = bool(re.search(r'break', code))
    loop_score = 0
    if has_while and has_break_q:
        loop_score = 2
    elif has_while and has_break:
        loop_score = 1
    comments += aia_utils.get_comments("使用 while 迴圈並按 q 鍵退出", loop_score, 2)
    total += loop_score
    
    # 6. Check release and destroy (1 mark)
    has_release = bool(re.search(r'cap\.release\s*\(\)', code))
    has_destroy = bool(re.search(r'cv2\.destroyAllWindows\s*\(\)', code))
    cleanup_score = 0
    if has_release and has_destroy:
        cleanup_score = 1
    comments += aia_utils.get_comments("釋放資源 (cap.release 及 destroyAllWindows)", cleanup_score, 1)
    total += cleanup_score
    
    # 7. Check imshow (1 mark)
    has_imshow = bool(re.search(r'cv2\.imshow', code))
    comments += aia_utils.get_comments("顯示視窗 (cv2.imshow)", 1 if has_imshow else 0, 1)
    total += 1 if has_imshow else 0
    
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