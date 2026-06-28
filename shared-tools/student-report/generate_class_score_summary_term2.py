#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build 4_Class Score Summary.xls for term-2 conduct/comment draft (S1-S5).

Workflow (matches prior years):
  1. Copy last term-2 workbook shell (subject columns / layout).
  2. Rename sheets to {class}-{class-teacher}-下學期總分.
  3. Refresh subject-teacher initials (row 2) and student name / score / rank rows.

See: Copies/2025_06_24_S12345_成績表初稿_供評語操行輸入 (24-25 term-2 layout)
"""

from __future__ import annotations

import shutil
import statistics
import sys
from pathlib import Path

import pyodbc
import win32com.client as win32

from _mssql_conn import connection_string

CONN = connection_string()

DEFAULT_TEMPLATE = Path(
    r"T:\24-25\ITAdmin_13_StudentReport\_Program\Copies"
    r"\2025_06_24_S12345_成績表初稿_供評語操行輸入\4_Class Score Summary.xls"
)
DEFAULT_OUTPUT = Path(
    r"T:\25-26\ITAdmin_13_StudentReport\_Program\Copies"
    r"\2026_06_26_S12345_成績表初稿_供評語操行輸入\4_Class Score Summary.xls"
)

# Excel header label -> tblZStudentRank2.idPaper
HEADER_TO_PAPER: dict[str, str] = {
    "ISC": "SCI",
    "SCI": "SCI",
    "CHT": "CHT",
}

# Form-1 homeroom letter -> auxiliary class for ENG/CHI teacher lookup
FORM1_AUX: dict[str, str] = {"A": "1U", "B": "1V", "C": "1X", "D": "1Y"}

DATA_START_ROW = 7
STUDENTS_PER_BLOCK = 5
FOOTER_AVG_ROW = 47
FOOTER_PASS_ROW = 48
FOOTER_MEDIAN_ROW = 49
PASS_THRESHOLD = 50.0


def parse_class_from_sheet(name: str) -> str:
    return name.split("-", 1)[0].strip()


def student_row_index(student_idx: int) -> int:
    """0-based student index -> Excel row (blank line after every 5 students)."""
    block = student_idx // STUDENTS_PER_BLOCK
    offset = student_idx % STUDENTS_PER_BLOCK
    return DATA_START_ROW + block * (STUDENTS_PER_BLOCK + 1) + offset


def score_display(raw: float | None) -> str | int | float:
    if raw is None:
        return ""
    return int(raw // 100)


def connect() -> pyodbc.Connection:
    return pyodbc.connect(CONN)


def fetch_class_teachers(cn: pyodbc.Connection) -> dict[str, str]:
    sql = """
    SELECT sc.class, sc.idStaff
    FROM dbo.tblStaffClass sc
    WHERE sc.flgHead = 1 AND LEFT(sc.class, 1) BETWEEN '1' AND '5'
    """
    return {
        getattr(r, "class").strip(): r.idStaff.strip()
        for r in cn.cursor().execute(sql)
    }


def fetch_subject_teachers(cn: pyodbc.Connection, homeroom: str) -> dict[str, str]:
    """idPaper -> teacher initial for a homeroom class."""
    out: dict[str, str] = {}

    sql_std = """
    SELECT ss.idSubject, MIN(ss.idStaff) AS idStaff
    FROM dbo.vwStaffSubject ss
    WHERE ss.class = ? AND ss.flgTeach = 1
    GROUP BY ss.idSubject
    """
    for r in cn.cursor().execute(sql_std, homeroom):
        out[r.idSubject.strip()] = r.idStaff.strip()

    form = homeroom[0]
    letter = homeroom[1] if len(homeroom) > 1 else ""
    aux = FORM1_AUX.get(letter) if form == "1" else None

    for paper in ("ENG", "CHI"):
        if aux and form == "1":
            row = cn.cursor().execute(
                """
                SELECT TOP 1 ss.idStaff
                FROM dbo.vwStaffSubject ss
                WHERE ss.class = ? AND ss.idSubject = ? AND ss.flgTeach = 1
                """,
                aux,
                paper,
            ).fetchone()
            if row:
                out[paper] = row.idStaff.strip()
                continue

        row = cn.cursor().execute(
            """
            SELECT TOP 1 ss.idStaff
            FROM dbo.tblStudent s
            INNER JOIN dbo.vwStudentPaper sp
                ON s.idStudent = sp.idStudent AND sp.idPaper = ? AND sp.flgTerm2 = 1
            INNER JOIN dbo.vwStaffSubject ss
                ON ss.class = sp.class AND ss.idSubject = sp.idPaper AND ss.flgTeach = 1
            WHERE s.class = ?
            GROUP BY ss.idStaff
            ORDER BY COUNT(*) DESC, ss.idStaff
            """,
            paper,
            homeroom,
        ).fetchone()
        if row:
            out[paper] = row.idStaff.strip()

    return out


def fetch_class_students(cn: pyodbc.Connection, homeroom: str) -> list[dict]:
    students_sql = """
    SELECT s.idStudent, s.numberClass, s.nameChinese
    FROM dbo.tblStudent s
    WHERE s.class = ? AND s.flgTerm2 = 1
    ORDER BY s.numberClass
    """
    students = [
        {
            "idStudent": r.idStudent,
            "num": int(r.numberClass),
            "name": (r.nameChinese or "").strip(),
        }
        for r in cn.cursor().execute(students_sql, homeroom)
    ]

    if not students:
        return []

    ids = ",".join(str(s["idStudent"]) for s in students)
    rank_sql = f"""
    SELECT z.idStudent, z.idPaper, z.score, z.rankClass, z.rankForm
    FROM dbo.tblZStudentRank2 z
    WHERE z.term = 2 AND z.section = 'O' AND z.flgStandard = 0 AND z.flgIgnore = 0
      AND z.idStudent IN ({ids})
    """
    by_student: dict[int, dict[str, dict]] = {s["idStudent"]: {} for s in students}
    form_rank: dict[int, int | None] = {}

    for r in cn.cursor().execute(rank_sql):
        sid = int(r.idStudent)
        paper = (r.idPaper or "").strip()
        by_student[sid][paper] = {
            "score": r.score,
            "rankClass": r.rankClass,
        }
        if paper == "" and r.rankForm is not None:
            form_rank[sid] = int(r.rankForm)

    for s in students:
        sid = s["idStudent"]
        s["papers"] = by_student.get(sid, {})
        s["formRank"] = form_rank.get(sid)

    return students


def read_subject_columns(ws) -> list[tuple[int, str]]:
    cols: list[tuple[int, str]] = []
    used = ws.UsedRange.Columns.Count
    for c in range(1, used + 1, 2):
        header = (ws.Cells(1, c).Text or "").strip()
        if header and header not in ("平均分", "級名次"):
            cols.append((c, header))
    return cols


def clear_student_area(ws, last_row: int = 46) -> None:
    for r in range(DATA_START_ROW, last_row + 1):
        for c in range(1, 31):
            ws.Cells(r, c).Value = None


def write_sheet(ws, cn: pyodbc.Connection, homeroom: str) -> int:
    subject_cols = read_subject_columns(ws)
    teachers = fetch_subject_teachers(cn, homeroom)

    for c, header in subject_cols:
        paper = HEADER_TO_PAPER.get(header, header)
        teacher = teachers.get(paper, "")
        if teacher:
            ws.Cells(2, c).Value = teacher

    clear_student_area(ws)
    students = fetch_class_students(cn, homeroom)

    averages: list[float] = []
    for idx, stu in enumerate(students):
        row = student_row_index(idx)
        ws.Cells(row, 1).Value = stu["num"]
        ws.Cells(row, 2).Value = stu["name"]

        for c, header in subject_cols:
            paper = HEADER_TO_PAPER.get(header, header)
            rec = stu["papers"].get(paper)
            if not rec or rec["score"] is None:
                continue
            ws.Cells(row, c).Value = score_display(rec["score"])
            if rec["rankClass"] is not None:
                ws.Cells(row, c + 1).Value = int(rec["rankClass"])

        avg_rec = stu["papers"].get("")
        if avg_rec and avg_rec["score"] is not None:
            avg_val = float(avg_rec["score"]) / 100.0
            ws.Cells(row, 27).Value = round(avg_val, 1)
            averages.append(avg_val)
        if stu["formRank"] is not None:
            ws.Cells(row, 29).Value = int(stu["formRank"])

    ws.Cells(FOOTER_AVG_ROW, 2).Value = "平均分"
    ws.Cells(FOOTER_PASS_ROW, 2).Value = "合格人數"
    ws.Cells(FOOTER_MEDIAN_ROW, 2).Value = "中位數"

    if averages:
        ws.Cells(FOOTER_AVG_ROW, 27).Value = round(sum(averages) / len(averages), 1)
        ws.Cells(FOOTER_PASS_ROW, 27).Value = sum(1 for a in averages if a >= PASS_THRESHOLD)
        ws.Cells(FOOTER_MEDIAN_ROW, 27).Value = round(statistics.median(averages), 1)

    return len(students)


def generate(template: Path, output: Path) -> None:
    if not template.exists():
        raise FileNotFoundError(f"Template missing: {template}")

    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(template, output)

    cn = connect()
    class_teachers = fetch_class_teachers(cn)

    xl = win32.DispatchEx("Excel.Application")
    xl.Visible = False
    xl.DisplayAlerts = False
    try:
        wb = xl.Workbooks.Open(str(output))
        # Rename sheets and build homeroom -> worksheet map
        for i in range(1, wb.Worksheets.Count + 1):
            ws = wb.Worksheets(i)
            homeroom = parse_class_from_sheet(ws.Name)
            ct = class_teachers.get(homeroom)
            if not ct:
                print(f"WARN: no class teacher for {homeroom}, keep sheet name {ws.Name}")
                continue
            new_name = f"{homeroom}-{ct}-下學期總分"
            if ws.Name != new_name:
                ws.Name = new_name

        for i in range(1, wb.Worksheets.Count + 1):
            ws = wb.Worksheets(i)
            homeroom = parse_class_from_sheet(ws.Name)
            count = write_sheet(ws, cn, homeroom)
            print(f"  {ws.Name}: {count} students")

        wb.Save()
        wb.Close(False)
    finally:
        xl.Quit()
        cn.close()

    print(f"Wrote {output}")


def main() -> int:
    template = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_TEMPLATE
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUTPUT
    generate(template, output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
