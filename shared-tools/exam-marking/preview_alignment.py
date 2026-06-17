"""Draw alignment + detected table grid on sample pages for manual verification."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import fitz

from answer_sheet_align import (
    crop_rgb,
    detect_page2_regions,
    load_exam_templates,
    prepare_aligned_page,
    resolve_bc_regions,
    resolve_page2_regions,
    find_markers,
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
    templates = load_exam_templates(layout, layout_path=_LAYOUT)
    doc = fitz.open(args.pdf)
    si = args.student
    p1 = doc[si * 2]
    p2 = doc[si * 2 + 1]
    args.output_dir.mkdir(parents=True, exist_ok=True)

    for label, page, role in (("p1", p1, "answer_p1"), ("p2", p2, "answer_p2")):
        img = render_page(page)
        img, affine, align_method = prepare_aligned_page(img, role, layout, templates=templates)
        vis = img.rgb.copy()
        markers = find_markers(img.gray)
        if markers is not None:
            for x, y in markers:
                cv2.circle(vis, (int(x), int(y)), 8, (0, 255, 0), 2)
        spec = layout["regions"][role]
        if role == "answer_p1":
            regions = resolve_bc_regions(img, spec, markers)
            if regions:
                for ri, box in enumerate(regions.match_rows, start=1):
                    x0, y0, x1, y1 = box
                    cv2.rectangle(vis, (x0, y0), (x1, y1), (255, 0, 0), 2)
                    cv2.imwrite(
                        str(args.output_dir / f"student{si:03d}_match_q{ri}.png"),
                        cv2.cvtColor(crop_rgb(img, box), cv2.COLOR_RGB2BGR),
                    )
                    if regions.match_cell_boxes and ri - 1 < len(regions.match_cell_boxes):
                        for ci, cbox in enumerate(regions.match_cell_boxes[ri - 1]):
                            cv2.rectangle(vis, cbox[:2], cbox[2:], (255, 128, 0), 1)
                x0, y0, x1, y1 = regions.tf_row
                cv2.rectangle(vis, (x0, y0), (x1, y1), (0, 0, 255), 2)
                if regions.tf_cell_boxes:
                    for cbox in regions.tf_cell_boxes:
                        cv2.rectangle(vis, cbox[:2], cbox[2:], (128, 0, 255), 1)
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
            p2 = resolve_page2_regions(img, spec)
            if p2:
                for box in p2.fill_boxes:
                    cv2.rectangle(vis, box[:2], box[2:], (0, 255, 255), 1)
                for box in p2.sa_boxes:
                    cv2.rectangle(vis, box[:2], box[2:], (255, 0, 255), 2)
            else:
                for item in spec.get("fill_lines", []):
                    px = warp_norm_box(tuple(item["box"]), img, affine)
                    cv2.rectangle(vis, px[:2], px[2:], (0, 0, 255), 1)
        cv2.imwrite(
            str(args.output_dir / f"student{si:03d}_{label}_overlay.png"),
            cv2.cvtColor(vis, cv2.COLOR_RGB2BGR),
        )
        print(f"{label}: align={align_method}, markers={'yes' if markers is not None else 'NO'}")

    doc.close()
    print(f"Wrote previews → {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
