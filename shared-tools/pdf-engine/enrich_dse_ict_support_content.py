#!/usr/bin/env python3
"""Back-fill support_content (algorithms, ASCII tables/diagrams) across question-bank."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

_SHARED = Path(__file__).resolve().parents[1]
if str(_SHARED) not in sys.path:
    sys.path.insert(0, str(_SHARED))

from dse_ict_support_content import apply_support_to_item  # noqa: E402

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
        pq["text"] = src.get("text", pq.get("text"))
        if src.get("stem"):
            pq["stem"] = src["stem"]
        if src.get("support_content"):
            pq["support_content"] = src["support_content"]


def enrich_bank(
    bank_root: Path,
    *,
    years: set[str] | None = None,
    force: bool = False,
    dry_run: bool = False,
) -> dict[str, int]:
    stats = {
        "files": 0,
        "items": 0,
        "supplemented": 0,
        "needs_review": 0,
        "skipped_existing": 0,
    }

    for path in sorted(bank_root.glob("*/*/questions.json")):
        year_m = re.match(r"^(\d{4})$", path.parent.parent.name)
        if not year_m:
            continue
        year = year_m.group(1)
        if years and year not in years:
            continue

        data = json.loads(path.read_text(encoding="utf-8"))
        items = data.get("items") or []
        file_changed = False
        for item in items:
            stats["items"] += 1
            if item.get("support_content") and not force:
                stats["skipped_existing"] += 1
                continue
            if apply_support_to_item(item, force=force):
                file_changed = True
                stats["supplemented"] += 1
                sc = item.get("support_content") or {}
                if sc.get("status") == "needs_review":
                    stats["needs_review"] += 1

        if file_changed:
            stats["files"] += 1
            meta = data.setdefault("meta", {})
            meta["support_enriched_at"] = datetime.now(timezone.utc).isoformat()
            _sync_paper_questions(data)
            if not dry_run:
                path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            rel = path.relative_to(REPO)
            print(f"{'[dry-run] ' if dry_run else ''}enriched {rel} (+{sum(1 for it in items if it.get('support_content'))} with support)")

    return stats


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bank", type=Path, default=DEFAULT_BANK)
    ap.add_argument("--years", nargs="*", help="Limit to years e.g. 2021 2022")
    ap.add_argument("--force", action="store_true", help="Recompute even if support_content exists")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    years = set(args.years) if args.years else None
    stats = enrich_bank(args.bank.expanduser().resolve(), years=years, force=args.force, dry_run=args.dry_run)
    print(
        f"Done: {stats['supplemented']} items supplemented in {stats['files']} files "
        f"({stats['needs_review']} needs_review, {stats['skipped_existing']} skipped existing)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
