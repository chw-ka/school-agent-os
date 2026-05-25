"""Phase 3: compare rendered DOCX tables with expected grids; optional PDF page PNGs."""
from __future__ import annotations

import base64
import re
import sys
from pathlib import Path
from typing import Any

from docx import Document

_FMT = Path(__file__).resolve().parents[1] / "paper-formatter"
if str(_FMT) not in sys.path:
    sys.path.insert(0, str(_FMT))

from written_slot_ranges import WRITTEN_SLOT_PARAGRAPHS  # noqa: E402
from solve_tables import tables_for_slot  # noqa: E402


def _slot_table_count_expected(slot_id: str, text: str) -> int:
    return len(tables_for_slot(slot_id, text))


def docx_table_notes_for_spec(docx_path: Path, spec: dict[str, Any]) -> dict[str, str]:
    """Per written slot: note if paper may be missing render tables (global + per-slot expected)."""
    docx_path = docx_path.expanduser().resolve()
    if not docx_path.is_file():
        return {}
    doc = Document(str(docx_path))
    actual_tables = len(doc.tables)

    per_slot: list[tuple[str, int]] = []
    for row in spec.get("items") or []:
        sid = str(row.get("id") or "")
        if str(row.get("section") or "") not in ("section_b", "section_c"):
            continue
        exp = _slot_table_count_expected(sid, str(row.get("text") or ""))
        if exp:
            per_slot.append((sid, exp))

    expected_total = sum(n for _, n in per_slot)
    notes: dict[str, str] = {}
    if expected_total and actual_tables < expected_total:
        gap = expected_total - actual_tables
        for sid, exp in per_slot:
            notes[sid] = (
                f"DOCX has {actual_tables} table(s) total but render expects {expected_total} "
                f"(this slot needs {exp}). About {gap} table(s) may be missing on paper."
            )
    elif expected_total:
        for sid, exp in per_slot:
            notes[sid] = f"DOCX has {actual_tables} table(s); this slot expects {exp} at render."
    return notes


def render_docx_pages_png(docx_path: Path, out_dir: Path, *, dpi: int = 150) -> list[Path]:
    """Export PDF pages as PNG when sibling PDF exists (same stem as DOCX)."""
    pdf = docx_path.with_suffix(".pdf")
    if not pdf.is_file():
        return []
    import fitz

    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    doc = fitz.open(pdf)
    for i in range(doc.page_count):
        pix = doc.load_page(i).get_pixmap(dpi=dpi)
        p = out_dir / f"page_{i + 1:02d}.png"
        pix.save(str(p))
        paths.append(p)
    return paths


def png_to_b64(path: Path) -> str:
    return base64.standard_b64encode(path.read_bytes()).decode("ascii")
