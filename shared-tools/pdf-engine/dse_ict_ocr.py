"""OCR HKDSE ICT scanned PDFs with on-disk cache (avoid re-OCR on every reference)."""
from __future__ import annotations

import json
import os
from pathlib import Path

import fitz
import numpy as np

from ocr_backends import DEFAULT_ENGINE, OcrEngineName, ocr_image_array, resolve_engine

# Higher scale helps question-number / MCQ option detection on scans.
DEFAULT_SCALE = 3.0
DEFAULT_PREPROCESS = True


def _page_to_array(page: fitz.Page, *, scale: float) -> np.ndarray:
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale))
    arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    if arr.shape[2] == 4:
        arr = arr[:, :, :3]
    return arr


def ocr_page(
    pdf_path: Path,
    page_no: int,
    *,
    scale: float = DEFAULT_SCALE,
    engine: OcrEngineName | str | None = None,
    preprocess: bool = DEFAULT_PREPROCESS,
    lang: str | None = None,
) -> str:
    doc = fitz.open(pdf_path)
    page = doc[page_no]
    arr = _page_to_array(page, scale=scale)
    return ocr_image_array(arr, engine=engine, preprocess=preprocess, lang=lang)


def ocr_pdf(
    pdf_path: Path,
    *,
    skip_first: int = 0,
    skip_last: int = 0,
    max_pages: int | None = None,
    scale: float = DEFAULT_SCALE,
    engine: OcrEngineName | str | None = None,
    preprocess: bool = DEFAULT_PREPROCESS,
    lang: str | None = None,
) -> tuple[str, list[str]]:
    """Return (full_text, page_texts)."""
    doc = fitz.open(pdf_path)
    start = min(skip_first, doc.page_count)
    end = doc.page_count - skip_last if skip_last else doc.page_count
    if max_pages is not None:
        end = min(end, start + max_pages)
    pages: list[str] = []
    for pn in range(start, end):
        pages.append(
            ocr_page(
                pdf_path,
                pn,
                scale=scale,
                engine=engine,
                preprocess=preprocess,
                lang=lang,
            )
        )
    return "\n\n".join(pages), pages


def default_skip_pages(slug: str) -> tuple[int, int, int | None]:
    """(skip_first, skip_last, max_pages) tuned per paper type."""
    if slug == "Paper1_MultipleChoice":
        return 2, 0, 14
    if slug == "Paper1B_CompulsoryStructured":
        return 2, 0, None
    if slug.startswith("Paper2"):
        return 2, 0, 10
    if slug == "MarkingScheme":
        return 0, 0, None
    if slug == "PerformanceReport":
        return 0, 0, 8
    return 1, 0, None


def _meta_path(cache_path: Path) -> Path:
    return cache_path.with_suffix(".meta.json")


def _cache_is_valid(
    meta_path: Path,
    pdf_path: Path,
    *,
    engine: OcrEngineName,
    scale: float,
    preprocess: bool,
) -> bool:
    if not meta_path.exists():
        return False
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    if meta.get("engine") != engine:
        return False
    if float(meta.get("scale", 0)) != scale:
        return False
    if bool(meta.get("preprocess", True)) != preprocess:
        return False
    try:
        pdf_mtime = pdf_path.stat().st_mtime
    except OSError:
        return False
    return meta.get("pdf_mtime") == pdf_mtime


def _write_cache_meta(
    meta_path: Path,
    pdf_path: Path,
    *,
    engine: OcrEngineName,
    scale: float,
    preprocess: bool,
) -> None:
    meta = {
        "engine": engine,
        "scale": scale,
        "preprocess": preprocess,
        "pdf_mtime": pdf_path.stat().st_mtime,
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def load_or_ocr(
    pdf_path: Path,
    cache_path: Path,
    *,
    slug: str,
    force: bool = False,
    scale: float = DEFAULT_SCALE,
    engine: OcrEngineName | str | None = None,
    preprocess: bool = DEFAULT_PREPROCESS,
    lang: str | None = None,
) -> str:
    cache_path = cache_path.expanduser().resolve()
    pdf_path = pdf_path.expanduser().resolve()
    engine_name = resolve_engine(engine)

    meta_path = _meta_path(cache_path)
    if (
        cache_path.exists()
        and not force
        and _cache_is_valid(meta_path, pdf_path, engine=engine_name, scale=scale, preprocess=preprocess)
    ):
        return cache_path.read_text(encoding="utf-8")

    skip_first, skip_last, max_pages = default_skip_pages(slug)
    text, _ = ocr_pdf(
        pdf_path,
        skip_first=skip_first,
        skip_last=skip_last,
        max_pages=max_pages,
        scale=scale,
        engine=engine_name,
        preprocess=preprocess,
        lang=lang,
    )
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(text, encoding="utf-8")
    _write_cache_meta(meta_path, pdf_path, engine=engine_name, scale=scale, preprocess=preprocess)
    return text
