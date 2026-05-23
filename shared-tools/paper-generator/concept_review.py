#!/usr/bin/env python3
"""Concept review for exam_blueprint.json vs concept_map.json (Phase 3)."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

_REPO = Path(__file__).resolve().parents[2]
_QCHECK = Path(__file__).resolve().parents[1] / "question-quality-check"
_PDF = Path(__file__).resolve().parents[1] / "pdf-engine"
for _p in (_QCHECK, _PDF):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from concept_check import (  # noqa: E402
    compare_concept_distributions,
    format_distribution_report,
)
from mcq_core_plan import MCQ_CORE_SEQUENCE, verify_core_sequence  # noqa: E402
from dse_ict_syllabus import classify_syllabus, load_concepts_cfg  # noqa: E402
from mcq_core_plan import CONCEPT_TO_CORE, ELECTIVE_EC_CONCEPTS  # noqa: E402

IssueSeverity = Literal["error", "warn", "info"]


@dataclass
class ConceptReviewIssue:
    severity: IssueSeverity
    kind: str
    message: str
    slot_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity,
            "kind": self.kind,
            "message": self.message,
            "slot_id": self.slot_id,
        }


@dataclass
class ConceptReviewReport:
    blueprint: str
    concept_map: str
    ok: bool
    issues: list[ConceptReviewIssue] = field(default_factory=list)
    distribution_text: str = ""
    summary: dict[str, Any] = field(default_factory=dict)

    @property
    def exit_code(self) -> int:
        if any(i.severity == "error" for i in self.issues):
            return 1
        if any(i.severity == "warn" for i in self.issues):
            return 0  # warnings pass; use --strict for fail on warn
        return 0

    def exit_code_strict(self) -> int:
        if any(i.severity in ("error", "warn") for i in self.issues):
            return 1 if any(i.severity == "error" for i in self.issues) else 2
        return 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": 1,
            "blueprint": self.blueprint,
            "concept_map": self.concept_map,
            "ok": self.ok,
            "issues": [i.to_dict() for i in self.issues],
            "summary": self.summary,
        }


def load_blueprint(path: Path) -> dict[str, Any]:
    return json.loads(path.expanduser().resolve().read_text(encoding="utf-8"))


def load_concept_map(path: Path) -> dict[str, Any]:
    return json.loads(path.expanduser().resolve().read_text(encoding="utf-8"))


def blueprint_to_spec(blueprint: dict[str, Any]) -> dict[str, Any]:
    """Pseudo exam spec for reusing concept_check distribution helpers."""
    items: list[dict[str, Any]] = []
    for slot in blueprint.get("slots") or []:
        title = slot.get("title") or slot["id"]
        concepts = list(slot.get("concepts") or [])
        row: dict[str, Any] = {
            "id": slot["id"],
            "section": slot["section"],
            "text": f"{title} [{' / '.join(concepts)}]",
            "marks": slot.get("marks", 1),
            "concepts": concepts,
        }
        if slot.get("core"):
            row["core"] = slot["core"]
        items.append(row)
    meta = dict(blueprint.get("meta") or {})
    meta.setdefault("mcq_core_sequence", [])
    return {"version": 1, "meta": meta, "items": items}


def _add(issues: list[ConceptReviewIssue], severity: IssueSeverity, kind: str, message: str, slot_id: str | None = None) -> None:
    issues.append(ConceptReviewIssue(severity, kind, message, slot_id))


def _check_structure(blueprint: dict[str, Any], issues: list[ConceptReviewIssue]) -> None:
    meta = blueprint.get("meta") or {}
    slots = blueprint.get("slots") or []
    sections = meta.get("sections") or {}
    mcq_n = sum(1 for s in slots if s.get("section") == "mcq")
    b_n = sum(1 for s in slots if s.get("section") == "section_b")
    c_n = sum(1 for s in slots if s.get("section") == "section_c")
    exp_mcq = (sections.get("mcq") or {}).get("count", 30)
    exp_b = (sections.get("section_b") or {}).get("count", 6)
    exp_c = (sections.get("section_c") or {}).get("count", 7)
    if mcq_n != exp_mcq:
        _add(issues, "error", "structure", f"Expected {exp_mcq} MCQ slots, got {mcq_n}")
    if b_n != exp_b:
        _add(issues, "error", "structure", f"Expected {exp_b} section_b slots, got {b_n}")
    if c_n != exp_c:
        _add(issues, "error", "structure", f"Expected {exp_c} section_c slots, got {c_n}")
    total_marks = sum(float(s.get("marks") or 0) for s in slots)
    exp_total = float(meta.get("total_marks") or 100)
    if abs(total_marks - exp_total) > 0.01:
        _add(
            issues,
            "error",
            "marks_total",
            f"Slot marks sum to {total_marks}, expected {exp_total}",
        )
    ids = [s.get("id") for s in slots]
    if len(ids) != len(set(ids)):
        _add(issues, "error", "duplicate_id", "Duplicate slot ids in blueprint")


def _check_mcq_sequence(blueprint: dict[str, Any], issues: list[ConceptReviewIssue]) -> None:
    slots = [s for s in blueprint.get("slots") or [] if s.get("section") == "mcq"]
    seq = [str(s.get("core") or "") for s in sorted(slots, key=lambda x: x.get("id", ""))]
    for msg in verify_core_sequence(tuple(seq)):
        _add(issues, "error", "mcq_core_sequence", msg)
    if len(seq) != len(MCQ_CORE_SEQUENCE):
        _add(
            issues,
            "error",
            "mcq_core_sequence",
            f"Expected {len(MCQ_CORE_SEQUENCE)} MCQ slots, got {len(seq)}",
        )
    for slot in slots:
        if not slot.get("core"):
            _add(
                issues,
                "error",
                "mcq_core_sequence",
                f"{slot.get('id')}: missing core on blueprint slot",
                slot_id=str(slot.get("id")),
            )


def _check_concept_targets(spec: dict[str, Any], issues: list[ConceptReviewIssue]) -> str:
    dist = compare_concept_distributions(spec, reference_spec=None)
    for delta in dist.target_violations:
        _add(
            issues,
            "error",
            "concept_target",
            f"{delta.concept}: count={delta.candidate} (min={delta.target_min}, max={delta.target_max})",
        )
    return format_distribution_report(dist)


def _check_out_of_syllabus(
    blueprint: dict[str, Any],
    issues: list[ConceptReviewIssue],
    *,
    concepts_cfg: dict | None = None,
) -> None:
    cfg = concepts_cfg or load_concepts_cfg()
    for slot in blueprint.get("slots") or []:
        concepts = slot.get("concepts") or []
        text = " ".join(concepts) + " " + str(slot.get("title") or "")
        syll = classify_syllabus(text, concepts=concepts, concepts_cfg=cfg)
        if syll["syllabus_status"] == "out_of_syllabus":
            reasons = "; ".join(syll.get("out_of_syllabus_reasons") or [])
            _add(
                issues,
                "error",
                "out_of_syllabus",
                f"Slot concepts/title hit removed syllabus: {reasons}",
                slot_id=str(slot.get("id")),
            )


def _check_f5_scope(
    blueprint: dict[str, Any],
    concept_map: dict[str, Any],
    issues: list[ConceptReviewIssue],
) -> None:
    scope = concept_map.get("f5_exam_scope") or {}
    mcq_units = set(scope.get("mcq_units") or ["A", "B", "D"])
    concept_index = concept_map.get("concept_index") or {}

    for slot in blueprint.get("slots") or []:
        sid = str(slot.get("id", ""))
        section = slot.get("section")
        concepts = slot.get("concepts") or []
        if section == "mcq":
            ec_only = [c for c in concepts if c in ELECTIVE_EC_CONCEPTS]
            compulsory = [c for c in concepts if CONCEPT_TO_CORE.get(c) in ("A", "B", "D")]
            if ec_only and not compulsory:
                _add(
                    issues,
                    "error",
                    "f5_mcq_ec",
                    f"MCQ slot has elective-only concepts {ec_only} (Module C not in 甲部)",
                    slot_id=sid,
                )
            for c in concepts:
                entry = concept_index.get(c) or {}
                unit = entry.get("unit") or CONCEPT_TO_CORE.get(c, "")
                if unit == "C" and c not in ("SQL",):
                    _add(
                        issues,
                        "warn",
                        "f5_mcq_network",
                        f"Concept «{c}» is Core C (networking); S5 Term2 MCQ usually excludes",
                        slot_id=sid,
                    )
            core = slot.get("core")
            if core and core not in mcq_units:
                _add(
                    issues,
                    "error",
                    "f5_mcq_core",
                    f"MCQ core {core} not in f5_exam_scope.mcq_units {sorted(mcq_units)}",
                    slot_id=sid,
                )
        if section == "section_c":
            if not any(
                CONCEPT_TO_CORE.get(c) in ("EA", "EC") or c in ("ERD", "數據庫", "SQL", "堆疊")
                for c in concepts
            ):
                _add(
                    issues,
                    "warn",
                    "f5_section_c",
                    f"丙部 slot may lack DB/algo elective concepts: {concepts}",
                    slot_id=sid,
                )


def _check_concept_map_index(
    blueprint: dict[str, Any],
    concept_map: dict[str, Any],
    issues: list[ConceptReviewIssue],
) -> None:
    index = concept_map.get("concept_index") or {}
    for slot in blueprint.get("slots") or []:
        for c in slot.get("concepts") or []:
            if c not in index:
                _add(
                    issues,
                    "warn",
                    "unknown_concept",
                    f"Concept «{c}» not in concept_map.concept_index",
                    slot_id=str(slot.get("id")),
                )


def _check_slot_overlap(blueprint: dict[str, Any], issues: list[ConceptReviewIssue]) -> None:
    """Warn when slots in same section share too many concepts."""
    by_section: dict[str, list[tuple[str, set[str]]]] = {}
    for slot in blueprint.get("slots") or []:
        sec = str(slot.get("section", ""))
        concepts = set(slot.get("concepts") or [])
        by_section.setdefault(sec, []).append((str(slot.get("id")), concepts))

    for sec, rows in by_section.items():
        for i in range(len(rows)):
            for j in range(i + 1, len(rows)):
                id_a, set_a = rows[i]
                id_b, set_b = rows[j]
                shared = set_a & set_b
                if len(shared) >= 3:
                    _add(
                        issues,
                        "warn",
                        "concept_overlap",
                        f"{sec}: {id_a} and {id_b} share {len(shared)} concepts: {sorted(shared)}",
                    )
        # MCQ: same concept in many slots
        if sec == "mcq":
            counts: Counter[str] = Counter()
            for _, cs in rows:
                counts.update(cs)
            for concept, n in counts.items():
                if concept in ("算法", "數據庫", "硬件", "軟件"):
                    continue
                if n >= 6:
                    _add(
                        issues,
                        "warn",
                        "mcq_concept_repeat",
                        f"MCQ concept «{concept}» appears in {n} slots (consider diversifying)",
                    )


def _check_common_mistakes_coverage(
    blueprint: dict[str, Any],
    concept_map: dict[str, Any],
    issues: list[ConceptReviewIssue],
) -> None:
    """Info/warn if high-stakes topics lack common_mistakes in concept_map."""
    index = concept_map.get("concept_index") or {}
    for slot in blueprint.get("slots") or []:
        if float(slot.get("marks") or 0) < 4:
            continue
        for c in slot.get("concepts") or []:
            entry = index.get(c) or {}
            mistakes = entry.get("common_mistakes") or []
            if not mistakes:
                _add(
                    issues,
                    "info",
                    "common_mistakes",
                    f"No common_mistakes recorded in concept_map for «{c}» (marks≥4 slot)",
                    slot_id=str(slot.get("id")),
                )


def run_concept_review(
    blueprint_path: Path,
    *,
    concept_map_path: Path | None = None,
    include_info: bool = True,
) -> ConceptReviewReport:
    blueprint_path = blueprint_path.expanduser().resolve()
    blueprint = load_blueprint(blueprint_path)
    cmap_path = concept_map_path or (
        _REPO / str((blueprint.get("meta") or {}).get("concept_map", ""))
    )
    if not cmap_path.exists():
        cmap_path = _REPO / "Subjects/DSE-ICT/question-bank/concept_map.json"
    concept_map = load_concept_map(cmap_path)

    issues: list[ConceptReviewIssue] = []
    _check_structure(blueprint, issues)
    spec = blueprint_to_spec(blueprint)
    _check_mcq_sequence(blueprint, issues)
    dist_text = _check_concept_targets(spec, issues)
    _check_out_of_syllabus(blueprint, issues)
    _check_f5_scope(blueprint, concept_map, issues)
    _check_concept_map_index(blueprint, concept_map, issues)
    _check_slot_overlap(blueprint, issues)
    if include_info:
        _check_common_mistakes_coverage(blueprint, concept_map, issues)

    if not include_info:
        issues = [i for i in issues if i.severity != "info"]

    errors = sum(1 for i in issues if i.severity == "error")
    warns = sum(1 for i in issues if i.severity == "warn")
    ok = errors == 0

    return ConceptReviewReport(
        blueprint=str(blueprint_path),
        concept_map=str(cmap_path.resolve()),
        ok=ok,
        issues=issues,
        distribution_text=dist_text,
        summary={
            "errors": errors,
            "warnings": warns,
            "info": sum(1 for i in issues if i.severity == "info"),
            "slot_count": len(blueprint.get("slots") or []),
        },
    )


def format_concept_review_report(report: ConceptReviewReport) -> str:
    lines = [
        "--- Concept review (blueprint) ---",
        f"Blueprint: {report.blueprint}",
        f"Concept map: {report.concept_map}",
        f"Status: {'PASS' if report.ok else 'FAIL'} "
        f"(errors={report.summary.get('errors', 0)}, warnings={report.summary.get('warnings', 0)})",
        "",
        report.distribution_text,
        "",
    ]
    if report.issues:
        lines.append("Issues:")
        for issue in report.issues:
            loc = f" [{issue.slot_id}]" if issue.slot_id else ""
            lines.append(f"  [{issue.severity}] {issue.kind}{loc}: {issue.message}")
    else:
        lines.append("No issues.")
    return "\n".join(lines)


def write_concept_review_json(report: ConceptReviewReport, path: Path) -> None:
    path = path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--blueprint", type=Path, required=True, help="exam_blueprint.json")
    ap.add_argument("--concept-map", type=Path, help="concept_map.json (default from blueprint meta)")
    ap.add_argument("--json", type=Path, help="Write *.concept_review.json report")
    ap.add_argument("--strict", action="store_true", help="Exit 1 on warnings too")
    ap.add_argument("--no-info", action="store_true", help="Omit info-level issues")
    args = ap.parse_args(argv)

    report = run_concept_review(
        args.blueprint,
        concept_map_path=args.concept_map,
        include_info=not args.no_info,
    )
    print(format_concept_review_report(report))
    if args.json:
        write_concept_review_json(report, args.json)
        print(f"Report: {args.json}")

    code = report.exit_code_strict() if args.strict else report.exit_code
    return code


if __name__ == "__main__":
    raise SystemExit(main())
