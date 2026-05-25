#!/usr/bin/env python3
"""solve_review — LLM student-style answer check (Phases 1–4)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_PG = Path(__file__).resolve().parent
_QCHECK = _PG.parent / "question-quality-check"
for _p in (_PG, _QCHECK):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from exam_spec import load_spec, save_spec  # noqa: E402
from solve_generation_rules import (  # noqa: E402
    load_generation_rules,
    merge_solve_report_into_rules,
    save_generation_rules,
)
from solve_llm import check_api_key, llm_config_from_env, llm_json_completion  # noqa: E402
from solve_review_core import (  # noqa: E402
    format_solve_review_report,
    run_solve_review,
    save_solve_review,
)
from solve_tables import sync_item_tables_in_spec  # noqa: E402

_DEFAULT_SPEC = (
    _REPO
    / "Subjects/S5-ICT/past-papers/2025-2026/Term 02/_generation/25_26_S5_ICT_Exam02.spec.json"
)
_DEFAULT_OUT = (
    _REPO
    / "Subjects/S5-ICT/past-papers/2025-2026/Term 02/_generation/25_26_S5_ICT_Exam02.solve_review.json"
)
_DEFAULT_DOCX = (
    _REPO
    / "Subjects/S5-ICT/past-papers/2025-2026/Term 02/WrittenExam/25_26_S5_ICT_Exam02.docx"
)
_DEFAULT_RULES = _REPO / "Subjects/DSE-ICT/question-bank/solve_generation_rules.json"


def _print_setup_help() -> None:
    status = check_api_key()
    env = status["env_file"]
    print("=== LLM setup (DeepSeek / Gemini / OpenAI) ===")
    print(f"1. Copy template:  cp .env.example {env}")
    print("2. DeepSeek (recommended): docs/DEEPSEEK_API.md")
    print("     DEEPSEEK_API_KEY=sk-...  +  DSE_ICT_LLM_PROVIDER=deepseek")
    print("3. Or Gemini: docs/GOOGLE_API_KEY.md")
    print("4. Re-run:  .venv/bin/python shared-tools/paper-generator/solve_review.py --check-key")
    print("")
    print(f"  .env exists: {status['env_exists']}")
    print(f"  DEEPSEEK_API_KEY set: {status['DEEPSEEK_API_KEY_set']}")
    print(f"  GOOGLE_API_KEY set: {status['GOOGLE_API_KEY_set']}")
    print(f"  OPENAI_API_KEY set: {status['OPENAI_API_KEY_set']}")
    print(f"  DSE_ICT_LLM_PROVIDER: {status['DSE_ICT_LLM_PROVIDER']}")
    print(f"  Recommended: {status['recommended']}")
    print("")
    print("Guides: docs/DEEPSEEK_API.md  |  docs/SOLVE_REVIEW.md")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--spec", type=Path, default=_DEFAULT_SPEC)
    ap.add_argument("--out", type=Path, default=_DEFAULT_OUT)
    ap.add_argument("--docx", type=Path, default=None, help="Rendered DOCX for table checks (Phase 3)")
    ap.add_argument("--sync-tables", action="store_true", help="Write item.tables into spec before review")
    ap.add_argument("--save-spec", action="store_true", help="Save spec after --sync-tables")
    ap.add_argument("--provider", choices=["gemini", "deepseek", "openai"], default=None)
    ap.add_argument("--model", default=None)
    ap.add_argument("--check-key", action="store_true", help="Show API key setup status")
    ap.add_argument(
        "--test-api",
        action="store_true",
        help="Call LLM once (tiny prompt) to verify API access",
    )
    ap.add_argument("--dry-run", action="store_true", help="Only sync tables, no LLM")
    ap.add_argument("--item", action="append", dest="items", help="Review only these item ids")
    ap.add_argument("--merge-rules", action="store_true", help="Phase 4: update solve_generation_rules.json")
    ap.add_argument("--rules", type=Path, default=_DEFAULT_RULES)
    ap.add_argument(
        "--vision-pdf",
        type=Path,
        default=None,
        help="Use PDF page images for written section (needs sibling PDF or this path)",
    )
    ap.add_argument("--vision-page", type=int, default=None, help="1-based page for all written items (simple mode)")
    args = ap.parse_args(argv)

    if args.check_key:
        _print_setup_help()
        status = check_api_key(provider=args.provider)
        ok = (
            status["DEEPSEEK_API_KEY_set"] == "True"
            or status["GOOGLE_API_KEY_set"] == "True"
            or status["OPENAI_API_KEY_set"] == "True"
        )
        return 0 if ok else 1

    if args.test_api:
        try:
            cfg = llm_config_from_env(provider=args.provider, model=args.model)
        except RuntimeError as e:
            print(str(e))
            _print_setup_help()
            return 2
        model = args.model or cfg.model or "?"
        print(f"Testing chat/completions ({cfg.provider} / {model}) …")
        try:
            data = llm_json_completion(
                cfg=cfg,
                system='Reply JSON only: {"status":"ok"}',
                user="ping",
            )
            print("API test passed:", data)
            return 0
        except RuntimeError as e:
            msg = str(e)
            print("API test failed.")
            if "429" in msg and "limit: 0" in msg:
                print(
                    "\nYour key is valid but this Google project has NO free-tier generate quota.\n"
                    "Fix (pick one):\n"
                    "  1. Create a new key at https://aistudio.google.com/apikey (AI Studio, not Cloud Console only)\n"
                    "  2. In Google AI Studio → Settings → check API key is linked to a project with quota\n"
                    "  3. Enable billing on the Cloud project (free tier still applies in many regions)\n"
                    "  4. See https://ai.google.dev/gemini-api/docs/rate-limits\n"
                )
            elif "403" in msg and cfg.provider == "gemini":
                print("Model or project denied — try DeepSeek: docs/DEEPSEEK_API.md")
            elif "401" in msg:
                print("Invalid API key — check DEEPSEEK_API_KEY in .env (docs/DEEPSEEK_API.md)")
            else:
                print(msg[:800])
            return 1

    spec_path = args.spec.expanduser().resolve()
    spec = load_spec(spec_path)

    if args.sync_tables or args.dry_run:
        n = sync_item_tables_in_spec(spec)
        print(f"Synced tables on {n} written item(s).")
        if args.save_spec or args.dry_run:
            save_spec(spec_path, spec)
            print(f"Wrote spec: {spec_path}")
        if args.dry_run:
            return 0

    try:
        cfg = llm_config_from_env(provider=args.provider, model=args.model)
    except RuntimeError as e:
        print(str(e))
        print("")
        _print_setup_help()
        return 2

    vision_slots: dict[str, str] | None = None
    if args.vision_pdf or args.vision_page:
        from solve_docx import png_to_b64, render_docx_pages_png

        pdf_path = args.vision_pdf
        if not pdf_path:
            pdf_path = (_DEFAULT_DOCX if args.docx is None else args.docx).with_suffix(".pdf")
        pdf_path = pdf_path.expanduser().resolve()
        docx_for_pdf = args.docx or _DEFAULT_DOCX
        pages = render_docx_pages_png(docx_for_pdf, spec_path.parent / "_solve_vision")
        if not pages and pdf_path.is_file():
            import fitz

            out_dir = spec_path.parent / "_solve_vision"
            out_dir.mkdir(parents=True, exist_ok=True)
            doc = fitz.open(pdf_path)
            pages = []
            for i in range(doc.page_count):
                p = out_dir / f"page_{i + 1:02d}.png"
                doc.load_page(i).get_pixmap(dpi=150).save(str(p))
                pages.append(p)
        if pages and args.vision_page and 1 <= args.vision_page <= len(pages):
            b64 = png_to_b64(pages[args.vision_page - 1])
            vision_slots = {}
            for row in spec.get("items") or []:
                if str(row.get("section") or "") in ("section_b", "section_c"):
                    vision_slots[str(row["id"])] = b64

    docx = args.docx.expanduser().resolve() if args.docx else None
    if docx is None and _DEFAULT_DOCX.is_file():
        docx = _DEFAULT_DOCX

    def progress(iid: str, _res: object) -> None:
        print(f"  reviewed {iid}")

    print(f"Solve review ({cfg.provider} / {cfg.model}) …")
    report = run_solve_review(
        spec,
        cfg=cfg,
        sync_tables=not args.sync_tables,
        item_ids=args.items,
        docx_path=docx,
        vision_slots=vision_slots,
        on_progress=progress,
    )
    save_solve_review(report, args.out)
    print(format_solve_review_report(report))
    print(f"Report: {args.out.expanduser().resolve()}")

    if args.merge_rules:
        rules = merge_solve_report_into_rules(report, load_generation_rules(args.rules))
        p = save_generation_rules(rules, args.rules)
        print(f"Generation rules: {p}")

    if args.save_spec:
        save_spec(spec_path, spec)

    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
