#!/usr/bin/env python3
"""CLI: question-level quality check on DOCX + optional spec (duplicates, concepts, answers)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from concept_check import (
    check_concepts,
    compare_concept_distributions,
    format_concept_report,
    format_distribution_report,
)
from exam_spec import load_spec
from answer_pattern_check import check_all_answer_patterns, format_all_patterns_report
from format_check import check_exam_format, format_format_report
from mcq_check import check_mcq, format_mcq_report
from quality_lib import THRESH_DUPLICATE, format_report_text, run_full_check, write_report_json
from spec_from_docx import docx_to_spec


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Question quality check: duplicates vs past papers, concepts, MCQ/answer keys.",
    )
    ap.add_argument("--candidate", required=True, help="Generated exam (.docx or .pdf)")
    ap.add_argument("--template", help="Original template / 原稿")
    ap.add_argument(
        "--past-papers-root",
        type=Path,
        default=_repo_root() / "Subjects" / "PastPaper" / "CMP+ICT",
    )
    ap.add_argument("--years", type=int, default=3)
    ap.add_argument("--subject", help='Limit past papers, e.g. "F5 ICT"')
    ap.add_argument("--reference", action="append", default=[])
    ap.add_argument("--candidate-spec", help="Candidate exam spec JSON")
    ap.add_argument("--template-spec", help="Template exam spec JSON")
    ap.add_argument("--json", type=Path, help="Write duplicate JSON report")
    ap.add_argument("--min-similarity", type=float, default=THRESH_DUPLICATE)
    ap.add_argument("--fail-on-duplicate", action=argparse.BooleanOptionalAction, default=False)
    ap.add_argument("--skip-concepts", action="store_true")
    ap.add_argument("--skip-mcq", action="store_true")
    ap.add_argument("--skip-format", action="store_true", help="Skip quote/indent format checks")
    args = ap.parse_args(argv)

    candidate = Path(args.candidate)
    template = Path(args.template) if args.template else None

    report = run_full_check(
        candidate,
        template=template,
        past_papers_root=args.past_papers_root,
        years=args.years,
        subject_subpath=args.subject,
        extra_references=[Path(r) for r in args.reference],
    )

    print("=== Duplicate check ===")
    print(format_report_text(report, min_similarity=args.min_similarity))

    exit_code = report.exit_code(fail_on_exact=args.fail_on_duplicate)

    if not args.skip_format:
        fmt = check_exam_format(candidate)
        print("\n=== Format (quotes + MCQ indent) ===")
        print(format_format_report(fmt))
        if not fmt.ok and exit_code == 0:
            exit_code = 1

    if not args.skip_mcq:
        cand_spec = None
        cand_spec_path = Path(args.candidate_spec) if args.candidate_spec else None
        if cand_spec_path and cand_spec_path.exists():
            cand_spec = load_spec(cand_spec_path)
        mcq_result = check_mcq(spec=cand_spec, docx_path=candidate)
        if mcq_result is not None:
            print("\n=== MCQ answers (balance + pattern) ===")
            print(format_mcq_report(mcq_result))
            if not mcq_result.ok and exit_code == 0:
                exit_code = 1
        if cand_spec is not None:
            pat_result = check_all_answer_patterns(cand_spec)
            print("\n=== All answer keys (randomness) ===")
            print(format_all_patterns_report(pat_result))
            if not pat_result.ok and exit_code == 0:
                exit_code = 1

    if not args.skip_concepts:
        cand_spec_path = Path(args.candidate_spec) if args.candidate_spec else None
        if cand_spec_path and cand_spec_path.exists():
            candidate_spec = load_spec(cand_spec_path)
            if args.template_spec:
                reference_spec = load_spec(Path(args.template_spec))
                ref_label = args.template_spec
            elif template:
                reference_spec = docx_to_spec(template)
                ref_label = str(template)
            else:
                reference_spec = None
                ref_label = ""

            if reference_spec is not None:
                concept_result = check_concepts(
                    candidate_spec,
                    reference_spec,
                    candidate_label=str(cand_spec_path),
                    reference_label=ref_label,
                )
                print("\n=== Concept alignment ===")
                print(format_concept_report(concept_result))
                if not concept_result.ok and exit_code == 0:
                    exit_code = 1
                if (
                    concept_result.distribution
                    and not concept_result.distribution_ok
                    and exit_code == 0
                ):
                    exit_code = 1

            dist = compare_concept_distributions(
                candidate_spec, reference_spec if reference_spec is not None else None
            )
            if dist.candidate.items_with_concepts > 0:
                print("\n=== Concept distribution ===")
                print(format_distribution_report(dist))
                if not dist.ok and exit_code == 0:
                    exit_code = 1

    if args.json:
        write_report_json(report, args.json)
        print(f"\nJSON report: {args.json}")

    return exit_code


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
