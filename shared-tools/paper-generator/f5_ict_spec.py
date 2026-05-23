"""Build F5 ICT blueprint exam spec (JSON) before DOCX render."""
from __future__ import annotations

import sys
from pathlib import Path

_COMPARE = Path(__file__).resolve().parents[1] / "question-quality-check"
if str(_COMPARE) not in sys.path:
    sys.path.insert(0, str(_COMPARE))

from dse_ict_style import style_meta
from exam_spec import build_spec, make_item
from mcq_core_plan import MCQ_SLOT_CONCEPTS as MCQ_CONCEPTS
from mcq_core_plan import MCQ_CORE_SEQUENCE, MCQ_SLOT_PLAN


def _join_lines(lines: list[str]) -> str:
    return "\n".join(x for x in lines if x is not None).strip()


def _part_b_items(build_part_b) -> list[dict]:
    all_lines = build_part_b()
    base = 313

    def slice_text(start: int, end: int) -> str:
        return _join_lines(all_lines[start - base : end - base + 1])

    return [
        make_item(
            "b-01",
            "section_b",
            slice_text(313, 322),
            marks=4,
            title="試算表（義賣）",
            concepts=["試算表", "IF", "COUNTIFS"],
        ),
        make_item(
            "b-02",
            "section_b",
            slice_text(323, 335),
            marks=5,
            title="數據有效性",
            concepts=["有效性檢驗", "奇偶檢測"],
        ),
        make_item(
            "b-03",
            "section_b",
            slice_text(336, 353),
            marks=4,
            title="多媒體檔案大小",
            concepts=["多媒體", "點陣圖", "壓縮"],
        ),
        make_item(
            "b-04",
            "section_b",
            slice_text(354, 376),
            marks=4,
            title="線性搜尋",
            concepts=["算法", "偽代碼", "陣列"],
        ),
        make_item(
            "b-05",
            "section_b",
            slice_text(377, 393),
            marks=4,
            title="索引檔存取",
            concepts=["檔案存取", "直接存取", "順序存取"],
        ),
        make_item(
            "b-06",
            "section_b",
            slice_text(394, 422),
            marks=9,
            title="網店訂單與 SQL",
            concepts=["數據庫", "SQL", "有效性檢驗", "資料類型"],
        ),
    ]


def _part_c_items(build_part_c) -> list[dict]:
    all_lines = build_part_c()
    base = 423

    def slice_text(start: int, end: int) -> str:
        return _join_lines(all_lines[start - base : end - base + 1])

    return [
        make_item(
            "c-01",
            "section_c",
            slice_text(425, 439),
            marks=4,
            title="戲院預訂 ERD",
            concepts=["ERD", "數據庫"],
        ),
        make_item(
            "c-02",
            "section_c",
            slice_text(440, 456),
            marks=2,
            title="CREATE / INSERT",
            concepts=["數據庫", "SQL"],
        ),
        make_item(
            "c-03",
            "section_c",
            slice_text(457, 481),
            marks=3,
            title="UNION / UPDATE",
            concepts=["數據庫", "SQL", "UNION"],
        ),
        make_item(
            "c-05",
            "section_c",
            slice_text(496, 540),
            marks=11,
            title="FACILITY / RESERVE",
            concepts=["數據庫", "SQL", "MINUS"],
        ),
        make_item(
            "c-06",
            "section_c",
            slice_text(541, 565),
            marks=5,
            title="SQL 查詢追蹤",
            concepts=["數據庫", "SQL", "JOIN", "GROUP BY"],
        ),
        make_item(
            "c-07",
            "section_c",
            slice_text(566, 594),
            marks=9,
            title="一卡通交易",
            concepts=["數據庫", "Transaction", "COMMIT", "ROLLBACK"],
        ),
        make_item(
            "c-08",
            "section_c",
            slice_text(595, 624),
            marks=6,
            title="堆疊操作",
            concepts=["算法", "堆疊", "偽代碼"],
        ),
    ]


def _written_items_from_picks(picks: dict[str, dict]) -> list[dict]:
    order = [sid for sid, *_ in __import__(
        "f5_ict_written_from_dse", fromlist=["WRITTEN_SLOT_PLAN"]
    ).WRITTEN_SLOT_PLAN]
    _fmt = Path(__file__).resolve().parents[1] / "paper-formatter"
    if str(_fmt) not in sys.path:
        sys.path.insert(0, str(_fmt))
    from f5_ict_written_content import build_part_b, build_part_c
    from written_picks_render import pick_slot_spec_text

    items: list[dict] = []
    for slot_id in order:
        p = picks[slot_id]
        builder = build_part_b if slot_id.startswith("b-") else build_part_c
        body = pick_slot_spec_text(p, slot_id, default_builder=builder)
        items.append(
            make_item(
                slot_id,
                p["section"],
                body,
                marks=p["marks"],
                title=p.get("title"),
                concepts=p.get("concepts"),
                dse_source=p.get("dse_source"),
                dse_sources=p.get("dse_sources"),
                mix_years=p.get("mix_years"),
                composition=p.get("composition"),
            )
        )
    return items


def build_f5_ict_exam_spec(
    *,
    mcq_rows: list[list[str]] | None = None,
    mcq_answers: str | None = None,
    mcq_provenance: list[str] | None = None,
    written_picks: dict[str, dict] | None = None,
) -> dict:
    _fmt = Path(__file__).resolve().parents[1] / "paper-formatter"
    if str(_fmt) not in sys.path:
        sys.path.insert(0, str(_fmt))
    from f5_ict_written_content import build_part_b, build_part_c

    from f5_ict_blueprint_db_web import build_mcq_payload

    rows = mcq_rows if mcq_rows is not None else build_mcq_payload()
    items: list[dict] = []
    for i, row in enumerate(rows, start=1):
        answer = mcq_answers[i - 1] if mcq_answers and i <= len(mcq_answers) else None
        core, concepts = MCQ_SLOT_PLAN[i - 1] if i <= len(MCQ_SLOT_PLAN) else ("", [])
        concepts = list(concepts)
        prov_id = (
            mcq_provenance[i - 1]
            if mcq_provenance and i - 1 < len(mcq_provenance)
            else None
        )
        item_kw: dict = {
            "marks": 1,
            "concepts": concepts,
            "core": core,
            "answer": answer,
        }
        if prov_id:
            item_kw["dse_source"] = prov_id
        items.append(make_item(f"mcq-{i:02d}", "mcq", _join_lines(row), **item_kw))
    if written_picks:
        items.extend(_written_items_from_picks(written_picks))
    else:
        items.extend(_part_b_items(build_part_b))
        items.extend(_part_c_items(build_part_c))
    meta: dict = {
        "title": "25-26 S5 ICT Exam02",
        "subject": "F5 ICT",
        "level": "S5",
        "total_marks": 100,
        "academic_year": "2025-2026",
        "footer": {
            "academic_year": "2025-2026",
            "level": "中五級",
            "term_exam": "下學期考試",
            "subject": "資訊及通訊科技",
        },
        "curriculum_units": ["Core-A", "Core-B", "Core-D", "Module-A", "Module-C"],
        "mcq_core_sequence": list(MCQ_CORE_SEQUENCE),
        "exam_structure": {
            "section_a": "MCQ — compulsory Core A/B/D only (DSE Paper 1A style)",
            "section_b": "Structured — compulsory (DSE Paper 1B style)",
            "section_c": "Structured — elective Module A + C (DSE Paper 2); no MCQ",
        },
        **style_meta(),
        "concept_targets": {
            "數據庫": {"min": 3, "max": 12},
            "算法": {"min": 8, "max": 14},
            "試算表": {"min": 2, "max": 6},
            "數據控制": {"min": 1, "max": 6},
            "多媒體": {"min": 4, "max": 10},
        },
    }
    if mcq_answers:
        meta["mcq_answers"] = mcq_answers
    if mcq_provenance:
        meta["mcq_provenance"] = list(mcq_provenance)
    return build_spec(meta, items)
