#!/usr/bin/env python3
"""Regenerate S3 CMP Chinese exam cover from 24_25 English written-exam layout."""
from __future__ import annotations

import argparse
from pathlib import Path

from docx import Document

from docx_inplace import ZhCoverPatch, regenerate_cmp_zh_cover_from_en_reference

_REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REFERENCE = (
    _REPO_ROOT
    / "Subjects/S3-CMP/past-papers/2024-2025/Term 02/WrittenExam"
    / "24_25_S3_CMP_Term2_WrittenExam.docx"
)

ZH_INSTRUCTIONS = [
    "考生須知:",
    "考生須於試題簿及答題紙的第一頁適當位置填寫考生姓名、班別、學號及試場。",
    "全卷共有四個部分，分別為甲部、乙部、丙部及丁部。",
    "所有問題均須作答。答案須寫在答題紙中適當的位置內。",
]


def main() -> int:
    p = argparse.ArgumentParser(
        description="Regenerate Chinese CMP cover using 24_25 written-exam spacing."
    )
    p.add_argument("--target", required=True, help="Exam .docx to update (in place).")
    p.add_argument(
        "--reference",
        default=str(DEFAULT_REFERENCE),
        help="24_25 cover layout source.",
    )
    p.add_argument("--date", default="__________")
    p.add_argument("--time", default="__________")
    p.add_argument("--year", default="2025 – 2026")
    p.add_argument("--term", default="下學期考試")
    p.add_argument("--pages", default="5頁")
    p.add_argument("--total", default="50")
    args = p.parse_args()

    target = Path(args.target)
    reference = Path(args.reference)
    doc = Document(str(target))
    ref = Document(str(reference))

    patch = ZhCoverPatch(
        school="迦密聖道中學",
        year_term=f"{args.year} {args.term}",
        level="中三級 電腦認知",
        paper="試題簿",
        date_line=f"\t日期:\t{args.date}",
        time_line=f"\t時間:\t{args.time}",
        duration_line="\t時限:\t30分鐘",
        pages_line=f"\t頁數:\t{args.pages}",
        total_line=f"\t總分:\t{args.total}",
    )
    regenerate_cmp_zh_cover_from_en_reference(
        target_doc=doc,
        reference_doc=ref,
        patch=patch,
        instructions=ZH_INSTRUCTIONS,
    )
    doc.save(str(target))
    print(f"Updated cover: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
