#!/usr/bin/env python3
"""Build cached HKDSE ICT question bank from scanned PDFs (OCR once, reuse JSON)."""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from dse_ict_naming import (
    FOLDER_ALIASES,
    PAPER_LABELS,
    PAPER_SLUGS,
    QUESTION_PAPERS,
    descriptive_pdf_name,
    paper_slug_from_name,
    rename_past_papers,
)
from dse_ict_ocr import load_or_ocr
from dse_ict_parser import (
    build_paper_spec,
    parse_mcq_answers,
    parse_mcq_questions,
    parse_written_questions,
    text_to_lines,
)

REPO = Path(__file__).resolve().parents[2]
DEFAULT_PAST = REPO / "Subjects/DSE-ICT/past-papers"
DEFAULT_BANK = REPO / "Subjects/DSE-ICT/question-bank"


def _iter_paper_pdfs(root: Path) -> list[tuple[str, str, Path]]:
    """Yield (year_label, slug, pdf_path) for question/marking PDFs."""
    out: list[tuple[str, str, Path]] = []
    for folder in sorted(root.iterdir()):
        if not folder.is_dir():
            continue
        name = folder.name
        if re.fullmatch(r"\d{4}", name):
            year_label = name
        elif name == "Practice-Paper":
            year_label = "Practice"
        elif name == "Sample-Paper":
            year_label = "Sample"
        else:
            continue
        for pdf in sorted(folder.glob("DSE_ICT_*.pdf")):
            slug = paper_slug_from_name(pdf.name)
            if slug:
                out.append((year_label, slug, pdf))
        # Also pick up not-yet-renamed legacy names
        for legacy, slug in PAPER_SLUGS.items():
            pdf = folder / legacy
            if pdf.exists():
                out.append((year_label, slug, pdf))
    return out


def _bank_paths(bank_root: Path, year_label: str, slug: str) -> tuple[Path, Path, Path]:
    base = bank_root / year_label / slug
    return base / "questions.json", base / "ocr.txt", base


def process_paper(
    *,
    year_label: str,
    slug: str,
    pdf_path: Path,
    bank_root: Path,
    force: bool = False,
    skip_ocr: bool = False,
    ocr_engine: str | None = None,
    ocr_preprocess: bool = True,
) -> dict | None:
    spec_path, ocr_path, out_dir = _bank_paths(bank_root, year_label, slug)
    if spec_path.exists() and not force and not skip_ocr:
        return json.loads(spec_path.read_text(encoding="utf-8"))

    paper_label = PAPER_LABELS.get(slug, slug)
    paper_id = f"{year_label}-{slug}"

    if skip_ocr and not ocr_path.exists():
        return None

    if slug in QUESTION_PAPERS or slug == "MarkingScheme":
        if skip_ocr:
            text = ocr_path.read_text(encoding="utf-8")
        else:
            text = load_or_ocr(
                pdf_path,
                ocr_path,
                slug=slug,
                force=force,
                engine=ocr_engine,
                preprocess=ocr_preprocess,
            )
    else:
        # Performance report — skip question extraction
        return None

    lines = text_to_lines(text)
    if slug == "Paper1_MultipleChoice":
        questions = parse_mcq_questions(lines, paper_id=paper_id)
    elif slug == "MarkingScheme":
        questions = []
        answers = parse_mcq_answers(text, paper_id=paper_id)
        spec = {
            "version": 1,
            "meta": {
                "source": "dse-ict-question-bank",
                "year_label": year_label,
                "paper_slug": slug,
                "paper_label": paper_label,
                "source_pdf": str(pdf_path).replace("\\", "/"),
                "ocr_cache": str(ocr_path).replace("\\", "/"),
            },
            "items": [],
            "paper": {"id": paper_id, "mcq_answers": answers},
        }
        out_dir.mkdir(parents=True, exist_ok=True)
        spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
        return spec
    else:
        questions = parse_written_questions(lines, paper_id=paper_id)

    spec = build_paper_spec(
        year_label=year_label,
        slug=slug,
        paper_label=paper_label,
        source_pdf=pdf_path,
        questions=questions,
        ocr_path=ocr_path if ocr_path.exists() else None,
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    return spec


def _merge_mcq_answers(bank_root: Path) -> None:
    """Copy MCQ keys from MarkingScheme into Paper1 question specs."""
    for year_dir in bank_root.iterdir():
        if not year_dir.is_dir() or year_dir.name == "index.json":
            continue
        ms_path = year_dir / "MarkingScheme" / "questions.json"
        p1_path = year_dir / "Paper1_MultipleChoice" / "questions.json"
        if not ms_path.exists() or not p1_path.exists():
            continue
        ms = json.loads(ms_path.read_text(encoding="utf-8"))
        answers = ms.get("paper", {}).get("mcq_answers") or {}
        if not answers:
            continue
        p1 = json.loads(p1_path.read_text(encoding="utf-8"))
        changed = False
        for item in p1.get("items", []):
            num = item.get("number")
            if num and num in answers:
                item["answer"] = answers[num]
                changed = True
        for q in p1.get("paper", {}).get("questions", []):
            num = q.get("number")
            if num and num in answers:
                q["answer"] = answers[num]
                changed = True
        if changed:
            p1_path.write_text(json.dumps(p1, ensure_ascii=False, indent=2), encoding="utf-8")


def build_index(bank_root: Path, past_root: Path) -> dict:
    entries: list[dict] = []
    by_type: dict[str, list[str]] = {}

    for year_label, slug, pdf_path in _iter_paper_pdfs(past_root):
        spec_path, ocr_path, _ = _bank_paths(bank_root, year_label, slug)
        entry = {
            "year_label": year_label,
            "paper_slug": slug,
            "paper_label": PAPER_LABELS.get(slug, slug),
            "pdf": str(pdf_path.relative_to(REPO)).replace("\\", "/"),
            "questions_json": str(spec_path.relative_to(REPO)).replace("\\", "/")
            if spec_path.exists()
            else None,
            "ocr_cache": str(ocr_path.relative_to(REPO)).replace("\\", "/")
            if ocr_path.exists()
            else None,
        }
        entries.append(entry)
        if spec_path.exists() and slug in QUESTION_PAPERS:
            try:
                spec = json.loads(spec_path.read_text(encoding="utf-8"))
                for q in spec.get("paper", {}).get("questions", []):
                    by_type.setdefault(q["type"], []).append(q["id"])
            except json.JSONDecodeError:
                pass

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "past_papers_root": str(past_root.relative_to(REPO)).replace("\\", "/"),
        "question_bank_root": str(bank_root.relative_to(REPO)).replace("\\", "/"),
        "papers": entries,
        "by_type": {k: sorted(v) for k, v in sorted(by_type.items())},
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--past-papers", type=Path, default=DEFAULT_PAST)
    ap.add_argument("--bank", type=Path, default=DEFAULT_BANK)
    ap.add_argument("--rename-only", action="store_true", help="Rename legacy PDFs/folders only")
    ap.add_argument("--years", nargs="*", help="Limit to year labels e.g. 2019 2020 or Practice Sample")
    ap.add_argument("--slugs", nargs="*", help="Limit to paper slugs e.g. Paper1_MultipleChoice")
    ap.add_argument("--force", action="store_true", help="Re-OCR and rebuild JSON")
    ap.add_argument(
        "--ocr",
        choices=["paddle", "tesseract"],
        default=None,
        help="OCR engine (default: paddle, or env DSE_ICT_OCR_ENGINE)",
    )
    ap.add_argument(
        "--no-preprocess",
        action="store_true",
        help="Skip scan denoise/contrast step before OCR",
    )
    ap.add_argument("--skip-ocr", action="store_true", help="Rebuild JSON from existing ocr.txt only")
    ap.add_argument("--index-only", action="store_true", help="Only refresh question-bank/index.json")
    args = ap.parse_args(argv)

    past_root = args.past_papers.expanduser().resolve()
    bank_root = args.bank.expanduser().resolve()

    if args.rename_only:
        moves = rename_past_papers(past_root)
        for src, dst in moves:
            print(f"Renamed: {src.name} -> {dst}")
        print(f"Done ({len(moves)} renames).")
        return 0

    papers = _iter_paper_pdfs(past_root)
    if args.years:
        allowed = set(args.years)
        papers = [p for p in papers if p[0] in allowed]
    if args.slugs:
        allowed_slugs = set(args.slugs)
        papers = [p for p in papers if p[1] in allowed_slugs]

    if not args.index_only:
        for year_label, slug, pdf_path in papers:
            if slug == "PerformanceReport":
                continue
            print(f"Processing {year_label} / {slug} ...")
            try:
                process_paper(
                    year_label=year_label,
                    slug=slug,
                    pdf_path=pdf_path,
                    bank_root=bank_root,
                    force=args.force,
                    skip_ocr=args.skip_ocr,
                    ocr_engine=args.ocr,
                    ocr_preprocess=not args.no_preprocess,
                )
            except FileNotFoundError as e:
                print(f"  skip: {e}")
            except Exception as e:
                print(f"  error: {e}")

    index = build_index(bank_root, past_root)
    bank_root.mkdir(parents=True, exist_ok=True)
    _merge_mcq_answers(bank_root)
    index = build_index(bank_root, past_root)
    index_path = bank_root / "index.json"
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {index_path} ({len(index['papers'])} papers catalogued)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
