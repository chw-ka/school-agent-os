#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pre-check tblStudentPaperScore vs term-2 exam absent SQL before running UPDATE."""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from generate_term2_discipline_absent_sql import (  # noqa: E402
    DEFAULT_ABSENT_XLSX,
    DEFAULT_DISCIPLINE_XLSX,
    DEFAULT_MAPPING_CSV,
    build_student_map,
    form_from_class,
    load_mapping,
    read_absent_records,
    read_discipline_rows,
    resolve_id_papers,
)

DEFAULT_SQL = Path(
    r"T:\25-26\ITAdmin_13_StudentReport\Datafile\25_26_Term2\SQL"
    r"\02_Update_tblStudentPaperScore_exam_absent_term2.sql"
)
DEFAULT_OUT = Path(
    r"T:\25-26\ITAdmin_13_StudentReport\Datafile\25_26_Term2\SQL"
    r"\term2_absent_precheck_report.csv"
)


def parse_sql_updates(sql_path: Path) -> list[dict]:
    text = sql_path.read_text(encoding="utf-8")
    updates: list[dict] = []
    current: dict = {}
    for line in text.splitlines():
        m = re.match(r"-- (.+?) \| (.+?) -> (\w+) \| (.+)$", line.strip())
        if m:
            current = {
                "comment": m.group(1).strip(),
                "label": m.group(2).strip(),
                "paper": m.group(3).strip(),
                "atype": m.group(4).strip(),
            }
            continue
        um = re.search(r"WHERE idStudent = (\d+) AND idPaper = '(\w+)'", line)
        if um and current:
            updates.append(
                {
                    **current,
                    "id": int(um.group(1)),
                    "paper": um.group(2),
                }
            )
            current = {}
    return updates


def excel_pairs(absent_xlsx: Path, discipline_xlsx: Path, mapping_csv: Path) -> set[tuple[int, str]]:
    discipline_rows = read_discipline_rows(discipline_xlsx)
    student_map = build_student_map(discipline_rows)
    records, _ = read_absent_records(absent_xlsx, student_map)
    rules = load_mapping(mapping_csv)
    pairs: set[tuple[int, str]] = set()
    for rec in records:
        form = form_from_class(rec.class_name)
        if form is None:
            continue
        papers, err = resolve_id_papers(rec.exam_label, form, rules)
        if err or not papers:
            continue
        sid = rec.id_student or student_map.get((rec.class_name, int(float(rec.num))))
        if sid is None:
            continue
        for paper in papers:
            pairs.add((sid, paper))
    return pairs


def build_mcp_check_sql(updates: list[dict]) -> str:
    """Single SELECT joining all expected absent pairs (deduped)."""
    seen: set[tuple[int, str]] = set()
    values: list[str] = []
    for u in updates:
        key = (u["id"], u["paper"])
        if key in seen:
            continue
        seen.add(key)
        values.append(f"({u['id']}, N'{u['paper']}')")
    values_sql = ",\n".join(values)
    return f"""
SELECT
  e.idStudent,
  s.class,
  s.numberClass,
  s.nameEng,
  e.idPaper,
  ps.score_exam_2,
  ps.flgAbsent_2,
  ps.flgIgnore_2,
  CASE
    WHEN ps.idStudent IS NULL THEN 'NO_ROW'
    WHEN ps.score_exam_2 IS NULL AND ISNULL(ps.flgAbsent_2, 0) = 0 AND ISNULL(ps.flgIgnore_2, 0) = 0 THEN 'NULL_SCORE_OK'
    WHEN ps.score_exam_2 = 0 AND ISNULL(ps.flgAbsent_2, 0) = 1 THEN 'ALREADY_OK'
    WHEN ps.score_exam_2 = 0 AND ISNULL(ps.flgAbsent_2, 0) = 0 THEN 'ZERO_NO_FLAG'
    WHEN ps.score_exam_2 IS NULL AND ISNULL(ps.flgAbsent_2, 0) = 1 THEN 'NULL_WITH_FLAG'
    WHEN ps.score_exam_2 > 0 THEN 'HAS_SCORE'
    ELSE 'OTHER'
  END AS check_status
FROM (
  SELECT v.idStudent, v.idPaper
  FROM (VALUES
{values_sql}
  ) AS v(idStudent, idPaper)
) e
LEFT JOIN dbo.tblStudent s ON s.idStudent = e.idStudent
LEFT JOIN dbo.tblStudentPaperScore ps
  ON ps.idStudent = e.idStudent AND ps.idPaper = e.idPaper
ORDER BY check_status DESC, s.class, s.numberClass, e.idPaper
"""


def main() -> int:
    sql_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SQL
    absent_xlsx = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_ABSENT_XLSX
    discipline_xlsx = Path(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_DISCIPLINE_XLSX
    mapping_csv = Path(sys.argv[4]) if len(sys.argv) > 4 else DEFAULT_MAPPING_CSV
    out_sql = (
        Path(sys.argv[5])
        if len(sys.argv) > 5
        else Path(
            r"T:\25-26\ITAdmin_13_StudentReport\Datafile\25_26_Term2\SQL"
            r"\term2_absent_precheck_query.sql"
        )
    )

    updates = parse_sql_updates(sql_path)
    sql_pairs = {(u["id"], u["paper"]) for u in updates}
    xls_pairs = excel_pairs(absent_xlsx, discipline_xlsx, mapping_csv)

    print(f"SQL file: {len(updates)} UPDATE lines, {len(sql_pairs)} unique pairs")
    print(f"Excel source: {len(xls_pairs)} unique pairs")
    print(f"In SQL not Excel: {len(sql_pairs - xls_pairs)}")
    print(f"In Excel not SQL: {len(xls_pairs - sql_pairs)}")

    check_sql = build_mcp_check_sql(updates)
    out_sql.write_text(check_sql.strip() + "\n", encoding="utf-8")
    print(f"Wrote check query: {out_sql}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
