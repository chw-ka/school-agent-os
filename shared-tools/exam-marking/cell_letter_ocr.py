"""Single-character OCR for 乙/丙 table cells (handwritten A–E or T/F only)."""
from __future__ import annotations

import re
from functools import lru_cache

import cv2
import numpy as np
from rapidfuzz import fuzz, process

MATCH_ALPHABET = "ABCDE"
TF_ALPHABET = "TF"
_TEMPLATE_SIZE = 64
_TEMPLATE_MIN_SCORE = 0.48


def _gray(cell: np.ndarray) -> np.ndarray:
    if cell.ndim == 3:
        return cv2.cvtColor(cell, cv2.COLOR_RGB2GRAY)
    return cell


def _inner_cell(cell: np.ndarray, *, margin_frac: float = 0.08) -> np.ndarray:
    """Drop table grid lines at cell borders."""
    if cell.size == 0:
        return cell
    h, w = cell.shape[:2]
    mx, my = max(1, int(w * margin_frac)), max(1, int(h * margin_frac))
    if w <= 2 * mx or h <= 2 * my:
        return cell
    return cell[my : h - my, mx : w - mx]


def _binarize_ink(gray: np.ndarray) -> np.ndarray:
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    adapt = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 4
    )
    _, light = cv2.threshold(gray, 145, 255, cv2.THRESH_BINARY_INV)
    return cv2.bitwise_or(cv2.bitwise_or(otsu, adapt), light)


def _ink_search_zone(zone: np.ndarray) -> tuple[np.ndarray, int]:
    """Drop printed (a)–(e) column on the left before blob detection."""
    h, w = zone.shape[:2]
    x0 = int(w * 0.20)
    return zone[:, x0:], x0


def _answer_zone(inner: np.ndarray, *, x_start: float = 0.32) -> np.ndarray:
    h, w = inner.shape[:2]
    return inner[:, int(w * x_start) : int(w * 0.94)]


def _rank_blobs(zone: np.ndarray, blobs: list[tuple[int, int, int, int, int]]) -> list[tuple[int, int, int, int, int]]:
    """Prefer centre-right ink (handwriting) over left-edge label punctuation."""
    h, w = zone.shape[:2]
    ranked: list[tuple[float, tuple[int, int, int, int, int]]] = []
    for area, x, y, cw, ch in blobs:
        cx = x + cw / 2
        if cx < w * 0.18 and area < w * h * 0.12:
            continue
        pos = 0.35 + 0.65 * (cx / max(w, 1))
        ranked.append((area * pos, (area, x, y, cw, ch)))
    ranked.sort(key=lambda t: t[0], reverse=True)
    return [b for _, b in ranked]


def _answer_blobs(zone: np.ndarray) -> list[tuple[int, int, int, int, int]]:
    if zone.size == 0:
        return []
    search, x_off = _ink_search_zone(zone)
    gray = _gray(search)
    h, w = gray.shape
    bw = _binarize_ink(gray)
    cnts, _ = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_area = max(18, int(h * w * 0.004))
    blobs: list[tuple[int, int, int, int, int]] = []
    for c in cnts:
        area = int(cv2.contourArea(c))
        if area < min_area:
            continue
        x, y, cw, ch = cv2.boundingRect(c)
        aspect = cw / max(ch, 1)
        if aspect > 10 or aspect < 0.08:
            continue
        if cw > w * 0.92 or ch > h * 0.92:
            continue
        blobs.append((area, x + x_off, y, cw, ch))
    blobs.sort(key=lambda b: b[0], reverse=True)
    return _rank_blobs(zone, blobs)


def ink_answer_roi(cell: np.ndarray) -> np.ndarray:
    """Largest handwritten ink blob in the answer column (right of printed label)."""
    if cell.size == 0:
        return cell
    inner = _inner_cell(cell)
    for x_start in (0.32, 0.40, 0.48):
        zone = _answer_zone(inner, x_start=x_start)
        blobs = _answer_blobs(zone)
        if blobs:
            _, x, y, cw, ch = blobs[0]
            pad = max(2, min(cw, ch) // 3)
            y0, y1 = max(0, y - pad), min(zone.shape[0], y + ch + pad)
            x0, x1 = max(0, x - pad), min(zone.shape[1], x + cw + pad)
            return zone[y0:y1, x0:x1]
    return _answer_zone(inner, x_start=0.40)


def _norm_glyph(roi: np.ndarray, *, size: int = _TEMPLATE_SIZE) -> np.ndarray:
    gray = _gray(roi)
    bw = _binarize_ink(gray)
    pts = cv2.findNonZero(bw)
    if pts is None:
        return np.zeros((size, size), dtype=np.uint8)
    x, y, w, h = cv2.boundingRect(pts)
    crop = bw[y : y + h, x : x + w]
    side = max(w, h, 1)
    sq = np.zeros((side, side), dtype=np.uint8)
    ox, oy = (side - w) // 2, (side - h) // 2
    sq[oy : oy + h, ox : ox + w] = crop
    return cv2.resize(sq, (size, size), interpolation=cv2.INTER_AREA)


@lru_cache(maxsize=1)
def _letter_templates(size: int = _TEMPLATE_SIZE) -> dict[str, np.ndarray]:
    templates: dict[str, np.ndarray] = {}
    for ch in "ABCDEFT":
        canvas = np.full((size, size), 255, dtype=np.uint8)
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 1.9 if ch in "EF" else 2.1
        thickness = 2
        (tw, th), _ = cv2.getTextSize(ch, font, scale, thickness)
        org = ((size - tw) // 2, (size + th) // 2)
        cv2.putText(canvas, ch, org, font, scale, 0, thickness, cv2.LINE_AA)
        templates[ch] = 255 - canvas
    return templates


def _template_match_letter(roi: np.ndarray, alphabet: str) -> tuple[str, float]:
    glyph = _norm_glyph(roi)
    if int(glyph.sum()) < 400:
        return "", 0.0
    templates = _letter_templates()
    scores: dict[str, float] = {}
    for ch in alphabet:
        tmpl = templates.get(ch)
        if tmpl is None:
            continue
        res = cv2.matchTemplate(glyph, tmpl, cv2.TM_CCOEFF_NORMED)
        scores[ch] = float(res.max())
    if not scores:
        return "", 0.0
    best = max(scores, key=scores.get)
    return best, scores[best]


def _prep_char_canvas(roi: np.ndarray, *, scale: int = 10) -> np.ndarray:
    gray = _gray(roi)
    gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    pad = 80
    canvas = np.full((bw.shape[0] + pad * 2, bw.shape[1] + pad * 2), 255, dtype=np.uint8)
    canvas[pad : pad + bw.shape[0], pad : pad + bw.shape[1]] = bw
    return cv2.cvtColor(canvas, cv2.COLOR_GRAY2RGB)


@lru_cache(maxsize=1)
def _paddle_en():
    from paddle_cell_ocr import get_paddle

    return get_paddle(lang="en")


def _ocr_char_canvas(canvas: np.ndarray) -> str:
    ocr = _paddle_en()
    for det in (False, True):
        result = ocr.ocr(canvas, det=det, cls=False)
        if not result or not result[0]:
            continue
        parts = []
        for item in result[0]:
            parts.append(item[1][0] if det else item[0])
        if parts:
            return "".join(parts)
    return ""


def _ocr_roi(roi: np.ndarray) -> list[str]:
    guesses: list[str] = []
    for scale in (8, 10, 12):
        raw = _ocr_char_canvas(_prep_char_canvas(roi, scale=scale))
        if raw:
            guesses.append(raw)
    return guesses


def _fuzzy_letter(guess: str, alphabet: str) -> str:
    guess = re.sub(r"[^A-Za-z0-9]", "", guess).upper()
    if not guess:
        return ""
    for ch in guess:
        if ch in alphabet:
            return ch
    aliases_ab = {"O": "D", "0": "D", "1": "E", "I": "E", "L": "E", "S": "D"}
    aliases_tf = {"1": "T", "I": "T", "L": "T", "7": "T", "P": "F", "E": "F"}
    aliases = aliases_tf if alphabet == TF_ALPHABET else aliases_ab
    for ch in guess:
        if ch in aliases and aliases[ch] in alphabet:
            return aliases[ch]
    hit = process.extractOne(guess, list(alphabet), scorer=fuzz.ratio)
    if hit and hit[1] >= 50:
        return hit[0]
    return ""


def read_single_letter(cell: np.ndarray, *, alphabet: str = MATCH_ALPHABET) -> str:
    """Read one handwritten letter from a table cell; ignore printed (a)–(e)."""
    if cell.size == 0:
        return ""
    inner = _inner_cell(cell)
    candidates: list[str] = []

    for x_start in (0.30, 0.38, 0.46):
        zone = _answer_zone(inner, x_start=x_start)
        for _, x, y, cw, ch in _answer_blobs(zone)[:2]:
            pad = max(2, min(cw, ch) // 3)
            y0, y1 = max(0, y - pad), min(zone.shape[0], y + ch + pad)
            x0, x1 = max(0, x - pad), min(zone.shape[1], x + cw + pad)
            blob = zone[y0:y1, x0:x1]
            for raw in _ocr_roi(blob):
                letter = _fuzzy_letter(raw, alphabet)
                if letter:
                    candidates.append(letter)
        for raw in _ocr_roi(zone):
            letter = _fuzzy_letter(raw, alphabet)
            if letter:
                candidates.append(letter)

    roi = ink_answer_roi(cell)
    tmpl_letter, tmpl_score = _template_match_letter(roi, alphabet)
    if tmpl_score >= _TEMPLATE_MIN_SCORE:
        candidates.append(tmpl_letter)

    candidates = [c for c in candidates if c in alphabet]
    if not candidates:
        return tmpl_letter if tmpl_score >= 0.35 else ""
    return max(set(candidates), key=candidates.count)


def read_match_letter(cell: np.ndarray) -> str:
    return read_single_letter(cell, alphabet=MATCH_ALPHABET)


def read_tf_letter(cell: np.ndarray) -> str:
    return read_single_letter(cell, alphabet=TF_ALPHABET)
