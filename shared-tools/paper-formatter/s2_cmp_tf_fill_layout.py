"""S2 CMP Term 2 T/F and fill-in items (avoid repeating 甲部 MCQ topics)."""
from __future__ import annotations

import random
import sys
from pathlib import Path
from typing import Optional

_QC = Path(__file__).resolve().parents[1] / "question-quality-check"
if str(_QC) not in sys.path:
    sys.path.insert(0, str(_QC))

from answer_pattern_check import check_tf_sequence

# Topics chosen to complement (not restate) 甲部 MCQ: no 幻覺/交叉查證/統計規律/TM 訓練流程
TF_ITEMS: list[tuple[str, str]] = [
    (
        "「語意轉換」是指把文章改寫成不同語氣或風格，而非單純縮短字數。",
        "T",
    ),
    (
        "「文生圖」只能修改現有相片，不能憑空生成全新影像。",
        "F",
    ),
    (
        "「圖生圖」通常需要上載現有相片，再依指示修改或二次創作。",
        "T",
    ),
    (
        "把 AI 生成內容直接交功課而完全不註明，仍符合學術誠信。",
        "F",
    ),
    (
        "Teachable Machine 必須另外安裝軟件才能使用，不能用瀏覽器開啟。",
        "F",
    ),
]

# Block A: 生成式 AI 四大應用 + RICCO 詞彙（甲部已考 幻覺/查證/統計規律）
FILL_BLOCK_A: list[tuple[str, str]] = [
    (
        "筆記列出文本生成四大應用之一，把長篇文章濃縮成精簡重點，稱為「 ________ 」。",
        "摘要",
    ),
    (
        "依故事情節發想並撰寫開頭，屬於「 ________ 」應用。",
        "創意寫作",
    ),
    (
        "把重點製作成互動練習題，屬於「 ________ 」應用。",
        "問答遊戲",
    ),
    (
        "在 R-I-C-C-O 中，要求 AI 扮演特定身分是設定「 ________ 」(Role)。",
        "角色",
    ),
    (
        "把 PDF 通告內容提供給 AI 作分析依據，是設定「 ________ 」(Context)。",
        "背景",
    ),
]

# Block B: 流動程式 + RICCO + 閱讀輔助（避開 TM 訓練/分享連結/分類標籤）
FILL_BLOCK_B: list[tuple[str, str]] = [
    (
        "App Inventor 以拖拉 ________ 方式組合程式邏輯。",
        "積木",
    ),
    (
        "在 App Inventor 載入 Teachable Machine 模型，需使用 ________ 擴充元件。",
        "TMIC",
    ),
    (
        "在 R-I-C-C-O 中，清楚說明要完成甚麼任務，是「 ________ 」(Instruction)。",
        "指令",
    ),
    (
        "使用 AI 時不應輸入地址或電話，以保障個人 ________ 。",
        "私隱",
    ),
    (
        "把 PDF 重點製成方便溫習的小卡片，稱為「 ________ 」。",
        "閃卡",
    ),
]


def _shuffle_pairs(items: list[tuple[str, str]], rng: random.Random) -> list[tuple[str, str]]:
    out = list(items)
    rng.shuffle(out)
    return out


def build_shuffled_tf(
    rng: Optional[random.Random] = None,
    *,
    max_attempts: int = 5000,
) -> tuple[list[str], str]:
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
    rng = rng or random.Random()
    block_a = _shuffle_pairs(FILL_BLOCK_A, rng)
    block_b = _shuffle_pairs(FILL_BLOCK_B, rng)
    bank_a = [w for _, w in block_a]
    bank_b = [w for _, w in block_b]
    rng.shuffle(bank_a)
    rng.shuffle(bank_b)
    fill_lines = [
        "丁部 – 填充題 (10 分)",
        "請在空格內填入最合適的文字。 (每空格 1 分)",
        *[q for q, _ in block_a],
        "請在空格內填入最合適的文字。 (每空格 1 分)",
        *[q for q, _ in block_b],
    ]
    fill_answers = [[w for _, w in block_a], [w for _, w in block_b]]
    return fill_lines, fill_answers, bank_a, bank_b
