#!/usr/bin/env python3
"""Phase 5: partial regen failed slots in an exam spec (max 10 attempts each)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_PG = Path(__file__).resolve().parent
for _p in (_PG, _PG.parent / "question-quality-check"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from check_spec import format_quality_report_text, report_exit_code, run_question_check  # noqa: E402
from exam_spec import load_spec, save_spec  # noqa: E402
from f5_ict_exam_blueprint import load_blueprint  # noqa: E402
from f5_ict_generate_from_blueprint import (  # noqa: E402
    _load_json,
    written_picks_from_items,
)
from f5_ict_written_from_dse import set_active_written_picks  # noqa: E402
from partial_regen import (  # noqa: E402
    build_reference_specs,
    collect_failed_slot_ids,
    partial_regen_with_review,
    run_partial_regen,
    save_partial_regen_report,
)

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
_DEFAULT_REPORT = (
    _REPO
    / "Subjects/S5-ICT/past-papers/2025-2026/Term 02/_generation/25_26_S5_ICT_Exam02.partial_regen.json"
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--spec", type=Path, default=_DEFAULT_SPEC)
    ap.add_argument("--blueprint", type=Path, default=_DEFAULT_BP)
    ap.add_argument("--style-patterns", type=Path, default=_DEFAULT_STYLE)
    ap.add_argument("--template", type=Path, default=_DEFAULT_TEMPLATE)
    ap.add_argument("--report", type=Path, default=_DEFAULT_REPORT)
    ap.add_argument("--seed", type=int, default=20252026)
    ap.add_argument("--max-attempts", type=int, default=10)
    ap.add_argument("--rounds", type=int, default=2, help="Repeat partial regen until clean or max rounds")
    ap.add_argument("--set-written-picks", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="Only list failed slots, do not regen")
    ap.add_argument(
        "--solve-report",
        type=Path,
        default=_DEFAULT_SPEC.parent / "25_26_S5_ICT_Exam02.solve_review.json",
        help="solve_review.json for blocked slots + repair hints",
    )
    ap.add_argument(
        "--solve-repair",
        action="store_true",
        help="LLM-repair blocked slots from solve_report before pattern regen",
    )
    ap.add_argument("--provider", choices=["gemini", "deepseek", "openai"], default=None)
    args = ap.parse_args(argv)

    spec_path = args.spec.expanduser().resolve()
    template = args.template.expanduser().resolve()
    root = _REPO / "Subjects"
    style_path = args.style_patterns.expanduser().resolve()
    style = _load_json(style_path) if style_path.exists() else {}

    if args.dry_run:
        report = run_question_check(
            spec_path,
            template_docx_path=template,
            past_papers_root=root,
            subject_subpath="S5-ICT",
        )
        failed = collect_failed_slot_ids(report)
        print(format_quality_report_text(report))
        print(f"\nFailed slots ({len(failed)}): {', '.join(failed) or '(none)'}")
        return 0 if not failed else 1

    spec = load_spec(spec_path)
    blueprint = load_blueprint(args.blueprint)
    report = run_question_check(
        spec_path,
        template_docx_path=template,
        past_papers_root=root,
        subject_subpath="S5-ICT",
    )
    failed = collect_failed_slot_ids(report)
    solve_fb: dict = {}
    solve_path = args.solve_report.expanduser().resolve()
    if solve_path.is_file():
        from solve_review_core import feedback_by_slot, load_solve_review

        sr = load_solve_review(solve_path)
        solve_fb = feedback_by_slot(sr)
        for sid in sr.blocked_ids:
            if sid not in failed:
                failed.append(sid)
        print(f"Loaded solve_review: {len(sr.blocked_ids)} blocked slot(s)")

    if not failed:
        print("No failed slots — spec already passes question_review.")
        return 0

    llm_cfg = None
    if args.solve_repair:
        from solve_llm import llm_config_from_env

        try:
            llm_cfg = llm_config_from_env(provider=args.provider)
        except RuntimeError as e:
            print(str(e))
            print("Run: .venv/bin/python shared-tools/paper-generator/solve_review.py --check-key")
            return 2

    refs = build_reference_specs(
        template_docx=template,
        past_papers_root=root,
        subject_subpath="S5-ICT",
    )
    last_pr = None
    for round_i in range(1, args.rounds + 1):
        if not failed:
            break
        print(f"Partial regen round {round_i}/{args.rounds}: {len(failed)} slot(s)")
        last_pr = run_partial_regen(
            spec,
            blueprint,
            style,
            failed,
            seed=args.seed + round_i * 1000,
            max_attempts=args.max_attempts,
            refs=refs,
            solve_feedback=solve_fb,
            use_llm_repair=args.solve_repair,
            llm_cfg=llm_cfg,
        )
        save_spec(spec_path, spec)
        save_partial_regen_report(last_pr, args.report)
        for s in last_pr.slots:
            status = "OK" if s.resolved else "FAIL"
            print(f"  {s.slot_id}: {status} ({s.attempts} tries) — {s.note}")
        q_mid = run_question_check(
            spec_path,
            template_docx_path=template,
            past_papers_root=root,
            subject_subpath="S5-ICT",
        )
        failed = collect_failed_slot_ids(q_mid)
    print(f"Wrote spec: {spec_path}")
    print(f"Regen report: {args.report.expanduser().resolve()}")
    if last_pr and last_pr.unresolved:
        print(f"Unresolved: {', '.join(last_pr.unresolved)}")

    if args.set_written_picks:
        set_active_written_picks(written_picks_from_items(spec["items"]))

    final = run_question_check(
        spec_path,
        template_docx_path=template,
        past_papers_root=root,
        subject_subpath="S5-ICT",
    )
    print("\n--- Final question_review ---")
    print(format_quality_report_text(final))
    code = report_exit_code(final)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
