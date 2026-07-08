#!/usr/bin/env python3
"""Append base64 chunk files and write final zip. Gitignored inputs."""

from __future__ import annotations

import argparse
import base64
from pathlib import Path


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("chunk_dir", type=Path, help="Directory with chunk_000.b64, ...")
    p.add_argument("out_zip", type=Path)
    args = p.parse_args()
    parts = sorted(args.chunk_dir.glob("chunk_*.b64"))
    if not parts:
        raise SystemExit(f"No chunks in {args.chunk_dir}")
    data = b"".join(base64.b64decode(f.read_text(encoding="ascii").strip()) for f in parts)
    args.out_zip.parent.mkdir(parents=True, exist_ok=True)
    args.out_zip.write_bytes(data)
    print(f"Wrote {len(data)} bytes -> {args.out_zip}")


if __name__ == "__main__":
    main()
