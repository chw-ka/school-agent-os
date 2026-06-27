"""
中二級下學期實習試 - 第二部分 (15 marks)
Students submit Task2.docx with Gemini image-generation prompts and evaluation.
"""

RUBRIC = [
    {"key": "mark1", "name": "提示語與初次海報 (a)", "max_marks": 5},
    {"key": "mark2", "name": "修正提示語與最終海報 (b)", "max_marks": 5},
    {"key": "mark3", "name": "自我成效評估 (c)", "max_marks": 5},
]

import os
import re

import aia_util as aia_utils
from docx_util import extract_docx_images, normalize_text, read_docx_text
from vision_util import call_gemini_vision_json

_VISION_PROMPT = (
    "A student used Gemini to generate AI-verification educational posters "
    "about responsible AI use / fact-checking (主題：善用AI、先查證後分享). "
    "They should have two versions: an initial draft and a revised version.\n\n"
    "Reply ONLY with valid JSON — no markdown:\n"
    '{"is_ai_poster": true_or_false, "has_two_versions": true_or_false}\n\n'
    "is_ai_poster: true if ANY image looks like an educational poster about AI or fact-checking.\n"
    "has_two_versions: true if there appear to be at least 2 distinct poster images."
)


def _analyze_posters(images):
    """Returns (is_ai_poster: bool, has_two_versions: bool)."""
    if not images:
        return False, False
    result = call_gemini_vision_json(images, _VISION_PROMPT, max_images=4, max_tokens=1024)
    return bool(result.get("is_ai_poster", False)), bool(result.get("has_two_versions", False))


def evaluate_docx(filepath):
    comments = "[O]: Correct\n[-]: Minor error\n[X]: Major error\n\n"
    raw_text = read_docx_text(filepath)
    text = normalize_text(raw_text)
    images = extract_docx_images(filepath)
    image_count = len(images)
    mark1 = mark2 = mark3 = 0

    # Vision check for poster content (helps when student submits images-only)
    vision_is_poster, vision_has_two = _analyze_posters(images)

    # (a) Poster prompt
    prompt_patterns = [
        r"善用\s*ai",
        r"先查證後分享",
        r"教育海報|學校教育海報|海報",
        r"查證|放大鏡|核對",
        r"中學生|學生",
    ]
    prompt_hits = sum(1 for p in prompt_patterns if re.search(p, text, re.I))
    if prompt_hits >= 4:
        mark1 += 3
        comments += f"[O] 海報提示語內容完整 ({prompt_hits}/5 項)\n"
    elif prompt_hits >= 2:
        mark1 += 2
        comments += f"[-] 海報提示語部分完整 ({prompt_hits}/5 項)\n"
    elif prompt_hits >= 1:
        mark1 += 1
        comments += f"[-] 海報提示語僅部分出現 ({prompt_hits}/5 項)\n"
    elif vision_is_poster:
        mark1 += 1
        comments += "[-] 只有圖片提交，未見文字提示語\n"
    else:
        comments += "[X] 海報提示語內容不足\n"

    if image_count >= 1:
        mark1 += 2
        comments += f"[O] 含初次海報截圖 ({image_count} 張圖)\n"
    else:
        comments += "[X] 缺少初次海報截圖\n"
    mark1 = min(mark1, 5)
    comments += aia_utils.get_comments("提示語與初次海報 (a)", mark1, 5)

    # (b) Revision prompt + final poster
    revision_patterns = [
        r"修改|調整|修正|優化|改進|強化|更改",
        r"顏色|放大鏡|查證|瑕疵|清晰",
    ]
    rev_hits = sum(1 for p in revision_patterns if re.search(p, text, re.I))
    if rev_hits >= 2:
        mark2 += 3
        comments += "[O] 含畫面修正提示語\n"
    elif rev_hits >= 1:
        mark2 += 2
        comments += "[-] 修正提示語部分出現\n"
    elif vision_has_two:
        mark2 += 1
        comments += "[-] 有兩張圖但缺少文字修正提示語\n"
    else:
        comments += "[X] 缺少修正提示語 (b)\n"

    if image_count >= 2 or vision_has_two:
        mark2 += 2
        comments += "[O] 含最終海報截圖\n"
    elif image_count >= 1:
        mark2 += 1
        comments += "[-] 可能只有一張海報截圖\n"
    else:
        comments += "[X] 缺少海報截圖\n"
    mark2 = min(mark2, 5)
    comments += aia_utils.get_comments("修正提示語與最終海報 (b)", mark2, 5)

    # (c) Self evaluation — 30-50 Chinese chars expected
    eval_patterns = [
        r"百分之百|100%|達成|要求",
        r"最好|做得最好|優點",
        r"進步|改善|空間|不足",
    ]
    eval_hits = sum(1 for p in eval_patterns if re.search(p, text, re.I))
    chinese_chars = len(re.findall(r"[一-鿿]", raw_text))
    if eval_hits >= 2 and chinese_chars >= 30:
        mark3 = 5
        comments += "[O] 自我成效評估完整\n"
    elif eval_hits >= 1 or chinese_chars >= 20:
        mark3 = 3
        comments += "[-] 自我成效評估部分完整\n"
    elif chinese_chars >= 10:
        mark3 = 1
        comments += "[-] 自我成效評估偏短\n"
    else:
        comments += "[X] 缺少自我成效評估 (c)\n"
    comments += aia_utils.get_comments("自我成效評估 (c)", mark3, 5)

    return mark1 + mark2 + mark3, comments, mark1, mark2, mark3


def test(submissions):
    for idx, row in submissions.iterrows():
        submissions.loc[idx, "marks"] = 0
        submissions.loc[idx, "comments"] = ""
        for key in ("mark1", "mark2", "mark3"):
            submissions.loc[idx, key] = 0

        filepath = str(row.get("filepath") or "")
        if not filepath or not os.path.exists(filepath):
            submissions.loc[idx, "comments"] = (
                "[O]: Correct\n[-]: Minor error\n[X]: Major error\n\n"
                "[X] Task2.docx not submitted\n"
            )
            continue
        if not filepath.lower().endswith(".docx"):
            submissions.loc[idx, "marks"] = 1
            submissions.loc[idx, "comments"] = (
                "[O]: Correct\n[-]: Minor error\n[X]: Major error\n\n"
                "[X] Expected Task2.docx submission\n"
                "[-] 有提交檔案但格式不正確（只可得 1 分）\n"
            )
            continue

        try:
            total, comments, m1, m2, m3 = evaluate_docx(filepath)
        except Exception as exc:
            submissions.loc[idx, "comments"] = (
                "[O]: Correct\n[-]: Minor error\n[X]: Major error\n\n"
                f"[X] Cannot read docx: {exc}\n"
            )
            continue

        submissions.loc[idx, "marks"] = total
        submissions.loc[idx, "comments"] = comments
        submissions.loc[idx, "mark1"] = m1
        submissions.loc[idx, "mark2"] = m2
        submissions.loc[idx, "mark3"] = m3
    return submissions
