#!/usr/bin/env python3
"""Print CDP step payloads sequentially for agent MCP invocation.

Usage:
  python exec_score_import_steps.py 124 0   # print step 0 JSON params only
  python exec_score_import_steps.py 124 all # print count
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DEFAULT_LOCAL = Path(__file__).resolve().parents[2] / "cloudsams-templates" / "asr" / "_local"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("seq")
    p.add_argument("step", help="step index or 'all'")
    p.add_argument("--base", type=Path, default=DEFAULT_LOCAL)
    args = p.parse_args()

    steps = json.loads((args.base / f"_steps_{args.seq}.json").read_text(encoding="utf-8"))
    if args.step == "all":
        print(len(steps))
        return
    idx = int(args.step)
    print(json.dumps(steps[idx], ensure_ascii=False))


if __name__ == "__main__":
    main()
