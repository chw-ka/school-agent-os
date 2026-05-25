"""Phase 4: aggregate solve_review feedback into generation rules for future slots."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from solve_review_core import SolveReviewReport, feedback_by_slot

RULES_VERSION = 1
_DEFAULT_RULES = Path(__file__).resolve().parents[2] / "Subjects/DSE-ICT/question-bank/solve_generation_rules.json"


def load_generation_rules(path: Path | None = None) -> dict[str, Any]:
    p = (path or _DEFAULT_RULES).expanduser().resolve()
    if not p.is_file():
        return {"version": RULES_VERSION, "updated_at": "", "by_slot": {}, "global": {"issue_counts": {}}}
    return json.loads(p.read_text(encoding="utf-8"))


def save_generation_rules(rules: dict[str, Any], path: Path | None = None) -> Path:
    p = (path or _DEFAULT_RULES).expanduser().resolve()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(rules, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def merge_solve_report_into_rules(
    report: SolveReviewReport,
    rules: dict[str, Any] | None = None,
    *,
    rules_path: Path | None = None,
) -> dict[str, Any]:
    """Increment issue_counts and append repair_constraints per slot."""
    rules = dict(rules or load_generation_rules(rules_path))
    rules.setdefault("version", RULES_VERSION)
    by_slot: dict[str, Any] = dict(rules.get("by_slot") or {})
    global_counts: dict[str, int] = dict((rules.get("global") or {}).get("issue_counts") or {})

    fb = feedback_by_slot(report)
    for slot_id, block in fb.items():
        slot_rules = dict(by_slot.get(slot_id) or {})
        counts: dict[str, int] = dict(slot_rules.get("issue_counts") or {})
        for kind in block.get("issue_kinds") or []:
            counts[kind] = counts.get(kind, 0) + 1
            global_counts[kind] = global_counts.get(kind, 0) + 1
        slot_rules["issue_counts"] = counts
        existing = list(slot_rules.get("repair_constraints") or [])
        for c in block.get("repair_constraints") or []:
            if c not in existing:
                existing.append(c)
        slot_rules["repair_constraints"] = existing[-20:]
        slot_rules["last_verdict"] = block.get("verdict")
        by_slot[slot_id] = slot_rules

    rules["by_slot"] = by_slot
    rules["global"] = {"issue_counts": global_counts}
    rules["updated_at"] = report.generated_at
    return rules


def constraints_for_slot(slot_id: str, rules: dict[str, Any] | None = None) -> list[str]:
    rules = rules or load_generation_rules()
    block = (rules.get("by_slot") or {}).get(slot_id) or {}
    return list(block.get("repair_constraints") or [])
