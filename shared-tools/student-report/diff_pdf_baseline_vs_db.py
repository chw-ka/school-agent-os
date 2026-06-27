#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Diff 2026-06-26 teacher verification PDFs vs current db25_26."""

from __future__ import annotations

import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import fitz
import pyodbc

from _mssql_conn import connection_string

CONN = connection_string()

PDF_DIR = Path(
    r"T:\25-26\ITAdmin_13_StudentReport\_Program\Copies\2026_06_26_成績核對_老師"
)
DEFAULT_OUT = Path(
    r"T:\25-26\ITAdmin_13_StudentReport\Datafile\25_26_Term2\2026_06_27_對分變更_vs_0626PDF.csv"
)

CLASS_HDR = re.compile(r"^(\d[A-Z])\s+(\S+)$")
STU_FULL = re.compile(r"^(\d[A-Z])(\d{2})\s+(.+)$")
STU_NUM = re.compile(r"^(\d{2})\s+(.+)$")
CLS_NUM = re.compile(r"^(\d[A-Z])(\d{2})$")
TEACHER_SCORE = re.compile(r"^([A-Z]{2,3}) - (分數|態度)")
TEACHER_SVC = re.compile(r"^([A-Z]{2,3}) （(服務|課外活動)）")
POST_COLS = 4


def norm(val: object) -> str:
    if val is None:
        return ""
    s = str(val).strip()
    if s in ("--", "NULL", "None"):
        return ""
    return s


def fmt_post(id_post: int, post_name: str, comment: str | None) -> str:
    comment = (comment or "").strip()
    if id_post == 101:
        return f"({comment})" if comment else ""
    if comment:
        return f"{post_name}({comment})"
    return post_name


@dataclass
class Row:
    category: str
    teacher: str
    aux_class: str = ""
    subject: str = ""
    class_: str = ""
    number_class: str = ""
    name_chinese: str = ""
    field: str = ""
    pdf_value: str = ""
    db_value: str = ""
    change: str = ""

    def key(self) -> tuple:
        return (
            self.category,
            self.aux_class,
            self.subject,
            self.class_,
            self.number_class,
            self.field,
        )

    def post_key(self) -> tuple:
        return (self.category, self.class_, self.number_class, self.field)


def iter_pdf_pages(path: Path):
    doc = fitz.open(path)
    for page in doc:
        yield [ln.strip() for ln in page.get_text().splitlines() if ln.strip()]
    doc.close()


def parse_score_att_page(lines: list[str], category: str) -> list[Row]:
    if not lines:
        return []
    m = TEACHER_SCORE.match(lines[0])
    if not m or m.group(2) != category:
        return []
    teacher = m.group(1)
    i = 2
    cols: list[tuple[str, str]] = []
    if category == "分數":
        while i < len(lines) and lines[i] != "總分":
            cm = CLASS_HDR.match(lines[i])
            if cm:
                cols.append((cm.group(1), cm.group(2)))
                i += 3
            else:
                i += 1
    else:
        while i < len(lines) and lines[i] != "學號學生姓名":
            cm = CLASS_HDR.match(lines[i])
            if cm:
                cols.append((cm.group(1), cm.group(2)))
                i += 1
            else:
                i += 1
    if not cols:
        return []

    if category == "分數":
        i += len(cols) * 3
        while i < len(lines) and lines[i] != "班號學生姓名":
            i += 1
        if i < len(lines):
            i += len(cols) * 3
        stride = 3
        fields = ("平時分", "考試分")
    else:
        if i < len(lines) and lines[i] == "學號學生姓名":
            i += len(cols) * 4
        stride = 4
        fields = ("上課", "功課")

    out: list[Row] = []
    block = stride * len(cols)
    while i + block <= len(lines):
        first = lines[i]
        if (
            first.startswith("全級")
            or first.startswith("標準差")
            or TEACHER_SCORE.match(first)
            or first.startswith("請各同事")
        ):
            break
        row_items: list[Row] = []
        for c, (aux, subj) in enumerate(cols):
            base = i + c * stride
            if category == "分數":
                sm = STU_FULL.match(lines[base])
                if not sm:
                    continue
                cls, num, name = sm.group(1), sm.group(2), sm.group(3)
                vals = (lines[base + 1], lines[base + 2])
            else:
                sm = STU_NUM.match(lines[base])
                if not sm:
                    continue
                num, name = sm.group(1), sm.group(2)
                cls = aux
                vals = (lines[base + 1], lines[base + 2])
            for fld, val in zip(fields, vals):
                row_items.append(
                    Row(
                        category=category,
                        teacher=teacher,
                        aux_class=aux,
                        subject=subj,
                        class_=cls,
                        number_class=num,
                        name_chinese=name,
                        field=fld,
                        pdf_value=norm(val),
                    )
                )
        if not row_items:
            break
        out.extend(row_items)
        i += block
    return out


def parse_post_page(lines: list[str], category: str) -> list[Row]:
    if not lines:
        return []
    m = TEACHER_SVC.match(lines[0])
    if not m or m.group(2) != category:
        return []
    teacher = m.group(1)
    i = 2
    while i < len(lines) and lines[i] != "班號":
        i += 1
    if i >= len(lines):
        return []
    i += POST_COLS * 3
    out: list[Row] = []
    stride = POST_COLS * 3
    while i + stride <= len(lines):
        if TEACHER_SVC.match(lines[i]) or lines[i].startswith("請各同事"):
            break
        if not CLS_NUM.match(lines[i]):
            break
        for c in range(POST_COLS):
            base = i + c * 3
            cls_num, name, post = lines[base], lines[base + 1], lines[base + 2]
            sm = CLS_NUM.match(cls_num)
            if not sm:
                continue
            cls, num = sm.group(1), sm.group(2)
            out.append(
                Row(
                    category=category,
                    teacher=teacher,
                    class_=cls,
                    number_class=num,
                    name_chinese=name,
                    field=post,
                    pdf_value=norm(post),
                )
            )
        i += stride
    return out


def parse_score_att_pdf(path: Path, category: str) -> list[Row]:
    out: list[Row] = []
    for page in iter_pdf_pages(path):
        out.extend(parse_score_att_page(page, category))
    return out


def parse_post_pdf(path: Path, category: str) -> list[Row]:
    out: list[Row] = []
    for page in iter_pdf_pages(path):
        out.extend(parse_post_page(page, category))
    return out


def fetch_class_teachers() -> dict[str, str]:
    """班主任 initial by class (tblStaffClass.flgHead=1; matches chw-api teacher1)."""
    sql = """
    SELECT sc.class, sc.idStaff
    FROM dbo.tblStaffClass sc
    WHERE sc.flgHead = 1
    """
    out: dict[str, str] = {}
    cn = pyodbc.connect(CONN)
    for r in cn.cursor().execute(sql):
        out[getattr(r, "class").strip()] = r.idStaff.strip()
    cn.close()
    return out


def apply_class_teacher(rows: list[Row], class_teachers: dict[str, str]) -> None:
    for r in rows:
        ct = class_teachers.get(r.class_)
        if ct:
            r.teacher = ct


def fetch_db_scores() -> dict[tuple, tuple[str, str, str]]:
    sql = """
    SELECT ss.idStaff, sp.class AS aux_class, sp.idPaper, s.class, s.numberClass,
           s.nameChinese, sps.score_regular_2, sps.score_exam_2, sps.grade_exam_2,
           sp.flgScore
    FROM dbo.tblStudent s
    INNER JOIN dbo.vwStudentPaper sp ON s.idStudent = sp.idStudent
    INNER JOIN dbo.tblStudentPaperScore sps
        ON s.idStudent = sps.idStudent AND sp.idPaper = sps.idPaper
    INNER JOIN dbo.vwStaffSubject ss
        ON sp.idSubject = ss.idSubject AND sp.class = ss.class AND ss.flgTeach = 1
    WHERE sp.flgTerm2 = 1 AND sp.form BETWEEN 1 AND 6
    """
    rows: dict[tuple, tuple[str, str, str]] = {}
    cn = pyodbc.connect(CONN)
    for r in cn.cursor().execute(sql):
        aux = r.aux_class.strip()
        paper = r.idPaper.strip()
        cls = getattr(r, "class").strip()
        num = f"{int(r.numberClass):02d}"
        teacher = r.idStaff.strip()
        name = (r.nameChinese or "").strip()
        if r.flgScore:
            for fld, val in (("平時分", r.score_regular_2), ("考試分", r.score_exam_2)):
                key = ("分數", aux, paper, cls, num, fld)
                rows[key] = (teacher, name, norm(val))
        else:
            rows[("分數", aux, paper, cls, num, "考試分")] = (
                teacher,
                name,
                norm(r.grade_exam_2),
            )
            rows[("分數", aux, paper, cls, num, "平時分")] = (teacher, name, "")
    cn.close()
    return rows


def fetch_db_attitudes() -> dict[tuple, tuple[str, str, str]]:
    sql = """
    SELECT ss2.idStaff, ss.class AS aux_class, ss.idSubject, s.class, s.numberClass,
           s.nameChinese, sa.lesson_2, sa.assessment_2
    FROM dbo.vwStudent s
    INNER JOIN dbo.vwStudentSubject ss ON s.idStudent = ss.idStudent
    INNER JOIN dbo.tblStaffSubject ss2
        ON ss.idSubject = ss2.idSubject AND ss2.class = s.class
    LEFT JOIN dbo.tblStudentAttitude sa
        ON s.idStudent = sa.idStudent AND sa.idSubject = ss.idSubject
    WHERE ss.flgTerm2 = 1 AND s.form BETWEEN 1 AND 6
    """
    rows: dict[tuple, tuple[str, str, str]] = {}
    cn = pyodbc.connect(CONN)
    for r in cn.cursor().execute(sql):
        aux = r.aux_class.strip()
        subj = r.idSubject.strip()
        cls = getattr(r, "class").strip()
        num = f"{int(r.numberClass):02d}"
        teacher = (r.idStaff or "").strip()
        name = (r.nameChinese or "").strip()
        for fld, val in (("上課", r.lesson_2), ("功課", r.assessment_2)):
            key = ("態度", aux, subj, cls, num, fld)
            rows[key] = (teacher, name, norm(val))
    cn.close()
    return rows


def fetch_db_class_posts(
    category: str, class_teachers: dict[str, str]
) -> tuple[dict[tuple, tuple[str, str, str]], dict[tuple, str]]:
    sql = """
    SELECT s.class, s.numberClass, s.nameChinese, cu.nameChinese AS unitName,
           p.idPost, p.nameChinese AS postName, ecac.nameChinese AS comment
    FROM dbo.tblStudentClassPost scp
    INNER JOIN dbo.tblStudent s ON scp.idStudent = s.idStudent
    INNER JOIN dbo.tblClassUnit cu ON scp.idClassUnit = cu.idClassUnit
    INNER JOIN dbo.tblPost p ON scp.idPost = p.idPost
    LEFT JOIN dbo.tblECAComment ecac ON scp.idComment = ecac.idComment
    WHERE s.flgTerm2 = 1
    """
    rows: dict[tuple, tuple[str, str, str]] = {}
    units: dict[tuple, str] = {}
    cn = pyodbc.connect(CONN)
    for r in cn.cursor().execute(sql):
        cls = getattr(r, "class").strip()
        num = f"{int(r.numberClass):02d}"
        name = (r.nameChinese or "").strip()
        unit = (r.unitName or "").strip()
        post = fmt_post(int(r.idPost), r.postName.strip(), r.comment)
        teacher = class_teachers.get(cls, "")
        key = (category, cls, num, post)
        rows[key] = (teacher, name, post)
        units[key] = unit
    cn.close()
    return rows, units


def fetch_db_unit_posts(category: str) -> dict[tuple, tuple[str, str, str]]:
    sql = """
    SELECT s.class, s.numberClass, s.nameChinese, p.idPost, p.nameChinese AS postName,
           ecac.nameChinese AS comment, su.idStaff
    FROM dbo.tblStudentUnitPost sup
    INNER JOIN dbo.tblStudent s ON sup.idStudent = s.idStudent
    INNER JOIN dbo.tblUnit u ON sup.idUnit = u.idUnit
    INNER JOIN dbo.tblPost p ON sup.idPost = p.idPost
    LEFT JOIN dbo.tblECAComment ecac ON sup.idComment = ecac.idComment
    LEFT JOIN dbo.tblStaffUnit su ON u.idUnit = su.idUnit AND su.flgHead = 1
    WHERE s.flgTerm2 = 1
    """
    rows: dict[tuple, tuple[str, str, str]] = {}
    cn = pyodbc.connect(CONN)
    for r in cn.cursor().execute(sql):
        cls = getattr(r, "class").strip()
        num = f"{int(r.numberClass):02d}"
        name = (r.nameChinese or "").strip()
        post = fmt_post(int(r.idPost), r.postName.strip(), r.comment)
        teacher = (r.idStaff or "").strip()
        key = (category, cls, num, post)
        rows[key] = (teacher, name, post)
    cn.close()
    return rows


def lookup_db(
    key: tuple,
    db_map: dict[tuple, tuple[str, str, str]],
) -> tuple[str, str, str]:
    hit = db_map.get(key)
    if hit:
        return hit
    if len(key) == 6:
        cat, aux, subj, cls, num, fld = key
        for (c, a, s, cl, n, f), val in db_map.items():
            if c == cat and s == subj and cl == cls and n == num and f == fld:
                return val
    return ("", "", "")


def diff_maps(
    pdf_rows: list[Row],
    db_map: dict[tuple, tuple[str, str, str]],
    is_post: bool = False,
    include_db_only: bool = False,
    class_teachers: dict[str, str] | None = None,
    unit_map: dict[tuple, str] | None = None,
) -> list[Row]:
    diffs: list[Row] = []
    pdf_keys: set[tuple] = set()

    for pr in pdf_rows:
        key = pr.post_key() if is_post else pr.key()
        pdf_keys.add(key)
        db_teacher, db_name, db_val = lookup_db(key, db_map)
        if not pr.teacher and db_teacher:
            pr.teacher = db_teacher
        if unit_map and is_post:
            pr.subject = unit_map.get(key, pr.subject)
        if not pr.name_chinese and db_name:
            pr.name_chinese = db_name
        if pr.pdf_value == db_val:
            continue
        pr.db_value = db_val
        if pr.pdf_value and not db_val:
            pr.change = "已刪除/清空"
        elif not pr.pdf_value and db_val:
            pr.change = "新填入"
        else:
            pr.change = "已修改"
        diffs.append(pr)

    if not include_db_only:
        return diffs

    for key, (db_teacher, db_name, db_val) in db_map.items():
        if key in pdf_keys or not db_val:
            continue
        cat, cls, num, post = key
        teacher = class_teachers.get(cls, db_teacher) if class_teachers else db_teacher
        diffs.append(
            Row(
                category=cat,
                teacher=teacher,
                subject=unit_map.get(key, "") if unit_map else "",
                class_=cls,
                number_class=num,
                name_chinese=db_name,
                field=post,
                pdf_value="",
                db_value=db_val,
                change="新增",
            )
        )
    return diffs


def main() -> None:
    out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT
    out_path.parent.mkdir(parents=True, exist_ok=True)

    class_teachers = fetch_class_teachers()

    pdf_scores = parse_score_att_pdf(PDF_DIR / "3_Check Scores.pdf", "分數")
    pdf_att = parse_score_att_pdf(PDF_DIR / "3_Check Attitudes.pdf", "態度")
    pdf_svc = parse_post_pdf(PDF_DIR / "2_Services.pdf", "服務")
    apply_class_teacher(pdf_svc, class_teachers)
    pdf_ecac = parse_post_pdf(PDF_DIR / "1_ECAC.pdf", "課外活動")

    db_scores = fetch_db_scores()
    db_att = fetch_db_attitudes()
    db_svc, svc_units = fetch_db_class_posts("服務", class_teachers)
    db_ecac = fetch_db_unit_posts("課外活動")

    diffs: list[Row] = []
    diffs.extend(diff_maps(pdf_scores, db_scores))
    diffs.extend(diff_maps(pdf_att, db_att))
    diffs.extend(
        diff_maps(
            pdf_svc,
            db_svc,
            is_post=True,
            include_db_only=True,
            class_teachers=class_teachers,
            unit_map=svc_units,
        )
    )
    diffs.extend(diff_maps(pdf_ecac, db_ecac, is_post=True, include_db_only=True))

    diffs.sort(
        key=lambda r: (
            r.teacher,
            r.category,
            r.aux_class,
            r.subject,
            r.class_,
            int(r.number_class or 0),
            r.field,
        )
    )

    with out_path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "負責老師",
                "類別",
                "組別",
                "單位/科目卷",
                "班別",
                "學號",
                "姓名",
                "欄位",
                "0626_PDF值",
                "現時DB值",
                "變更",
            ]
        )
        for r in diffs:
            w.writerow(
                [
                    r.teacher,
                    r.category,
                    r.aux_class,
                    r.subject,
                    r.class_,
                    r.number_class,
                    r.name_chinese,
                    r.field,
                    r.pdf_value,
                    r.db_value,
                    r.change,
                ]
            )

    by_cat: dict[str, int] = {}
    by_teacher: dict[str, int] = {}
    for r in diffs:
        by_cat[r.category] = by_cat.get(r.category, 0) + 1
        by_teacher[r.teacher] = by_teacher.get(r.teacher, 0) + 1

    print(f"Parsed PDF: scores={len(pdf_scores)} att={len(pdf_att)} svc={len(pdf_svc)} ecac={len(pdf_ecac)}")
    print(f"Wrote {len(diffs)} diffs -> {out_path}")
    print("By category:", dict(sorted(by_cat.items())))
    print("Top teachers:", sorted(by_teacher.items(), key=lambda x: (-x[1], x[0]))[:15])


if __name__ == "__main__":
    main()
