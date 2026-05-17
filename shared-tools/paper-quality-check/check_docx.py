#!/usr/bin/env python3
"""CLI: paper-level quality check on rendered DOCX (footer, cover)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from check_paper import format_paper_report_text, report_exit_code, run_paper_check


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Paper quality check: footer banner and cover page vs filename/meta.",
    )
    ap.add_argument("--candidate", required=True, help="Generated exam DOCX")
    ap.add_argument("--candidate-spec", help="Exam spec JSON (meta.footer)")
    ap.add_argument("--template", help="Template DOCX (footer fallback)")
    ap.add_argument("--skip-footer", action="store_true")
    ap.add_argument("--skip-cover", action="store_true")
    ap.add_argument("--json", type=Path, help="Write JSON report")
    ap.add_argument("--strict", action="store_true", help="Exit 2 on issues")
    args = ap.parse_args(argv)

    report = run_paper_check(
        Path(args.candidate),
        candidate_spec_path=Path(args.candidate_spec) if args.candidate_spec else None,
        template_docx_path=Path(args.template) if args.template else None,
        verify_footer=not args.skip_footer,
        verify_cover=not args.skip_cover,
    )

    print(format_paper_report_text(report))
    if args.json:
        from check_paper import write_paper_report_json

        write_paper_report_json(report, args.json)
        print(f"\nJSON report: {args.json}")

    return report_exit_code(report, strict=args.strict)


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
