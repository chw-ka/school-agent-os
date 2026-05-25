#!/usr/bin/env python3
"""Extract DSE ICT style patterns from question-bank (no full stems).

Reads structured bank JSON, aggregates command verbs, terminology, scenario frames,
subpart templates, and MCQ distractor patterns by concept. Output is used for
generate-from-blueprint (Phase 1 side product).

Example:
  .venv/bin/python shared-tools/paper-generator/extract_style_patterns.py
  .venv/bin/python shared-tools/paper-generator/extract_style_patterns.py \\
    --years 2021 2022 2023 2024 2025 --out Subjects/DSE-ICT/question-bank/style_patterns.json
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_BANK = _REPO / "Subjects/DSE-ICT/question-bank"
_DEFAULT_OUT = _DEFAULT_BANK / "style_patterns.json"
_DEFAULT_CURRICULUM = _DEFAULT_BANK / "curriculum_concepts.json"
_STYLE_GUIDE = Path(__file__).resolve().parent / "dse_ict_style_guide.json"

_DEFAULT_YEARS = ("2019", "2021", "2022", "2023", "2024", "2025", "2026")
_WRITTEN_SLUGS_B = frozenset({"Paper1B_CompulsoryStructured"})
_WRITTEN_SLUGS_C = frozenset(
    {"Paper2A_Database", "Paper2D_SoftwareDevelopment", "Paper2_Elective"}
)
_DEFAULT_SLUGS = (
    "Paper1_MultipleChoice",
    "Paper1A_MultipleChoice",
    "Paper1B_CompulsoryStructured",
    "Paper2A_Database",
    "Paper2D_SoftwareDevelopment",
    "Paper2_Elective",
)

_SKIP_SLUGS = frozenset({"MarkingScheme", "PerformanceReport"})

# Leading question phrasing (DSE ICT)
_COMMAND_VERB_RE = re.compile(
    r"^(?:"
    r"下列哪[一項些句關於]|下列哪項|下列哪些|下列何者|"
    r"以下哪[一項些]|以下算法的|下列算法的|"
    r"比較[^，。]{0,24}，下列|"
    r"為什麼|解釋|描述|指出|列出|說明|舉出|完成|寫出|繪製|設計|建議|討論|評論|"
    r"考慮以下|細看以下|參考以下|在以下|根據以下|"
    r"除了[^，。]{0,30}，描述|"
    r"測試下列|若使用|當使用"
    r")[^\n]{0,72}"
)

_SUBPART_LEAD_RE = re.compile(
    r"^(?:在\s*)?[A-Z]{1,3}\d+(?::[A-Z]+\d+)?\s*"
    r"(?:輸入|輸入公式|寫出|完成|描述|指出|列出|解釋|除了)[^\n]{0,88}"
)

_SCENARIO_HINT_RE = re.compile(
    r"(?:某|一間|一家|一所|老師|學生|公司|商店|戲院|網店|圖書館|醫院|學校|"
    r"超級市場|餐廳|銀行|機場|博物館|社區中心|活動|系統|表格|數據庫)"
)

_CELL_RE = re.compile(r"\b[A-Z]{1,3}\d+(?::[A-Z]+\d+)?\b")
_YEAR_RE = re.compile(r"\b20[12]\d\b")
_NUM_RE = re.compile(r"\b\d+(?:\.\d+)?\b")
_QUOTED_RE = re.compile(r'"[^"]{1,40}"|`[^`]{1,80}`')
_NAME_RE = re.compile(
    r"\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+|Wong|Chan|Lee|Lau|Cheung|Ng)\b"
)
_IP_RE = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b")
_TABLE_RE = re.compile(r"\b[A-Z][A-Z0-9_]{3,}\b")
_TABLE_WORD_SKIP = frozenset({
    "SUMIF", "COUNTIF", "COUNTIFS", "VLOOKUP", "XLOOKUP", "SELECT", "INSERT",
    "UPDATE", "DELETE", "CREATE", "WHERE", "FROM", "JOIN", "GROUP", "HAVING",
    "INNER", "OUTER", "LEFT", "RIGHT", "DISTINCT", "ORDER", "TABLE", "VIEW",
    "INDEX", "COMMIT", "ROLLBACK", "OUTPUT", "INPUT", "WHILE", "ENDIF",
})
_SQL_SNIP_RE = re.compile(
    r"\b(?:SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|COMMIT|ROLLBACK)\b"
    r"[^;\n]{0,100}",
    re.IGNORECASE,
)
_JSON_BLOCK_RE = re.compile(r"\{[^{}]*\}", re.DOTALL)
_COMBO_OPT_RE = re.compile(
    r"只有\s*[（(]?\s*[123][^A-D\n]{0,40}|"
    r"[（(][123][）)]、?[（(][123][）)]\s*和\s*[（(][123][）)]|"
    r"[（(]1[）)]、[（(]2[）)]\s*和\s*[（(]3[）)]|"
    r"皆是|全部"
)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_keyword_terminology(curriculum_path: Path) -> list[str]:
    if not curriculum_path.exists():
        return []
    data = _load_json(curriculum_path)
    terms: set[str] = set()
    for row in data.get("keyword_concepts", []):
        for kw in row.get("keywords", []):
            if len(kw) >= 2:
                terms.add(kw)
        for c in row.get("concepts", []):
            if len(c) >= 2:
                terms.add(c)
    return sorted(terms, key=len, reverse=True)


def _strip_json_blocks(text: str) -> str:
    return _JSON_BLOCK_RE.sub("", text).strip()


def redact_for_pattern(text: str) -> str:
    """Generalize stem/subpart text — placeholders only, no exam-specific literals."""
    t = _strip_json_blocks(text)
    t = re.sub(r"\s+", " ", t).strip()
    if not t:
        return ""
    def _table_repl(m: re.Match[str]) -> str:
        w = m.group(0)
        if w in _TABLE_WORD_SKIP or w.endswith("IF") or w.endswith("IFS"):
            return w
        return "{TABLE}"

    # TABLE before {YEAR}-style placeholders so "YEAR" inside braces is not matched
    t = _TABLE_RE.sub(_table_repl, t)
    t = _IP_RE.sub("{IP}", t)
    t = _SQL_SNIP_RE.sub("{SQL}", t)
    t = _QUOTED_RE.sub('"{STR}"', t)
    t = _CELL_RE.sub("{CELL}", t)
    t = _YEAR_RE.sub("{YEAR}", t)
    t = _NAME_RE.sub("{NAME}", t)
    t = _NUM_RE.sub("{N}", t)
    t = re.sub(r"\{\{+", "{", t)
    t = re.sub(r"\}\}+", "}", t)
    return t[:200].strip()


def extract_command_verb(stem: str) -> str | None:
    line = stem.strip().split("\n")[0].strip()
    m = _COMMAND_VERB_RE.match(line)
    if m:
        return redact_for_pattern(m.group(0))
    m2 = _SUBPART_LEAD_RE.match(line)
    if m2:
        return redact_for_pattern(m2.group(0))
    for prefix in ("寫出", "列出", "描述", "指出", "解釋", "完成", "繪製", "設計"):
        if line.startswith(prefix):
            return redact_for_pattern(line[: min(80, len(line))])
    return None


def infer_question_type(item: dict, paper_slug: str) -> str:
    section = (item.get("section") or "").lower()
    if section == "mcq" or "MultipleChoice" in paper_slug:
        return "mcq"
    details = item.get("answer_details") or {}
    atype = (details.get("type") or item.get("question_type") or "").lower()
    text = (item.get("stem") or item.get("text") or "").lower()
    if "fill_in" in atype or "fill_in" in text:
        return "fill"
    if "matching" in atype:
        return "matching"
    if "true_false" in atype or "tf" in atype:
        return "tf"
    if any(k in text for k in ("erd", "實體關係", "實體關係圖")):
        return "erd"
    if any(k in text for k in ("select ", "insert ", "update ", "delete ", "create table", "sql")):
        return "sql"
    if "algorithm" in atype or "偽代碼" in text or "流程圖" in text:
        return "algorithm"
    marks = float(item.get("marks") or 0)
    if marks <= 3:
        return "short"
    if marks >= 6:
        return "long"
    return "structured"


def extract_scenario_frame(stem: str) -> str | None:
    line = stem.strip().split("\n")[0].strip()
    if len(line) < 14:
        return None
    if not _SCENARIO_HINT_RE.search(line) and "？" not in line and "?" not in line:
        return None
    red = redact_for_pattern(line)
    if len(red) < 12 or red.count("{") > 8:
        return None
    return red


def extract_subpart_template(item: dict) -> str | None:
    number = str(item.get("number") or "")
    if not re.search(r"\([a-z]\)", number, re.I):
        return None
    stem = (item.get("stem") or item.get("text") or "").strip()
    first = stem.split("\n")[0].strip()
    red = redact_for_pattern(first)
    if len(red) < 10:
        return None
    if "_Q(" in red or re.search(r"Sheet\d+_Q", red, re.I):
        return None
    if not re.search(r"(寫出|列出|描述|指出|解釋|完成|繪製|設計|建議|比較|說明|估算|簡述)", red):
        return None
    label = re.sub(r"\d+", "", number).strip() or number
    return f"{label} {red}"[:120]


def extract_mcq_distractor_patterns(item: dict) -> list[str]:
    opts = item.get("options")
    if not isinstance(opts, dict):
        return []
    patterns: list[str] = []
    for letter in ("A", "B", "C", "D"):
        raw = str(opts.get(letter) or "").strip()
        if not raw:
            continue
        red = redact_for_pattern(raw)
        if _COMBO_OPT_RE.search(raw) or raw.startswith("只有"):
            patterns.append(red)
        elif len(red) <= 48 and "{" in red:
            patterns.append(red)
    combo = "\n".join(str(opts.get(k) or "") for k in "ABCD")
    for m in _COMBO_OPT_RE.findall(combo):
        patterns.append(redact_for_pattern(m))
    return patterns


def extract_terminology(text: str, keywords: list[str]) -> list[str]:
    found: list[str] = []
    for kw in keywords:
        if kw in text:
            found.append(kw)
    return found


def iter_bank_items(
    bank_root: Path,
    years: tuple[str, ...],
    slugs: tuple[str, ...],
) -> tuple[list[dict], dict[str, Any]]:
    rows: list[dict] = []
    meta_files: list[str] = []
    for year in years:
        year_dir = bank_root / year
        if not year_dir.is_dir():
            continue
        for slug_dir in sorted(year_dir.iterdir()):
            if not slug_dir.is_dir():
                continue
            slug = slug_dir.name
            if slug in _SKIP_SLUGS:
                continue
            if slugs and slug not in slugs:
                continue
            qpath = slug_dir / "questions.json"
            if not qpath.exists():
                continue
            data = _load_json(qpath)
            meta_files.append(str(qpath.relative_to(_REPO)))
            for it in data.get("items", []):
                rows.append(
                    {
                        "item": it,
                        "year": year,
                        "slug": slug,
                        "paper_label": (data.get("meta") or {}).get("paper_label", slug),
                    }
                )
    return rows, {"question_files": meta_files}


def _top_counter_items(counter: Counter, limit: int) -> list[dict[str, Any]]:
    return [{"text": text, "count": count} for text, count in counter.most_common(limit)]


def _written_bucket_factory() -> dict[str, Any]:
    return {
        "item_count": 0,
        "question_types": Counter(),
        "command_verbs": Counter(),
        "terminology": Counter(),
        "scenario_frames": Counter(),
        "subpart_templates": Counter(),
        "marks": Counter(),
        "years": Counter(),
        "paper_slugs": Counter(),
    }


def _concept_bucket_factory() -> dict[str, Any]:
    bucket = _written_bucket_factory()
    bucket["distractor_patterns"] = Counter()
    return bucket


def _serialize_written_bucket(bucket: dict[str, Any], *, limit: int) -> dict[str, Any]:
    return {
        "item_count": bucket["item_count"],
        "question_types": dict(bucket["question_types"].most_common()),
        "command_verbs": _top_counter_items(bucket["command_verbs"], limit),
        "terminology": _top_counter_items(bucket["terminology"], limit),
        "scenario_frames": _top_counter_items(bucket["scenario_frames"], limit),
        "subpart_templates": _top_counter_items(bucket["subpart_templates"], limit),
        "marks_distribution": dict(bucket["marks"].most_common()),
        "years": dict(bucket["years"].most_common()),
        "paper_slugs": dict(bucket["paper_slugs"].most_common()),
    }


def _feed_written_bucket(
    bucket: dict[str, Any],
    *,
    row: dict,
    it: dict,
    stem: str,
    qtype: str,
    verb: str | None,
    terms: list[str],
    scenario: str | None,
    sub_t: str | None,
    marks_key: str,
) -> None:
    bucket["item_count"] += 1
    bucket["question_types"][qtype] += 1
    bucket["years"][row["year"]] += 1
    bucket["paper_slugs"][row["slug"]] += 1
    if marks_key:
        bucket["marks"][marks_key] += 1
    if verb:
        bucket["command_verbs"][verb] += 1
    for t in terms:
        bucket["terminology"][t] += 1
    if scenario:
        bucket["scenario_frames"][scenario] += 1
    if sub_t:
        bucket["subpart_templates"][sub_t] += 1


def build_style_patterns(
    bank_root: Path,
    curriculum_path: Path,
    years: tuple[str, ...],
    slugs: tuple[str, ...],
    *,
    per_concept_limit: int = 20,
) -> dict[str, Any]:
    keywords = _load_keyword_terminology(curriculum_path)
    rows, scan_meta = iter_bank_items(bank_root, years, slugs)

    global_verbs: Counter = Counter()
    global_terms: Counter = Counter()
    global_scenarios: Counter = Counter()
    global_distractors: Counter = Counter()
    global_qtypes: Counter = Counter()

    by_concept: dict[str, dict[str, Any]] = defaultdict(_concept_bucket_factory)
    written_b_concept: dict[str, dict[str, Any]] = defaultdict(_written_bucket_factory)
    written_c_concept: dict[str, dict[str, Any]] = defaultdict(_written_bucket_factory)
    written_b_unit: dict[str, dict[str, Any]] = defaultdict(_written_bucket_factory)
    written_c_unit: dict[str, dict[str, Any]] = defaultdict(_written_bucket_factory)

    for row in rows:
        it = row["item"]
        concepts = [str(c) for c in (it.get("concepts") or []) if c]
        if not concepts:
            concepts = ["(untagged)"]

        stem = (it.get("stem") or it.get("text") or "").strip()
        if not stem:
            continue

        qtype = infer_question_type(it, row["slug"])
        global_qtypes[qtype] += 1

        verb = extract_command_verb(stem)
        if verb:
            global_verbs[verb] += 1

        terms = extract_terminology(stem, keywords)
        for t in terms:
            global_terms[t] += 1

        scenario = extract_scenario_frame(stem)
        if scenario:
            global_scenarios[scenario] += 1

        sub_t = extract_subpart_template(it)
        distractors = extract_mcq_distractor_patterns(it) if qtype == "mcq" else []
        for d in distractors:
            global_distractors[d] += 1

        marks_raw = it.get("marks")
        if marks_raw is None:
            marks_key = ""
        elif isinstance(marks_raw, float) and marks_raw == int(marks_raw):
            marks_key = str(int(marks_raw))
        else:
            marks_key = str(marks_raw)

        for concept in concepts:
            bucket = by_concept[concept]
            bucket["item_count"] += 1
            bucket["question_types"][qtype] += 1
            bucket["years"][row["year"]] += 1
            bucket["paper_slugs"][row["slug"]] += 1
            if marks_key:
                bucket["marks"][marks_key] += 1
            if verb:
                bucket["command_verbs"][verb] += 1
            for t in terms:
                bucket["terminology"][t] += 1
            if scenario:
                bucket["scenario_frames"][scenario] += 1
            if sub_t:
                bucket["subpart_templates"][sub_t] += 1
            for d in distractors:
                bucket["distractor_patterns"][d] += 1

        slug = row["slug"]
        unit = str(it.get("curriculum_unit") or "(untagged)").strip()
        feed_kw = dict(
            row=row,
            it=it,
            stem=stem,
            qtype=qtype,
            verb=verb,
            terms=terms,
            scenario=scenario,
            sub_t=sub_t,
            marks_key=marks_key,
        )
        if slug in _WRITTEN_SLUGS_B:
            ub = written_b_unit[unit]
            _feed_written_bucket(ub, **feed_kw)
            for concept in concepts:
                _feed_written_bucket(written_b_concept[concept], **feed_kw)
        elif slug in _WRITTEN_SLUGS_C:
            uc = written_c_unit[unit]
            _feed_written_bucket(uc, **feed_kw)
            for concept in concepts:
                _feed_written_bucket(written_c_concept[concept], **feed_kw)

    # Merge static style guide hints
    guide_verbs: list[str] = []
    if _STYLE_GUIDE.exists():
        guide = _load_json(_STYLE_GUIDE)
        guide_verbs = list(guide.get("mcq_stem_templates") or [])
        for verbs in (guide.get("structured_question_verbs") or {}).values():
            if isinstance(verbs, list):
                guide_verbs.extend(verbs)

    concepts_out: dict[str, Any] = {}
    for concept, bucket in sorted(by_concept.items(), key=lambda x: (-x[1]["item_count"], x[0])):
        concepts_out[concept] = {
            "item_count": bucket["item_count"],
            "question_types": dict(bucket["question_types"].most_common()),
            "command_verbs": _top_counter_items(bucket["command_verbs"], per_concept_limit),
            "terminology": _top_counter_items(bucket["terminology"], per_concept_limit),
            "scenario_frames": _top_counter_items(bucket["scenario_frames"], per_concept_limit),
            "subpart_templates": _top_counter_items(bucket["subpart_templates"], per_concept_limit),
            "distractor_patterns": _top_counter_items(bucket["distractor_patterns"], 12),
            "marks_distribution": dict(bucket["marks"].most_common()),
            "years": dict(bucket["years"].most_common()),
            "paper_slugs": dict(bucket["paper_slugs"].most_common()),
        }

    def _written_section_out(
        by_concept_map: dict[str, dict[str, Any]],
        by_unit_map: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        return {
            "by_concept": {
                k: _serialize_written_bucket(v, limit=per_concept_limit)
                for k, v in sorted(
                    by_concept_map.items(), key=lambda x: (-x[1]["item_count"], x[0])
                )
            },
            "by_curriculum_unit": {
                k: _serialize_written_bucket(v, limit=per_concept_limit)
                for k, v in sorted(
                    by_unit_map.items(), key=lambda x: (-x[1]["item_count"], x[0])
                )
            },
        }

    written_out = {
        "section_b": _written_section_out(written_b_concept, written_b_unit),
        "section_c": _written_section_out(written_c_concept, written_c_unit),
        "usage": (
            "乙部只含 Paper1B；丙部只含 Paper2A/2D/2 Elective。"
            "用 by_concept 揀問法形狀（已 redact），generate 時填新情境／數字，唔抄 stem。"
        ),
    }

    return {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": str(bank_root.relative_to(_REPO)),
        "curriculum": str(curriculum_path.relative_to(_REPO)),
        "style_guide": str(_STYLE_GUIDE.relative_to(_REPO)),
        "years": list(years),
        "paper_slugs": list(slugs),
        "stats": {
            "items_scanned": len(rows),
            "concepts": len(concepts_out),
            "question_files": len(scan_meta["question_files"]),
        },
        "scan": scan_meta,
        "global": {
            "question_types": dict(global_qtypes.most_common()),
            "command_verbs": _top_counter_items(global_verbs, 40),
            "terminology": _top_counter_items(global_terms, 60),
            "scenario_frames": _top_counter_items(global_scenarios, 30),
            "distractor_patterns": _top_counter_items(global_distractors, 25),
            "style_guide_stem_templates": guide_verbs[:30],
        },
        "by_concept": concepts_out,
        "written": written_out,
        "notes": (
            "Patterns are redacted (placeholders). Do not use as exam stems verbatim. "
            "Use for generate-from-blueprint: verbs, terminology, scenario frames, subpart shapes. "
            "Written sections: see `written.section_b` / `written.section_c` by_concept and by_curriculum_unit."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bank", type=Path, default=_DEFAULT_BANK)
    ap.add_argument("--curriculum", type=Path, default=_DEFAULT_CURRICULUM)
    ap.add_argument("--years", nargs="+", default=list(_DEFAULT_YEARS))
    ap.add_argument("--slugs", nargs="*", default=list(_DEFAULT_SLUGS))
    ap.add_argument("--out", type=Path, default=_DEFAULT_OUT)
    ap.add_argument("--per-concept-limit", type=int, default=20)
    ap.add_argument("--dry-run", action="store_true", help="Print stats only, do not write")
    args = ap.parse_args(argv)

    bank = args.bank.expanduser().resolve()
    years = tuple(str(y) for y in args.years)
    slugs = tuple(args.slugs) if args.slugs else _DEFAULT_SLUGS

    payload = build_style_patterns(
        bank,
        args.curriculum.expanduser().resolve(),
        years,
        slugs,
        per_concept_limit=args.per_concept_limit,
    )

    print(
        f"Scanned {payload['stats']['items_scanned']} items, "
        f"{payload['stats']['concepts']} concepts, "
        f"{payload['stats']['question_files']} question files"
    )

    if args.dry_run:
        return 0

    out = args.out.expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
