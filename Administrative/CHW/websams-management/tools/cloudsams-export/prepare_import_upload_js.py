#!/usr/bin/env python3
"""Print JS snippet to attach import zip to CloudSAMS file upload input."""

from __future__ import annotations

import argparse
import base64
from pathlib import Path


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("zip_path", type=Path)
    p.add_argument("--name", help="Filename shown in upload widget")
    args = p.parse_args()
    b64 = base64.b64encode(args.zip_path.read_bytes()).decode()
    name = args.name or args.zip_path.name
    print(
        f"""(function() {{
  const b64 = "{b64}";
  const bytes = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
  const file = new File([bytes], {name!r}, {{type: 'application/zip'}});
  const input = document.getElementById('fmAsrDataEntryImport:fileUpload_input');
  if (!input) return {{error: 'no input'}};
  const dt = new DataTransfer();
  dt.items.add(file);
  input.files = dt.files;
  input.dispatchEvent(new Event('change', {{bubbles: true}}));
  const w = PrimeFaces.widgets.widget_fmAsrDataEntryImport_fileUpload;
  if (w && w.upload) w.upload();
  return {{ok: true, size: bytes.length, name: {name!r}}};
}})()"""
    )


if __name__ == "__main__":
    main()
