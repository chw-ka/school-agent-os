#!/usr/bin/env python3
"""Fill score export via Excel COM (preserves CloudSAMS .xls structure)."""

from __future__ import annotations

import argparse
import shutil
import zipfile
from pathlib import Path

import pyodbc
import xlrd

CONN = (
    "DRIVER={ODBC Driver 13 for SQL Server};"
    "SERVER=10.103.16.21;DATABASE=db25_26;UID=sa;PWD=sql2admin"
)

PAPER_MAP: dict[str, tuple[str, str]] = {
    "01233210075": ("CHT", "score"),
    "01233210080": ("CHI", "score"),
    "01233210093": ("CES", "score"),
    "01233210110": ("STM", "score"),
    "01233210165": ("ENG", "score"),
    "01233210185": ("PED", "grade"),
    "01233210210": ("GEO", "score"),
    "01233210260": ("SCI", "score"),
    "01233210280": ("MTH", "score"),
    "01233210350": ("PTH", "score"),
}


def _parse_col(header: str) -> tuple[str, str] | None:
    if not header or header.startswith("*") or header.startswith("DE_"):
        return None
    paper_id = header.split("_")[-1]
    return PAPER_MAP.get(paper_id)


def _fetch(class_name: str) -> dict[int, dict[str, tuple]]:
    sql = """
    SELECT s.numberClass, sps.idPaper,
           sps.score_exam_1, sps.grade_exam_1,
           sps.flgIgnore_1, sps.flgAbsent_1
    FROM dbo.tblStudent s
    JOIN dbo.tblStudentPaperScore sps ON sps.idStudent = s.idStudent
    WHERE s.class = ?
    """
    out: dict[int, dict[str, tuple]] = {}
    with pyodbc.connect(CONN) as conn:
        cur = conn.cursor()
        cur.execute(sql, class_name)
        for num, paper, sc, gr, ign, absn in cur.fetchall():
            out.setdefault(int(num), {})[paper] = (sc, gr, ign, absn)
    return out


# Template / UI symbols (ASR manual §2.1.12): N.T.=免修, + =缺席零分, - =缺席不計分.
# "AB" is NOT valid in 積分與等級 import — day-level absence uses Others (NON_ATTENDANCE.xls).
SPECIAL_MARKS = frozenset({"N.T.", "+", "-", "EX"})


def _cell_value(rec: tuple | None, field: str) -> str:
    if not rec:
        return ""
    sc, gr, ign, absn = rec
    if absn:
        # Per-subject exam absent: score grid uses "+" (counts as 0), not "AB".
        return "+" if field == "score" else ""
    if ign:
        return "N.T."
    if field == "score":
        if sc is None:
            return ""
        return str(int(sc)) if float(sc) == int(sc) else str(sc)
    if gr is None:
        return ""
    return str(gr).strip()


def _resolve_write(template_val: object, new_val: str) -> str:
    existing = str(template_val).strip() if template_val not in (None, "") else ""
    new_val = new_val.strip()
    if new_val:
        return new_val
    if existing in SPECIAL_MARKS:
        return existing
    return ""


def _batch_zip_name(template: Path) -> str:
    bits = template.stem.split("_")
    return f"{bits[0]}_{bits[1]}_{bits[2]}.zip"


def fill_with_excel(template: Path, class_name: str, output: Path) -> int:
    import win32com.client  # type: ignore

    legacy = _fetch(class_name)
    rb = xlrd.open_workbook(str(template))
    sheet = rb.sheet_by_index(0)
    hdr = sheet.row_values(0)
    cols: list[tuple[int, str, str]] = []
    for i, h in enumerate(hdr):
        h = str(h).strip() if h else ""
        parsed = _parse_col(h)
        if parsed:
            cols.append((i, parsed[0], parsed[1]))

    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(template, output)
    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False
    written = 0
    try:
        wb = excel.Workbooks.Open(str(output.resolve()))
        ws = wb.Worksheets(1)
        for r in range(1, sheet.nrows):
            try:
                num = int(float(sheet.cell_value(r, 6)))
            except (TypeError, ValueError):
                continue
            row_data = legacy.get(num, {})
            for col_i, paper, field in cols:
                existing = sheet.cell_value(r, col_i)
                val = _resolve_write(existing, _cell_value(row_data.get(paper), field))
                if str(existing).strip() != val:
                    ws.Cells(r + 1, col_i + 1).Value = val
                if val:
                    written += 1
        wb.Save()
        wb.Close(SaveChanges=True)
    finally:
        excel.Quit()
    return written


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--template", type=Path, required=True)
    p.add_argument("--class", dest="class_name", default="1A")
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--zip", type=Path)
    args = p.parse_args()

    out_xls = args.output_dir / args.template.name
    n = fill_with_excel(args.template, args.class_name, out_xls)
    zip_path = args.zip or (args.output_dir.parent / "import-zips" / _batch_zip_name(args.template))
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(out_xls, out_xls.name)
    print(f"Wrote {out_xls} ({out_xls.stat().st_size} bytes, {n} cells) -> {zip_path}")


if __name__ == "__main__":
    main()
