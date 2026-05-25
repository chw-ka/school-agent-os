#!/usr/bin/env python3
"""Refine noisy OCR question extractions with an OpenAI-compatible LLM (cached JSON)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from dse_ict_llm_refine import (
    LlmConfig,
    build_refined_spec,
    default_content_pages,
    refine_from_text,
    refine_from_vision_pages,
    validate_refined_questions,
)
from dse_ict_naming import PAPER_LABELS, QUESTION_PAPERS, past_paper_pdf_path
from dse_ict_parser import parse_mcq_answers

REPO = Path(__file__).resolve().parents[2]
DEFAULT_BANK = REPO / "Subjects/DSE-ICT/question-bank"
DEFAULT_PAST = REPO / "Subjects/DSE-ICT/past-papers"


def _load_mcq_answers(bank_root: Path, year_label: str) -> dict[int, str]:
    ms_ocr = bank_root / year_label / "MarkingScheme" / "ocr.txt"
    if not ms_ocr.exists():
        return {}
    return parse_mcq_answers(ms_ocr.read_text(encoding="utf-8"), paper_id=f"{year_label}-MarkingScheme")


def _load_draft_questions(bank_root: Path, year_label: str, slug: str) -> list[dict]:
    draft_path = bank_root / year_label / slug / "questions.json"
    if not draft_path.exists():
        return []
    spec = json.loads(draft_path.read_text(encoding="utf-8"))
    return spec.get("paper", {}).get("questions") or []


def refine_paper(
    *,
    bank_root: Path,
    past_root: Path,
    year_label: str,
    slug: str,
    mode: str,
    force: bool,
    cfg: LlmConfig,
) -> Path | None:
    if slug not in QUESTION_PAPERS:
        print(f"  skip {slug}: not a question paper")
        return None

    out_dir = bank_root / year_label / slug
    out_path = out_dir / "questions_refined.json"
    if out_path.exists() and not force:
        print(f"  cached {out_path.relative_to(REPO)}")
        return out_path

    ocr_path = out_dir / "ocr.txt"
    if mode == "text" and not ocr_path.exists():
        print(f"  skip: missing {ocr_path.relative_to(REPO)} — run build_dse_ict_question_bank.py first")
        return None

    pdf_path = past_paper_pdf_path(past_root, year_label, slug)
    if mode == "vision" and not pdf_path.exists():
        print(f"  skip: missing PDF {pdf_path}")
        return None

    paper_label = PAPER_LABELS.get(slug, slug)
    draft = _load_draft_questions(bank_root, year_label, slug)
    mcq_answers = _load_mcq_answers(bank_root, year_label) if slug == "Paper1_MultipleChoice" else {}

    print(f"  refining {year_label}/{slug} via {mode} ({cfg.model}) ...")
    if mode == "vision":
        pages = default_content_pages(slug, pdf_path)
        ocr_by_page = {}
        if ocr_path.exists():
            # Best-effort: whole OCR blob has no page boundaries; vision relies on image.
            pass
        questions = refine_from_vision_pages(
            cfg=cfg,
            paper_label=paper_label,
            slug=slug,
            pdf_path=pdf_path,
            page_numbers=pages,
            mcq_answers=mcq_answers or None,
        )
    else:
        ocr_text = ocr_path.read_text(encoding="utf-8")
        questions = refine_from_text(
            cfg=cfg,
            paper_label=paper_label,
            slug=slug,
            ocr_text=ocr_text,
            draft_questions=draft,
            mcq_answers=mcq_answers or None,
        )

    validation = validate_refined_questions(questions, slug=slug, mcq_answers=mcq_answers or None)
    spec = build_refined_spec(
        year_label=year_label,
        slug=slug,
        paper_label=paper_label,
        source_pdf=pdf_path if pdf_path.exists() else out_dir / "ocr.txt",
        questions=questions,
        validation=validation,
        mode=mode,  # type: ignore[arg-type]
        model=cfg.model or "",
        provider=cfg.provider,
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")

    review = validation.get("needs_review_numbers") or []
    warnings = validation.get("warnings") or []
    print(f"  wrote {len(questions)} questions → {out_path.relative_to(REPO)}")
    if review:
        print(f"  needs_review: {review[:15]}{'…' if len(review) > 15 else ''}")
    for w in warnings:
        print(f"  warning: {w}")
    return out_path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bank", type=Path, default=DEFAULT_BANK)
    ap.add_argument("--past-papers", type=Path, default=DEFAULT_PAST)
    ap.add_argument("--years", nargs="+", required=True, help="e.g. 2019 2020 or Practice Sample")
    ap.add_argument("--slugs", nargs="+", help="Paper slugs; default = all question papers")
    ap.add_argument(
        "--mode",
        choices=["text", "vision"],
        default="text",
        help="text=OCR+LLM (cheap); vision=page images+LLM (best for 2-column MCQ scans)",
    )
    ap.add_argument("--force", action="store_true", help="Re-run LLM even if questions_refined.json exists")
    ap.add_argument(
        "--provider",
        choices=["gemini", "deepseek", "openai"],
        default=None,
        help="LLM provider (default: deepseek > gemini > openai from .env keys)",
    )
    ap.add_argument("--model", help="Override DSE_ICT_LLM_MODEL / default for mode")
    args = ap.parse_args(argv)

    cfg = LlmConfig.from_env(mode=args.mode, provider=args.provider)  # type: ignore[arg-type]
    if args.model:
        cfg.model = args.model

    bank_root = args.bank.expanduser().resolve()
    past_root = args.past_papers.expanduser().resolve()
    slugs = args.slugs or sorted(QUESTION_PAPERS)

    for year_label in args.years:
        for slug in slugs:
            try:
                refine_paper(
                    bank_root=bank_root,
                    past_root=past_root,
                    year_label=year_label,
                    slug=slug,
                    mode=args.mode,
                    force=args.force,
                    cfg=cfg,
                )
            except Exception as e:
                print(f"  error {year_label}/{slug}: {e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
