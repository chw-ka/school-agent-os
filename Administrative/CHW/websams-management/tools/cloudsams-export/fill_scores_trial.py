#!/usr/bin/env python3
"""Fill one CloudSAMS ASR score export .xls from legacy tblStudentPaperScore (trial)."""

from __future__ import annotations

import argparse
import re
import zipfile
from pathlib import Path

import pyodbc
import xlrd
from xlutils.copy import copy

CONN = (
    "DRIVER={ODBC Driver 13 for SQL Server};"
    "SERVER=10.103.16.21;DATABASE=db25_26;UID=sa;PWD=sql2admin"
)

# Trailing paper id in column header -> (legacy idPaper, score|grade)
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
    parts = header.split("_")
    if len(parts) < 5:
        return None
    paper_id = parts[-1]
    if paper_id in PAPER_MAP:
        return PAPER_MAP[paper_id]
    return None


def _batch_zip_name(template: Path) -> str:
    # DE_52457320260707_124_3_3_S1_1A.xls -> DE_52457320260707_124.zip
    stem = template.stem
    bits = stem.split("_")
    if len(bits) >= 3 and bits[0] == "DE":
        return f"{bits[0]}_{bits[1]}_{bits[2]}.zip"
    raise ValueError(f"Cannot derive batch zip name from {template.name}")


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


SPECIAL_MARKS = frozenset({"N.T.", "+", "-", "EX"})


def _cell_value(rec: tuple | None, field: str) -> str:
    if not rec:
        return ""
    sc, gr, ign, absn = rec
    if absn:
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


def fill_template(template: Path, class_name: str, output: Path) -> int:
    legacy = _fetch(class_name)
    rb = xlrd.open_workbook(str(template), formatting_info=True)
    wb = copy(rb)
    ws = wb.get_sheet(0)
    hdr = [str(c.value).strip() if c.value else "" for c in rb.sheet_by_index(0).row(0)]
    cols: list[tuple[int, str, str]] = []
    for i, h in enumerate(hdr):
        parsed = _parse_col(h)
        if parsed:
            cols.append((i, parsed[0], parsed[1]))

    written = 0
    sheet = rb.sheet_by_index(0)
    for r in range(1, sheet.nrows):
        try:
            num = int(float(sheet.cell_value(r, 6)))
        except (TypeError, ValueError):
            continue
        row_data = legacy.get(num, {})
        for col_i, paper, field in cols:
            existing = sheet.cell_value(r, col_i)
            new_val = _cell_value(row_data.get(paper), field)
            existing_s = str(existing).strip() if existing not in (None, "") else ""
            val = new_val.strip() if new_val.strip() else (
                existing_s if existing_s in SPECIAL_MARKS else ""
            )
            if existing_s != val:
                ws.write(r, col_i, val)
            if val:
                written += 1

    output.parent.mkdir(parents=True, exist_ok=True)
    wb.save(str(output))
    return written


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--template", type=Path, required=True)
    p.add_argument("--class", dest="class_name", default="1A")
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--zip", type=Path, help="Output zip (default: DE_{school}{date}_{seq}.zip from template name)")
    args = p.parse_args()

    out_xls = args.output_dir / args.template.name
    n = fill_template(args.template, args.class_name, out_xls)
    zip_path = args.zip or (args.output_dir.parent / "import-zips" / _batch_zip_name(args.template))
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(out_xls, out_xls.name)
    print(f"Wrote {out_xls} ({n} cells) -> {zip_path}")


if __name__ == "__main__":
    main()
