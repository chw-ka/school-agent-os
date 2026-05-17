#!/usr/bin/env python3
"""OCR scanned HKDSE ICT past papers and extract terminology / phrasing hints."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

import fitz

DEFAULT_ROOT = Path(__file__).resolve().parents[2] / "Subjects/PastPaper/ICT"
DEFAULT_YEARS = [2019, 2020, 2021, 2022, 2023]
LANG = "chi_tra+eng"


def ocr_page(pdf_path: Path, page_no: int, scale: float = 2.2) -> str:
    doc = fitz.open(pdf_path)
    page = doc[page_no]
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale))
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        img = Path(f.name)
    pix.save(str(img))
    r = subprocess.run(
        ["tesseract", str(img), "stdout", "-l", LANG, "--psm", "6"],
        capture_output=True,
        text=True,
    )
    img.unlink(missing_ok=True)
    return r.stdout if r.returncode == 0 else ""


def collect_text(root: Path, years: list[int], parts: list[str]) -> str:
    chunks: list[str] = []
    for year in years:
        for part in parts:
            p = root / str(year) / part
            if not p.exists():
                continue
            doc = fitz.open(p)
            end = min(doc.page_count, 14 if part == "p1.pdf" else 8)
            for pn in range(2, end):
                t = ocr_page(p, pn)
                if len(t.strip()) > 50:
                    chunks.append(t)
    return "\n".join(chunks)


def extract_patterns(text: str) -> dict:
    term_re = re.compile(
        r"(?:數據|資訊|試算表|處理器|記憶體|快取|編碼|壓縮|驅動|軟件|硬件|作業系統|"
        r"數據庫|SQL|正規化|主鍵|外鍵|偽代碼|算法|有效性檢驗|奇偶檢測|"
        r"樞紐分析|目標搜尋|IPv6|ASCII|Unicode|CPU|RAM|ROM|SSD|HDD|"
        r"二進制|十六進制|補碼|輸入|輸出|處理|儲存|實用程式|應用軟件)"
        r"[\u4e00-\u9fff]{0,8}"
    )
    return {
        "char_count": len(text),
        "terminology_frequency": Counter(term_re.findall(text)).most_common(100),
        "mcq_only_patterns": list(dict.fromkeys(re.findall(r"只有\s*[（(]?\s*[123][^A-D\n]{0,35}", text)))[:30],
        "question_starters": list(
            dict.fromkeys(
                re.findall(
                    r"(?:下列|以下|比較|為什麼|解釋|指出|描述|寫出|完成|考慮|細看|參考)[^\n]{8,90}",
                    text,
                )
            )
        )[:50],
        "english_in_parens": list(dict.fromkeys(re.findall(r"[（(]([A-Za-z][A-Za-z0-9\s\-/\.]{1,35})[）)]", text)))[:80],
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--years", type=int, nargs="+", default=DEFAULT_YEARS)
    ap.add_argument("--parts", nargs="+", default=["p1.pdf", "p2a.pdf", "p2b.pdf"])
    ap.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).parent / "dse_ict_ocr_extract.json",
    )
    ap.add_argument("--raw", type=Path, help="Optional path to write raw OCR text")
    args = ap.parse_args(argv)

    text = collect_text(args.root.expanduser().resolve(), args.years, args.parts)
    if args.raw:
        args.raw.write_text(text, encoding="utf-8")
    out = {
        "source_years": args.years,
        "source_parts": args.parts,
        **extract_patterns(text),
    }
    args.out.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {args.out} ({out['char_count']} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
