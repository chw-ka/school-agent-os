#!/usr/bin/env python3
"""
Fill a CloudSAMS ASR export xlsx with legacy tblStudentPaperScore data.

Prerequisites:
  1. Real export from 學生成績 → 匯出資料 (batch number embedded — do not rename file)
  2. inspect_asr_export.py run to capture column schema
  3. Legacy MSSQL query for matching form/term/paper

Usage (after Step 1 export exists locally):
  python export_scores.py --template _local/extracted/S1-T1A1-1A.xlsx --form 1 --term 1 --period T1A1 --dry-run
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# TODO: wire legacy SQL + column mapping once schema.json exists from first export


def main() -> None:
    p = argparse.ArgumentParser(description="Fill CloudSAMS ASR export from legacy scores")
    p.add_argument("--template", type=Path, required=True, help="Decrypted CloudSAMS export xlsx (unchanged filename)")
    p.add_argument("--form", type=int, required=True, help="Legacy form id (1=S1 …)")
    p.add_argument("--term", type=int, choices=[1, 2], required=True)
    p.add_argument("--period", required=True, help="T1A1|T1A2|T1|T2A1|T2A2|T2|Annual")
    p.add_argument("--output", type=Path, help="Output path (default: overwrite template copy)")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    if not args.template.is_file():
        sys.exit(f"Template not found: {args.template}")

    print(
        f"Scaffold only — run inspect_asr_export.py first, then implement mapping for "
        f"form={args.form} term={args.term} period={args.period}",
        file=sys.stderr,
    )
    if args.dry_run:
        print("Dry run OK (no writes).", file=sys.stderr)
        return
    sys.exit("Not implemented until first ASR export schema is captured.")


if __name__ == "__main__":
    main()
