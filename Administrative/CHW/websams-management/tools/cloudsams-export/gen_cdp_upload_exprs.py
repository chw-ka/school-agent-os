#!/usr/bin/env python3
"""Generate CDP Runtime.evaluate expressions for chunked zip upload."""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("zip_path", type=Path)
    p.add_argument("--outdir", type=Path, required=True)
    p.add_argument("--chunk", type=int, default=4000)
    args = p.parse_args()

    b64 = base64.b64encode(args.zip_path.read_bytes()).decode()
    chunks = [b64[i : i + args.chunk] for i in range(0, len(b64), args.chunk)]
    args.outdir.mkdir(parents=True, exist_ok=True)

    for i, c in enumerate(chunks):
        if i == 0:
            expr = f"window.__zipB64 = {json.dumps(c)}; 'ok{i}'"
        else:
            expr = f"window.__zipB64 += {json.dumps(c)}; 'ok{i}'"
        (args.outdir / f"chunk{i}.txt").write_text(expr, encoding="utf-8")

    name = args.zip_path.name
    final = f"""(() => {{
  const bytes = Uint8Array.from(atob(window.__zipB64), (c) => c.charCodeAt(0));
  const file = new File([bytes], {json.dumps(name)}, {{ type: 'application/zip' }});
  const input = document.getElementById('fmAsrDataEntryImport:fileUpload_input');
  if (!input) return {{ error: 'no input' }};
  const dt = new DataTransfer();
  dt.items.add(file);
  input.files = dt.files;
  input.dispatchEvent(new Event('change', {{ bubbles: true }}));
  const w = PrimeFaces.widgets.widget_fmAsrDataEntryImport_fileUpload;
  if (w && w.upload) w.upload();
  return {{ ok: true, size: bytes.length, name: {json.dumps(name)} }};
}})()"""
    (args.outdir / "final.txt").write_text(final, encoding="utf-8")
    print(f"chunks={len(chunks)} outdir={args.outdir}")


if __name__ == "__main__":
    main()
