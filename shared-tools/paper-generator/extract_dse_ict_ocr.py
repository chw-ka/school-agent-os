#!/usr/bin/env python3
"""Extract HKDSE ICT terminology / phrasing from cached question-bank OCR.

Run once:
  python shared-tools/pdf-engine/build_dse_ict_question_bank.py

Then this script reads cached OCR text (no re-OCR, no token waste).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

_PDF_ENGINE = Path(__file__).resolve().parents[1] / "pdf-engine"
if str(_PDF_ENGINE) not in sys.path:
    sys.path.insert(0, str(_PDF_ENGINE))

from dse_ict_ocr import load_or_ocr  # noqa: E402
from dse_ict_question_bank import collect_bank_text  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
DEFAULT_ROOT = REPO / "Subjects/DSE-ICT/past-papers"
DEFAULT_BANK = REPO / "Subjects/DSE-ICT/question-bank"
DEFAULT_YEARS = [2019, 2020, 2021, 2022, 2023]
DEFAULT_SLUGS = [
    "Paper1_MultipleChoice",
    "Paper2A_Database",
    "Paper2B_DataCommunicationsNetworking",
]


def ocr_collect_live(root: Path, bank: Path, years: list[int], slugs: list[str]) -> str:
    chunks: list[str] = []
    for year in years:
        label = str(year)
        for slug in slugs:
            pdf = root / label / f"DSE_ICT_{label}_{slug}.pdf"
            if not pdf.exists():
                continue
            cache = bank / label / slug / "ocr.txt"
            text = load_or_ocr(pdf, cache, slug=slug)
            if len(text.strip()) > 50:
                chunks.append(text)
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
    ap.add_argument("--bank", type=Path, default=DEFAULT_BANK)
    ap.add_argument("--years", type=int, nargs="+", default=DEFAULT_YEARS)
    ap.add_argument("--slugs", nargs="+", default=DEFAULT_SLUGS)
    ap.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).parent / "dse_ict_ocr_extract.json",
    )
    ap.add_argument("--raw", type=Path, help="Optional path to write raw OCR text")
    ap.add_argument("--force-ocr", action="store_true", help="Ignore question-bank cache")
    args = ap.parse_args(argv)

    year_labels = [str(y) for y in args.years]
    if args.force_ocr:
        text = ocr_collect_live(
            args.root.expanduser().resolve(),
            args.bank.expanduser().resolve(),
            args.years,
            args.slugs,
        )
    else:
        text = collect_bank_text(year_labels, args.slugs, bank_root=args.bank)
        if len(text.strip()) < 100:
            print("Question bank cache empty — run build_dse_ict_question_bank.py first.")
            print("Falling back to live OCR...")
            text = ocr_collect_live(
                args.root.expanduser().resolve(),
                args.bank.expanduser().resolve(),
                args.years,
                args.slugs,
            )

    if args.raw:
        args.raw.write_text(text, encoding="utf-8")
    out = {
        "source_years": args.years,
        "source_slugs": args.slugs,
        **extract_patterns(text),
    }
    args.out.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {args.out} ({out['char_count']} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
