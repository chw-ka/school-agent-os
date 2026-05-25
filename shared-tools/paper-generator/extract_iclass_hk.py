#!/usr/bin/env python3
"""Extract iClass HK question banks (DOCX) and teaching slides (PPTX) to JSON.

Source files live under Subjects/DSE-ICT/iclass-hk/. Output is written to
Subjects/DSE-ICT/iclass-hk/json/ plus an aggregated depth_profile.json for
F5 / Core D exam calibration (not DSE past-paper bank copy).

Example:
  .venv/bin/python shared-tools/paper-generator/extract_iclass_hk.py
  .venv/bin/python shared-tools/paper-generator/extract_iclass_hk.py --out Subjects/DSE-ICT/iclass-hk/json
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET
from zipfile import ZipFile

_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SRC = _REPO / "Subjects/DSE-ICT/iclass-hk"
_DEFAULT_OUT = _DEFAULT_SRC / "json"

_W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
_A_NS = "{http://schemas.openxmlformats.org/drawingml/2006/main}"

_SECTION_ALIASES: dict[str, str] = {
    "選擇題": "mcq",
    "multiple-choice questions": "mcq",
    "multiple choice questions": "mcq",
    "mc": "mcq",
    "mcq": "mcq",
    "短答題": "short_answer",
    "short questions": "short_answer",
    "short question": "short_answer",
    "長答題": "long_answer",
    "long questions": "long_answer",
    "long question": "long_answer",
}
_SECTION_HEADERS = frozenset(_SECTION_ALIASES.keys())

_ID_RE = re.compile(
    r"^(SSICT[A-Z0-9]+_\w+),\s*(\d+(?:\.\d+)?)(?:,\s*(\d{4}))?\s*$",
    re.I,
)
_ANSWER_INLINE_RE = re.compile(
    r"^\[--(?:答案|Answer)：\s*(.+?)--\]\s*$",
    re.I,
)
_ANSWER_OPEN_RE = re.compile(r"^\[--(?:答案|Answer)：\s*$", re.I)
_ANSWER_CLOSE_RE = re.compile(r"^--\]\s*$")
_QNUM_RE = re.compile(r"^\d+\.\s*$")
_PART_LABEL_RE = re.compile(r"^\(([a-z]+(?:\([ivx]+\))?)\)\s*$", re.I)
_MARKS_RE = re.compile(r"（\s*(\d+(?:\.\d+)?)\s*分\s*）")
_OPTION_RE = re.compile(r"^([A-D])\.\s*$")
_BLANK_LINE_RE = re.compile(r"^_+\s*$")

# Optional per-file overrides (auto-inferred from filename when absent)
_SOURCE_META: dict[str, dict[str, Any]] = {}

_UNIT_SCOPE: dict[str, tuple[str, str, str]] = {
    "CoreA": ("A", "Core-A", "mcq_core_a"),
    "CoreB": ("B", "Core-B", "mcq_core_b"),
    "CoreD": ("D", "Core-D", "mcq_core_d"),
    "ElecA": ("EA", "EA", "elective_db"),
    "ElecC": ("EC", "EC", "elective_sd"),
}

_PPTX_SERIES: dict[str, tuple[str, str]] = {
    "HD1": ("D-d", "Core-D"),
    "HD2": ("D-d", "Core-D"),
    "HA1": ("A-a", "Core-A"),
    "EB": ("B-a", "Core-B"),
    "EA1": ("EA-a", "EA"),
    "EELECA": ("EA-a", "EA"),
    "EELECC": ("EC-a", "EC"),
}


def _slugify(text: str) -> str:
    s = re.sub(r"[^\w\u4e00-\u9fff]+", "_", text.strip())
    return re.sub(r"_+", "_", s).strip("_")[:80]


def infer_qb_meta(filename: str) -> dict[str, Any]:
    if filename in _SOURCE_META:
        return dict(_SOURCE_META[filename])
    stem = Path(filename).stem
    m = re.match(
        r"QB_(?P<family>CoreA|CoreB|CoreD|ElecA|ElecC)(?P<tail>i|\d+)?_(?P<lang>hk|en)_(?P<title>.+)$",
        stem,
        re.I,
    )
    if not m:
        return {
            "slug": _slugify(stem),
            "title": stem,
            "language": "unknown",
            "curriculum_unit": "unknown",
            "f5_scope": None,
        }
    family = m.group("family")
    tail = (m.group("tail") or "").lower()
    lang = m.group("lang").lower()
    title = m.group("title").strip()
    integrated = tail == "i"
    chapter = int(tail) if tail.isdigit() else None
    ca, curriculum_unit, f5_scope = _UNIT_SCOPE[family]
    slug = f"{family}{tail or ''}_{lang}"
    meta: dict[str, Any] = {
        "slug": slug,
        "family": family,
        "chapter": chapter,
        "integrated": integrated,
        "language": lang,
        "title": title,
        "curriculum_unit": curriculum_unit,
        "ca_unit": ca,
        "f5_scope": f5_scope,
        "topic_code": f"{ca}{chapter:02d}" if chapter else f"{ca}99",
    }
    if lang == "hk":
        meta["title_zh"] = title
    else:
        meta["title_en"] = title
    return meta


def infer_pptx_meta(filename: str) -> dict[str, Any]:
    if filename in _SOURCE_META:
        return dict(_SOURCE_META[filename])
    stem = Path(filename).stem
    m = re.match(
        r"^(?P<series>HD\d|HA\d|EB|EA\d|EElecA|EElecC)\s*(?:Ch\s*)?(?P<ch>\d+)?",
        stem,
        re.I,
    )
    series = (m.group("series") if m else stem.split()[0]).upper().replace(" ", "")
    ch = int(m.group("ch")) if m and m.group("ch") else None
    series_key = series
    if series.startswith("EA") and series != "EA1":
        series_key = "EA1"
    unit_code, curriculum_unit = _PPTX_SERIES.get(
        series_key, _PPTX_SERIES.get(series[:3], ("unknown", "unknown"))
    )
    slug = _slugify(f"{series}_Ch{ch or 0}_slides")
    return {
        "slug": slug,
        "series": series,
        "chapter": ch,
        "title": stem,
        "curriculum_unit": unit_code,
        "curriculum_part": curriculum_unit,
        "kind": "slides",
    }


def _section_type_from_line(line: str) -> str | None:
    return _SECTION_ALIASES.get(line.strip().lower())


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def docx_paragraphs(path: Path) -> list[str]:
    with ZipFile(path) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))
    paras: list[str] = []
    for p in root.iter(f"{_W_NS}p"):
        texts: list[str] = []
        for t in p.iter(f"{_W_NS}t"):
            if t.text:
                texts.append(t.text)
            if t.tail:
                texts.append(t.tail)
        line = "".join(texts).strip()
        if line:
            paras.append(line)
    return paras


def pptx_slide_texts(path: Path) -> list[dict[str, Any]]:
    with ZipFile(path) as zf:
        slide_names = sorted(
            n
            for n in zf.namelist()
            if n.startswith("ppt/slides/slide") and n.endswith(".xml")
        )
        slides: list[dict[str, Any]] = []
        for idx, sn in enumerate(slide_names, start=1):
            root = ET.fromstring(zf.read(sn))
            texts: list[str] = []
            for t in root.iter(f"{_A_NS}t"):
                if t.text:
                    texts.append(t.text)
                if t.tail:
                    texts.append(t.tail)
            text = "".join(texts).strip()
            if text:
                slides.append({"slide_index": idx, "slide_part": sn, "text": text})
    return slides


def _split_answer_block(lines: list[str]) -> tuple[str | None, str | None]:
    """Return (mcq_letter, free_text_answer)."""
    body = "\n".join(lines).strip()
    if not body:
        return None, None
    if len(body) == 1 and body.upper() in "ABCD":
        return body.upper(), None
    if re.fullmatch(r"[A-D]", body.splitlines()[0].strip()):
        first = body.splitlines()[0].strip().upper()
        rest = "\n".join(body.splitlines()[1:]).strip()
        return first, rest or None
    return None, body


def _parse_mcq_block(lines: list[str]) -> tuple[str, dict[str, str], str | None, str | None]:
    """Parse MCQ stem, options, answer letter, answer text."""
    stem_lines: list[str] = []
    options: dict[str, str] = {}
    current_opt: str | None = None
    opt_lines: list[str] = []
    pre_option = True

    i = 0
    while i < len(lines):
        line = lines[i]
        m_opt = _OPTION_RE.match(line)
        if m_opt:
            if current_opt and opt_lines:
                options[current_opt] = "\n".join(opt_lines).strip()
            current_opt = m_opt.group(1)
            opt_lines = []
            pre_option = False
            i += 1
            continue
        if pre_option:
            if line != "1." and not _QNUM_RE.match(line):
                stem_lines.append(line)
        elif current_opt:
            if _ANSWER_INLINE_RE.match(line):
                ans_m = _ANSWER_INLINE_RE.match(line)
                letter = (ans_m.group(1) if ans_m else "").strip().upper() or None
                if current_opt and opt_lines:
                    options[current_opt] = "\n".join(opt_lines).strip()
                return "\n".join(stem_lines).strip(), options, letter, None
            if _ANSWER_OPEN_RE.match(line):
                ans_lines: list[str] = []
                i += 1
                while i < len(lines) and not _ANSWER_CLOSE_RE.match(lines[i]):
                    ans_lines.append(lines[i])
                    i += 1
                if current_opt and opt_lines:
                    options[current_opt] = "\n".join(opt_lines).strip()
                letter, text = _split_answer_block(ans_lines)
                return "\n".join(stem_lines).strip(), options, letter, text
            opt_lines.append(line)
        i += 1

    if current_opt and opt_lines:
        options[current_opt] = "\n".join(opt_lines).strip()
    return "\n".join(stem_lines).strip(), options, None, None


def _parse_structured_block(lines: list[str]) -> tuple[str, list[dict[str, Any]], str | None]:
    """Parse short/long answer: stem, parts with marks, model answer text."""
    stem_lines: list[str] = []
    parts: list[dict[str, Any]] = []
    current_part: dict[str, Any] | None = None
    part_lines: list[str] = []
    answer_lines: list[str] | None = None
    in_answer = False

    def flush_part() -> None:
        nonlocal current_part, part_lines
        if current_part is not None:
            current_part["text"] = "\n".join(part_lines).strip()
            parts.append(current_part)
            current_part = None
            part_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]
        if _ANSWER_OPEN_RE.match(line):
            flush_part()
            in_answer = True
            answer_lines = []
            i += 1
            continue
        if in_answer:
            if _ANSWER_CLOSE_RE.match(line):
                in_answer = False
                i += 1
                continue
            if answer_lines is not None:
                answer_lines.append(line)
            i += 1
            continue
        pm = _PART_LABEL_RE.match(line)
        if pm:
            flush_part()
            label = pm.group(1).lower()
            current_part = {"label": label, "marks": None, "text": ""}
            part_lines = []
            i += 1
            if i < len(lines):
                marks_m = _MARKS_RE.search(lines[i])
                if marks_m:
                    current_part["marks"] = float(marks_m.group(1))
                    part_lines.append(lines[i])
                    i += 1
            continue
        if current_part is not None:
            if _BLANK_LINE_RE.match(line):
                i += 1
                continue
            part_lines.append(line)
        elif line != "1." and not _QNUM_RE.match(line):
            stem_lines.append(line)
        i += 1

    flush_part()
    _, answer_text = _split_answer_block(answer_lines or [])
    return "\n".join(stem_lines).strip(), parts, answer_text


def parse_docx_questions(paras: list[str], *, section_type: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    current_section = "mcq"
    i = 0
    while i < len(paras):
        line = paras[i]
        sec_hdr = _section_type_from_line(line)
        if sec_hdr:
            current_section = sec_hdr
            i += 1
            continue
        id_m = _ID_RE.match(line)
        if not id_m:
            i += 1
            continue

        bank_id = id_m.group(1)
        total_marks = float(id_m.group(2))
        year_tag = id_m.group(3)
        i += 1
        block: list[str] = []
        while i < len(paras) and not _ID_RE.match(paras[i]) and not _section_type_from_line(paras[i]):
            block.append(paras[i])
            i += 1

        sec = section_type if section_type != "auto" else current_section
        item: dict[str, Any] = {
            "id": bank_id,
            "bank_code": bank_id,
            "section_type": sec,
            "marks": total_marks,
            "year_tag": year_tag,
        }

        if sec == "mcq":
            stem, options, letter, ans_text = _parse_mcq_block(block)
            item.update(
                {
                    "stem": stem,
                    "options": options,
                    "answer": letter,
                    "answer_text": ans_text,
                    "parts": [],
                }
            )
        else:
            stem, parts, ans_text = _parse_structured_block(block)
            item.update(
                {
                    "stem": stem,
                    "options": {},
                    "answer": None,
                    "answer_text": ans_text,
                    "parts": parts,
                }
            )
        item["text"] = _item_full_text(item)
        items.append(item)
    return items


def _item_full_text(item: dict[str, Any]) -> str:
    chunks = [str(item.get("stem") or "")]
    opts = item.get("options") or {}
    for letter in "ABCD":
        if opts.get(letter):
            chunks.append(f"{letter}. {opts[letter]}")
    for part in item.get("parts") or []:
        chunks.append(f"({part.get('label')}) {part.get('text')}")
    if item.get("answer_text"):
        chunks.append(str(item["answer_text"]))
    return "\n".join(c for c in chunks if c).strip()


def _infer_concepts(item: dict[str, Any], meta: dict[str, Any]) -> list[str]:
    text = (item.get("text") or "").lower()
    concepts: list[str] = []
    family = meta.get("family") or ""
    chapter = meta.get("chapter")
    ca = meta.get("ca_unit") or ""
    if ca and chapter:
        concepts.append(f"{ca}-ch{chapter}")
    elif ca:
        concepts.append(f"{ca}-integrated")

    rules: list[tuple[str, str]] = [
        (r"python|程式|編程|程式碼|program", "Python"),
        (r"for\s|while\s|循環|loop|range\(", "循環"),
        (r"列表|list|索引|index|array", "列表"),
        (r"函數|function|def\s|sub-?program", "函數"),
        (r"除錯|debug|錯誤|語法錯誤|邏輯錯誤|運行時|syntax", "除錯"),
        (r"測試|test case|測試數據|邊界|boundary", "程式測試"),
        (r"算法|偽代碼|流程圖|←|algorithm|pseudocode", "算法"),
        (r"堆疊|stack|佇列|queue", "堆疊"),
        (r"排序|sort|searching|搜尋", "排序"),
        (r"sql|select|insert|update|delete|create table", "SQL"),
        (r"database|資料庫|erd|entity|primary key|foreign key", "數據庫"),
        (r"ram|rom|cpu|hardware|硬件|記憶體|storage", "硬件"),
        (r"software|軟件|作業系統|operating system|driver", "軟件"),
        (r"試算表|spreadsheet|formula|函數", "試算表"),
        (r"多媒體|jpeg|png|bmp|pixel|像素|compression", "多媒體"),
        (r"資訊|information|data|數據|field|record|欄位|記錄", "資訊處理"),
        (r"binary|hex|二進制|十六進制|bit", "進制"),
        (r"network|網絡|protocol|tcp|ip", "網絡"),
        (r"輸入|輸出|input\(|print\(|keyboard|speaker", "輸入輸出"),
        (r"if\s|else|條件|selection", "選擇結構"),
        (r"整數|浮點|字串|布爾|數據類型|integer|string", "數據類型"),
    ]
    for pat, label in rules:
        if re.search(pat, text, re.I):
            if label not in concepts:
                concepts.append(label)
    if family and not any(c.startswith(family[-1]) for c in concepts):
        concepts.insert(0, meta.get("curriculum_unit", family))
    return concepts


def extract_docx(path: Path, out_dir: Path) -> dict[str, Any]:
    fname = path.name
    meta_extra = infer_qb_meta(fname)
    paras = docx_paragraphs(path)
    title_line = paras[0] if paras and len(paras[0]) < 80 else meta_extra.get("title", "")

    items = parse_docx_questions(paras, section_type="auto")
    for it in items:
        it["concepts"] = _infer_concepts(it, meta_extra)
        it["difficulty_tier"] = _difficulty_tier(it)

    payload: dict[str, Any] = {
        "version": 1,
        "meta": {
            "source": "iclass-hk",
            "provider": "iClass HK (SSICT question bank)",
            "source_file": str(path.relative_to(_REPO)).replace("\\", "/"),
            "slug": meta_extra.get("slug", _slugify(path.stem)),
            "title": meta_extra.get("title") or title_line,
            "title_zh": meta_extra.get("title_zh"),
            "title_en": meta_extra.get("title_en"),
            "language": meta_extra.get("language"),
            "family": meta_extra.get("family"),
            "chapter": meta_extra.get("chapter"),
            "integrated": meta_extra.get("integrated", False),
            "topic_code": meta_extra.get("topic_code"),
            "curriculum_unit": meta_extra.get("curriculum_unit"),
            "ca_unit": meta_extra.get("ca_unit"),
            "f5_exam_scope": meta_extra.get("f5_scope"),
            "extracted_at": _utc_now(),
            "item_count": len(items),
            "section_counts": dict(Counter(it["section_type"] for it in items)),
        },
        "items": items,
    }
    out_name = meta_extra.get("slug", _slugify(path.stem)) + ".json"
    out_path = out_dir / out_name
    _write_json(out_path, payload)
    return {"out": str(out_path.relative_to(_REPO)), "meta": payload["meta"], "items": len(items)}


def _difficulty_tier(item: dict[str, Any]) -> str:
    marks = float(item.get("marks") or 1)
    text = item.get("text") or ""
    sec = item.get("section_type")
    if sec == "long_answer" or marks >= 8:
        return "advanced"
    if sec == "short_answer" or marks >= 3:
        return "intermediate"
    if "for " in text and "range" in text:
        return "intermediate"
    if len(text) > 400 or text.count("\n") > 8:
        return "intermediate"
    return "foundation"


def extract_pptx(path: Path, out_dir: Path) -> dict[str, Any]:
    meta_extra = infer_pptx_meta(path.name)
    slides = pptx_slide_texts(path)
    topics: Counter[str] = Counter()
    for slide in slides:
        t = slide["text"]
        if re.search(r"測試站|活動|課本|Activity", t, re.I):
            topics["課本活動"] += 1
        if re.search(r"for |while |range\(", t, re.I):
            topics["循環"] += 1
        if re.search(r"錯誤|除錯|debug|error", t, re.I):
            topics["除錯"] += 1
        if re.search(r"列表|list", t, re.I):
            topics["列表"] += 1
        if re.search(r"堆疊|stack", t, re.I):
            topics["堆疊"] += 1
        if re.search(r"sql|database|SELECT", t, re.I):
            topics["數據庫"] += 1
        if re.search(r"RAM|CPU|hardware|硬件", t, re.I):
            topics["硬件"] += 1

    payload: dict[str, Any] = {
        "version": 1,
        "meta": {
            "source": "iclass-hk",
            "provider": "iClass HK (teaching slides)",
            "source_file": str(path.relative_to(_REPO)).replace("\\", "/"),
            "slug": meta_extra.get("slug", _slugify(path.stem)),
            "title": meta_extra.get("title", path.stem),
            "series": meta_extra.get("series"),
            "chapter": meta_extra.get("chapter"),
            "curriculum_unit": meta_extra.get("curriculum_unit"),
            "curriculum_part": meta_extra.get("curriculum_part"),
            "kind": "slides",
            "extracted_at": _utc_now(),
            "slide_count": len(slides),
            "topic_tags": dict(topics.most_common()),
        },
        "slides": slides,
    }
    out_name = meta_extra.get("slug", _slugify(path.stem)) + ".json"
    out_path = out_dir / out_name
    _write_json(out_path, payload)
    return {"out": str(out_path.relative_to(_REPO)), "meta": payload["meta"], "slides": len(slides)}


def build_depth_profile(sources: list[dict[str, Any]], out_dir: Path) -> Path:
    """Aggregate iClass QB stats for exam depth calibration (all units)."""
    by_unit: dict[str, Any] = defaultdict(
        lambda: {
            "items": 0,
            "section_types": Counter(),
            "marks": Counter(),
            "difficulty": Counter(),
            "concepts": Counter(),
            "sample_stems": [],
            "sources": [],
        }
    )
    all_mcq_stems: list[str] = []
    all_written_stems: list[str] = []
    totals = Counter()

    for entry in sources:
        if entry.get("kind") == "slides":
            continue
        json_path = _REPO / entry["json"]
        if not json_path.exists():
            continue
        data = _load_json(json_path)
        meta = data.get("meta") or {}
        unit = str(meta.get("curriculum_unit") or meta.get("family") or "unknown")
        ch = meta.get("chapter")
        ch_key = f"{unit}-ch{ch}" if ch else f"{unit}-integrated"
        bucket = by_unit[ch_key]
        bucket["sources"].append(entry.get("slug") or entry.get("file"))
        for it in data.get("items", []):
            bucket["items"] += 1
            totals["items"] += 1
            totals[it.get("section_type", "unknown")] += 1
            bucket["section_types"][it.get("section_type")] += 1
            bucket["marks"][str(it.get("marks"))] += 1
            bucket["difficulty"][it.get("difficulty_tier", "foundation")] += 1
            for c in it.get("concepts") or []:
                bucket["concepts"][c] += 1
            stem = (it.get("stem") or "")[:200]
            if it.get("section_type") == "mcq" and len(all_mcq_stems) < 60:
                all_mcq_stems.append(stem)
            elif it.get("section_type") != "mcq" and len(all_written_stems) < 40:
                all_written_stems.append(stem)
            if len(bucket["sample_stems"]) < 5 and stem:
                bucket["sample_stems"].append(stem)

    def _serialize_unit(key: str, b: dict[str, Any]) -> dict[str, Any]:
        return {
            "unit_key": key,
            "item_count": b["items"],
            "section_types": dict(b["section_types"]),
            "marks_distribution": dict(b["marks"]),
            "difficulty_distribution": dict(b["difficulty"]),
            "top_concepts": [c for c, _ in b["concepts"].most_common(12)],
            "sample_stems": b["sample_stems"],
            "source_slugs": b["sources"][:6],
        }

    profile: dict[str, Any] = {
        "version": 2,
        "generated_at": _utc_now(),
        "purpose": (
            "Calibrate S5/F5 ICT exam depth across Core A/B/D and electives (EA/EC). "
            "iClass HK items are school-level benchmarks — match depth by curriculum_unit + concepts."
        ),
        "usage_notes": [
            "Each generated spec item may include depth_references from matching iClass QB JSON.",
            "Do not copy stems verbatim into exams (copyright); use for depth and topic coverage.",
            "Core A/B MCQ: scenario + hardware/software/data organisation; not only definitions.",
            "Core D: code trace, lists, testing/debugging.",
            "EA written: SQL multi-step; EC: Python structures, sorting, files.",
        ],
        "totals": dict(totals),
        "units": [_serialize_unit(k, b) for k, b in sorted(by_unit.items())],
        "chapters": [_serialize_unit(k, b) for k, b in sorted(by_unit.items())],
        "guidance_for_f5_exam": {
            "mcq_core_a": {"prefer_scenario": True, "avoid_trivial_recall": True},
            "mcq_core_b": {"include_hardware_specs": True, "compare_devices": True},
            "mcq_core_d": {
                "min_fraction_intermediate": 0.4,
                "include_code_trace": True,
                "include_list_or_nested_loop": True,
                "avoid_only_definition_recall": True,
            },
            "written_core_b": {"multi_part": True, "marks_per_part": [2, 3, 4]},
            "written_ea": {"sql_completion": True, "multi_table": True},
            "written_ec": {"python_completion": True, "algorithm_or_structure": True},
        },
        "sample_mcq_stems": all_mcq_stems[:20],
        "sample_written_stems": all_written_stems[:15],
    }
    out_path = out_dir.parent / "depth_profile.json"
    _write_json(out_path, profile)
    return out_path


def build_index(sources: list[dict[str, Any]], out_dir: Path) -> None:
    index = {
        "version": 1,
        "generated_at": _utc_now(),
        "root": str(out_dir.relative_to(_REPO)).replace("\\", "/"),
        "source_folder": str(_DEFAULT_SRC.relative_to(_REPO)).replace("\\", "/"),
        "depth_profile": str((out_dir.parent / "depth_profile.json").relative_to(_REPO)).replace(
            "\\", "/"
        ),
        "sources": sources,
    }
    _write_json(out_dir / "index.json", index)


def run(src_dir: Path, out_dir: Path) -> int:
    sources: list[dict[str, Any]] = []
    for docx in sorted(src_dir.glob("QB_*.docx")):
        result = extract_docx(docx, out_dir)
        sources.append(
            {
                "kind": "question_bank",
                "file": docx.name,
                "json": result["out"],
                "items": result["items"],
                "slug": result["meta"]["slug"],
            }
        )
        print(f"  {docx.name}: {result['items']} items → {result['out']}")

    for pptx in sorted(src_dir.glob("*.pptx")):
        result = extract_pptx(pptx, out_dir)
        sources.append(
            {
                "kind": "slides",
                "file": pptx.name,
                "json": result["out"],
                "slides": result["slides"],
                "slug": result["meta"]["slug"],
            }
        )
        print(f"  {pptx.name}: {result['slides']} slides → {result['out']}")

    depth_path = build_depth_profile(sources, out_dir)
    build_index(sources, out_dir)
    print(f"  depth_profile → {depth_path.relative_to(_REPO)}")
    print(f"  index → {(out_dir / 'index.json').relative_to(_REPO)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Extract iClass HK DOCX/PPTX to JSON")
    ap.add_argument("--src", type=Path, default=_DEFAULT_SRC, help="Source folder")
    ap.add_argument("--out", type=Path, default=_DEFAULT_OUT, help="JSON output folder")
    args = ap.parse_args()
    src = args.src.expanduser().resolve()
    out = args.out.expanduser().resolve()
    if not src.is_dir():
        print(f"Missing source dir: {src}")
        return 1
    print(f"Extracting from {src} …")
    return run(src, out)


if __name__ == "__main__":
    raise SystemExit(main())
