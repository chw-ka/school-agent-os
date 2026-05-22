#!/usr/bin/env python3
"""Re-tag all DSE ICT question-bank items: concepts + syllabus_status (2021 revision)."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_SHARED = Path(__file__).resolve().parents[1]
if str(_SHARED) not in sys.path:
    sys.path.insert(0, str(_SHARED))

from dse_ict_syllabus import load_concepts_cfg, tag_item  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
DEFAULT_BANK = REPO / "Subjects/DSE-ICT/question-bank"


def _sync_paper_questions(spec: dict) -> None:
    paper = spec.get("paper") or {}
    questions = paper.get("questions") or []
    by_id = {it["id"]: it for it in spec.get("items", []) if it.get("id")}
    for pq in questions:
        src = by_id.get(pq.get("id"))
        if not src:
            continue
        pq["concepts"] = src.get("concepts", [])
        if src.get("syllabus_status"):
            pq["syllabus_status"] = src["syllabus_status"]


def retag_bank(bank_root: Path, *, dry_run: bool = False) -> dict[str, int]:
    cfg = load_concepts_cfg()
    stats = {"files": 0, "items": 0, "out_of_syllabus": 0, "current": 0}

    for path in sorted(bank_root.glob("*/**/questions.json")):
        year_m = re.match(r"^(\d{4})$", path.parent.parent.name)
        if not year_m:
            continue
        year = year_m.group(1)
        slug = path.parent.name
        data = json.loads(path.read_text(encoding="utf-8"))
        items = data.get("items") or []
        changed = False
        for item in items:
            before = json.dumps(
                {
                    "concepts": item.get("concepts"),
                    "syllabus_status": item.get("syllabus_status"),
                },
                ensure_ascii=False,
                sort_keys=True,
            )
            tag_item(item, paper_slug=slug, paper_year=year, concepts_cfg=cfg)
            after = json.dumps(
                {
                    "concepts": item.get("concepts"),
                    "syllabus_status": item.get("syllabus_status"),
                },
                ensure_ascii=False,
                sort_keys=True,
            )
            if before != after:
                changed = True
            stats["items"] += 1
            if item.get("syllabus_status") == "out_of_syllabus":
                stats["out_of_syllabus"] += 1
            else:
                stats["current"] += 1

        if changed and not dry_run:
            _sync_paper_questions(data)
            meta = data.setdefault("meta", {})
            meta["syllabus_retagged_at"] = __import__("datetime").datetime.now(
                __import__("datetime").timezone.utc
            ).isoformat()
            meta["syllabus_revision"] = cfg.get("syllabus_revision", "2021")
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"Updated {path.relative_to(REPO)} ({len(items)} items)")
        stats["files"] += 1

    return stats


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bank", type=Path, default=DEFAULT_BANK)
    ap.add_argument("--dry-run", action="store_true", help="Count only; do not write files")
    args = ap.parse_args(argv)
    stats = retag_bank(args.bank.expanduser().resolve(), dry_run=args.dry_run)
    print(
        f"Done: {stats['files']} files, {stats['items']} items — "
        f"current={stats['current']}, out_of_syllabus={stats['out_of_syllabus']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
