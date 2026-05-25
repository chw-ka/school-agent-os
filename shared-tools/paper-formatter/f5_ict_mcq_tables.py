"""Insert 甲部 MCQ body tables after stem — table name, then table, before (1)(2)(3) / options."""

from __future__ import annotations

import re
from typing import Any

from docx import Document

from f5_ict_layout import F5_ICT_MCQ_BLOCKS
from f5_ict_written_tables import (
    build_excel_compact_grid,
    insert_named_tables_after_stem,
)

MCQ_TABLE_SLOTS: frozenset[int] = frozenset({6, 13, 15})

_SUB_RE = re.compile(r"^\t+\(1\)\t")
_OPT_RE = re.compile(r"^\t([A-D])\.\t")


def _mcq_item(spec: dict[str, Any], slot: int) -> dict[str, Any] | None:
    want = f"mcq-{slot:02d}"
    for it in spec.get("items") or []:
        if it.get("id") == want:
            return it
    return None


def _anchor_after_stem(doc: Document, slot: int) -> int:
    start, end = F5_ICT_MCQ_BLOCKS[slot - 1]
    last_stem = start
    for i in range(start, end):
        t = doc.paragraphs[i].text
        if not t.strip():
            continue
        if _SUB_RE.match(t) or _OPT_RE.match(t):
            return last_stem
        last_stem = i
    return last_stem


def _build_mcq06_sale_grid() -> list[list[str]]:
    """甲6：學會義賣簡表（僅 B–F；與乙1 Order 全欄不同）。"""
    return build_excel_compact_grid(
        [("B", "商品"), ("C", "單價"), ("D", "數量"), ("F", "總價")],
        [
            ["明信片", "15", "8", "120"],
            ["布袋", "45", "3", "135"],
            ["徽章", "20", "6", "120"],
        ],
    )


def _build_mcq13_donate_grid() -> list[list[str]]:
    return build_excel_compact_grid(
        [("A", "班別"), ("C", "已捐金額")],
        [
            ["5A", "1200"],
            ["5B", "800"],
            ["5C", "950"],
        ],
    )


def _build_mcq13_target_grid() -> list[list[str]]:
    return build_excel_compact_grid(
        [("H", "班別"), ("I", "目標金額")],
        [
            ["5A", "1500"],
            ["5B", "1000"],
            ["5C", "1200"],
        ],
    )


def _build_mcq15_member_grid() -> list[list[str]]:
    return [
        ["MID", "Name"],
        ["M10001", "陳大文"],
        ["M10002", "李美玲"],
        ["M10003", "王志強"],
    ]


def _build_mcq15_loan_grid() -> list[list[str]]:
    return [
        ["MID", "BookID"],
        ["M10001", "B12001"],
        ["M10001", "B12035"],
        ["M10002", "B12008"],
    ]


def table_grids_for_mcq_slot(slot: int, item: dict[str, Any]) -> list[tuple[str, list[list[str]]]]:
    if slot == 6:
        return [("Sale", _build_mcq06_sale_grid())]
    if slot == 13:
        return [
            ("Donate", _build_mcq13_donate_grid()),
            ("Target", _build_mcq13_target_grid()),
        ]
    if slot == 15:
        return [
            ("MEMBER", _build_mcq15_member_grid()),
            ("LOAN", _build_mcq15_loan_grid()),
        ]
    return []


def apply_mcq_tables_from_spec(doc: Document, spec: dict[str, Any]) -> int:
    count = 0
    for slot in sorted(MCQ_TABLE_SLOTS, reverse=True):
        item = _mcq_item(spec, slot)
        if not item:
            continue
        blocks = table_grids_for_mcq_slot(slot, item)
        if not blocks:
            continue
        anchor = _anchor_after_stem(doc, slot)
        count += insert_named_tables_after_stem(
            doc, anchor, blocks, slot_id=f"mcq-{slot:02d}", written=False
        )
    return count
