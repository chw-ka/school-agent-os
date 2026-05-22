#!/usr/bin/env python3
"""Compare 25/26 S5 ICT Exam02 vs past papers at 90% similarity."""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(_ROOT / "shared-tools/question-quality-check"))

from check_spec import compare_spec_to_spec
from exam_spec import spec_items
from quality_lib import compare_documents, extract_lines, extract_mcq_stems, extract_written_units
from spec_from_docx import docx_to_spec

THRESH = 0.90
CAND = _ROOT / "Subjects/S5-ICT/past-papers/2025-2026/Term 02/WrittenExam/25_26_S5_ICT_Exam02.docx"
REFS = [
    ("23/24 Term2 PDF", _ROOT / "Subjects/S5-ICT/past-papers/2024-2025/Term 02/WrittenExam/23_24_S5_ICT_Exam02.pdf"),
    ("23/24 Term2 DOCX", _ROOT / "Subjects/S5-ICT/past-papers/2024-2025/Term 02/WrittenExam/23_24_S5_ICT_Exam02.docx"),
    ("24/25 Term2 DOCX", _ROOT / "Subjects/S5-ICT/past-papers/2024-2025/Term 02/WrittenExam/24_25_S5_ICT_Exam02.docx"),
    ("24/25 Term2 PDF", _ROOT / "Subjects/S5-ICT/past-papers/2024-2025/Term 02/WrittenExam/24_25_S5_ICT_Exam02.pdf"),
    ("24/25 Term1 DOCX", _ROOT / "Subjects/S5-ICT/past-papers/2024-2025/Term 01/WrittenExam/24_25_S5_ICT_Exam01.docx"),
]
OUT = Path(__file__).resolve().parent / "25_26_S5_ICT_Exam02.past90.json"


def main() -> int:
    cand_spec = docx_to_spec(CAND)
    c_items = list(spec_items(cand_spec))

    best_item: dict = {}
    best_80: dict = {}
    for label, ref in REFS:
        if not ref.exists():
            continue
        ref_spec = docx_to_spec(ref)
        for d in compare_spec_to_spec(cand_spec, ref_spec, reference_path=label, threshold=THRESH - 0.001):
            if d.similarity >= THRESH:
                k = d.candidate_id
                if k not in best_item or d.similarity > best_item[k].similarity:
                    best_item[k] = d
        for d in compare_spec_to_spec(cand_spec, ref_spec, reference_path=label, threshold=0.80 - 0.001):
            if 0.80 <= d.similarity < THRESH:
                k = d.candidate_id
                if k not in best_80 or d.similarity > best_80[k].similarity:
                    best_80[k] = d

    cand_lines = extract_lines(CAND)
    c_mcq = extract_mcq_stems(cand_lines)
    c_written = extract_written_units(cand_lines)

    best_mcq: dict = {}
    best_written: dict = {}
    line90: list = []
    sec90: list = []
    for label, ref in REFS:
        if not ref.exists():
            continue
        for m in compare_documents(CAND, ref, reference_label=label):
            if m.similarity < THRESH:
                continue
            if m.match_type in ("mcq_full", "mcq_stem"):
                k = m.candidate_label
                if k not in best_mcq or m.similarity > best_mcq[k].similarity:
                    best_mcq[k] = m
            elif m.match_type == "written":
                k = m.candidate_label
                if k not in best_written or m.similarity > best_written[k].similarity:
                    best_written[k] = m
            elif m.match_type == "line":
                line90.append(m)
            elif m.match_type == "section":
                sec90.append(m)

    ge90_items = sorted(best_item.values(), key=lambda x: -x.similarity)

    print("=== 25/26 S5 ICT Exam02 vs past papers (>=90% similarity) ===\n")
    print(f"Candidate: {CAND.name}")
    print(f"Spec items (whole questions): {len(c_items)}")
    print(f"  >=90% match to any past paper: {len(ge90_items)}")
    print(f"  80-89% (near match): {len(best_80)}")
    print(f"MCQ slots: {len(c_mcq)}  |  >=90%: {len(best_mcq)}")
    print(f"Written sub-units (乙/丙): {len(c_written)}  |  >=90%: {len(best_written)}")
    print(f"Line-level hits >=90%: {len(line90)} (SQL fragments etc., not full questions)")

    if ge90_items:
        print("\n--- Whole questions >=90% ---")
        for d in ge90_items:
            print(f"  {d.similarity:.0%}  {d.candidate_id}  vs  {d.reference_id}  [{d.reference}]")
            snip = (d.candidate_text or "")[:72]
            print(f"    {snip}")

    if best_mcq:
        print("\n--- MCQ >=90% ---")
        for m in sorted(best_mcq.values(), key=lambda x: -x.similarity):
            print(f"  {m.similarity:.0%}  {m.candidate_label} vs {m.reference_label} [{m.reference}]")

    if best_written:
        print("\n--- Written units >=90% ---")
        for m in sorted(best_written.values(), key=lambda x: -x.similarity):
            print(f"  {m.similarity:.0%}  {m.candidate_label} vs {m.reference_label} [{m.reference}]")
            print(f"    {m.candidate_snippet[:70]}")

    if best_80 and not ge90_items:
        print("\n--- 80-89% (not quite 9成) top items ---")
        for d in sorted(best_80.values(), key=lambda x: -x.similarity)[:12]:
            print(f"  {d.similarity:.0%}  {d.candidate_id}  vs  {d.reference_id}  [{d.reference}]")

    by_ref = defaultdict(int)
    for m in line90:
        by_ref[m.reference] += 1
    if by_ref:
        print("\n--- Line-level >=90% by reference (shell/SQL overlap) ---")
        for ref, n in sorted(by_ref.items(), key=lambda x: -x[1]):
            print(f"  {ref}: {n}")

    payload = {
        "threshold": THRESH,
        "candidate": str(CAND),
        "total_spec_items": len(c_items),
        "spec_items_ge90": len(ge90_items),
        "spec_items_80_89": len(best_80),
        "mcq_total": len(c_mcq),
        "mcq_ge90": len(best_mcq),
        "written_total": len(c_written),
        "written_ge90": len(best_written),
        "line_hits_ge90": len(line90),
        "matches_ge90": [
            {
                "candidate_id": d.candidate_id,
                "reference_id": d.reference_id,
                "reference": d.reference,
                "similarity": round(d.similarity, 4),
                "snippet": (d.candidate_text or "")[:200],
            }
            for d in ge90_items
        ],
        "mcq_matches": [
            {
                "candidate": m.candidate_label,
                "reference": m.reference_label,
                "ref_file": m.reference,
                "similarity": round(m.similarity, 4),
            }
            for m in sorted(best_mcq.values(), key=lambda x: -x.similarity)
        ],
        "written_matches": [
            {
                "candidate": m.candidate_label,
                "reference": m.reference_label,
                "ref_file": m.reference,
                "similarity": round(m.similarity, 4),
                "snippet": m.candidate_snippet[:120],
            }
            for m in sorted(best_written.values(), key=lambda x: -x.similarity)
        ],
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nReport: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
