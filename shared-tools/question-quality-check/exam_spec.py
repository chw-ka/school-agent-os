"""
Exam content as JSON (exam spec) for fast compare-before-render workflow.

Schema version 1:
{
  "version": 1,
  "meta": {
    "title", "subject", "level",
    "footer": {
      "academic_year": "2025-2026",
      "level": "中三級",
      "term_exam": "下學期考試",
      "subject": "電腦認知"
    }
  },
  "items": [
    {
      "id": "mcq-01",
      "section": "mcq",
      "text": "<comparable plain text>",
      "marks": 1,
      "concepts": ["進制", "十六進制"],
      "answer": "B",
      "title": "optional short label"
    }
  ]
}
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional

SPEC_VERSION = 1


@dataclass
class ExamItem:
    id: str
    section: str
    text: str
    marks: Optional[float] = None
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class DuplicateEntry:
    candidate_id: str
    reference: str
    reference_id: str
    similarity: float
    match_type: str
    candidate_text: str
    reference_text: str


@dataclass
class DuplicateReport:
    candidate: str
    threshold: float
    references_checked: list[str] = field(default_factory=list)
    duplicates: list[DuplicateEntry] = field(default_factory=list)

    @property
    def has_duplicates(self) -> bool:
        return len(self.duplicates) > 0

    @property
    def regenerate_ids(self) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for d in sorted(self.duplicates, key=lambda x: (-x.similarity, x.candidate_id)):
            if d.candidate_id not in seen:
                seen.add(d.candidate_id)
                out.append(d.candidate_id)
        return out

    def to_dict(self) -> dict:
        return {
            "threshold": self.threshold,
            "candidate": self.candidate,
            "has_duplicates": self.has_duplicates,
            "regenerate_ids": self.regenerate_ids,
            "references_checked": self.references_checked,
            "duplicate_count": len(self.duplicates),
            "duplicates": [asdict(d) for d in self.duplicates],
        }


def load_spec(path: Path) -> dict:
    path = path.expanduser().resolve()
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Exam spec must be a JSON object.")
    if data.get("version", 1) != SPEC_VERSION:
        raise ValueError(f"Unsupported spec version: {data.get('version')}")
    return data


def save_spec(path: Path, spec: dict) -> None:
    path = path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    spec = dict(spec)
    spec.setdefault("version", SPEC_VERSION)
    path.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")


def spec_items(spec: dict) -> list[ExamItem]:
    raw = spec.get("items")
    if not isinstance(raw, list):
        raise ValueError('Exam spec must contain array "items".')
    items: list[ExamItem] = []
    for i, row in enumerate(raw, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"items[{i}] must be an object.")
        item_id = row.get("id")
        section = row.get("section")
        text = row.get("text")
        if not item_id or not section or not text:
            raise ValueError(f"items[{i}] requires id, section, text.")
        marks = row.get("marks")
        meta = {k: v for k, v in row.items() if k not in ("id", "section", "text", "marks")}
        items.append(
            ExamItem(
                id=str(item_id),
                section=str(section),
                text=str(text).strip(),
                marks=float(marks) if marks is not None else None,
                meta=meta,
            )
        )
    return items


def make_item(
    item_id: str,
    section: str,
    text: str,
    *,
    marks: Optional[float] = None,
    **meta: Any,
) -> dict:
    row: dict[str, Any] = {"id": item_id, "section": section, "text": text.strip()}
    if marks is not None:
        row["marks"] = marks
    row.update(meta)
    return row


def build_spec(meta: dict, items: list[dict]) -> dict:
    return {"version": SPEC_VERSION, "meta": meta, "items": items}
