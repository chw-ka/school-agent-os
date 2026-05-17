#!/usr/bin/env python3
"""CLI: question quality check on exam spec JSON (before DOCX render)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_CHECK_DIR = Path(__file__).resolve().parent
if str(_CHECK_DIR) not in sys.path:
    sys.path.insert(0, str(_CHECK_DIR))

from check_spec import (
    format_quality_report_text,
    report_exit_code,
    run_question_check,
    write_quality_report_json,
)
from quality_lib import THRESH_DUPLICATE, infer_subject_subpath


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Question quality check on exam spec JSON (duplicates, concepts, answer keys).",
    )
    ap.add_argument("--candidate", required=True, help="Candidate exam spec .json")
    ap.add_argument("--template", help="Template DOCX (converted to spec on the fly)")
    ap.add_argument("--template-spec", help="Template exam spec .json")
    ap.add_argument("--candidate-docx", help="Rendered candidate DOCX (MCQ key fallback)")
    ap.add_argument(
        "--past-papers-root",
        type=Path,
        default=_repo_root() / "Subjects" / "PastPaper" / "CMP+ICT",
    )
    ap.add_argument("--years", type=int, default=3)
    ap.add_argument("--subject", help='e.g. "F5 ICT"')
    ap.add_argument("--reference-spec", action="append", default=[])
    ap.add_argument("--reference", action="append", default=[])
    ap.add_argument("--json", type=Path)
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--skip-concepts", action="store_true")
    ap.add_argument("--skip-mcq", action="store_true")
    ap.add_argument("--skip-format", action="store_true")
    args = ap.parse_args(argv)

    candidate = Path(args.candidate)
    subject = args.subject or infer_subject_subpath(candidate)

    report = run_question_check(
        candidate,
        template_spec_path=Path(args.template_spec) if args.template_spec else None,
        template_docx_path=Path(args.template) if args.template else None,
        candidate_docx_path=Path(args.candidate_docx) if args.candidate_docx else None,
        past_papers_root=args.past_papers_root,
        years=args.years,
        subject_subpath=subject,
        extra_reference_specs=[Path(p) for p in args.reference_spec],
        extra_reference_docx=[Path(p) for p in args.reference],
        threshold=THRESH_DUPLICATE,
        verify_concepts=not args.skip_concepts,
        verify_mcq=not args.skip_mcq,
        verify_format=not args.skip_format,
    )

    print(format_quality_report_text(report))
    if args.json:
        write_quality_report_json(report, args.json)
        print(f"\nQuality report: {args.json}")

    return report_exit_code(report, strict=args.strict)


if __name__ == "__main__":
    raise SystemExit(main())
