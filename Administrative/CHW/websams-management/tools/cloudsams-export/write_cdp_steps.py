#!/usr/bin/env python3
import base64
import json
import sys
from pathlib import Path

zip_path = Path(sys.argv[1])
out_path = Path(sys.argv[2])
chunk_size = int(sys.argv[3]) if len(sys.argv) > 3 else 32000

b64 = base64.b64encode(zip_path.read_bytes()).decode()
chunks = [b64[i : i + chunk_size] for i in range(0, len(b64), chunk_size)]
name = zip_path.name
steps: list[dict] = []
for i, c in enumerate(chunks):
    expr = (
        f"window.__zipB64 = {json.dumps(c)}; 'ok{i}'"
        if i == 0
        else f"window.__zipB64 += {json.dumps(c)}; 'ok{i}'"
    )
    steps.append({"expression": expr, "returnByValue": True})
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
steps.append({"expression": final, "returnByValue": True})
out_path.write_text(json.dumps(steps), encoding="utf-8")
print(len(steps))
