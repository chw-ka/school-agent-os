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


def _has_exit_handling(code):
    exit_patterns = [
        r"cv2\.waitKey.*32|0x20|ord\s*\(\s*['\"]\s+['\"]\s*\)",
        r"cv2\.waitKey.*27|0x1[Bb]|==\s*27",
        r"ord\s*\(\s*['\"]q['\"]\s*\)|ord\s*\(\s*['\"]Q['\"]\s*\)",
        r"[cC]hr\s*\(\s*\w+\s*\)\s*(?:==|in)\s*.*['\"]q['\"]",
        r"==\s*['\"]q['\"]|==\s*['\"]Q['\"]",
    ]
    if any(re.search(pattern, code) for pattern in exit_patterns):
        return True
    if re.search(r"cv2\.waitKey", code) and re.search(r"\bbreak\b", code):
        return True
    return False


def _has_release(code):
    return bool(re.search(r"\w+\.release\s*\(\)", code))


def evaluate(filepath):
    code = read_code(filepath)
    comments = ""
    total = 0

    if re.search(r"import\s+cv2", code):
        comments += aia_utils.get_comments("匯入 cv2 模組", 1, 1)
        total += 1
    else:
        comments += aia_utils.get_comments("匯入 cv2 模組", 0, 1)

    if re.search(r"cv2\.VideoCapture\s*\(\s*0\s*\)", code):
        comments += aia_utils.get_comments("使用 cv2.VideoCapture(0) 開啟鏡頭", 1, 1)
        total += 1
    else:
        comments += aia_utils.get_comments("使用 cv2.VideoCapture(0) 開啟鏡頭", 0, 1)

    if re.search(r"cv2\.selectROI", code):
        comments += aia_utils.get_comments("手動圈出要追蹤的物件 (cv2.selectROI)", 1, 1)
        total += 1
    else:
        comments += aia_utils.get_comments("手動圈出要追蹤的物件 (cv2.selectROI)", 0, 1)

    if re.search(r"tracker\s*=\s*cv2\.(legacy\.)?Tracker\w+_create\s*\(", code) and \
       re.search(r"tracker\.init\s*\(", code):
        comments += aia_utils.get_comments("初始化追蹤器 (建立 + init)", 1, 1)
        total += 1
    else:
        comments += aia_utils.get_comments("初始化追蹤器 (建立 + init)", 0, 1)

    if re.search(r"while\s+True", code) or re.search(r"while\s+[^:]*:", code):
        comments += aia_utils.get_comments("即時追蹤迴圈 (while)", 1, 1)
        total += 1
    else:
        comments += aia_utils.get_comments("即時追蹤迴圈 (while)", 0, 1)

    if re.search(r"tracker\.update", code) and re.search(r"cv2\.rectangle", code):
        comments += aia_utils.get_comments("更新追蹤器並繪製矩形框", 1, 1)
        total += 1
    else:
        comments += aia_utils.get_comments("更新追蹤器並繪製矩形框", 0, 1)

    if re.search(r"cv2\.rectangle.*(255\s*,\s*0\s*,\s*255|128\s*,\s*0\s*,\s*128)", code) or \
       re.search(r"colors?\s*=\s*\(?\s*255\s*,\s*0\s*,\s*255\s*\)?", code) or \
       re.search(r"colors?\s*=\s*\(?\s*128\s*,\s*0\s*,\s*128\s*\)?", code):
        comments += aia_utils.get_comments("紫色方框 (BGR: 255,0,255 或類似)", 1, 1)
        total += 1
    else:
        comments += aia_utils.get_comments("紫色方框 (BGR: 255,0,255 或類似)", 0, 1)

    if re.search(r"cv2\.imshow", code):
        comments += aia_utils.get_comments("顯示影像 (cv2.imshow)", 1, 1)
        total += 1
    else:
        comments += aia_utils.get_comments("顯示影像 (cv2.imshow)", 0, 1)

    if _has_exit_handling(code):
        comments += aia_utils.get_comments("按鍵結束程式 (空白鍵 / ESC / q)", 1, 1)
        total += 1
    else:
        comments += aia_utils.get_comments("按鍵結束程式 (空白鍵 / ESC / q)", 0, 1)

    if _has_release(code):
        comments += aia_utils.get_comments("釋放鏡頭資源 (.release())", 1, 1)
        total += 1
    else:
        comments += aia_utils.get_comments("釋放鏡頭資源 (.release())", 0, 1)

    header = "[O]: Correct\n[-]: Minor error\n[X]: Major error\n\n"
    return total, header + comments


def test(submissions):
    for idx, row in submissions.iterrows():
        submissions.loc[idx, "marks"] = 0
        submissions.loc[idx, "comments"] = ""
        filepath = row.get("filepath")
        if not filepath or not os.path.exists(str(filepath)):
            submissions.loc[idx, "comments"] = "No file found in the submission\n"
            continue
        mark, comments = evaluate(str(filepath))
        mark, comments = finalize_ch1_4_mark(mark, comments, str(filepath), chapter=4)
        submissions.loc[idx, "marks"] = mark
        submissions.loc[idx, "comments"] = comments
    return submissions
