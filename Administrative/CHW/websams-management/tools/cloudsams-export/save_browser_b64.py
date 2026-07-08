#!/usr/bin/env python3
"""Assemble b64 chunks from browser export and save zip."""

from __future__ import annotations

import argparse
import base64
from pathlib import Path


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("chunk_dir", type=Path)
    p.add_argument("out_zip", type=Path)
    args = p.parse_args()
    parts = []
    for i in range(10):
        f = args.chunk_dir / f"chunk_{i:03d}.b64"
        if f.is_file():
            parts.append(f.read_text(encoding="ascii").strip())
    if not parts:
        raise SystemExit(f"No chunks in {args.chunk_dir}")
    data = base64.b64decode("".join(parts))
    args.out_zip.parent.mkdir(parents=True, exist_ok=True)
    args.out_zip.write_bytes(data)
    print(f"Wrote {len(data)} bytes -> {args.out_zip}")


if __name__ == "__main__":
    main()
