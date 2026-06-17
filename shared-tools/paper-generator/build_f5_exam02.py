#!/usr/bin/env python3
"""Canonical F5 ICT Exam02 pipeline (blueprint generate → partial regen → render).

Replaces bank pick-transform via regenerate_exam02.py (use --legacy-pick there only).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_PG = Path(__file__).resolve().parent
if str(_PG) not in sys.path:
    sys.path.insert(0, str(_PG))

_DEFAULT_GEN = _REPO / "Subjects/S5-ICT/assessments/2025-2026/Term 02/_generation"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--generation-dir", type=Path, default=_DEFAULT_GEN)
    ap.add_argument("--seed", type=int, default=20252026)
    ap.add_argument(
        "--full-regen",
        action="store_true",
        help="Force full regeneration (overwrite spec) from blueprint with updated workflow",
    )
    ap.add_argument("--no-partial-regen", action="store_true")
    ap.add_argument("--regen-rounds", type=int, default=3)
    ap.add_argument("--skip-render", action="store_true", help="Stop after spec + question_review")
    ap.add_argument("--render-only", action="store_true", help="Only render_from_spec (existing spec)")
    ap.add_argument("--force-render", action="store_true", help="Render even if question_review fails")
    args = ap.parse_args(argv)

    gen = args.generation_dir.expanduser().resolve()
    spec = gen / "25_26_S5_ICT_Exam02.spec.json"
    docx = gen.parent / "WrittenExam" / "25_26_S5_ICT_Exam02.docx"

    if args.render_only:
        from render_from_spec import main as render_main

        rargv = ["--spec", str(spec), "--out", str(docx)]
        if args.force_render:
            rargv.append("--force")
        return render_main(rargv)

    from generate_from_blueprint import main as gen_main

    gargv = [
        "--out",
        str(spec),
        "--seed",
        str(args.seed),
        "--set-written-picks",
        "--question-check",
    ]
    if args.full_regen:
        # No special flag needed beyond overwriting output, but keep for clarity / CLI ergonomics.
        pass
    if not args.no_partial_regen:
        gargv.extend(["--partial-regen", "--regen-rounds", str(args.regen_rounds)])
    code = gen_main(gargv)
    if code != 0 and not args.force_render:
        print("generate_from_blueprint failed — fix spec or use --force-render.")
        if args.skip_render:
            return code
        return code

    if args.skip_render:
        return code

    from render_from_spec import main as render_main

    rargv = ["--spec", str(spec), "--out", str(docx)]
    if args.force_render or code != 0:
        rargv.append("--force")
    rcode = render_main(rargv)
    return max(code, rcode)


if __name__ == "__main__":
    raise SystemExit(main())
