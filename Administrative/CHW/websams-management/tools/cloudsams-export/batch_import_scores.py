#!/usr/bin/env python3
"""Upload filled score zips to CloudSAMS import page via Playwright CDP.

Prerequisites:
- CloudSAMS import page open in a Chromium-based browser
- Start Chrome with remote debugging, e.g.:
    chrome.exe --remote-debugging-port=9222
  Or use the Cursor embedded browser if PLAYWRIGHT_CDP_URL is set.

Usage:
  set PLAYWRIGHT_CDP_URL=http://127.0.0.1:9222
  python batch_import_scores.py --seq 124,134,144
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

DEFAULT_IMPORT_DIR = (
    Path(__file__).resolve().parents[2] / "cloudsams-templates" / "asr" / "_local" / "import-zips"
)
IMPORT_URL_FRAGMENT = "/flows/asr/data_entry/import"


def _upload_js(zip_path: Path) -> str:
    import base64

    b64 = base64.b64encode(zip_path.read_bytes()).decode()
    chunk = 8000
    parts = [b64[i : i + chunk] for i in range(0, len(b64), chunk)]
    name = zip_path.name
    return f"""(async () => {{
  const parts = {json.dumps(parts)};
  const b64 = parts.join("");
  const bytes = Uint8Array.from(atob(b64), (c) => c.charCodeAt(0));
  const file = new File([bytes], {json.dumps(name)}, {{ type: "application/zip" }});
  const input = document.getElementById("fmAsrDataEntryImport:fileUpload_input");
  if (!input) return {{ error: "no input" }};
  const dt = new DataTransfer();
  dt.items.add(file);
  input.files = dt.files;
  input.dispatchEvent(new Event("change", {{ bubbles: true }}));
  const w = PrimeFaces.widgets.widget_fmAsrDataEntryImport_fileUpload;
  if (w && w.upload) w.upload();
  return {{ ok: true, size: bytes.length, name: {json.dumps(name)} }};
}})()"""


def _read_counts(page) -> dict:
    return page.evaluate(
        """() => {
      const lines = document.body.innerText.split('\\n').map(l => l.trim()).filter(Boolean);
      const pick = (en, zh) => {
        const i = lines.indexOf(en);
        if (i >= 0 && i + 1 < lines.length) return lines[i + 1];
        const j = lines.indexOf(zh);
        return j >= 0 && j + 1 < lines.length ? lines[j + 1] : '';
      };
      return {
        total: pick('Total Records in the Import File', '匯入檔案的紀錄總數'),
        imported: pick('No. of Records Imported to the System', '匯入系統的紀錄數目'),
        rejected: pick('No. of Records Rejected by the System', '被系統拒絕的紀錄數目'),
        file: lines.find(l => /DE_524573/.test(l)) || ''
      };
    }"""
    )


def import_zip(page, zip_path: Path) -> dict:
    page.goto(page.url)  # refresh form state
    time.sleep(1)
    upload = page.evaluate(_upload_js(zip_path))
    if not upload.get("ok"):
        return {"zip": zip_path.name, "error": upload}
    time.sleep(6)
    save = page.locator("#fmAsrDataEntryImport\\:saveButton")
    if save.is_enabled():
        save.click()
        time.sleep(10)
    counts = _read_counts(page)
    save2 = page.locator("#fmAsrDataEntryImport\\:saveButton")
    if save2.is_enabled():
        save2.click()
        time.sleep(5)
        counts = _read_counts(page)
    return {"zip": zip_path.name, "upload": upload, **counts}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--seq", default="124,134,144", help="Zip seq ids, comma-separated")
    p.add_argument("--import-dir", type=Path, default=DEFAULT_IMPORT_DIR)
    p.add_argument("--cdp", default=os.environ.get("PLAYWRIGHT_CDP_URL", "http://127.0.0.1:9222"))
    args = p.parse_args()

    seqs = [s.strip() for s in args.seq.split(",") if s.strip()]
    zips = [args.import_dir / f"DE_52457320260707_{s}.zip" for s in seqs]
    for z in zips:
        if not z.exists():
            raise SystemExit(f"Missing {z}")

    results = []
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(args.cdp)
        context = browser.contexts[0]
        page = next((pg for pg in context.pages if IMPORT_URL_FRAGMENT in pg.url), context.pages[0])
        if IMPORT_URL_FRAGMENT not in page.url:
            page.goto(f"https://chw.sams.edu.hk{IMPORT_URL_FRAGMENT}")
            time.sleep(3)
        for z in zips:
            print(f"Importing {z.name}...")
            results.append(import_zip(page, z))
            print(results[-1])

    out = args.import_dir.parent / "_cdp_exec" / "import_results.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
