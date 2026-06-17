"""Draw alignment + detected table grid on sample pages for manual verification."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import fitz

from answer_sheet_align import (
    crop_rgb,
    detect_fill_line_rois,
    detect_table_cells,
    find_bc_table_regions,
    find_markers,
    page_affine,
    render_page,
    warp_norm_box,
)

_LAYOUT = Path(__file__).with_name("s3_cmp_term02_layout.json")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf", type=Path)
    ap.add_argument("-o", "--output-dir", type=Path, required=True)
    ap.add_argument("--student", type=int, default=0)
    args = ap.parse_args()

    layout = json.loads(_LAYOUT.read_text(encoding="utf-8"))
    doc = fitz.open(args.pdf)
    si = args.student
    p1 = doc[si * 2]
    p2 = doc[si * 2 + 1]
    args.output_dir.mkdir(parents=True, exist_ok=True)

    for label, page, role in (("p1", p1, "answer_p1"), ("p2", p2, "answer_p2")):
        img = render_page(page)
        vis = img.rgb.copy()
        markers = find_markers(img.gray)
        if markers is not None:
            for x, y in markers:
                cv2.circle(vis, (int(x), int(y)), 8, (0, 255, 0), 2)
        affine = page_affine(img)
        spec = layout["regions"][role]
        if role == "answer_p1":
            regions = find_bc_table_regions(img, markers)
            if regions:
                for ri, box in enumerate(regions.match_rows, start=1):
                    x0, y0, x1, y1 = box
                    cv2.rectangle(vis, (x0, y0), (x1, y1), (255, 0, 0), 2)
                    cv2.imwrite(
                        str(args.output_dir / f"student{si:03d}_match_q{ri}.png"),
                        cv2.cvtColor(crop_rgb(img, box), cv2.COLOR_RGB2BGR),
                    )
                x0, y0, x1, y1 = regions.tf_row
                cv2.rectangle(vis, (x0, y0), (x1, y1), (0, 0, 255), 2)
                cv2.imwrite(
                    str(args.output_dir / f"student{si:03d}_tf_block.png"),
                    cv2.cvtColor(crop_rgb(img, regions.tf_block), cv2.COLOR_RGB2BGR),
                )
            else:
                for key in ("match_block", "tf_block"):
                    block = spec[key]
                    px = warp_norm_box(tuple(block["box"]), img, affine)
                    cv2.rectangle(vis, px[:2], px[2:], (255, 128, 0), 2)
        else:
            for item in spec.get("fill_lines", []):
                px = warp_norm_box(tuple(item["box"]), img, affine)
                x0, y0, x1, y1 = px
                cv2.rectangle(vis, (x0, y0), (x1, y1), (0, 0, 255), 1)
            auto = detect_fill_line_rois(img.rgb)
            if auto:
                for px in auto:
                    x0, y0, x1, y1 = px
                    cv2.rectangle(vis, (x0, y0), (x1, y1), (0, 255, 255), 1)
        cv2.imwrite(
            str(args.output_dir / f"student{si:03d}_{label}_overlay.png"),
            cv2.cvtColor(vis, cv2.COLOR_RGB2BGR),
        )
        print(f"{label}: markers={'yes' if markers is not None else 'NO'}, affine={'yes' if affine is not None else 'NO'}")

    doc.close()
    print(f"Wrote previews → {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
