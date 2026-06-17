"""Per-page alignment for scanned S3 CMP answer sheets (translation + scale from fiducials)."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

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


def _cluster_positions(values: list[int], merge_gap: int = 4) -> list[int]:
    if not values:
        return []
    values = sorted(values)
    groups: list[list[int]] = [[values[0]]]
    for v in values[1:]:
        if v - groups[-1][-1] <= merge_gap:
            groups[-1].append(v)
        else:
            groups.append([v])
    return [int(sum(g) / len(g)) for g in groups]


def _hough_horizontal_ys(gray: np.ndarray, *, min_len_ratio: float = 0.28) -> list[int]:
    h, w = gray.shape
    if h < 20 or w < 40:
        return []
    edges = cv2.Canny(gray, 30, 120)
    lines = cv2.HoughLinesP(
        edges,
        1,
        np.pi / 180,
        threshold=max(35, w // 18),
        minLineLength=int(w * min_len_ratio),
        maxLineGap=14,
    )
    ys: list[int] = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if abs(y2 - y1) <= 6 and abs(x2 - x1) >= w * min_len_ratio:
                ys.append(int((y1 + y2) / 2))
    return _cluster_positions(ys, merge_gap=4)


def _hough_vertical_xs(gray: np.ndarray, *, min_len_ratio: float = 0.35) -> list[int]:
    h, w = gray.shape
    if h < 20 or w < 40:
        return []
    edges = cv2.Canny(gray, 30, 120)
    lines = cv2.HoughLinesP(
        edges,
        1,
        np.pi / 180,
        threshold=max(30, h // 10),
        minLineLength=int(h * min_len_ratio),
        maxLineGap=10,
    )
    xs: list[int] = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if abs(x2 - x1) <= 6 and abs(y2 - y1) >= h * min_len_ratio:
                xs.append(int((x1 + x2) / 2))
    return _cluster_positions(xs, merge_gap=4)


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
    """Find horizontal answer underlines on page 2 (丁部); return pixel boxes (x0,y0,x1,y1)."""
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    h, w = gray.shape
    x0, x1 = int(w * 0.12), int(w * 0.95)
    y0, y1 = int(h * 0.10), int(h * 0.58)
    roi = gray[y0:y1, x0:x1]
    if roi.size == 0:
        return None

    ys = _underline_ys_in_roi(roi, y_offset=y0)
    if len(ys) < expected:
        return None

    ys = ys[:expected]
    gaps = [ys[i + 1] - ys[i] for i in range(min(4, len(ys) - 1))]
    line_h = max(12, int(np.median(gaps) * 0.42)) if gaps else 14
    boxes: list[tuple[int, int, int, int]] = []
    for y in ys:
        boxes.append((x0, max(0, y - line_h - 6), x1, min(h, y + 3)))
    return boxes


def _underline_ys_in_roi(roi_gray: np.ndarray, *, y_offset: int = 0) -> list[int]:
    rh, rw = roi_gray.shape
    bw = cv2.adaptiveThreshold(roi_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 21, 10)
    kw = max(40, int(rw * 0.15))
    horiz = cv2.erode(bw, cv2.getStructuringElement(cv2.MORPH_RECT, (kw, 1)), 1)
    horiz = cv2.dilate(horiz, cv2.getStructuringElement(cv2.MORPH_RECT, (kw, 1)), 1)
    ys = _line_positions(horiz.sum(axis=1), min_gap=10, thresh_ratio=0.18)
    return [y + y_offset for y in ys]


def _cluster_label_rows(gray: np.ndarray) -> list[int]:
    """Cluster printed (a)(b)(c) label rows in the left margin across page 2."""
    h, w = gray.shape
    strip = gray[int(h * 0.10) : int(h * 0.88), : int(w * 0.22)]
    y_off = int(h * 0.10)
    _, bw = cv2.threshold(strip, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    cnts, _ = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    ys: list[int] = []
    for c in cnts:
        x, y, cw, ch = cv2.boundingRect(c)
        if 7 <= cw <= 20 and 9 <= ch <= 26 and x >= int(strip.shape[1] * 0.30):
            ys.append(y_off + y + ch // 2)
    return _cluster_positions(sorted(ys), merge_gap=32)


def _ruled_line_ys_in_band(
    gray: np.ndarray,
    y0: int,
    y1: int,
    x0: int,
    x1: int,
) -> list[int]:
    strip = gray[y0:y1, x0:x1]
    if strip.size == 0:
        return []
    return _underline_ys_in_roi(strip, y_offset=y0)


def _sa_block_bottom_after_ruled_lines(
    gray: np.ndarray,
    y_start: int,
    x_left: int,
    x_right: int,
    *,
    lines: int = 4,
) -> int | None:
    """End 戊部 (c) at the last ruled line + small padding (exclude 全卷完)."""
    h = gray.shape[0]
    ys = _ruled_line_ys_in_band(gray, y_start, min(h, y_start + 240), x_left, x_right)
    if len(ys) < lines:
        return None
    gaps = [ys[i + 1] - ys[i] for i in range(len(ys) - 1)]
    pad = max(16, int(np.median(gaps) * 0.35)) if gaps else 18
    return ys[lines - 1] + pad


def detect_sa_block_rois(img: np.ndarray, *, expected: int = 3) -> list[tuple[int, int, int, int]] | None:
    """Locate 戊部 sub-parts via (a)(b)(c) label clusters in the left margin."""
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    h, w = gray.shape
    clusters = _cluster_label_rows(gray)
    if len(clusters) >= 10 + expected:
        sa_ys = _merge_close_clusters(clusters[10:], min_gap=55)[:expected]
    else:
        sa_ys = _merge_close_clusters([c for c in clusters if c > h * 0.46], min_gap=55)[:expected]
    if len(sa_ys) < expected:
        return None

    x_left, x_right = int(w * 0.08), int(w * 0.95)
    boxes: list[tuple[int, int, int, int]] = []
    for i, cy in enumerate(sa_ys[:expected]):
        if i == 0:
            y_end = (cy + sa_ys[i + 1]) // 2 - 6
            y_start = max(0, 2 * cy - y_end)
        else:
            y_start = (sa_ys[i - 1] + cy) // 2 + 8
            y_end = (cy + sa_ys[i + 1]) // 2 - 6 if i + 1 < len(sa_ys) else None
        if i + 1 >= expected:
            ruled_end = _sa_block_bottom_after_ruled_lines(gray, y_start, x_left, x_right)
            y_end = ruled_end if ruled_end is not None else int(h * 0.76)
        boxes.append((x_left, y_start, x_right, y_end))
    return boxes


def _merge_close_clusters(clusters: list[int], *, min_gap: int) -> list[int]:
    if not clusters:
        return []
    out = [clusters[0]]
    for c in clusters[1:]:
        if c - out[-1] < min_gap:
            out[-1] = int((out[-1] + c) / 2)
        else:
            out.append(c)
    return out


@dataclass
class Page2Regions:
    fill_boxes: list[tuple[int, int, int, int]]
    sa_boxes: list[tuple[int, int, int, int]]
    method: str


def detect_page2_regions(page: PageImage) -> Page2Regions | None:
    """Auto-detect 丁部 fill lines + 戊部 SA blocks on answer page 2."""
    fill = detect_fill_line_rois(page.rgb, expected=10)
    sa = detect_sa_block_rois(page.rgb, expected=3)
    if not fill or not sa:
        return None
    return Page2Regions(fill_boxes=fill, sa_boxes=sa, method="underline+label_clusters")


def resolve_page2_regions(page: PageImage, layout_p2: dict | None = None) -> Page2Regions | None:
    """Auto-detect page 2; apply per-block norm box overrides from layout when set."""
    regions = detect_page2_regions(page)
    if layout_p2 is None:
        return regions

    overrides: dict[str, tuple[float, float, float, float]] = {}
    cal = layout_p2.get("calibrated") or {}
    if cal.get("enabled"):
        for sid, box in (cal.get("sa_overrides") or {}).items():
            overrides[sid] = tuple(box)

    sa_specs = layout_p2.get("sa_blocks") or []
    for item in sa_specs:
        if item.get("use_box"):
            overrides[item["id"]] = tuple(item["box"])

    if not overrides:
        return regions

    if regions is None:
        fill = [
            norm_box_to_px(tuple(x["box"]), page.width, page.height)
            for x in layout_p2.get("fill_lines", [])
        ]
        sa = [
            norm_box_to_px(tuple(x["box"]), page.width, page.height)
            for x in sa_specs
        ]
        regions = Page2Regions(fill_boxes=fill, sa_boxes=sa, method="layout_fallback")

    sa_boxes = list(regions.sa_boxes)
    for idx, item in enumerate(sa_specs):
        box = overrides.get(item["id"])
        if box is not None and idx < len(sa_boxes):
            sa_boxes[idx] = norm_box_to_px(box, page.width, page.height)

    method = regions.method
    if overrides:
        method = f"{method}+sa_override"
    return Page2Regions(fill_boxes=regions.fill_boxes, sa_boxes=sa_boxes, method=method)


def page_affine(page: PageImage) -> np.ndarray | None:
    markers = find_markers(page.gray)
    if markers is None:
        return None
    ref = REF_MARKERS_SCALE2 * (page.scale / RENDER_SCALE)
    return marker_affine(markers, ref)


# --- ORB template alignment (blank answer sheets from exam PDF) ---

_TEMPLATE_CACHE: dict[str, dict[str, PageImage]] = {}


def _resolve_template_pdf(layout: dict, layout_path: Path | None = None) -> Path | None:
    tpl_cfg = (layout.get("alignment") or {}).get("template") or {}
    raw = tpl_cfg.get("pdf")
    if not raw:
        return None
    p = Path(raw)
    if p.is_file():
        return p
    roots = []
    if layout_path is not None:
        roots.extend([layout_path.parent, layout_path.parent.parent.parent])
    roots.append(Path(__file__).resolve().parents[2])
    for root in roots:
        cand = root / p
        if cand.is_file():
            return cand
    return None


def load_exam_templates(
    layout: dict,
    *,
    layout_path: Path | None = None,
    scale: float = RENDER_SCALE,
) -> dict[str, PageImage]:
    """Load blank answer-sheet template pages (exam PDF 倒数第4/3页 = pages 8–9)."""
    pdf_path = _resolve_template_pdf(layout, layout_path)
    if pdf_path is None:
        return {}
    key = f"{pdf_path}:{pdf_path.stat().st_mtime}:{scale}"
    if key in _TEMPLATE_CACHE:
        return _TEMPLATE_CACHE[key]

    tpl_cfg = (layout.get("alignment") or {}).get("template") or {}
    pages = tpl_cfg.get("pages") or {"answer_p1": 8, "answer_p2": 9}
    roles = layout.get("page_roles") or ["answer_p1", "answer_p2"]
    doc = fitz.open(pdf_path)
    out: dict[str, PageImage] = {}
    for role in roles:
        page_no = int(pages.get(role, 0))
        if page_no < 1 or page_no > doc.page_count:
            continue
        out[role] = render_page(doc[page_no - 1], scale=scale)
    doc.close()
    _TEMPLATE_CACHE[key] = out
    return out


def _orb_homography(
    scan_gray: np.ndarray,
    template_gray: np.ndarray,
    *,
    max_features: int = 1200,
    good_match_percent: float = 0.2,
    min_inliers: int = 12,
) -> np.ndarray | None:
    """Return H mapping scan coords -> template coords, or None."""
    orb = cv2.ORB_create(max_features)
    kp1, des1 = orb.detectAndCompute(scan_gray, None)
    kp2, des2 = orb.detectAndCompute(template_gray, None)
    if des1 is None or des2 is None or len(kp1) < 8 or len(kp2) < 8:
        return None

    matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
    matches = matcher.match(des1, des2, None)
    if len(matches) < 8:
        return None
    matches = sorted(matches, key=lambda m: m.distance)
    n_good = max(8, int(len(matches) * good_match_percent))
    matches = matches[:n_good]

    pts_scan = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    pts_tpl = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
    H, mask = cv2.findHomography(pts_scan, pts_tpl, cv2.RANSAC, 5.0)
    if H is None or mask is None:
        return None
    inliers = int(mask.ravel().sum())
    if inliers < min_inliers:
        return None
    return H


def align_page_to_exam_template(
    page: PageImage,
    template: PageImage,
) -> tuple[PageImage, np.ndarray | None]:
    """Warp scan page into blank exam template space via ORB + homography."""
    H = _orb_homography(page.gray, template.gray)
    if H is None:
        return page, None
    warped_rgb = cv2.warpPerspective(
        page.rgb,
        H,
        (template.width, template.height),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(255, 255, 255),
    )
    warped_gray = cv2.cvtColor(warped_rgb, cv2.COLOR_RGB2GRAY)
    return (
        PageImage(page=page.page, scale=page.scale, rgb=warped_rgb, gray=warped_gray),
        H,
    )


def prepare_aligned_page(
    page_img: PageImage,
    role: str,
    layout: dict,
    templates: dict[str, PageImage] | None = None,
) -> tuple[PageImage, np.ndarray | None, str]:
    """
    Align scan page for cropping/OCR.
    Page 1: ZipGrade markers; page 2: ORB vs blank template (no ZipGrade on p2).
    Returns (page_image, affine_or_none, method).
    """
    align_cfg = layout.get("alignment") or {}
    prefer_orb = role in (align_cfg.get("orb_preferred_roles") or ["answer_p2"])

    if prefer_orb and align_cfg.get("orb_fallback", True):
        if templates is None:
            templates = load_exam_templates(layout)
        template = templates.get(role)
        if template is not None:
            aligned, H = align_page_to_exam_template(page_img, template)
            if H is not None:
                return aligned, None, "orb"

    affine = page_affine(page_img)
    if affine is not None:
        return page_img, affine, "markers"

    if not align_cfg.get("orb_fallback", True):
        return page_img, None, "none"

    if templates is None:
        templates = load_exam_templates(layout)
    template = templates.get(role)
    if template is None:
        return page_img, None, "none"

    aligned, H = align_page_to_exam_template(page_img, template)
    if H is not None:
        return aligned, None, "orb"
    return page_img, None, "none"

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
    """Pick the 5 answer cells on one table row (each cell includes its (a)–(e) label)."""
    if len(row_boxes) < cols:
        return None
    row_boxes = sorted(row_boxes, key=lambda b: b[0])
    hs = [b[3] - b[1] for b in row_boxes]
    med_h = float(np.median(hs)) if hs else 0.0
    row_boxes = [b for b in row_boxes if 0.5 * med_h <= (b[3] - b[1]) <= 1.8 * med_h] or row_boxes
    row_boxes = sorted(row_boxes, key=lambda b: b[0])
    return row_boxes[:cols] if len(row_boxes) >= cols else row_boxes[-cols:]


def _answer_col_bounds_in_row(row_img: np.ndarray, *, cols: int = 5) -> list[tuple[int, int]]:
    """Return (x0, x1) within row_img for each of the 5 answer columns."""
    if row_img.size == 0:
        return [(0, 1)] * cols
    gray = cv2.cvtColor(row_img, cv2.COLOR_RGB2GRAY)
    h, w = gray.shape

    cells = detect_table_cells(row_img, rows=1, cols=cols, label_cols=0)
    if cells and len(cells[0]) == cols:
        bw = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 15, 8)
        vk = max(8, h // 3)
        vert = cv2.erode(bw, cv2.getStructuringElement(cv2.MORPH_RECT, (1, vk)), 1)
        vert = cv2.dilate(vert, cv2.getStructuringElement(cv2.MORPH_RECT, (1, vk)), 1)
        xs = _line_positions(vert.sum(axis=0), min_gap=max(6, w // 40), thresh_ratio=0.22)
        if len(xs) >= cols + 1:
            pairs = [(xs[i], xs[i + 1]) for i in range(len(xs) - 1)]
            if len(pairs) >= cols:
                return pairs[:cols]

    slot = max(1, w // cols)
    return [(slot * i, slot * (i + 1)) for i in range(cols)]


def _split_answer_row(row_img: np.ndarray, *, cols: int = 5) -> list[np.ndarray]:
    """Split one table row into 5 answer cells (a)–(e)."""
    if row_img.size == 0:
        return [np.zeros((1, 1, 3), dtype=np.uint8)] * cols
    bounds = _answer_col_bounds_in_row(row_img, cols=cols)
    return [row_img[:, x0:x1] for x0, x1 in bounds]


def _row_answer_cell_boxes(
    row_box: tuple[int, int, int, int],
    row_img: np.ndarray,
    *,
    cols: int = 5,
) -> list[tuple[int, int, int, int]]:
    """Absolute page boxes for each answer cell in a table row."""
    rx0, ry0, _, _ = row_box
    bounds = _answer_col_bounds_in_row(row_img, cols=cols)
    return [(rx0 + x0, ry0, rx0 + x1, ry0 + row_img.shape[0]) for x0, x1 in bounds]


def _five_col_bounds_in_row_strip(
    gray_strip: np.ndarray,
) -> tuple[int, int, list[tuple[int, int]]] | None:
    """Detect 5 equal-ish answer columns in a full-page-width table row strip."""
    if gray_strip.size == 0 or gray_strip.shape[0] < 12:
        return None
    h, w = gray_strip.shape
    bw = cv2.adaptiveThreshold(gray_strip, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 15, 8)
    vk = max(8, h // 3)
    vert = cv2.erode(bw, cv2.getStructuringElement(cv2.MORPH_RECT, (1, vk)), 1)
    vert = cv2.dilate(vert, cv2.getStructuringElement(cv2.MORPH_RECT, (1, vk)), 1)
    xs = _line_positions(vert.sum(axis=0), min_gap=8, thresh_ratio=0.2)
    if len(xs) < 6:
        return None
    pairs = [(xs[i], xs[i + 1]) for i in range(len(xs) - 1)]
    best: tuple[float, list[tuple[int, int]]] | None = None
    for i in range(len(pairs) - 4):
        chunk = pairs[i : i + 5]
        widths = [b - a for a, b in chunk]
        med = float(np.median(widths))
        if med < 70 or med > 220:
            continue
        if max(widths) > 2.2 * max(min(widths), 1):
            continue
        score = float(np.std(widths))
        if best is None or score < best[0]:
            best = (score, chunk)
    if best is None:
        return None
    chunk = best[1]
    return chunk[0][0], chunk[-1][1], chunk


def _refine_bc_regions_x(page: PageImage, regions: BcTableRegions) -> BcTableRegions:
    """Snap row boxes to detected 5-column table x extent."""
    for row_box in (*regions.match_rows, regions.tf_row):
        y0, y1 = row_box[1], row_box[3]
        strip = page.gray[y0:y1, :]
        found = _five_col_bounds_in_row_strip(strip)
        if found is None:
            continue
        x0, x1, cols = found
        if x1 - x0 < int(page.width * 0.38):
            continue

        def patch_row(rb: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
            return (x0, rb[1], x1, rb[3])

        regions.match_rows = [patch_row(r) for r in regions.match_rows]
        regions.tf_row = patch_row(regions.tf_row)
        regions.match_block = (x0, regions.match_block[1], x1, regions.match_block[3])
        regions.tf_block = (x0, regions.tf_block[1], x1, regions.tf_block[3])
        regions.match_cell_boxes = [
            [(cx0, ry0, cx1, ry1) for cx0, cx1 in cols]
            for ry0, ry1 in ((r[1], r[3]) for r in regions.match_rows)
        ]
        regions.tf_cell_boxes = [
            (cx0, regions.tf_row[1], cx1, regions.tf_row[3]) for cx0, cx1 in cols
        ]
        return regions
    return regions


def _bc_table_x_bounds(page: PageImage, frame: McFrame) -> tuple[int, int]:
    """Horizontal extent of 乙/丙 answer tables (~35%–98% page width per layout template)."""
    w = page.width
    x0 = int(w * 0.35)
    x1 = int(w * 0.98)
    if x1 - x0 < int(w * 0.40):
        cx = int((frame.left + frame.right) / 2)
        half = int(w * 0.40) // 2
        x0, x1 = max(0, cx - half), min(w, cx + half)
    return x0, x1


@dataclass
class BcTableRegions:
    """Pixel boxes for 乙部 (2 rows) and 丙部 (1 row) on page 1."""

    match_rows: list[tuple[int, int, int, int]]  # x0,y0,x1,y1 per answer row
    tf_row: tuple[int, int, int, int]
    match_block: tuple[int, int, int, int]
    tf_block: tuple[int, int, int, int]
    method: str
    match_cell_boxes: list[list[tuple[int, int, int, int]]] | None = None
    tf_cell_boxes: list[tuple[int, int, int, int]] | None = None


def _equal_col_cells(
    row_box: tuple[int, int, int, int],
    *,
    cols: int = 5,
) -> list[tuple[int, int, int, int]]:
    x0, y0, x1, y1 = row_box
    cw = max(1, (x1 - x0) // cols)
    return [
        (x0 + i * cw, y0, x0 + (i + 1) * cw if i < cols - 1 else x1, y1)
        for i in range(cols)
    ]


def bc_regions_from_calibrated(
    page: PageImage,
    calibrated: dict,
) -> BcTableRegions | None:
    """Build BC regions from hand-tuned norm boxes in layout JSON (calibrate once)."""
    if not calibrated.get("enabled"):
        return None
    rows_spec = calibrated.get("rows")
    if not rows_spec:
        return None

    match_rows: list[tuple[int, int, int, int]] = []
    match_cells: list[list[tuple[int, int, int, int]]] = []
    tf_row: tuple[int, int, int, int] | None = None
    tf_cells: list[tuple[int, int, int, int]] = []

    for item in rows_spec:
        box = tuple(item["box"])
        cols = int(item.get("cols", 5))
        px = norm_box_to_px(box, page.width, page.height)
        cells = _equal_col_cells(px, cols=cols)
        rid = str(item.get("id", ""))
        if rid.startswith("match"):
            match_rows.append(px)
            match_cells.append(cells)
        elif rid.startswith("tf"):
            tf_row = px
            tf_cells = cells

    if len(match_rows) < 2 or tf_row is None:
        return None

    match_block = (
        min(r[0] for r in match_rows),
        match_rows[0][1],
        max(r[2] for r in match_rows),
        match_rows[-1][3],
    )
    return BcTableRegions(
        match_rows=match_rows,
        tf_row=tf_row,
        match_block=match_block,
        tf_block=tf_row,
        method="layout_calibrated",
        match_cell_boxes=match_cells,
        tf_cell_boxes=tf_cells,
    )


def resolve_bc_regions(
    page: PageImage,
    layout_p1: dict | None = None,
    markers: np.ndarray | None = None,
) -> BcTableRegions | None:
    """Prefer hand-calibrated layout; fall back to OpenCV detection."""
    if layout_p1:
        cal = layout_p1.get("calibrated")
        if cal:
            regions = bc_regions_from_calibrated(page, cal)
            if regions is not None:
                return regions
    return find_bc_table_regions(page, markers)


def _bc_rows_from_hough(
    roi_gray: np.ndarray,
    x_off: int,
    y_off: int,
    x1_abs: int,
) -> BcTableRegions | None:
    w_roi = roi_gray.shape[1]
    ys = _hough_horizontal_ys(roi_gray, min_len_ratio=0.18 if w_roi > 900 else 0.28)
    if len(ys) < 2:
        return None

    pairs = [(ys[i], ys[i + 1], ys[i + 1] - ys[i]) for i in range(len(ys) - 1)]
    good = [(a, b, h) for a, b, h in pairs if 45 <= h <= 95]
    if len(good) < 3:
        return None

    m1_a, m1_b, _ = good[0]
    m2_a, m2_b, _ = good[1]
    after_gap = [p for p in good[2:] if p[0] >= m2_b + 80]
    tall = [p for p in after_gap if p[2] >= 60]
    tf_pair = tall[0] if tall else (after_gap[-1] if after_gap else None)
    if tf_pair is None:
        return None
    tf_a, tf_b, _ = tf_pair

    def abs_row(a: int, b: int) -> tuple[int, int, int, int]:
        return (x_off, y_off + a, x1_abs, y_off + b)

    match_rows = [abs_row(m1_a, m1_b), abs_row(m2_a, m2_b)]
    tf_row = abs_row(tf_a, tf_b)
    match_block = (x_off, y_off + m1_a, x1_abs, y_off + m2_b)
    return BcTableRegions(
        match_rows=match_rows,
        tf_row=tf_row,
        match_block=match_block,
        tf_block=tf_row,
        method="mc_markers+hough_grid",
    )


def _attach_bc_cell_boxes(page: PageImage, regions: BcTableRegions) -> BcTableRegions:
    regions = _refine_bc_regions_x(page, regions)
    if regions.match_cell_boxes and regions.tf_cell_boxes:
        return regions
    match_cells: list[list[tuple[int, int, int, int]]] = []
    for row_box in regions.match_rows:
        row_img = crop_rgb(page, row_box)
        match_cells.append(_row_answer_cell_boxes(row_box, row_img))
    tf_img = crop_rgb(page, regions.tf_row)
    tf_cells = _row_answer_cell_boxes(regions.tf_row, tf_img)
    regions.match_cell_boxes = match_cells
    regions.tf_cell_boxes = tf_cells
    return regions


def find_bc_table_regions(page: PageImage, markers: np.ndarray | None = None) -> BcTableRegions | None:
    """
    Locate 乙/丙 answer tables using MC corner markers + OpenCV box/line detection.
    Handles per-page scan drift without fixed page-normalised boxes.
    """
    markers = markers if markers is not None else find_markers(page.gray)
    if markers is None:
        return None

    frame = mc_frame(markers)
    y_band0 = int(frame.bottom - 0.06 * frame.height)
    y_band1 = int(frame.bottom + 0.48 * frame.height)
    y_band0, y_band1 = max(0, y_band0), min(page.height, y_band1)
    x0, x1 = 0, page.width

    roi_gray = page.gray[y_band0:y_band1, :]

    # 1) Contour cell boxes — best when grid borders are crisp.
    boxes = _detect_cell_boxes_in_roi(roi_gray)
    if boxes:
        hs = [b[3] - b[1] for b in boxes]
        y_tol = max(14, int(np.median(hs) * 0.55)) if hs else 18
        rows = _group_boxes_into_rows(boxes, y_tol=y_tol)
        row_cells: list[list[tuple[int, int, int, int]]] = []
        for r in rows:
            picked = _pick_answer_cells_from_row(r, cols=5)
            if picked:
                row_cells.append(picked)
        if len(row_cells) >= 3:

            def row_bounds(cells: list[tuple[int, int, int, int]]) -> tuple[int, int, int, int]:
                pad = 3
                return (
                    int(min(c[0] for c in cells)) - pad,
                    y_band0 + int(min(c[1] for c in cells)) - pad,
                    int(max(c[2] for c in cells)) + pad,
                    y_band0 + int(max(c[3] for c in cells)) + pad,
                )

            r1 = row_bounds(row_cells[0])
            r2 = row_bounds(row_cells[1])
            tf = row_bounds(row_cells[2])
            match_block = (min(r1[0], r2[0]), r1[1], max(r1[2], r2[2]), r2[3])
            regions = BcTableRegions(
                match_rows=[r1, r2],
                tf_row=tf,
                match_block=match_block,
                tf_block=tf,
                method="mc_markers+box_detect",
            )
            return _attach_bc_cell_boxes(page, regions)

    # 2) Hough horizontal lines on full page width; x refined per 5-column grid.
    regions = _bc_rows_from_hough(roi_gray, 0, y_band0, page.width)
    if regions is not None:
        return _attach_bc_cell_boxes(page, regions)

    # 3) Morphological horizontal lines (legacy fallback).
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
    regions = BcTableRegions(
        match_rows=match_rows,
        tf_row=tf_row,
        match_block=match_block,
        tf_block=tf_row,
        method="mc_markers+line_detect",
    )
    return _attach_bc_cell_boxes(page, regions)
