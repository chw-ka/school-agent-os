"""Pluggable OCR backends for scanned HK exam PDFs."""
from __future__ import annotations

import os
import subprocess
import tempfile
from abc import ABC, abstractmethod
from functools import lru_cache
from pathlib import Path
from typing import Literal

import numpy as np

from ocr_preprocess import preprocess_scan

OcrEngineName = Literal["paddle", "tesseract"]

DEFAULT_ENGINE: OcrEngineName = os.environ.get("DSE_ICT_OCR_ENGINE", "paddle")  # type: ignore[assignment]
if DEFAULT_ENGINE not in ("paddle", "tesseract"):
    DEFAULT_ENGINE = "paddle"


def resolve_engine(name: str | None) -> OcrEngineName:
    engine = (name or DEFAULT_ENGINE).strip().lower()
    if engine not in ("paddle", "tesseract"):
        raise ValueError(f"Unknown OCR engine {name!r}. Choose paddle or tesseract.")
    return engine  # type: ignore[return-value]


def _sort_boxes_reading_order(items: list) -> list:
    def key(item):
        box = item[0]
        ys = [p[1] for p in box]
        xs = [p[0] for p in box]
        return (min(ys), min(xs))

    return sorted(items, key=key)


def _box_center_y(box: list) -> float:
    return sum(p[1] for p in box) / len(box)


def _boxes_to_lines(items: list, *, y_threshold: float = 18.0) -> list[str]:
    """Merge detection boxes on the same visual row (helps MCQ A./B./C./D.)."""
    if not items:
        return []
    sorted_items = _sort_boxes_reading_order(items)
    lines: list[str] = []
    row: list[tuple[list, str]] = []
    row_y: float | None = None

    for box, (text, _conf) in ((it[0], it[1]) for it in sorted_items):
        t = text.strip()
        if not t:
            continue
        cy = _box_center_y(box)
        if row_y is None or abs(cy - row_y) <= y_threshold:
            row.append((box, t))
            row_y = cy if row_y is None else (row_y + cy) / 2
            continue
        row.sort(key=lambda pair: min(p[0] for p in pair[0]))
        lines.append(" ".join(t for _, t in row))
        row = [(box, t)]
        row_y = cy

    if row:
        row.sort(key=lambda pair: min(p[0] for p in pair[0]))
        lines.append(" ".join(t for _, t in row))
    return lines


class OcrBackend(ABC):
    name: OcrEngineName

    @abstractmethod
    def ocr_image(self, arr: np.ndarray) -> str:
        """Return plain text for one page image (RGB uint8 array)."""


class PaddleBackend(OcrBackend):
    name = "paddle"

    def __init__(self, *, lang: str = "chinese_cht") -> None:
        self.lang = lang
        self._ocr = _get_paddle_reader(lang)

    def ocr_image(self, arr: np.ndarray) -> str:
        result = self._ocr.ocr(arr, cls=True)
        if not result or not result[0]:
            return ""
        lines = _boxes_to_lines(result[0])
        return "\n".join(lines)


class TesseractBackend(OcrBackend):
    name = "tesseract"

    def __init__(self, *, lang: str = "chi_tra+eng", psm: int = 6) -> None:
        self.lang = lang
        self.psm = psm

    def ocr_image(self, arr: np.ndarray) -> str:
        try:
            import cv2
        except ImportError as e:
            raise ImportError("opencv-python-headless required to write temp images for Tesseract") from e

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            img = Path(f.name)
        try:
            cv2.imwrite(str(img), cv2.cvtColor(arr, cv2.COLOR_RGB2BGR))
            try:
                r = subprocess.run(
                    ["tesseract", str(img), "stdout", "-l", self.lang, "--psm", str(self.psm)],
                    capture_output=True,
                    text=True,
                )
            except FileNotFoundError as e:
                raise FileNotFoundError(
                    "tesseract not found on PATH. Install Tesseract with chi_tra+eng, "
                    "or use --ocr paddle (recommended for scanned papers)."
                ) from e
            return r.stdout if r.returncode == 0 else ""
        finally:
            img.unlink(missing_ok=True)


@lru_cache(maxsize=2)
def _get_paddle_reader(lang: str):
    try:
        from paddleocr import PaddleOCR
    except ImportError as e:
        raise ImportError(
            "PaddleOCR not installed. For scanned DSE papers run:\n"
            "  pip install -r requirements-ocr.txt"
        ) from e
    return PaddleOCR(use_angle_cls=True, lang=lang, show_log=False)


@lru_cache(maxsize=4)
def get_backend(engine: OcrEngineName, *, lang: str | None = None) -> OcrBackend:
    if engine == "paddle":
        return PaddleBackend(lang=lang or "chinese_cht")
    return TesseractBackend(lang=lang or "chi_tra+eng")


def ocr_image_array(
    arr: np.ndarray,
    *,
    engine: OcrEngineName | str | None = None,
    preprocess: bool = True,
    lang: str | None = None,
) -> str:
    backend = get_backend(resolve_engine(engine), lang=lang)
    img = preprocess_scan(arr) if preprocess else arr
    return backend.ocr_image(img)
