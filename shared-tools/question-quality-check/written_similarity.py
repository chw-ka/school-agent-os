"""乙／丙 written similarity vs DSE bank: 整條 60%, subquestion 85%."""
from __future__ import annotations

from dataclasses import dataclass, field

from quality_lib import (
    THRESH_WRITTEN_STEM,
    THRESH_WRITTEN_SUBPART,
    normalize_text,
    split_written_stem_and_subparts,
    text_similarity,
)


def _bank_item_text(it: dict) -> str:
    return (it.get("stem") or it.get("text") or "").strip()


@dataclass
class WrittenSubpartMatch:
    preview: str
    similarity: float
    bank_id: str


@dataclass
class WrittenSimilarityAudit:
    """Similarity of one 乙／丙 slot or block vs question-bank."""

    label: str
    stem_sim: float = 0.0
    stem_bank_id: str = ""
    fail_stem: bool = False
    subpart_max_sim: float = 0.0
    subpart_bank_id: str = ""
    fail_subpart: bool = False
    subparts: list[WrittenSubpartMatch] = field(default_factory=list)
    stem_threshold: float = THRESH_WRITTEN_STEM
    subpart_threshold: float = THRESH_WRITTEN_SUBPART

    @property
    def fail(self) -> bool:
        return self.fail_stem or self.fail_subpart


def audit_written_text_vs_bank(
    text: str,
    bank_items: list[dict],
    *,
    label: str = "",
    stem_threshold: float = THRESH_WRITTEN_STEM,
    subpart_threshold: float = THRESH_WRITTEN_SUBPART,
    sample: int = 400,
) -> WrittenSimilarityAudit:
    """Compare slot text: whole stem ≤ stem_threshold; each subpart ≤ subpart_threshold."""
    import random

    pool = bank_items
    if len(pool) > sample:
        pool = random.sample(pool, sample)

    stem, subparts = split_written_stem_and_subparts(text)
    out = WrittenSimilarityAudit(
        label=label,
        stem_threshold=stem_threshold,
        subpart_threshold=subpart_threshold,
    )

    stem_norm = normalize_text(stem) if stem else normalize_text(text)
    compare_whole = stem_norm if len(stem_norm) >= 20 else normalize_text(text)

    for it in pool:
        raw = _bank_item_text(it)
        if len(raw) < 12:
            continue
        sim = text_similarity(compare_whole, raw)
        if sim > out.stem_sim:
            out.stem_sim = sim
            out.stem_bank_id = str(it.get("id", ""))
    out.fail_stem = out.stem_sim > stem_threshold

    for sp in subparts:
        best, bid = 0.0, ""
        for it in pool:
            raw = _bank_item_text(it)
            if len(raw) < 12:
                continue
            sim = text_similarity(sp, raw)
            if sim > best:
                best, bid = sim, str(it.get("id", ""))
        out.subparts.append(
            WrittenSubpartMatch(preview=sp[:120].replace("\n", " "), similarity=best, bank_id=bid)
        )
        if best > out.subpart_max_sim:
            out.subpart_max_sim = best
            out.subpart_bank_id = bid
        if best > subpart_threshold:
            out.fail_subpart = True

    return out


def audit_written_slots_vs_bank(
    slots: list[tuple[str, str]],
    bank_items: list[dict],
    *,
    stem_threshold: float = THRESH_WRITTEN_STEM,
    subpart_threshold: float = THRESH_WRITTEN_SUBPART,
) -> list[WrittenSimilarityAudit]:
    """slots: list of (slot_id, full_text)."""
    return [
        audit_written_text_vs_bank(
            text,
            bank_items,
            label=slot_id,
            stem_threshold=stem_threshold,
            subpart_threshold=subpart_threshold,
        )
        for slot_id, text in slots
    ]
