#!/usr/bin/env python3
"""Execute CloudSAMS score zip import steps via prepared _steps_{seq}.json files.

Writes MCP payload files for each step; intended for agent-driven browser_cdp calls.
Also supports --print-step to emit one step JSON for direct CDP use.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

DEFAULT_LOCAL = Path(__file__).resolve().parents[2] / "cloudsams-templates" / "asr" / "_local"


def load_steps(seq: str, base: Path) -> list[dict]:
    path = base / f"_steps_{seq}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("seq", help="Zip sequence id, e.g. 124")
    p.add_argument("--base", type=Path, default=DEFAULT_LOCAL)
    p.add_argument("--view-id", default="2a0b75")
    p.add_argument("--step", type=int, help="Print payload for one step index")
    p.add_argument("--count", action="store_true", help="Print number of steps")
    args = p.parse_args()

    steps = load_steps(args.seq, args.base)
    if args.count:
        print(len(steps))
        return

    if args.step is None:
        for i, step in enumerate(steps):
            out = args.base / "_cdp_exec" / f"mcp_{args.seq}_{i}.json"
            out.parent.mkdir(parents=True, exist_ok=True)
            payload = {"method": "Runtime.evaluate", "params": step, "viewId": args.view_id}
            out.write_text(json.dumps(payload), encoding="utf-8")
        print(f"wrote {len(steps)} payloads for seq {args.seq}")
        return

    if args.step < 0 or args.step >= len(steps):
        raise SystemExit(f"step {args.step} out of range 0..{len(steps)-1}")
    print(json.dumps(steps[args.step]))


if __name__ == "__main__":
    main()
