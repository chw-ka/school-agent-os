"""MCQ table grids for slots 06 / 13 / 15."""
from __future__ import annotations

import sys
from pathlib import Path

_FMT = Path(__file__).resolve().parent
if str(_FMT) not in sys.path:
    sys.path.insert(0, str(_FMT))

from f5_ict_mcq_tables import MCQ_TABLE_SLOTS, table_grids_for_mcq_slot
from f5_ict_written_tables import format_table_label


def test_mcq_table_slots_have_grids():
    g06 = table_grids_for_mcq_slot(6, {"text": ""})
    assert g06[0][0] == "Sale"
    grid = g06[0][1]
    assert grid[0] == ["", "B", "C", "D", "F"]
    assert len(grid[0]) == 5

    g13 = table_grids_for_mcq_slot(13, {"text": ""})
    assert [n for n, _ in g13] == ["Device"]
    assert g13[0][1][0] == ["裝置", "用途"]

    g15 = table_grids_for_mcq_slot(15, {"text": ""})
    assert [n for n, _ in g15] == ["MEMBER", "LOAN"]
    assert MCQ_TABLE_SLOTS == frozenset({6, 13, 15})
    assert format_table_label("Sale").startswith("\t\t")
    assert format_table_label("Order", written=True).startswith("\t")


if __name__ == "__main__":
    test_mcq_table_slots_have_grids()
    print("ok")
