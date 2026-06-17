"""PaddleOCR helpers for S3 CMP answer-sheet cells (PaddleOCR 2.7 + numpy 1.x)."""
from __future__ import annotations

import re
from functools import lru_cache

import cv2
import fitz
import numpy as np
from paddleocr import PaddleOCR

from answer_sheet_align import (
    PageImage,
    crop_rgb,
    detect_fill_line_rois,
    detect_page2_regions,
    resolve_page2_regions,
    detect_sa_block_rois,
    detect_table_cells,
    resolve_bc_regions,
    find_markers,
    page_affine,
    render_page,
    warp_norm_box,
    _split_answer_row,
)


@lru_cache(maxsize=2)
def get_paddle(*, lang: str = "en") -> PaddleOCR:
    return PaddleOCR(use_angle_cls=lang == "en", lang=lang, show_log=False)


def ocr_letter_cell(cell: np.ndarray, *, alphabet: str = "ABCDE") -> str:
    from cell_letter_ocr import read_match_letter, read_tf_letter

    if alphabet == "TF":
        return read_tf_letter(cell)
    return read_match_letter(cell)


def read_letter_grid_from_image(
    table_img: np.ndarray,
    *,
    rows: int,
    cols: int = 5,
    alphabet: str = "ABCDE",
) -> list[str]:
    """OCR a table block; prefer line-detected cells, else equal split."""
    cells = detect_table_cells(table_img, rows=rows, cols=cols, label_cols=0)
    if cells:
        return [
            "".join(ocr_letter_cell(c, alphabet=alphabet) for c in row) for row in cells
        ]

    h, w = table_img.shape[:2]
    row_h = h // rows
    slot_w = w // (cols + 1)
    out: list[str] = []
    for r in range(rows):
        row = table_img[r * row_h : (r + 1) * row_h]
        letters = [
            ocr_letter_cell(row[:, (i + 1) * slot_w : (i + 2) * slot_w], alphabet=alphabet)
            for i in range(cols)
        ]
        out.append("".join(letters))
    return out


def read_table_on_page(
    page_img: PageImage,
    box_norm: tuple[float, float, float, float],
    *,
    rows: int,
    cols: int = 5,
    affine: np.ndarray | None = None,
    alphabet: str = "ABCDE",
) -> list[str]:
    box_px = warp_norm_box(box_norm, page_img, affine)
    table = crop_rgb(page_img, box_px)
    return read_letter_grid_from_image(table, rows=rows, cols=cols, alphabet=alphabet)


def read_bc_tables_on_page(
    page_img: PageImage,
    *,
    layout_p1: dict | None = None,
) -> tuple[list[str], str, str]:
    """
    OCR 乙部 (2 rows) + 丙部 (1 row).
    Returns (match_rows, tf_row, method).
    """
    regions = resolve_bc_regions(page_img, layout_p1)
    if regions is None:
        return [], "", "fallback"
    match_out: list[str] = []
    if regions.match_cell_boxes:
        for row_cells in regions.match_cell_boxes:
            match_out.append(
                "".join(ocr_letter_cell(crop_rgb(page_img, box)) for box in row_cells)
            )
    else:
        for row_box in regions.match_rows:
            row_img = crop_rgb(page_img, row_box)
            cells = _split_answer_row(row_img)
            match_out.append("".join(ocr_letter_cell(c) for c in cells))
    if regions.tf_cell_boxes:
        tf = "".join(
            ocr_letter_cell(crop_rgb(page_img, box), alphabet="TF")
            for box in regions.tf_cell_boxes
        )
    else:
        tf_img = crop_rgb(page_img, regions.tf_row)
        tf_cells = _split_answer_row(tf_img)
        tf = "".join(ocr_letter_cell(c, alphabet="TF") for c in tf_cells)
    return match_out, tf, regions.method


def _fill_answer_roi(img: np.ndarray) -> np.ndarray:
    """Skip printed (a)–(e) label; keep handwritten answer zone."""
    if img.size == 0:
        return img
    h, w = img.shape[:2]
    return img[:, int(w * 0.12) :]


def ocr_fill_image(img: np.ndarray) -> str:
    if img.size == 0:
        return ""
    roi = _fill_answer_roi(img)
    ocr = get_paddle(lang="en")
    result = ocr.ocr(roi, cls=False)
    if not result or not result[0]:
        return ""
    parts = [line[1][0] for line in result[0]]
    text = " ".join(parts)
    return re.sub(r"^\s*\([a-e]\)\s*", "", text, flags=re.I).strip()


def ocr_text_image(img: np.ndarray) -> str:
    if img.size == 0:
        return ""
    ocr = get_paddle(lang="chinese_cht")
    result = ocr.ocr(img, cls=False)
    if not result or not result[0]:
        return ""
    return " ".join(line[1][0] for line in result[0]).strip()


def read_fill_lines_on_page(
    page_img: PageImage,
    line_boxes_norm: list[tuple[float, float, float, float]],
    *,
    affine: np.ndarray | None = None,
) -> list[str]:
    """Read fill lines; try line detection first, fall back to warped template boxes."""
    auto = detect_fill_line_rois(page_img.rgb, expected=len(line_boxes_norm))
    if auto and len(auto) >= len(line_boxes_norm):
        return [ocr_fill_image(crop_rgb(page_img, b)) for b in auto[: len(line_boxes_norm)]]

    out: list[str] = []
    for box in line_boxes_norm:
        px = warp_norm_box(box, page_img, affine)
        out.append(ocr_fill_image(crop_rgb(page_img, px)))
    return out


def read_sa_blocks_on_page(
    page_img: PageImage,
    boxes_norm: list[tuple[float, float, float, float]],
    *,
    affine: np.ndarray | None = None,
    layout_p2: dict | None = None,
) -> list[str]:
    p2 = resolve_page2_regions(page_img, layout_p2)
    if p2 and len(p2.sa_boxes) >= len(boxes_norm):
        return [ocr_text_image(crop_rgb(page_img, b)) for b in p2.sa_boxes[: len(boxes_norm)]]

    auto = detect_sa_block_rois(page_img.rgb, expected=len(boxes_norm))
    if auto and len(auto) >= len(boxes_norm):
        return [ocr_text_image(crop_rgb(page_img, b)) for b in auto[: len(boxes_norm)]]

    out: list[str] = []
    for box in boxes_norm:
        px = warp_norm_box(box, page_img, affine)
        out.append(ocr_text_image(crop_rgb(page_img, px)))
    return out


# Legacy helpers (fixed crop without alignment) — kept for debug scripts
def clip_page(page: fitz.Page, box: tuple[float, float, float, float], scale: float = 5.0) -> np.ndarray:
    page_img = render_page(page, scale=scale)
    from answer_sheet_align import norm_box_to_px

    x0, y0, x1, y1 = norm_box_to_px(box, page_img.width, page_img.height)
    return crop_rgb(page_img, (x0, y0, x1, y1))
