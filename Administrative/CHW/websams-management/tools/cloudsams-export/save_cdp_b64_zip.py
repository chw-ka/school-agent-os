#!/usr/bin/env python3
"""Save zip from browser CDP Runtime.evaluate JSON response."""

from __future__ import annotations

import argparse
import base64
import json
import shutil
import sys
import zipfile
from pathlib import Path

import pyzipper

DEFAULT_DIR = Path(__file__).resolve().parents[2] / "cloudsams-templates" / "asr" / "_local"
PWD = b"EvanGelisTic1617!"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("cdp_json", type=Path, help="CDP response JSON file")
    p.add_argument("out_name", help="Output zip filename under _local/")
    p.add_argument("--dir", type=Path, default=DEFAULT_DIR)
    p.add_argument("--level", help="Verify inner zip names contain this level tag, e.g. S2")
    p.add_argument(
        "--whole-school",
        action="store_true",
        help="Verify all of S1..S6 appear in inner zip names (use for whole-school export)",
    )
    args = p.parse_args()

    resp = json.loads(args.cdp_json.read_text(encoding="utf-8"))
    val = resp["result"]["value"]
    data = base64.b64decode(val["b64"])
    dest = args.dir / args.out_name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    print(f"Wrote {len(data)} bytes -> {dest}")

    if args.whole_school:
        work = args.dir / "_verify-whole-school"
        if work.exists():
            shutil.rmtree(work)
        work.mkdir()
        with pyzipper.AESZipFile(dest) as z:
            z.extractall(work, pwd=PWD)
        inner = sorted(work.glob("*.zip"))
        expect = {f"S{i}" for i in range(1, 7)}
        found = set()
        for pth in inner:
            for lvl in expect:
                if f"_{lvl}_" in pth.name:
                    found.add(lvl)
        print("Inner:", len(inner), "class zips; levels:", sorted(found))
        missing = expect - found
        if missing:
            print("ERROR missing levels:", sorted(missing), file=sys.stderr)
            sys.exit(1)
        print("OK whole-school")
    elif args.level:
        work = args.dir / f"_verify-{args.level}-t1"
        if work.exists():
            shutil.rmtree(work)
        work.mkdir()
        with pyzipper.AESZipFile(dest) as z:
            z.extractall(work, pwd=PWD)
        inner = sorted(work.glob("*.zip"))
        bad = [p.name for p in inner if f"_{args.level}_" not in p.name]
        print("Inner:", [p.name for p in inner])
        if bad:
            print("ERROR wrong level:", bad, file=sys.stderr)
            sys.exit(1)
        print("OK", args.level)


if __name__ == "__main__":
    main()
