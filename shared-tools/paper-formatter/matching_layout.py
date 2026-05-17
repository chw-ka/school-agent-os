"""Shuffle matching rows (prompt + correct letter) to avoid ABCDE rubric patterns."""
from __future__ import annotations

import random
import sys
from pathlib import Path
from typing import Optional

_QC = Path(__file__).resolve().parents[1] / "question-quality-check"
if str(_QC) not in sys.path:
    sys.path.insert(0, str(_QC))

from answer_pattern_check import check_matching_sequence

# (左欄描述, 正確字母 A–E)
MATCH_BLOCK_1: list[tuple[str, str]] = [
    ("gTTS", "B"),
    ("playsound", "A"),
    ("SpeechRecognition", "C"),
    ("detectMultiScale()", "D"),
    ("os.remove()", "E"),
]

MATCH_BLOCK_2: list[tuple[str, str]] = [
    ("開始 STT 前，先進行環境降噪。", "A"),
    ("把 TTS 語音儲存為 mp3 檔。", "B"),
    ("把錄到的語音轉成文字。", "C"),
    ("把彩色影像轉為灰階以提高效率。", "D"),
    ("物件追蹤前，手動圈選要追蹤的目標。", "E"),
]


def _build_one_block(
    items: list[tuple[str, str]],
    header: tuple[str, str],
    rng: random.Random,
    *,
    max_attempts: int = 5000,
) -> tuple[list[tuple[str, str]], str]:
    """Table rows for docx table + 5-letter rubric key (a)–(e)."""
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
    """
    Returns (table1_rows, table2_rows, matching_answers).
    matching_answers: two strings of 5 letters for rubric blocks 1 and 2.
    """
    rng = rng or random.Random()
    rows1, key1 = _build_one_block(
        MATCH_BLOCK_1,
        ("函數庫", "功能（請填寫字母）"),
        rng,
    )
    rows2, key2 = _build_one_block(
        MATCH_BLOCK_2,
        ("描述", "步驟（請填寫字母）"),
        rng,
    )
    return rows1, rows2, [key1, key2]
