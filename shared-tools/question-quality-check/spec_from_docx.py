"""Convert DOCX/PDF exam files to exam spec JSON (for reference papers)."""
from __future__ import annotations

import re
from pathlib import Path

from quality_lib import extract_lines, extract_mcq_stems, extract_written_units
from exam_spec import build_spec, make_item


def _concepts_from_written(text: str, label: str) -> list[str]:
    concepts: list[str] = []
    if label:
        concepts.append(label.split("-")[-1].strip()[:40])
    for line in text.splitlines():
        m = re.match(r"^\d+\.\s*(.+?)(?:\t|\s*\()", line.strip())
        if m:
            topic = m.group(1).strip()
            if topic and topic not in concepts:
                concepts.append(topic)
    return concepts[:5]


def docx_to_spec(path: Path, *, meta: dict | None = None) -> dict:
    path = path.expanduser().resolve()
    lines = extract_lines(path)
    items: list[dict] = []

    for m in extract_mcq_stems(lines):
        items.append(
            make_item(
                f"mcq-{m['index']:02d}",
                "mcq",
                m["full"],
                marks=1,
                stem=m["stem"],
            )
        )

    for u in extract_written_units(lines):
        sec = u["section"].replace("部", "").lower()  # 乙 -> 乙
        uid = u["index"]
        label = u.get("label") or ""
        items.append(
            make_item(
                f"{sec}-{uid:02d}",
                f"section_{sec}",
                u["text"],
                label=label,
                concepts=_concepts_from_written(u["text"], label),
            )
        )

    default_meta = {
        "source": str(path),
        "source_name": path.name,
    }
    if meta:
        default_meta.update(meta)
    return build_spec(default_meta, items)
