"""Resolve render-time table grids for solve review (spec text + synthetic tables)."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_FMT = Path(__file__).resolve().parents[1] / "paper-formatter"
if str(_FMT) not in sys.path:
    sys.path.insert(0, str(_FMT))

from f5_ict_written_tables import table_grids_for_pick  # noqa: E402


def grid_to_markdown(name: str, grid: list[list[str]]) -> str:
    if not grid:
        return ""
    lines = [f"### {name}", ""]
    if len(grid) == 1 and len(grid[0]) == 1:
        lines.append(grid[0][0])
        return "\n".join(lines)
    widths = [max(len(str(row[c])) for row in grid) for c in range(len(grid[0]))]
    for row in grid:
        cells = [str(row[c]).ljust(widths[c]) if c < len(row) else "" for c in range(len(widths))]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def tables_for_slot(slot_id: str, text: str) -> list[dict[str, Any]]:
    """Tables that would appear on the rendered paper for this written slot."""
    pick = {"text": text, "id": slot_id}
    rows: list[dict[str, Any]] = []
    for name, grid in table_grids_for_pick(slot_id, pick):
        rows.append({"name": name, "grid": grid, "markdown": grid_to_markdown(name, grid)})
    return rows


def tables_markdown_for_slot(slot_id: str, text: str) -> str:
    parts = [t["markdown"] for t in tables_for_slot(slot_id, text) if t.get("markdown")]
    if not parts:
        return ""
    return "\n\n".join(parts)


def sync_item_tables_in_spec(spec: dict[str, Any]) -> int:
    """Write item.tables from render builders (source of truth for solve + future render)."""
    n = 0
    for row in spec.get("items") or []:
        sid = str(row.get("id") or "")
        sec = str(row.get("section") or "")
        if sec not in ("section_b", "section_c"):
            continue
        tables = tables_for_slot(sid, str(row.get("text") or ""))
        if tables:
            row["tables"] = [{"name": t["name"], "grid": t["grid"]} for t in tables]
            n += 1
    return n
