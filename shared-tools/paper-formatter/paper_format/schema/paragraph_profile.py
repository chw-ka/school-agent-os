"""Serializable paragraph formatting profile (tab stops, alignment, fonts, spacing)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class TabStopProfile:
    position_emu: int
    alignment: str  # LEFT | CENTER | RIGHT | DECIMAL | BAR

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> TabStopProfile:
        return cls(position_emu=int(d["position_emu"]), alignment=str(d["alignment"]))


@dataclass
class RunDefaults:
    font_name: str | None = None
    font_size_pt: float | None = None
    bold: bool | None = None
    italic: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> RunDefaults:
        return cls(
            font_name=d.get("font_name"),
            font_size_pt=d.get("font_size_pt"),
            bold=d.get("bold"),
            italic=d.get("italic"),
        )


@dataclass
class ParagraphProfile:
    """Formatting to reproduce when writing new content into a paragraph slot."""

    role: str
    style_name: str | None = None
    alignment: str | None = None  # None = inherit / clear to default
    tab_stops: list[TabStopProfile] = field(default_factory=list)
    left_indent_emu: int | None = None
    first_line_indent_emu: int | None = None
    space_before_pt: float | None = None
    space_after_pt: float | None = None
    line_spacing_rule: str | None = None  # auto | exact | at_least | multiple
    line_spacing_pt: float | None = None
    run_defaults: RunDefaults | None = None
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"role": self.role}
        if self.style_name:
            d["style_name"] = self.style_name
        if self.alignment:
            d["alignment"] = self.alignment
        if self.tab_stops:
            d["tab_stops"] = [t.to_dict() for t in self.tab_stops]
        for key in (
            "left_indent_emu",
            "first_line_indent_emu",
            "space_before_pt",
            "space_after_pt",
            "line_spacing_rule",
            "line_spacing_pt",
        ):
            val = getattr(self, key)
            if val is not None:
                d[key] = val
        if self.run_defaults:
            d["run_defaults"] = self.run_defaults.to_dict()
        if self.notes:
            d["notes"] = self.notes
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ParagraphProfile:
        return cls(
            role=str(d["role"]),
            style_name=d.get("style_name"),
            alignment=d.get("alignment"),
            tab_stops=[TabStopProfile.from_dict(t) for t in d.get("tab_stops") or []],
            left_indent_emu=d.get("left_indent_emu"),
            first_line_indent_emu=d.get("first_line_indent_emu"),
            space_before_pt=d.get("space_before_pt"),
            space_after_pt=d.get("space_after_pt"),
            line_spacing_rule=d.get("line_spacing_rule"),
            line_spacing_pt=d.get("line_spacing_pt"),
            run_defaults=(
                RunDefaults.from_dict(d["run_defaults"]) if d.get("run_defaults") else None
            ),
            notes=str(d.get("notes") or ""),
        )
