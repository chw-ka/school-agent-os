#!/usr/bin/env python3
"""Execute generated term2 SQL files against db25_26."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pyodbc

from _mssql_conn import connection_string

CONN = connection_string()

DEFAULT_SQL_DIR = Path(
    r"T:\25-26\ITAdmin_13_StudentReport\Datafile\25_26_Term2\SQL"
)

UPDATE_RE = re.compile(
    r"WHERE idStudent = (\d+) AND idPaper = '([^']+)'",
    re.I,
)


def load_updates(path: Path) -> list[str]:
    stmts: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("--"):
            continue
        upper = line.upper()
        if upper.startswith("USE ") or upper == "GO":
            continue
        if upper.startswith("UPDATE "):
            stmts.append(line)
    return stmts


def parse_paper_target(stmt: str) -> tuple[int, str] | None:
    m = UPDATE_RE.search(stmt)
    if not m:
        return None
    return int(m.group(1)), m.group(2)


def main() -> int:
    sql_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SQL_DIR
    files = [
        ("discipline", sql_dir / "01_Update_tblStudentDiscipline_term2.sql"),
        ("exam_absent", sql_dir / "02_Update_tblStudentPaperScore_exam_absent_term2.sql"),
    ]
    for _, path in files:
        if not path.exists():
            print(f"Missing: {path}", file=sys.stderr)
            return 1

    cn = pyodbc.connect(CONN, autocommit=False)
    cur = cn.cursor()

    absent_stmts = load_updates(files[1][1])
    sample = [t for t in (parse_paper_target(s) for s in absent_stmts[:5]) if t]

    print("PRE-CHECK sample exam absent targets:")
    for sid, paper in sample:
        cur.execute(
            "SELECT score_exam_2, flgAbsent_2, flgIgnore_2 "
            "FROM dbo.tblStudentPaperScore WHERE idStudent = ? AND idPaper = ?",
            sid,
            paper,
        )
        print(f"  {sid}/{paper}: before={cur.fetchone()}")

    for label, path in files:
        stmts = load_updates(path)
        print(f"Executing {label}: {len(stmts)} UPDATEs from {path.name}")
        affected = 0
        zero_row: list[str] = []
        for stmt in stmts:
            cur.execute(stmt)
            rc = cur.rowcount
            if rc is not None and rc > 0:
                affected += rc
            elif label == "exam_absent":
                zero_row.append(stmt)
        print(f"  statements with rows affected: {affected}")
        if zero_row:
            print(f"  zero-row updates: {len(zero_row)}")
            for stmt in zero_row[:10]:
                t = parse_paper_target(stmt)
                print(f"    {t}")

    cn.commit()
    print("COMMIT OK")

    print("POST-CHECK sample exam absent targets:")
    for sid, paper in sample:
        cur.execute(
            "SELECT score_exam_2, flgAbsent_2, flgIgnore_2 "
            "FROM dbo.tblStudentPaperScore WHERE idStudent = ? AND idPaper = ?",
            sid,
            paper,
        )
        print(f"  {sid}/{paper}: after={cur.fetchone()}")

    cur.execute(
        "SELECT "
        "SUM(CASE WHEN flgAbsent_2 = 1 AND score_exam_2 = 0 THEN 1 ELSE 0 END), "
        "SUM(CASE WHEN flgIgnore_2 = 1 AND score_exam_2 = 0 THEN 1 ELSE 0 END), "
        "SUM(CASE WHEN flgAbsent_2 = 1 AND score_exam_2 > 0 THEN 1 ELSE 0 END) "
        "FROM dbo.tblStudentPaperScore"
    )
    row = cur.fetchone()
    print(f"DB summary absent_ok={row[0]} exempt_ok={row[1]} absent_with_score={row[2]}")
    cn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
