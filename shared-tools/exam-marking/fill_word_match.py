"""Fuzzy match 丁部 fill-in answers against fixed word banks."""
from __future__ import annotations

import re

from rapidfuzz import fuzz

FILL_MATCH_THRESHOLD = 72


def normalize_fill(text: str) -> str:
    return re.sub(r"\s+", "", text).lower()


def match_fill_word(
    ocr_text: str,
    word_bank: list[str],
    *,
    threshold: int = FILL_MATCH_THRESHOLD,
) -> tuple[str, int, str]:
    """
    Map OCR text to the closest word-bank entry.
    Returns (matched_word, score, raw_ocr).
    """
    raw = (ocr_text or "").strip()
    norm = normalize_fill(raw)
    if not norm:
        return "", 0, raw

    bank_norm = {normalize_fill(w): w for w in word_bank}
    if norm in bank_norm:
        return bank_norm[norm], 100, raw

    best_word, best_score = "", 0
    for wn, original in bank_norm.items():
        score = max(
            fuzz.ratio(norm, wn),
            fuzz.partial_ratio(norm, wn),
            fuzz.WRatio(norm, wn),
        )
        if score > best_score:
            best_word, best_score = original, int(score)

    if best_score >= threshold:
        return best_word, best_score, raw
    return "", best_score, raw
