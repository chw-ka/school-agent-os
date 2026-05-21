"""OCR HKDSE ICT scanned PDFs with on-disk cache (avoid re-OCR on every reference)."""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

import fitz

DEFAULT_LANG = "chi_tra+eng"
DEFAULT_SCALE = 2.2


def ocr_page(pdf_path: Path, page_no: int, *, scale: float = DEFAULT_SCALE, lang: str = DEFAULT_LANG) -> str:
    doc = fitz.open(pdf_path)
    page = doc[page_no]
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale))
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        img = Path(f.name)
    try:
        pix.save(str(img))
        try:
            r = subprocess.run(
                ["tesseract", str(img), "stdout", "-l", lang, "--psm", "6"],
                capture_output=True,
                text=True,
            )
        except FileNotFoundError as e:
            raise FileNotFoundError(
                "tesseract not found on PATH. Install Tesseract OCR with chi_tra+eng language data."
            ) from e
        return r.stdout if r.returncode == 0 else ""
    finally:
        img.unlink(missing_ok=True)


def ocr_pdf(
    pdf_path: Path,
    *,
    skip_first: int = 0,
    skip_last: int = 0,
    max_pages: int | None = None,
    scale: float = DEFAULT_SCALE,
    lang: str = DEFAULT_LANG,
) -> tuple[str, list[str]]:
    """Return (full_text, page_texts)."""
    doc = fitz.open(pdf_path)
    start = min(skip_first, doc.page_count)
    end = doc.page_count - skip_last if skip_last else doc.page_count
    if max_pages is not None:
        end = min(end, start + max_pages)
    pages: list[str] = []
    for pn in range(start, end):
        pages.append(ocr_page(pdf_path, pn, scale=scale, lang=lang))
    return "\n\n".join(pages), pages


def default_skip_pages(slug: str) -> tuple[int, int, int | None]:
    """(skip_first, skip_last, max_pages) tuned per paper type."""
    if slug == "Paper1_MultipleChoice":
        return 2, 0, 14
    if slug.startswith("Paper2"):
        return 2, 0, 10
    if slug == "MarkingScheme":
        return 0, 0, None
    if slug == "PerformanceReport":
        return 0, 0, 8
    return 1, 0, None


def load_or_ocr(
    pdf_path: Path,
    cache_path: Path,
    *,
    slug: str,
    force: bool = False,
    scale: float = DEFAULT_SCALE,
    lang: str = DEFAULT_LANG,
) -> str:
    cache_path = cache_path.expanduser().resolve()
    if cache_path.exists() and not force:
        return cache_path.read_text(encoding="utf-8")

    skip_first, skip_last, max_pages = default_skip_pages(slug)
    text, _ = ocr_pdf(
        pdf_path,
        skip_first=skip_first,
        skip_last=skip_last,
        max_pages=max_pages,
        scale=scale,
        lang=lang,
    )
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(text, encoding="utf-8")
    return text
