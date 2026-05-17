#!/usr/bin/env python3
"""Extract a .docx (zip) into raw files and normalize XML for diffing.

Usage:
  python shared-tools/paper-formatter/docx_xml/extract_docx_xml.py --input <file.docx> --output-dir <dir>

Output layout:
  <output-dir>/raw/         extracted docx contents
  <output-dir>/normalized/  normalized XML + copied non-XML files

Normalization goals:
- Stable attribute ordering
- Remove indentation-only whitespace between tags
- Pretty-print with consistent indentation/newlines
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET


def _is_whitespace_only(s: str | None) -> bool:
    return s is not None and s.strip() == ""


def _strip_insignificant_whitespace(elem: ET.Element) -> None:
    """Remove indentation/newline-only text nodes to stabilize diffs."""
    # Keep meaningful whitespace (non-empty after strip).
    if _is_whitespace_only(elem.text):
        elem.text = None
    if _is_whitespace_only(elem.tail):
        elem.tail = None
    for child in list(elem):
        _strip_insignificant_whitespace(child)


def _sort_attributes(elem: ET.Element) -> None:
    # Element.attrib is a dict; rewrite with sorted key order for stable output.
    if elem.attrib:
        elem.attrib = dict(sorted(elem.attrib.items(), key=lambda kv: kv[0]))
    for child in list(elem):
        _sort_attributes(child)


def _indent(tree: ET.ElementTree, space: str = "  ") -> None:
    # Python 3.9+: ET.indent exists.
    indent_fn = getattr(ET, "indent", None)
    if indent_fn is None:
        return
    indent_fn(tree, space=space)


def normalize_xml_bytes(xml_bytes: bytes, src: Path) -> bytes:
    """Normalize XML bytes. Falls back to original bytes on parse errors."""
    try:
        parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
        root = ET.fromstring(xml_bytes, parser=parser)
        _strip_insignificant_whitespace(root)
        _sort_attributes(root)
        tree = ET.ElementTree(root)
        _indent(tree, space="  ")

        # ET.tostring doesn't include XML declaration by default; write to bytes via ElementTree.
        import io

        buf = io.BytesIO()
        tree.write(buf, encoding="utf-8", xml_declaration=True, short_empty_elements=True)
        buf.write(b"\n")
        return buf.getvalue()
    except Exception:
        # Some parts may not be XML (or may contain odd constructs). Keep raw for comparison.
        return xml_bytes


def extract_docx(input_docx: Path, raw_dir: Path) -> None:
    if raw_dir.exists():
        shutil.rmtree(raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(input_docx, "r") as zf:
        # Protect against zip-slip
        for member in zf.infolist():
            member_path = Path(member.filename)
            if member_path.is_absolute() or ".." in member_path.parts:
                raise ValueError(f"Unsafe path in zip: {member.filename}")
        zf.extractall(raw_dir)


def normalize_tree(raw_dir: Path, normalized_dir: Path) -> None:
    if normalized_dir.exists():
        shutil.rmtree(normalized_dir)
    normalized_dir.mkdir(parents=True, exist_ok=True)

    for path in raw_dir.rglob("*"):
        if path.is_dir():
            continue
        rel = path.relative_to(raw_dir)
        out_path = normalized_dir / rel
        out_path.parent.mkdir(parents=True, exist_ok=True)

        data = path.read_bytes()
        if path.suffix.lower() == ".xml":
            data = normalize_xml_bytes(data, src=path)
        out_path.write_bytes(data)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Extract .docx and normalize XML for diffing")
    ap.add_argument("--input", required=True, help="Path to .docx")
    ap.add_argument("--output-dir", required=True, help="Output directory")
    args = ap.parse_args(argv)

    input_docx = Path(args.input).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()

    if not input_docx.exists():
        print(f"ERROR: input not found: {input_docx}", file=sys.stderr)
        return 2
    if input_docx.suffix.lower() != ".docx":
        print(f"ERROR: input must be .docx: {input_docx}", file=sys.stderr)
        return 2

    output_dir.mkdir(parents=True, exist_ok=True)

    raw_dir = output_dir / "raw"
    normalized_dir = output_dir / "normalized"

    extract_docx(input_docx, raw_dir)
    normalize_tree(raw_dir, normalized_dir)

    print(f"Extracted:   {input_docx}")
    print(f"Raw:         {raw_dir}")
    print(f"Normalized:  {normalized_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
