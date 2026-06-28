"""Re-grade female PED: TOTAL_MARK >= 46 and GRADE D -> C."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pyodbc

sys.path.insert(0, str(Path(__file__).resolve().parents[5] / "shared-tools" / "student-report"))
from _mssql_conn import connection_string

T_DATAFILE = Path(
    r"T:\25-26\ITAdmin_13_StudentReport\Datafile\25_26_Term2\Datafile"
)
CSV = T_DATAFILE / "ped_female_grade_exam_2_2526.csv"
CONN = connection_string()


def main() -> None:
    df = pd.read_csv(CSV)
    targets = df[(df["TOTAL_MARK"] >= 46) & (df["GRADE"] == "D")].copy()
    print(f"Re-grade D->C (total>=46): {len(targets)} students")
    print(
        targets[["idStudent", "class", "numberClass", "nameChinese", "TOTAL_MARK", "GRADE"]].to_string(
            index=False
        )
    )

    cn = pyodbc.connect(CONN)
    cur = cn.cursor()
    updated = 0
    for sid in targets["idStudent"].astype(int):
        cur.execute(
            """
            UPDATE dbo.tblStudentPaperScore
            SET grade_exam_2 = N'C'
            WHERE idStudent = ? AND idPaper = N'PED' AND grade_exam_2 = N'D'
            """,
            int(sid),
        )
        updated += cur.rowcount
    cn.commit()

    df.loc[targets.index, "GRADE"] = "C"
    df.to_csv(CSV, index=False, encoding="utf-8-sig")
    print(f"\nDB updated rows: {updated}")
    cn.close()


if __name__ == "__main__":
    main()
