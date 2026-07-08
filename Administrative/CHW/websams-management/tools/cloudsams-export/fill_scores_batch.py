#!/usr/bin/env python3
"""Fill all class templates from a whole-school score export and build import zips."""

from __future__ import annotations

import argparse
import re
import shutil
import zipfile
from pathlib import Path

import pyzipper

from fill_scores_excel_com import fill_with_excel

DEFAULT_LOCAL = Path(__file__).resolve().parents[2] / "cloudsams-templates" / "asr" / "_local"
CLASS_RE = re.compile(r"_S\d+_([A-Z0-9]+)\.xls$", re.I)
CHUNK_SIZE = 10


def extract_scores_zip(encrypted: Path, out_dir: Path, password: bytes) -> list[Path]:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    with pyzipper.AESZipFile(encrypted) as zf:
        zf.extractall(out_dir, pwd=password)
    templates = sorted(out_dir.rglob("DE_*.xls"))
    if not templates:
        raise SystemExit(f"No DE_*.xls found under {out_dir}")
    return templates


def _class_name(path: Path) -> str:
    m = CLASS_RE.search(path.name)
    if not m:
        raise ValueError(f"Cannot parse class from {path.name}")
    return m.group(1)


def _seq(path: Path) -> str:
    return path.stem.split("_")[2]


def chunk_and_zip(filled: list[Path], import_dir: Path) -> list[Path]:
    import_dir.mkdir(parents=True, exist_ok=True)
    zips: list[Path] = []
    for i in range(0, len(filled), CHUNK_SIZE):
        chunk = filled[i : i + CHUNK_SIZE]
        zip_name = f"DE_52457320260707_{_seq(chunk[0])}.zip"
        out_zip = import_dir / zip_name
        with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for f in chunk:
                zf.write(f, f.name)
        print(f"Import zip ({len(chunk)} xls) -> {out_zip}")
        zips.append(out_zip)
    return zips


def main() -> None:
    p = argparse.ArgumentParser(description="Fill whole-school ASR score export")
    p.add_argument(
        "--export-zip",
        type=Path,
        default=DEFAULT_LOCAL / "whole-school-T1A1-scores.zip",
        help="Encrypted CloudSAMS whole-school score export",
    )
    p.add_argument("--password", default="EvanGelisTic1617!")
    p.add_argument("--template-dir", type=Path, default=DEFAULT_LOCAL / "extracted-ws")
    p.add_argument("--work-dir", type=Path, default=DEFAULT_LOCAL / "scores-fill-work")
    p.add_argument("--import-dir", type=Path, default=DEFAULT_LOCAL / "import-zips")
    p.add_argument("--skip-extract", action="store_true")
    p.add_argument("--classes", help="Comma-separated subset e.g. 1A,2B (default: all)")
    args = p.parse_args()

    if not args.skip_extract:
        templates = extract_scores_zip(args.export_zip, args.template_dir, args.password.encode())
    else:
        templates = sorted(args.template_dir.rglob("DE_*.xls"))
    if args.classes:
        wanted = {c.strip().upper() for c in args.classes.split(",")}
        templates = [t for t in templates if _class_name(t).upper() in wanted]

    args.work_dir.mkdir(parents=True, exist_ok=True)
    filled: list[Path] = []
    total_cells = 0
    for tpl in templates:
        cls = _class_name(tpl)
        out = args.work_dir / tpl.name
        n = fill_with_excel(tpl, cls, out)
        total_cells += n
        filled.append(out)
        print(f"  {cls}: {n} cells -> {out.name}")

    zips = chunk_and_zip(filled, args.import_dir)
    print(f"Done: {len(filled)} classes, {total_cells} cells, {len(zips)} import zip(s)")


if __name__ == "__main__":
    main()
