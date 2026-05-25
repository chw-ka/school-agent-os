"""Solve review — LLM attempts each exam item like a S5 student (text + render tables)."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from exam_spec import load_spec, spec_items
from solve_llm import LlmConfig, llm_json_completion, llm_json_with_image
from solve_tables import sync_item_tables_in_spec, tables_markdown_for_slot

Verdict = Literal["solvable", "blocked", "uncertain"]

ISSUE_KINDS = (
    "missing_table",
    "vague_prompt",
    "wrong_column_ref",
    "contradictory_data",
    "no_unique_answer",
    "ambiguous_wording",
    "missing_algorithm",
    "scenario_mismatch",
    "incomplete_erd",
    "mcq_all_plausible",
    "docx_table_missing",
    "other",
)

_SOLVE_SYSTEM = """You are a Hong Kong Form 5 ICT student taking a school exam.
Answer ONLY using information in the question stem and any tables provided.
Do not invent data not given.

Reply with JSON only:
{
  "verdict": "solvable" | "blocked" | "uncertain",
  "confidence": 0.0-1.0,
  "subparts": [
    {
      "label": "a",
      "verdict": "solvable" | "blocked" | "uncertain",
      "issue_kinds": ["missing_table", ...],
      "missing": ["what data is missing, in Chinese"],
      "repair_constraints": ["actionable fix for question author, English or 中文"],
      "answer_sketch": "brief student answer or why impossible"
    }
  ],
  "issue_kinds": [],
  "missing": [],
  "repair_constraints": [],
  "answer_sketch": "overall note"
}

Use verdict "blocked" if any subpart cannot be answered fairly.
issue_kinds must be from: """ + ", ".join(ISSUE_KINDS)


@dataclass
class SolveSubpartResult:
    label: str
    verdict: Verdict
    issue_kinds: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    repair_constraints: list[str] = field(default_factory=list)
    answer_sketch: str = ""


@dataclass
class SolveItemResult:
    item_id: str
    section: str
    verdict: Verdict
    confidence: float = 0.0
    subparts: list[SolveSubpartResult] = field(default_factory=list)
    issue_kinds: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    repair_constraints: list[str] = field(default_factory=list)
    answer_sketch: str = ""
    tables_included: bool = False
    vision_used: bool = False

    @property
    def blocked(self) -> bool:
        return self.verdict == "blocked"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SolveReviewReport:
    version: int = 1
    candidate: str = ""
    generated_at: str = ""
    provider: str = ""
    model: str = ""
    ok: bool = True
    items: list[SolveItemResult] = field(default_factory=list)
    blocked_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "candidate": self.candidate,
            "generated_at": self.generated_at,
            "provider": self.provider,
            "model": self.model,
            "ok": self.ok,
            "blocked_ids": self.blocked_ids,
            "items": [i.to_dict() for i in self.items],
        }


def _parse_subparts(data: dict[str, Any]) -> list[SolveSubpartResult]:
    out: list[SolveSubpartResult] = []
    for sp in data.get("subparts") or []:
        if not isinstance(sp, dict):
            continue
        kinds = [k for k in (sp.get("issue_kinds") or []) if k in ISSUE_KINDS]
        out.append(
            SolveSubpartResult(
                label=str(sp.get("label") or ""),
                verdict=_norm_verdict(sp.get("verdict")),
                issue_kinds=kinds,
                missing=[str(x) for x in (sp.get("missing") or [])],
                repair_constraints=[str(x) for x in (sp.get("repair_constraints") or [])],
                answer_sketch=str(sp.get("answer_sketch") or ""),
            )
        )
    return out


def _norm_verdict(v: Any) -> Verdict:
    s = str(v or "").strip().lower()
    if s in ("solvable", "ok", "pass"):
        return "solvable"
    if s in ("blocked", "fail", "failed"):
        return "blocked"
    return "uncertain"


def _parse_item_result(item_id: str, section: str, data: dict[str, Any], *, tables: bool, vision: bool) -> SolveItemResult:
    kinds = [k for k in (data.get("issue_kinds") or []) if k in ISSUE_KINDS]
    subparts = _parse_subparts(data)
    if subparts and any(sp.verdict == "blocked" for sp in subparts):
        verdict: Verdict = "blocked"
    else:
        verdict = _norm_verdict(data.get("verdict"))
    return SolveItemResult(
        item_id=item_id,
        section=section,
        verdict=verdict,
        confidence=float(data.get("confidence") or 0),
        subparts=subparts,
        issue_kinds=kinds,
        missing=[str(x) for x in (data.get("missing") or [])],
        repair_constraints=[str(x) for x in (data.get("repair_constraints") or [])],
        answer_sketch=str(data.get("answer_sketch") or ""),
        tables_included=tables,
        vision_used=vision,
    )


def _build_user_prompt(
    *,
    item_id: str,
    section: str,
    text: str,
    tables_md: str,
    docx_note: str = "",
) -> str:
    parts = [
        f"Item ID: {item_id}",
        f"Section: {section}",
        "",
        "=== Question text ===",
        text.strip(),
    ]
    if tables_md:
        parts.extend(["", "=== Tables (as on exam paper) ===", tables_md])
    if docx_note:
        parts.extend(["", "=== Rendered DOCX note ===", docx_note])
    parts.append("")
    parts.append("Try to answer every subpart (a)(b)(c). Mark blocked if data is missing or contradictory.")
    return "\n".join(parts)


def review_one_item(
    *,
    cfg: LlmConfig,
    item_id: str,
    section: str,
    text: str,
    tables_md: str = "",
    docx_note: str = "",
    image_b64: str | None = None,
) -> SolveItemResult:
    user = _build_user_prompt(
        item_id=item_id,
        section=section,
        text=text,
        tables_md=tables_md,
        docx_note=docx_note,
    )
    if image_b64:
        data = llm_json_with_image(
            cfg=cfg,
            system=_SOLVE_SYSTEM,
            user_text=user,
            image_b64=image_b64,
        )
        vision = True
    else:
        data = llm_json_completion(cfg=cfg, system=_SOLVE_SYSTEM, user=user)
        vision = False
    return _parse_item_result(
        item_id,
        section,
        data,
        tables=bool(tables_md),
        vision=vision,
    )


def collect_blocked_slot_ids(report: SolveReviewReport) -> list[str]:
    return list(report.blocked_ids)


def run_solve_review(
    spec: dict[str, Any],
    *,
    cfg: LlmConfig,
    sync_tables: bool = True,
    item_ids: list[str] | None = None,
    docx_path: Path | None = None,
    vision_slots: dict[str, str] | None = None,
    on_progress: Any | None = None,
) -> SolveReviewReport:
    """Review each spec item with LLM (+ optional vision images per slot)."""
    if sync_tables:
        sync_item_tables_in_spec(spec)

    docx_notes: dict[str, str] = {}
    if docx_path and docx_path.is_file():
        from solve_docx import docx_table_notes_for_spec

        docx_notes = docx_table_notes_for_spec(docx_path, spec)

    candidate = str(spec.get("meta", {}).get("title") or "exam-spec")
    items_out: list[SolveItemResult] = []
    blocked: list[str] = []

    for item in spec_items(spec):
        if item_ids and item.id not in item_ids:
            continue
        sec = item.section
        if sec not in ("mcq", "section_a", "section_b", "section_c"):
            continue

        tables_md = ""
        if sec in ("section_b", "section_c"):
            tables_md = tables_markdown_for_slot(item.id, item.text)
            if not tables_md and item.meta.get("tables"):
                from solve_tables import grid_to_markdown

                chunks = []
                for t in item.meta.get("tables") or []:
                    chunks.append(grid_to_markdown(str(t.get("name", "表")), t.get("grid") or []))
                tables_md = "\n\n".join(chunks)

        img_b64 = (vision_slots or {}).get(item.id)
        result = review_one_item(
            cfg=cfg,
            item_id=item.id,
            section=sec,
            text=item.text,
            tables_md=tables_md,
            docx_note=docx_notes.get(item.id, ""),
            image_b64=img_b64,
        )
        items_out.append(result)
        if result.blocked:
            blocked.append(item.id)
        if on_progress:
            on_progress(item.id, result)

    ok = not blocked
    return SolveReviewReport(
        candidate=candidate,
        generated_at=datetime.now(timezone.utc).isoformat(),
        provider=cfg.provider,
        model=str(cfg.model or ""),
        ok=ok,
        items=items_out,
        blocked_ids=blocked,
    )


def load_solve_review(path: Path) -> SolveReviewReport:
    data = json.loads(path.expanduser().resolve().read_text(encoding="utf-8"))
    items = []
    for row in data.get("items") or []:
        items.append(
            SolveItemResult(
                item_id=row["item_id"],
                section=row.get("section", ""),
                verdict=_norm_verdict(row.get("verdict")),
                confidence=float(row.get("confidence") or 0),
                subparts=[
                    SolveSubpartResult(
                        label=sp.get("label", ""),
                        verdict=_norm_verdict(sp.get("verdict")),
                        issue_kinds=list(sp.get("issue_kinds") or []),
                        missing=list(sp.get("missing") or []),
                        repair_constraints=list(sp.get("repair_constraints") or []),
                        answer_sketch=str(sp.get("answer_sketch") or ""),
                    )
                    for sp in row.get("subparts") or []
                ],
                issue_kinds=list(row.get("issue_kinds") or []),
                missing=list(row.get("missing") or []),
                repair_constraints=list(row.get("repair_constraints") or []),
                answer_sketch=str(row.get("answer_sketch") or ""),
                tables_included=bool(row.get("tables_included")),
                vision_used=bool(row.get("vision_used")),
            )
        )
    return SolveReviewReport(
        candidate=data.get("candidate", ""),
        generated_at=data.get("generated_at", ""),
        provider=data.get("provider", ""),
        model=data.get("model", ""),
        ok=bool(data.get("ok", True)),
        items=items,
        blocked_ids=list(data.get("blocked_ids") or []),
    )


def save_solve_review(report: SolveReviewReport, path: Path) -> None:
    path = path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")


def feedback_by_slot(report: SolveReviewReport) -> dict[str, dict[str, Any]]:
    """Map slot_id → merged repair_constraints / issue_kinds for regen."""
    out: dict[str, dict[str, Any]] = {}
    for item in report.items:
        if item.verdict not in ("blocked", "uncertain"):
            continue
        kinds: set[str] = set(item.issue_kinds)
        constraints: list[str] = list(item.repair_constraints)
        missing: list[str] = list(item.missing)
        for sp in item.subparts:
            kinds.update(sp.issue_kinds)
            constraints.extend(sp.repair_constraints)
            missing.extend(sp.missing)
        out[item.item_id] = {
            "verdict": item.verdict,
            "issue_kinds": sorted(kinds),
            "repair_constraints": _dedupe(constraints),
            "missing": _dedupe(missing),
            "answer_sketch": item.answer_sketch,
        }
    return out


def _dedupe(lines: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for x in lines:
        x = x.strip()
        if x and x not in seen:
            seen.add(x)
            out.append(x)
    return out


def format_solve_review_report(report: SolveReviewReport) -> str:
    lines = [
        f"Solve review: {'OK' if report.ok else 'BLOCKED'}",
        f"  Provider: {report.provider}  Model: {report.model}",
        f"  Items: {len(report.items)}  Blocked: {len(report.blocked_ids)}",
    ]
    if report.blocked_ids:
        lines.append(f"  Blocked IDs: {', '.join(report.blocked_ids)}")
    for item in report.items:
        if item.verdict == "solvable":
            continue
        lines.append(f"\n  {item.item_id} [{item.verdict}] conf={item.confidence:.2f}")
        for c in item.repair_constraints[:5]:
            lines.append(f"    fix: {c}")
        for m in item.missing[:3]:
            lines.append(f"    missing: {m}")
    return "\n".join(lines)
