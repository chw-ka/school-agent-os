"""MCQ code block layout: split statements, tabs, gaps."""
from __future__ import annotations

import sys
from pathlib import Path

_FMT = Path(__file__).resolve().parent
if str(_FMT) not in sys.path:
    sys.path.insert(0, str(_FMT))

from mcq_code_layout import (
    format_mcq_stem_with_code,
    insert_code_block_gaps,
    is_code_layout_line,
    split_mixed_intro_line,
    split_semicolon_statements,
)


def test_split_inline_pseudocode():
    intro, code, tail = split_mixed_intro_line(
        "考慮以下偽代碼：x ← 2；y ← x + 3；x ← x + 1；輸出 y"
    )
    assert intro == "考慮以下偽代碼："
    assert code == ["x ← 2", "y ← x + 3", "x ← x + 1", "輸出 y"]
    assert tail is None


def test_split_trailing_question():
    intro, code, tail = split_mixed_intro_line(
        "考慮以下偽代碼：若 (score ≥ 60) 且 (score ≤ 100) 則 grade ←「合格」，"
        "否則 grade ←「不合格」。若 score = 60，grade 是？"
    )
    assert intro == "考慮以下偽代碼："
    assert len(code) == 1
    assert "grade ←「合格」" in code[0]
    assert tail == "若 score = 60，grade 是？"


def test_mcq_code_single_tab():
    stem = format_mcq_stem_with_code("count ← 0\n當 count < 3：輸出 count；count ← count + 1")
    lines = stem.splitlines()
    assert lines[0].startswith("\t") and not lines[0].startswith("\t\t")
    assert lines[1].startswith("\t")


def test_code_gaps_before_code_only():
    body = ["考慮以下偽代碼：", "\tx ← 2", "輸出是？"]
    out = insert_code_block_gaps(body, max_lines=6)
    assert out[1] == ""
    assert is_code_layout_line(out[2])


if __name__ == "__main__":
    test_split_inline_pseudocode()
    test_split_trailing_question()
    test_mcq_code_single_tab()
    test_code_gaps_before_code_only()
    print("ok")
