"""Exam spec for 25-26 S3 CMP Term 2 written exam (quality-check + concept balance)."""
from __future__ import annotations

import random
import sys
from pathlib import Path
from typing import Optional

_SPEC_DIR = Path(__file__).resolve().parents[1] / "question-quality-check"
if str(_SPEC_DIR) not in sys.path:
    sys.path.insert(0, str(_SPEC_DIR))

from exam_spec import build_spec, make_item
from mcq_answer_keys import MCQ_CORRECT_INDEX

CONCEPT_TARGETS = {
    "生成式AI": {"min": 3, "max": 5},
    "套件與pip": {"min": 1, "max": 3},
    "物件追蹤": {"min": 3, "max": 5},
    "OpenCV": {"min": 4, "max": 8},
    "Vibe Coding": {"min": 3, "max": 6},
    "程式結構": {"min": 3, "max": 6},
    "語音程式": {"min": 4, "max": 8},
    "Cloud API": {"min": 2, "max": 4},
    "學術誠信": {"min": 1, "max": 2},
}

_SUB = ("(a)", "(b)", "(c)", "(d)", "(e)")


def format_matching_rubric_blocks(blocks: list[str]) -> list[str]:
    lines: list[str] = []
    for block_num, letters in enumerate(blocks, start=1):
        for i, ch in enumerate(letters):
            if i == 0:
                lines.append(f"{block_num}.\t{_SUB[i]}\t\t{ch}\t@1分")
            else:
                lines.append(f"{_SUB[i]}\t\t{ch}")
        if block_num < len(blocks):
            lines.append("")
    return lines


def format_tf_rubric(tf: str) -> list[str]:
    lines: list[str] = []
    for i, ch in enumerate(tf):
        if i == 0:
            lines.append(f"1.\t{_SUB[i]}\t\t{ch}\t@1分")
        else:
            lines.append(f"{_SUB[i]}\t\t{ch}")
    return lines


def format_fill_rubric_blocks(blocks: list[list[str]]) -> list[str]:
    lines: list[str] = []
    for block_num, answers in enumerate(blocks, start=1):
        for i, word in enumerate(answers):
            if i == 0:
                lines.append(f"{block_num}.\t{_SUB[i]}\t\t{word}\t@1分")
            else:
                lines.append(f"{_SUB[i]}\t\t{word}")
        if block_num < len(blocks):
            lines.append("")
    return lines


def _mcq_items(mcq_answers: str) -> list[dict]:
    rows: list[tuple[str, str, list[str]]] = [
        ("mcq-01", "生成式AI", ["老師要求用生成式 AI 整理一份 PDF 通告重點，下列哪項較屬合理應用？", "(1)摘要 (2)問答 (3)檢查日期"]),
        ("mcq-02", "套件與pip", ["執行 import cv2 時出現 ModuleNotFoundError，較合理處理是？"]),
        ("mcq-03", "生成式AI", ["AI 捏造看似可信但不存在的內容，較適合稱為？"]),
        ("mcq-04", "學術誠信", ["用 AI 協助寫報告，下列哪項最符合「負責任使用」？"]),
        ("mcq-05", "語音程式", ["語音轉文字程式因網絡中斷崩潰，較應加入？"]),
        ("mcq-06", "物件追蹤", ["要在影片追蹤足球，下列步驟次序最合理？"]),
        ("mcq-07", "OpenCV", ["人臉偵測誤判框太多，較合理調整是？"]),
        ("mcq-08", "生成式AI", ["使用生成式 AI 閱讀長 PDF 時，下列哪項較不合理？"]),
        ("mcq-09", "OpenCV", ["cv2.VideoCapture(0) 的 0 在課堂實驗通常指？"]),
        ("mcq-10", "Vibe Coding", ["Vibe Coding 下，學生最合適扮演？"]),
        ("mcq-11", "Vibe Coding", ["AI 寫的遊戲太快，學生最應？"]),
        ("mcq-12", "OpenCV", ["拍照做人臉偵測前先把影像轉灰階，主要原因是？"]),
        ("mcq-13", "物件追蹤", ["即時鏡頭追蹤要較流暢，較宜選 KCF 而非 CSRT，因為？"]),
        ("mcq-14", "Cloud API", ["Google 翻譯 API 顯示找不到憑證，較可能是？"]),
        ("mcq-15", "程式結構", ["要刪除專案內舊的 sound.mp3，較應使用？"]),
        ("mcq-16", "程式結構", ["測驗程式把題目放在 quiz_data.json，主要是為了？"]),
        ("mcq-17", "程式結構", ["製作有按鈕、選項的測驗視窗介面，較應使用？"]),
        ("mcq-18", "物件追蹤", ["追蹤準確度要求高、速度可慢，較應選哪種 tracker？"]),
        ("mcq-19", "生成式AI", ["把 AI 生成內容直接交功課且完全不註明，最違反？"]),
        ("mcq-20", "OpenCV", ["課堂鏡頭畫面全黑，較應先檢查？"]),
    ]
    if len(mcq_answers) != len(rows):
        raise RuntimeError("MCQ answer count must match item count")
    items: list[dict] = []
    for (item_id, concept, text_parts), letter in zip(rows, mcq_answers, strict=True):
        items.append(
            make_item(
                item_id,
                "mcq",
                "\n".join(text_parts),
                marks=1,
                concepts=[concept],
                answer=letter,
            )
        )
    return items


def _concepts_for_tf(stmt: str) -> list[str]:
    if "Vibe Coding" in stmt:
        return ["Vibe Coding"]
    if "pip" in stmt:
        return ["套件與pip"]
    if "password.json" in stmt:
        return ["Cloud API"]
    return ["語音程式"]


def _concepts_for_fill(answer: str) -> list[str]:
    if answer == "password.json":
        return ["Cloud API"]
    if answer in {"gTTS", "playsound", "SpeechRecognition", "yue"}:
        return ["語音程式"]
    if answer == "opencv-python":
        return ["OpenCV", "套件與pip"]
    if answer in {"xml", "cvtColor"}:
        return ["OpenCV"]
    if answer == "quiz_data.json":
        return ["程式結構"]
    if answer == "高級程式員":
        return ["Vibe Coding"]
    return ["OpenCV"]


def _section_items(
    *,
    tf_lines: list[str],
    tf_answers: str,
    fill_answers: list[list[str]],
) -> list[dict]:
    fmt_dir = Path(__file__).resolve().parent
    if str(fmt_dir) not in sys.path:
        sys.path.insert(0, str(fmt_dir))
    from tf_fill_layout import FILL_BLOCK_A, FILL_BLOCK_B

    if len(tf_lines) != len(tf_answers):
        raise RuntimeError("T/F statement count must match answer key length")

    fill_a_by_answer = {a: q for q, a in FILL_BLOCK_A}
    fill_b_by_answer = {a: q for q, a in FILL_BLOCK_B}
    fill_a = [fill_a_by_answer[w] for w in fill_answers[0] if w in fill_a_by_answer]
    fill_b = [fill_b_by_answer[w] for w in fill_answers[1] if w in fill_b_by_answer]

    items: list[dict] = [
        make_item("b-match-lib", "section_b", "乙部：函數庫配對", marks=5, concepts=["語音程式"]),
        make_item("b-match-step", "section_b", "乙部：步驟配對", marks=5, concepts=["物件追蹤"]),
    ]
    for i, stmt in enumerate(tf_lines, start=1):
        items.append(
            make_item(
                f"c-tf-{i:02d}",
                "section_c",
                stmt,
                marks=1,
                concepts=_concepts_for_tf(stmt),
                answer=tf_answers[i - 1],
            )
        )
    for i, (prompt, ans) in enumerate(zip(fill_a, fill_answers[0], strict=True), start=1):
        items.append(
            make_item(
                f"d-fill-a-{i:02d}",
                "section_d",
                prompt,
                marks=1,
                concepts=_concepts_for_fill(ans),
                answer=ans,
            )
        )
    for i, (prompt, ans) in enumerate(zip(fill_b, fill_answers[1], strict=True), start=1):
        items.append(
            make_item(
                f"d-fill-b-{i:02d}",
                "section_d",
                prompt,
                marks=1,
                concepts=_concepts_for_fill(ans),
                answer=ans,
            )
        )
    items.append(
        make_item(
            "e-sa-01",
            "section_e",
            "根據筆記，Vibe Coding 為什麼需要「迭代（Iteration）」？請舉一個例子說明。",
            marks=5,
            concepts=["Vibe Coding"],
        )
    )
    return items


def build_s3_cmp_term2_exam_spec(
    *,
    mcq_answers: str,
    matching_answers: list[str],
    tf_lines: list[str],
    tf_answers: str,
    fill_answers: list[list[str]],
    fill_word_banks: list[list[str]],
) -> dict:
    return build_spec(
        {
            "title": "25-26 S3 CMP Term 2 Written Exam",
            "subject": "S3 CMP",
            "level": "中三級",
            "total_marks": 50,
            "academic_year": "2025-2026",
            "mcq_answers": mcq_answers,
            "matching_answers": matching_answers,
            "tf_answers": tf_answers,
            "fill_answers": fill_answers,
            "fill_word_banks": fill_word_banks,
            "footer": {
                "academic_year": "2025-2026",
                "level": "中三級",
                "term_exam": "下學期考試",
                "subject": "電腦認知",
            },
            "concept_targets": CONCEPT_TARGETS,
        },
        _mcq_items(mcq_answers)
        + _section_items(tf_lines=tf_lines, tf_answers=tf_answers, fill_answers=fill_answers),
    )
