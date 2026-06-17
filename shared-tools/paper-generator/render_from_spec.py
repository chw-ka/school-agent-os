#!/usr/bin/env python3
"""Phase 6: render exam DOCX from spec + paper_review."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_PG = Path(__file__).resolve().parent
for _p in (_PG, _PG.parent / "question-quality-check"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from exam_spec import load_spec  # noqa: E402
from f5_ict_blueprint_db_web import render_docx  # noqa: E402
from f5_ict_generate_from_blueprint import written_picks_from_items  # noqa: E402
from f5_ict_written_from_dse import set_active_written_picks  # noqa: E402
from spec_mcq_render import spec_mcq_to_final_rows  # noqa: E402

_DEFAULT_SPEC = (
    _REPO
    / "Subjects/S5-ICT/assessments/2025-2026/Term 02/_generation/25_26_S5_ICT_Exam02.spec.json"
)
_DEFAULT_TEMPLATE = (
    _REPO
    / "Subjects/S5-ICT/past-papers/2024-2025/Term 02/WrittenExam/24_25_S5_ICT_Exam02.docx"
)
_DEFAULT_DOCX = (
    _REPO
    / "Subjects/S5-ICT/past-papers/2025-2026/Term 02/WrittenExam/25_26_S5_ICT_Exam02.docx"
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--spec", type=Path, default=_DEFAULT_SPEC)
    ap.add_argument("--template", type=Path, default=_DEFAULT_TEMPLATE)
    ap.add_argument("--out", type=Path, default=_DEFAULT_DOCX)
    ap.add_argument("--question-check", action="store_true", help="Run question_review before render")
    ap.add_argument("--no-paper-check", action="store_true", help="Skip paper_review after render")
    ap.add_argument(
        "--force",
        action="store_true",
        help="Render even if question_review fails",
    )
    args = ap.parse_args(argv)

    spec_path = args.spec.expanduser().resolve()
    template = args.template.expanduser().resolve()
    out_path = args.out.expanduser().resolve()
    spec = load_spec(spec_path)

    if args.question_check:
        from post_check import run_question_spec_check

        q_code = run_question_spec_check(
            candidate_spec=spec_path,
            template=template,
            subject_subpath="S5-ICT",
        )
        print(f"question_review exit: {q_code}")
        if q_code != 0 and not args.force:
            print("Question check failed — use --force to render anyway.")
            return q_code

    final_rows, mcq_key = spec_mcq_to_final_rows(spec)
    meta = spec.get("meta") or {}
    use_template_written = meta.get("written_render") == "template"
    picks = {} if use_template_written else written_picks_from_items(spec.get("items") or [])
    set_active_written_picks(picks)
    if use_template_written:
        written_mode = "template (f5_ict_written_content)"
    elif meta.get("written_render") == "patterns":
        written_mode = f"patterns ({len(picks)} slots)"
    else:
        written_mode = f"picks ({len(picks)} slots)"
    print(f"MCQ rows: {len(final_rows)}, written: {written_mode}")

    footer = dict((spec.get("meta") or {}).get("footer") or {})
    if not footer:
        footer = {
            "academic_year": "2025-2026",
            "level": "中五級",
            "term_exam": "下學期考試",
            "subject": "資訊及通訊科技",
        }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    populate_body_tables = meta.get("written_render") == "template"
    render_docx(
        template,
        out_path,
        final_mcq_rows=final_rows,
        footer_meta=footer,
        populate_body_tables=populate_body_tables,
        spec=spec,
        mcq_key=mcq_key,
        include_answers=True,
    )
    print(f"Wrote DOCX: {out_path}")
    print(f"MCQ key: {mcq_key}")

    if args.no_paper_check:
        return 0

    from post_check import run_post_render_check

    p_code = run_post_render_check(
        candidate_spec=spec_path,
        candidate_docx=out_path,
        template=template,
    )
    print(f"paper_review exit: {p_code}")
    return p_code


if __name__ == "__main__":
    raise SystemExit(main())
