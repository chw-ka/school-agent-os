"""iClass HK depth calibration — reference similar items when generating exams.

Loads `Subjects/DSE-ICT/iclass-hk/json/*.json` and `depth_profile.json`.
Used for every blueprint slot: attach `depth_references` to spec items and,
when concepts match, adapt ask depth from iClass (not verbatim copy).
"""
from __future__ import annotations

import json
import random
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[2]
_ICLASS_JSON = _REPO / "Subjects/DSE-ICT/iclass-hk/json"
_DEPTH_PROFILE = _REPO / "Subjects/DSE-ICT/iclass-hk/depth_profile.json"

_TIER_RANK = {"foundation": 0, "intermediate": 1, "advanced": 2}
_NUM_RE = re.compile(r"\b(\d{1,4})\b")
_NAME_RE = re.compile(r"(偉豪|家明|嘉欣|子華|張先生|李小姐|[「『][^」』]{2,8}[」』])")

# Blueprint concept → iClass item concept tags
_CONCEPT_EXPAND: dict[str, tuple[str, ...]] = {
    "Python": ("Python", "列表", "循環", "輸入輸出", "選擇結構", "函數", "數據類型"),
    "算法": ("算法",),
    "流程圖": ("算法",),
    "程式測試": ("程式測試", "除錯"),
    "除錯": ("除錯", "程式測試"),
    "邊界值": ("程式測試", "除錯"),
    "模組": ("Python", "函數"),
    "排序": ("算法", "Python", "排序"),
    "堆疊": ("算法", "堆疊"),
    "線性搜尋": ("算法",),
    "迭代": ("循環", "算法"),
    "選擇結構": ("選擇結構", "Python"),
    "循環": ("循環", "Python"),
    "資訊處理": ("資訊處理",),
    "數據組織": ("資訊處理",),
    "欄位": ("資訊處理",),
    "記錄": ("資訊處理",),
    "試算表": ("試算表",),
    "多媒體": ("多媒體",),
    "進制": ("進制",),
    "RAM": ("硬件",),
    "ROM": ("硬件",),
    "CPU": ("硬件",),
    "硬件": ("硬件",),
    "軟件": ("軟件",),
    "作業系統": ("軟件",),
    "輸入裝置": ("輸入輸出", "硬件"),
    "輸出裝置": ("輸入輸出", "硬件"),
    "數據庫": ("數據庫", "SQL"),
    "SQL": ("SQL", "數據庫"),
    "ERD": ("數據庫",),
    "正規化": ("數據庫",),
    "JOIN": ("SQL", "數據庫"),
}

_CORE_D_CONCEPTS = frozenset(_CONCEPT_EXPAND) | frozenset(
    {
        "Python",
        "算法",
        "流程圖",
        "程式測試",
        "除錯",
        "邊界值",
        "模組",
        "排序",
        "堆疊",
        "迭代",
        "線性搜尋",
        "選擇結構",
        "循環",
        "資訊處理",
        "試算表",
        "多媒體",
        "進制",
        "RAM",
        "硬件",
        "軟件",
        "數據庫",
        "SQL",
    }
)

_WRITTEN_ICLASS_SLOTS = frozenset({"b-04", "b-05"})

_COMBO_MCQ_SLOTS = frozenset({2, 5, 9, 14, 19, 24, 29})


def _stem_fits_mcq_slot(stem: str, slot_index: int) -> bool:
    """Respect template MCQ block row budget (see spec_mcq_render.MCQ_SPANS)."""
    from spec_mcq_render import MCQ_SPANS

    span = MCQ_SPANS[slot_index - 1] if 1 <= slot_index <= len(MCQ_SPANS) else 10
    lines = stem.count("\n") + 1
    max_stem_lines = max(3, span - 2)
    if slot_index in _COMBO_MCQ_SLOTS:
        max_stem_lines = min(max_stem_lines, 3)
    return lines <= max_stem_lines and len(stem) <= max_stem_lines * 55


@lru_cache(maxsize=1)
def load_depth_profile() -> dict[str, Any]:
    if not _DEPTH_PROFILE.is_file():
        return {}
    return json.loads(_DEPTH_PROFILE.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _load_all_bank_items() -> tuple[dict[str, Any], ...]:
    rows: list[dict[str, Any]] = []
    if not _ICLASS_JSON.is_dir():
        return tuple()
    skip = frozenset({"index.json"})
    for path in sorted(_ICLASS_JSON.glob("*.json")):
        if path.name in skip:
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if not data.get("items"):
            continue
        meta = data.get("meta") or {}
        for it in data.get("items") or []:
            rows.append(
                {
                    **it,
                    "_chapter": meta.get("chapter"),
                    "_slug": meta.get("slug"),
                    "_title": meta.get("title") or meta.get("title_zh"),
                    "_family": meta.get("family"),
                    "_curriculum_unit": meta.get("curriculum_unit"),
                    "_ca_unit": meta.get("ca_unit"),
                    "_language": meta.get("language"),
                }
            )
    return tuple(rows)


def _expand_concepts(concepts: list[str]) -> set[str]:
    tags: set[str] = set()
    for c in concepts:
        tags.add(c)
        tags.update(_CONCEPT_EXPAND.get(c, ()))
    return tags


def _score_item(
    item: dict[str, Any],
    concepts: list[str],
    *,
    core: str | None = None,
    section: str | None = None,
) -> float:
    tags = _expand_concepts(concepts)
    if not tags:
        return 0.0
    item_tags = set(item.get("concepts") or [])
    overlap = len(tags & item_tags)
    if overlap == 0:
        return 0.0
    score = float(overlap)
    if "Python" in concepts and "Python" in item_tags:
        score += 2.5
    stem = str(item.get("stem") or "")
    if "Python" in concepts and ("Python" in stem or "def " in stem or "for " in stem):
        score += 1.0
    tier = _TIER_RANK.get(str(item.get("difficulty_tier") or "foundation"), 0)
    score += tier * 0.5
    cu = str(item.get("_curriculum_unit") or "")
    if core and cu.startswith(f"Core-{core}"):
        score += 0.8
    elif core == "A" and cu == "Core-A":
        score += 0.8
    elif core == "B" and cu == "Core-B":
        score += 0.8
    elif core == "D" and cu.startswith("Core-D"):
        score += 0.8
    if core == "D" and item.get("_chapter") in (4, 5, 6, None):
        score += 0.3
    if section == "mcq" and item.get("section_type") == "mcq":
        score += 0.3
    if section and section.startswith("section_") and item.get("section_type") != "mcq":
        score += 0.3
    if section == "section_b":
        if item.get("section_type") == "short_answer":
            score += 0.8
        elif item.get("section_type") == "long_answer":
            score -= 0.6
    if section == "section_c" and item.get("section_type") in ("short_answer", "long_answer"):
        score += 0.3
    return score


def _ranked_items(
    concepts: list[str],
    *,
    core: str | None = None,
    section: str | None = None,
    min_tier: str | None = None,
) -> list[tuple[float, dict[str, Any]]]:
    floor = _TIER_RANK.get(min_tier, 0) if min_tier else 0
    ranked: list[tuple[float, dict[str, Any]]] = []
    for it in _load_all_bank_items():
        tier = _TIER_RANK.get(str(it.get("difficulty_tier") or "foundation"), 0)
        if tier < floor:
            continue
        sc = _score_item(it, concepts, core=core, section=section)
        if sc > 0:
            ranked.append((sc, it))
    ranked.sort(key=lambda x: (-x[0], str(x[1].get("id"))))
    return ranked


def depth_reference_summary(item: dict[str, Any]) -> dict[str, Any]:
    stem = str(item.get("stem") or item.get("text") or "")[:220]
    return {
        "id": item.get("id"),
        "bank_code": item.get("bank_code"),
        "chapter": item.get("_chapter"),
        "source_slug": item.get("_slug"),
        "section_type": item.get("section_type"),
        "marks": item.get("marks"),
        "difficulty_tier": item.get("difficulty_tier"),
        "concepts": list(item.get("concepts") or []),
        "stem_preview": stem.replace("\n", " ")[:200],
    }


def depth_references_for_slot(
    slot: dict[str, Any],
    *,
    limit: int = 3,
) -> list[dict[str, Any]]:
    """Return top iClass items as depth benchmarks for this blueprint slot."""
    concepts = list(slot.get("concepts") or [])
    if not concepts and not _load_all_bank_items():
        return []
    ranked = _ranked_items(
        concepts,
        core=str(slot.get("core") or "") or None,
        section=str(slot.get("section") or "") or None,
        min_tier="foundation",
    )
    return [depth_reference_summary(it) for _, it in ranked[:limit]]


def slot_uses_iclass_depth(slot: dict[str, Any]) -> bool:
    concepts = set(slot.get("concepts") or [])
    core = str(slot.get("core") or "")
    sid = str(slot.get("id") or "")
    if core in ("A", "B", "D") or concepts & _CORE_D_CONCEPTS:
        return True
    if sid.startswith("c-") and concepts & {"數據庫", "SQL", "ERD", "正規化", "JOIN"}:
        return True
    if sid in _WRITTEN_ICLASS_SLOTS:
        return True
    if depth_references_for_slot(slot, limit=1):
        return True
    return False


def attach_depth_references(item: dict[str, Any], slot: dict[str, Any]) -> dict[str, Any]:
    refs = depth_references_for_slot(slot, limit=3)
    if refs:
        item["depth_references"] = refs
        item["depth_calibration"] = "iclass-hk"
    return item


def _mutate_numbers(text: str, rng: random.Random, *, max_subs: int = 4) -> str:
    matches = list(_NUM_RE.finditer(text))
    if not matches:
        return text
    picks = rng.sample(matches, k=min(max_subs, len(matches)))
    parts: list[str] = []
    last = 0
    for m in sorted(picks, key=lambda x: x.start()):
        n = int(m.group(1))
        delta = rng.choice([-2, -1, 1, 2])
        new_n = max(0, n + delta) if n < 20 else n + delta
        parts.append(text[last : m.start()])
        parts.append(str(new_n))
        last = m.end()
    parts.append(text[last:])
    return "".join(parts)


def _anonymize_names(text: str, rng: random.Random) -> str:
    names = ("青禾社", "煦風學會", "某校", "該公司", "該程式")
    return _NAME_RE.sub(lambda _: rng.choice(names), text, count=3)


def _options_fit_mcq_slot(options: list[str], slot_index: int) -> bool:
    from spec_mcq_render import MCQ_SPANS

    span = MCQ_SPANS[slot_index - 1] if 1 <= slot_index <= len(MCQ_SPANS) else 10
    opt_budget = max(4, span - 3)
    used = 0
    for o in options:
        lines = o.count("\n") + 1
        if lines > 2 or len(o) > 90:
            return False
        used += max(1, lines)
    return used + 2 <= opt_budget


def _trim_stem_for_span(stem: str, slot_index: int) -> str:
    from spec_mcq_render import MCQ_SPANS

    span = MCQ_SPANS[slot_index - 1] if 1 <= slot_index <= len(MCQ_SPANS) else 10
    budget = max(2, span - 5)
    lines = [ln for ln in stem.splitlines() if ln.strip()]
    if len(lines) <= budget:
        return stem
    return "\n".join(lines[: budget - 1] + [lines[-1]])


def adapt_iclass_mcq(
    item: dict[str, Any],
    rng: random.Random,
    *,
    slot_index: int = 1,
) -> tuple[str, list[str], int] | None:
    stem = str(item.get("stem") or "").strip()
    if len(re.findall(r"[\u4e00-\u9fff]", stem)) < 8:
        return None
    opts_map = item.get("options") or {}
    letters = [k for k in "ABCD" if opts_map.get(k)]
    if not stem or len(letters) < 4:
        return None
    options = [str(opts_map[k]).strip() for k in letters]
    if not _options_fit_mcq_slot(options, slot_index):
        return None
    ans_letter = str(item.get("answer") or "A").strip().upper()[:1]
    try:
        correct_idx = letters.index(ans_letter)
    except ValueError:
        correct_idx = 0
    stem = _anonymize_names(_mutate_numbers(stem, rng), rng)
    stem = _trim_stem_for_span(stem, slot_index)
    return stem, options, correct_idx


def pick_iclass_mcq(
    rng: random.Random,
    *,
    slot_index: int,
    concepts: list[str] | None = None,
    core: str | None = None,
    min_tier: str = "intermediate",
    prefer_python: bool = False,
) -> tuple[str, list[str], int] | None:
    """Pick iClass MCQ shape matched to slot concepts (light variation, not copy)."""
    ranked = _ranked_items(
        list(concepts or []),
        core=core,
        section="mcq",
        min_tier=min_tier,
    )
    if prefer_python:
        py_ranked = [
            (sc, it)
            for sc, it in ranked
            if "Python" in (it.get("concepts") or [])
            or "python" in str(it.get("stem") or "").lower()
        ]
        if py_ranked:
            ranked = py_ranked
    if not ranked:
        ranked = _ranked_items(list(concepts or []), core=core, section="mcq", min_tier="foundation")
    if not ranked and core == "D":
        # Legacy: any Core D chapter MCQ
        pool = [
            it
            for it in _load_all_bank_items()
            if it.get("section_type") == "mcq"
            and _TIER_RANK.get(str(it.get("difficulty_tier")), 0)
            >= _TIER_RANK.get(min_tier, 1)
        ]
        if pool:
            rng2 = random.Random((slot_index * 7919) ^ rng.randint(0, 2**30))
            return adapt_iclass_mcq(rng2.choice(pool), rng, slot_index=slot_index)
        return None
    if not ranked:
        return None
    top_score = ranked[0][0]
    pool = [it for sc, it in ranked if sc >= top_score - 0.5][:12]
    pool = [it for it in pool if _stem_fits_mcq_slot(str(it.get("stem") or ""), slot_index)]
    pool = [
        it
        for it in pool
        if _options_fit_mcq_slot(
            [str((it.get("options") or {}).get(k) or "") for k in "ABCD"],
            slot_index,
        )
    ]
    if not pool:
        pool = [it for sc, it in ranked[:20] if _stem_fits_mcq_slot(str(it.get("stem") or ""), slot_index)]
    if not pool:
        return None
    rng2 = random.Random((slot_index * 7919) ^ rng.randint(0, 2**30))
    item = rng2.choice(pool)
    return adapt_iclass_mcq(item, rng, slot_index=slot_index)


def _subpart_line(label: str, body: str, marks: int | float) -> str:
    return f"({label}) {body.strip()}\t({int(marks)} 分)"


def adapt_iclass_written(
    item: dict[str, Any],
    slot: dict[str, Any],
    rng: random.Random,
) -> str | None:
    """Build written-style text from iClass short/long item (structure only)."""
    stem = str(item.get("stem") or "").strip()
    if len(stem) < 20:
        return None
    stem = _anonymize_names(_mutate_numbers(stem, rng), rng)
    parts = list(item.get("parts") or [])
    subparts = list(slot.get("subparts") or [])
    lines: list[str] = [stem]
    if parts and subparts:
        for i, part in enumerate(parts):
            if i >= len(subparts):
                break
            label = str(part.get("label") or "a")[0]
            body = str(part.get("text") or "").strip()
            if body:
                body = _anonymize_names(_mutate_numbers(body, rng), rng)
                mk = subparts[i].get("marks", part.get("marks", 2))
                lines.append(_subpart_line(label, body, mk))
    elif subparts:
        labels = "abcdef"[: len(subparts)]
        chunk = max(1, len(stem) // len(subparts))
        for i, sp in enumerate(subparts):
            seg = stem[i * chunk : (i + 1) * chunk] if i < len(subparts) - 1 else stem[i * chunk :]
            prompt = seg.strip() or f"就上述內容回答 ({labels[i]}) 部分。"
            lines.append(_subpart_line(labels[i], prompt, sp.get("marks", 2)))
    marks_total = float(slot.get("marks") or item.get("marks") or 4)
    if len(lines) == 1:
        return None
    if any("回答上述問題" in ln for ln in lines):
        return None
    return "\n\n".join(lines)


def pick_iclass_written(
    slot: dict[str, Any],
    rng: random.Random,
    *,
    min_tier: str = "intermediate",
) -> str | None:
    concepts = list(slot.get("concepts") or [])
    ranked = _ranked_items(
        concepts,
        core=str(slot.get("core") or "") or None,
        section=str(slot.get("section") or ""),
        min_tier=min_tier,
    )
    written = [
        (sc, it)
        for sc, it in ranked
        if it.get("section_type") in ("short_answer", "long_answer")
    ]
    if not written:
        return None
    top = written[0][0]
    pool = [it for sc, it in written if sc >= top - 0.5][:8]
    item = rng.choice(pool)
    return adapt_iclass_written(item, slot, rng)


def try_iclass_mcq(
    slot: dict[str, Any],
    rng: random.Random,
    *,
    variant: int = 0,
) -> tuple[str, list[str], int] | None:
    """Return adapted MCQ if slot should use iClass depth."""
    if not slot_uses_iclass_depth(slot):
        return None
    sid = str(slot.get("id", ""))
    m = re.search(r"(\d+)$", sid)
    idx = int(m.group(1)) if m else 1
    concepts = list(slot.get("concepts") or [])
    core = str(slot.get("core") or "") or None
    programming_slot = core == "D" or idx >= 21
    prefer_python = "Python" in concepts or programming_slot
    from spec_mcq_render import MCQ_SPANS

    span = MCQ_SPANS[idx - 1] if 1 <= idx <= len(MCQ_SPANS) else 10
    if span <= 7:
        return None
    min_tier = "intermediate"
    if programming_slot and idx in (23, 25, 26, 28):
        min_tier = "advanced"
    ranked = _ranked_items(concepts, core=core, section="mcq", min_tier=min_tier)
    if not ranked and min_tier == "advanced":
        ranked = _ranked_items(concepts, core=core, section="mcq", min_tier="intermediate")
    prob = 0.55
    if programming_slot:
        prob = 0.95
    elif core == "D":
        prob = 0.75
    if ranked and ranked[0][0] >= 2.0:
        prob = min(0.98, prob + 0.05)
    if not programming_slot and rng.random() > prob:
        return None
    return pick_iclass_mcq(
        rng,
        slot_index=idx + variant,
        concepts=concepts,
        core=core,
        min_tier=min_tier,
        prefer_python=prefer_python,
    )


def core_d_generation_hints() -> dict[str, Any]:
    profile = load_depth_profile()
    if not profile:
        return {}
    return {
        "guidance": profile.get("guidance_for_f5_exam"),
        "usage_notes": profile.get("usage_notes"),
        "chapters": profile.get("chapters"),
    }


def depth_calibration_meta() -> dict[str, Any]:
    profile = load_depth_profile()
    return {
        "source": "iclass-hk",
        "profile_path": str(_DEPTH_PROFILE.relative_to(_REPO)).replace("\\", "/"),
        "json_root": str(_ICLASS_JSON.relative_to(_REPO)).replace("\\", "/"),
        "bank_items": len(_load_all_bank_items()),
        "purpose": (profile.get("purpose") if profile else "depth calibration"),
    }
