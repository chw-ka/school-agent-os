#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class CheckResult:
    ok: bool
    message: str


def _run(cmd: list[str]) -> None:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"Command failed ({p.returncode}): {' '.join(cmd)}\n\n{p.stdout}")


def _safe_extract_zip(zip_path: Path, out_dir: Path) -> None:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.infolist():
            mp = Path(member.filename)
            if mp.is_absolute() or ".." in mp.parts:
                raise ValueError(f"Unsafe zip member path: {member.filename}")
        zf.extractall(out_dir)


def _strip_all_text_nodes(elem: ET.Element) -> None:
    # Remove text/tails everywhere so comparison checks structure only.
    elem.text = None
    elem.tail = None
    # Stop comparing below paragraph/run-level: content inside paragraphs can change
    # (runs, bookmarks, tabs, breaks) when replacing text. For a "format check" we
    # compare table/paragraph skeleton + paragraph properties only.
    if elem.tag.endswith("}p"):
        # Keep pPr if present; drop the rest.
        kept = []
        for child in list(elem):
            if child.tag.endswith("}pPr"):
                kept.append(child)
        for child in list(elem):
            elem.remove(child)
        for child in kept:
            elem.append(child)
        return

    # Stop comparing below run-level.
    if elem.tag.endswith("}r"):
        for child in list(elem):
            elem.remove(child)
        return
    for child in list(elem):
        _strip_all_text_nodes(child)


def _sort_attribs(elem: ET.Element) -> None:
    # Ignore xml:space since it's text-related and can legitimately change
    # when only the run text changes (we compare structure, not content).
    xml_space = "{http://www.w3.org/XML/1998/namespace}space"
    if xml_space in elem.attrib:
        elem.attrib.pop(xml_space, None)
    if elem.attrib:
        elem.attrib = dict(sorted(elem.attrib.items(), key=lambda kv: kv[0]))
    for child in list(elem):
        _sort_attribs(child)


def _canonical_xml_hash(xml_path: Path) -> str:
    data = xml_path.read_bytes()
    try:
        parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
        root = ET.fromstring(data, parser=parser)
    except Exception:
        # Non-XML: hash raw bytes
        return hashlib.sha256(data).hexdigest()

    _strip_all_text_nodes(root)
    _sort_attribs(root)
    # Canonical-ish bytes
    out = ET.tostring(root, encoding="utf-8", short_empty_elements=True)
    return hashlib.sha256(out).hexdigest()

def _first_structure_diff(a: ET.Element, b: ET.Element, path: str = "") -> str | None:
    """
    Return a short path describing the first structural mismatch (text already stripped).
    Path format: /tag[idx]/tag[idx]...
    """
    if a.tag != b.tag:
        return f"{path}: tag {a.tag!r} != {b.tag!r}"
    if dict(a.attrib) != dict(b.attrib):
        return f"{path}/{a.tag}: attribs differ"
    a_children = list(a)
    b_children = list(b)
    if len(a_children) != len(b_children):
        return f"{path}/{a.tag}: child count {len(a_children)} != {len(b_children)}"
    for i, (ac, bc) in enumerate(zip(a_children, b_children), start=1):
        sub = _first_structure_diff(ac, bc, path=f"{path}/{a.tag}[{i}]")
        if sub:
            return sub
    return None


def _structure_diff_hint(xml_a: Path, xml_b: Path) -> str:
    try:
        ra = ET.fromstring(
            xml_a.read_bytes(),
            parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True)),
        )
        rb = ET.fromstring(
            xml_b.read_bytes(),
            parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True)),
        )
        _strip_all_text_nodes(ra)
        _strip_all_text_nodes(rb)
        _sort_attribs(ra)
        _sort_attribs(rb)
        hint = _first_structure_diff(ra, rb, path="")
        return hint or "Unknown structural diff (hash differs but traversal matched)."
    except Exception as e:
        return f"Failed to compute diff hint: {e}"


def _collect_compare_files(extracted_dir: Path) -> list[Path]:
    """
    Compare the usual formatting-critical WordprocessingML parts.
    We only include files that exist in the template; candidates may have extra files.
    """
    word = extracted_dir / "word"
    candidates = [
        word / "document.xml",
        word / "styles.xml",
        word / "numbering.xml",
        word / "settings.xml",
    ]
    # headers/footers if present
    candidates += sorted(word.glob("header*.xml"))
    candidates += sorted(word.glob("footer*.xml"))
    # theme can affect layout (fonts)
    candidates += [extracted_dir / "word" / "theme" / "theme1.xml"]
    return [p for p in candidates if p.exists()]


def compare_docx_structure(template_docx: Path, candidate_docx: Path, tmp_dir: Path) -> CheckResult:
    t_dir = tmp_dir / "template"
    c_dir = tmp_dir / "candidate"
    _safe_extract_zip(template_docx, t_dir)
    _safe_extract_zip(candidate_docx, c_dir)

    template_files = _collect_compare_files(t_dir)
    if not template_files:
        return CheckResult(False, f"No comparable XML parts found in template: {template_docx}")

    diffs: list[str] = []
    for t_file in template_files:
        rel = t_file.relative_to(t_dir)
        c_file = c_dir / rel
        if not c_file.exists():
            diffs.append(f"Missing in candidate: {rel}")
            continue
        th = _canonical_xml_hash(t_file)
        ch = _canonical_xml_hash(c_file)
        if th != ch:
            extra = ""
            if rel.as_posix() == "word/document.xml":
                extra = " — " + _structure_diff_hint(t_file, c_file)
            diffs.append(f"Structure differs: {rel}{extra}")

    if diffs:
        return CheckResult(False, "Structural mismatches found:\n- " + "\n- ".join(diffs))
    return CheckResult(True, "OK: Candidate matches template structure (text ignored).")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description="Regenerate a DOCX from a template and verify internal XML structure matches (ignoring text)."
    )
    ap.add_argument("--template-docx", required=True, help="Template DOCX path (source of truth).")
    ap.add_argument("--generator", required=True, help="Generator script to run (python).")
    ap.add_argument("--output-docx", required=True, help="Output DOCX path to (re)generate.")
    ap.add_argument("--date", default="__________", help="Date string passed to generator.")
    ap.add_argument("--time", default="__________", help="Time string passed to generator.")
    ap.add_argument("--tmp-dir", default=".tmp/docx-structure-check", help="Temp dir under workspace.")
    args = ap.parse_args(argv)

    template_docx = Path(args.template_docx).expanduser().resolve()
    output_docx = Path(args.output_docx).expanduser().resolve()
    generator = Path(args.generator).expanduser().resolve()
    tmp_dir = Path(args.tmp_dir).expanduser().resolve()

    if not template_docx.exists():
        print(f"ERROR: template not found: {template_docx}", file=sys.stderr)
        return 2
    if not generator.exists():
        print(f"ERROR: generator not found: {generator}", file=sys.stderr)
        return 2

    # 1) Regenerate output docx
    _run(
        [
            sys.executable,
            str(generator),
            "--template",
            str(template_docx),
            "--output",
            str(output_docx),
            "--date",
            str(args.date),
            "--time",
            str(args.time),
        ]
    )

    # 2) Compare structure
    res = compare_docx_structure(template_docx, output_docx, tmp_dir=tmp_dir)
    print(res.message)
    return 0 if res.ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

