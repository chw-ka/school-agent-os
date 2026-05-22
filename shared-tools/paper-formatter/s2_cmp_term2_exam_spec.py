"""Exam spec for 25-26 S2 CMP Term 2 written exam."""
from __future__ import annotations

import sys
from pathlib import Path

_SPEC_DIR = Path(__file__).resolve().parents[1] / "question-quality-check"
if str(_SPEC_DIR) not in sys.path:
    sys.path.insert(0, str(_SPEC_DIR))

from exam_spec import build_spec, make_item
from s3_cmp_term2_exam_spec import (
    format_fill_rubric_blocks,
    format_matching_rubric_blocks,
    format_tf_rubric,
)

CONCEPT_TARGETS = {
    "生成式AI": {"min": 8, "max": 20},
    "提示語工程": {"min": 3, "max": 8},
    "Teachable Machine": {"min": 6, "max": 14},
    "學術誠信": {"min": 0, "max": 3},
}


def _mcq_items(mcq_answers: str) -> list[dict]:
    rows: list[tuple[str, str, str]] = [
        ("mcq-01", "生成式AI", "下列哪些是生成式人工智能較常見的「服務／應用」例子？"),
        ("mcq-02", "生成式AI", "根據筆記，下列哪一項最能描述「幻覺（Hallucination）」？"),
        ("mcq-03", "學術誠信", "確認 AI 資訊是否可信時，筆記建議的做法不包括下列哪一項？"),
        ("mcq-04", "生成式AI", "下列哪一項屬於「語意轉換」？"),
        ("mcq-05", "提示語工程", "「限制（Constraint）」最常做的事是？"),
        ("mcq-06", "提示語工程", "下列哪一項屬於「輸出格式（Output）」的要求？"),
        ("mcq-07", "生成式AI", "AI 可以協助閱讀 PDF／Word，下列哪一項不是筆記所列的核心功能？"),
        ("mcq-08", "Teachable Machine", "Teachable Machine 訓練手勢模型，官方網址是哪一個？"),
        ("mcq-09", "Teachable Machine", "下列哪一句最能描述「圖像識別」？"),
        ("mcq-10", "生成式AI", "「文生圖」，下列哪一項正確？"),
        ("mcq-11", "生成式AI", "下列哪一項屬於「圖生圖／影像編輯」方向的應用？"),
        ("mcq-12", "生成式AI", "AI 並不像人類一樣真正理解，其主要運作方式較接近下列哪一項？"),
        ("mcq-13", "生成式AI", "筆記提及可用哪些做法來核對 AI 的回答？"),
        ("mcq-14", "Teachable Machine", "Teachable Machine 訓練流程中，訓練模型之前應完成？"),
        ("mcq-15", "Teachable Machine", "機器學習用於圖像辨識的主要原因是？"),
        ("mcq-16", "生成式AI", "關於生成式 AI「謬誤與真相」，下列敘述哪一項較符合「真相」？"),
        ("mcq-17", "Teachable Machine", "最不符合 Teachable Machine 影像分類訓練的正確做法？"),
        ("mcq-18", "Teachable Machine", "Teachable Machine 建立兩種手勢控制遊戲角色，最合理組合？"),
        ("mcq-19", "Teachable Machine", "訓練後要『充分測試』模型準確性，最主要原因是？"),
        ("mcq-20", "Teachable Machine", "完成訓練後『記下可分享的連結』的主要用途是？"),
    ]
    if len(mcq_answers) != len(rows):
        raise RuntimeError("MCQ answer count must match item count")
    return [
        make_item(iid, "mcq", text, marks=1, concepts=[concept], answer=letter)
        for (iid, concept, text), letter in zip(rows, mcq_answers, strict=True)
    ]


def _concepts_for_tf(stmt: str) -> list[str]:
    if "App Inventor" in stmt or "積木" in stmt:
        return ["Teachable Machine"]
    if "學術誠信" in stmt or "交功課" in stmt or "註明" in stmt:
        return ["學術誠信"]
    if "R-I-C-C-O" in stmt or "Instruction" in stmt:
        return ["提示語工程"]
    return ["生成式AI"]


def _concepts_for_fill(answer: str) -> list[str]:
    if answer in {"積木", "TMIC"}:
        return ["Teachable Machine"]
    if answer in {"指令", "角色", "背景"}:
        return ["提示語工程"]
    if answer in {"私隱"}:
        return ["學術誠信"]
    return ["生成式AI"]


def _section_items(
    *,
    tf_lines: list[str],
    tf_answers: str,
    fill_answers: list[list[str]],
    short_answer: str,
) -> list[dict]:
    fmt_dir = Path(__file__).resolve().parent
    if str(fmt_dir) not in sys.path:
        sys.path.insert(0, str(fmt_dir))
    from s2_cmp_tf_fill_layout import FILL_BLOCK_A, FILL_BLOCK_B

    if len(tf_lines) != len(tf_answers):
        raise RuntimeError("T/F statement count must match answer key length")

    fill_a_by_answer = {a: q for q, a in FILL_BLOCK_A}
    fill_b_by_answer = {a: q for q, a in FILL_BLOCK_B}
    fill_a = [fill_a_by_answer[w] for w in fill_answers[0] if w in fill_a_by_answer]
    fill_b = [fill_b_by_answer[w] for w in fill_answers[1] if w in fill_b_by_answer]

    items: list[dict] = [
        make_item("b-match-ricco", "section_b", "乙部：RICCO 配對", marks=5, concepts=["提示語工程"]),
        make_item("b-match-term", "section_b", "乙部：術語配對", marks=5, concepts=["生成式AI"]),
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
            short_answer,
            marks=5,
            concepts=["提示語工程"],
        )
    )
    return items


def build_s2_cmp_term2_exam_spec(
    *,
    mcq_answers: str,
    matching_answers: list[str],
    tf_lines: list[str],
    tf_answers: str,
    fill_answers: list[list[str]],
    fill_word_banks: list[list[str]],
    short_answer: str,
) -> dict:
    return build_spec(
        {
            "title": "25-26 S2 CMP Term 2 Written Exam",
            "subject": "S2 CMP",
            "level": "中二級",
            "total_marks": 50,
            "academic_year": "2025-2026",
            "mcq_answers": mcq_answers,
            "matching_answers": matching_answers,
            "tf_answers": tf_answers,
            "fill_answers": fill_answers,
            "fill_word_banks": fill_word_banks,
            "footer": {
                "academic_year": "2025-2026",
                "level": "中二級",
                "term_exam": "下學期考試",
                "subject": "電腦認知",
            },
            "concept_targets": CONCEPT_TARGETS,
        },
        _mcq_items(mcq_answers)
        + _section_items(
            tf_lines=tf_lines,
            tf_answers=tf_answers,
            fill_answers=fill_answers,
            short_answer=short_answer,
        ),
    )
