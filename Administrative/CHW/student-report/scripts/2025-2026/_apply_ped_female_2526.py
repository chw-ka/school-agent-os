"""Apply female PED grade_exam_2 updates to db25_26."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import pyodbc

sys.path.insert(0, str(Path(__file__).resolve().parents[5] / "shared-tools" / "student-report"))
from _mssql_conn import connection_string

CONN = connection_string()
T_DATAFILE = Path(
    r"T:\25-26\ITAdmin_13_StudentReport\Datafile\25_26_Term2\Datafile"
)
JSON_PATH = T_DATAFILE / "ped_female_grade_exam_2_2526.json"


def main() -> None:
    rows = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    cn = pyodbc.connect(CONN)
    cn.autocommit = False
    cur = cn.cursor()

    missing = []
    mismatched_name = []
    updated = 0
    skipped = []

    for r in rows:
        sid = r["idStudent"]
        grade = r["grade"]
        cur.execute(
            """
            SELECT s.idStudent, s.class, s.numberClass, s.nameChinese, s.gender,
                   sps.grade_exam_2, sps.flgIgnore_2, sps.flgAbsent_2
            FROM dbo.tblStudent s
            INNER JOIN dbo.tblStudentPaperScore sps
                ON s.idStudent = sps.idStudent AND sps.idPaper = N'PED'
            WHERE s.idStudent = ?
            """,
            sid,
        )
        db = cur.fetchone()
        if not db:
            missing.append(sid)
            continue
        if db.gender != "F":
            mismatched_name.append((sid, db.nameChinese, db.gender))
            continue
        if db.flgIgnore_2 or db.flgAbsent_2:
            skipped.append((sid, db.nameChinese, "ignore/absent"))
            continue
        if db.grade_exam_2 == grade:
            continue
        cur.execute(
            """
            UPDATE dbo.tblStudentPaperScore
            SET grade_exam_2 = ?
            WHERE idStudent = ? AND idPaper = N'PED'
            """,
            grade,
            sid,
        )
        updated += 1

    cn.commit()
    cn.close()

    print(f"Total Excel rows: {len(rows)}")
    print(f"Updated: {updated}")
    print(f"Missing PED row: {len(missing)} {missing[:10]}")
    print(f"Non-F gender: {len(mismatched_name)}")
    print(f"Skipped ignore/absent: {len(skipped)} {skipped[:5]}")


if __name__ == "__main__":
    main()
