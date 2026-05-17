"""Verify assessed concepts align between candidate and reference exam specs."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional

from exam_spec import ExamItem, load_spec, spec_items


@dataclass(frozen=True)
class ConceptMismatch:
    slot: str
    candidate_id: str
    reference_id: str
    candidate_concepts: list[str]
    reference_concepts: list[str]


@dataclass
class ConceptDistribution:
    """How often each concept appears across items (one count per item mentioning it)."""

    total_items: int = 0
    items_with_concepts: int = 0
    items_without_concepts: int = 0
    concept_counts: dict[str, int] = field(default_factory=dict)
    by_section: dict[str, dict[str, int]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_items": self.total_items,
            "items_with_concepts": self.items_with_concepts,
            "items_without_concepts": self.items_without_concepts,
            "concept_counts": dict(
                sorted(self.concept_counts.items(), key=lambda x: (-x[1], x[0]))
            ),
            "by_section": {
                sec: dict(sorted(cnt.items(), key=lambda x: (-x[1], x[0])))
                for sec, cnt in sorted(self.by_section.items())
            },
        }


@dataclass(frozen=True)
class ConceptDistributionDelta:
    concept: str
    candidate: int
    reference: int
    target_min: Optional[int] = None
    target_max: Optional[int] = None

    @property
    def delta(self) -> int:
        return self.candidate - self.reference

    @property
    def violates_target(self) -> bool:
        if self.target_min is not None and self.candidate < self.target_min:
            return True
        if self.target_max is not None and self.candidate > self.target_max:
            return True
        return False


@dataclass
class ConceptDistributionReport:
    candidate: ConceptDistribution = field(default_factory=ConceptDistribution)
    reference: Optional[ConceptDistribution] = None
    deltas: list[ConceptDistributionDelta] = field(default_factory=list)
    missing_in_candidate: list[str] = field(default_factory=list)
    extra_in_candidate: list[str] = field(default_factory=list)
    target_violations: list[ConceptDistributionDelta] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """Only explicit meta.concept_targets violations fail; missing vs ref is advisory."""
        return not self.target_violations

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "candidate": self.candidate.to_dict(),
            "reference": self.reference.to_dict() if self.reference else None,
            "missing_in_candidate": self.missing_in_candidate,
            "extra_in_candidate": self.extra_in_candidate,
            "deltas": [
                {
                    "concept": d.concept,
                    "candidate": d.candidate,
                    "reference": d.reference,
                    "delta": d.delta,
                    "target_min": d.target_min,
                    "target_max": d.target_max,
                }
                for d in self.deltas
            ],
            "target_violations": [d.concept for d in self.target_violations],
        }


@dataclass
class ConceptCheckResult:
    candidate: str
    reference: str
    ok: bool
    checked_slots: int = 0
    mismatches: list[ConceptMismatch] = field(default_factory=list)
    skipped_slots: int = 0
    distribution: Optional[ConceptDistributionReport] = None

    @property
    def distribution_ok(self) -> bool:
        if self.distribution is None:
            return True
        return self.distribution.ok

    def to_dict(self) -> dict:
        d: dict[str, Any] = {
            "ok": self.ok,
            "checked_slots": self.checked_slots,
            "skipped_slots": self.skipped_slots,
            "mismatch_count": len(self.mismatches),
            "mismatches": [asdict(m) for m in self.mismatches],
        }
        if self.distribution is not None:
            d["distribution"] = self.distribution.to_dict()
        return d


def item_concepts(item: ExamItem) -> list[str]:
    raw = item.meta.get("concepts")
    if raw is None:
        raw = item.meta.get("concept")
    if raw is None and item.meta.get("title"):
        raw = [item.meta["title"]]
    if raw is None:
        return []
    if isinstance(raw, str):
        return [raw.strip()] if raw.strip() else []
    if isinstance(raw, list):
        return [str(c).strip() for c in raw if str(c).strip()]
    return []


def _slot_key(item: ExamItem, position: int) -> str:
    slot = item.meta.get("concept_slot") or item.meta.get("slot")
    if slot:
        return str(slot)
    return f"{item.section}:{position:02d}"


def build_concept_distribution(spec: dict) -> ConceptDistribution:
    items = spec_items(spec)
    dist = ConceptDistribution(total_items=len(items))
    for item in items:
        concepts = item_concepts(item)
        if not concepts:
            dist.items_without_concepts += 1
            continue
        dist.items_with_concepts += 1
        seen_in_item: set[str] = set()
        for c in concepts:
            key = c.strip()
            if not key:
                continue
            norm = key.lower()
            if norm in seen_in_item:
                continue
            seen_in_item.add(norm)
            dist.concept_counts[key] = dist.concept_counts.get(key, 0) + 1
            sec = item.section or "unknown"
            bucket = dist.by_section.setdefault(sec, {})
            bucket[key] = bucket.get(key, 0) + 1
    return dist


def _parse_concept_targets(meta: dict) -> dict[str, tuple[Optional[int], Optional[int]]]:
    raw = meta.get("concept_targets") or meta.get("concept_distribution")
    if not isinstance(raw, dict):
        return {}
    out: dict[str, tuple[Optional[int], Optional[int]]] = {}
    for concept, spec in raw.items():
        if isinstance(spec, int):
            out[str(concept)] = (spec, spec)
        elif isinstance(spec, dict):
            out[str(concept)] = (
                spec.get("min"),
                spec.get("max"),
            )
    return out


def compare_concept_distributions(
    candidate_spec: dict,
    reference_spec: Optional[dict] = None,
) -> ConceptDistributionReport:
    cand_dist = build_concept_distribution(candidate_spec)
    ref_dist = build_concept_distribution(reference_spec) if reference_spec else None
    targets = _parse_concept_targets(candidate_spec.get("meta", {}))
    if not targets and reference_spec:
        targets = _parse_concept_targets(reference_spec.get("meta", {}))

    report = ConceptDistributionReport(candidate=cand_dist, reference=ref_dist)
    ref_counts = ref_dist.concept_counts if ref_dist else {}
    all_concepts = set(cand_dist.concept_counts) | set(ref_counts) | set(targets)

    for concept in sorted(all_concepts, key=lambda c: (-cand_dist.concept_counts.get(c, 0), c)):
        c_count = cand_dist.concept_counts.get(concept, 0)
        r_count = ref_counts.get(concept, 0)
        t_min, t_max = targets.get(concept, (None, None))
        delta = ConceptDistributionDelta(
            concept=concept,
            candidate=c_count,
            reference=r_count,
            target_min=t_min,
            target_max=t_max,
        )
        report.deltas.append(delta)
        if delta.violates_target:
            report.target_violations.append(delta)

    if ref_dist:
        report.missing_in_candidate = [
            c for c in ref_counts if ref_counts[c] > 0 and cand_dist.concept_counts.get(c, 0) == 0
        ]
        report.extra_in_candidate = [
            c
            for c in cand_dist.concept_counts
            if cand_dist.concept_counts[c] > 0 and ref_counts.get(c, 0) == 0
        ]

    return report


def format_distribution_report(report: ConceptDistributionReport) -> str:
    lines = [
        "Concept distribution (candidate):",
        f"  items: {report.candidate.total_items} total, "
        f"{report.candidate.items_with_concepts} with concepts, "
        f"{report.candidate.items_without_concepts} without",
    ]
    if report.candidate.concept_counts:
        lines.append("  counts:")
        for concept, n in sorted(
            report.candidate.concept_counts.items(), key=lambda x: (-x[1], x[0])
        ):
            lines.append(f"    {concept}: {n}")
    else:
        lines.append("  (no concepts metadata on items)")

    if report.reference and report.reference.concept_counts:
        lines.extend(["", "Reference distribution:"])
        for concept, n in sorted(
            report.reference.concept_counts.items(), key=lambda x: (-x[1], x[0])
        ):
            c_n = report.candidate.concept_counts.get(concept, 0)
            mark = ""
            if c_n != n:
                mark = f"  (candidate {c_n}, Δ{c_n - n:+d})"
            lines.append(f"    {concept}: {n}{mark}")

    if report.missing_in_candidate:
        lines.append(f"\nMissing vs reference: {', '.join(report.missing_in_candidate)}")
    if report.extra_in_candidate:
        lines.append(f"Extra vs reference: {', '.join(report.extra_in_candidate)}")
    if report.target_violations:
        lines.append("\nTarget violations:")
        for d in report.target_violations:
            lines.append(
                f"  {d.concept}: count={d.candidate} "
                f"(target min={d.target_min}, max={d.target_max})"
            )

    if report.reference and report.candidate.by_section:
        lines.append("\nBy section (candidate):")
        for sec, counts in sorted(report.candidate.by_section.items()):
            summary = ", ".join(f"{k}×{v}" for k, v in sorted(counts.items(), key=lambda x: -x[1]))
            lines.append(f"  {sec}: {summary}")

    status = "OK" if report.ok else "REVIEW"
    if report.reference and report.missing_in_candidate:
        status = "REVIEW (missing concepts)"
    lines.insert(0, f"Distribution: {status}")
    return "\n".join(lines)


def _pair_items(cand: list[ExamItem], ref: list[ExamItem]) -> list[tuple[str, ExamItem, ExamItem]]:
    pairs: list[tuple[str, ExamItem, ExamItem]] = []
    ref_by_id = {i.id: i for i in ref}
    used_ref: set[str] = set()

    for c in cand:
        if c.id in ref_by_id:
            pairs.append((c.id, c, ref_by_id[c.id]))
            used_ref.add(c.id)

    cand_rest = [c for c in cand if c.id not in ref_by_id]
    ref_rest = [r for r in ref if r.id not in used_ref]

    def by_section(items: list[ExamItem]) -> dict[str, list[ExamItem]]:
        buckets: dict[str, list[ExamItem]] = {}
        for it in items:
            buckets.setdefault(it.section, []).append(it)
        return buckets

    cb = by_section(cand_rest)
    rb = by_section(ref_rest)
    for sec in sorted(set(cb) & set(rb)):
        c_items, r_items = cb[sec], rb[sec]
        for pos, (c_item, r_item) in enumerate(zip(c_items, r_items), start=1):
            pairs.append((_slot_key(c_item, pos), c_item, r_item))

    return pairs


def check_concepts(
    candidate_spec: dict,
    reference_spec: dict,
    *,
    candidate_label: str = "",
    reference_label: str = "",
    include_distribution: bool = True,
) -> ConceptCheckResult:
    cand_items = spec_items(candidate_spec)
    ref_items = spec_items(reference_spec)
    pairs = _pair_items(cand_items, ref_items)

    mismatches: list[ConceptMismatch] = []
    checked = 0
    skipped = 0

    for slot, c_item, r_item in pairs:
        c_concepts = item_concepts(c_item)
        r_concepts = item_concepts(r_item)
        if not c_concepts or not r_concepts:
            skipped += 1
            continue
        checked += 1
        if {x.lower() for x in c_concepts} != {x.lower() for x in r_concepts}:
            mismatches.append(
                ConceptMismatch(
                    slot=slot,
                    candidate_id=c_item.id,
                    reference_id=r_item.id,
                    candidate_concepts=c_concepts,
                    reference_concepts=r_concepts,
                )
            )

    distribution = None
    if include_distribution:
        distribution = compare_concept_distributions(candidate_spec, reference_spec)

    return ConceptCheckResult(
        candidate=candidate_label,
        reference=reference_label,
        ok=len(mismatches) == 0,
        checked_slots=checked,
        mismatches=mismatches,
        skipped_slots=skipped,
        distribution=distribution,
    )


def check_concept_distribution_only(candidate_spec: dict) -> ConceptDistributionReport:
    return compare_concept_distributions(candidate_spec, reference_spec=None)


def check_concepts_from_paths(candidate: Path, reference: Path) -> ConceptCheckResult:
    candidate = candidate.expanduser().resolve()
    reference = reference.expanduser().resolve()
    return check_concepts(
        load_spec(candidate),
        load_spec(reference),
        candidate_label=str(candidate),
        reference_label=str(reference),
    )


def format_concept_report(result: ConceptCheckResult) -> str:
    lines = [
        f"Concept alignment: {'OK' if result.ok else 'MISMATCHES'}",
        f"Checked slots: {result.checked_slots} (skipped {result.skipped_slots} — missing concepts metadata)",
        f"Reference: {result.reference or '(inline spec)'}",
    ]
    if not result.mismatches:
        lines.append("All paired items assess the same concepts.")
    else:
        lines.append(f"Mismatches: {len(result.mismatches)}")
        for m in result.mismatches:
            lines.append(
                f"\n  [{m.slot}] {m.candidate_id} ↔ {m.reference_id}\n"
                f"    candidate: {m.candidate_concepts}\n"
                f"    reference: {m.reference_concepts}"
            )

    if result.distribution is not None:
        lines.extend(["", format_distribution_report(result.distribution)])

    return "\n".join(lines)
