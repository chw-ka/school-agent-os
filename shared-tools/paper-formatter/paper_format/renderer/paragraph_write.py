"""Write paragraph text using stored role profiles."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from docx_inplace import CODE_FONT, BODY_FONT, is_program_text, is_sql_text, set_paragraph_text_distribute
from paper_format.f5_ict_roles import (
    mcq_line_kind,
    mcq_role_for_kind,
    written_line_kind,
    written_role_for_kind,
)
from paper_format.extractor.f5_ict_extract import get_role_profile
from paper_format.renderer.profile_apply import apply_paragraph_profile, apply_run_defaults

if TYPE_CHECKING:
    from docx.text.paragraph import Paragraph


def _font_for_line(text: str, role: str) -> str:
    if role in ("mcq.code_left", "mcq.code_center", "written.code", "written.sql"):
        return CODE_FONT
    if is_program_text(text) or is_sql_text(text):
        return CODE_FONT
    return BODY_FONT


def set_paragraph_with_role(
    paragraph: Paragraph,
    text: str,
    role: str,
    profile: dict[str, Any],
) -> None:
    """Apply role profile (tabs, alignment, spacing) then write text with correct font."""
    prof = get_role_profile(profile, role)
    if prof:
        apply_paragraph_profile(paragraph, prof)
    set_paragraph_text_distribute(paragraph, text)
    if not text.strip():
        return
    font = _font_for_line(text, role)
    for r in paragraph.runs:
        r.font.name = font
    if prof:
        apply_run_defaults(paragraph, prof)


def write_mcq_line(
    paragraph: Paragraph,
    text: str,
    profile: dict[str, Any],
    *,
    collapsed: bool = False,
    code_before: bool = False,
    code_after: bool = False,
) -> None:
    kind = mcq_line_kind(text, collapsed=collapsed)
    code_center = kind == "code" and is_sql_text(text) and not text.startswith("\t")
    role = mcq_role_for_kind(kind, code_center=code_center)
    prof = get_role_profile(profile, role)
    if prof:
        apply_paragraph_profile(paragraph, prof)
    set_paragraph_text_distribute(paragraph, text)
    if not text.strip():
        return
    if kind == "code" and prof:
        from paper_format.renderer.profile_apply import apply_code_paragraph_spacing

        apply_code_paragraph_spacing(
            paragraph,
            prof,
            before=code_before,
            after=code_after,
        )
    font = _font_for_line(text, role)
    for r in paragraph.runs:
        r.font.name = font
    if prof:
        apply_run_defaults(paragraph, prof)


def write_written_line(paragraph: Paragraph, text: str, profile: dict[str, Any]) -> None:
    kind = written_line_kind(text)
    role = written_role_for_kind(kind)
    set_paragraph_with_role(paragraph, text, role, profile)
