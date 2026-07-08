#!/usr/bin/env python3
"""Fill CloudSAMS ASR Others export from legacy data.

Follows ../chw-websams-migration/migrate_others.py:
  export (encrypted) -> decrypt -> edit cells only -> plain zip (same xls basenames).
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import zipfile
from pathlib import Path

try:
    import pyzipper
except ImportError:
    pyzipper = None  # type: ignore

from xlutils.copy import copy
import xlrd

DEFAULT_OUT = Path(__file__).resolve().parents[2] / "cloudsams-templates" / "asr" / "_local"

COMMENT_COLUMNS = ("評語 (中文)", "Comment (Chinese)")
OTHERS_SUFFIXES = (
    "AWARD_PUNISHMENT.xls",
    "CONDUCT_AND_OVERALL_COMMENT.xls",
    "NON_ATTENDANCE.xls",
    "OTHER_ASSESS.xls",
    "OVERALL_COMMENT.xls",
)


def _decrypt_zip(zpath: Path, out_dir: Path, password: bytes) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    if pyzipper is None:
        raise SystemExit("pip install pyzipper")
    with pyzipper.AESZipFile(zpath) as z:
        z.extractall(out_dir, pwd=password)
    return sorted(out_dir.glob("**/*.xls"))


def _comment_column(hdr: list[str]) -> int:
    for name in COMMENT_COLUMNS:
        if name in hdr:
            return hdr.index(name)
    raise SystemExit(f"No comment column in {COMMENT_COLUMNS}; got {hdr}")


def fill_comment(xls: Path, reg_no: str, comment: str, dry_run: bool) -> None:
    rb = xlrd.open_workbook(str(xls), formatting_info=True)
    ws = rb.sheet_by_index(0)
    hdr = [str(c) for c in ws.row_values(0)]
    col = _comment_column(hdr)
    row_idx = None
    for r in range(1, ws.nrows):
        if str(ws.row_values(r)[5]).strip() == reg_no:
            row_idx = r
            break
    if row_idx is None:
        raise SystemExit(f"Reg no {reg_no} not found in {xls.name}")
    if dry_run:
        print(f"Would write {xls.name} row {row_idx} col {col}: {comment[:60]}...")
        return
    wb = copy(rb)
    sheet = wb.get_sheet(0)
    sheet.write(row_idx, col, comment)
    wb.save(str(xls))
    print(f"Filled {xls.name} ({hdr[col]})")


def build_import_zip(
    xls_files: list[Path],
    out_zip: Path,
    *,
    max_files: int = 12,
    zip_prefix: str = "OTHERS_T1",
) -> None:
    """Plain zip for 匯入「其他資料」 — no password, flat xls, basenames unchanged."""
    if len(xls_files) > max_files:
        raise SystemExit(f"Other-data import allows max {max_files} Excel files; got {len(xls_files)}")
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for f in xls_files:
            z.write(f, f.name)
    print(f"Wrote import zip ({len(xls_files)} xls, no password) -> {out_zip}")


def chunk_and_zip(
    xls_files: list[Path],
    out_dir: Path,
    *,
    chunk_size: int = 12,
    zip_prefix: str = "OTHERS_T1",
) -> list[Path]:
    """Split into multiple import zips (max 12 xls each), chw-websams-migration style."""
    out_dir.mkdir(parents=True, exist_ok=True)
    zips: list[Path] = []
    for i in range(0, len(xls_files), chunk_size):
        chunk = xls_files[i : i + chunk_size]
        out_zip = out_dir / f"{zip_prefix}_{i // chunk_size + 1}.zip"
        build_import_zip(chunk, out_zip, max_files=chunk_size, zip_prefix=zip_prefix)
        zips.append(out_zip)
    return zips


def filter_others_xls(files: list[Path]) -> list[Path]:
    return sorted(f for f in files if f.name.endswith(OTHERS_SUFFIXES))


def main() -> None:
    p = argparse.ArgumentParser(description="Fill ASR Others 整體評語 export (keep filenames)")
    p.add_argument("--zip", type=Path, help="Encrypted CloudSAMS Others export zip")
    p.add_argument("--password", default="EvanGelisTic1617!")
    p.add_argument("--reg-no", help="e.g. #25001 (single-student trial)")
    p.add_argument("--comment", help="Comment text for --reg-no trial")
    p.add_argument("--class-xls", type=Path, help="Already-decrypted xls (skip zip extract)")
    p.add_argument("--build-zip", type=Path, help="Output plain import zip path")
    p.add_argument("--input-dir", type=Path, help="Directory of filled xls to chunk+zip")
    p.add_argument("--zip-prefix", default="OTHERS_T1")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    if args.input_dir:
        files = filter_others_xls(sorted(args.input_dir.glob("*.xls")))
        if not files:
            sys.exit(f"No Others xls in {args.input_dir}")
        out_dir = args.build_zip.parent if args.build_zip else DEFAULT_OUT / "import-zips"
        chunk_and_zip(files, out_dir, zip_prefix=args.zip_prefix)
        return

    if args.class_xls:
        if not args.reg_no or not args.comment:
            sys.exit("--reg-no and --comment required with --class-xls")
        fill_comment(args.class_xls, args.reg_no, args.comment, args.dry_run)
        if args.build_zip:
            build_import_zip([args.class_xls], args.build_zip)
        return

    if not args.zip:
        sys.exit("Provide --zip, --class-xls, or --input-dir")
    if not args.reg_no or not args.comment:
        sys.exit("--reg-no and --comment required with --zip")

    pwd = args.password.encode()
    if not args.zip.is_file():
        sys.exit(f"Zip not found: {args.zip}")

    work = DEFAULT_OUT / "others-fill-work"
    if work.exists():
        shutil.rmtree(work)
    xls_files = filter_others_xls(_decrypt_zip(args.zip, work, pwd))
    if not xls_files:
        sys.exit("No Others xls in zip (expected *CONDUCT_AND_OVERALL_COMMENT.xls etc.)")

    target = xls_files[0]
    for f in xls_files:
        if "CONDUCT_AND_OVERALL_COMMENT" in f.name.upper():
            target = f
            break
        if "OVERALL_COMMENT" in f.name.upper():
            target = f

    fill_comment(target, args.reg_no, args.comment, args.dry_run)
    if args.build_zip and not args.dry_run:
        build_import_zip([target], args.build_zip)


if __name__ == "__main__":
    main()
