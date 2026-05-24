"""Extract paragraph formatting profiles from reference DOCX."""

from __future__ import annotations

from typing import TYPE_CHECKING

from paper_format.schema.paragraph_profile import ParagraphProfile, RunDefaults, TabStopProfile

if TYPE_CHECKING:
    from docx.text.paragraph import Paragraph


def _emu(val) -> int | None:
    if val is None:
        return None
    return int(val)


def _pt(val) -> float | None:
    if val is None:
        return None
    return float(val.pt)


def _alignment_name(val) -> str | None:
    if val is None:
        return None
    return val.name if hasattr(val, "name") else str(val)


def _line_spacing_rule(pf) -> tuple[str | None, float | None]:
    rule = pf.line_spacing_rule
    if rule is None:
        return None, None
    name = rule.name if hasattr(rule, "name") else str(rule)
    ls = pf.line_spacing
    pt = float(ls.pt) if ls is not None and hasattr(ls, "pt") else None
    return name, pt


def extract_paragraph_profile(paragraph: Paragraph, *, role: str) -> ParagraphProfile:
    pf = paragraph.paragraph_format
    tab_stops: list[TabStopProfile] = []
    if pf.tab_stops:
        for ts in pf.tab_stops:
            tab_stops.append(
                TabStopProfile(
                    position_emu=int(ts.position),
                    alignment=_alignment_name(ts.alignment) or "LEFT",
                )
            )

    run_defaults: RunDefaults | None = None
    for r in paragraph.runs:
        if not (r.text or "").strip():
            continue
        run_defaults = RunDefaults(
            font_name=r.font.name,
            font_size_pt=_pt(r.font.size),
            bold=r.font.bold,
            italic=r.font.italic,
        )
        break

    rule, ls_pt = _line_spacing_rule(pf)
    style_name = paragraph.style.name if paragraph.style else None

    return ParagraphProfile(
        role=role,
        style_name=style_name,
        alignment=_alignment_name(pf.alignment),
        tab_stops=tab_stops,
        left_indent_emu=_emu(pf.left_indent),
        first_line_indent_emu=_emu(pf.first_line_indent),
        space_before_pt=_pt(pf.space_before),
        space_after_pt=_pt(pf.space_after),
        line_spacing_rule=rule,
        line_spacing_pt=ls_pt,
        run_defaults=run_defaults,
    )
