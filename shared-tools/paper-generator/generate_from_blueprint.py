#!/usr/bin/env python3
"""Phase 4: generate exam spec from blueprint + style_patterns (no bank copy)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_PG = Path(__file__).resolve().parent
for _p in (_PG, _PG.parent / "question-quality-check"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from concept_review import format_concept_review_report, run_concept_review  # noqa: E402
from exam_spec import save_spec  # noqa: E402
from f5_ict_exam_blueprint import load_blueprint  # noqa: E402
from f5_ict_generate_from_blueprint import (  # noqa: E402
    _load_json,
    build_spec_from_blueprint,
    written_picks_from_items,
)
from f5_ict_written_from_dse import set_active_written_picks  # noqa: E402

_DEFAULT_BP = (
    _REPO
    / "Subjects/S5-ICT/past-papers/2025-2026/Term 02/_generation/exam_blueprint.json"
)
_DEFAULT_STYLE = _REPO / "Subjects/DSE-ICT/question-bank/style_patterns.json"
_DEFAULT_SPEC = (
    _REPO
    / "Subjects/S5-ICT/past-papers/2025-2026/Term 02/_generation/25_26_S5_ICT_Exam02.spec.json"
)
_DEFAULT_TEMPLATE = (
    _REPO
    / "Subjects/S5-ICT/past-papers/2024-2025/Term 02/WrittenExam/24_25_S5_ICT_Exam02.docx"
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--blueprint", type=Path, default=_DEFAULT_BP)
    ap.add_argument("--style-patterns", type=Path, default=_DEFAULT_STYLE)
    ap.add_argument("--out", type=Path, default=_DEFAULT_SPEC)
    ap.add_argument("--seed", type=int, default=20252026)
    ap.add_argument("--concept-review", action="store_true", help="Run concept_review on blueprint first")
    ap.add_argument("--question-check", action="store_true", help="Run question_review on generated spec")
    ap.add_argument("--template", type=Path, default=_DEFAULT_TEMPLATE)
    ap.add_argument("--set-written-picks", action="store_true", help="Activate written_picks for DOCX render")
    ap.add_argument(
        "--partial-regen",
        action="store_true",
        help="After generate, regen failed slots only (max 10 each)",
    )
    ap.add_argument("--max-attempts", type=int, default=10)
    ap.add_argument(
        "--regen-report",
        type=Path,
        default=_DEFAULT_SPEC.parent / "25_26_S5_ICT_Exam02.partial_regen.json",
    )
    ap.add_argument(
        "--regen-rounds",
        type=int,
        default=2,
        help="Partial regen passes when --partial-regen (default 2)",
    )
    args = ap.parse_args(argv)

    bp_path = args.blueprint.expanduser().resolve()
    if args.concept_review:
        cr = run_concept_review(bp_path)
        print(format_concept_review_report(cr))
        if not cr.ok:
            print("Concept review failed — fix blueprint before generate.")
            return 1

    blueprint = load_blueprint(bp_path)
    style_path = args.style_patterns.expanduser().resolve()
    style = _load_json(style_path) if style_path.exists() else {}

    spec = build_spec_from_blueprint(blueprint, seed=args.seed, style_patterns=style)
    out_path = args.out.expanduser().resolve()
    save_spec(out_path, spec)
    print(f"Wrote spec: {out_path} ({len(spec['items'])} items)")
    print(f"MCQ key: {spec['meta'].get('mcq_answers', '')}")

    if args.partial_regen:
        from partial_regen import (
            build_reference_specs,
            collect_failed_slot_ids,
            run_partial_regen,
            save_partial_regen_report,
        )
        from check_spec import run_question_check

        root = _REPO / "Subjects"
        template = args.template.expanduser().resolve()
        q0 = run_question_check(
            out_path,
            template_docx_path=template,
            past_papers_root=root,
            subject_subpath="S5-ICT",
        )
        failed = collect_failed_slot_ids(q0)
        refs = build_reference_specs(
            template_docx=template,
            past_papers_root=root,
            subject_subpath="S5-ICT",
        )
        for round_i in range(1, args.regen_rounds + 1):
            if not failed:
                break
            print(f"Partial regen round {round_i}/{args.regen_rounds}: {len(failed)} slot(s)")
            pr = run_partial_regen(
                spec,
                blueprint,
                style,
                failed,
                seed=args.seed + round_i * 1000,
                max_attempts=args.max_attempts,
                refs=refs,
            )
            save_spec(out_path, spec)
            save_partial_regen_report(pr, args.regen_report.expanduser().resolve())
            print(f"  → unresolved: {pr.unresolved or '(none)'}")
            q_mid = run_question_check(
                out_path,
                template_docx_path=template,
                past_papers_root=root,
                subject_subpath="S5-ICT",
            )
            failed = collect_failed_slot_ids(q_mid)
        if not failed:
            print("Partial regen: all targeted slots resolved.")
        else:
            print(f"Report: {args.regen_report}")

    if args.set_written_picks:
        picks = written_picks_from_items(spec["items"])
        set_active_written_picks(picks)
        print(f"set_active_written_picks({len(picks)} written slots)")

    if args.question_check:
        from post_check import run_question_spec_check

        code = run_question_spec_check(
            candidate_spec=out_path,
            template=args.template.expanduser().resolve(),
            subject_subpath="S5-ICT",
        )
        print(f"question_review exit: {code}")
        return code

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
