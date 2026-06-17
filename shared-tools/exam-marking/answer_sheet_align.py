"""Per-page alignment for scanned S3 CMP answer sheets (translation + scale from fiducials)."""
from __future__ import annotations

from dataclasses import dataclass

import cv2
import fitz
import numpy as np

# Reference marker centres on a nominal page (scale=2 render of A4), order: TL TR BR BL
# Calibrated from SKM_C750i26061513350_reordered.pdf student 0 page 1.
REF_MARKERS_SCALE2 = np.float32(
    [
        [486, 546],  # TL
        [729, 508],  # TR
        [575, 899],  # BR
        [486, 939],  # BL
    ]
)

RENDER_SCALE = 2.0


@dataclass
class PageImage:
    page: fitz.Page
    scale: float
    rgb: np.ndarray
    gray: np.ndarray

    @property
    def height(self) -> int:
        return self.rgb.shape[0]

    @property
    def width(self) -> int:
        return self.rgb.shape[1]


def render_page(page: fitz.Page, scale: float = RENDER_SCALE) -> PageImage:
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale))
    rgb = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    return PageImage(page=page, scale=scale, rgb=rgb, gray=gray)


def _square_candidates(gray: np.ndarray) -> list[tuple[float, float, float]]:
    """Return (cx, cy, score) for dark square fiducials."""
    _, bw = cv2.threshold(gray, 90, 255, cv2.THRESH_BINARY_INV)
    cnts, _ = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    out: list[tuple[float, float, float]] = []
    h, w = gray.shape
    for c in cnts:
        x, y, cw, ch = cv2.boundingRect(c)
        area = cw * ch
        if area < 400 or area > 12_000:
            continue
        if cw < 14 or ch < 14:
            continue
        ratio = cw / ch
        if ratio < 0.65 or ratio > 1.45:
            continue
        # MC registration marks sit in central band
        cx, cy = x + cw / 2, y + ch / 2
        if cy < h * 0.18 or cy > h * 0.72:
            continue
        if cx < w * 0.28 or cx > w * 0.88:
            continue
        out.append((cx, cy, float(area)))
    return out


def find_markers(gray: np.ndarray) -> np.ndarray | None:
    """Find 4 ZipGrade-style corner marks; return TL,TR,BR,BL or None."""
    cands = _square_candidates(gray)
    if len(cands) < 4:
        return None
    pts = np.float32([(x, y) for x, y, _ in cands])
    # Pick extremes: min x+y ~TL, max x-y ~TR, max x+y ~BR, min x-y ~BL
    s = pts[:, 0] + pts[:, 1]
    d = pts[:, 0] - pts[:, 1]
    tl = pts[int(np.argmin(s))]
    br = pts[int(np.argmax(s))]
    tr = pts[int(np.argmax(d))]
    bl = pts[int(np.argmin(d))]
    ordered = np.float32([tl, tr, br, bl])
    # Sanity: reasonable spread
    w = float(np.linalg.norm(tr - tl))
    h = float(np.linalg.norm(bl - tl))
    if w < 80 or h < 120:
        return None
    return ordered


def marker_affine(cur: np.ndarray, ref: np.ndarray | None = None) -> np.ndarray:
    """2x3 affine mapping ref template coords -> current page coords."""
    ref = ref if ref is not None else REF_MARKERS_SCALE2
    return cv2.estimateAffinePartial2D(ref, cur, method=cv2.RANSAC)[0]


def norm_box_to_px(
    box: tuple[float, float, float, float],
    page_w: int,
    page_h: int,
) -> tuple[int, int, int, int]:
    x0, y0, x1, y1 = box
    return (
        int(x0 * page_w),
        int(y0 * page_h),
        int(x1 * page_w),
        int(y1 * page_h),
    )


def warp_norm_box(
    box: tuple[float, float, float, float],
    page: PageImage,
    affine: np.ndarray | None,
) -> tuple[int, int, int, int]:
    """Map normalized template box through page affine (if any)."""
    x0, y0, x1, y1 = norm_box_to_px(box, page.width, page.height)
    if affine is None:
        return x0, y0, x1, y1
    corners = np.float32([[x0, y0], [x1, y0], [x1, y1], [x0, y1]]).reshape(-1, 1, 2)
    warped = cv2.transform(corners, affine)
    xs = warped[:, 0, 0]
    ys = warped[:, 0, 1]
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def crop_rgb(page: PageImage, box_px: tuple[int, int, int, int]) -> np.ndarray:
    x0, y0, x1, y1 = box_px
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(page.width, x1), min(page.height, y1)
    if x1 <= x0 or y1 <= y0:
        return np.zeros((1, 1, 3), dtype=np.uint8)
    return page.rgb[y0:y1, x0:x1].copy()


def _line_positions(proj: np.ndarray, min_gap: int, thresh_ratio: float = 0.35) -> list[int]:
    thresh = float(proj.max()) * thresh_ratio
    idx = np.where(proj >= thresh)[0]
    if len(idx) == 0:
        return []
    groups: list[list[int]] = [[int(idx[0])]]
    for i in idx[1:]:
        if i - groups[-1][-1] <= min_gap:
            groups[-1].append(int(i))
        else:
            groups.append([int(i)])
    return [int(sum(g) / len(g)) for g in groups]


def detect_table_cells(
    img: np.ndarray,
    *,
    rows: int,
    cols: int = 5,
    label_cols: int = 1,
) -> list[list[np.ndarray]] | None:
    """Split bordered table into cell images [row][col] (answer cols only)."""
    if img.size == 0 or img.shape[0] < 20 or img.shape[1] < 40:
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    bw = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 15, 8)
    h, w = gray.shape
    hk = max(15, w // 12)
    vk = max(10, h // 6)
    horiz = cv2.erode(bw, cv2.getStructuringElement(cv2.MORPH_RECT, (hk, 1)), 1)
    horiz = cv2.dilate(horiz, cv2.getStructuringElement(cv2.MORPH_RECT, (hk, 1)), 1)
    vert = cv2.erode(bw, cv2.getStructuringElement(cv2.MORPH_RECT, (1, vk)), 1)
    vert = cv2.dilate(vert, cv2.getStructuringElement(cv2.MORPH_RECT, (1, vk)), 1)
    ys = _line_positions(horiz.sum(axis=1), min_gap=max(4, h // 40))
    xs = _line_positions(vert.sum(axis=0), min_gap=max(4, w // 40))
    need_h = rows + 1
    need_v = cols + label_cols + 1
    if len(ys) < need_h or len(xs) < need_v:
        return None
    # Use outer grid lines; pick last `need_h` horizontal and last `need_v` vertical
    ys = ys[-need_h:]
    xs = xs[-need_v:]
    cells: list[list[np.ndarray]] = []
    for r in range(rows):
        row_cells = []
        y0, y1 = ys[r], ys[r + 1]
        for c in range(cols):
            ci = label_cols + c
            x0, x1 = xs[ci], xs[ci + 1]
            pad = 2
            cell = img[y0 + pad : y1 - pad, x0 + pad : x1 - pad]
            row_cells.append(cell)
        cells.append(row_cells)
    return cells


def detect_fill_line_rois(
    img: np.ndarray,
    *,
    expected: int = 10,
) -> list[tuple[int, int, int, int]] | None:
    """Find horizontal answer lines on page 2; return pixel boxes (x0,y0,x1,y1)."""
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    h, w = gray.shape
    # answer lines in upper ~55% of page
    roi = gray[: int(h * 0.58), :]
    bw = cv2.adaptiveThreshold(roi, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 21, 10)
    horiz = cv2.erode(bw, cv2.getStructuringElement(cv2.MORPH_RECT, (w // 3, 1)), 1)
    horiz = cv2.dilate(horiz, cv2.getStructuringElement(cv2.MORPH_RECT, (w // 3, 1)), 1)
    ys = _line_positions(horiz.sum(axis=1), min_gap=max(8, roi.shape[0] // 30))
    if len(ys) < expected:
        return None
    # cluster into 10 lines (2 groups of 5)
    ys = ys[-expected:] if len(ys) >= expected else ys
    boxes = []
    line_h = max(12, roi.shape[0] // 40)
    for y in ys[:expected]:
        y0 = max(0, y - line_h)
        y1 = min(h, y + line_h // 2)
        boxes.append((int(w * 0.12), y0, int(w * 0.95), y1))
    return boxes


def page_affine(page: PageImage) -> np.ndarray | None:
    markers = find_markers(page.gray)
    if markers is None:
        return None
    ref = REF_MARKERS_SCALE2 * (page.scale / RENDER_SCALE)
    return marker_affine(markers, ref)


@dataclass
class McFrame:
    """ZipGrade MC grid bounds from corner fiducials (TL, TR, BR, BL)."""

    tl: np.ndarray
    tr: np.ndarray
    br: np.ndarray
    bl: np.ndarray

    @property
    def left(self) -> float:
        return float(min(self.tl[0], self.bl[0]))

    @property
    def right(self) -> float:
        return float(max(self.tr[0], self.br[0]))

    @property
    def top(self) -> float:
        return float(min(self.tl[1], self.tr[1]))

    @property
    def bottom(self) -> float:
        return float(max(self.bl[1], self.br[1]))

    @property
    def width(self) -> float:
        return self.right - self.left

    @property
    def height(self) -> float:
        return self.bottom - self.top


def mc_frame(markers: np.ndarray) -> McFrame:
    tl, tr, br, bl = markers
    return McFrame(tl=tl, tr=tr, br=br, bl=bl)


def _horiz_lines_in_roi(gray: np.ndarray, x0: int, y0: int, x1: int, y1: int) -> list[int]:
    """Horizontal grid-line y-positions inside ROI (coords relative to ROI top)."""
    roi = gray[y0:y1, x0:x1]
    if roi.size == 0 or roi.shape[0] < 12:
        return []
    bw = cv2.adaptiveThreshold(roi, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 15, 8)
    h, w = roi.shape
    hk = max(20, w // 8)
    horiz = cv2.erode(bw, cv2.getStructuringElement(cv2.MORPH_RECT, (hk, 1)), 1)
    horiz = cv2.dilate(horiz, cv2.getStructuringElement(cv2.MORPH_RECT, (hk, 1)), 1)
    return _line_positions(horiz.sum(axis=1), min_gap=max(4, h // 50), thresh_ratio=0.25)


def _detect_cell_boxes_in_roi(gray: np.ndarray) -> list[tuple[int, int, int, int]]:
    """
    Detect table cell rectangles inside an ROI using contour boxes.
    Returns a list of (x0,y0,x1,y1) in ROI-local coordinates.
    """
    h, w = gray.shape
    if h < 40 or w < 80:
        return []
    bw = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 21, 10)
    # Extract grid lines, then invert to get cell interiors.
    hk = max(25, w // 12)
    vk = max(18, h // 6)
    horiz = cv2.erode(bw, cv2.getStructuringElement(cv2.MORPH_RECT, (hk, 1)), 1)
    horiz = cv2.dilate(horiz, cv2.getStructuringElement(cv2.MORPH_RECT, (hk, 1)), 1)
    vert = cv2.erode(bw, cv2.getStructuringElement(cv2.MORPH_RECT, (1, vk)), 1)
    vert = cv2.dilate(vert, cv2.getStructuringElement(cv2.MORPH_RECT, (1, vk)), 1)
    grid = cv2.bitwise_or(horiz, vert)
    # Thicken grid lines so adjacent cell interiors disconnect.
    grid = cv2.dilate(grid, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)), 2)
    inv = cv2.bitwise_not(grid)
    # remove background by forcing a border
    inv[0, :] = 0
    inv[-1, :] = 0
    inv[:, 0] = 0
    inv[:, -1] = 0

    cnts, _ = cv2.findContours(inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    out: list[tuple[int, int, int, int]] = []
    roi_area = float(h * w)
    for c in cnts:
        x, y, cw, ch = cv2.boundingRect(c)
        area = float(cw * ch)
        if area < roi_area * 0.001 or area > roi_area * 0.12:
            continue
        if cw < 25 or ch < 18:
            continue
        ratio = cw / max(1.0, float(ch))
        if ratio < 0.55 or ratio > 4.5:
            continue
        out.append((x, y, x + cw, y + ch))

    # de-dup very similar boxes (same location/size)
    out.sort(key=lambda b: (b[1], b[0], (b[2] - b[0]) * (b[3] - b[1])))
    dedup: list[tuple[int, int, int, int]] = []
    for b in out:
        if not dedup:
            dedup.append(b)
            continue
        x0, y0, x1, y1 = b
        px0, py0, px1, py1 = dedup[-1]
        if abs(x0 - px0) < 4 and abs(y0 - py0) < 4 and abs(x1 - px1) < 4 and abs(y1 - py1) < 4:
            continue
        dedup.append(b)
    return dedup


def _group_boxes_into_rows(
    boxes: list[tuple[int, int, int, int]],
    *,
    y_tol: int,
) -> list[list[tuple[int, int, int, int]]]:
    if not boxes:
        return []
    # sort by center y
    boxes = sorted(boxes, key=lambda b: (int((b[1] + b[3]) / 2), b[0]))
    rows: list[list[tuple[int, int, int, int]]] = []
    for b in boxes:
        cy = int((b[1] + b[3]) / 2)
        if not rows:
            rows.append([b])
            continue
        last = rows[-1]
        last_cy = int(sum(int((x[1] + x[3]) / 2) for x in last) / len(last))
        if abs(cy - last_cy) <= y_tol:
            last.append(b)
        else:
            rows.append([b])
    return rows


def _pick_answer_cells_from_row(
    row_boxes: list[tuple[int, int, int, int]],
    *,
    cols: int = 5,
) -> list[tuple[int, int, int, int]] | None:
    """
    Given many boxes on one visual row, pick the rightmost answer cells.
    We expect (label col + 5 answers) but scans sometimes miss borders.
    """
    if len(row_boxes) < cols:
        return None
    row_boxes = sorted(row_boxes, key=lambda b: b[0])
    # keep reasonably aligned boxes by height similarity
    hs = [b[3] - b[1] for b in row_boxes]
    med_h = float(np.median(hs)) if hs else 0.0
    row_boxes = [b for b in row_boxes if 0.5 * med_h <= (b[3] - b[1]) <= 1.8 * med_h] or row_boxes
    row_boxes = sorted(row_boxes, key=lambda b: b[0])
    if len(row_boxes) >= cols + 1:
        # drop left-most label col; keep next 5 (or last 5 if extra noise)
        cand = row_boxes[1 : 1 + cols]
        if len(cand) == cols:
            return cand
        return row_boxes[-cols:]
    return row_boxes[-cols:]


def _split_answer_row(row_img: np.ndarray, *, cols: int = 5) -> list[np.ndarray]:
    """Split one table row into answer cells (skip left row-label column)."""
    if row_img.size == 0:
        return [np.zeros((1, 1, 3), dtype=np.uint8)] * cols
    gray = cv2.cvtColor(row_img, cv2.COLOR_RGB2GRAY)
    h, w = gray.shape
    bw = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 15, 8)
    vk = max(8, h // 3)
    vert = cv2.erode(bw, cv2.getStructuringElement(cv2.MORPH_RECT, (1, vk)), 1)
    vert = cv2.dilate(vert, cv2.getStructuringElement(cv2.MORPH_RECT, (1, vk)), 1)
    xs = _line_positions(vert.sum(axis=0), min_gap=max(6, w // 40), thresh_ratio=0.28)
    need = cols + 2  # label col + 5 answers + right edge
    if len(xs) >= need:
        xs = xs[-need:]
        return [row_img[:, xs[i]: xs[i + 1]] for i in range(1, cols + 1)]

    x0 = int(w * 0.12)
    x1 = w
    slot = (x1 - x0) // cols
    return [row_img[:, x0 + i * slot : x0 + (i + 1) * slot] for i in range(cols)]


@dataclass
class BcTableRegions:
    """Pixel boxes for 乙部 (2 rows) and 丙部 (1 row) on page 1."""

    match_rows: list[tuple[int, int, int, int]]  # x0,y0,x1,y1 per answer row
    tf_row: tuple[int, int, int, int]
    match_block: tuple[int, int, int, int]
    tf_block: tuple[int, int, int, int]
    method: str


def find_bc_table_regions(page: PageImage, markers: np.ndarray | None = None) -> BcTableRegions | None:
    """
    Locate 乙/丙 answer tables using MC corner markers + morphological line detection.
    Handles per-page scan drift without fixed page-normalised boxes.
    """
    markers = markers if markers is not None else find_markers(page.gray)
    if markers is None:
        return None

    frame = mc_frame(markers)
    x0 = int(frame.left - 0.14 * frame.width)
    x1 = int(frame.right + 0.22 * frame.width)
    y_band0 = int(frame.bottom + 2)
    y_band1 = int(frame.bottom + 0.48 * frame.height)
    x0, y_band0 = max(0, x0), max(0, y_band0)
    x1, y_band1 = min(page.width, x1), min(page.height, y_band1)

    # 1) Prefer contour-box detection (more drift-tolerant than line heuristics).
    roi_gray = page.gray[y_band0:y_band1, x0:x1]
    boxes = _detect_cell_boxes_in_roi(roi_gray)
    if boxes:
        # group into rows based on median box height
        hs = [b[3] - b[1] for b in boxes]
        y_tol = max(14, int(np.median(hs) * 0.55)) if hs else 18
        rows = _group_boxes_into_rows(boxes, y_tol=y_tol)
        # keep candidate rows that look like answer rows
        row_cells: list[list[tuple[int, int, int, int]]] = []
        for r in rows:
            picked = _pick_answer_cells_from_row(r, cols=5)
            if picked:
                row_cells.append(picked)
        if len(row_cells) >= 3:
            # take top-3 candidate rows: match1, match2, tf
            def row_bounds(cells: list[tuple[int, int, int, int]]) -> tuple[int, int, int, int]:
                xs0 = [c[0] for c in cells]
                ys0 = [c[1] for c in cells]
                xs1 = [c[2] for c in cells]
                ys1 = [c[3] for c in cells]
                pad = 3
                return (
                    x0 + int(min(xs0)) - pad,
                    y_band0 + int(min(ys0)) - pad,
                    x0 + int(max(xs1)) + pad,
                    y_band0 + int(max(ys1)) + pad,
                )

            r1 = row_bounds(row_cells[0])
            r2 = row_bounds(row_cells[1])
            tf = row_bounds(row_cells[2])
            match_block = (min(r1[0], r2[0]), r1[1], max(r1[2], r2[2]), r2[3])
            return BcTableRegions(
                match_rows=[r1, r2],
                tf_row=tf,
                match_block=match_block,
                tf_block=tf,
                method="mc_markers+box_detect",
            )

    # 2) Fallback to horizontal line detection if boxes fail.
    ys = _horiz_lines_in_roi(page.gray, x0, y_band0, x1, y_band1)
    if len(ys) < 3:
        return None
    gaps = [ys[i + 1] - ys[i] for i in range(len(ys) - 1)]
    tight = [g for g in gaps if g < 110]
    row_h = int(np.median(tight[:2] if len(tight) >= 2 else tight or gaps[:1]))
    row_h = max(28, row_h)
    r1_y0 = y_band0 + ys[0]
    r1_y1 = y_band0 + ys[1]
    r2_y0 = r1_y1
    r2_y1 = r2_y0 + row_h
    if len(ys) >= 4:
        tf_y0 = y_band0 + ys[-2]
        tf_y1 = y_band0 + ys[-1]
    else:
        tf_y0 = y_band0 + ys[-1]
        tf_y1 = tf_y0 + row_h
    if tf_y1 - tf_y0 < row_h * 0.7:
        tf_y1 = tf_y0 + row_h
    match_rows = [(x0, r1_y0, x1, r1_y1), (x0, r2_y0, x1, r2_y1)]
    tf_row = (x0, tf_y0, x1, tf_y1)
    match_block = (x0, r1_y0, x1, r2_y1)
    tf_block = tf_row
    return BcTableRegions(
        match_rows=match_rows,
        tf_row=tf_row,
        match_block=match_block,
        tf_block=tf_block,
        method="mc_markers+line_detect",
    )
