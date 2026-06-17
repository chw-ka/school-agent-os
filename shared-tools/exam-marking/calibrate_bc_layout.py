"""Export or preview S3 CMP page-1 BC crop layout (calibrate once in JSON).

Hand-tune `s3_cmp_term02_layout.json` → regions.answer_p1.calibrated, then all scans
reuse norm boxes without re-tuning OpenCV.

Examples:
  # Suggest calibrated rows from auto-detection (paste into layout JSON):
  python calibrate_bc_layout.py scan.pdf --student 0 --dump

  # Preview crops from current layout:
  python calibrate_bc_layout.py scan.pdf -o ./_cal_preview --student 0
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import fitz

from answer_sheet_align import (
    bc_regions_from_calibrated,
    crop_rgb,
    find_bc_table_regions,
    render_page,
    resolve_bc_regions,
)

_LAYOUT = Path(__file__).with_name("s3_cmp_term02_layout.json")


def _norm_box(box: tuple[int, int, int, int], w: int, h: int) -> list[float]:
    x0, y0, x1, y1 = box
    return [round(x0 / w, 4), round(y0 / h, 4), round(x1 / w, 4), round(y1 / h, 4)]


def dump_calibrated(page_img, *, table_x: tuple[float, float] | None) -> dict:
    """Build calibrated snippet from detection + optional table x override."""
    auto = find_bc_table_regions(page_img)
    if auto is None:
        raise SystemExit("Could not detect BC rows; set boxes manually in layout JSON.")

    w, h = page_img.width, page_img.height
    rows_out: list[dict] = []
    names = ["match_q1", "match_q2", "tf_q1"]
    row_boxes = [*auto.match_rows, auto.tf_row]
    for name, row in zip(names, row_boxes, strict=True):
        x0, y0, x1, y1 = row
        if table_x is not None:
            x0 = int(w * table_x[0])
            x1 = int(w * table_x[1])
        rows_out.append({"id": name, "box": _norm_box((x0, y0, x1, y1), w, h), "cols": 5})

    return {
        "enabled": True,
        "reference": "edit me",
        "rows": rows_out,
    }


def save_preview(page_img, regions, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for ri, row in enumerate(regions.match_rows, start=1):
        cv2.imwrite(
            str(dest / f"match_q{ri}_row.png"),
            cv2.cvtColor(crop_rgb(page_img, row), cv2.COLOR_RGB2BGR),
        )
        if regions.match_cell_boxes and ri - 1 < len(regions.match_cell_boxes):
            for ci, box in enumerate(regions.match_cell_boxes[ri - 1]):
                ch = chr(ord("a") + ci)
                cv2.imwrite(
                    str(dest / f"match_q{ri}_{ch}.png"),
                    cv2.cvtColor(crop_rgb(page_img, box), cv2.COLOR_RGB2BGR),
                )
    if regions.tf_cell_boxes:
        for ci, box in enumerate(regions.tf_cell_boxes):
            ch = chr(ord("a") + ci)
            cv2.imwrite(
                str(dest / f"tf_q1_{ch}.png"),
                cv2.cvtColor(crop_rgb(page_img, box), cv2.COLOR_RGB2BGR),
            )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf", type=Path, help="Reference scan PDF (reordered, 2 pp/student)")
    ap.add_argument("--student", type=int, default=0)
    ap.add_argument("--dump", action="store_true", help="Print calibrated JSON for layout file")
    ap.add_argument(
        "--table-x",
        nargs=2,
        type=float,
        metavar=("X0", "X1"),
        help="Override table left/right as page fractions (e.g. 0.168 0.882)",
    )
    ap.add_argument("-o", "--output-dir", type=Path, help="Write per-cell preview PNGs")
    ap.add_argument("--layout", type=Path, default=_LAYOUT)
    args = ap.parse_args()

    doc = fitz.open(args.pdf)
    page_img = render_page(doc[args.student * 2])
    doc.close()

    if args.dump:
        table_x = tuple(args.table_x) if args.table_x else None
        snippet = dump_calibrated(page_img, table_x=table_x)
        print(json.dumps(snippet, ensure_ascii=False, indent=2))
        return 0

    layout = json.loads(args.layout.read_text(encoding="utf-8"))
    spec = layout["regions"]["answer_p1"]
    regions = resolve_bc_regions(page_img, spec)
    if regions is None:
        raise SystemExit("No BC regions (check calibrated.enabled and row boxes).")
    print(f"method: {regions.method}")
    if args.output_dir:
        save_preview(page_img, regions, args.output_dir)
        print(f"Wrote previews → {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
