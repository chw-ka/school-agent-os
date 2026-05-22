#!/usr/bin/env python3
"""Audit F5 ICT exam spec for intra-exam and past-paper MCQ duplicates."""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "shared-tools/question-quality-check"))

from check_spec import compare_intra_spec, compare_spec_to_spec
from exam_spec import load_spec
from spec_from_docx import docx_to_spec

SPEC = _ROOT / "Subjects/S5-ICT/past-papers/2025-2026/Term 02/_generation/25_26_S5_ICT_Exam02.spec.json"
REFS = [
    _ROOT / "Subjects/S5-ICT/past-papers/2024-2025/Term 02/WrittenExam/24_25_S5_ICT_Exam02.pdf",
    _ROOT / "Subjects/S5-ICT/past-papers/2024-2025/Term 02/WrittenExam/23_24_S5_ICT_Exam02.pdf",
    _ROOT / "Subjects/S5-ICT/past-papers/2024-2025/Term 02/WrittenExam/24_25_S5_ICT_Exam02.docx",
]


def main() -> int:
    spec = load_spec(SPEC)
    print("=== INTRA-EXAM DUPLICATES ===")
    intra = compare_intra_spec(spec)
    if not intra:
        print("None (>60%)")
    for d in intra:
        print(f"{d.candidate_id} vs {d.reference_id}: {d.similarity:.0%}")
        print(f"  {d.candidate_text[:100]}")

    for qid in ("mcq-03", "mcq-11", "mcq-13", "mcq-18", "mcq-08", "mcq-25", "mcq-27", "mcq-28"):
        for it in spec["items"]:
            if it["id"] == qid:
                print(f"\n=== {qid} ===")
                print(it["text"][:500])

    for ref in REFS:
        if not ref.exists():
            print(f"\nMISSING: {ref}")
            continue
        ref_spec = docx_to_spec(ref)
        dups = compare_spec_to_spec(spec, ref_spec, reference_path=ref.name)
        mcq = [d for d in dups if d.candidate_id.startswith("mcq")]
        print(f"\n=== vs {ref.name}: {len(mcq)} MCQ pairs >60% ===")
        for d in mcq[:12]:
            print(f"  {d.candidate_id} vs {d.reference_id}: {d.similarity:.0%}")
            print(f"    {d.candidate_text[:70]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
