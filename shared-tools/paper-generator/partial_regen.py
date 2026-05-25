"""Partial regen: retry failed slots only (max N attempts per slot, no whole-paper re-seed)."""
from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional

_REPO = Path(__file__).resolve().parents[2]
_PG = Path(__file__).resolve().parent
_QCHECK = _PG.parent / "question-quality-check"
for _p in (_PG, _QCHECK):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from check_spec import (  # noqa: E402
    QuestionQualityReport,
    compare_intra_spec,
    compare_spec_to_spec,
    run_question_check,
)
from coherence_check import check_text_coherence  # noqa: E402
from exam_spec import load_spec  # noqa: E402
from f5_ict_generate_from_blueprint import (  # noqa: E402
    _find_slot,
    generate_item_for_slot,
    replace_spec_item,
)


@dataclass
class SlotRegenResult:
    slot_id: str
    resolved: bool
    attempts: int = 0
    note: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PartialRegenResult:
    ok: bool
    seed: int
    max_attempts: int
    slots: list[SlotRegenResult] = field(default_factory=list)
    unresolved: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "seed": self.seed,
            "max_attempts": self.max_attempts,
            "unresolved": self.unresolved,
            "slots": [s.to_dict() for s in self.slots],
        }


def collect_failed_slot_ids(report: QuestionQualityReport) -> list[str]:
    """Union of slots flagged by duplicate / coherence / cross-section concept checks."""
    seen: set[str] = set()
    out: list[str] = []

    def add(sid: str) -> None:
        if sid and sid not in seen:
            seen.add(sid)
            out.append(sid)

    for sid in report.regenerate_ids:
        add(sid)

    if report.coherence is not None:
        for issue in report.coherence.issues:
            add(issue.item_id)

    if report.solvability is not None:
        for issue in report.solvability.issues:
            add(issue.item_id)

    if report.concept_conflicts is not None:
        for c in report.concept_conflicts.conflicts:
            if c.item_a_section in ("mcq", "section_a"):
                add(c.item_a_id)
            if c.item_b_section in ("mcq", "section_a"):
                add(c.item_b_id)

    return out


def _item_by_id(spec: dict, slot_id: str) -> dict | None:
    for it in spec.get("items") or []:
        if it.get("id") == slot_id:
            return it
    return None


def _slot_intra_dup(spec: dict, slot_id: str) -> bool:
    for dup in compare_intra_spec(spec):
        if dup.candidate_id == slot_id or dup.reference_id == slot_id:
            return True
    return False


def _slot_ref_dup(
    spec: dict,
    slot_id: str,
    refs: list[tuple[str, dict]],
    *,
    threshold: float,
) -> bool:
    item = _item_by_id(spec, slot_id)
    if not item:
        return False
    mini = {"version": 1, "meta": {}, "items": [item]}
    for label, ref in refs:
        for dup in compare_spec_to_spec(mini, ref, reference_path=label, threshold=threshold):
            if dup.similarity > threshold:
                return True
    return False


_COMBO_SLOT_IDS = frozenset(
    f"mcq-{i:02d}" for i in (2, 5, 9, 14, 19, 24, 29)
)


def slot_passes_local_check(
    spec: dict,
    slot_id: str,
    *,
    refs: Optional[list[tuple[str, dict]]] = None,
    threshold: float = 0.75,
    skip_ref_check_for_combo: bool = True,
) -> bool:
    item = _item_by_id(spec, slot_id)
    if not item:
        return False
    section = item.get("section", "mcq")
    sec = "mcq" if section in ("mcq", "section_a") else section
    if check_text_coherence(slot_id, item.get("text", ""), section=sec):
        return False
    if _slot_intra_dup(spec, slot_id):
        return False
    use_refs = refs
    if skip_ref_check_for_combo and slot_id in _COMBO_SLOT_IDS:
        use_refs = None
    if use_refs and _slot_ref_dup(spec, slot_id, use_refs, threshold=threshold):
        return False
    return True


def run_partial_regen(
    spec: dict[str, Any],
    blueprint: dict[str, Any],
    style: dict[str, Any],
    failed_ids: list[str],
    *,
    seed: int,
    max_attempts: int = 10,
    refs: Optional[list[tuple[str, dict]]] = None,
    solve_feedback: Optional[dict[str, dict[str, Any]]] = None,
    use_llm_repair: bool = False,
    llm_cfg: Any = None,
    llm_repair_attempts: int = 3,
) -> PartialRegenResult:
    results: list[SlotRegenResult] = []
    unresolved: list[str] = []

    for slot_id in failed_ids:
        slot = _find_slot(blueprint, slot_id)
        if not slot:
            results.append(SlotRegenResult(slot_id, False, 0, note="slot not in blueprint"))
            unresolved.append(slot_id)
            continue

        resolved = False
        note = ""
        fb = (solve_feedback or {}).get(slot_id)
        if use_llm_repair and fb and llm_cfg is not None:
            from solve_repair import repair_item_with_llm

            item_row = _item_by_id(spec, slot_id)
            if item_row:
                for attempt in range(1, llm_repair_attempts + 1):
                    try:
                        new_item = repair_item_with_llm(
                            cfg=llm_cfg,
                            slot=slot,
                            item=item_row,
                            feedback=fb,
                        )
                        replace_spec_item(spec, new_item, seed=seed)
                        if slot_passes_local_check(spec, slot_id, refs=refs):
                            resolved = True
                            note = f"llm repair ok on attempt {attempt}"
                            results.append(SlotRegenResult(slot_id, True, attempt, note=note))
                            break
                    except Exception as exc:
                        note = f"llm repair attempt {attempt}: {exc}"
                if resolved:
                    continue

        for attempt in range(1, max_attempts + 1):
            variant = attempt
            item = generate_item_for_slot(slot, style, seed=seed + attempt * 17, variant=variant)
            replace_spec_item(spec, item, seed=seed)
            if slot_passes_local_check(spec, slot_id, refs=refs):
                resolved = True
                note = note or f"pattern regen ok on attempt {attempt}"
                results.append(SlotRegenResult(slot_id, True, attempt, note=note))
                break
        else:
            note = note or f"still failing after {max_attempts} attempts"
            results.append(SlotRegenResult(slot_id, False, max_attempts, note=note))
            unresolved.append(slot_id)

    return PartialRegenResult(
        ok=not unresolved,
        seed=seed,
        max_attempts=max_attempts,
        slots=results,
        unresolved=unresolved,
    )


def build_reference_specs(
    *,
    template_docx: Path | None,
    past_papers_root: Path,
    subject_subpath: str,
    years: int = 3,
) -> list[tuple[str, dict]]:
    from check_spec import discover_past_papers
    from spec_from_docx import docx_to_spec

    refs: list[tuple[str, dict]] = []
    if template_docx and template_docx.exists():
        refs.append((str(template_docx), docx_to_spec(template_docx)))
    for p in discover_past_papers(
        past_papers_root,
        years=years,
        subject_subpath=subject_subpath,
        include_candidate=None,
    ):
        refs.append((str(p), docx_to_spec(p)))
    return refs


def partial_regen_with_review(
    spec_path: Path,
    blueprint_path: Path,
    style: dict[str, Any],
    *,
    seed: int = 20252026,
    max_attempts: int = 10,
    template_docx: Path | None = None,
    past_papers_root: Path | None = None,
    subject_subpath: str = "S5-ICT",
) -> tuple[dict, PartialRegenResult, QuestionQualityReport]:
    from f5_ict_exam_blueprint import load_blueprint

    spec_path = spec_path.expanduser().resolve()
    spec = load_spec(spec_path)
    blueprint = load_blueprint(blueprint_path)
    root = past_papers_root or (_REPO / "Subjects")
    refs = build_reference_specs(
        template_docx=template_docx,
        past_papers_root=root,
        subject_subpath=subject_subpath,
    )

    report = run_question_check(
        spec_path,
        template_docx_path=template_docx,
        past_papers_root=root,
        subject_subpath=subject_subpath,
    )
    failed = collect_failed_slot_ids(report)
    if not failed:
        return spec, PartialRegenResult(ok=True, seed=seed, max_attempts=max_attempts), report

    pr = run_partial_regen(
        spec,
        blueprint,
        style,
        failed,
        seed=seed,
        max_attempts=max_attempts,
        refs=refs,
    )
    final = run_question_check(
        spec_path,
        template_docx_path=template_docx,
        past_papers_root=root,
        subject_subpath=subject_subpath,
    )
    return spec, pr, final


def save_partial_regen_report(result: PartialRegenResult, path: Path) -> None:
    path = path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
