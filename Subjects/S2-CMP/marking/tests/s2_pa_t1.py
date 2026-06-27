"""
中二級下學期實習試 - 第一部分 (15 marks)
Students submit Task1.docx with Gemini prompt choices and outputs.
"""

RUBRIC = [
    {"key": "mark1", "name": "正確提示語 (a)", "max_marks": 5},
    {"key": "mark2", "name": "追問提示語 (b)", "max_marks": 5},
    {"key": "mark3", "name": "Gemini 產出內容", "max_marks": 5},
]

import os
import re

import aia_util as aia_utils
from docx_util import count_docx_images, normalize_text, read_docx_text


def _has_pattern(text, patterns):
    return any(re.search(pattern, text, re.I) for pattern in patterns)


def evaluate_docx(filepath):
    comments = "[O]: Correct\n[-]: Minor error\n[X]: Major error\n\n"
    text = normalize_text(read_docx_text(filepath))
    image_count = count_docx_images(filepath)
    mark1 = mark2 = mark3 = 0

    # (a) Correct choice is B — learning tips for F2 students, bullets, 4 points, 2 verification methods
    option_b_patterns = [
        r"善用生成式人工智能完成專題研習",
        r"給中二學生閱讀",
        r"4\s*個重點",
        r"2\s*個查證方法",
        r"不可直接抄用\s*ai",
    ]
    option_b_hits = sum(1 for p in option_b_patterns if re.search(p, text, re.I))
    if _has_pattern(text, [r"^\s*b[\.\)、]", r"選項\s*b", r"答案\s*[：:]\s*b"]):
        mark1 += 2
        comments += "[O] 標示選擇 B\n"
    elif option_b_hits >= 3:
        mark1 += 1
        comments += "[-] 含選項 B 內容但未明確標示\n"
    else:
        comments += "[X] 未見正確提示語 (應選 B)\n"

    if option_b_hits >= 4:
        mark1 += 3
        comments += f"[O] 提示語內容完整 ({option_b_hits}/5 項)\n"
    elif option_b_hits >= 2:
        mark1 += 2
        comments += f"[-] 提示語內容部分完整 ({option_b_hits}/5 項)\n"
    else:
        comments += "[X] 提示語內容不足\n"
    mark1 = min(mark1, 5)
    comments += aia_utils.get_comments("正確提示語 (a)", mark1, 5)

    # (b) Follow-up prompt
    followup_patterns = [
        r"3\s*個核心專有名詞",
        r"英文翻譯",
        r"簡短解釋",
        r"抽選",
    ]
    follow_hits = sum(1 for p in followup_patterns if re.search(p, text, re.I))
    if follow_hits >= 3:
        mark2 = 5
        comments += "[O] 追問提示語完整\n"
    elif follow_hits >= 2:
        mark2 = 3
        comments += "[-] 追問提示語部分完整\n"
    elif follow_hits >= 1:
        mark2 = 1
        comments += "[-] 追問提示語僅部分出現\n"
    else:
        comments += "[X] 缺少追問提示語 (b)\n"
    comments += aia_utils.get_comments("追問提示語 (b)", mark2, 5)

    # Gemini outputs — accept screenshot-only submissions with partial credit
    output_patterns = [
        r"查證",
        r"專題研習|生成式|人工智能|ai",
        r"抄用|引用|核實",
        r"[•·\-–—]\s*\S+|^\s*\d+[\.\)、]",
    ]
    output_hits = sum(1 for p in output_patterns if re.search(p, text, re.I | re.M))
    text_len = len(re.sub(r"\s+", "", text))
    if output_hits >= 3 and text_len > 200:
        mark3 = 5
        comments += "[O] Gemini 產出內容充足\n"
    elif output_hits >= 2 or text_len > 120:
        mark3 = 3
        comments += "[-] Gemini 產出內容一般\n"
    elif text_len > 60:
        mark3 = 1
        comments += "[-] Gemini 產出內容偏少\n"
    elif image_count >= 2:
        mark3 = 2
        comments += "[-] 主要以截圖呈現 Gemini 產出（文字未能擷取）\n"
    elif image_count >= 1:
        mark3 = 1
        comments += "[-] 有截圖但文字未能擷取\n"
    else:
        comments += "[X] Gemini 產出內容不足\n"
    comments += aia_utils.get_comments("Gemini 產出內容", mark3, 5)

    return mark1 + mark2 + mark3, comments, mark1, mark2, mark3


def test(submissions):
    for idx, row in submissions.iterrows():
        submissions.loc[idx, "marks"] = 0
        submissions.loc[idx, "comments"] = ""
        submissions.loc[idx, "mark1"] = 0
        submissions.loc[idx, "mark2"] = 0
        submissions.loc[idx, "mark3"] = 0

        filepath = str(row.get("filepath") or "")
        if not filepath or not os.path.exists(filepath):
            submissions.loc[idx, "comments"] = (
                "[O]: Correct\n[-]: Minor error\n[X]: Major error\n\n"
                "[X] Task1.docx not submitted\n"
            )
            continue
        if not filepath.lower().endswith(".docx"):
            # Some students submit PDF instead of DOCX — give minimal credit for submission
            submissions.loc[idx, "marks"] = 1
            submissions.loc[idx, "comments"] = (
                "[O]: Correct\n[-]: Minor error\n[X]: Major error\n\n"
                "[X] Expected Task1.docx submission\n"
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
