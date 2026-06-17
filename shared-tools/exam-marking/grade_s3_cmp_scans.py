"""Crop answer-sheet regions and OCR for S3 CMP Term02 (sections B–E) via PaddleOCR."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import cv2
import fitz

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from answer_sheet_align import (  # noqa: E402
    crop_rgb,
    detect_page2_regions,
    detect_table_cells,
    load_exam_templates,
    prepare_aligned_page,
    resolve_bc_regions,
    resolve_page2_regions,
    render_page,
    warp_norm_box,
    _split_answer_row,
)

_LAYOUT = _HERE / "s3_cmp_term02_layout.json"


from fill_word_match import match_fill_word, normalize_fill  # noqa: E402


def grade_bcd(extracted: dict[str, str], spec: dict[str, Any]) -> dict[str, Any]:
    meta = spec["meta"]
    scores: dict[str, Any] = {
        "section_b": 0,
        "section_c": 0,
        "section_d": 0,
        "section_e": None,
        "sa_manual": True,
        "details": {},
    }

    for qi, key in enumerate(meta.get("matching_answers") or [], start=1):
        got = extracted.get(f"match_q{qi}", "")
        scores["details"][f"match_q{qi}"] = {"expected": key, "got": got}
        for a, b in zip(key, got):
            if a == b:
                scores["section_b"] += 1

    tf_key = meta.get("tf_answers") or ""
    got_tf = extracted.get("tf_q1", "")
    scores["details"]["tf_q1"] = {"expected": tf_key, "got": got_tf}
    for a, b in zip(tf_key, got_tf):
        if a == b:
            scores["section_c"] += 1

    fill_blocks = meta.get("fill_answers") or []
    word_banks = meta.get("fill_word_banks") or []
    for bi, block in enumerate(fill_blocks, start=1):
        bank = word_banks[bi - 1] if bi - 1 < len(word_banks) else []
        got_words: list[str] = []
        resolved_words: list[str] = []
        cell_details: list[dict[str, Any]] = []
        for j, word in enumerate(block):
            cell_id = f"fill_q{bi}_{chr(ord('a') + j)}"
            raw = extracted.get(cell_id, "")
            matched, sim_score, _ = match_fill_word(raw, bank) if bank else ("", 0, raw)
            resolved = matched or normalize_fill(raw)
            got_words.append(normalize_fill(raw))
            resolved_words.append(resolved)
            correct = normalize_fill(matched or "") == normalize_fill(word) if matched else False
            if correct:
                scores["section_d"] += 1
            cell_details.append(
                {
                    "id": cell_id,
                    "expected": word,
                    "ocr": raw,
                    "resolved": matched or None,
                    "similarity": sim_score,
                    "correct": correct,
                }
            )
        scores["details"][f"fill_q{bi}"] = {
            "expected": block,
            "got": got_words,
            "resolved": resolved_words,
            "cells": cell_details,
        }

    sa_ids = [k for k in extracted if k.startswith("sa_q")]
    scores["details"]["section_e"] = {
        "manual_only": True,
        "note": "戊部為長答；OCR 不可靠，請人手批改。",
        "extracted": {k: extracted[k] for k in sorted(sa_ids)},
    }

    scores["total_auto"] = scores["section_b"] + scores["section_c"] + scores["section_d"]
    return scores


def _ocr_imports():
    from paddle_cell_ocr import (  # noqa: E402
        read_bc_tables_on_page,
        read_fill_lines_on_page,
        read_sa_blocks_on_page,
    )

    return read_bc_tables_on_page, read_fill_lines_on_page, read_sa_blocks_on_page


def extract_student(
    pages: list[fitz.Page],
    layout: dict,
    *,
    crop_dir: Path | None,
    student_idx: int,
    crops_only: bool,
    templates: dict | None = None,
) -> dict[str, str]:
    roles = layout["page_roles"]
    regions = layout["regions"]
    out: dict[str, str] = {}
    align_meta: dict[str, str] = {}

    for page, role in zip(pages, roles, strict=True):
        page_img = render_page(page)
        page_img, affine, align_method = prepare_aligned_page(
            page_img, role, layout, templates=templates
        )
        align_meta[role] = align_method
        spec = regions[role]

        if role == "answer_p1":
            bc_regions = resolve_bc_regions(page_img, spec)
            bc_method = bc_regions.method if bc_regions else "no_markers"
            if crops_only:
                match_rows = [""] * 2
                tf_row = ""
            else:
                read_bc_tables_on_page, _, _ = _ocr_imports()
                match_rows, tf_row, bc_method = read_bc_tables_on_page(page_img, layout_p1=spec)
            for i, ans in enumerate(match_rows, start=1):
                out[f"match_q{i}"] = ans
            out["tf_q1"] = tf_row

            if crop_dir:
                _save_bc_crops(
                    page_img,
                    crop_dir / f"student_{student_idx:03d}",
                    bc_regions,
                    bc_method,
                )
        else:
            fill_specs = spec.get("fill_lines", [])
            fill_boxes = [tuple(x["box"]) for x in fill_specs]
            fill_ids = [x["id"] for x in fill_specs]
            if crops_only:
                fills = [""] * len(fill_ids)
            else:
                _, read_fill_lines_on_page, _ = _ocr_imports()
                fills = read_fill_lines_on_page(page_img, fill_boxes, affine=affine)
            for fid, text in zip(fill_ids, fills, strict=True):
                out[fid] = text

            sa_specs = spec.get("sa_blocks", [])
            sa_boxes = [tuple(x["box"]) for x in sa_specs]
            sa_ids = [x["id"] for x in sa_specs]
            if crops_only:
                sas = [""] * len(sa_ids)
            else:
                _, _, read_sa_blocks_on_page = _ocr_imports()
                sas = read_sa_blocks_on_page(page_img, sa_boxes, affine=affine, layout_p2=spec)
            for sid, text in zip(sa_ids, sas, strict=True):
                out[sid] = text

            if crop_dir:
                dest = crop_dir / f"student_{student_idx:03d}"
                dest.mkdir(parents=True, exist_ok=True)
                p2 = resolve_page2_regions(page_img, spec)
                if p2:
                    for item, box in zip(fill_specs, p2.fill_boxes, strict=True):
                        cv2.imwrite(
                            str(dest / f"{item['id']}.png"),
                            cv2.cvtColor(crop_rgb(page_img, box), cv2.COLOR_RGB2BGR),
                        )
                    for item, box in zip(sa_specs, p2.sa_boxes, strict=True):
                        cv2.imwrite(
                            str(dest / f"{item['id']}.png"),
                            cv2.cvtColor(crop_rgb(page_img, box), cv2.COLOR_RGB2BGR),
                        )
                else:
                    for item in fill_specs:
                        px = warp_norm_box(tuple(item["box"]), page_img, affine)
                        cv2.imwrite(
                            str(dest / f"{item['id']}.png"),
                            cv2.cvtColor(crop_rgb(page_img, px), cv2.COLOR_RGB2BGR),
                        )
                    for item in sa_specs:
                        px = warp_norm_box(tuple(item["box"]), page_img, affine)
                        cv2.imwrite(
                            str(dest / f"{item['id']}.png"),
                            cv2.cvtColor(crop_rgb(page_img, px), cv2.COLOR_RGB2BGR),
                        )

    out["_aligned"] = json.dumps(align_meta)
    return out


def _save_bc_crops(
    page_img,
    dest: Path,
    regions,
    method: str,
) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    if regions is None:
        return
    cv2.imwrite(
        str(dest / "match_block.png"),
        cv2.cvtColor(crop_rgb(page_img, regions.match_block), cv2.COLOR_RGB2BGR),
    )
    cv2.imwrite(
        str(dest / "tf_block.png"),
        cv2.cvtColor(crop_rgb(page_img, regions.tf_block), cv2.COLOR_RGB2BGR),
    )
    for ri, row_box in enumerate(regions.match_rows, start=1):
        row_img = crop_rgb(page_img, row_box)
        cv2.imwrite(str(dest / f"match_q{ri}_row.png"), cv2.cvtColor(row_img, cv2.COLOR_RGB2BGR))
        cell_boxes = (
            regions.match_cell_boxes[ri - 1]
            if regions.match_cell_boxes and ri - 1 < len(regions.match_cell_boxes)
            else None
        )
        if cell_boxes:
            for ci, box in enumerate(cell_boxes):
                ch = chr(ord("a") + ci)
                cv2.imwrite(
                    str(dest / f"match_q{ri}_{ch}.png"),
                    cv2.cvtColor(crop_rgb(page_img, box), cv2.COLOR_RGB2BGR),
                )
        else:
            for ci, cell in enumerate(_split_answer_row(row_img)):
                ch = chr(ord("a") + ci)
                cv2.imwrite(
                    str(dest / f"match_q{ri}_{ch}.png"),
                    cv2.cvtColor(cell, cv2.COLOR_RGB2BGR),
                )
    tf_img = crop_rgb(page_img, regions.tf_row)
    if regions.tf_cell_boxes:
        for ci, box in enumerate(regions.tf_cell_boxes):
            ch = chr(ord("a") + ci)
            cv2.imwrite(
                str(dest / f"tf_q1_{ch}.png"),
                cv2.cvtColor(crop_rgb(page_img, box), cv2.COLOR_RGB2BGR),
            )
    else:
        for ci, cell in enumerate(_split_answer_row(tf_img)):
            ch = chr(ord("a") + ci)
            cv2.imwrite(
                str(dest / f"tf_q1_{ch}.png"),
                cv2.cvtColor(cell, cv2.COLOR_RGB2BGR),
            )
    (dest / "_align_method.txt").write_text(method, encoding="utf-8")


def _save_table_crops(
    page_img,
    affine,
    match_spec: dict,
    tf_spec: dict,
    dest: Path,
) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for name, spec in ("match_block", match_spec), ("tf_block", tf_spec):
        px = warp_norm_box(tuple(spec["box"]), page_img, affine)
        table = crop_rgb(page_img, px)
        cv2.imwrite(str(dest / f"{name}.png"), cv2.cvtColor(table, cv2.COLOR_RGB2BGR))
        cells = detect_table_cells(table, rows=spec["rows"])
        if not cells:
            continue
        for ri, row in enumerate(cells, start=1):
            for ci, cell in enumerate(row):
                ch = chr(ord("a") + ci)
                key = "tf_q1" if name == "tf_block" else f"match_q{ri}"
                cv2.imwrite(
                    str(dest / f"{key}_{ch}.png"),
                    cv2.cvtColor(cell, cv2.COLOR_RGB2BGR),
                )


def run_batch(
    pdf_path: Path,
    spec_path: Path,
    *,
    crop_dir: Path | None,
    limit: int | None,
    crops_only: bool,
) -> list[dict[str, Any]]:
    layout = json.loads(_LAYOUT.read_text(encoding="utf-8"))
    templates = load_exam_templates(layout, layout_path=_LAYOUT)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    doc = fitz.open(pdf_path)
    pps = layout["pages_per_student"]
    n_students = len(doc) // pps
    if limit:
        n_students = min(n_students, limit)

    results: list[dict[str, Any]] = []
    for si in range(n_students):
        pages = [doc[si * pps + k] for k in range(pps)]
        extracted = extract_student(
            pages, layout, crop_dir=crop_dir, student_idx=si, crops_only=crops_only,
            templates=templates,
        )
        align_info = extracted.pop("_aligned", "{}")
        scores = {} if crops_only else grade_bcd(extracted, spec)
        results.append(
            {
                "student_index": si,
                "scan_pages": [si * pps, si * pps + 1],
                "aligned": json.loads(align_info),
                "extracted": extracted,
                "scores": scores,
            }
        )
        if (si + 1) % 10 == 0:
            print(f"  {si + 1}/{n_students}", flush=True)
    doc.close()
    return results


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf", type=Path, help="Reordered scan PDF (2 pages per student)")
    ap.add_argument("--spec", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, default=None)
    ap.add_argument("--crop-dir", type=Path, default=None, help="Save crop PNGs per student")
    ap.add_argument("--crops-only", action="store_true", help="Only save crops; skip OCR/grading")
    ap.add_argument("--limit", type=int, default=None, help="Process first N students only")
    args = ap.parse_args(argv)
    if not args.crops_only and not args.output:
        ap.error("--output is required unless --crops-only")
    if args.crops_only and not args.crop_dir:
        ap.error("--crop-dir is required with --crops-only")

    print(f"Processing {args.pdf.name} (PaddleOCR + per-page align)...")
    results = run_batch(
        args.pdf,
        args.spec,
        crop_dir=args.crop_dir,
        limit=args.limit,
        crops_only=args.crops_only,
    )
    payload = {
        "students": results,
        "count": len(results),
        "ocr_engine": "paddleocr-2.7+cell_letter+fuzzy_fill",
        "alignment": "zipgrade_markers+orb_template",
        "sa_grading": "manual_only",
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote {args.output} ({len(results)} students)")
    else:
        print(f"Cropped {len(results)} students → {args.crop_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
