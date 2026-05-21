"""Build F5 ICT blueprint exam spec (JSON) before DOCX render."""
from __future__ import annotations

import sys
from pathlib import Path

_COMPARE = Path(__file__).resolve().parents[1] / "question-quality-check"
if str(_COMPARE) not in sys.path:
    sys.path.insert(0, str(_COMPARE))

from dse_ict_style import style_meta
from exam_spec import build_spec, make_item

# Correct option index (0=A … 3=D) per MCQ 1–30 — must match build_mcq_payload() order.
F5_MCQ_CORRECT_INDEX: tuple[int, ...] = (
    0, 0, 1, 1, 1, 2, 0, 1, 1, 0, 2, 0, 0, 1, 1, 2, 2, 0, 1, 1, 2, 3, 0, 1, 1, 0, 1, 3, 0, 2,
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
    ["數據組織", "欄位"],
    ["數據控制", "有效性檢驗"],
    ["資訊處理", "數據與資訊"],
    ["硬件", "RAM"],
    ["硬件", "輸入裝置"],
    ["數據組織", "記錄"],
    ["數據控制", "奇偶檢測"],
    ["資訊處理", "批次處理"],
    ["數據組織", "檔案存取"],
    ["多媒體", "向量圖"],
    ["軟件", "作業系統"],
    ["資訊處理", "輸入處理輸出"],
    ["多媒體", "影片檔案大小"],
    ["數據組織", "檔案存取"],
    ["軟件", "專用軟件"],
    ["多媒體", "顏色深度"],
    ["多媒體", "音訊"],
    ["進制", "二進制"],
    ["資訊處理", "資訊處理循環"],
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
            slice_text(313, 322),
            marks=4,
            title="試算表",
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
            title="多媒體與檔案傳送",
            concepts=["多媒體", "檔案大小", "網絡傳輸"],
        ),
        make_item(
            "b-04",
            "section_b",
            slice_text(354, 376),
            marks=4,
            title="算法追蹤",
            concepts=["算法", "偽代碼", "陣列"],
        ),
        make_item(
            "b-05",
            "section_b",
            slice_text(377, 393),
            marks=4,
            title="檔案存取",
            concepts=["檔案存取", "直接存取", "順序存取"],
        ),
        make_item(
            "b-06",
            "section_b",
            slice_text(394, 422),
            marks=9,
            title="網上商店與 SQL",
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
            title="ERD",
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
            "c-04",
            "section_c",
            slice_text(482, 495),
            marks=3,
            title="第三範式",
            concepts=["數據庫", "正規化", "3NF"],
        ),
        make_item(
            "c-05",
            "section_c",
            slice_text(496, 540),
            marks=11,
            title="ROOM / BOOKING",
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
            title="交易控制",
            concepts=["數據庫", "Transaction", "COMMIT", "ROLLBACK"],
        ),
        make_item(
            "c-08",
            "section_c",
            slice_text(595, 624),
            marks=6,
            title="點名資料庫",
            concepts=["數據庫", "SQL", "算法"],
        ),
    ]


def build_f5_ict_exam_spec(
    *,
    mcq_rows: list[list[str]] | None = None,
    mcq_answers: str | None = None,
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
        **style_meta(),
        "concept_targets": {
            "數據庫": {"min": 3, "max": 12},
            "算法": {"min": 1, "max": 10},
            "試算表": {"min": 2, "max": 6},
            "數據控制": {"min": 2, "max": 6},
            "多媒體": {"min": 4, "max": 10},
        },
    }
    if mcq_answers:
        meta["mcq_answers"] = mcq_answers
    return build_spec(meta, items)
