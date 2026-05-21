"""F5/S5 ICT written-exam table helpers (24_25 template layout)."""

from __future__ import annotations

from typing import Iterable

from docx import Document
from docx.table import Table

from docx_inplace import set_paragraph_text_distribute

# Cover + tables referenced by the 24_25 S5 ICT Exam02 question body.
F5_ICT_BODY_TABLES: frozenset[int] = frozenset(
    {
        0,  # cover
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        11,
        14,
        15,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
        25,
        31,
    }
)

# MCQ-only tables in template; cleared when MCQ stems are text-only.
F5_ICT_MCQ_TABLES: frozenset[int] = frozenset({1, 2})

# Optional diagram / answer scratch tables — cleared when unused.
F5_ICT_OPTIONAL_CLEAR: frozenset[int] = frozenset({10, 12, 13, 16, 26, 27, 28, 29, 30, 32})

# Answer-key appendix tables (duplicates / reference sheets).
F5_ICT_ANSWER_APPENDIX: frozenset[int] = frozenset(range(33, 43))


def clear_table(table: Table) -> None:
    """Blank every cell while preserving table dimensions and styles."""
    for row in table.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                set_paragraph_text_distribute(p, "")


def clear_tables(doc: Document, indices: Iterable[int]) -> None:
    for i in indices:
        if 0 <= i < len(doc.tables):
            clear_table(doc.tables[i])


def set_cell_text(table: Table, r: int, c: int, text: str) -> None:
    cell = table.cell(r, c)
    if cell.paragraphs:
        set_paragraph_text_distribute(cell.paragraphs[0], text)
    else:
        cell.text = text


def clear_unused_f5_ict_tables(doc: Document) -> None:
    """Remove leftover template artefacts (unused MCQ / appendix / optional tables)."""
    to_clear = F5_ICT_MCQ_TABLES | F5_ICT_OPTIONAL_CLEAR | F5_ICT_ANSWER_APPENDIX
    clear_tables(doc, to_clear)


def apply_f5_ict_table_content(doc: Document) -> None:
    """Populate body tables for the 25-26 DB-focused variant."""
    # B1 — spreadsheet sample (table 3)
    t3 = doc.tables[3]
    headers = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
    for c, h in enumerate(headers):
        set_cell_text(t3, 0, c, h)
    rows = [
        ["1", "訂單日期", "產品類別", "單價", "數量", "會員等級", "總價", "VIP 折扣?", "備註"],
        ["2", "2026-03-01", "文具", "25", "12", "VIP", "", "是", ""],
        ["3", "2026-03-02", "電子", "680", "2", "一般", "", "否", ""],
    ]
    for r, row in enumerate(rows, start=1):
        for c, val in enumerate(row):
            set_cell_text(t3, r, c, val)

    # B2 — validation methods (table 4)
    t4 = doc.tables[4]
    set_cell_text(t4, 0, 0, "資料欄")
    set_cell_text(t4, 0, 1, "適當的數據有效性檢驗")
    set_cell_text(t4, 0, 2, "例子")
    samples = [
        ("電話", "只允許 8 位數字", "91234567"),
        ("電郵", "必須包含 @", "user@school.edu.hk"),
        ("數量", "整數 1–99", "15"),
    ]
    for r, (a, b, c) in enumerate(samples, start=1):
        set_cell_text(t4, r, 0, a)
        set_cell_text(t4, r, 1, b)
        set_cell_text(t4, r, 2, c)

    # B3 — email sample (table 5)
    set_cell_text(
        doc.tables[5],
        0,
        0,
        "老師您好：\n請使用以下連結下載評審影片：\n"
        "http://www.school.edu.hk/ict2026/demo.zip\n（檔案大小：250 MB）",
    )

    # B4 — array trace placeholders (tables 6–9)
    for ti in (6, 7, 8, 9):
        tb = doc.tables[ti]
        set_cell_text(tb, 0, 0, "B[1]")
        set_cell_text(tb, 0, 1, "B[2]")
        set_cell_text(tb, 0, 2, "B[3]")
        set_cell_text(tb, 0, 3, "B[4]")

    # B6 — CUSTOMER sample (table 11)
    t11 = doc.tables[11]
    hdr = ["CID", "CNAME", "PHONE", "EMAIL", "LAST_ORDER"]
    for c, h in enumerate(hdr):
        set_cell_text(t11, 0, c, h)
    data = [
        ("C001", "Lee Wai Man", "91234567", "lee@mail.com", "2026-05-12"),
        ("C002", "Chan Mei Ling", "92345678", "chan@mail.com", "2026-04-20"),
        ("C003", "Ng Ka Ho", "93456789", "ng@mail.com", "2026-03-01"),
    ]
    for r, row in enumerate(data, start=1):
        for c, val in enumerate(row):
            set_cell_text(t11, r, c, val)

    # C2 — BOOKSALE insert sample (table 14)
    set_cell_text(
        doc.tables[14],
        0,
        0,
        '銷售編號：S1234567\n書名："Database Design"\n價格：280',
    )

    # C3 — Sales2023 / Sales2024 (table 15)
    t15 = doc.tables[15]
    for c, h in enumerate(["PID", "SID", "AMT"]):
        set_cell_text(t15, 0, c, h)
    rows15 = [
        ("P01", "S01", "120"),
        ("P02", "S02", "80"),
        ("P03", "S03", "0"),
        ("P04", "S04", "55"),
    ]
    for r, row in enumerate(rows15, start=1):
        for c, val in enumerate(row):
            set_cell_text(t15, r, c, val)

    # C4 — denormalised sample (table 17)
    t17 = doc.tables[17]
    set_cell_text(t17, 0, 0, "欄名")
    set_cell_text(t17, 0, 1, "描述")
    schema = [
        ("SID", "學生編號"),
        ("SNAME", "姓名"),
        ("EID", "比賽編號"),
        ("ENAME", "比賽名稱"),
        ("SCORE", "分數"),
    ]
    for r, (a, b) in enumerate(schema, start=1):
        set_cell_text(t17, r, 0, a)
        set_cell_text(t17, r, 1, b)

    # C5 — ROOM / BOOKING (tables 18–19)
    t18 = doc.tables[18]
    for c, h in enumerate(["欄名", "數據類型", "描述", "例子"]):
        set_cell_text(t18, 0, c, h)
    set_cell_text(t18, 1, 0, "RID")
    set_cell_text(t18, 1, 1, "CHAR(4)")
    set_cell_text(t18, 1, 2, "活動室編號")
    set_cell_text(t18, 1, 3, "R101")

    t19 = doc.tables[19]
    for c, h in enumerate(["欄名", "數據類型", "描述", "例子"]):
        set_cell_text(t19, 0, c, h)
    set_cell_text(t19, 1, 0, "BID")
    set_cell_text(t19, 1, 1, "CHAR(6)")
    set_cell_text(t19, 1, 2, "預約編號")
    set_cell_text(t19, 1, 3, "B12001")

    # C6 — query trace grids (tables 20–24)
    for ti in range(20, 25):
        tb = doc.tables[ti]
        set_cell_text(tb, 0, 0, "步驟")
        set_cell_text(tb, 0, 1, "結果列")

    # C7 — DB operation reference (table 25)
    t25 = doc.tables[25]
    set_cell_text(t25, 0, 0, "SQL 子句")
    set_cell_text(t25, 0, 1, "用途")
    ops = [
        ("BEGIN TRANSACTION", "開始交易"),
        ("COMMIT / ROLLBACK", "確認或還原變更"),
    ]
    for r, (a, b) in enumerate(ops, start=1):
        set_cell_text(t25, r, 0, a)
        set_cell_text(t25, r, 1, b)

    # C8 — attendance matrix (table 31)
    t31 = doc.tables[31]
    set_cell_text(t31, 0, 0, "Day\\Student")
    for c in range(1, 4):
        set_cell_text(t31, 0, c, f"S{c}")
    days = [("D1", "P", "A", "P"), ("D2", "A", "A", "P"), ("D3", "P", "P", "A")]
    for r, row in enumerate(days, start=1):
        for c, val in enumerate(row):
            set_cell_text(t31, r, c, val)
