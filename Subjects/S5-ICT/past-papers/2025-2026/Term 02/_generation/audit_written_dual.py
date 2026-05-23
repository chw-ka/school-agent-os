#!/usr/bin/env python3
"""Audit 乙／丙 in exam DOCX vs DSE bank: stem 60%, subquestion 85%."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(_ROOT / "shared-tools/question-quality-check"))
sys.path.insert(0, str(_ROOT / "shared-tools/paper-generator"))

from check_spec import load_dse_ict_bank_written_spec
from quality_lib import SECTION_BOUNDARIES, THRESH_WRITTEN_STEM, THRESH_WRITTEN_SUBPART, _section_lines, extract_lines
from written_similarity import audit_written_text_vs_bank

DOCX = _ROOT / "Subjects/S5-ICT/past-papers/2025-2026/Term 02/WrittenExam/25_26_S5_ICT_Exam02.docx"
OUT = Path(__file__).resolve().parent / "25_26_S5_ICT_Exam02.written_dual_audit.json"

# Split 乙／丙 into scenario blocks (between subpart markers / blank scenario lines)
_SCENARIO_BREAK = re.compile(r"^\s*(?:\t+\s*)?\([a-z]{1,2}\)\s", re.I)


def _scenario_blocks(sec_lines: list[str]) -> list[tuple[str, str]]:
    """Return (label, text) per main scenario cluster in a section."""
    blocks: list[tuple[str, list[str]]] = []
    current: list[str] = []
    label = ""

    for ln in sec_lines:
        s = ln.strip()
        if not s or "部 (" in s or "分)：" in s or "分）：" in s:
            continue
        if _SCENARIO_BREAK.match(ln) and current:
            blocks.append((label or f"block-{len(blocks)+1}", current))
            current = [ln]
            label = s[:40]
        elif _SCENARIO_BREAK.match(ln):
            current = [ln]
            label = s[:40]
        else:
            if not current and len(s) >= 20 and not s.startswith("\t"):
                label = s[:40]
            current.append(ln)

    if current:
        blocks.append((label or f"block-{len(blocks)+1}", current))

    out: list[tuple[str, str]] = []
    for i, (lab, lines) in enumerate(blocks):
        text = "\n".join(lines).strip()
        if len(text) >= 30:
            out.append((f"{lab[:24]}-{i+1}", text))
    return out


def main() -> int:
    bank = load_dse_ict_bank_written_spec()["items"]
    lines = extract_lines(DOCX)
    audits: list[dict] = []

    for sec, end in SECTION_BOUNDARIES:
        if sec not in ("乙部", "丙部"):
            continue
        sec_lines = _section_lines(lines, sec, end)
        for block_id, text in _scenario_blocks(sec_lines):
            label = f"{sec}-{block_id}"
            a = audit_written_text_vs_bank(text, bank, label=label)
            audits.append(
                {
                    "id": label,
                    "section": sec,
                    "stem_sim": round(a.stem_sim, 4),
                    "stem_bank_id": a.stem_bank_id,
                    "fail_stem": a.fail_stem,
                    "subpart_max_sim": round(a.subpart_max_sim, 4),
                    "subpart_bank_id": a.subpart_bank_id,
                    "fail_subpart": a.fail_subpart,
                    "fail": a.fail,
                    "subparts": [
                        {
                            "preview": sp.preview,
                            "sim": round(sp.similarity, 4),
                            "bank_id": sp.bank_id,
                            "fail": sp.similarity > THRESH_WRITTEN_SUBPART,
                        }
                        for sp in a.subparts
                    ],
                    "preview": text[:120].replace("\n", " "),
                }
            )

    fail_stem = [x for x in audits if x["fail_stem"]]
    fail_sub = [x for x in audits if x["fail_subpart"]]

    payload = {
        "candidate": str(DOCX),
        "thresholds": {
            "stem": THRESH_WRITTEN_STEM,
            "subpart": THRESH_WRITTEN_SUBPART,
        },
        "rule": "整條 > 60% or 子題 > 85% = too close to DSE bank",
        "blocks": len(audits),
        "fail_stem": len(fail_stem),
        "fail_subpart": len(fail_sub),
        "fail_either": len([x for x in audits if x["fail"]]),
        "audits": sorted(audits, key=lambda x: (-max(x["stem_sim"], x["subpart_max_sim"]), x["id"])),
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Exam: {DOCX.name}")
    print(f"Rule: 整條 > {THRESH_WRITTEN_STEM:.0%} | 子題 > {THRESH_WRITTEN_SUBPART:.0%}\n")
    print(f"Blocks checked: {len(audits)}")
    print(f"Fail stem (>{THRESH_WRITTEN_STEM:.0%}): {len(fail_stem)}")
    print(f"Fail subpart (>{THRESH_WRITTEN_SUBPART:.0%}): {len(fail_sub)}")

    for x in audits:
        if not x["fail"]:
            continue
        tags = []
        if x["fail_stem"]:
            tags.append(f"stem={x['stem_sim']:.0%}")
        if x["fail_subpart"]:
            tags.append(f"sub={x['subpart_max_sim']:.0%}")
        print(f"\n  {x['id']}  [{', '.join(tags)}]")
        if x["fail_stem"]:
            print(f"    stem → {x['stem_bank_id']}")
        if x["fail_subpart"]:
            print(f"    sub  → {x['subpart_bank_id']}")
        for sp in x["subparts"]:
            if sp["fail"]:
                print(f"    ({sp['sim']:.0%}) {sp['preview'][:70]}… → {sp['bank_id']}")

    print(f"\nReport: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
