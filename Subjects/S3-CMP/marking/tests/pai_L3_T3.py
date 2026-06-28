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
    
    # 1. Check import cv2 (1 mark)
    has_cv2 = bool(re.search(r'import\s+cv2', code))
    if has_cv2:
        comments += aia_utils.get_comments("匯入 cv2 模組", 1, 1)
        total += 1
    else:
        comments += aia_utils.get_comments("匯入 cv2 模組", 0, 1)
    
    # 2. Check CascadeClassifier usage (1 mark)
    has_cascade = bool(re.search(r'CascadeClassifier', code))
    if has_cascade:
        comments += aia_utils.get_comments("載入人臉識別模型 CascadeClassifier", 1, 1)
        total += 1
    else:
        comments += aia_utils.get_comments("載入人臉識別模型 CascadeClassifier", 0, 1)
    
    # 3. Check VideoCapture (1 mark)
    has_videocap = bool(re.search(r'VideoCapture', code))
    if has_videocap:
        comments += aia_utils.get_comments("讀取影片 VideoCapture", 1, 1)
        total += 1
    else:
        comments += aia_utils.get_comments("讀取影片 VideoCapture", 0, 1)
    
    # 4. Check detectMultiScale (1 mark)
    has_detect = bool(re.search(r'detectMultiScale', code))
    if has_detect:
        comments += aia_utils.get_comments("偵測人臉 detectMultiScale", 1, 1)
        total += 1
    else:
        comments += aia_utils.get_comments("偵測人臉 detectMultiScale", 0, 1)
    
    # 5. Check GaussianBlur (1 mark)
    has_blur = bool(re.search(r'GaussianBlur', code))
    if has_blur:
        comments += aia_utils.get_comments("高斯模糊 GaussianBlur", 1, 1)
        total += 1
    else:
        comments += aia_utils.get_comments("高斯模糊 GaussianBlur", 0, 1)
    
    # 6. Check ROI extraction (frame[y:y+h, x:x+w]) (1 mark)
    has_roi = bool(re.search(r'frame\s*\[\s*y\s*:\s*y\s*\+\s*h\s*,\s*x\s*:\s*x\s*\+\s*w\s*\]', code))
    if has_roi:
        comments += aia_utils.get_comments("擷取臉部區域 ROI", 1, 1)
        total += 1
    else:
        comments += aia_utils.get_comments("擷取臉部區域 ROI", 0, 1)
    
    # 7. Check putText with "Privacy Mode: ON" (1 mark)
    has_puttext = bool(re.search(r'putText.*Privacy\s*Mode\s*:\s*ON', code, re.IGNORECASE))
    if has_puttext:
        comments += aia_utils.get_comments("顯示文字 Privacy Mode: ON", 1, 1)
        total += 1
    else:
        comments += aia_utils.get_comments("顯示文字 Privacy Mode: ON", 0, 1)
    
    # 8. Check while loop for video processing (1 mark)
    has_while = bool(re.search(r'while\s+True', code))
    if has_while:
        comments += aia_utils.get_comments("使用 while 迴圈處理影片", 1, 1)
        total += 1
    else:
        comments += aia_utils.get_comments("使用 while 迴圈處理影片", 0, 1)
    
    # 9. Check break condition (ret or q key) (1 mark)
    has_break = bool(re.search(r'if\s+not\s+ret\s*:\s*break', code)) or bool(re.search(r'if\s+cv2\.waitKey.*ord\([\'"]q[\'"]\)\s*:\s*break', code))
    if has_break:
        comments += aia_utils.get_comments("正確的 break 條件 (ret 或 q 鍵)", 1, 1)
        total += 1
    else:
        comments += aia_utils.get_comments("正確的 break 條件 (ret 或 q 鍵)", 0, 1)
    
    # 10. Check release/destroyAllWindows (1 mark)
    has_release = bool(re.search(r'release\(\)', code)) and bool(re.search(r'destroyAllWindows\(\)', code))
    if has_release:
        comments += aia_utils.get_comments("釋放資源 release/destroyAllWindows", 1, 1)
        total += 1
    else:
        comments += aia_utils.get_comments("釋放資源 release/destroyAllWindows", 0, 1)
    
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