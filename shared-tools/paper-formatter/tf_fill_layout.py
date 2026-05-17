"""Shuffle T/F statements and fill-in blanks (keep each item's correct answer)."""
from __future__ import annotations

import random
import sys
from pathlib import Path
from typing import Optional

_QC = Path(__file__).resolve().parents[1] / "question-quality-check"
if str(_QC) not in sys.path:
    sys.path.insert(0, str(_QC))

from answer_pattern_check import check_tf_sequence, has_pattern_issues

# (statement, T/F) — truth fixed; display order shuffled at generate time
TF_ITEMS: list[tuple[str, str]] = [
    ("外建函數庫跟 Python 一起安裝，完全不需要 pip。", "F"),
    ("課堂建議使用 playsound==1.2.2 以減少播放問題。", "T"),
    ("'password.json' 是用來儲存同學遊戲分數的檔案。", "F"),
    ("STT 程式使用 try…except 可處理聽不清或服務錯誤。", "T"),
    ("Vibe Coding 代表 AI 第一次就一定完美，不需要修改。", "F"),
]

FILL_BLOCK_A: list[tuple[str, str]] = [
    ("文字轉語音常使用 ________ 函數庫把文字變成語音。", "gTTS"),
    ("播放 mp3 常使用 ________ 函數庫。", "playsound"),
    ("語音轉文字使用 ________ 函數庫。", "SpeechRecognition"),
    ("辨識廣東話時，language 參數常用 ________。", "yue"),
    ("Google 翻譯需要 ________ 憑證檔。", "password.json"),
]

FILL_BLOCK_B: list[tuple[str, str]] = [
    ("電腦視覺常用 OpenCV，安裝指令為 pip install ________。", "opencv-python"),
    ("人臉模型 Haar Cascade 的副檔名是 ________。", "xml"),
    ("把彩色影像轉灰階使用 cv2.________()。", "cvtColor"),
    ("Vibe Coding 中，AI 像________，學生像總監。", "高級程式員"),
    ("測驗程式從 ________ 檔讀取題目（分開資料與程式）。", "quiz_data.json"),
]

FILL_BANK_A = [w for _, w in FILL_BLOCK_A]
FILL_BANK_B = [w for _, w in FILL_BLOCK_B]


def _shuffle_pairs(
    items: list[tuple[str, str]],
    rng: random.Random,
) -> list[tuple[str, str]]:
    out = list(items)
    rng.shuffle(out)
    return out


def build_shuffled_tf(
    rng: Optional[random.Random] = None,
    *,
    max_attempts: int = 5000,
) -> tuple[list[str], str]:
    """Return statement lines + answer string without FTFTF-style patterns."""
    rng = rng or random.Random()
    cfg = {"forbid_periods": [2, 3, 4, 5], "max_consecutive": 2}

    for _ in range(max_attempts):
        shuffled = _shuffle_pairs(TF_ITEMS, rng)
        lines = [s for s, _ in shuffled]
        key = "".join(a for _, a in shuffled)
        if check_tf_sequence(list(key), config=cfg).ok:
            return lines, key
    raise RuntimeError("Could not shuffle T/F items to a non-pattern key")


def build_shuffled_fill(
    rng: Optional[random.Random] = None,
) -> tuple[list[str], list[list[str]], list[str], list[str]]:
    """
    Return full 丁部 paragraph lines, fill_answers (2 blocks), shuffled word banks.
    Questions and rubric answers use the same shuffled order per block.
    """
    rng = rng or random.Random()

    block_a = _shuffle_pairs(FILL_BLOCK_A, rng)
    block_b = _shuffle_pairs(FILL_BLOCK_B, rng)

    bank_a = [w for _, w in block_a]
    bank_b = [w for _, w in block_b]
    rng.shuffle(bank_a)
    rng.shuffle(bank_b)

    fill_lines = [
        "丁部 – 填充題 (10 分)",
        "請在空格內填入最合適的文字。（每空格 1 分）",
        *[q for q, _ in block_a],
        "請在空格內填入最合適的文字。（每空格 1 分）",
        *[q for q, _ in block_b],
    ]
    fill_answers = [
        [w for _, w in block_a],
        [w for _, w in block_b],
    ]
    return fill_lines, fill_answers, bank_a, bank_b
