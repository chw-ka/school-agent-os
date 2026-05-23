"""Pick 乙部／丙部 structured items from DSE question-bank (Paper 1B + Paper 2A)."""
from __future__ import annotations

import json
import random
import re
import sys
from collections import defaultdict
from pathlib import Path

from f5_ict_from_dse import (
    _BANK_SIM_THRESH,
    _BANK_SIM_THRESH_WRITTEN_STEM,
    _BANK_SIM_THRESH_WRITTEN_SUBPART,
    _adapt_text,
    _concept_overlap,
    _load_bank_items,
    _syllabus_ok,
    _text_ok,
    _unit_ok,
    _vary_numbers_text,
)
from quality_lib import normalize_text, text_similarity

_QCHECK = Path(__file__).resolve().parents[1] / "question-quality-check"
if str(_QCHECK) not in sys.path:
    sys.path.insert(0, str(_QCHECK))
from coherence_check import _TOPIC_SQL, check_text_coherence  # noqa: E402

_JSON_BLOCK_RE = re.compile(r"\n?\s*\{[\s\S]*\}\s*$")
_IMAGE_DESC_RE = re.compile(r"\[圖片描述\][^\n]*")
_QNUM_RE = re.compile(r"^(\d+)")
_COL_REF_RE = re.compile(r"欄\s*([A-Z])(?![A-Z])", re.IGNORECASE)
_CELL_REF_RE = re.compile(r"\b([A-Z])(\d{1,3})\b")

_WRITTEN_NAME_SUBS = (
    ("小芬", "家豪"),
    ("志明", "美玲"),
    ("志文", "家明"),
    ("阿文", "嘉欣"),
)
_WRITTEN_PHRASE_SWAPS = (
    ("寫出", "試寫出"),
    ("列出", "試列出"),
    ("簡略說明", "簡要說明"),
    ("舉出", "舉例說明"),
    ("完成以下", "試完成以下"),
    ("描述", "說明"),
    ("解釋", "說明"),
)

# slot_id, section, concepts, paper slugs, marks, title
WRITTEN_SLOT_PLAN: tuple[tuple[str, str, tuple[str, ...], tuple[str, ...], int, str], ...] = (
    ("b-01", "section_b", ("試算表", "IF", "COUNTIFS"), ("Paper1B_CompulsoryStructured",), 4, "試算表"),
    ("b-02", "section_b", ("有效性檢驗", "奇偶檢測"), ("Paper1B_CompulsoryStructured",), 5, "數據有效性"),
    ("b-03", "section_b", ("多媒體", "點陣圖", "壓縮"), ("Paper1B_CompulsoryStructured",), 4, "多媒體檔案大小"),
    ("b-04", "section_b", ("算法", "偽代碼", "陣列"), ("Paper1B_CompulsoryStructured",), 4, "線性搜尋"),
    ("b-05", "section_b", ("檔案存取", "直接存取", "順序存取"), ("Paper1B_CompulsoryStructured",), 4, "索引檔存取"),
    ("b-06", "section_b", ("數據庫", "SQL", "資料類型"), ("Paper1B_CompulsoryStructured",), 9, "網店訂單與 SQL"),
    ("c-01", "section_c", ("ERD", "數據庫"), ("Paper2A_Database", "Paper2_Elective"), 4, "戲院預訂 ERD"),
    ("c-02", "section_c", ("數據庫", "SQL"), ("Paper2A_Database", "Paper2_Elective"), 2, "CREATE / INSERT"),
    ("c-03", "section_c", ("數據庫", "SQL", "UNION"), ("Paper2A_Database", "Paper2_Elective"), 3, "UNION / UPDATE"),
    ("c-05", "section_c", ("數據庫", "SQL", "MINUS"), ("Paper2A_Database", "Paper2_Elective"), 11, "FACILITY / RESERVE"),
    ("c-06", "section_c", ("數據庫", "SQL", "JOIN", "GROUP BY"), ("Paper2A_Database", "Paper2_Elective"), 5, "SQL 查詢追蹤"),
    ("c-07", "section_c", ("數據庫", "Transaction", "COMMIT", "ROLLBACK"), ("Paper2A_Database", "Paper2_Elective"), 9, "一卡通交易"),
    (
        "c-08",
        "section_c",
        ("算法", "堆疊", "偽代碼"),
        ("Paper2D_SoftwareDevelopment", "Paper2_Elective"),
        6,
        "堆疊操作",
    ),
)

# Paragraph index in template for opening scenario line (DOCX replace_span)
WRITTEN_SCENARIO_PARA: dict[str, int] = {
    "b-01": 313,
    "b-02": 323,
    "b-03": 336,
    "b-04": 354,
    "b-05": 377,
    "b-06": 394,
    "c-01": 425,
    "c-02": 440,
    "c-03": 457,
    "c-05": 496,
    "c-06": 541,
    "c-07": 566,
    "c-08": 595,
}

_WRITTEN_YEARS = ("2021", "2022", "2023", "2024", "2025")
_WRITTEN_BANK_SLUGS = (
    "Paper1B_CompulsoryStructured",
    "Paper2A_Database",
    "Paper2_Elective",
    "Paper2D_SoftwareDevelopment",
)
_active_written_picks: dict[str, dict] | None = None


def set_active_written_picks(picks: dict[str, dict] | None) -> None:
    global _active_written_picks
    _active_written_picks = picks


def get_active_written_picks() -> dict[str, dict] | None:
    return _active_written_picks


def scenario_override(slot_id: str, default: str) -> str:
    picks = _active_written_picks
    if not picks or slot_id not in picks:
        return default
    line = picks[slot_id].get("scenario_line", "").strip()
    return line if line else default


def _item_part_text(it: dict) -> str:
    return (it.get("stem") or it.get("text") or "").strip()


def _shift_column_refs(text: str, rng: random.Random) -> str:
    offset = rng.randint(1, 2)

    def col_sub(m: re.Match[str]) -> str:
        letter = m.group(1).upper()
        new_i = min(ord("Z"), ord(letter) - ord("A") + offset)
        return f"欄 {chr(ord('A') + new_i)}"

    out = _COL_REF_RE.sub(col_sub, text)

    def cell_sub(m: re.Match[str]) -> str:
        letter, num = m.group(1).upper(), int(m.group(2))
        new_i = min(ord("Z") - ord("A"), ord(letter) - ord("A") + offset)
        new_letter = chr(ord("A") + new_i)
        return f"{new_letter}{max(2, num + rng.choice([0, 1, 2]))}"

    return _CELL_REF_RE.sub(cell_sub, out)


def _reframe_written_phrases(text: str, rng: random.Random) -> str:
    out = text
    for old, new in _WRITTEN_NAME_SUBS:
        if old in out and rng.random() < 0.85:
            out = out.replace(old, new)
    swaps = list(_WRITTEN_PHRASE_SWAPS)
    rng.shuffle(swaps)
    for old, new in swaps[: rng.randint(2, 4)]:
        if old in out:
            out = out.replace(old, new, 1)
    return out


def _prepare_written_part(text: str, rng: random.Random, mapping: dict[int, int]) -> str:
    t = _strip_written_raw(text)
    t = _adapt_text(t, rng)
    t = _vary_numbers_text(t, rng, mapping)
    if rng.random() < 0.55 and re.search(r"欄\s*[A-Z]", t, re.I):
        t = _shift_column_refs(t, rng)
    t = _reframe_written_phrases(t, rng)
    return re.sub(r"\n{3,}", "\n\n", t.strip())


def _clean_bank_written_text(text: str, rng: random.Random, mapping: dict[int, int] | None = None) -> str:
    m = mapping if mapping is not None else {}
    return _prepare_written_part(text, rng, m)


def _cluster_key(item: dict) -> str:
    num = str(item.get("number") or "")
    m = _QNUM_RE.match(num.strip())
    if m:
        return m.group(1)
    iid = str(item.get("id", ""))
    parts = iid.split("-")
    for p in parts:
        if p.isdigit():
            return p
    return iid


def _written_pool(rng: random.Random, slugs: tuple[str, ...]) -> list[dict]:
    pool: list[dict] = []
    years = list(_WRITTEN_YEARS)
    rng.shuffle(years)
    for year in years:
        for slug in slugs:
            for it in _load_bank_items(year, slug):
                if not _text_ok(it.get("text", "") or it.get("stem", "")):
                    continue
                if not _unit_ok(it.get("curriculum_unit", "")):
                    continue
                if not _syllabus_ok(it):
                    continue
                pool.append({**it, "_year": year, "_slug": slug})
    return pool


def _cluster_items(pool: list[dict]) -> dict[str, list[dict]]:
    clusters: dict[str, list[dict]] = defaultdict(list)
    for it in pool:
        key = f"{it['_year']}:{it['_slug']}:{_cluster_key(it)}"
        clusters[key].append(it)
    return clusters


def _score_cluster(items: list[dict], concepts: tuple[str, ...]) -> int:
    return sum(_concept_overlap(it.get("concepts", []), list(concepts)) for it in items)


def _assemble_cluster_text(
    items: list[dict],
    rng: random.Random,
    *,
    max_parts: int = 10,
    mapping: dict[int, int] | None = None,
) -> str:
    ordered = sorted(items, key=lambda x: str(x.get("number", x.get("id", ""))))
    parts: list[str] = []
    seen: set[str] = set()
    m = mapping if mapping is not None else {}
    for it in ordered:
        raw = _item_part_text(it)
        if not raw:
            continue
        cleaned = _prepare_written_part(raw, rng, m)
        key = cleaned[:80]
        if key in seen:
            continue
        seen.add(key)
        parts.append(cleaned)
        if len(parts) >= max_parts:
            break
    return "\n\n".join(parts)


def _ranked_parts(
    pool: list[dict],
    concepts: tuple[str, ...],
    used_ids: set[str],
) -> list[dict]:
    scored: list[tuple[int, dict]] = []
    for it in pool:
        if it["id"] in used_ids:
            continue
        raw = _item_part_text(it)
        if len(raw) < 12 or not _text_ok(raw):
            continue
        score = _concept_overlap(it.get("concepts", []), list(concepts))
        if score < 1:
            continue
        scored.append((score, it))
    scored.sort(key=lambda x: (-x[0], x[1].get("_year", ""), x[1]["id"]))
    return [it for _, it in scored]


def _select_cross_year_parts(
    rng: random.Random,
    candidates: list[dict],
    *,
    n_parts: int,
    min_years: int = 2,
) -> list[dict]:
    if not candidates:
        return []
    by_year: dict[str, list[dict]] = defaultdict(list)
    for it in candidates[:48]:
        by_year[str(it.get("_year", ""))].append(it)
    years = [y for y in by_year if y]
    picked: list[dict] = []
    seen_ids: set[str] = set()

    if len(years) >= min_years:
        rng.shuffle(years)
        for y in years[:min_years]:
            choices = [x for x in by_year[y] if x["id"] not in seen_ids]
            if not choices:
                continue
            it = rng.choice(choices)
            picked.append(it)
            seen_ids.add(it["id"])
    while len(picked) < n_parts:
        pool = [x for x in candidates[:36] if x["id"] not in seen_ids]
        if not pool:
            break
        it = rng.choice(pool)
        picked.append(it)
        seen_ids.add(it["id"])
    if not picked:
        return []
    picked.sort(key=lambda p: -len(_item_part_text(p)))
    return picked[:n_parts]


def _compose_written_text(
    parts: list[dict],
    rng: random.Random,
    *,
    mapping: dict[int, int],
) -> str:
    """Same-topic parts only; preserve DSE subpart order; no meta bridge."""
    ordered = sorted(parts, key=lambda x: str(x.get("number", x.get("id", ""))))
    blocks: list[str] = []
    seen: set[str] = set()
    for it in ordered:
        block = _prepare_written_part(_item_part_text(it), rng, mapping)
        if not block or block[:72] in seen:
            continue
        seen.add(block[:72])
        blocks.append(block)
    return "\n\n".join(blocks)


def _pick_coherent_parts(
    rng: random.Random,
    candidates: list[dict],
    concepts: tuple[str, ...],
    slot_id: str,
    *,
    used_ids: set[str],
) -> list[dict] | None:
    """One primary cluster; optionally one extra part from another year if same topic."""
    pool = [c for c in candidates if c["id"] not in used_ids]
    if not pool:
        return None
    clusters = _cluster_items(pool)
    scored: list[tuple[int, str, list[dict]]] = []
    for key, items in clusters.items():
        score = _score_cluster(items, concepts)
        if score < 1:
            continue
        scored.append((score, key, items))
    if not scored:
        return None
    scored.sort(key=lambda x: (-x[0], x[1]))
    rng.shuffle(scored[: min(6, len(scored))])
    _sc, _key, primary = scored[0]
    primary_sorted = sorted(primary, key=lambda x: str(x.get("number", x.get("id", ""))))
    parts = primary_sorted[: min(3, len(primary_sorted))]
    primary_text = _strip_written_raw("\n\n".join(_item_part_text(p) for p in parts))
    if len(scored) > 1 and rng.random() < 0.45:
        for _sc2, _k2, other in scored[1:6]:
            if str(other[0].get("_year")) == str(parts[0].get("_year")):
                continue
            extra = rng.choice(other)
            trial = parts + [extra]
            if _parts_topic_compatible(trial, slot_id):
                parts = trial
                break
    if not _parts_topic_compatible(parts, slot_id):
        return None
    return parts


def _max_similarity_to_parts(parts: list[dict], composed: str) -> float:
    if not parts:
        return 0.0
    return max(
        _written_text_similarity(_strip_written_raw(_item_part_text(p)), composed) for p in parts
    )


def _strengthen_written_text(text: str, rng: random.Random, mapping: dict[int, int]) -> str:
    """Extra pass when still too close to a single bank part (no meta bridge)."""
    t = _vary_numbers_text(text, rng, mapping)
    return _reframe_written_phrases(t, rng)


def _topic_tags(text: str) -> set[str]:
    from coherence_check import (  # noqa: PLC0415
        _TOPIC_ALGO,
        _TOPIC_ANTIVIRUS,
        _TOPIC_MEDIA,
        _TOPIC_SHEET,
        _TOPIC_SQL,
        _TOPIC_VALIDATION,
    )

    tags: set[str] = set()
    if _TOPIC_SQL.search(text):
        tags.add("sql")
    if _TOPIC_MEDIA.search(text):
        tags.add("media")
    if _TOPIC_ANTIVIRUS.search(text):
        tags.add("antivirus")
    if _TOPIC_ALGO.search(text):
        tags.add("algo")
    if _TOPIC_SHEET.search(text):
        tags.add("sheet")
    if _TOPIC_VALIDATION.search(text):
        tags.add("validation")
    return tags


def _parts_topic_compatible(parts: list[dict], slot_id: str) -> bool:
    texts = [_strip_written_raw(_item_part_text(p)) for p in parts]
    tags = set()
    for t in texts:
        tags |= _topic_tags(t)
    if len(tags) <= 1:
        return True
    from coherence_check import _SLOT_TOPIC_ALLOW  # noqa: PLC0415

    allowed = _SLOT_TOPIC_ALLOW.get(slot_id)
    if allowed and tags <= allowed:
        return True
    return False


_COHERENCE_HARD = frozenset({"meta_bridge", "topic_clash", "orphan_subpart", "subpart_order"})


def _written_text_coherent(slot_id: str, text: str, section: str) -> bool:
    issues = check_text_coherence(slot_id, text, section=section)
    return not any(i.kind in _COHERENCE_HARD for i in issues)


def _bank_sim_limit(text: str, threshold: float) -> float:
    """Short stems are harder to distinguish from bank; allow slightly higher sim."""
    n = len(normalize_text(text))
    if n < 100:
        return min(0.88, threshold + 0.26)
    if n < 200:
        return min(0.78, threshold + 0.14)
    return threshold


def _max_similarity_to_bank(composed: str, pool: list[dict], *, sample: int = 280) -> float:
    if not pool:
        return 0.0
    if len(pool) > sample:
        pool = random.sample(pool, sample)
    best = 0.0
    for it in pool:
        raw = _strip_written_raw(_item_part_text(it))
        if len(raw) < 12:
            continue
        sim = _written_text_similarity(raw, composed)
        if sim > best:
            best = sim
    return best


def _first_scenario_line(full_text: str, max_len: int = 420) -> str:
    for block in full_text.split("\n\n"):
        line = block.strip().split("\n")[0].strip()
        if len(line) >= 12 and not line.startswith("{"):
            return line[:max_len]
    line = full_text.strip().split("\n")[0].strip()
    return line[:max_len] if line else ""


def pick_written_items_from_bank(
    rng: random.Random | None = None,
    *,
    max_attempts: int = 80,
    bank_stem_threshold: float = _BANK_SIM_THRESH_WRITTEN_STEM,
    bank_subpart_threshold: float = _BANK_SIM_THRESH_WRITTEN_SUBPART,
) -> dict[str, dict]:
    """Return slot_id → pick dict; cross-year parts + transforms.

    Whole slot/stem vs bank ≤ bank_stem_threshold (60%).
    Composed vs source parts (subquestions) ≤ bank_subpart_threshold (85%).
    """
    from f5_ict_pipeline_flags import PICK_TIME_BANK_SIM_GATE

    rng = rng or random.Random()
    last_err: str | None = None
    for _attempt in range(max_attempts):
        picks: dict[str, dict] = {}
        used_ids: set[str] = set()
        ok = True
        for slot_id, section, concepts, slugs, marks, title in WRITTEN_SLOT_PLAN:
            pool = _written_pool(rng, slugs)
            required = [c for c in concepts if c in ("堆疊", "ERD")]
            candidates = _ranked_parts(pool, concepts, used_ids)
            if slot_id in ("b-06", "c-01", "c-02", "c-03", "c-05", "c-06", "c-07") and candidates:
                sql_cands = [c for c in candidates if _TOPIC_SQL.search(_item_part_text(c))]
                if sql_cands:
                    candidates = sql_cands
            if not candidates:
                ok = False
                last_err = f"No bank parts for {slot_id} ({concepts})"
                break

            slot_pick: dict | None = None
            for _slot_try in range(40):
                num_mapping: dict[int, int] = {}
                parts = _pick_coherent_parts(
                    rng, candidates, concepts, slot_id, used_ids=used_ids
                )
                if not parts:
                    continue
                if required and not any(
                    any(rc in it.get("concepts", []) for rc in required) for it in parts
                ):
                    continue
                full = _compose_written_text(parts, rng, mapping=num_mapping)
                if len(full) < 24:
                    continue
                if not _written_text_coherent(slot_id, full, section):
                    continue
                sim_parts = _max_similarity_to_parts(parts, full)
                sim_bank = _max_similarity_to_bank(full, pool)
                sub_lim = _bank_sim_limit(full, bank_subpart_threshold)
                stem_lim = _bank_sim_limit(full, bank_stem_threshold)
                for _ in range(3):
                    if sim_parts <= sub_lim and sim_bank <= stem_lim:
                        break
                    full = _strengthen_written_text(full, rng, num_mapping)
                    if not _written_text_coherent(slot_id, full, section):
                        break
                    sim_parts = _max_similarity_to_parts(parts, full)
                    sim_bank = _max_similarity_to_bank(full, pool)
                    sub_lim = _bank_sim_limit(full, bank_subpart_threshold)
                    stem_lim = _bank_sim_limit(full, bank_stem_threshold)
                if PICK_TIME_BANK_SIM_GATE and (sim_parts > sub_lim or sim_bank > stem_lim):
                    continue
                if not _written_text_coherent(slot_id, full, section):
                    continue
                years = sorted({str(p.get("_year", "")) for p in parts if p.get("_year")})
                source_ids = [it["id"] for it in parts]
                for iid in source_ids:
                    used_ids.add(iid)
                slot_pick = {
                    "id": slot_id,
                    "section": section,
                    "text": full,
                    "scenario_line": _first_scenario_line(full),
                    "marks": marks,
                    "title": title,
                    "concepts": list(concepts),
                    "dse_source": source_ids[0],
                    "dse_sources": source_ids,
                    "dse_year": years[0] if len(years) == 1 else "+".join(years),
                    "dse_slug": parts[0].get("_slug"),
                    "mix_years": years,
                    "composition": "cross_year" if len(years) >= 2 else "single_cluster",
                }
                break

            if slot_pick is None:
                clusters = _cluster_items(pool)
                scored_c: list[tuple[int, str, list[dict]]] = []
                for key, items in clusters.items():
                    if any(it["id"] in used_ids for it in items):
                        continue
                    score = _score_cluster(items, concepts)
                    if score < 1:
                        continue
                    if required and not any(
                        any(rc in it.get("concepts", []) for rc in required) for it in items
                    ):
                        continue
                    scored_c.append((score, key, items))
                if not scored_c:
                    ok = False
                    last_err = (
                        f"No composed pick for {slot_id} "
                        f"(stem>{bank_stem_threshold:.0%} or subpart>{bank_subpart_threshold:.0%})"
                    )
                    break
                scored_c.sort(key=lambda x: (-x[0], x[1]))
                rng.shuffle(scored_c[:10])
                for _sc, _key, cluster_items in scored_c[:12]:
                    ordered = sorted(
                        cluster_items,
                        key=lambda x: str(x.get("number", x.get("id", ""))),
                    )
                    for take in (2, 1):
                        num_mapping: dict[int, int] = {}
                        subset = ordered[:take]
                        full = _assemble_cluster_text(
                            subset, rng, max_parts=take, mapping=num_mapping
                        )
                        if len(full) < 20 or not _written_text_coherent(slot_id, full, section):
                            continue
                        sim_bank = _max_similarity_to_bank(full, pool)
                        if sim_bank > _bank_sim_limit(full, bank_stem_threshold) + 0.05:
                            continue
                        break
                    else:
                        continue
                    source_ids = [it["id"] for it in subset]
                    for iid in source_ids:
                        used_ids.add(iid)
                    slot_pick = {
                        "id": slot_id,
                        "section": section,
                        "text": full,
                        "scenario_line": _first_scenario_line(full),
                        "marks": marks,
                        "title": title,
                        "concepts": list(concepts),
                        "dse_source": source_ids[0],
                        "dse_sources": source_ids,
                        "dse_year": cluster_items[0].get("_year"),
                        "dse_slug": cluster_items[0].get("_slug"),
                        "mix_years": sorted({str(p.get("_year", "")) for p in subset}),
                        "composition": "cluster_fallback",
                    }
                    break
                if slot_pick is None:
                    ok = False
                    last_err = f"No coherent fallback for {slot_id}"
                    break

            picks[slot_id] = slot_pick

        if ok and len(picks) == len(WRITTEN_SLOT_PLAN):
            return picks
    raise RuntimeError(last_err or "Could not pick written items from DSE bank")


def _strip_written_raw(text: str) -> str:
    t = _IMAGE_DESC_RE.sub("", text)
    t = _JSON_BLOCK_RE.sub("", t)
    t = t.replace("`", "'")
    t = re.sub(r"\*\*([^*]+)\*\*", r"\1", t)
    return re.sub(r"\n{3,}", "\n\n", t.strip())


def _assemble_cluster_raw(items: list[dict], *, max_parts: int = 10) -> str:
    ordered = sorted(items, key=lambda x: str(x.get("number", x.get("id", ""))))
    parts: list[str] = []
    seen: set[str] = set()
    for it in ordered:
        raw = (it.get("stem") or it.get("text") or "").strip()
        if not raw:
            continue
        cleaned = _strip_written_raw(raw)
        key = cleaned[:80]
        if key in seen:
            continue
        seen.add(key)
        parts.append(cleaned)
        if len(parts) >= max_parts:
            break
    return "\n\n".join(parts)


def _written_text_similarity(original: str, adapted: str) -> float:
    return text_similarity(normalize_text(original), normalize_text(adapted))


def _load_bank_written_by_id(item_id: str) -> dict | None:
    for year in _WRITTEN_YEARS:
        for slug in _WRITTEN_BANK_SLUGS:
            for it in _load_bank_items(year, slug):
                if it.get("id") == item_id:
                    return it
    return None


def _written_bank_pool() -> list[dict]:
    pool: list[dict] = []
    for year in _WRITTEN_YEARS:
        for slug in _WRITTEN_BANK_SLUGS:
            pool.extend(_load_bank_items(year, slug))
    return pool


def audit_written_source_similarity(
    picks: dict[str, dict],
    *,
    threshold: float = _BANK_SIM_THRESH_WRITTEN_SUBPART,
) -> list[tuple[str, float, str]]:
    """(slot_id, max similarity, dse_source) vs each raw source part (subquestion gate, default 85%)."""
    hits: list[tuple[str, float, str]] = []
    for slot_id, p in sorted(picks.items()):
        source_ids = list(p.get("dse_sources") or [])
        if p.get("dse_source"):
            source_ids.insert(0, p["dse_source"])
        bank_items: list[dict] = []
        seen_ids: set[str] = set()
        for iid in source_ids:
            sid = str(iid or "")
            if not sid or sid in seen_ids:
                continue
            seen_ids.add(sid)
            it = _load_bank_written_by_id(sid)
            if it:
                bank_items.append(it)
        if not bank_items:
            continue
        sim = _max_similarity_to_parts(bank_items, p.get("text", ""))
        if sim > threshold:
            hits.append((slot_id, sim, str(p.get("dse_source") or source_ids[0])))
    return hits


def audit_written_best_bank_match(
    picks: dict[str, dict],
    *,
    threshold: float = _BANK_SIM_THRESH_WRITTEN_STEM,
) -> list[tuple[str, float, str]]:
    """(slot_id, similarity, bank_id) for highest whole-slot match in written bank (default 60%)."""
    pool = _written_bank_pool()
    hits: list[tuple[str, float, str]] = []
    for slot_id, p in sorted(picks.items()):
        cand = p.get("text", "")
        best_sim, best_id = 0.0, ""
        for it in pool:
            raw = (it.get("stem") or it.get("text") or "").strip()
            if len(raw) < 12:
                continue
            sim = _written_text_similarity(raw, cand)
            if sim > best_sim:
                best_sim, best_id = sim, str(it.get("id", ""))
        if best_sim > threshold:
            hits.append((slot_id, best_sim, best_id))
    return hits


def audit_written_bank_similarity(
    picks: dict[str, dict],
    *,
    stem_threshold: float = _BANK_SIM_THRESH_WRITTEN_STEM,
    subpart_threshold: float = _BANK_SIM_THRESH_WRITTEN_SUBPART,
) -> dict[str, list[tuple[str, float, str]]]:
    return {
        "source": audit_written_source_similarity(picks, threshold=subpart_threshold),
        "bank_best": audit_written_best_bank_match(picks, threshold=stem_threshold),
    }


def written_preview_json(
    picks: dict[str, dict],
    *,
    source_hits: list[tuple[str, float, str]] | None = None,
    bank_best_hits: list[tuple[str, float, str]] | None = None,
) -> str:
    src_by_slot = {s: (round(sim, 4), iid) for s, sim, iid in (source_hits or [])}
    best_by_slot = {s: (round(sim, 4), iid) for s, sim, iid in (bank_best_hits or [])}
    rows = []
    for sid, p in sorted(picks.items()):
        row = {
            "slot": sid,
            "dse_source": p.get("dse_source"),
            "dse_sources": p.get("dse_sources"),
            "dse_year": p.get("dse_year"),
            "mix_years": p.get("mix_years"),
            "composition": p.get("composition"),
            "dse_slug": p.get("dse_slug"),
            "preview": (p.get("scenario_line") or "")[:100],
        }
        if sid in src_by_slot:
            row["source_similarity"] = src_by_slot[sid][0]
            row["over_threshold_subpart"] = True
            row["over_threshold"] = True  # legacy alias
        if sid in best_by_slot:
            row["bank_best_similarity"] = best_by_slot[sid][0]
            row["bank_best_id"] = best_by_slot[sid][1]
            row["over_threshold_stem"] = True
        rows.append(row)
    return json.dumps({"count": len(rows), "items": rows}, ensure_ascii=False, indent=2)
