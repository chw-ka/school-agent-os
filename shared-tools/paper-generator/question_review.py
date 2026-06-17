#!/usr/bin/env python3
"""question_review — spec-only quality check (alias for run_question_spec_check)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_PG = Path(__file__).resolve().parent
if str(_PG) not in sys.path:
    sys.path.insert(0, str(_PG))

from post_check import run_question_review  # noqa: E402

_DEFAULT_SPEC = (
    _REPO
    / "Subjects/S5-ICT/assessments/2025-2026/Term 02/_generation/25_26_S5_ICT_Exam02.spec.json"
)
_DEFAULT_TEMPLATE = (
    _REPO
    / "Subjects/S5-ICT/past-papers/2024-2025/Term 02/WrittenExam/24_25_S5_ICT_Exam02.docx"
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--spec", type=Path, default=_DEFAULT_SPEC)
    ap.add_argument("--template", type=Path, default=_DEFAULT_TEMPLATE)
    ap.add_argument("--json", type=Path, help="Write quality report JSON")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args(argv)
    return run_question_review(
        candidate_spec=args.spec,
        template=args.template,
        subject_subpath="S5-ICT",
        json_report=args.json,
        strict=args.strict,
    )


if __name__ == "__main__":
    raise SystemExit(main())
