#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compare absent Excel/SQL pairs against tblStudentPaperScore via UNION ALL batches."""

from __future__ import annotations

import csv
import json
import re
import subprocess
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
            updates.append({**current, "id": int(um.group(1)), "paper": um.group(2)})
            current = {}
    return updates


def classify(score, flg_absent, flg_ignore, has_row: bool) -> str:
    if not has_row:
        return "NO_ROW"
    fa = 0 if flg_absent is None else int(flg_absent)
    fi = 0 if flg_ignore is None else int(flg_ignore)
    if score is None and fa == 0 and fi == 0:
        return "NULL_SCORE_OK"
    if score == 0 and fa == 1:
        return "ALREADY_OK"
    if score == 0 and fa == 0:
        return "ZERO_NO_FLAG"
    if score is None and fa == 1:
        return "NULL_WITH_FLAG"
    if score is not None and score > 0:
        return "HAS_SCORE"
    return "OTHER"


def build_union_sql(pairs: list[tuple[int, str]]) -> str:
    parts = [f"SELECT {sid} AS idStudent, N'{paper}' AS idPaper" for sid, paper in pairs]
    union = "\nUNION ALL\n".join(parts)
    return f"""
SELECT
  e.idStudent,
  s.class,
  s.numberClass,
  s.nameEng,
  e.idPaper,
  ps.score_exam_2,
  ps.flgAbsent_2,
  ps.flgIgnore_2
FROM (
{union}
) e
LEFT JOIN dbo.tblStudent s ON s.idStudent = e.idStudent
LEFT JOIN dbo.tblStudentPaperScore ps
  ON ps.idStudent = e.idStudent AND ps.idPaper = e.idPaper
"""


def run_mcp_query(sql: str) -> list[dict]:
    payload = json.dumps({"query": sql.strip()})
    # cursor agent mcp call - use subprocess to node? Not available.
    # Fallback: write sql and print for manual; try pyodbc if configured.
    raise NotImplementedError("Use --stdin-sql mode with external MCP output")


def main() -> int:
    updates = parse_sql_updates(DEFAULT_SQL)
    meta = {(u["id"], u["paper"]): u for u in updates}
    pairs = sorted(meta.keys())

    # Emit batched SQL files for MCP (50 pairs each)
    batch_dir = Path(
        r"T:\25-26\ITAdmin_13_StudentReport\Datafile\25_26_Term2\SQL"
        r"\term2_absent_precheck_batches"
    )
    batch_dir.mkdir(parents=True, exist_ok=True)
    batch_size = 50
    for i in range(0, len(pairs), batch_size):
        chunk = pairs[i : i + batch_size]
        sql = build_union_sql(chunk)
        (batch_dir / f"batch_{i // batch_size + 1:02d}.sql").write_text(sql.strip() + "\n", encoding="utf-8")

    print(f"Pairs: {len(pairs)}")
    print(f"Wrote {len(list(batch_dir.glob('batch_*.sql')))} batch SQL files to {batch_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
