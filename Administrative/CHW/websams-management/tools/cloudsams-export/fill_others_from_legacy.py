#!/usr/bin/env python3
"""Fill CloudSAMS ASR Others export templates from legacy db25_26."""

from __future__ import annotations

import argparse
import shutil
import zipfile
from pathlib import Path

import xlrd
from xlutils.copy import copy

try:
    import pyodbc
    import pyzipper
except ImportError:
    pyodbc = None  # type: ignore
    pyzipper = None  # type: ignore

DEFAULT_OUT = Path(__file__).resolve().parents[2] / "cloudsams-templates" / "asr" / "_local"
PWD = b"EvanGelisTic1617!"
CONN = (
    "DRIVER={ODBC Driver 13 for SQL Server};"
    "SERVER=10.103.16.21;DATABASE=db25_26;UID=sa;PWD=sql2admin"
)

CONDUCT_COLS = ("操行", "紀律", "禮貌", "責任", "合群")
COMMENT_COLS = ("評語 (中文)", "Comment (Chinese)")
AWARD_COLS = ("大功", "小功", "優點", "大過", "小過", "缺點")
ATT_COLS = ("缺席", "遲到", "早退")


def _idx(hdr: list[str], names: tuple[str, ...]) -> int | None:
    for n in names:
        if n in hdr:
            return hdr.index(n)
    return None


def _strip_grade(v) -> str:
    if v is None or v == "":
        return ""
    return str(v).strip()


def _points_to_merits(n: int) -> tuple[int, int, int]:
    n = int(n or 0)
    large = n // 9
    rem = n % 9
    small = rem // 3
    merit = rem % 3
    return large, small, merit


def _concat_comment(parts: list[str | None]) -> str:
    bits = [p.strip() for p in parts if p and str(p).strip()]
    return "\n".join(bits)


def _fetch_legacy(term: int, classes: list[str] | None) -> dict[tuple[str, int], dict]:
    if pyodbc is None:
        raise SystemExit("pip install pyodbc pyzipper")
    sfx = f"_{term}"
    class_filter = ""
    params: list = []
    if classes:
        placeholders = ",".join("?" for _ in classes)
        class_filter = f" AND s.class IN ({placeholders})"
        params.extend(classes)

    sql = f"""
    SELECT s.class, s.numberClass,
           sc.conduct_1{sfx}, sc.conduct_2{sfx}, sc.conduct_3{sfx}, sc.conduct_4{sfx}, sc.conduct_5{sfx},
           cm.custom_1{sfx}, cm.custom_2{sfx}, cm.custom_3{sfx}, cm.custom_4{sfx},
           c1.comment AS comment1, c2.comment AS comment2, c3.comment AS comment3, c4.comment AS comment4,
           sd.dayAbsent{sfx}, sd.numLate{sfx}, sd.numDemeritDS{sfx}, sd.numDemeritHW{sfx},
           sr.numMerit1{sfx}, sr.numMerit2{sfx}, sr.numMerit3{sfx}, sr.numMerit4{sfx}
    FROM dbo.tblStudent s
    LEFT JOIN dbo.tblStudentConduct sc ON sc.idStudent = s.idStudent
    LEFT JOIN dbo.tblStudentComment cm ON cm.idStudent = s.idStudent
    LEFT JOIN dbo.tblComment c1 ON c1.idComment = cm.comment_1{sfx}
    LEFT JOIN dbo.tblComment c2 ON c2.idComment = cm.comment_2{sfx}
    LEFT JOIN dbo.tblComment c3 ON c3.idComment = cm.comment_3{sfx}
    LEFT JOIN dbo.tblComment c4 ON c4.idComment = cm.comment_4{sfx}
    LEFT JOIN dbo.tblStudentDiscipline sd ON sd.idStudent = s.idStudent
    LEFT JOIN dbo.tblStudentReward sr ON sr.idStudent = s.idStudent
    WHERE 1=1{class_filter}
    ORDER BY s.class, s.numberClass
    """
    rows: dict[tuple[str, int], dict] = {}
    with pyodbc.connect(CONN) as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        cols = [d[0] for d in cur.description]
        for rec in cur.fetchall():
            d = dict(zip(cols, rec))
            key = (str(d["class"]).strip(), int(d["numberClass"]))
            comment_parts = []
            for i in range(1, 5):
                custom = d.get(f"custom_{i}{sfx}")
                if custom and str(custom).strip():
                    comment_parts.append(str(custom).strip())
                else:
                    c = d.get(f"comment{i}")
                    if c and str(c).strip():
                        comment_parts.append(str(c).strip())
            merit_pts = sum(int(d.get(f"numMerit{i}{sfx}") or 0) for i in range(1, 5))
            demerit_pts = int(d.get(f"numDemeritDS{sfx}") or 0) + int(d.get(f"numDemeritHW{sfx}") or 0)
            lg, sm, mr = _points_to_merits(merit_pts)
            dlg, dsm, dmr = _points_to_merits(demerit_pts)
            rows[key] = {
                "conduct": [_strip_grade(d.get(f"conduct_{i}{sfx}")) for i in range(1, 6)],
                "comment": _concat_comment(comment_parts),
                "absent": int(d.get(f"dayAbsent{sfx}") or 0),
                "late": int(d.get(f"numLate{sfx}") or 0),
                "award": (lg, sm, mr, dlg, dsm, dmr),
            }
    return rows


def extract_others_zip(encrypted: Path, work: Path, password: bytes) -> list[Path]:
    if pyzipper is None:
        raise SystemExit("pip install pyzipper")
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    xls_out = work / "xls"
    xls_out.mkdir()
    with pyzipper.AESZipFile(encrypted) as outer:
        outer.extractall(work / "inner", pwd=password)
    files: list[Path] = []
    for inner_zip in sorted((work / "inner").glob("*.zip")):
        with zipfile.ZipFile(inner_zip) as inner:
            inner.extractall(xls_out)
    files = sorted(xls_out.glob("*.xls"))
    if not files:
        raise SystemExit(f"No xls found under {encrypted}")
    return files


def _fill_row(sheet, row_idx: int, hdr: list[str], updates: dict[str, object]) -> int:
    n = 0
    for col_name, val in updates.items():
        if col_name not in hdr:
            continue
        if val is None or val == "":
            continue
        sheet.write(row_idx, hdr.index(col_name), val)
        n += 1
    return n


def fill_xls(path: Path, legacy: dict[tuple[str, int], dict], *, dry_run: bool) -> int:
    rb = xlrd.open_workbook(str(path), formatting_info=True)
    ws = rb.sheet_by_index(0)
    hdr = [str(c) for c in ws.row_values(0)]
    filled = 0
    wb = copy(rb)
    sheet = wb.get_sheet(0)

    conduct_i = [_idx(hdr, (c,)) for c in CONDUCT_COLS]
    comment_i = _idx(hdr, COMMENT_COLS)
    award_i = [_idx(hdr, (c,)) for c in AWARD_COLS]
    att_i = [_idx(hdr, (c,)) for c in ATT_COLS]

    for r in range(1, ws.nrows):
        cls = str(ws.row_values(r)[6]).strip()
        num = int(float(ws.row_values(r)[7]))
        data = legacy.get((cls, num))
        if not data:
            continue
        updates: dict[str, object] = {}
        if "CONDUCT_AND_OVERALL_COMMENT" in path.name.upper():
            for i, col in enumerate(CONDUCT_COLS):
                if conduct_i[i] is not None and i < len(data["conduct"]):
                    updates[col] = data["conduct"][i]
            if comment_i is not None and data["comment"]:
                updates[hdr[comment_i]] = data["comment"]
        elif "AWARD_PUNISHMENT" in path.name.upper():
            for i, col in enumerate(AWARD_COLS):
                if award_i[i] is not None:
                    updates[col] = data["award"][i]
        elif "NON_ATTENDANCE" in path.name.upper():
            if att_i[0] is not None:
                updates[ATT_COLS[0]] = data["absent"]
            if att_i[1] is not None:
                updates[ATT_COLS[1]] = data["late"]
        else:
            continue
        if dry_run:
            print(f"Would fill {path.name} {cls}{num}: {list(updates.keys())}")
        else:
            filled += _fill_row(sheet, r, hdr, updates)

    if not dry_run and filled:
        wb.save(str(path))
        print(f"Filled {path.name} ({filled} cells)")
    return filled


def chunk_and_zip(xls_files: list[Path], out_dir: Path, prefix: str) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    zips: list[Path] = []
    for i in range(0, len(xls_files), 12):
        chunk = xls_files[i : i + 12]
        out_zip = out_dir / f"{prefix}_{i // 12 + 1}.zip"
        with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for f in chunk:
                z.write(f, f.name)
        print(f"Import zip ({len(chunk)} xls) -> {out_zip}")
        zips.append(out_zip)
    return zips


def main() -> None:
    p = argparse.ArgumentParser(description="Fill Others export from legacy MSSQL")
    p.add_argument("--zip", type=Path, required=True, help="Encrypted CloudSAMS Others export zip")
    p.add_argument("--password", default="EvanGelisTic1617!")
    p.add_argument("--term", type=int, default=1, choices=(1, 2))
    p.add_argument("--classes", help="Comma-separated e.g. 1A,1B (default: all in zip)")
    p.add_argument("--work-dir", type=Path, default=DEFAULT_OUT / "others-fill-work")
    p.add_argument("--import-dir", type=Path, default=DEFAULT_OUT / "import-zips")
    p.add_argument("--zip-prefix", default="OTHERS_T1_FILLED")
    p.add_argument("--types", default="conduct,attendance,award", help="conduct,attendance,award,other")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    classes = [c.strip() for c in args.classes.split(",")] if args.classes else None
    legacy = _fetch_legacy(args.term, classes)
    print(f"Legacy rows: {len(legacy)}")

    xls_files = extract_others_zip(args.zip, args.work_dir, args.password.encode())
    type_map = {
        "conduct": "CONDUCT_AND_OVERALL_COMMENT",
        "attendance": "NON_ATTENDANCE",
        "award": "AWARD_PUNISHMENT",
        "other": "OTHER_ASSESS",
    }
    wanted = {type_map[t.strip()] for t in args.types.split(",") if t.strip() in type_map}
    targets = [f for f in xls_files if any(tag in f.name.upper() for tag in wanted)]
    if classes:
        targets = [f for f in targets if any(f"_{c}_" in f.name or f"_{c}." in f.name for c in classes)]

    total = 0
    for f in targets:
        total += fill_xls(f, legacy, dry_run=args.dry_run)

    if args.dry_run:
        print(f"Dry run: {len(targets)} files")
        return

    filled = [f for f in targets if f.stat().st_size > 0]
    chunk_and_zip(filled, args.import_dir, args.zip_prefix)
    print(f"Done: {total} cells across {len(targets)} xls")


if __name__ == "__main__":
    main()
