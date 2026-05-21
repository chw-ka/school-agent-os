"""Load pre-built DSE ICT question bank (avoid re-OCR)."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFAULT_BANK = REPO / "Subjects/DSE-ICT/question-bank"


def load_index(bank_root: Path | None = None) -> dict:
    root = (bank_root or DEFAULT_BANK).expanduser().resolve()
    path = root / "index.json"
    if not path.exists():
        return {"papers": [], "by_type": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def load_paper_spec(year_label: str, slug: str, *, bank_root: Path | None = None, prefer_refined: bool = False) -> dict | None:
    root = (bank_root or DEFAULT_BANK).expanduser().resolve()
    if prefer_refined:
        refined = root / year_label / slug / "questions_refined.json"
        if refined.exists():
            return json.loads(refined.read_text(encoding="utf-8"))
    path = root / year_label / slug / "questions.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_ocr_text(year_label: str, slug: str, *, bank_root: Path | None = None) -> str | None:
    root = (bank_root or DEFAULT_BANK).expanduser().resolve()
    path = root / year_label / slug / "ocr.txt"
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def collect_bank_text(
    years: list[str | int],
    slugs: list[str],
    *,
    bank_root: Path | None = None,
) -> str:
    """Concatenate cached OCR for style/terminology extraction."""
    chunks: list[str] = []
    for year in years:
        label = str(year)
        for slug in slugs:
            text = load_ocr_text(label, slug, bank_root=bank_root)
            if text and len(text.strip()) > 50:
                chunks.append(text)
    return "\n".join(chunks)
