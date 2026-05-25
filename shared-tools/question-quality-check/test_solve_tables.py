"""Tests for solve_tables (no API)."""
from __future__ import annotations

from solve_tables import grid_to_markdown, tables_for_slot


def test_b05_has_transaction_table():
    text = "資料表 TRANSACTION，部分記錄見表。\n(a) CREATE TABLE…"
    tables = tables_for_slot("b-05", text)
    assert len(tables) == 1
    assert tables[0]["name"] == "TRANSACTION"
    assert "T001" in grid_to_markdown(tables[0]["name"], tables[0]["grid"])


def test_c05_has_three_tables():
    text = "MEMBER、FACILITY、RESERVE（見表）。"
    tables = tables_for_slot("c-05", text)
    names = {t["name"] for t in tables}
    assert names == {"MEMBER", "FACILITY", "RESERVE"}
