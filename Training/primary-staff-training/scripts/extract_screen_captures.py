#!/usr/bin/env python3
"""Extract embedded images from Screen Capture.docx in document order."""

from __future__ import annotations

import re
import shutil
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

DOCX = Path(__file__).resolve().parent.parent / "docs" / "screen-captures" / "Screen Capture.docx"
OUT_DIR = DOCX.parent / "extracted"


def parse_document_order(docx: zipfile.ZipFile) -> list[str]:
    """Return media filenames in document order (e.g. media/image1.png)."""
    rels_xml = docx.read("word/_rels/document.xml.rels")
    rels_root = ET.fromstring(rels_xml)
    rid_to_target: dict[str, str] = {}
    for rel in rels_root:
        rid = rel.attrib.get("Id", "")
        target = rel.attrib.get("Target", "")
        if "media/" in target:
            rid_to_target[rid] = target if target.startswith("media/") else f"media/{target.split('/')[-1]}"

    doc_xml = docx.read("word/document.xml").decode("utf-8")
    embed_attr = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed"
    # Walk document in order via r:embed occurrences
    order: list[str] = []
    seen: set[str] = set()
    for m in re.finditer(r'r:embed="(rId\d+)"', doc_xml):
        rid = m.group(1)
        target = rid_to_target.get(rid)
        if target and target not in seen:
            order.append(target)
            seen.add(target)
    return order


def main() -> None:
    if not DOCX.exists():
        raise SystemExit(f"Missing: {DOCX}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(DOCX) as zf:
        order = parse_document_order(zf)
        manifest_lines = ["# Screen captures extracted from Screen Capture.docx\n"]
        manifest_lines.append("| # | File | Source | Size |")
        manifest_lines.append("|---|------|--------|------|")

        for i, media_path in enumerate(order, start=1):
            src_name = media_path.split("/")[-1]
            ext = Path(src_name).suffix or ".png"
            out_name = f"screen-{i:02d}{ext}"
            out_path = OUT_DIR / out_name

            data = zf.read(f"word/{media_path}")
            out_path.write_bytes(data)
            size_kb = len(data) // 1024
            manifest_lines.append(f"| {i} | `{out_name}` | `{src_name}` | {size_kb} KB |")
            print(f"[{i:02d}] {out_name} ← {src_name} ({size_kb} KB)")

        # Also copy raw media/ folder for reference
        raw_dir = OUT_DIR / "raw"
        raw_dir.mkdir(exist_ok=True)
        for name in zf.namelist():
            if name.startswith("word/media/"):
                raw_name = name.split("/")[-1]
                (raw_dir / raw_name).write_bytes(zf.read(name))

        manifest = OUT_DIR / "README.md"
        manifest.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
        print(f"\nExtracted {len(order)} images → {OUT_DIR}")
        print(f"Manifest: {manifest}")


if __name__ == "__main__":
    main()
