#!/usr/bin/env python3
"""Print CDP Runtime.evaluate payloads for chunked zip upload (one JSON line per step)."""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("zip_path", type=Path)
    p.add_argument("--chunk", type=int, default=32000)
    args = p.parse_args()

    b64 = base64.b64encode(args.zip_path.read_bytes()).decode()
    chunks = [b64[i : i + args.chunk] for i in range(0, len(b64), args.chunk)]
    name = args.zip_path.name
    steps: list[str] = []
    for i, c in enumerate(chunks):
        if i == 0:
            steps.append(f"window.__zipB64 = {json.dumps(c)}; 'ok{i}'")
        else:
            steps.append(f"window.__zipB64 += {json.dumps(c)}; 'ok{i}'")
    steps.append(
        f"""(() => {{
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
    )
    for s in steps:
        print(json.dumps({"expression": s, "returnByValue": True}))


if __name__ == "__main__":
    main()
