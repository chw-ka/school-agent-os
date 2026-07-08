#!/usr/bin/env python3
"""Emit chunked base64 upload JS for large import zips."""

from __future__ import annotations

import argparse
import base64
from pathlib import Path


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("zip_path", type=Path)
    p.add_argument("--name", help="Filename shown in upload widget")
    p.add_argument("--chunk", type=int, default=8000)
    args = p.parse_args()
    b64 = base64.b64encode(args.zip_path.read_bytes()).decode()
    chunks = [b64[i : i + args.chunk] for i in range(0, len(b64), args.chunk)]
    name = args.name or args.zip_path.name
    print(
        f"""(async () => {{
  const parts = {chunks!r};
  const b64 = parts.join("");
  const bytes = Uint8Array.from(atob(b64), (c) => c.charCodeAt(0));
  const file = new File([bytes], {name!r}, {{ type: "application/zip" }});
  const input = document.getElementById("fmAsrDataEntryImport:fileUpload_input");
  if (!input) return {{ error: "no input" }};
  const dt = new DataTransfer();
  dt.items.add(file);
  input.files = dt.files;
  input.dispatchEvent(new Event("change", {{ bubbles: true }}));
  const w = PrimeFaces.widgets.widget_fmAsrDataEntryImport_fileUpload;
  if (w && w.upload) w.upload();
  return {{ ok: true, size: bytes.length, name: {name!r} }};
}})()"""
    )


if __name__ == "__main__":
    main()
