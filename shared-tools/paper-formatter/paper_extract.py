#!/usr/bin/env python3
"""Extract F5 ICT (or future) template profile from reference DOCX."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_FMT = Path(__file__).resolve().parent
if str(_FMT) not in sys.path:
    sys.path.insert(0, str(_FMT))

from paper_format.extractor.f5_ict_extract import extract_f5_ict_profile, save_profile

_DEFAULT_SRC = (
    Path(__file__).resolve().parents[2]
    / "Subjects/S5-ICT/past-papers/2024-2025/Term 02/WrittenExam/24_25_S5_ICT_Exam02.docx"
)
_DEFAULT_OUT = (
    Path(__file__).resolve().parents[2]
    / "Subjects/S5-ICT/templates/24_25_S5_ICT_Exam02.profile.json"
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Extract paragraph role profiles (tabs, alignment, fonts) from reference DOCX.",
    )
    ap.add_argument("--source", type=Path, default=_DEFAULT_SRC, help="Reference past paper DOCX")
    ap.add_argument("--out", type=Path, default=_DEFAULT_OUT, help="Output profile JSON")
    ap.add_argument("--label", default="24_25_S5_ICT_Exam02", help="Profile label")
    args = ap.parse_args(argv)

    if not args.source.exists():
        print(f"ERROR: source not found: {args.source}", file=sys.stderr)
        return 1

    profile = extract_f5_ict_profile(args.source, source_label=args.label)
    save_profile(profile, args.out)
    roles = len(profile.get("roles") or {})
    print(f"Wrote {args.out} ({roles} role profiles)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
