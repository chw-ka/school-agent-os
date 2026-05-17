"""Build F5 ICT blueprint exam spec (JSON) before DOCX render."""
from __future__ import annotations

import sys
from pathlib import Path

# question-quality-check on path (exam spec schema)
_COMPARE = Path(__file__).resolve().parents[1] / "question-quality-check"
if str(_COMPARE) not in sys.path:
    sys.path.insert(0, str(_COMPARE))

from exam_spec import build_spec, make_item


def _join_lines(lines: list[str]) -> str:
    return "\n".join(x for x in lines if x is not None).strip()


def _part_b_items(build_part_b) -> list[dict]:
    """Logical 乙部 units aligned with generator content."""
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
            title="網絡與保安",
            concepts=["WPA3", "VPN", "網絡安全"],
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
            "c-web-1",
            "section_c",
            slice_text(457, 470),
            marks=10,
            title="選修B 註冊表單",
            concepts=["客戶端驗證", "伺服器端驗證", "HTTP"],
        ),
        make_item(
            "c-web-2",
            "section_c",
            slice_text(482, 492),
            marks=10,
            title="選修B BMI",
            concepts=["CSS", "JavaScript", "網頁開發"],
        ),
    ]


def build_f5_ict_exam_spec() -> dict:
    from f5_ict_blueprint_db_web import build_mcq_payload, build_part_b, build_part_c

    items: list[dict] = []
    for i, row in enumerate(build_mcq_payload(), start=1):
        items.append(make_item(f"mcq-{i:02d}", "mcq", _join_lines(row), marks=1))
    items.extend(_part_b_items(build_part_b))
    items.extend(_part_c_items(build_part_c))
    return build_spec(
        {
            "title": "F5 ICT Exam02 Blueprint (Database + Web)",
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
        },
        items,
    )
