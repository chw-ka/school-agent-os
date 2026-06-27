"""MS Forms scoring helpers for Python & AI (PAI) assignments.

All paths are resolved relative to the working directory (the subject's marking/ dir).
"""

import json
import re
import urllib.error
import urllib.request
from pathlib import Path

import pandas as pd

# CWD-relative paths — resolved at call time so scripts can run from any marking/ dir.
STUID_MAP_PATH = Path("records") / "stuid_class_map.json"
STUDENT_DATA_PATH = Path("student_data") / "student_data.csv"

# Default path for Ch4T1 Forms responses (override by passing forms_path to load_ch4t1_forms_scores).
CH4T1_FORMS_PATH = (
    Path("task_info") / "Python與人工智能_第四章_任務一"
    / "第四章 OpenCV 物件追蹤 (Object Tracking)(1-100).xlsx"
)

CH4T1_SPEED_COLS = ["BOOSTING", "MIL", "KCF", "TLD", "MEDIANFLOW", "MOSSE", "CSRT"]
CH4T1_STAB_COLS = [f"{name}2" for name in CH4T1_SPEED_COLS]
CH4T1_OCC_COLS = [f"{name}3" for name in CH4T1_SPEED_COLS]

_SPEED_VALUES = {"慢", "一般", "快"}
_OCC_VALUES = {"跟緊", "跟丟"}


def _fetch_stuid_map_from_api():
    mapping = {}
    for class_name in ("3A", "3B", "3C", "3D"):
        url = f"http://127.0.0.1:8000/students?class_name={class_name}&limit=50"
        with urllib.request.urlopen(url, timeout=5) as resp:
            students = json.load(resp)
        for student in students:
            mapping[str(student["stuid"])] = {
                "class": student["class"],
                "number": student["number"],
            }
    return mapping


def _load_stuid_map_from_student_data():
    if not STUDENT_DATA_PATH.exists():
        return {}
    df = pd.read_csv(STUDENT_DATA_PATH, dtype={"class": str, "number": int, "stuid": int})
    return {
        str(int(row["stuid"])): {"class": row["class"], "number": int(row["number"])}
        for _, row in df.iterrows()
    }


def load_stuid_class_map():
    if STUID_MAP_PATH.exists():
        with open(STUID_MAP_PATH, encoding="utf-8") as f:
            return json.load(f)
    if STUDENT_DATA_PATH.exists():
        return _load_stuid_map_from_student_data()
    try:
        mapping = _fetch_stuid_map_from_api()
        STUID_MAP_PATH.parent.mkdir(exist_ok=True)
        with open(STUID_MAP_PATH, "w", encoding="utf-8") as f:
            json.dump(mapping, f, ensure_ascii=False, indent=2)
        return mapping
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return {}


_INDEX_RE = re.compile(r"^3[A-D]\d{2}$")


def student_index(class_name, classnumber):
    if class_name is None or classnumber is None:
        return None
    if pd.isna(class_name) or pd.isna(classnumber):
        return None

    class_name = str(class_name).strip()
    text = str(classnumber).strip()
    if text.isdigit():
        number = int(text)
    else:
        match = re.match(r"^0*(\d+)", text)
        if not match:
            return None
        number = int(match.group(1))

    if not class_name or number <= 0:
        return None

    key = f"{class_name}{number:02d}"
    return key if _INDEX_RE.match(key) else None


def resolve_student_key(row):
    key = student_index(row.get("class"), row.get("classnumber"))
    if key:
        return key
    index = str(row.get("index", "")).strip()
    if _INDEX_RE.match(index):
        return index
    filepath = row.get("filepath")
    if filepath is not None and not (isinstance(filepath, float) and pd.isna(filepath)):
        match = re.match(r"^(3[A-D]\d{2})", Path(str(filepath)).name)
        if match:
            return match.group(1)
    return None


def _cell_filled(value):
    return pd.notna(value) and str(value).strip() != ""


def _count_section(row, cols, valid_fn):
    return sum(
        1 for col in cols
        if col in row.index and _cell_filled(row[col]) and valid_fn(row[col])
    )


def _stab_valid(value):
    text = str(value).strip()
    if text in {"1", "2", "3", "4", "5"}:
        return True
    try:
        return 1 <= int(float(value)) <= 5
    except (TypeError, ValueError):
        return False


def score_ch4t1_forms_row(row):
    """Return (marks, comments) for one MS Forms response row."""
    speed_n = _count_section(row, CH4T1_SPEED_COLS, lambda v: str(v).strip() in _SPEED_VALUES)
    stab_n = _count_section(row, CH4T1_STAB_COLS, _stab_valid)
    occ_n = _count_section(row, CH4T1_OCC_COLS, lambda v: str(v).strip() in _OCC_VALUES)

    speed_marks = round(3 * speed_n / 7)
    stab_marks = round(4 * stab_n / 7)
    occ_marks = round(3 * occ_n / 7)
    total = speed_marks + stab_marks + occ_marks

    comments = (
        "[O]: Correct\n[-]: Minor error\n[X]: Major error\n\n"
        f"[O] MS Forms 執行速度 ({speed_marks}/3)：{speed_n}/7 項\n"
        f"[O] MS Forms 追蹤穩定度 ({stab_marks}/4)：{stab_n}/7 項\n"
        f"[O] MS Forms 遮擋表現 ({occ_marks}/3)：{occ_n}/7 項\n"
    )
    if total < 10:
        comments += "[-] 部分欄位未填寫或格式不正確\n"
    return total, comments


def load_ch4t1_forms_scores(forms_path=None):
    """Load Ch4T1 marks keyed by student index (e.g. 3B05)."""
    forms_path = Path(forms_path) if forms_path else CH4T1_FORMS_PATH
    if not forms_path.exists():
        return {}

    stuid_map = load_stuid_class_map()
    df = pd.read_excel(forms_path)
    scores = {}
    for _, row in df.iterrows():
        email = str(row.get("Email", "")).strip().lower()
        match = re.match(r"(\d+)@", email)
        if not match:
            continue
        info = stuid_map.get(match.group(1))
        if not info:
            continue
        marks, comments = score_ch4t1_forms_row(row)
        key = student_index(info["class"], info["number"])
        scores[key] = (marks, comments)
    return scores
