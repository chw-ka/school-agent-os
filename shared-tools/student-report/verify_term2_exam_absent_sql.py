#!/usr/bin/env python3
"""Verify term2 exam absent SQL targets in db25_26."""
from __future__ import annotations

import re
from pathlib import Path

import pyodbc

from _mssql_conn import connection_string

CONN = connection_string()
SQL_PATH = Path(
    r"T:\25-26\ITAdmin_13_StudentReport\Datafile\25_26_Term2\SQL"
    r"\02_Update_tblStudentPaperScore_exam_absent_term2.sql"
)
UPDATE_RE = re.compile(
    r"WHERE idStudent = (\d+) AND idPaper = '([^']+)'", re.I
)


def main() -> None:
    cn = pyodbc.connect(CONN)
    cur = cn.cursor()
    no_row = []
    not_ok = []
    ok = 0
    for line in SQL_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip().startswith("UPDATE "):
            continue
        is_exempt = "flgIgnore_2" in line
        m = UPDATE_RE.search(line)
        sid, paper = int(m.group(1)), m.group(2)
        cur.execute(
            "SELECT score_exam_2, flgAbsent_2, flgIgnore_2 "
            "FROM dbo.tblStudentPaperScore WHERE idStudent=? AND idPaper=?",
            sid,
            paper,
        )
        row = cur.fetchone()
        if row is None:
            no_row.append((sid, paper, "exempt" if is_exempt else "absent"))
            continue
        score, fa, fi = row[0], bool(row[1]), bool(row[2])
        good = score == 0 and ((is_exempt and fi) or (not is_exempt and fa))
        if good:
            ok += 1
        else:
            not_ok.append((sid, paper, row, is_exempt))
    print(f"OK: {ok}")
    print(f"NO_ROW: {len(no_row)}")
    for x in no_row:
        print(f"  {x}")
    print(f"NOT_OK: {len(not_ok)}")
    for x in not_ok[:15]:
        print(f"  {x}")
    cn.close()


if __name__ == "__main__":
    main()
