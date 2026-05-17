#!/usr/bin/env python3
"""CLI: paper quality check when spec + rendered DOCX are available."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_CHECK_DIR = Path(__file__).resolve().parent
if str(_CHECK_DIR) not in sys.path:
    sys.path.insert(0, str(_CHECK_DIR))

from check_paper import format_paper_report_text, report_exit_code, run_paper_check, write_paper_report_json


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Paper quality check (footer + cover) with spec + DOCX.")
    ap.add_argument("--candidate-spec", required=True, help="Exam spec JSON")
    ap.add_argument("--candidate-docx", help="Rendered DOCX (default: same stem as spec)")
    ap.add_argument("--template", help="Template DOCX for footer fallback")
    ap.add_argument("--json", type=Path)
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--skip-footer", action="store_true")
    ap.add_argument("--skip-cover", action="store_true")
    args = ap.parse_args(argv)

    spec_path = Path(args.candidate_spec).expanduser().resolve()
    docx_path = Path(args.candidate_docx) if args.candidate_docx else spec_path.with_suffix(".docx")
    if not docx_path.exists():
        print(f"DOCX not found: {docx_path}", file=sys.stderr)
        return 1

    report = run_paper_check(
        docx_path,
        candidate_spec_path=spec_path,
        template_docx_path=Path(args.template) if args.template else None,
        verify_footer=not args.skip_footer,
        verify_cover=not args.skip_cover,
    )
    print(format_paper_report_text(report))
    if args.json:
        write_paper_report_json(report, args.json)
    return report_exit_code(report, strict=args.strict)


if __name__ == "__main__":
    raise SystemExit(main())
