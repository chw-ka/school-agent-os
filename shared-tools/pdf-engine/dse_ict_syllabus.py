"""Tag DSE ICT question-bank items against the 2021-revised curriculum (2025+ HKDSE)."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
DEFAULT_CONCEPTS_PATH = REPO / "Subjects/DSE-ICT/question-bank/curriculum_concepts.json"

# Concepts removed from compulsory A-d (word / presentation apps) in 2021 revision
OUT_OF_SYLLABUS_CONCEPTS: frozenset[str] = frozenset(
    {
        "文書處理",
        "演示軟件",
        "郵件合併",
        "OLE",
        "網上演示",
    }
)


def load_concepts_cfg(path: Path | None = None) -> dict:
    p = path or DEFAULT_CONCEPTS_PATH
    return json.loads(p.read_text(encoding="utf-8"))


def _elective_code_from_section(section: str) -> str | None:
    if "數據庫" in section or section.startswith("甲部"):
        return "EA"
    if "網絡" in section or section.startswith("乙部"):
        return "EB"
    if "算法" in section or "程式" in section or section.startswith("丙部"):
        return "EC"
    return None


def infer_concepts_from_text(
    text: str,
    *,
    paper_slug: str,
    concepts_cfg: dict,
    raw: dict | None = None,
) -> dict[str, Any]:
    """Keyword-based concept + curriculum unit tagging (2025+ syllabus aware)."""
    lower = text.lower()
    matched_concepts: list[str] = []
    units: set[str] = set()
    topics: set[str] = set()

    legacy = concepts_cfg.get("legacy_elective_map", {})
    elective_code = legacy.get(paper_slug)

    if paper_slug == "Paper2_Elective" and raw:
        sec = str(raw.get("section") or "")
        elective_code = _elective_code_from_section(sec) or elective_code

    for rule in concepts_cfg.get("keyword_concepts", []):
        if rule.get("out_of_syllabus"):
            continue
        if any(kw.lower() in lower or kw in text for kw in rule["keywords"]):
            matched_concepts.extend(rule.get("concepts", []))
            if rule.get("unit"):
                units.add(rule["unit"])
            if rule.get("topic"):
                topics.add(rule["topic"])

    qtype = ((raw or {}).get("question_type") or "").lower()
    if "sql" in qtype or re.search(r"\bSQL\b", text, re.I):
        matched_concepts.extend(["SQL", "數據庫"])
        units.add("EA" if elective_code in ("EA", None) and paper_slug == "Paper2_Elective" else "A")
        if paper_slug == "Paper2_Elective":
            units.add("EA")
    if any(x in qtype for x in ("algorithm", "pseudocode", "trace")):
        matched_concepts.extend(["算法", "偽代碼"])
        units.add("EC" if elective_code == "EC" else "D")

    # Explicit concept hints from gemini / prior tags (non-removed only)
    for c in (raw or {}).get("concepts") or []:
        if c not in OUT_OF_SYLLABUS_CONCEPTS:
            matched_concepts.append(str(c))

    if elective_code:
        part = "elective"
        unit_label = concepts_cfg["elective_options"][elective_code]["label"]
        curriculum_unit = f"選修{elective_code[-1]}-{unit_label}"
    elif paper_slug == "Paper2_Elective":
        part = "elective"
        curriculum_unit = "選修部分"
    elif paper_slug == "Paper1B_CompulsoryStructured":
        part = "compulsory"
        curriculum_unit = "必修部分-乙丙部"
    elif paper_slug in ("Paper1_MultipleChoice", "Paper1A_MultipleChoice"):
        part = "compulsory"
        curriculum_unit = "必修部分-甲部"
    elif paper_slug == "MarkingScheme":
        part = "marking"
        curriculum_unit = "評卷參考"
    else:
        part = "compulsory"
        curriculum_unit = "必修部分"

    if units and part == "compulsory":
        comp = concepts_cfg["compulsory_units"]
        unit_labels = [f"{u}-{comp[u]['label']}" for u in sorted(units) if u in comp]
        if unit_labels:
            curriculum_unit = "；".join(unit_labels)

    topic_labels: list[str] = []
    comp = concepts_cfg.get("compulsory_units", {})
    elec = concepts_cfg.get("elective_options", {})
    for t in sorted(topics):
        if "-" in t:
            unit_key, sub = t.split("-", 1)
            if unit_key in comp and sub in comp[unit_key]["topics"]:
                topic_labels.append(comp[unit_key]["topics"][sub])
            elif unit_key in elec and sub in elec[unit_key]["topics"]:
                topic_labels.append(elec[unit_key]["topics"][sub])

    seen: set[str] = set()
    concepts_out: list[str] = []
    for c in matched_concepts:
        if c in OUT_OF_SYLLABUS_CONCEPTS:
            continue
        if c not in seen:
            seen.add(c)
            concepts_out.append(c)

    return {
        "concepts": concepts_out,
        "curriculum_part": part,
        "curriculum_unit": curriculum_unit,
        "curriculum_topics": topic_labels,
    }


def classify_syllabus(
    text: str,
    *,
    concepts: list[str] | None = None,
    concepts_cfg: dict | None = None,
    paper_year: str | None = None,
) -> dict[str, Any]:
    """Return syllabus_status + reasons. Uses EDB 2021 revision rules in curriculum_concepts.json."""
    cfg = concepts_cfg or load_concepts_cfg()
    concepts = concepts or []
    lower = text.lower()
    reasons: list[str] = []

    for rule in cfg.get("out_of_syllabus_rules", []):
        kws = rule.get("keywords") or []
        unless = rule.get("unless_keywords") or []
        if not any(kw.lower() in lower or kw in text for kw in kws):
            continue
        if unless and any(u.lower() in lower or u in text for u in unless):
            continue
        reasons.append(rule.get("label") or rule.get("id", "out_of_syllabus"))

    removed_hits = [c for c in concepts if c in OUT_OF_SYLLABUS_CONCEPTS]
    if removed_hits:
        reasons.append(f"removed concept tag(s): {', '.join(removed_hits)}")

    for rule in cfg.get("out_of_syllabus_rules", []):
        for c in rule.get("concepts") or []:
            if c in concepts and c not in removed_hits:
                reasons.append(rule.get("label") or f"concept {c}")

    # Exact ASCII / character code recall (guide: recall of specific codes not required)
    if re.search(r"ASCII.*(十六進制|hex).*(分別|分別為|____)", text, re.I):
        reasons.append("specific ASCII code recall (not required in 2021 syllabus)")
    if re.search(r"字符.*ASCII.*十六進制.*分別", text):
        reasons.append("specific ASCII code recall (not required in 2021 syllabus)")

    if re.search(r"\bRAID[- ]?[015]", text, re.I) or "RAID-" in text.upper():
        reasons.append("RAID levels (removed from Core B)")

    # Deduplicate preserving order
    seen: set[str] = set()
    unique_reasons: list[str] = []
    for r in reasons:
        if r not in seen:
            seen.add(r)
            unique_reasons.append(r)

    status = "out_of_syllabus" if unique_reasons else "current"
    return {
        "syllabus_status": status,
        "syllabus_revision": cfg.get("syllabus_revision", "2021"),
        "out_of_syllabus_reasons": unique_reasons,
    }


def tag_item(
    item: dict,
    *,
    paper_slug: str,
    paper_year: str,
    concepts_cfg: dict | None = None,
) -> dict:
    """Re-infer concepts and syllabus flags on a question-bank item (in place)."""
    cfg = concepts_cfg or load_concepts_cfg()
    text = item.get("text") or item.get("stem") or ""
    raw = item.get("gemini_raw") or {}

    tags = infer_concepts_from_text(
        text,
        paper_slug=paper_slug,
        concepts_cfg=cfg,
        raw={**raw, "concepts": item.get("concepts")},
    )
    item["concepts"] = tags["concepts"]
    item["curriculum_part"] = tags["curriculum_part"]
    item["curriculum_unit"] = tags["curriculum_unit"]
    if tags["curriculum_topics"]:
        item["curriculum_topics"] = tags["curriculum_topics"]
    elif "curriculum_topics" in item:
        del item["curriculum_topics"]

    syll = classify_syllabus(
        text,
        concepts=item["concepts"],
        concepts_cfg=cfg,
        paper_year=paper_year,
    )
    item["syllabus_status"] = syll["syllabus_status"]
    item["syllabus_revision"] = syll["syllabus_revision"]
    if syll["out_of_syllabus_reasons"]:
        item["out_of_syllabus_reasons"] = syll["out_of_syllabus_reasons"]
    elif "out_of_syllabus_reasons" in item:
        del item["out_of_syllabus_reasons"]
    return item


def is_syllabus_current(item: dict, *, concepts_cfg: dict | None = None) -> bool:
    status = item.get("syllabus_status")
    if status:
        return status == "current"
    text = item.get("text") or item.get("stem") or ""
    syll = classify_syllabus(
        text,
        concepts=item.get("concepts") or [],
        concepts_cfg=concepts_cfg,
    )
    return syll["syllabus_status"] == "current"
