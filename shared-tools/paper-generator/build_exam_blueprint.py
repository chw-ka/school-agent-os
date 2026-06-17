#!/usr/bin/env python3
"""CLI: write exam_blueprint.json for F5 ICT Exam02."""
from __future__ import annotations

import argparse
from pathlib import Path

from concept_review import (
    format_concept_review_report,
    run_concept_review,
    write_concept_review_json,
)
from f5_ict_exam_blueprint import build_f5_exam02_blueprint, save_blueprint

_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_OUT = (
    _REPO
    / "Subjects/S5-ICT/assessments/2025-2026/Term 02/_generation/exam_blueprint.json"
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=_DEFAULT_OUT)
    ap.add_argument("--academic-year", default="2025-2026")
    ap.add_argument("--title", default="25-26 S5 ICT Exam02 Blueprint")
    ap.add_argument("--review", action="store_true", help="Run concept_review after write")
    ap.add_argument("--strict", action="store_true", help="Fail review on warnings")
    ap.add_argument("--json-report", type=Path, help="concept_review JSON path")
    args = ap.parse_args(argv)

    blueprint = build_f5_exam02_blueprint(
        academic_year=args.academic_year,
        title=args.title,
    )
    out = save_blueprint(blueprint, args.out)
    print(f"Wrote {out} ({len(blueprint['slots'])} slots)")

    if args.review:
        report = run_concept_review(out)
        print()
        print(format_concept_review_report(report))
        jpath = args.json_report or out.with_suffix(".concept_review.json")
        write_concept_review_json(report, jpath)
        print(f"Report: {jpath}")
        code = report.exit_code_strict() if args.strict else report.exit_code
        return code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
