#!/usr/bin/env python3
"""Save base64 zip from stdin or arg to _local/. Gitignored output."""

from __future__ import annotations

import argparse
import base64
import sys
from pathlib import Path

DEFAULT_DIR = Path(__file__).resolve().parents[2] / "cloudsams-templates" / "asr" / "_local"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("out_name", help="Output zip filename")
    p.add_argument("--dir", type=Path, default=DEFAULT_DIR)
    p.add_argument("--b64-file", type=Path, help="Read base64 from file instead of stdin")
    args = p.parse_args()
    raw = args.b64_file.read_text(encoding="utf-8") if args.b64_file else sys.stdin.read()
    data = base64.b64decode(raw.strip())
    out = args.dir / args.out_name
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    print(f"Wrote {len(data)} bytes -> {out}")


if __name__ == "__main__":
    main()
