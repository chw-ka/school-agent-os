"""Tests for solvability_check."""
from __future__ import annotations

from solvability_check import check_item_solvability, check_spec_solvability


def test_placeholder_fails():
    issues = check_item_solvability("b-01", "試算表 {CELL} 公式", section="section_b")
    assert any(i.kind == "placeholder" for i in issues)


def test_b01_scenario_mismatch():
    issues = check_item_solvability(
        "b-01",
        "某校購買新電腦，需選擇操作系統。",
        section="section_b",
    )
    assert any(i.kind == "scenario_mismatch" for i in issues)


def test_ok_sheet_item():
    issues = check_item_solvability(
        "b-01",
        "試算表：欄 C=單價，F2 寫 =IF(AND(E2=\"Y\",D2>=5),C2*D2*0.9,C2*D2)\t(3分)",
        section="section_b",
    )
    hard = {i.kind for i in issues}
    assert "scenario_mismatch" not in hard
    assert "placeholder" not in hard


def test_spec_solvability_minimal():
    spec = {
        "meta": {"title": "t"},
        "items": [
            {"id": "b-01", "section": "section_b", "text": "試算表 F2 =IF(E2=\"Y\",1,0)\t(2分)"},
        ],
    }
    r = check_spec_solvability(spec)
    assert r.items_checked == 1
