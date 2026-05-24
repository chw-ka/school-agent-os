"""
In-place DOCX text edits that preserve template layout (runs, paragraphs, styles).

Cover pages: never assign cell.text or rebuild the cover from scratch. Edit only the
existing cover paragraphs that need to change (often just the paper title line).
"""

from __future__ import annotations

import re
from copy import deepcopy
from dataclasses import dataclass
from typing import Iterable, Optional, Sequence

CODE_FONT = "Courier New"
BODY_FONT = "新細明體"

_PSEUDO_KW = re.compile(
    r"\b(FOR|WHILE|REPEAT|UNTIL|IF|THEN|ELSE|ENDIF|ENDFOR|ENDWHILE|OUTPUT|"
    r"PROCEDURE|ENDPROCEDURE|CALL|RETURN|PUSH|POP|BEGIN|END)\b",
    re.IGNORECASE,
)
_PYTHON_KW = re.compile(r"^\s*(def |print\(|import |while |if |for |elif )", re.IGNORECASE)
_PSEUDO_ASSIGN = re.compile(r"^\s*\w+\s*←")

# Chinese CMP cover (table 0, cell 0,0) — 20 paragraphs in 24_25 templates.
ZH_COVER_PARA = {
    "school": 3,
    "year_term": 4,
    "level": 6,
    "paper": 7,
    "date": 9,
    "time": 10,
    "duration": 11,
    "pages": 12,
    "total": 13,
}

# English CMP written cover — 43 paragraphs in 24_25 S3 WrittenExam template.
EN_COVER_PARA = {
    "school": 4,
    "year_term": 5,
    "subject": 7,
    "paper": 8,
    "date": 10,
    "time": 11,
    "duration": 12,
    "pages": 13,
    "total": 14,
}


def is_program_text(text: str) -> bool:
    """True for pseudocode / Python / similar program lines."""
    s = text.strip()
    if not s:
        return False
    if "←" in s or "→" in s:
        return True
    if _PSEUDO_ASSIGN.match(s):
        return True
    if _PSEUDO_KW.search(s):
        return True
    if _PYTHON_KW.match(s):
        return True
    if re.search(r"^\s*\w+\s*=\s*\w", s) and not s.endswith("？"):
        return True
    return False


def is_sql_text(text: str) -> bool:
    s = text.strip()
    if not s:
        return False
    return bool(
        re.match(
            r"^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|FROM|WHERE|"
            r"UNION|BEGIN|COMMIT|ROLLBACK|MINUS|JOIN|GROUP|HAVING|SET|VALUES|INTO)\b",
            s,
            re.IGNORECASE,
        )
    )


def set_paragraph_text_distribute(paragraph, text: str) -> None:
    """
    Set paragraph text while preserving existing run count and formatting.

    Never assigns paragraph.text (which rebuilds runs and shifts layout).
    """
    runs = list(paragraph.runs)
    if not runs:
        if text != "":
            paragraph.add_run(text)
        return

    lens = [max(1, len(r.text)) for r in runs]
    remaining = text
    for i, (r, ln) in enumerate(zip(runs, lens)):
        is_last = i == len(runs) - 1
        if is_last:
            r.text = remaining if remaining != "" else " "
            remaining = ""
        else:
            seg = remaining[:ln]
            remaining = remaining[ln:]
            r.text = seg if seg != "" else " "


def set_paragraph_text_rich(paragraph, text: str) -> None:
    """Write paragraph text; pseudocode / Python / SQL use Courier New."""
    # Template rows may be CENTER (e.g. SQL snippet) — MCQ options must stay left.
    paragraph.paragraph_format.alignment = None
    set_paragraph_text_distribute(paragraph, text)
    if not text.strip():
        return
    font = (
        CODE_FONT
        if (is_program_text(text) or is_sql_text(text))
        else BODY_FONT
    )
    for r in paragraph.runs:
        r.font.name = font


def replace_in_paragraph_runs(paragraph, needle: str, replacement: str) -> None:
    """Replace substring within existing runs (keeps run boundaries)."""
    for r in paragraph.runs:
        if needle in r.text:
            r.text = r.text.replace(needle, replacement)


def clone_table_cell_content(source_cell, target_cell) -> None:
    """Deep-copy all XML inside a table cell (paragraphs, spacing, styles)."""
    target_tc = target_cell._tc
    for child in list(target_tc):
        target_tc.remove(child)
    for child in source_cell._tc:
        target_tc.append(deepcopy(child))


def set_paragraph_primary_run(paragraph, text: str) -> None:
    """
    Set visible text while keeping paragraph properties; collapse extras into run 0.
    Prefer this over distribute when replacing whole metadata lines on EN-layout covers.
    """
    runs = list(paragraph.runs)
    if not runs:
        if text:
            paragraph.add_run(text)
        return
    runs[0].text = text if text else ""
    for r in runs[1:]:
        r.text = ""


@dataclass(frozen=True)
class ZhCoverPatch:
    """Only non-None fields are written to the cover cell."""

    school: Optional[str] = None
    year_term: Optional[str] = None
    term_needle: Optional[str] = None
    term_replacement: Optional[str] = None
    level: Optional[str] = None
    paper: Optional[str] = None
    date_line: Optional[str] = None
    time_line: Optional[str] = None
    duration_line: Optional[str] = None
    pages_line: Optional[str] = None
    total_line: Optional[str] = None


@dataclass(frozen=True)
class EnCoverPatch:
    """Only non-None fields are written to the cover cell."""

    school: Optional[str] = None
    year_term: Optional[str] = None
    subject: Optional[str] = None
    paper: Optional[str] = None
    date_line: Optional[str] = None
    time_line: Optional[str] = None
    duration_line: Optional[str] = None
    pages_line: Optional[str] = None
    total_line: Optional[str] = None


def _para_map_set(paras, idx_map: dict[str, int], key: str, text: Optional[str]) -> None:
    if text is None:
        return
    set_paragraph_text_distribute(paras[idx_map[key]], text)


def apply_cmp_cover_zh(cover_cell, patch: ZhCoverPatch) -> None:
    """
    Update Chinese CMP cover in-place. Instructions paragraphs are never touched.
    """
    paras = cover_cell.paragraphs
    if len(paras) < 20:
        raise ValueError(
            f"Unexpected Chinese cover structure ({len(paras)} paragraphs; expected >= 20)."
        )

    idx = ZH_COVER_PARA
    _para_map_set(paras, idx, "school", patch.school)
    if patch.term_needle and patch.term_replacement:
        replace_in_paragraph_runs(paras[idx["year_term"]], patch.term_needle, patch.term_replacement)
    if patch.year_term is not None:
        if not patch.term_needle or patch.term_needle in paras[idx["year_term"]].text:
            set_paragraph_text_distribute(paras[idx["year_term"]], patch.year_term)
    _para_map_set(paras, idx, "level", patch.level)
    _para_map_set(paras, idx, "paper", patch.paper)
    _para_map_set(paras, idx, "date", patch.date_line)
    _para_map_set(paras, idx, "time", patch.time_line)
    _para_map_set(paras, idx, "duration", patch.duration_line)
    _para_map_set(paras, idx, "pages", patch.pages_line)
    _para_map_set(paras, idx, "total", patch.total_line)


def clear_table_cells(table) -> None:
    """Blank every cell while preserving table dimensions and styles."""
    for row in table.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                set_paragraph_text_distribute(p, "")


def clear_all_tables_except(
    doc,
    keep_indices: Iterable[int] = (0,),
) -> None:
    """
    Blank all tables before writing new question content.

    Default keeps index 0 (cover). Other tables are cleared; populate only those
    required by the current paper via apply_*_table_content().
    """
    keep = set(keep_indices)
    for i, table in enumerate(doc.tables):
        if i in keep:
            continue
        clear_table_cells(table)


def delete_table(table) -> None:
    """Remove a table element from the document body."""
    element = table._element
    element.getparent().remove(element)


def delete_tables_except(doc, keep_indices: Iterable[int]) -> None:
    """Physically remove tables not in keep_indices (delete high indices first)."""
    keep = set(keep_indices)
    for i in range(len(doc.tables) - 1, -1, -1):
        if i not in keep:
            delete_table(doc.tables[i])


def apply_cmp_cover_zh_on_en_layout(
    cover_cell,
    patch: ZhCoverPatch,
    *,
    instructions: Sequence[str],
    instructions_start: int = 17,
) -> None:
    """
    Chinese cover text on the 24_25 English written-exam cover layout (43 paragraphs).

    Use after clone_table_cell_content from 24_25_S3_CMP_Term2_WrittenExam.docx.
    """
    paras = cover_cell.paragraphs
    if len(paras) < 21:
        raise ValueError(
            f"Unexpected EN-layout cover ({len(paras)} paragraphs; expected >= 21)."
        )

    idx = EN_COVER_PARA
    if patch.school is not None:
        set_paragraph_primary_run(paras[idx["school"]], patch.school)
    if patch.year_term is not None:
        set_paragraph_primary_run(paras[idx["year_term"]], patch.year_term)
    if patch.level is not None:
        set_paragraph_primary_run(paras[idx["subject"]], patch.level)
    if patch.paper is not None:
        set_paragraph_primary_run(paras[idx["paper"]], patch.paper)
    if patch.date_line is not None:
        set_paragraph_primary_run(paras[idx["date"]], patch.date_line)
    if patch.time_line is not None:
        set_paragraph_primary_run(paras[idx["time"]], patch.time_line)
    if patch.duration_line is not None:
        set_paragraph_primary_run(paras[idx["duration"]], patch.duration_line)
    if patch.pages_line is not None:
        set_paragraph_primary_run(paras[idx["pages"]], patch.pages_line)
    if patch.total_line is not None:
        set_paragraph_primary_run(paras[idx["total"]], patch.total_line)

    for i, line in enumerate(instructions):
        pi = instructions_start + i
        if pi >= len(paras):
            break
        set_paragraph_primary_run(paras[pi], line)


def regenerate_cmp_zh_cover_from_en_reference(
    *,
    target_doc,
    reference_doc,
    patch: ZhCoverPatch,
    instructions: Sequence[str],
    table_index: int = 0,
) -> None:
    """Replace cover cell with EN reference layout, then apply Chinese fields."""
    ref_cell = reference_doc.tables[table_index].cell(0, 0)
    tgt_cell = target_doc.tables[table_index].cell(0, 0)
    clone_table_cell_content(ref_cell, tgt_cell)
    apply_cmp_cover_zh_on_en_layout(tgt_cell, patch, instructions=instructions)


def apply_cmp_cover_en(cover_cell, patch: EnCoverPatch) -> None:
    """Update English CMP written cover in-place. Instructions paragraphs are never touched."""
    paras = cover_cell.paragraphs
    if len(paras) < 21:
        raise ValueError(
            f"Unexpected English cover structure ({len(paras)} paragraphs; expected >= 21)."
        )

    idx = EN_COVER_PARA
    _para_map_set(paras, idx, "school", patch.school)
    _para_map_set(paras, idx, "year_term", patch.year_term)
    _para_map_set(paras, idx, "subject", patch.subject)
    _para_map_set(paras, idx, "paper", patch.paper)
    _para_map_set(paras, idx, "date", patch.date_line)
    _para_map_set(paras, idx, "time", patch.time_line)
    _para_map_set(paras, idx, "duration", patch.duration_line)
    _para_map_set(paras, idx, "pages", patch.pages_line)
    _para_map_set(paras, idx, "total", patch.total_line)
