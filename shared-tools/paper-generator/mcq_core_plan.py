"""MCQ slot plan: Core A → B → D blocks + EDB-ordered concept tags per slot."""
from __future__ import annotations

from pathlib import Path

# 30 slots: Core A (10) → Core B (10) → Core D (10)
MCQ_CORE_SEQUENCE: tuple[str, ...] = ("A",) * 10 + ("B",) * 10 + ("D",) * 10

# Concepts that belong to elective EC (Module C) — not compulsory 甲部 MCQ targets
ELECTIVE_EC_CONCEPTS: frozenset[str] = frozenset(
    {
        "堆疊",
        "佇列",
        "鏈列",
        "鏈表",
        "遞歸",
        "動態規劃",
        "圖形化編程",
    }
)

# Map concept tags → unit (A/B/D compulsory, EC/EA elective)
CONCEPT_TO_CORE: dict[str, str] = {
    # A — 資訊處理 (topics A-a … A-d)
    "資訊處理": "A",
    "數據與資訊": "A",
    "資訊處理循環": "A",
    "輸入處理輸出": "A",
    "批次處理": "A",
    "數據組織": "A",
    "欄位": "A",
    "記錄": "A",
    "檔案存取": "A",
    "直接存取": "A",
    "順序存取": "A",
    "有效性檢驗": "A",
    "奇偶檢測": "A",
    "數據控制": "A",
    "進制": "A",
    "十六進制": "A",
    "二進制補碼": "A",
    "字元編碼": "A",
    "UTF-8": "A",
    "多媒體": "A",
    "音訊": "A",
    "音訊檔案大小": "A",
    "點陣圖": "A",
    "向量圖": "A",
    "壓縮": "A",
    "顏色深度": "A",
    "影片檔案大小": "A",
    "試算表": "A",
    "VLOOKUP": "A",
    "COUNTIF": "A",
    "SUMIF": "A",
    "RANK": "A",
    "XLOOKUP": "A",
    "文書處理": "A",
    "演示軟件": "A",
    "SQL": "A",
    # B — 電腦系統基礎 (B-a, B-b)
    "硬件": "B",
    "快取記憶體": "B",
    "SSD": "B",
    "RAM": "B",
    "輸入裝置": "B",
    "輸出裝置": "B",
    "軟件": "B",
    "實用程式": "B",
    "作業系統": "B",
    "專用軟件": "B",
    "驅動程式": "B",
    # D — 計算思維與程式編寫 (D-a … D-d, compulsory only)
    "問題分析": "D",
    "子問題": "D",
    "算法": "D",
    "偽代碼": "D",
    "流程圖": "D",
    "迴圈": "D",
    "迭代": "D",
    "排序": "D",
    "搜尋": "D",
    "線性搜尋": "D",
    "陣列": "D",
    "變量": "D",
    "模組": "D",
    "程式測試": "D",
    "除錯": "D",
    "邊界值": "D",
    "語法錯誤": "D",
    "邏輯錯誤": "D",
    "二進制": "D",
    "布爾邏輯": "D",
    # EC — 選修算法與程式編寫 (Module C; not 甲部 MCQ)
    "堆疊": "EC",
    "佇列": "EC",
    "鏈列": "EC",
    "鏈表": "EC",
}


def _curriculum_path() -> Path:
    return (
        Path(__file__).resolve().parents[2]
        / "Subjects/DSE-ICT/question-bank/curriculum_concepts.json"
    )


# Slot plan: (core, concept keywords) — order follows EDB C&A Guide topic sequence
# See curriculum_concepts.json → mcq_compulsory_slot_order
MCQ_SLOT_PLAN: tuple[tuple[str, tuple[str, ...]], ...] = (
    # Core A ×10 (A-a → A-b → A-c → A-d)
    ("A", ("資訊處理", "數據與資訊", "資訊處理循環")),
    ("A", ("資訊處理", "輸入處理輸出", "批次處理")),
    ("A", ("數據組織", "欄位", "記錄")),
    ("A", ("數據組織", "檔案存取", "直接存取")),
    ("A", ("數據控制", "有效性檢驗", "奇偶檢測")),
    ("A", ("進制", "十六進制", "二進制補碼")),
    ("A", ("字元編碼", "UTF-8")),
    ("A", ("多媒體", "點陣圖", "向量圖")),
    ("A", ("多媒體", "壓縮", "顏色深度")),
    ("A", ("試算表", "XLOOKUP", "COUNTIF", "SUMIF", "RANK", "IF")),
    # Core B ×10 (B-a → B-b)
    ("B", ("硬件", "RAM", "快取記憶體")),
    ("B", ("硬件", "SSD")),
    ("B", ("硬件", "輸入裝置")),
    ("B", ("硬件", "RAM", "快取記憶體")),
    ("B", ("硬件", "SSD", "輸出裝置")),
    ("B", ("軟件", "作業系統", "驅動程式")),
    ("B", ("軟件", "實用程式")),
    ("B", ("軟件", "專用軟件")),
    ("B", ("軟件", "作業系統", "實用程式")),
    ("B", ("硬件", "輸入裝置", "RAM")),
    # Core D ×10 (D-a → D-b → D-c → D-d); no 堆疊 (EC elective)
    ("D", ("問題分析", "算法", "子問題")),
    ("D", ("算法", "偽代碼", "流程圖")),
    ("D", ("迴圈", "算法", "迭代")),
    ("D", ("排序", "算法", "陣列")),
    ("D", ("搜尋", "算法", "線性搜尋")),
    ("D", ("算法", "陣列", "變量")),
    ("D", ("進制", "二進制", "布爾邏輯")),
    ("D", ("程式測試", "除錯", "邊界值")),
    ("D", ("程式測試", "語法錯誤", "邏輯錯誤")),
    ("D", ("算法", "偽代碼", "模組")),
)

MCQ_SLOT_CONCEPTS: tuple[list[str], ...] = tuple(list(c) for _, c in MCQ_SLOT_PLAN)


def compulsory_cores_for_item(concepts: list[str], curriculum_unit: str = "") -> set[str]:
    """Cores A/B/D matched by concept tags (excludes EC elective-only tags as sole match)."""
    tagged: set[str] = set()
    for c in concepts:
        unit = CONCEPT_TO_CORE.get(c)
        if unit in ("A", "B", "D"):
            tagged.add(unit)
    if "B-" in curriculum_unit or "電腦系統" in curriculum_unit:
        tagged.add("B")
    if "D-" in curriculum_unit or "計算思維" in curriculum_unit:
        tagged.add("D")
    if "A-" in curriculum_unit or "資訊處理" in curriculum_unit:
        tagged.add("A")
    # Drop D match if item is EC-data-structure only (e.g. 堆疊 with no algo tag)
    ec_hits = {c for c in concepts if c in ELECTIVE_EC_CONCEPTS or CONCEPT_TO_CORE.get(c) == "EC"}
    if ec_hits and "算法" not in concepts and "偽代碼" not in concepts:
        tagged.discard("D")
    return tagged


def cores_for_item(concepts: list[str], curriculum_unit: str = "") -> set[str]:
    out = compulsory_cores_for_item(concepts, curriculum_unit)
    for c in concepts:
        if CONCEPT_TO_CORE.get(c) == "EC":
            out.add("EC")
    return out


def item_matches_core(item: dict, core: str) -> bool:
    if core not in ("A", "B", "D"):
        return False
    return core in compulsory_cores_for_item(
        item.get("concepts") or [],
        item.get("curriculum_unit") or "",
    )


def verify_core_sequence(sequence: tuple[str, ...] | list[str]) -> list[str]:
    """Return error messages if core order is not A block → B block → D block."""
    errors: list[str] = []
    expected = MCQ_CORE_SEQUENCE
    if len(sequence) != len(expected):
        errors.append(f"Expected {len(expected)} MCQ cores, got {len(sequence)}")
    for i, (exp, got) in enumerate(zip(expected, sequence, strict=False), start=1):
        if exp != got:
            errors.append(f"MCQ-{i:02d}: expected Core {exp}, got Core {got}")
    return errors
