"""Build F5 ICT blueprint exam spec (JSON) before DOCX render."""
from __future__ import annotations

import sys
from pathlib import Path

_COMPARE = Path(__file__).resolve().parents[1] / "question-quality-check"
if str(_COMPARE) not in sys.path:
    sys.path.insert(0, str(_COMPARE))

from exam_spec import build_spec, make_item

# Correct option index (0=A … 3=D) per MCQ 1–30 — must match build_mcq_payload() order.
F5_MCQ_CORRECT_INDEX: tuple[int, ...] = (
    0, 0, 1, 1, 1, 3, 0, 1, 1, 0, 2, 1, 3, 1, 2, 3, 1, 0, 1, 1, 3, 3, 1, 1, 3, 1, 1, 3, 0, 3,
)

MCQ_CONCEPTS: tuple[list[str], ...] = (
    ["進制", "十六進制"],
    ["進制", "二進制補碼"],
    ["字元編碼", "UTF-8"],
    ["多媒體", "音訊檔案大小"],
    ["試算表", "VLOOKUP"],
    ["試算表", "COUNTIFS"],
    ["硬件", "快取記憶體"],
    ["硬件", "SSD"],
    ["軟件", "實用程式"],
    ["多媒體", "點陣圖"],
    ["多媒體", "壓縮"],
    ["數據庫", "1NF"],
    ["數據控制", "有效性檢驗"],
    ["資訊處理", "數據與資訊"],
    ["算法", "迴圈"],
    ["算法", "排序"],
    ["數據組織", "記錄"],
    ["算法", "冒泡排序"],
    ["數據結構", "隊列"],
    ["數據組織", "檔案存取"],
    ["數據庫", "主鍵"],
    ["數據庫", "外鍵"],
    ["算法", "陣列"],
    ["算法", "追蹤"],
    ["數據庫", "正規化"],
    ["算法", "搜尋"],
    ["程式設計", "模組化"],
    ["數據結構", "堆疊"],
    ["程式設計", "函數"],
    ["數據庫", "SQL"],
)


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
            slice_text(313, 321),
            marks=10,
            title="試算表",
            concepts=["試算表", "IF", "樞紐分析表"],
        ),
        make_item(
            "b-02",
            "section_b",
            slice_text(323, 334),
            marks=10,
            title="數據控制與私隱",
            concepts=["有效性檢驗", "檔案存取", "數據私隱"],
        ),
        make_item(
            "b-03",
            "section_b",
            slice_text(336, 345),
            marks=10,
            title="算法追蹤",
            concepts=["偽代碼", "陣列", "次大值"],
        ),
    ]


def _part_c_items(build_part_c) -> list[dict]:
    all_lines = build_part_c()
    base = 423

    def slice_text(start: int, end: int) -> str:
        return _join_lines(all_lines[start - base : end - base + 1])

    return [
        make_item(
            "c-db",
            "section_c",
            slice_text(423, 455),
            marks=20,
            title="選修A 數據庫",
            concepts=["ERD", "SQL", "數據庫"],
        ),
        make_item(
            "c-norm",
            "section_c",
            slice_text(457, 470),
            marks=10,
            title="正規化與資料完整性",
            concepts=["正規化", "1NF", "更新異常"],
        ),
        make_item(
            "c-sql-adv",
            "section_c",
            slice_text(482, 492),
            marks=10,
            title="進階 SQL",
            concepts=["SQL", "GROUP BY", "UPDATE"],
        ),
    ]


def build_f5_ict_exam_spec(
    *,
    mcq_rows: list[list[str]] | None = None,
    mcq_answers: str | None = None,
) -> dict:
    from f5_ict_blueprint_db_web import build_mcq_payload, build_part_b, build_part_c

    rows = mcq_rows if mcq_rows is not None else build_mcq_payload()
    items: list[dict] = []
    for i, row in enumerate(rows, start=1):
        answer = mcq_answers[i - 1] if mcq_answers and i <= len(mcq_answers) else None
        concepts = list(MCQ_CONCEPTS[i - 1]) if i <= len(MCQ_CONCEPTS) else []
        items.append(
            make_item(
                f"mcq-{i:02d}",
                "mcq",
                _join_lines(row),
                marks=1,
                concepts=concepts,
                answer=answer,
            )
        )
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
        "concept_targets": {
            "數據庫": {"min": 6, "max": 12},
            "算法": {"min": 5, "max": 12},
            "試算表": {"min": 2, "max": 6},
            "數據控制": {"min": 1, "max": 4},
        },
    }
    if mcq_answers:
        meta["mcq_answers"] = mcq_answers
    return build_spec(meta, items)
