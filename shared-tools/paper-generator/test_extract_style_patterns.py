"""Tests for style pattern extraction (redaction + verb)."""
from extract_style_patterns import (
    extract_command_verb,
    extract_mcq_distractor_patterns,
    extract_scenario_frame,
    redact_for_pattern,
)


def test_redact_placeholders():
    t = '在 F2 輸入公式，2024 年 "S01" 的 SUMIF(A2:A81, "x", F2:F81)'
    r = redact_for_pattern(t)
    assert "{CELL}" in r
    assert "{YEAR}" in r
    assert "{N}" in r or "{STR}" in r


def test_command_verb_mcq():
    v = extract_command_verb("下列哪一項關於 RAM 與 ROM 的敘述是正確的？")
    assert v is not None
    assert "下列" in v


def test_scenario_frame():
    s = extract_scenario_frame("某網店使用數據庫儲存訂單。下列哪項……？")
    assert s is not None
    assert "網店" in s or "{N}" in s


def test_combo_distractor():
    item = {
        "options": {
            "A": "只有 (1)",
            "B": "只有 (2)",
            "C": "只有 (1) 和 (3)",
            "D": "只有 (2) 和 (3)",
        }
    }
    pats = extract_mcq_distractor_patterns(item)
    assert any("只有" in p for p in pats)


if __name__ == "__main__":
    test_redact_placeholders()
    test_command_verb_mcq()
    test_scenario_frame()
    test_combo_distractor()
    print("ok")
