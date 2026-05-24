"""Apply stored paragraph profiles (tab stops, alignment, style) when rendering."""

from __future__ import annotations

from typing import TYPE_CHECKING

from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_TAB_ALIGNMENT
from docx.shared import Emu, Length, Pt

from paper_format.schema.paragraph_profile import ParagraphProfile

if TYPE_CHECKING:
    from docx.text.paragraph import Paragraph

_ALIGN = {
    "LEFT": WD_ALIGN_PARAGRAPH.LEFT,
    "CENTER": WD_ALIGN_PARAGRAPH.CENTER,
    "RIGHT": WD_ALIGN_PARAGRAPH.RIGHT,
    "JUSTIFY": WD_ALIGN_PARAGRAPH.JUSTIFY,
    "DISTRIBUTE": WD_ALIGN_PARAGRAPH.DISTRIBUTE,
}

_TAB = {
    "LEFT": WD_TAB_ALIGNMENT.LEFT,
    "CENTER": WD_TAB_ALIGNMENT.CENTER,
    "RIGHT": WD_TAB_ALIGNMENT.RIGHT,
    "DECIMAL": WD_TAB_ALIGNMENT.DECIMAL,
    "BAR": WD_TAB_ALIGNMENT.BAR,
}

_LINE_RULE = {
    "SINGLE": WD_LINE_SPACING.SINGLE,
    "ONE_POINT_FIVE": WD_LINE_SPACING.ONE_POINT_FIVE,
    "DOUBLE": WD_LINE_SPACING.DOUBLE,
    "AT_LEAST": WD_LINE_SPACING.AT_LEAST,
    "EXACTLY": WD_LINE_SPACING.EXACTLY,
    "MULTIPLE": WD_LINE_SPACING.MULTIPLE,
}


def apply_paragraph_profile(paragraph: Paragraph, profile: ParagraphProfile) -> None:
    """Restore paragraph-level formatting from a template profile."""
    pf = paragraph.paragraph_format

    if profile.style_name:
        try:
            paragraph.style = profile.style_name
        except KeyError:
            pass

    if profile.alignment:
        pf.alignment = _ALIGN.get(profile.alignment, WD_ALIGN_PARAGRAPH.LEFT)
    else:
        pf.alignment = None

    if profile.left_indent_emu is not None:
        pf.left_indent = Length(profile.left_indent_emu)
    if profile.first_line_indent_emu is not None:
        pf.first_line_indent = Length(profile.first_line_indent_emu)

    if profile.space_before_pt is not None:
        pf.space_before = Pt(profile.space_before_pt)
    if profile.space_after_pt is not None:
        pf.space_after = Pt(profile.space_after_pt)

    if profile.line_spacing_rule:
        rule = _LINE_RULE.get(profile.line_spacing_rule)
        if rule is not None:
            pf.line_spacing_rule = rule
            if profile.line_spacing_pt is not None:
                pf.line_spacing = Pt(profile.line_spacing_pt)

    if profile.tab_stops:
        pf.tab_stops.clear_all()
        for ts in profile.tab_stops:
            align = _TAB.get(ts.alignment, WD_TAB_ALIGNMENT.LEFT)
            pf.tab_stops.add_tab_stop(Emu(ts.position_emu), align)


def apply_code_paragraph_spacing(
    paragraph: Paragraph,
    profile: ParagraphProfile,
    *,
    before: bool = True,
    after: bool = True,
) -> None:
    """Visual gap before/after code block (Word spacing, not extra blank paragraphs)."""
    pf = paragraph.paragraph_format
    if before and profile.space_before_pt is None:
        pf.space_before = Pt(6)
    if after and profile.space_after_pt is None:
        pf.space_after = Pt(6)


def apply_run_defaults(paragraph: Paragraph, profile: ParagraphProfile) -> None:
    """Apply default run font from profile to all runs (after text is set)."""
    rd = profile.run_defaults
    if not rd:
        return
    for r in paragraph.runs:
        if rd.font_name:
            r.font.name = rd.font_name
        if rd.font_size_pt is not None:
            r.font.size = Pt(rd.font_size_pt)
        if rd.bold is not None:
            r.font.bold = rd.bold
        if rd.italic is not None:
            r.font.italic = rd.italic
