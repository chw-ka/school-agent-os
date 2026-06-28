"""One-off: import female PED term-2 grades from NY Excel."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

EXCEL = Path(
    r"t:\25-26\ITAdmin_13_StudentReport\Datafile\25_26_Term2\Datafile\體育分_2526_NY_女.xlsx"
)
OUT_DIR = Path(
    r"T:\25-26\ITAdmin_13_StudentReport\Datafile\25_26_Term2\Datafile"
)


def load_rows() -> pd.DataFrame:
    df = pd.read_excel(EXCEL, sheet_name=0, header=0)
    df = df.rename(
        columns={
            df.columns[0]: "idStudent",
            df.columns[1]: "class",
            df.columns[2]: "numberClass",
            df.columns[3]: "nameChinese",
            df.columns[4]: "gender",
            df.columns[23]: "TOTAL_MARK",
            df.columns[24]: "GRADE",
        }
    )
    df["idStudent"] = df["idStudent"].astype(int)
    df["numberClass"] = df["numberClass"].astype(int)
    df["class"] = df["class"].astype(str).str.strip()
    df["GRADE"] = df["GRADE"].astype(str).str.strip().str.upper()
    df["form"] = df["class"].str[0]
    return df


def awards_by_form(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.sort_values(["form", "TOTAL_MARK", "idStudent"], ascending=[True, False, True])
        .groupby("form", as_index=False)
        .first()
    )


def sql_updates(df: pd.DataFrame) -> str:
    lines = [
        "-- Female PED term 2 grades from 體育分_2526_NY_女.xlsx",
        "-- Column X TOTAL_MARK (reference only); Column Y GRADE -> grade_exam_2",
        "BEGIN TRANSACTION;",
        "",
    ]
    for _, r in df.iterrows():
        grade = r["GRADE"].replace("'", "''")
        lines.append(
            f"UPDATE dbo.tblStudentPaperScore SET grade_exam_2 = N'{grade}' "
            f"WHERE idStudent = {int(r['idStudent'])} AND idPaper = N'PED';"
        )
    lines.extend(["", "COMMIT TRANSACTION;", ""])
    return "\n".join(lines)


def main() -> None:
    df = load_rows()
    awards = awards_by_form(df)

    print(f"Rows in Excel: {len(df)}")
    print(f"Forms: {sorted(df['form'].unique())}")
    print(f"GRADE counts:\n{df['GRADE'].value_counts().to_string()}\n")

    print("=== Top female PED per form (TOTAL_MARK) ===")
    for _, r in awards.iterrows():
        print(
            f"Form {r['form']}: {r['class']} {r['numberClass']:02d} "
            f"id={r['idStudent']} mark={r['TOTAL_MARK']} grade={r['GRADE']} "
            f"name={r['nameChinese']}"
        )

    sql_path = OUT_DIR / "ped_female_grade_exam_2_update_2526.sql"
    csv_path = OUT_DIR / "ped_female_grade_exam_2_2526.csv"
    awards_path = OUT_DIR / "ped_female_awards_by_form_2526.csv"

    sql_path.write_text(sql_updates(df), encoding="utf-8")
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    awards.to_csv(awards_path, index=False, encoding="utf-8-sig")

    print(f"\nWrote {sql_path}")
    print(f"Wrote {csv_path}")
    print(f"Wrote {awards_path}")

    # JSON for MCP batch if needed
    payload = [
        {"idStudent": int(r.idStudent), "grade": r.GRADE, "total": float(r.TOTAL_MARK)}
        for r in df.itertuples()
    ]
    json_path = OUT_DIR / "ped_female_grade_exam_2_2526.json"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {json_path}")


if __name__ == "__main__":
    main()
