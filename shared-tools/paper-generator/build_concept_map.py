#!/usr/bin/env python3
"""Build concept_map.json: C&A Guide tree + question-bank statistics.

Merges curriculum_concepts.json (EDB structure) with bank item counts,
marks distribution, question types, and marking-scheme hints for common mistakes.

Example:
  .venv/bin/python shared-tools/paper-generator/build_concept_map.py
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from extract_style_patterns import infer_question_type, iter_bank_items

_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_BANK = _REPO / "Subjects/DSE-ICT/question-bank"
_DEFAULT_CURRICULUM = _DEFAULT_BANK / "curriculum_concepts.json"
_DEFAULT_STYLE = _DEFAULT_BANK / "style_patterns.json"
_DEFAULT_OUT = _DEFAULT_BANK / "concept_map.json"
_CA_GUIDE = _REPO / "Subjects/DSE-ICT/edb/ICT_C&A Guide_c_final.pdf"

_DEFAULT_YEARS = ("2019", "2021", "2022", "2023", "2024", "2025")
_DEFAULT_SLUGS = (
    "Paper1_MultipleChoice",
    "Paper1A_MultipleChoice",
    "Paper1B_CompulsoryStructured",
    "Paper2A_Database",
    "Paper2D_SoftwareDevelopment",
    "Paper2_Elective",
)
_MARKING_SLUG = "MarkingScheme"

# Pedagogy seeds (topic-level); enriched from marking scheme when found
_TOPIC_MISTAKE_SEEDS: dict[str, list[str]] = {
    "A-b": ["混淆欄位與記錄", "混淆檔案與數據庫表"],
    "A-c": ["混淆二進制與十六進制的位元數", "混淆有損與無損壓縮"],
    "A-d": ["試算表函數參照類型錯誤（相對／絕對）", "SQL 語句缺少 WHERE"],
    "B-a": ["混淆 RAM 與 ROM", "混淆快取與主記憶體"],
    "B-b": ["混淆系統軟件與應用軟件", "混淆編譯程式與解釋程式"],
    "D-b": ["堆疊 top／bottom 方向混淆", "混淆排序與搜尋算法"],
    "D-d": ["混淆語法錯誤與邏輯錯誤", "測試個案未包含邊界值"],
    "EA-a": ["混淆實體完整性與參照完整性", "ERD  cardinality 標示錯誤"],
    "EA-b": ["JOIN 條件遺漏", "混淆 DELETE 與 DROP"],
    "EA-c": ["正規化步驟跳過導致冗餘", "主鍵／外鍵指派錯誤"],
    "EC-a": ["堆疊 push／pop 次序錯誤", "混淆堆疊與佇列"],
}

_MISTAKE_NOTE_RE = re.compile(
    r"(?:混淆|誤以為|常見錯誤|易錯|不要|應避免|錯誤地)[^\n。；]{4,60}|"
    r"[^。\n]{2,30}與[^。\n]{2,30}混淆"
)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _marks_key(marks: Any) -> str:
    if marks is None:
        return ""
    if isinstance(marks, float) and marks == int(marks):
        return str(int(marks))
    return str(marks)


def _counter_dict(c: Counter) -> dict[str, int]:
    return dict(c.most_common())


def _map_concepts_to_topics(curriculum: dict) -> dict[str, set[str]]:
    """concept label → set of topic ids (A-b, EA-c, …)."""
    out: dict[str, set[str]] = defaultdict(set)
    for row in curriculum.get("keyword_concepts", []):
        topic = str(row.get("topic") or "")
        if not topic:
            continue
        for c in row.get("concepts", []):
            out[str(c)].add(topic)
    for concept, unit in (curriculum.get("concept_to_unit") or {}).items():
        if concept not in out:
            # fallback: attach to first topic in unit
            unit_key = str(unit)
            topics = _topics_for_unit(curriculum, unit_key)
            if topics:
                out[concept].add(topics[0])
    return out


def _topics_for_unit(curriculum: dict, unit: str) -> list[str]:
    comp = (curriculum.get("compulsory_units") or {}).get(unit, {})
    if comp:
        return list((comp.get("topics") or {}).keys())
    elec = (curriculum.get("elective_options") or {}).get(unit, {})
    if elec:
        return list((elec.get("topics") or {}).keys())
    return []


def _topic_keywords(curriculum: dict) -> dict[str, list[str]]:
    """topic → keywords from keyword_concepts rows."""
    out: dict[str, list[str]] = defaultdict(list)
    seen: dict[str, set[str]] = defaultdict(set)
    for row in curriculum.get("keyword_concepts", []):
        topic = str(row.get("topic") or "")
        if not topic:
            continue
        for kw in row.get("keywords", []):
            kw = str(kw)
            if kw not in seen[topic]:
                seen[topic].add(kw)
                out[topic].append(kw)
    return dict(out)


def _topic_concepts_from_curriculum(curriculum: dict) -> dict[str, set[str]]:
    out: dict[str, set[str]] = defaultdict(set)
    for row in curriculum.get("keyword_concepts", []):
        topic = str(row.get("topic") or "")
        for c in row.get("concepts", []):
            out[topic].add(str(c))
    return dict(out)


def _extract_mistakes_from_marking_item(item: dict) -> list[str]:
    found: list[str] = []
    for key in ("answer_details", "gemini_raw"):
        block = item.get(key)
        if not isinstance(block, dict):
            continue
        for sub in ("notes", "expected_answer_options", "expected_reasons"):
            val = block.get(sub)
            if isinstance(val, str):
                for m in _MISTAKE_NOTE_RE.findall(val):
                    found.append(m.strip())
            elif isinstance(val, list):
                for entry in val:
                    s = str(entry).strip()
                    if len(s) < 6 or len(s) > 80:
                        continue
                    if any(x in s for x in ("非", "錯誤", "不要", "混淆", "誤")):
                        found.append(s)
    text = item.get("text") or ""
    for m in _MISTAKE_NOTE_RE.findall(text):
        found.append(m.strip())
    return found


def _scan_bank_stats(
    bank_root: Path,
    years: tuple[str, ...],
    slugs: tuple[str, ...],
) -> tuple[dict[str, dict], dict[str, dict]]:
    """Return (concept_stats, topic_stats)."""
    rows, _ = iter_bank_items(bank_root, years, slugs)
    concept_stats: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "item_count": 0,
            "years": Counter(),
            "paper_slugs": Counter(),
            "marks": Counter(),
            "question_types": Counter(),
        }
    )
    for row in rows:
        it = row["item"]
        concepts = [str(c) for c in (it.get("concepts") or []) if c]
        if not concepts:
            continue
        qtype = infer_question_type(it, row["slug"])
        marks = _marks_key(it.get("marks"))
        for c in concepts:
            st = concept_stats[c]
            st["item_count"] += 1
            st["years"][row["year"]] += 1
            st["paper_slugs"][row["slug"]] += 1
            if marks:
                st["marks"][marks] += 1
            st["question_types"][qtype] += 1
    return dict(concept_stats), rows


def _finalize_stats(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "item_count": raw["item_count"],
        "years": _counter_dict(raw["years"]),
        "paper_slugs": _counter_dict(raw["paper_slugs"]),
        "marks_distribution": _counter_dict(raw["marks"]),
        "question_types": _counter_dict(raw["question_types"]),
    }


def _scan_marking_mistakes(
    bank_root: Path,
    years: tuple[str, ...],
) -> dict[str, Counter]:
    """concept → mistake phrases from marking scheme."""
    out: dict[str, Counter] = defaultdict(Counter)
    for year in years:
        path = bank_root / year / _MARKING_SLUG / "questions.json"
        if not path.exists():
            continue
        data = _load_json(path)
        for it in data.get("items", []):
            concepts = [str(c) for c in (it.get("concepts") or []) if c]
            if not concepts:
                continue
            for phrase in _extract_mistakes_from_marking_item(it):
                for c in concepts:
                    out[c][phrase] += 1
    return out


def _merge_style_hints(style_path: Path, concept_index: dict[str, Any]) -> None:
    if not style_path.exists():
        return
    data = _load_json(style_path)
    for concept, block in (data.get("by_concept") or {}).items():
        if concept not in concept_index:
            continue
        entry = concept_index[concept]
        terms = [t["text"] for t in (block.get("terminology") or [])[:8]]
        if terms:
            entry["top_terminology"] = terms
        qtypes = block.get("question_types") or {}
        if qtypes:
            entry["question_types"] = qtypes


def _build_tree_section(
    curriculum: dict,
    section_key: str,
    units_key: str,
    concept_stats: dict[str, dict],
    concept_topics: dict[str, set[str]],
    topic_concepts: dict[str, set[str]],
    topic_keywords: dict[str, list[str]],
    marking_mistakes: dict[str, Counter],
) -> dict[str, Any]:
    units_src = curriculum.get(units_key) or {}
    tree: dict[str, Any] = {}
    for unit_id, unit in units_src.items():
        topics_out: dict[str, Any] = {}
        for topic_id, topic_label in (unit.get("topics") or {}).items():
            concepts_set = set(topic_concepts.get(topic_id, set()))
            # add bank concepts primarily mapped to this topic
            for concept, topics in concept_topics.items():
                if topic_id in topics:
                    concepts_set.add(concept)
            concepts_sorted = sorted(concepts_set)

            topic_bank_count = 0
            topic_marks: Counter = Counter()
            topic_qtypes: Counter = Counter()
            topic_years: Counter = Counter()
            mistakes: Counter = Counter()
            for seed in _TOPIC_MISTAKE_SEEDS.get(topic_id, []):
                mistakes[seed] += 1

            for concept in concepts_sorted:
                st = concept_stats.get(concept)
                if not st:
                    continue
                topic_bank_count += st["item_count"]
                topic_marks.update(st["marks"])
                topic_qtypes.update(st["question_types"])
                topic_years.update(st["years"])
                for phrase, cnt in marking_mistakes.get(concept, Counter()).items():
                    mistakes[phrase] += cnt

            topics_out[topic_id] = {
                "label": topic_label,
                "concepts": concepts_sorted,
                "keywords": topic_keywords.get(topic_id, []),
                "common_mistakes": [t for t, _ in mistakes.most_common(8)],
                "bank_stats": {
                    "item_count": topic_bank_count,
                    "years": _counter_dict(topic_years),
                    "marks_distribution": _counter_dict(topic_marks),
                    "question_types": _counter_dict(topic_qtypes),
                },
            }
        tree[unit_id] = {
            "label": unit.get("label", unit_id),
            "topics": topics_out,
        }
        if section_key == "elective" and unit.get("legacy_paper"):
            tree[unit_id]["legacy_paper"] = unit["legacy_paper"]
    return tree


def build_concept_map(
    bank_root: Path,
    curriculum_path: Path,
    years: tuple[str, ...],
    slugs: tuple[str, ...],
    *,
    style_patterns_path: Path | None = None,
) -> dict[str, Any]:
    curriculum = _load_json(curriculum_path)
    concept_topics = _map_concepts_to_topics(curriculum)
    topic_concepts = _topic_concepts_from_curriculum(curriculum)
    topic_keywords = _topic_keywords(curriculum)
    concept_stats_raw, bank_rows = _scan_bank_stats(bank_root, years, slugs)
    concept_stats = {k: _finalize_stats(v) for k, v in concept_stats_raw.items()}
    bank_item_count = sum(
        1 for row in bank_rows if (row["item"].get("concepts") or [])
    )
    marking_mistakes = _scan_marking_mistakes(bank_root, years)

    compulsory = _build_tree_section(
        curriculum,
        "compulsory",
        "compulsory_units",
        concept_stats_raw,
        concept_topics,
        topic_concepts,
        topic_keywords,
        marking_mistakes,
    )
    elective = _build_tree_section(
        curriculum,
        "elective",
        "elective_options",
        concept_stats_raw,
        concept_topics,
        topic_concepts,
        topic_keywords,
        marking_mistakes,
    )

    concept_index: dict[str, Any] = {}
    all_concepts = set(concept_stats.keys()) | set(concept_topics.keys())
    for concept in sorted(all_concepts):
        topics = sorted(concept_topics.get(concept, set()))
        unit = (curriculum.get("concept_to_unit") or {}).get(concept, "")
        mistakes = marking_mistakes.get(concept, Counter())
        for seed_topic in topics:
            for seed in _TOPIC_MISTAKE_SEEDS.get(seed_topic, []):
                mistakes[seed] += 1
        concept_index[concept] = {
            "unit": unit,
            "topics": topics,
            "bank_stats": concept_stats.get(concept, {"item_count": 0}),
            "common_mistakes": [t for t, _ in mistakes.most_common(6)],
        }

    if style_patterns_path:
        _merge_style_hints(style_patterns_path, concept_index)

    return {
        "version": 2,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": str(_CA_GUIDE.relative_to(_REPO)),
        "curriculum": str(curriculum_path.relative_to(_REPO)),
        "question_bank": str(bank_root.relative_to(_REPO)),
        "years": list(years),
        "stats": {
            "bank_items_scanned": bank_item_count,
            "bank_rows_total": len(bank_rows),
            "distinct_concepts": len(concept_index),
            "compulsory_units": len(compulsory),
            "elective_units": len(elective),
        },
        "f5_exam_scope": {
            "mcq_units": ["A", "B", "D"],
            "written_compulsory": "Paper1B",
            "written_elective": "EA",
            "exclude_units_heavy": ["C"],
            "notes": "S5 Term2: Core A/B/D MCQ; 乙部 1B; 丙部 DB (EA) + 堆疊 (EC)",
        },
        "out_of_syllabus_rules": curriculum.get("out_of_syllabus_rules", []),
        "legacy_elective_map": curriculum.get("legacy_elective_map", {}),
        "mcq_compulsory_slot_order": curriculum.get("mcq_compulsory_slot_order", []),
        "tree": {
            "compulsory": compulsory,
            "elective": elective,
        },
        "concept_index": concept_index,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bank", type=Path, default=_DEFAULT_BANK)
    ap.add_argument("--curriculum", type=Path, default=_DEFAULT_CURRICULUM)
    ap.add_argument("--style-patterns", type=Path, default=_DEFAULT_STYLE)
    ap.add_argument("--years", nargs="+", default=list(_DEFAULT_YEARS))
    ap.add_argument("--slugs", nargs="*", default=list(_DEFAULT_SLUGS))
    ap.add_argument("--out", type=Path, default=_DEFAULT_OUT)
    ap.add_argument("--no-style", action="store_true", help="Skip merging style_patterns.json")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    years = tuple(str(y) for y in args.years)
    slugs = tuple(args.slugs) if args.slugs else _DEFAULT_SLUGS
    style = None if args.no_style else args.style_patterns.expanduser().resolve()

    payload = build_concept_map(
        args.bank.expanduser().resolve(),
        args.curriculum.expanduser().resolve(),
        years,
        slugs,
        style_patterns_path=style,
    )

    print(
        f"Concepts: {payload['stats']['distinct_concepts']}, "
        f"bank-tagged items: {payload['stats']['bank_items_scanned']}, "
        f"units: {payload['stats']['compulsory_units']} compulsory + "
        f"{payload['stats']['elective_units']} elective"
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
