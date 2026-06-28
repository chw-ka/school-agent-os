#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Export tblStudentReward INSERT SQL from Excel I-column formula results."""

from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import win32com.client as win32
except ImportError:
    print("Install: pip install pywin32", file=sys.stderr)
    raise

DEFAULT_XLS = Path(
    r"T:\25-26\ITAdmin_13_StudentReport\Datafile\25_26_Term2\D_Done_SQL_Term2_Merit.xlsx"
)
DEFAULT_OUT = Path(
    r"T:\25-26\ITAdmin_13_StudentReport\Datafile\25_26_Term2\SQL"
    r"\03_Insert_tblStudentReward_term2.sql"
)

DATA_START_ROW = 2
SQL_COL = 9
PARSE_PAT = re.compile(
    r"insert\s+tblstudentreward\s+select\s+"
    r"(\d+)\s*,\s*"
    r"(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*"
    r"(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)",
    re.I,
)


def parse_insert(stmt: str) -> tuple[int, tuple[int, ...]] | None:
    m = PARSE_PAT.search(str(stmt).replace(";", ""))
    if not m:
        return None
    sid = int(m.group(1))
    fields = tuple(int(m.group(i)) for i in range(2, 10))
    return sid, fields


def format_insert(fields: tuple[int, ...], sid: int) -> str:
    return (
        "INSERT tblStudentReward SELECT "
        f"{sid}, {fields[0]}, {fields[1]}, {fields[2]}, {fields[3]}, "
        f"{fields[4]}, {fields[5]}, {fields[6]}, {fields[7]};"
    )


def read_excel_inserts(xls_path: Path) -> list[tuple[int, tuple[int, ...]]]:
    xl = win32.Dispatch("Excel.Application")
    xl.Visible = False
    xl.DisplayAlerts = False
    inserts: list[tuple[int, tuple[int, ...]]] = []
    try:
        wb = xl.Workbooks.Open(str(xls_path.resolve()))
        ws = wb.Sheets(1)
        last_row = ws.UsedRange.Rows.Count
        for r in range(DATA_START_ROW, last_row + 1):
            sql = ws.Cells(r, SQL_COL).Value
            if not sql:
                continue
            parsed = parse_insert(str(sql))
            if not parsed:
                raise ValueError(f"Row {r}: cannot parse SQL: {sql!r}")
            inserts.append(parsed)
        wb.Close(False)
    finally:
        xl.Quit()
    return inserts


def write_sql_file(inserts: list[tuple[int, tuple[int, ...]]], out_path: Path) -> None:
    lines = [
        "-- Generated: Insert tblStudentReward term 2 merits (優點)",
        "-- Source: D_Done_SQL_Term2_Merit.xlsx (I column formulas)",
        f"-- Rows: {len(inserts)}",
        f"-- {datetime.now().isoformat(timespec='seconds')}",
        "USE db25_26;",
        "GO",
        "",
    ]
    for sid, fields in inserts:
        lines.append(format_insert(fields, sid))
    lines.extend(["", f"-- Done: {len(inserts)} inserts"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def compare_inserts(
    excel_inserts: list[tuple[int, tuple[int, ...]]],
    file_path: Path,
) -> tuple[bool, str]:
    file_map: dict[int, tuple[int, ...]] = {}
    for line in file_path.read_text(encoding="utf-8").splitlines():
        if line.strip().lower().startswith("insert"):
            parsed = parse_insert(line)
            if parsed:
                file_map[parsed[0]] = parsed[1]

    excel_map = {sid: fields for sid, fields in excel_inserts}
    only_excel = sorted(set(excel_map) - set(file_map))
    only_file = sorted(set(file_map) - set(excel_map))
    mismatches = [
        (sid, excel_map[sid], file_map[sid])
        for sid in sorted(set(excel_map) & set(file_map))
        if excel_map[sid] != file_map[sid]
    ]

    if only_excel or only_file or mismatches:
        lines = [
            f"Excel rows: {len(excel_map)}, file rows: {len(file_map)}",
            f"Only in Excel: {len(only_excel)}",
            f"Only in file: {len(only_file)}",
            f"Field mismatches: {len(mismatches)}",
        ]
        for sid, ex, fi in mismatches[:10]:
            lines.append(f"  idStudent {sid}: excel={ex} file={fi}")
        return False, "\n".join(lines)
    return True, f"OK: {len(excel_map)} rows match exactly."


def main() -> int:
    xls_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_XLS
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUT

    if not xls_path.exists():
        print(f"Missing Excel: {xls_path}", file=sys.stderr)
        return 1

    inserts = read_excel_inserts(xls_path)
    write_sql_file(inserts, out_path)
    print(f"Wrote {out_path} ({len(inserts)} inserts)")

    ok, msg = compare_inserts(inserts, out_path)
    print(msg)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
