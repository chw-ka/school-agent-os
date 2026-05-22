#!/usr/bin/env python3
"""Audit exam vs past papers + DSE bank at 60% (too similar = risk)."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(_ROOT / "shared-tools/question-quality-check"))

from check_spec import compare_spec_to_spec
from exam_spec import load_spec, spec_items
from quality_lib import discover_past_papers, text_similarity
from spec_from_docx import docx_to_spec

TH = 0.60
SPEC = _ROOT / "Subjects/S5-ICT/past-papers/2025-2026/Term 02/_generation/25_26_S5_ICT_Exam02.spec.json"
BANK = _ROOT / "Subjects/DSE-ICT/question-bank"
OUT = Path(__file__).resolve().parent / "25_26_S5_ICT_Exam02.risk60.json"


def _stem(t: str) -> str:
    lines: list[str] = []
    for line in (t or "").split("\n"):
        s = line.strip()
        if re.match(r"^[ABCD][\.\)]", s):
            break
        if s:
            lines.append(s)
    return "\n".join(lines)


def _load_bank() -> dict[str, dict]:
    by_id: dict[str, dict] = {}
    for year in ("2021", "2022", "2023", "2024", "2025"):
        for slug in ("Paper1_MultipleChoice", "Paper1A_MultipleChoice"):
            path = BANK / year / slug / "questions.json"
            if not path.exists():
                continue
            for it in json.loads(path.read_text(encoding="utf-8")).get("items", []):
                iid = it.get("id")
                if iid:
                    by_id[iid] = it
    return by_id


def main() -> int:
    spec = load_spec(SPEC)
    mcqs = [x for x in spec_items(spec) if x.id.startswith("mcq")]
    bank = _load_bank()

    past_refs: list[Path] = []
    for p in discover_past_papers(_ROOT / "Subjects", years=3, subject_subpath="S5-ICT"):
        if "25_26" not in p.name:
            past_refs.append(p)
    for extra in (
        _ROOT / "Subjects/S5-ICT/past-papers/2024-2025/Term 02/WrittenExam/24_25_S5_ICT_Exam02.docx",
        _ROOT / "Subjects/S5-ICT/past-papers/2024-2025/Term 02/WrittenExam/23_24_S5_ICT_Exam02.pdf",
    ):
        if extra.exists() and extra not in past_refs:
            past_refs.append(extra)

    print(f"Rule: similarity > {TH:.0%} = too close (complaint risk)\n")

    fail_past: set[str] = set()
    fail_bank: set[str] = set()
    rows: list[dict] = []

    for it in mcqs:
        et, es = it.text or "", _stem(it.text or "")
        best_past, best_past_ref = 0.0, ""
        for ref in past_refs:
            ref_spec = docx_to_spec(ref)
            for d in compare_spec_to_spec(spec, ref_spec, reference_path=ref.name, threshold=TH - 0.001):
                if d.candidate_id == it.id and d.similarity > best_past:
                    best_past = d.similarity
                    best_past_ref = f"{ref.name} / {d.reference_id}"
        best_bank, best_bank_id = 0.0, ""
        for bid, b in bank.items():
            bt = b.get("text") or ""
            bs = b.get("stem") or _stem(bt)
            sim = max(text_similarity(et, bt), text_similarity(es, bs))
            if sim > best_bank:
                best_bank, best_bank_id = sim, bid

        too_past = best_past > TH
        too_bank = best_bank > TH
        if too_past:
            fail_past.add(it.id)
        if too_bank:
            fail_bank.add(it.id)
        rows.append(
            {
                "id": it.id,
                "past_sim": round(best_past, 4),
                "past_ref": best_past_ref,
                "bank_sim": round(best_bank, 4),
                "bank_id": best_bank_id,
                "fail_past": too_past,
                "fail_bank": too_bank,
                "preview": es[:80],
            }
        )

    fail_either = {r["id"] for r in rows if r["fail_past"] or r["fail_bank"]}
    pass_both = [r for r in rows if not r["fail_past"] and not r["fail_bank"]]

    print("=== MCQ vs school past papers (>60%) ===")
    print(f"TOO SIMILAR: {len(fail_past)} / {len(mcqs)}")
    print("=== MCQ vs DSE question-bank (>60%) ===")
    print(f"TOO SIMILAR: {len(fail_bank)} / {len(mcqs)}")
    print("=== MCQ pass BOTH (<=60% past AND <=60% bank) ===")
    print(f"OK: {len(pass_both)} / {len(mcqs)}")
    print()

    for r in sorted(rows, key=lambda x: -max(x["past_sim"], x["bank_sim"])):
        if not (r["fail_past"] or r["fail_bank"]):
            continue
        tags = []
        if r["fail_past"]:
            tags.append("past")
        if r["fail_bank"]:
            tags.append("bank")
        print(f"  {r['id']}  past={r['past_sim']:.0%}  bank={r['bank_sim']:.0%}  [{','.join(tags)}]")
        if r["fail_past"]:
            print(f"    past: {r['past_ref']}")
        if r["fail_bank"]:
            print(f"    bank: {r['bank_id']}")

    if pass_both:
        print("\n--- OK (<=60% both) ---")
        for r in pass_both:
            print(f"  {r['id']}  past={r['past_sim']:.0%}  bank={r['bank_sim']:.0%}")

    payload = {
        "threshold": TH,
        "rule": "similarity > threshold = too similar",
        "mcq_total": len(mcqs),
        "fail_past_papers": len(fail_past),
        "fail_dse_bank": len(fail_bank),
        "fail_either": len(fail_either),
        "pass_both": len(pass_both),
        "past_references": [str(p) for p in past_refs],
        "rows": rows,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nReport: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
