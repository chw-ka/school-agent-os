"""Parse OCR/text from HKDSE ICT papers into structured question records."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

_COMPARE = Path(__file__).resolve().parents[1] / "question-quality-check"
if str(_COMPARE) not in sys.path:
    sys.path.insert(0, str(_COMPARE))

from exam_spec import build_spec, make_item  # noqa: E402
from quality_lib import extract_mcq_stems, extract_written_units, is_option_line  # noqa: E402


def text_to_lines(text: str) -> list[str]:
    lines: list[str] = []
    for raw in text.splitlines():
        t = raw.strip()
        if t:
            lines.append(t)
    return lines


def _is_option_line_ocr(t: str) -> bool:
    if is_option_line(t):
        return True
    s = t.lstrip()
    return bool(re.match(r"^[ABCD][\.\)、\s]", s))


def parse_mcq_questions(lines: list[str], *, paper_id: str) -> list[dict[str, Any]]:
    """Extract MCQ items; fall back to OCR-tolerant scan if standard parser finds none."""
    stems = extract_mcq_stems(lines)
    if not stems:
        stems = _parse_mcq_ocr_fallback(lines)

    items: list[dict[str, Any]] = []
    for m in stems:
        opts = _split_options(m.get("full") or m["stem"])
        qn = m["index"]
        items.append(
            {
                "id": f"{paper_id}-Q{qn:02d}",
                "type": "mcq",
                "number": qn,
                "section": "甲部",
                "stem": m["stem"],
                "options": opts,
                "marks": 1,
                "text": m.get("full") or m["stem"],
            }
        )
    return items


def _split_options(full: str) -> dict[str, str]:
    opts: dict[str, str] = {}
    for line in full.splitlines():
        s = line.lstrip()
        m = re.match(r"^([ABCD])[\.\)、]\s*(.*)$", s)
        if m:
            opts[m.group(1)] = m.group(2).strip()
    return opts


def _parse_mcq_ocr_fallback(lines: list[str]) -> list[dict]:
    out: list[dict] = []
    i = 0
    qn = 0
    while i < len(lines):
        if "乙部" in lines[i]:
            break
        if any(x in lines[i] for x in ("甲部", "多項選擇", "請選擇")):
            i += 1
            continue
        if _is_option_line_ocr(lines[i]):
            i += 1
            continue
        parts: list[str] = []
        while i < len(lines) and not _is_option_line_ocr(lines[i]) and "乙部" not in lines[i]:
            if lines[i] and "甲部" not in lines[i]:
                parts.append(lines[i])
            i += 1
        opts: list[str] = []
        while i < len(lines) and _is_option_line_ocr(lines[i]):
            opts.append(lines[i])
            i += 1
        if parts and opts:
            qn += 1
            stem = "\n".join(parts)
            out.append({"index": qn, "stem": stem, "full": "\n".join(parts + opts)})
    return out


def _infer_written_type(text: str, section: str) -> str:
    if "配對" in text or "配對題" in section:
        return "matching"
    if "是非" in text or "對或錯" in text:
        return "true_false"
    if "填充" in text or "字庫" in text or "空格" in text:
        return "fill_in"
    if re.search(r"\([a-z]\)", text, re.I) and len(text) > 120:
        return "structured"
    if section == "丙部" or "論述" in text:
        return "long_answer"
    return "short_answer"


def parse_written_questions(lines: list[str], *, paper_id: str) -> list[dict[str, Any]]:
    units = extract_written_units(lines)
    items: list[dict[str, Any]] = []
    for u in units:
        sec = u["section"]
        qtype = _infer_written_type(u["text"], sec)
        sec_key = "乙" if "乙" in sec else "丙" if "丙" in sec else sec
        items.append(
            {
                "id": f"{paper_id}-{sec_key}{u['index']:02d}",
                "type": qtype,
                "number": u["index"],
                "section": sec,
                "label": u.get("label") or "",
                "text": u["text"],
                "marks": _guess_marks(u["text"]),
            }
        )
    return items


def _guess_marks(text: str) -> float | None:
    nums = [int(x) for x in re.findall(r"[\(（](\d+)\s*分", text)]
    if nums:
        return float(sum(nums))
    m = re.search(r"共\s*(\d+)\s*分", text)
    return float(m.group(1)) if m else None


def parse_mcq_answers(text: str, *, paper_id: str) -> dict[int, str]:
    """Parse MCQ answer key lines from marking scheme OCR."""
    answers: dict[int, str] = {}
    for line in text.splitlines():
        m = re.match(r"^(\d{1,2})\s+([ABCD])\b", line.strip())
        if m:
            answers[int(m.group(1))] = m.group(2)
            continue
        m = re.match(r"^([ABCD])\s*$", line.strip())
        if m and len(answers) < 40:
            answers[len(answers) + 1] = m.group(1)
    # Space-separated keys: DBBCB CBCBB ...
    for line in text.splitlines():
        if not re.search(r"[ABCD]{5,}", line):
            continue
        letters = re.findall(r"[ABCD]", line.upper())
        if len(letters) >= 20:
            for i, ch in enumerate(letters[:40], start=1):
                answers.setdefault(i, ch)
    return answers


def build_paper_spec(
    *,
    year_label: str,
    slug: str,
    paper_label: str,
    source_pdf: Path,
    questions: list[dict[str, Any]],
    ocr_path: Path | None = None,
    answers: dict[int, str] | None = None,
) -> dict[str, Any]:
    paper_id = f"{year_label}-{slug}"
    meta: dict[str, Any] = {
        "source": "dse-ict-question-bank",
        "year_label": year_label,
        "paper_slug": slug,
        "paper_label": paper_label,
        "source_pdf": str(source_pdf).replace("\\", "/"),
        "question_count": len(questions),
    }
    if ocr_path:
        meta["ocr_cache"] = str(ocr_path).replace("\\", "/")

    spec_items: list[dict] = []
    for q in questions:
        section = q["type"]
        if q["type"] == "mcq":
            row = make_item(
                q["id"],
                "mcq",
                q["text"],
                marks=q.get("marks"),
                number=q["number"],
                stem=q.get("stem"),
                options=q.get("options"),
            )
            if answers and q["number"] in answers:
                row["answer"] = answers[q["number"]]
        else:
            row = make_item(
                q["id"],
                q["type"],
                q["text"],
                marks=q.get("marks"),
                number=q["number"],
                section_label=q.get("section"),
                label=q.get("label"),
            )
        spec_items.append(row)

    spec = build_spec(meta, spec_items)
    spec["paper"] = {
        "id": paper_id,
        "questions": questions,
    }
    return spec
