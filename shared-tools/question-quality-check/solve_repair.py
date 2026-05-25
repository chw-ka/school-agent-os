"""LLM repair a single spec item using solve_review feedback."""
from __future__ import annotations

import re
from typing import Any

from exam_spec import make_item
from solve_llm import LlmConfig, llm_json_completion

_REPAIR_SYSTEM = """You rewrite ONE Hong Kong Form 5 ICT exam question for a school paper.
Keep the same item_id, section, marks total, and curriculum concepts.
Fix all repair_constraints. Include all data needed to answer (tables inline or column lists).
Use tab-indented subparts: \\t(a)\\t...\\t(N分)
Do not copy DSE stems verbatim. Traditional Chinese unless the original was English.

Reply JSON only:
{
  "text": "full new question text",
  "notes": "what you fixed"
}
"""


def repair_item_with_llm(
    *,
    cfg: LlmConfig,
    slot: dict[str, Any],
    item: dict[str, Any],
    feedback: dict[str, Any],
    blueprint_concepts: list[str] | None = None,
) -> dict[str, Any]:
    """Return new spec item dict (same id/section)."""
    constraints = feedback.get("repair_constraints") or []
    missing = feedback.get("missing") or []
    kinds = feedback.get("issue_kinds") or []
    user = "\n".join(
        [
            f"item_id: {item.get('id')}",
            f"section: {item.get('section')}",
            f"marks: {item.get('marks')}",
            f"concepts: {', '.join(blueprint_concepts or slot.get('concepts') or [])}",
            f"issue_kinds: {', '.join(kinds)}",
            "",
            "repair_constraints:",
            *[f"- {c}" for c in constraints],
            "",
            "missing:",
            *[f"- {m}" for m in missing],
            "",
            "=== Current text (broken) ===",
            str(item.get("text") or ""),
        ]
    )
    data = llm_json_completion(cfg=cfg, system=_REPAIR_SYSTEM, user=user)
    new_text = str(data.get("text") or "").strip()
    if not new_text:
        raise ValueError(f"LLM repair returned empty text for {item.get('id')}")

    sid = str(item.get("id"))
    section = str(item.get("section"))
    marks = item.get("marks", slot.get("marks", 1))
    concepts = list(item.get("concepts") or slot.get("concepts") or [])
    row = make_item(
        sid,
        section,
        new_text,
        marks=marks,
        concepts=concepts,
        dse_source=f"generated://repair/{sid}",
        composition="llm_repair",
        repair_notes=str(data.get("notes") or ""),
    )
    if section == "mcq":
        letter = str(item.get("answer") or "A")[:1].upper()
        if re.search(r"[A-D]\.\s", new_text):
            row["answer"] = letter
    return row
