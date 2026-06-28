#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Export discipline UPDATE SQL from Excel K-column formula results."""

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
    r"T:\25-26\ITAdmin_13_StudentReport\Datafile\25_26_Term2\A_Done_SQL_Term2_DisciplineRecord.xls"
)
DEFAULT_OUT = Path(
    r"T:\25-26\ITAdmin_13_StudentReport\Datafile\25_26_Term2\SQL\01_Update_tblStudentDiscipline_term2.sql"
)

DATA_START_ROW = 4
PARSE_PAT = re.compile(
    r"dayabsent_2\s*=\s*([\d.]+).*?"
    r"numlate_2\s*=\s*(\d+).*?"
    r"numdemeritds_2\s*=\s*(\d+).*?"
    r"numdemerithw_2\s*=\s*(\d+).*?"
    r"flghw_2\s*=\s*(\d+).*?"
    r"idstudent\s*=\s*(\d+)",
    re.I | re.S,
)


def parse_update(stmt: str) -> tuple[int, tuple] | None:
    m = PARSE_PAT.search(str(stmt).replace(";", ""))
    if not m:
        return None
    sid = int(m.group(6))
    fields = (
        float(m.group(1)),
        int(m.group(2)),
        int(m.group(3)),
        int(m.group(4)),
        int(m.group(5)),
    )
    return sid, fields


def format_update(fields: tuple, sid: int) -> str:
    day, late, ds, hw, flg = fields
    day_s = str(int(day)) if day == int(day) else str(day)
    return (
        "UPDATE tblStudentDiscipline SET "
        f"dayAbsent_2 = {day_s}, "
        f"numLate_2 = {late}, "
        f"numDemeritDS_2 = {ds}, "
        f"numDemeritHW_2 = {hw}, "
        f"flgHW_2 = {flg} "
        f"WHERE idStudent = {sid};"
    )


def read_excel_updates(xls_path: Path) -> list[tuple[int, tuple]]:
    xl = win32.Dispatch("Excel.Application")
    xl.Visible = False
    xl.DisplayAlerts = False
    updates: list[tuple[int, tuple]] = []
    try:
        wb = xl.Workbooks.Open(str(xls_path.resolve()))
        ws = wb.Sheets("S1-5_DisciplineRecord")
        last_row = ws.UsedRange.Rows.Count
        for r in range(DATA_START_ROW, last_row + 1):
            sql = ws.Cells(r, 11).Value
            if not sql:
                continue
            parsed = parse_update(str(sql))
            if not parsed:
                raise ValueError(f"Row {r}: cannot parse SQL: {sql!r}")
            updates.append(parsed)
        wb.Close(False)
    finally:
        xl.Quit()
    return updates


def write_sql_file(updates: list[tuple[int, tuple]], out_path: Path) -> None:
    lines = [
        "-- Generated: Update tblStudentDiscipline term 2 (遲缺、缺點、功課警告)",
        "-- Source: A_Done_SQL_Term2_DisciplineRecord.xls (K column formulas)",
        f"-- Rows: {len(updates)}",
        f"-- {datetime.now().isoformat(timespec='seconds')}",
        "USE db25_26;",
        "GO",
        "",
    ]
    for sid, fields in updates:
        lines.append(format_update(fields, sid))
    lines.extend(["", f"-- Done: {len(updates)} updates"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def compare_updates(
    excel_updates: list[tuple[int, tuple]],
    file_path: Path,
) -> tuple[bool, str]:
    file_map: dict[int, tuple] = {}
    for line in file_path.read_text(encoding="utf-8").splitlines():
        if line.strip().lower().startswith("update"):
            parsed = parse_update(line)
            if parsed:
                file_map[parsed[0]] = parsed[1]

    excel_map = {sid: fields for sid, fields in excel_updates}
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

    updates = read_excel_updates(xls_path)
    write_sql_file(updates, out_path)
    print(f"Wrote {out_path} ({len(updates)} updates)")

    ok, msg = compare_updates(updates, out_path)
    print(msg)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
