"""Lightweight scan preprocessing before OCR (exam PDFs from scanners)."""
from __future__ import annotations

import numpy as np

try:
    import cv2
except ImportError:  # pragma: no cover - optional at import, required for OCR build
    cv2 = None  # type: ignore[assignment]


def preprocess_scan(arr: np.ndarray) -> np.ndarray:
    """Denoise + local contrast; keeps 3-channel RGB for OCR backends."""
    if cv2 is None:
        raise ImportError(
            "opencv-python-headless is required for scan preprocessing. "
            "Install OCR extras: pip install -r requirements-ocr.txt"
        )
    if arr.ndim == 2:
        gray = arr
    else:
        gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    gray = cv2.fastNlMeansDenoising(gray, h=8)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
