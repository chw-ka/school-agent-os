#!/usr/bin/env python3
"""Regenerate 25/26 S5 ICT Exam02 spec + DOCX and write bank-risk report."""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[6]
_GEN = Path(__file__).resolve().parent
_EXAM = _ROOT / "Subjects/S5-ICT/past-papers/2025-2026/Term 02/WrittenExam"
_TEMPLATE = _ROOT / "Subjects/S5-ICT/past-papers/2024-2025/Term 02/WrittenExam/24_25_S5_ICT_Exam02.docx"

for _d in (
    _ROOT / "shared-tools/paper-generator",
    _ROOT / "shared-tools/paper-formatter",
    _ROOT / "shared-tools/question-quality-check",
):
    sys.path.insert(0, str(_d))

from exam_spec import save_spec
from f5_ict_blueprint_db_web import generate
from f5_ict_from_dse import (
    _BANK_SIM_THRESH,
    audit_mcq_bank_similarity,
    build_mcq_payload_from_bank,
)
from f5_ict_written_from_dse import (
    audit_written_bank_similarity,
    pick_written_items_from_bank,
    set_active_written_picks,
    written_preview_json,
)
from f5_ict_spec import build_f5_ict_exam_spec
from post_check import run_spec_check

SPEC_OUT = _GEN / "25_26_S5_ICT_Exam02.spec.json"
DOCX_OUT = _EXAM / "25_26_S5_ICT_Exam02.docx"
DUP_OUT = _GEN / "25_26_S5_ICT_Exam02.spec.duplicates.json"
RISK_OUT = _GEN / "25_26_S5_ICT_Exam02.bank_risk.json"
PREVIEW_OUT = _GEN / "mcq_preview.json"
WRITTEN_PREVIEW_OUT = _GEN / "written_preview.json"
SEED = 2025_2026


def main() -> int:
    rng = random.Random(SEED)
    mcq_rows, correct_indices, prov = build_mcq_payload_from_bank(rng, max_attempts=60)
    written_picks = pick_written_items_from_bank(rng)
    set_active_written_picks(written_picks)
    written_audit = audit_written_bank_similarity(written_picks)
    written_src_hits = written_audit["source"]
    written_best_hits = written_audit["bank_best"]
    WRITTEN_PREVIEW_OUT.write_text(
        written_preview_json(
            written_picks,
            source_hits=written_src_hits,
            bank_best_hits=written_best_hits,
        ),
        encoding="utf-8",
    )

    items = [{"id": pid} for pid in prov]
    bank_hits = audit_mcq_bank_similarity(items, mcq_rows)

    hit_by_slot = {sl: round(sim, 4) for sl, sim, _ in bank_hits}
    PREVIEW_OUT.write_text(
        json.dumps(
            {
                "seed": SEED,
                "count": len(prov),
                "items": [
                    {
                        "provenance": p,
                        "bank_similarity": hit_by_slot.get(i + 1, 0.0),
                        "preview": (mcq_rows[i][0][:100] if mcq_rows[i] else ""),
                    }
                    for i, p in enumerate(prov)
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    def _hit_rows(rows: list[tuple], *, slot_fmt: str | None = None) -> list[dict]:
        out: list[dict] = []
        for row in rows:
            if slot_fmt:
                s, sim, iid = row
                out.append({"slot": slot_fmt.format(s), "similarity": round(sim, 4), "bank_id": iid})
            else:
                sid, sim, iid = row
                out.append({"slot": sid, "similarity": round(sim, 4), "bank_id": iid})
        return out

    RISK_OUT.write_text(
        json.dumps(
            {
                "threshold": _BANK_SIM_THRESH,
                "mcq_total": 30,
                "mcq_over_threshold": len(bank_hits),
                "mcq_ok_count": 30 - len(bank_hits),
                "mcq_hits": _hit_rows(bank_hits, slot_fmt="mcq-{:02d}"),
                "written_total": len(written_picks),
                "written_source_over_threshold": len(written_src_hits),
                "written_source_hits": _hit_rows(written_src_hits),
                "written_bank_best_over_threshold": len(written_best_hits),
                "written_bank_best_hits": _hit_rows(written_best_hits),
                "over_threshold": len(bank_hits),
                "ok_count": 30 - len(bank_hits),
                "hits": _hit_rows(bank_hits, slot_fmt="mcq-{:02d}"),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    footer = {
        "academic_year": "2025-2026",
        "level": "中五級",
        "term_exam": "下學期考試",
        "subject": "資訊及通訊科技",
    }
    final_rows, mcq_key = generate(
        _TEMPLATE,
        DOCX_OUT,
        footer_meta=footer,
        rng=rng,
        mcq_payload=mcq_rows,
        mcq_correct_indices=correct_indices,
    )

    spec = build_f5_ict_exam_spec(
        mcq_rows=final_rows,
        mcq_answers=mcq_key,
        mcq_provenance=prov,
        written_picks=written_picks,
    )
    save_spec(SPEC_OUT, spec)

    check = run_spec_check(
        candidate_spec=SPEC_OUT,
        template=_TEMPLATE,
        candidate_docx=None,
        subject_subpath="S5-ICT",
        json_report=DUP_OUT,
    )

    print(f"Spec: {SPEC_OUT}")
    print(f"DOCX: {DOCX_OUT}")
    print(f"MCQ key: {mcq_key}")
    print(f"MCQ bank >{_BANK_SIM_THRESH:.0%}: {len(bank_hits)}/30")
    print(
        f"Written bank >{_BANK_SIM_THRESH:.0%}: "
        f"source {len(written_src_hits)}/{len(written_picks)}, "
        f"best-match {len(written_best_hits)}/{len(written_picks)} — {RISK_OUT.name}"
    )
    print(f"Written preview: {WRITTEN_PREVIEW_OUT.name}")
    for sid in ("b-01", "b-06", "c-01", "c-08"):
        p = written_picks.get(sid, {})
        print(f"  {sid}: {p.get('dse_year')} {p.get('dse_source', '')[:48]}")
    for s, sim, iid in bank_hits[:8]:
        print(f"  mcq-{s:02d} {sim:.0%} ({iid})")
    for sid, sim, iid in written_src_hits[:8]:
        print(f"  {sid} source {sim:.0%} ({iid})")
    for sid, sim, iid in written_best_hits[:6]:
        if sid not in {x[0] for x in written_src_hits}:
            print(f"  {sid} bank-best {sim:.0%} ({iid})")
    print(f"Duplicate check exit: {check}")
    return check


if __name__ == "__main__":
    raise SystemExit(main())
