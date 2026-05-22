"""Shuffle S2 CMP Term 2 matching rows (乙部)."""
from __future__ import annotations

import random
import sys
from pathlib import Path
from typing import Optional

_QC = Path(__file__).resolve().parents[1] / "question-quality-check"
if str(_QC) not in sys.path:
    sys.path.insert(0, str(_QC))

from answer_pattern_check import check_matching_sequence

# Table 2: (描述, 正確術語字母) — Ch2 四大應用 + App Inventor，避開甲部已考的查證/TM 流程
MATCH_BLOCK_2: list[tuple[str, str]] = [
    ("把長文章濃縮成精簡重點。", "A"),
    ("把口語句子改寫成正式書信語氣。", "B"),
    ("依文字描述生成全新影像。", "C"),
    ("上載相片後依指示修改或二次創作。", "D"),
    ("在 App Inventor 以拖拉方式組合程式邏輯。", "E"),
]

# Table 1 rubric key: R, I, C-背景, C-限制, O → 組件庫字母
RICCO_MATCH_KEY = "BEDCA"


def _build_one_block(
    items: list[tuple[str, str]],
    header: tuple[str, str],
    rng: random.Random,
    *,
    max_attempts: int = 5000,
) -> tuple[list[tuple[str, str]], str]:
    cfg = {"forbid_periods": [2, 3, 4, 5], "forbid_block_rotation": False}
    for _ in range(max_attempts):
        shuffled = list(items)
        rng.shuffle(shuffled)
        key = "".join(letter for _, letter in shuffled)
        if not check_matching_sequence(list(key), alphabet="ABCDE", config=cfg).ok:
            continue
        subs = [f"({c})" for c in "abcde"]
        rows = [header] + [(label, sub) for sub, (label, _) in zip(subs, shuffled)]
        return rows, key
    raise RuntimeError("Could not shuffle matching block without letter pattern")


def build_shuffled_matching(
    rng: Optional[random.Random] = None,
) -> tuple[list[tuple[str, str]], list[tuple[str, str]], list[str]]:
    rng = rng or random.Random()
    rows2, key2 = _build_one_block(
        MATCH_BLOCK_2,
        ("描述", "術語（請填寫字母）"),
        rng,
    )
    rows1 = [
        ("要素", "提示語組件（請填寫字母）"),
        ("R 角色（Role）", "(a)"),
        ("I 指令（Instruction）", "(b)"),
        ("C 背景（Context）", "(c)"),
        ("C 限制（Constraint）", "(d)"),
        ("O 輸出格式（Output）", "(e)"),
    ]
    return rows1, rows2, [RICCO_MATCH_KEY, key2]
