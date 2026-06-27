"""POC: DeepSeek-OCR-2 on S3 CMP answer-sheet crops/pages (via HF Space or local GPU)."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import cv2
import fitz

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from answer_sheet_align import (  # noqa: E402
    crop_rgb,
    load_exam_templates,
    prepare_aligned_page,
    render_page,
    resolve_bc_regions,
    warp_norm_box,
)

_LAYOUT = _HERE / "s3_cmp_term02_layout.json"
HF_SPACE = "merterbak/DeepSeek-OCR-Demo"

MATCH_PROMPT = (
    "<|grounding|>This is one cell from a Hong Kong school exam answer table. "
    "Ignore the printed sub-question label like (a) or (b). "
    "Read only the single handwritten capital letter (A, B, C, D, or E) that the student wrote. "
    "Reply with exactly one letter."
)
TF_PROMPT = (
    "<|grounding|>This is one cell from a True/False answer row. "
    "Ignore printed labels. Read only the handwritten T or F. Reply with one letter."
)
FILL_PROMPT = (
    "<|grounding|>This is one fill-in-the-blank answer line from a school ICT exam. "
    "Ignore the printed (a)-(e) label. Transcribe only the handwritten English word or filename."
)
PAGE_PROMPT = (
    "<|grounding|>Convert this exam answer sheet page to markdown. "
    "Preserve table structure for matching answers and true/false rows."
)


def _render_student_pages(pdf: Path, student_index: int, *, scale: float = 2.0) -> list[tuple[str, object]]:
    layout = json.loads(_LAYOUT.read_text(encoding="utf-8"))
    templates = load_exam_templates(layout, layout_path=_LAYOUT)
    pps = layout["pages_per_student"]
    roles = layout["page_roles"]
    doc = fitz.open(pdf)
    base = student_index * pps
    out: list[tuple[str, object]] = []
    for i, role in enumerate(roles):
        page = doc[base + i]
        page_img = render_page(page, scale=scale)
        page_img, _, _ = prepare_aligned_page(page_img, role, layout, templates=templates)
        out.append((role, page_img))
    doc.close()
    return out


def _save_page_png(page_img, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(dest), cv2.cvtColor(page_img.rgb, cv2.COLOR_RGB2BGR))
    return dest


def _collect_cell_crops(page_img, layout_p1: dict, dest: Path) -> list[dict[str, str]]:
    regions = resolve_bc_regions(page_img, layout_p1)
    if regions is None:
        return []
    items: list[dict[str, str]] = []
    if regions.match_cell_boxes:
        for ri, row in enumerate(regions.match_cell_boxes, start=1):
            for ci, box in enumerate(row):
                ch = chr(ord("a") + ci)
                cid = f"match_q{ri}_{ch}"
                path = dest / f"{cid}.png"
                cv2.imwrite(str(path), cv2.cvtColor(crop_rgb(page_img, box), cv2.COLOR_RGB2BGR))
                items.append({"id": cid, "path": str(path), "kind": "match"})
    if regions.tf_cell_boxes:
        for ci, box in enumerate(regions.tf_cell_boxes):
            ch = chr(ord("a") + ci)
            cid = f"tf_q1_{ch}"
            path = dest / f"{cid}.png"
            cv2.imwrite(str(path), cv2.cvtColor(crop_rgb(page_img, box), cv2.COLOR_RGB2BGR))
            items.append({"id": cid, "path": str(path), "kind": "tf"})
    return items


def _collect_fill_crops(page_img, layout_p2: dict, affine, dest: Path) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for spec in layout_p2.get("fill_lines", [])[:5]:
        box = tuple(spec["box"])
        px = warp_norm_box(box, page_img, affine)
        path = dest / f"{spec['id']}.png"
        cv2.imwrite(str(path), cv2.cvtColor(crop_rgb(page_img, px), cv2.COLOR_RGB2BGR))
        items.append({"id": spec["id"], "path": str(path), "kind": "fill"})
    return items


def _hf_client():
    try:
        from gradio_client import Client, handle_file
    except ImportError as e:
        raise SystemExit("pip install gradio_client") from e
    import os

    token = (os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_HUB_TOKEN") or "").strip()
    kwargs = {"hf_token": token} if token else {}
    return Client(HF_SPACE, **kwargs), handle_file


def _run_hf_ocr(image_path: Path, *, task: str, custom_prompt: str = "") -> dict[str, str]:
    client, handle_file = _hf_client()
    result = client.predict(
        handle_file(str(image_path)),
        None,
        task,
        custom_prompt,
        1,
        api_name="/run",
    )
    text, markdown, raw, _img, _gallery = result
    return {"text": text or "", "markdown": markdown or "", "raw": raw or ""}


def _pick_letter(text: str, alphabet: str) -> str:
    text = text.upper()
    for ch in text:
        if ch in alphabet:
            return ch
    return ""


def _local_ocr(image_path: Path, prompt: str) -> str:
    import os
    import torch
    from transformers import AutoModel, AutoTokenizer

    model_name = "deepseek-ai/DeepSeek-OCR-2"
    device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
    dtype = torch.bfloat16 if device == "cuda" else torch.float16
    attn = "flash_attention_2" if device == "cuda" else "sdpa"
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModel.from_pretrained(
        model_name,
        _attn_implementation=attn,
        trust_remote_code=True,
        use_safetensors=True,
        torch_dtype=dtype,
    )
    model = model.eval().to(device)
    out_dir = image_path.parent / "_ds_ocr_tmp"
    out_dir.mkdir(exist_ok=True)
    full_prompt = f"<image>\n{prompt}"
    model.infer(
        tokenizer,
        prompt=full_prompt,
        image_file=str(image_path),
        output_path=str(out_dir),
        base_size=1024,
        image_size=768,
        crop_mode=True,
        save_results=False,
    )
    for p in sorted(out_dir.glob("*.txt")):
        return p.read_text(encoding="utf-8", errors="ignore").strip()
    return ""


def run_poc(
    pdf: Path,
    *,
    student_index: int,
    backend: str,
    out_dir: Path,
    pages_only: bool,
) -> dict:
    layout = json.loads(_LAYOUT.read_text(encoding="utf-8"))
    templates = load_exam_templates(layout, layout_path=_LAYOUT)
    spec_path = pdf.parent.parent / "25_26_S3_CMP_Term02_Exam.spec.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8")) if spec_path.exists() else {}
    meta = spec.get("meta", {})

    out_dir.mkdir(parents=True, exist_ok=True)
    pages = _render_student_pages(pdf, student_index)
    payload: dict = {
        "backend": backend,
        "student_index": student_index,
        "hf_space": HF_SPACE if backend == "hf" else None,
        "pages": [],
        "cells": [],
        "summary": {},
    }

    for role, page_img in pages:
        png = _save_page_png(page_img, out_dir / f"page_{role}.png")
        page_rec = {"role": role, "image": str(png), "ocr": {}}
        if backend == "hf":
            if role == "answer_p1":
                page_rec["ocr"] = _run_hf_ocr(png, task="📝 Free OCR", custom_prompt="")
            else:
                page_rec["ocr"] = _run_hf_ocr(
                    png, task="📋 Markdown", custom_prompt=PAGE_PROMPT.replace("<|grounding|>", "")
                )
        elif backend == "local":
            page_rec["ocr"]["text"] = _local_ocr(png, PAGE_PROMPT)
        payload["pages"].append(page_rec)

        if pages_only:
            continue

        if role == "answer_p1":
            cells = _collect_cell_crops(page_img, layout["regions"]["answer_p1"], out_dir / "cells_p1")
        else:
            _, affine, _ = prepare_aligned_page(page_img, role, layout, templates=templates)
            cells = _collect_fill_crops(page_img, layout["regions"]["answer_p2"], affine, out_dir / "cells_p2")

        for cell in cells:
            path = Path(cell["path"])
            if backend == "hf":
                if cell["kind"] == "match":
                    ocr = _run_hf_ocr(path, task="✏️ Custom", custom_prompt=MATCH_PROMPT)
                elif cell["kind"] == "tf":
                    ocr = _run_hf_ocr(path, task="✏️ Custom", custom_prompt=TF_PROMPT)
                else:
                    ocr = _run_hf_ocr(path, task="✏️ Custom", custom_prompt=FILL_PROMPT)
            else:
                prompt = {"match": MATCH_PROMPT, "tf": TF_PROMPT, "fill": FILL_PROMPT}[cell["kind"]]
                ocr = {"text": _local_ocr(path, prompt)}
            letter = ""
            if cell["kind"] == "match":
                letter = _pick_letter(ocr.get("text", "") + ocr.get("raw", ""), "ABCDE")
            elif cell["kind"] == "tf":
                letter = _pick_letter(ocr.get("text", "") + ocr.get("raw", ""), "TF")
            payload["cells"].append({**cell, "ocr": ocr, "parsed": letter or ocr.get("text", "").strip()})

    match_rows: list[str] = []
    for qi in (1, 2):
        letters = []
        for ch in "abcde":
            cid = f"match_q{qi}_{ch}"
            hit = next((c for c in payload["cells"] if c["id"] == cid), None)
            letters.append((hit or {}).get("parsed", ""))
        match_rows.append("".join(letters))
    tf = "".join(
        (next((c for c in payload["cells"] if c["id"] == f"tf_q1_{ch}"), {}) or {}).get("parsed", "")
        for ch in "abcde"
    )
    payload["summary"] = {
        "match_got": match_rows,
        "match_key": meta.get("matching_answers"),
        "tf_got": tf,
        "tf_key": meta.get("tf_answers"),
        "fill_got": [
            (next((c for c in payload["cells"] if c["id"] == f"fill_q1_{ch}"), {}) or {}).get("parsed", "")
            for ch in "abcde"
        ],
        "fill_key_q1": (meta.get("fill_answers") or [[]])[0] if meta.get("fill_answers") else [],
    }
    return payload


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf", type=Path, help="Reordered scan PDF")
    ap.add_argument("--student", type=int, default=0)
    ap.add_argument(
        "--backend",
        choices=["hf", "local"],
        default="hf",
        help="hf=HuggingFace Space (no local GPU); local=CUDA/MPS inference",
    )
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--pages-only", action="store_true", help="Only OCR full pages, skip per-cell crops")
    ap.add_argument("--cells-only", action="store_true", help="Skip full-page OCR (faster cell POC)")
    args = ap.parse_args(argv)

    if args.cells_only:
        args.pages_only = True

    print(f"DeepSeek-OCR-2 POC ({args.backend}) student {args.student} …")
    payload = run_poc(
        args.pdf,
        student_index=args.student,
        backend=args.backend,
        out_dir=args.output,
        pages_only=args.pages_only,
    )
    out_json = args.output / "poc_deepseek_ocr2.json"
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
    print(f"Wrote {out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
