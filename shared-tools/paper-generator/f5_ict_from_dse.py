#!/usr/bin/env python3
"""
Build F5 ICT Exam02 content from DSE question-bank (2021–2025), adapt stems, emit spec + DOCX.

Filters curriculum: Core A, B, D + Elective A (DB), C (algo/programming).
Excludes Core C (networking/web) heavy items.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_BANK = _REPO / "Subjects/DSE-ICT/question-bank"
_YEARS = ("2021", "2022", "2023", "2024", "2025", "2026")

_QCHECK = Path(__file__).resolve().parents[1] / "question-quality-check"
_PDF_ENGINE = Path(__file__).resolve().parents[1] / "pdf-engine"
_FMT = Path(__file__).resolve().parents[1] / "paper-formatter"
if str(_QCHECK) not in sys.path:
    sys.path.insert(0, str(_QCHECK))
if str(_PDF_ENGINE) not in sys.path:
    sys.path.insert(0, str(_PDF_ENGINE))
if str(_FMT) not in sys.path:
    sys.path.insert(0, str(_FMT))
from quality_lib import normalize_text, text_similarity
from dse_ict_syllabus import is_syllabus_current, load_concepts_cfg
from dse_ict_support_content import mcq_support_lines as _mcq_support_lines

from dse_ict_style import COMBO_OPTS_3_ONLY
from mcq_answer_keys import sort_combination_options
from mcq_core_plan import (
    MCQ_CORE_SEQUENCE,
    MCQ_SLOT_CONCEPTS,
    MCQ_SLOT_PLAN,
    item_matches_core,
    verify_core_sequence,
)

_COMBO_OPTION_RE = re.compile(
    r"\(\d+\).*(?:只有|和|皆是|及|與)|(?:只有|和).*\(\d+\)",
    re.IGNORECASE,
)

# Re-export for f5_ict_spec / checks
__all__ = ["MCQ_SLOT_CONCEPTS", "MCQ_CORE_SEQUENCE", "MCQ_SLOT_PLAN", "build_mcq_payload_from_bank"]

# Curriculum units to include (compulsory A/B/D + elective DB + algo)
_ALLOWED_UNIT_PREFIXES = ("A-", "B-", "D-", "EA", "EC", "選修")
_EXCLUDE_NETWORK_KW = (
    "LAN", "WAN", "HTML", "CSS", "網頁", "路由器", "DNS", "HTTP", "HTTPS",
    "Wi-Fi", "802.11", "藍牙", "防火牆", "VPN", "TCP/IP", "IPv4", "IPv6", "MAC 位址",
    "交換器", "建網", "網站建構", "光纖", "網上平台", "串流視像", "網絡頻寬",
    "Mbps", "Gbps", "伺服器上載", "下載連結",
)

# vs DSE bank + school past papers: stem similarity must stay <= 60% (complaint risk)
_BANK_SIM_THRESH = 0.60
# Never ship a stem identical to the source bank item (flip-only / option shuffle)
_BANK_SIM_IDENTICAL = 0.999
# Within-exam: avoid near-duplicate stems in the same paper (stricter than bank/past ref)
_INTRA_EXAM_THRESH = 0.72

# Hand-crafted fallbacks when bank item cannot fit template span (slot index 1-based)
_FALLBACK_A: list[dict] = [
    {
        "id": "fallback-parity-a05",
        "text": "電腦接收了三組數據序列如下，每組序列包含一個奇偶檢驗，發現其中兩組序列在傳送時損壞了。\n第一組：0101 0111\n第二組：1101 0101\n第三組：1110 1011\n以下哪項最能描述此情況？\nA. 第一組和第二組 偶數\nB. 第一組和第三組 偶數\nC. 第二組和第三組 偶數\nD. 第二組和第三組 奇數",
        "options": {
            "A": "第一組和第二組 偶數",
            "B": "第一組和第三組 偶數",
            "C": "第二組和第三組 偶數",
            "D": "第二組和第三組 奇數",
        },
        "answer": "C",
        "concepts": ["奇偶檢測", "有效性檢驗", "數據控制"],
        "curriculum_unit": "A-資訊處理",
        "syllabus_status": "current",
    },
]

_FALLBACK_D: list[dict] = [
    {
        "id": "fallback-algo-d01",
        "text": "把複雜問題分解為較小子問題，在計算思維中稱為什麼？\nA. 編譯\nB. 問題分解\nC. 備份\nD. 格式化",
        "options": {"A": "編譯", "B": "問題分解", "C": "備份", "D": "格式化"},
        "answer": "B",
        "concepts": ["問題分析", "算法", "子問題"],
        "curriculum_unit": "D-計算思維與程式編寫",
    },
    {
        "id": "fallback-algo-d02",
        "text": "考慮以下迴圈結構。若計數器初值為 0，重複 4 次後計數器的值是多少？\nA. 2\nB. 3\nC. 4\nD. 5",
        "options": {"A": "2", "B": "3", "C": "4", "D": "5"},
        "answer": "C",
        "concepts": ["迴圈", "算法"],
        "curriculum_unit": "D-計算思維與程式編寫",
    },
    {
        "id": "fallback-algo-d03",
        "text": "下列哪項最能描述「問題分解」在算法設計中的作用？\nA. 合併所有子程式\nB. 把複雜問題拆成較小的子問題\nC. 刪除測試個案\nD. 增加變數數目",
        "options": {"A": "合併所有子程式", "B": "把複雜問題拆成較小的子問題", "C": "刪除測試個案", "D": "增加變數數目"},
        "answer": "B",
        "concepts": ["算法", "偽代碼"],
        "curriculum_unit": "D-計算思維與程式編寫",
    },
    {
        "id": "fallback-algo-d04",
        "text": "以冒泡排序處理陣列 [3, 1, 4, 2]，第一趟完成後陣列會變成什麼？\nA. [1, 3, 2, 4]\nB. [1, 3, 4, 2]\nC. [3, 1, 2, 4]\nD. [1, 2, 3, 4]",
        "options": {"A": "[1, 3, 2, 4]", "B": "[1, 3, 4, 2]", "C": "[3, 1, 2, 4]", "D": "[1, 2, 3, 4]"},
        "answer": "A",
        "concepts": ["排序", "算法"],
        "curriculum_unit": "D-計算思維與程式編寫",
    },
    {
        "id": "fallback-algo-d05",
        "text": "在陣列 [5, 2, 8, 2, 9] 中使用線性搜尋找 8，最少要比较多少個元素？\nA. 1\nB. 2\nC. 3\nD. 4",
        "options": {"A": "1", "B": "2", "C": "3", "D": "4"},
        "answer": "C",
        "concepts": ["搜尋", "算法"],
        "curriculum_unit": "D-計算思維與程式編寫",
    },
    {
        "id": "fallback-algo-d06",
        "text": "下列哪項是「迭代」的特徵？\nA. 函數直接呼叫自己\nB. 使用迴圈重複執行步驟\nC. 只執行一次條件判斷\nD. 不需要計數器",
        "options": {"A": "函數直接呼叫自己", "B": "使用迴圈重複執行步驟", "C": "只執行一次條件判斷", "D": "不需要計數器"},
        "answer": "B",
        "concepts": ["算法"],
        "curriculum_unit": "D-計算思維與程式編寫",
    },
    {
        "id": "fallback-algo-d07",
        "text": "考慮陣列 A[1..4] = [2, 5, 1, 8]。以線性搜尋找 5，最少要檢查多少個元素？\nA. 1\nB. 2\nC. 3\nD. 4",
        "options": {"A": "1", "B": "2", "C": "3", "D": "4"},
        "answer": "B",
        "concepts": ["搜尋", "算法", "陣列", "線性搜尋"],
        "curriculum_unit": "D-計算思維與程式編寫",
    },
    {
        "id": "fallback-algo-d08",
        "text": "編寫程式後，選擇邊界值作為測試數據的主要目的是什麼？\nA. 加快執行速度\nB. 檢查極端情況下的結果\nC. 減少變數數目\nD. 刪除錯誤訊息",
        "options": {"A": "加快執行速度", "B": "檢查極端情況下的結果", "C": "減少變數數目", "D": "刪除錯誤訊息"},
        "answer": "B",
        "concepts": ["程式測試", "算法"],
        "curriculum_unit": "D-計算思維與程式編寫",
    },
    {
        "id": "fallback-algo-d09",
        "text": "若算法中使用了 IF…ELSE 分支，下列哪項測試策略最適合？\nA. 只測試真確情況\nB. 同時測試真確和錯誤情況\nC. 刪除所有條件\nD. 只測試輸出格式",
        "options": {"A": "只測試真確情況", "B": "同時測試真確和錯誤情況", "C": "刪除所有條件", "D": "只測試輸出格式"},
        "answer": "B",
        "concepts": ["程式測試", "算法"],
        "curriculum_unit": "D-計算思維與程式編寫",
    },
    {
        "id": "fallback-algo-d10",
        "text": "下列偽代碼中，變數 total 的作用是什麼？\nA. 儲存迴圈次數\nB. 累加數值總和\nC. 輸出結果\nD. 重置計數器",
        "options": {"A": "儲存迴圈次數", "B": "累加數值總和", "C": "輸出結果", "D": "重置計數器"},
        "answer": "B",
        "concepts": ["算法", "偽代碼"],
        "curriculum_unit": "D-計算思維與程式編寫",
    },
]

_FALLBACK_A07: dict = {
    "id": "fallback-utf8-a07",
    "text": "學校網站建議採用 UTF-8 儲存中文內容，較 ASCII 更適合的主要原因是什麼？\nA. UTF-8 每個字固定 1 字節\nB. UTF-8 可表示多語言字元\nC. UTF-8 只適用於英文字\nD. UTF-8 不能顯示中文",
    "options": {
        "A": "UTF-8 每個字固定 1 字節",
        "B": "UTF-8 可表示多語言字元",
        "C": "UTF-8 只適用於英文字",
        "D": "UTF-8 不能顯示中文",
    },
    "answer": "B",
    "concepts": ["字元編碼", "UTF-8", "ASCII"],
    "curriculum_unit": "A-資訊處理",
}

_FALLBACK_A04: dict = {
    "id": "fallback-files-a04",
    "text": "學校圖書館以檔案總管開啟「有聲書」資料夾並直接點選播放，這屬於哪類檔案存取方式？\nA. 循序存取\nB. 直接存取\nC. 隨機存取\nD. 索引存取",
    "options": {"A": "循序存取", "B": "直接存取", "C": "隨機存取", "D": "索引存取"},
    "answer": "B",
    "concepts": ["數據組織", "檔案存取", "直接存取"],
    "curriculum_unit": "A-資訊處理",
}

_FALLBACK_A09: dict = {
    "id": "fallback-media-a09",
    "text": "將活動相片儲存為 JPEG 而非未壓縮 BMP，最主要考慮是什麼？\nA. 提高解像度\nB. 減少檔案大小\nC. 增加色彩深度\nD. 加長傳輸時間",
    "options": {"A": "提高解像度", "B": "減少檔案大小", "C": "增加色彩深度", "D": "加長傳輸時間"},
    "answer": "B",
    "concepts": ["多媒體", "壓縮", "點陣圖"],
    "curriculum_unit": "A-資訊處理",
}

FALLBACK_BY_SLOT: dict[int, dict] = {
    4: _FALLBACK_A04,
    5: _FALLBACK_A[0],
    7: _FALLBACK_A07,
    9: _FALLBACK_A09,
}
for _slot, _fb in zip(range(21, 31), _FALLBACK_D, strict=True):
    FALLBACK_BY_SLOT[_slot] = _fb

_SYLLABUS_CFG = load_concepts_cfg()
_SUBS = [
    (r"態表示", "能表示"),
    (r"星晴", "樂活"),
    (r"志文", "家明"),
    (r"阿文", "美玲"),
    (r"CUSTOMER", "CLIENT"),
    (r"BOOKSALE", "GOODSALE"),
    (r"Sales2023", "Order2024"),
    (r"Sales2024", "Order2025"),
    (r"2025", "2026"),
    (r"2024", "2025"),
    (r"203\.186\.200\.12", "192.168.10.50"),
    (r"school\.edu\.hk", "campus.edu.hk"),
    (r"Lee Wai Man", "Wong Ka Ming"),
    (r"Chan Mei Ling", "Lau Hoi Yan"),
    (r"Ng Ka Ho", "Cheung Tsz Kin"),
]


def _load_bank_items(year: str, slug: str) -> list[dict]:
    path = _BANK / year / slug / "questions.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("items", [])


def _unit_ok(curriculum_unit: str) -> bool:
    if not curriculum_unit:
        return True
    if "C-互聯網" in curriculum_unit:
        # allow if also tagged A/B/D
        if not any(p in curriculum_unit for p in ("A-", "B-", "D-")):
            return False
    if "E-" in curriculum_unit and "A-" not in curriculum_unit:
        return False
    return True


def _text_ok(text: str) -> bool:
    return not any(kw in text for kw in _EXCLUDE_NETWORK_KW)


def _syllabus_ok(item: dict) -> bool:
    return is_syllabus_current(item, concepts_cfg=_SYLLABUS_CFG)


def _concept_overlap(a: list[str], b: list[str]) -> int:
    sa, sb = set(a), set(b)
    direct = len(sa & sb)
    if direct:
        return direct
    if "二進制" in sb and any("二進制" in x for x in sa):
        return 1
    if "陣列" in sb and any("陣列" in x for x in sa):
        return 1
    return 0


def _slot_candidates(
    pool: list[dict],
    *,
    used_ids: set[str],
    chosen_fps: list[str],
    core: str,
    concepts: list[str],
    span: int,
    require_concepts: bool,
    require_dedup: bool,
) -> list[dict]:
    candidates: list[dict] = []
    for it in pool:
        if it["id"] in used_ids:
            continue
        if not _fits_span(it, span):
            continue
        if not _syllabus_ok(it):
            continue
        if not item_matches_core(it, core):
            continue
        if require_concepts and _concept_overlap(it.get("concepts", []), concepts) < 1:
            continue
        if require_dedup and _too_similar_to_chosen(_stem_fingerprint(it), chosen_fps):
            continue
        candidates.append(it)
    return candidates


def _adapt_text(text: str, rng: random.Random) -> str:
    out = text
    for pat, repl in _SUBS:
        out = re.sub(pat, repl, out)
    out = out.replace("```", "").strip()
    return out.strip()


# DSE exam style: keep bank phrasing; vary scenario numbers; optional cross-mix (A 問法 + B 內容).
_DIM_RE = re.compile(r"(\d+)\s*[x×]\s*(\d+)", re.IGNORECASE)
_ARRAY_RE = re.compile(r"\[([^\]]+)\]")
_INT_RE = re.compile(r"(?<![.\d^])(\d{1,4})(?![.\d^])")


def _map_int(n: int, rng: random.Random, mapping: dict[int, int]) -> int:
    if n in mapping:
        return mapping[n]
    if n <= 1:
        mapping[n] = n
        return n
    delta = rng.choice([2, 3, 4, -2, -3, -4])
    new = max(2, n + delta)
    if new == n:
        new = n + 2
    mapping[n] = new
    return new


def _vary_numbers_text(text: str, rng: random.Random, mapping: dict[int, int]) -> str:
    """Replace scenario integers (not 2^7 exponents) with consistent offsets."""
    if not text:
        return text

    def dim_sub(m: re.Match[str]) -> str:
        a, b = int(m.group(1)), int(m.group(2))
        return f"{_map_int(a, rng, mapping)}x{_map_int(b, rng, mapping)}"

    out = _DIM_RE.sub(dim_sub, text)

    def arr_sub(m: re.Match[str]) -> str:
        inner = m.group(1)
        parts = re.split(r"(\d+)", inner)
        rebuilt: list[str] = []
        for p in parts:
            if p.isdigit():
                rebuilt.append(str(_map_int(int(p), rng, mapping)))
            else:
                rebuilt.append(p)
        return "[" + "".join(rebuilt) + "]"

    out = _ARRAY_RE.sub(arr_sub, out)

    def int_sub(m: re.Match[str]) -> str:
        n = int(m.group(1))
        return str(_map_int(n, rng, mapping))

    return _INT_RE.sub(int_sub, out)


def _mcq_shape(item: dict) -> str:
    q, stmts, opts, _ = _extract_mcq_parts(item)
    if _is_combo_mcq_options(opts, stmts):
        return "combo"
    ctx = _context_lines(item, q, stmts)
    ctx_blob = "\n".join(ctx)
    if ctx and any(k in ctx_blob for k in ("←", "當 ", "重複", "算法", "輸入 N", "輸出")):
        return "algorithm"
    if stmts:
        return "statements"
    return "single"


# 是 ↔ 不是（DSE 常見改寫）
_POLARITY_FLIPS: list[tuple[str, str]] = [
    (r"以下哪個步驟是", "以下哪個步驟不是"),
    (r"以下哪一個步驟是", "以下哪一個步驟不是"),
    (r"下列哪個步驟是", "下列哪個步驟不是"),
    (r"以下哪項是", "以下哪項不是"),
    (r"下列哪項是", "下列哪項不是"),
    (r"以下哪個是", "以下哪個不是"),
    (r"以下哪一種是", "以下哪一種不是"),
    (r"下列哪一種是", "下列哪一種不是"),
    (r"以下哪些是", "以下哪些不是"),
    (r"下列哪些是", "下列哪些不是"),
    (r"哪項是", "哪項不是"),
    (r"哪個是", "哪個不是"),
    (r"是數據驗證", "不是數據驗證"),
    (r"是資料驗證", "不是資料驗證"),
    (r"是數據有效性", "不是數據有效性"),
    (r"是資料有效性", "不是資料有效性"),
    (r"是正確的", "不是正確的"),
    (r"是合理的", "不是合理的"),
    (r"是有效的", "不是有效的"),
    (r"是(.{1,12}?)(方法|步驟)", r"不是\1\2"),
]
_COMBO_Q_TEMPLATES: list[str] = [
    "{prefix}以下哪項／些是正確的？",
    "{prefix}以下哪項／些描述是正確的？",
    "{prefix}以下哪項／些是合理的？",
    "{prefix}以下哪項／些是有效的？",
]
_OPTION_FORMULA_RE = re.compile(
    r"[=+\^]|SQL|SELECT|INSERT|UPDATE|DELETE|0x[0-9A-Fa-f]|[0-9]{4}\s+[0-9]{4}",
)


def _resolve_answer_letter(
    q: str,
    opts: dict[str, str],
    ans: str | None,
    *,
    statements: list[str] | None = None,
) -> str:
    if ans and str(ans).strip() and str(ans).strip()[0] in "ABCD":
        return str(ans).strip()[0].upper()
    if statements and _is_combo_mcq_options(opts, statements):
        inferred = _infer_combo_answer_letter(q, opts, statements)
        if inferred:
            return inferred
    if "數據驗證的方法" in q or "資料驗證的方法" in q:
        for letter in "ABCD":
            if "兩次" in opts.get(letter, ""):
                return letter
    if "數據控制" in q and "這是因為" in q:
        for letter in "ABCD":
            t = opts.get(letter, "")
            if "準確" in t or "輸入數據" in t or "輸入資料" in t:
                return letter
    if "啟動" in q and ("儲存" in q or "保存" in q):
        for letter in "ABCD":
            if "ROM" in opts.get(letter, ""):
                return letter
    if "SSD" in q.upper() and re.search(r"硬碟|HDD", q, re.I):
        for letter in "ABCD":
            t = opts.get(letter, "")
            if "經常" in t:
                return letter
        for letter in "ABCD":
            t = opts.get(letter, "")
            if letter == "A" and re.search(r"讀寫|存取|速度", t):
                return letter
            if t.strip() in ("SSD", "固態硬碟"):
                return letter
    if "實時處理" in q:
        for letter in "ABCD":
            if "延遲" in opts.get(letter, ""):
                return letter
    if "最不重要" in q or "最不重要的因素" in q:
        for letter in "ABCD":
            t = opts.get(letter, "")
            if "操作系統" in t or "ROM " in t or t.strip().startswith("ROM"):
                return letter
        for letter in "ABCD":
            if "SSD" in opts.get(letter, ""):
                return letter
    return "A"


def _can_flip_polarity(question: str) -> bool:
    if "不是" in question:
        return False
    if re.search(r"(範圍|結果|輸出|目的)是什麼", question):
        return False
    return any(old in question for old, _ in _POLARITY_FLIPS)


def _flip_polarity_question(question: str) -> str:
    q = question
    for old, new in _POLARITY_FLIPS:
        if old in q:
            return q.replace(old, new, 1)
    return q


def _flip_answer_letter(correct: str, rng: random.Random) -> str:
    wrong = [L for L in "ABCD" if L != correct]
    return rng.choice(wrong)


# 「X 重要，這是因為」+ 選項「它…」→「以下哪一步驟可以…？」+ 流程名稱選項
_CAUSAL_BECAUSE_RE = re.compile(r"這是因為|这是因为")
_EXPLANATION_OPT_RE = re.compile(r"^它")
_IPC_STAGE_LABELS: tuple[str, ...] = (
    "數據控制",
    "數據收集",
    "數據分析",
    "數據儲存",
    "數據組織",
    "數據處理",
)


def _can_reframe_causal_importance(
    question: str,
    statements: list[str],
    opts: dict[str, str],
) -> bool:
    if statements or "這是因為" not in question and "这是因为" not in question:
        return False
    if not _simple_text_options(opts):
        return False
    expl = sum(1 for t in opts.values() if _EXPLANATION_OPT_RE.match(t.strip()))
    return expl >= 2


def _outcome_from_explanation(option_text: str) -> str:
    t = option_text.strip()
    if t.startswith("它"):
        t = t[1:].strip()
    return t.rstrip("。.")


def _subject_from_causal_question(question: str) -> str:
    m = re.match(r"^(.+?)對", question.strip())
    if m:
        return m.group(1).strip()
    return "數據控制"


def _reframe_causal_importance(
    question: str,
    opts: dict[str, str],
    ans: str | None,
    rng: random.Random,
) -> tuple[str, list[str], dict[str, str], str]:
    """
    例：數據控制對資訊系統非常重要，這是因為 / 選項「它確保輸入數據的準確性」
    → 以下哪一步驟可以確保輸入數據的準確性？ / A 數據控制 B 數據收集 …
    """
    resolved = _resolve_answer_letter(question, opts, ans)
    subject = _subject_from_causal_question(question)
    outcome = _outcome_from_explanation(opts.get(resolved, ""))
    if not outcome:
        outcome = "達到有關目的"

    use_data = "資料" in question or "資料" in outcome
    stages = [s.replace("數據", "資料") for s in _IPC_STAGE_LABELS] if use_data else list(_IPC_STAGE_LABELS)
    if subject not in stages:
        stages = [subject, *[s for s in stages if s != subject]]

    new_q = f"以下哪一步驟可以{outcome}？"
    if len(subject) > 10 or "驗證" in subject or "檢驗" in subject:
        new_q = f"以下哪一項可以{outcome}？"

    prefer = [s for s in ("數據收集", "數據分析", "數據儲存", "數據組織", "數據處理") if s != subject]
    if use_data:
        prefer = [s.replace("數據", "資料") for s in prefer]
    distractors = [s for s in prefer if s in stages][:3]
    while len(distractors) < 3:
        extra = [s for s in stages if s != subject and s not in distractors]
        if not extra:
            break
        distractors.append(rng.choice(extra))
    labels = [subject, *distractors[:3]]
    letters = list("ABCD")
    new_opts = {letters[i]: labels[i] for i in range(4)}
    new_ans = letters[labels.index(subject)]
    return new_q, [], new_opts, new_ans


_SSD_OS_INSTALL_RE = re.compile(
    r"操作系統.*(?:安裝|存放).*(?:SSD|固態)|(?:SSD|固態).*(?:硬碟|HDD).*操作系統",
    re.I,
)


def _can_reframe_ssd_vs_hdd(
    question: str,
    statements: list[str],
    opts: dict[str, str],
) -> bool:
    if statements or not _simple_text_options(opts):
        return False
    if "SSD" not in question.upper():
        return False
    if not re.search(r"硬碟|HDD", question, re.I):
        return False
    return bool(_SSD_OS_INSTALL_RE.search(question) or "為什麼操作系統" in question)


def _capacities_from_ssd_question(question: str) -> tuple[str | None, str | None]:
    ssd_m = re.search(r"(\d+)\s*GB\s*SSD", question, re.I)
    hdd_m = re.search(r"(\d+)\s*(TB|GB)\s*硬碟", question, re.I)
    ssd = f"{ssd_m.group(1)}GB" if ssd_m else None
    hdd = f"{hdd_m.group(1)}{hdd_m.group(2)}" if hdd_m else None
    return ssd, hdd


def _reframe_ssd_vs_hdd(
    question: str,
    opts: dict[str, str],
    ans: str | None,
    rng: random.Random,
) -> tuple[str, list[str], dict[str, str], str]:
    """
    例：思明…500GB SSD + 2TB 硬碟，為何 OS 裝在 SSD？
    → SSD 較 HDD 優點 / 較宜安裝在哪種裝置（同概念，不同題款）。
    """
    ssd_cap, hdd_cap = _capacities_from_ssd_question(question)
    ssd_label = ssd_cap or "512GB"
    hdd_label = hdd_cap or "2TB"

    variants: list[tuple[str, dict[str, str], str]] = [
        (
            "下列哪項是固態硬碟（SSD）較傳統硬碟機（HDD）的優點？",
            {
                "A": "讀寫速度較快",
                "B": "每 GB 儲存成本較低",
                "C": "適合長期保存大量影片檔案",
                "D": "利用旋轉碟片提高抗震力",
            },
            "A",
        ),
        (
            f"一部桌上電腦設有 {ssd_label} SSD 及 {hdd_label} 硬碟機。"
            "為縮短系統及常用程式啟動時間，操作系統較宜安裝在？",
            {
                "A": "SSD",
                "B": "硬碟機",
                "C": "RAM",
                "D": "ROM",
            },
            "A",
        ),
        (
            "下列哪項最能說明操作系統檔宜存放在 SSD 而非硬碟機？",
            {
                "A": "系統檔案需經常讀寫，SSD 存取較快",
                "B": "操作系統容量必須小於 SSD 容量",
                "C": "SSD 每 GB 價格較硬碟機低",
                "D": "操作系統屬於應用軟件",
            },
            "A",
        ),
    ]
    new_q, new_opts, new_ans = rng.choice(variants)
    return new_q, [], new_opts, new_ans


def _can_reframe_least_important(
    question: str,
    statements: list[str],
    opts: dict[str, str],
) -> bool:
    return not statements and ("最不重要" in question or "最不重要的因素" in question)


def _reframe_least_important(
    question: str,
    opts: dict[str, str],
    ans: str | None,
    rng: random.Random,
) -> tuple[str, list[str], dict[str, str], str]:
    resolved = _resolve_answer_letter(question, opts, ans)
    new_q = question.replace("悉個", "哪一")
    for old, new in (
        ("應該最不重要", "可略為忽略"),
        ("應最不重要", "可略為忽略"),
        ("哪項是最不重要的因素", "哪項因素可略為忽略"),
        ("哪項不是最不重要的因素", "哪項因素可略為忽略"),
    ):
        if old in new_q:
            new_q = new_q.replace(old, new, 1)
            break
    if new_q == question:
        new_q = re.sub(r"最不重要\??", "可略為忽略？", question)
    return new_q, [], opts, resolved


_REALTIME_REASON_RE = re.compile(
    r"[。．]?這是實時處理[^。]*(?:原因是因為|主因)?[_\s]*[。．]?$|"
    r"[。．]?實時處理[^。]*(?:原因是因為|主因)?[_\s]*[。．]?$",
)


def _can_reframe_realtime(
    question: str,
    statements: list[str],
    opts: dict[str, str],
) -> bool:
    return not statements and "實時處理" in question and bool(
        _REALTIME_REASON_RE.search(question.strip())
    )


def _reframe_realtime(
    question: str,
    opts: dict[str, str],
    ans: str | None,
    rng: random.Random,
) -> tuple[str, list[str], dict[str, str], str]:
    resolved = _resolve_answer_letter(question, opts, ans)
    scenario = _REALTIME_REASON_RE.sub("", question.strip()).rstrip("。")
    endings = (
        "下列哪項最能說明須採用實時處理？",
        "下列哪項最能解釋上述系統屬於實時處理？",
        "下列哪項是採用實時處理的主因？",
    )
    new_q = f"{scenario}。{rng.choice(endings)}"
    return new_q, [], opts, resolved


_ALGORITHM_OUTPUT_RE = re.compile(
    r"^(此|這)(算法|演算法)的輸出是什麼[？?]?$",
)


def _can_reframe_algorithm_output(
    question: str,
    statements: list[str],
    opts: dict[str, str],
) -> bool:
    if statements:
        return False
    q = question.strip()
    return bool(_ALGORITHM_OUTPUT_RE.match(q)) or (
        len(q) <= 20 and "輸出" in q and ("算法" in q or "演算法" in q)
    )


def _reframe_algorithm_output(
    question: str,
    opts: dict[str, str],
    ans: str | None,
    rng: random.Random,
) -> tuple[str, list[str], dict[str, str], str]:
    resolved = _resolve_answer_letter(question, opts, ans)
    variants = (
        "參考下列算法，執行後會輸出哪個數值？",
        "下列哪個數值最有可能是上述算法的輸出？",
        "以上程序段執行後，會輸出下列哪個數值？",
    )
    return rng.choice(variants), [], opts, resolved


def _generic_stem_nudge(question: str, rng: random.Random) -> str:
    """Last-resort DSE-style wording shift when stem would stay identical to bank."""
    q = question.strip()
    candidates: list[str] = []
    if q.startswith("以下"):
        candidates.append("下列" + q[2:])
    elif q.startswith("下列"):
        candidates.append("以下" + q[2:])
    if "哪一天" in q:
        candidates.append(q.replace("哪一天", "某日", 1))
    if "哪個" in q:
        candidates.append(q.replace("哪個", "哪一個", 1))
    if "通常" in q:
        candidates.append(q.replace("通常", "一般", 1))
    if "通常儲存在哪個地方" in q:
        candidates.append(
            q.replace("通常儲存在哪個地方", "一般會儲存在哪一種儲存裝置", 1)
        )
    if q.startswith("用作"):
        candidates.append("在開機時，" + q[2:])
    if len(q) >= 24 and not q.startswith(("根據", "在開機", "就以上")):
        candidates.append(f"在一般情況下，{q}")
    if len(q) >= 36 and not q.startswith("根據"):
        candidates.append(f"根據以上描述，{q}")
    if "_______" in q:
        candidates.append(q.replace("_______", "下列哪一項"))
    candidates = [c for c in candidates if c and c != q]
    if not candidates:
        return q
    return rng.choice(candidates)


def _reframe_modes_available(q: str, stmts: list[str], opts: dict[str, str]) -> bool:
    return (
        _can_reframe_ssd_vs_hdd(q, stmts, opts)
        or _can_reframe_causal_importance(q, stmts, opts)
        or _can_reframe_realtime(q, stmts, opts)
        or _can_reframe_least_important(q, stmts, opts)
        or _can_reframe_algorithm_output(q, stmts, opts)
    )


def _apply_reframe(
    question: str,
    stmts: list[str],
    opts: dict[str, str],
    resolved: str,
    rng: random.Random,
) -> tuple[str, list[str], dict[str, str], str] | None:
    if _can_reframe_ssd_vs_hdd(question, stmts, opts):
        return _reframe_ssd_vs_hdd(question, opts, resolved, rng)
    if _can_reframe_causal_importance(question, stmts, opts):
        return _reframe_causal_importance(question, opts, resolved, rng)
    if _can_reframe_realtime(question, stmts, opts):
        return _reframe_realtime(question, opts, resolved, rng)
    if _can_reframe_least_important(question, stmts, opts):
        return _reframe_least_important(question, opts, resolved, rng)
    if _can_reframe_algorithm_output(question, stmts, opts):
        return _reframe_algorithm_output(question, opts, resolved, rng)
    return None


def _simple_text_options(opts: dict[str, str]) -> bool:
    for text in opts.values():
        if _OPTION_FORMULA_RE.search(text):
            return False
        if len(text) > 72:
            return False
    return True


def _can_convert_to_combo(
    question: str,
    statements: list[str],
    opts: dict[str, str],
    *,
    span: int,
) -> bool:
    if statements or span < 10:
        return False
    if not _simple_text_options(opts):
        return False
    if len(opts) != 4:
        return False
    if _context_lines({"text": question}, question, statements):
        return False
    if len(_scenario_prefix(question)) < 8:
        return False
    if any(re.fullmatch(r"[\d\s\.\-]+", t.strip()) for t in opts.values()):
        return False
    if re.search(r"(算法|偽代碼|輸出|餘數|循環)", question):
        return False
    return bool(question.strip())


def _scenario_prefix(question: str) -> str:
    parts = re.split(r"(以下|下列)", question, maxsplit=1)
    prefix = parts[0].strip()
    if len(prefix) < 8:
        return ""
    if not prefix.endswith(("，", "。", "？", "?")):
        prefix += "，"
    return prefix


def _combo_question_line(prefix: str, original_q: str, rng: random.Random) -> str:
    lead = prefix or ""
    if "驗證" in original_q:
        return f"{lead}以下哪項／些是數據驗證的步驟？"
    if "有效性" in original_q:
        return f"{lead}以下哪項／些是數據有效性檢驗的步驟？"
    if "優點" in original_q:
        return f"{lead}以下哪項／些是優點？"
    if "功能" in original_q and "操作系統" in original_q:
        return f"{lead}以下哪項／些是操作系統的功能？"
    return rng.choice(_COMBO_Q_TEMPLATES).format(prefix=lead)


_COMBO_ALL_RE = re.compile(r"\(1\).*\(2\).*\(3\)|皆是|全部都|均正確", re.IGNORECASE)


def _combo_true_nums(option_text: str, n_stmts: int) -> set[int]:
    t = option_text.strip()
    if _COMBO_ALL_RE.search(t):
        return set(range(1, min(n_stmts, 3) + 1))
    return {int(x) for x in re.findall(r"\((\d+)\)", t)}


def _infer_combo_answer_letter(q: str, opts: dict[str, str], stmts: list[str]) -> str | None:
    if "影響資訊系統的輸出" in q:
        for letter in "ABCD":
            if "(1)" in opts.get(letter, "") and "(3)" in opts.get(letter, ""):
                return letter
    if "操作系統的功能" in q or "哪些是操作系統" in q:
        for letter in "ABCD":
            t = opts.get(letter, "")
            if "(1)" in t and "(2)" in t and ("和 (3)" in t or "及 (3)" in t):
                return letter
    if "圖像文件類型" in q or "圖像檔" in q:
        for letter in "ABCD":
            if "(2)" in opts.get(letter, "") and "(3)" in opts.get(letter, ""):
                return letter
    if "病毒偵測" in q or "電腦病毒" in q:
        for letter in "ABCD":
            if opts.get(letter, "").strip() == "只有 (3)":
                return letter
    return None


def _can_convert_to_single(
    question: str,
    statements: list[str],
    opts: dict[str, str],
) -> bool:
    if not _is_combo_mcq_options(opts, statements):
        return False
    if len(statements) < 2 or len(statements) > 4:
        return False
    if any(len(s) > 80 for s in statements):
        return False
    if not all(s.strip() for s in statements):
        return False
    return True


def _mild_false_statement(stmt: str, rng: random.Random) -> str:
    for a, b in (("會", "不會"), ("可以", "不可以"), ("能", "不能"), ("是", "不是"), ("增加", "減少")):
        if a in stmt and b not in stmt:
            return stmt.replace(a, b, 1)
    return f"以上各項均與「{stmt[:12]}…」無關"


def _combo_to_single_question(question: str, *, ask_false: bool) -> str:
    q = question.split("\n")[0].strip()
    q = (
        q.replace("哪類／些", "哪一類")
        .replace("哪個／些", "哪一個")
        .replace("哪句／些", "哪一句")
        .replace("／些", "")
        .replace("/些", "")
    )
    q = re.sub(r"以下哪项", "以下哪一項", q)
    q = re.sub(r"以下哪項", "以下哪一項", q)
    q = re.sub(r"下列哪项", "下列哪一項", q)
    q = re.sub(r"下列哪項", "下列哪一項", q)
    q = re.sub(r"以下哪句", "以下哪一句", q)
    if ask_false:
        if "影響" in q and not re.search(r"不.{0,2}影響", q):
            q = q.replace("將影響", "不會影響", 1)
            q = re.sub(r"(?<!不)會影響", "不會影響", q, count=1)
        elif "？" not in q and "?" not in q:
            q += "？"
        elif "不是" not in q and "不正確" not in q:
            q = q.rstrip("？?") + "是不正確的？"
    elif "？" not in q and "?" not in q:
        q += "？"
    return q


def _stmt_single_options(
    statements: list[str],
    correct_idx: int,
    rng: random.Random,
) -> tuple[dict[str, str], str]:
    """Map statements to A–D; correct_idx is 0-based index into statements used as options."""
    letters = list("ABCD")
    texts = list(statements[:3])
    while len(texts) < 3:
        texts.append("以上各項均不正確")
    if len(statements) <= 3:
        wrong = [i for i in range(3) if i != correct_idx]
        d_text = _mild_false_statement(texts[rng.choice(wrong) if wrong else 0], rng)
        opt_texts = [texts[0], texts[1], texts[2], d_text]
        new_ans = letters[correct_idx]
    else:
        opt_texts = statements[:4]
        new_ans = letters[min(correct_idx, 3)]
    return {L: opt_texts[i] for i, L in enumerate(letters)}, new_ans


def _convert_combo_to_single(
    question: str,
    statements: list[str],
    opts: dict[str, str],
    ans: str | None,
    rng: random.Random,
) -> tuple[str, list[str], dict[str, str], str]:
    """Turn DSE (1)(2)(3) combo into a 4-option single MCQ."""
    resolved = _resolve_answer_letter(question, opts, ans)
    inferred = _infer_combo_answer_letter(question, opts, statements)
    if inferred:
        resolved = inferred
    true_nums = _combo_true_nums(opts.get(resolved, ""), len(statements))
    false_nums = [i for i in range(1, len(statements) + 1) if i not in true_nums]

    if len(true_nums) == 1:
        correct_idx = list(true_nums)[0] - 1
        new_q = _combo_to_single_question(question, ask_false=False)
        new_opts, new_ans = _stmt_single_options(statements, correct_idx, rng)
    elif false_nums:
        correct_idx = rng.choice(false_nums) - 1
        new_q = _combo_to_single_question(question, ask_false=True)
        new_opts, new_ans = _stmt_single_options(statements, correct_idx, rng)
    else:
        correct_idx = 0
        new_q = _combo_to_single_question(question, ask_false=False)
        new_opts, new_ans = _stmt_single_options(statements, correct_idx, rng)

    return new_q, [], new_opts, new_ans


def _convert_single_to_combo(
    question: str,
    opts: dict[str, str],
    ans: str,
    rng: random.Random,
) -> tuple[str, list[str], dict[str, str], str]:
    """Turn a 4-option single MCQ into DSE (1)(2)(3) combo style."""
    letters = list("ABCD")
    opt_texts = [opts[L] for L in letters]
    correct = _resolve_answer_letter(question, opts, ans)
    correct_idx = letters.index(correct)

    if correct_idx == 3:
        stmt_texts = opt_texts[1:4]
        true_num = 3
    else:
        stmt_texts = opt_texts[0:3]
        true_num = correct_idx + 1

    prefix = _scenario_prefix(question)
    new_q = _combo_question_line(prefix, question, rng)
    combo_tuple = COMBO_OPTS_3_ONLY
    target = f"只有 ({true_num})"
    new_opts = {L: combo_tuple[i] for i, L in enumerate(letters)}
    new_ans = letters[combo_tuple.index(target)]
    return new_q, stmt_texts, new_opts, new_ans


def _pick_style_item(
    pool: list[dict],
    content: dict,
    rng: random.Random,
    used_ids: set[str],
    core: str,
    *,
    span: int,
) -> dict | None:
    """Another DSE item with the same MCQ shape — borrow its question phrasing."""
    shape = _mcq_shape(content)
    alts = [
        it
        for it in pool
        if it["id"] != content["id"]
        and it["id"] not in used_ids
        and item_matches_core(it, core)
        and _mcq_shape(it) == shape
        and _fits_span(it, span)
    ]
    if not alts:
        return None
    rng.shuffle(alts)
    return alts[0]


def _prepare_dse_item(
    content: dict,
    rng: random.Random,
    *,
    style_item: dict | None = None,
    transform: str = "base",
    span: int = 6,
) -> dict:
    """
    DSE-native stem: no school prefixes. Optional style_item = A 問法 + content = B 內容/選項.
    transform: base | flip | combo | single | reframe (因果題改問法).
    """
    work = {**content}
    mapping: dict[int, int] = {}
    text = _adapt_text(content.get("text", ""), rng)
    q, stmts, opts, ans = _extract_mcq_parts({**content, "text": text})
    ctx = _context_lines({**content, "text": text}, q, stmts)
    style_id: str | None = None
    transform_used = transform

    if style_item and style_item["id"] != content["id"] and transform == "base":
        st_text = _adapt_text(style_item.get("text", ""), rng)
        qs, _, _, _ = _extract_mcq_parts({**style_item, "text": st_text})
        shape = _mcq_shape(content)
        # Do not cross-mix combo stems (A 問法 + B 陳述會張冠李戴)
        if shape == "algorithm" and ctx and qs:
            q = qs
            style_id = str(style_item["id"])

    resolved = _resolve_answer_letter(q, opts, ans, statements=stmts)

    if transform == "reframe":
        reframed = _apply_reframe(q, stmts, opts, resolved, rng)
        if reframed is not None:
            q, stmts, opts, resolved = reframed
            transform_used = "reframe"
    elif transform == "flip" and _can_flip_polarity(q):
        q = _flip_polarity_question(q)
        resolved = _flip_answer_letter(resolved, rng)
        transform_used = "flip"
    elif transform == "combo" and _can_convert_to_combo(q, stmts, opts, span=span):
        q, stmts, opts, resolved = _convert_single_to_combo(q, opts, resolved, rng)
        transform_used = "combo"
    elif transform == "single" and _can_convert_to_single(q, stmts, opts):
        q, stmts, opts, resolved = _convert_combo_to_single(q, stmts, opts, resolved, rng)
        transform_used = "single"
    elif transform != "base":
        transform_used = "base"

    q = _vary_numbers_text(q, rng, mapping)
    stmts = [_vary_numbers_text(s, rng, mapping) for s in stmts]
    combo_opts = _is_combo_mcq_options(opts, stmts)
    opts = {
        k: (v if combo_opts else _vary_numbers_text(v, rng, mapping))
        for k, v in opts.items()
    }
    ctx = [_vary_numbers_text(c, rng, mapping) for c in ctx]

    body_lines = [q]
    if ctx:
        body_lines.append("")
        body_lines.extend(ctx)
    if stmts:
        body_lines.append("")
        for i, stmt in enumerate(stmts, start=1):
            body_lines.append(f"({i}) {stmt}")
    for L in "ABCD":
        if L in opts:
            body_lines.append(f"{L}. {opts[L]}")

    work["text"] = "\n".join(body_lines)
    work["stem"] = q
    work["statements"] = stmts
    work["options"] = opts
    work["answer"] = resolved
    if style_id:
        work["_style_id"] = style_id
    work["_transform"] = transform_used
    work["_distinction_ready"] = True
    return work


def _bank_stem_similarity(original: dict, adapted: dict) -> float:
    oq, ost, _, _ = _extract_mcq_parts(original)
    aq, ast, _, _ = _extract_mcq_parts(adapted)
    o = normalize_text("\n".join([p for p in [oq, *ost] if p]))
    a = normalize_text("\n".join([p for p in [aq, *ast] if p]))
    return text_similarity(o, a)


def _transform_modes(item: dict, *, span: int) -> list[str]:
    text = _adapt_text(item.get("text", ""), random.Random(0))
    q, stmts, opts, ans = _extract_mcq_parts({**item, "text": text})
    modes = ["base"]
    if _reframe_modes_available(q, stmts, opts):
        modes.append("reframe")
    if _can_convert_to_single(q, stmts, opts):
        modes.append("single")
    if _can_flip_polarity(q):
        modes.append("flip")
    if _can_convert_to_combo(q, stmts, opts, span=span):
        modes.append("combo")
    return modes


def _prepare_bank_item(
    item: dict,
    rng: random.Random,
    *,
    style_item: dict | None = None,
    span: int = 6,
) -> dict:
    """DSE-style item; try base / 是↔不是 / combo to lower bank similarity."""
    if str(item.get("id", "")).startswith("fallback"):
        return {**item, "_distinction_ready": True}
    modes = _transform_modes(item, span=span)
    ordered = [m for m in ("reframe", "single", "combo", "flip", "base") if m in modes]
    text_probe = _adapt_text(item.get("text", ""), rng)
    q_probe, stmts_probe, opts_probe, _ = _extract_mcq_parts({**item, "text": text_probe})
    if span <= 8 and _is_combo_mcq_options(opts_probe, stmts_probe) and "single" in ordered:
        ordered = ["single"] + [m for m in ordered if m != "single"]
    best = _prepare_dse_item(item, rng, style_item=style_item, transform="base", span=span)
    best_sim = _bank_stem_similarity(item, best)
    for mode in ordered:
        for _ in range(8):
            work = _prepare_dse_item(
                item,
                rng,
                style_item=style_item if mode == "base" else None,
                transform=mode,
                span=span,
            )
            sim = _bank_stem_similarity(item, work)
            if sim <= _BANK_SIM_THRESH:
                return work
            if sim < best_sim:
                best_sim, best = sim, work
    if _bank_stem_similarity(item, best) >= _BANK_SIM_IDENTICAL:
        bq, bstmts, bopts, bans = _extract_mcq_parts(best)
        resolved = str(best.get("answer") or bans or "A")[0].upper()
        for _ in range(6):
            reframed = _apply_reframe(bq, bstmts, bopts, resolved, rng)
            if reframed is None:
                break
            nq, nstmts, nopts, nans = reframed
            body = [nq]
            if nstmts:
                body.append("")
                body.extend(f"({i}) {s}" for i, s in enumerate(nstmts, start=1))
            for L in "ABCD":
                if L in nopts:
                    body.append(f"{L}. {nopts[L]}")
            trial = {
                **best,
                "text": "\n".join(body),
                "stem": nq,
                "statements": nstmts,
                "options": nopts,
                "answer": nans,
            }
            sim = _bank_stem_similarity(item, trial)
            if sim < best_sim:
                best_sim, best = sim, trial
                bq, bstmts, bopts, resolved = nq, nstmts, nopts, nans
            if sim < _BANK_SIM_IDENTICAL:
                break
    if _bank_stem_similarity(item, best) >= _BANK_SIM_IDENTICAL:
        bq, bstmts, bopts, bans = _extract_mcq_parts(best)
        nudged = _generic_stem_nudge(bq, rng)
        if nudged != bq:
            body = [nudged]
            if bstmts:
                body.append("")
                body.extend(f"({i}) {s}" for i, s in enumerate(bstmts, start=1))
            for L in "ABCD":
                if L in bopts:
                    body.append(f"{L}. {bopts[L]}")
            trial = {**best, "text": "\n".join(body), "stem": nudged}
            sim = _bank_stem_similarity(item, trial)
            if sim < _BANK_SIM_IDENTICAL:
                best = trial
    return best


def _stem_fingerprint(item: dict) -> str:
    """Comparable key for de-duplication (stem + sub-statements, no options)."""
    question, statements, _opts, _ = _extract_mcq_parts(item)
    parts = [question]
    parts.extend(statements)
    return normalize_text("\n".join(parts))


def _extract_mcq_parts(item: dict) -> tuple[str, list[str], dict[str, str], str | None]:
    """Return (question_line, statement_texts, options dict, answer letter)."""
    raw = item.get("gemini_raw") or {}
    answer = item.get("answer")
    opts: dict[str, str] = {}

    if isinstance(item.get("options"), dict):
        opts = {k: str(v) for k, v in item["options"].items() if k in "ABCD"}
    elif isinstance(raw.get("options"), dict):
        opts = {k: str(v) for k, v in raw["options"].items() if k in "ABCD"}
    elif isinstance(raw.get("options"), list):
        for line in raw["options"]:
            m = re.match(r"^([ABCD])[\.\)]\s*(.*)$", str(line).strip())
            if m:
                opts[m.group(1)] = m.group(2).strip()

    statements: list[str] = []
    for key in ("sub_questions_list", "statements"):
        val = raw.get(key)
        if isinstance(val, list) and val:
            statements = [str(s).strip() for s in val]
            break

    stem = (item.get("stem") or raw.get("question_text") or "").strip()
    text = (item.get("text") or "").strip()

    if not stem and text:
        stem = text.split("\n")[0]

    question = stem.split("\n")[0].strip() if stem else text.split("\n")[0].strip()

    opts_use_numbered = any(re.search(r"\(\d+\)", v) for v in opts.values())

    if not statements and opts_use_numbered:
        source = text if text else stem
        middle: list[str] = []
        seen_first = False
        for line in source.split("\n"):
            s = line.strip()
            if not s or s.startswith("["):
                continue
            if re.match(r"^[ABCD][\.\)]", s):
                break
            if not seen_first:
                if s == question or s.startswith(question[: min(20, len(question))]):
                    seen_first = True
                continue
            if re.match(r"^\(\d+\)", s):
                statements.append(re.sub(r"^\(\d+\)\s*", "", s))
            elif s and not s.endswith("？") and not s.endswith("?"):
                middle.append(s)
        if not statements and middle:
            statements = middle

    # Strip (n) prefixes if present
    cleaned: list[str] = []
    for s in statements:
        cleaned.append(re.sub(r"^\(\d+\)\s*", "", s.strip()))
    statements = [s for s in cleaned if s]

    if not opts and text:
        for line in text.split("\n"):
            m = re.match(r"^([ABCD])[\.\)]\s*(.*)$", line.strip())
            if m:
                opts[m.group(1)] = m.group(2).strip()

    return question, statements, opts, answer


def _layout_mcq_block(
    question: str,
    statements: list[str],
    opts: dict[str, str],
    span: int,
    *,
    hint: str = "",
    context: list[str] | None = None,
) -> list[str]:
    """Build template lines: DSE style with (1)(2)(3) sub-items where needed."""
    opt_lines = [f"\t{L}.\t{opts[L]}" for L in "ABCD" if L in opts]
    if len(opt_lines) != 4:
        raise ValueError(f"MCQ must have 4 options, got {len(opt_lines)} for: {question[:60]}")

    body: list[str] = [question]
    ctx = context or []
    if ctx:
        body.append("")
        body.extend(ctx)
    if statements:
        if body[-1] != "":
            body.append("")
        for i, stmt in enumerate(statements, start=1):
            body.append(f"\t\t({i})\t{stmt}")
        body.append("")
    elif hint:
        body.append("")
        body.append(hint)
        body.append("")
    elif not ctx:
        body.append("")

    body.extend(opt_lines)

    # Pad with blank lines before options
    while len(body) < span:
        insert_at = len(body) - 4
        body.insert(max(1, insert_at), "")

    # Trim excess blank lines (keep question + options intact)
    while len(body) > span:
        removed = False
        for i in range(1, len(body) - 4):
            if body[i] == "" and len(body) > span:
                body.pop(i)
                removed = True
                break
        if not removed:
            body = body[:span]
            break

    if len(body) < span:
        body.extend([""] * (span - len(body)))
    if len(body) != span:
        raise ValueError(
            f"MCQ layout span mismatch: need {span}, got {len(body)} "
            f"(q={question[:40]!r}, statements={len(statements)})"
        )
    return body


def _parse_mcq_item(item: dict) -> tuple[list[str], list[str], str | None]:
    """Legacy wrapper — prefer _layout_mcq_block via _format_mcq_block."""
    question, statements, opts, answer = _extract_mcq_parts(item)
    lines = _layout_mcq_block(question, statements, opts, span=6)
    return lines, lines, answer


def _algo_output_family(text: str) -> bool:
    return "下列算法的輸出" in text


def _too_similar_to_chosen(fp: str, chosen_fps: list[str]) -> bool:
    for other in chosen_fps:
        if text_similarity(fp, other) > _INTRA_EXAM_THRESH:
            return True
        if _algo_output_family(fp) and _algo_output_family(other):
            return True
    return False


def _context_lines(item: dict, question: str, statements: list[str]) -> list[str]:
    """Extra stem lines (binary sequences, SQL, sub-questions) — not numbered statements."""
    if statements:
        return []
    text = (item.get("text") or "").strip()
    q_first = question.split("\n")[0].strip()
    ctx: list[str] = []
    for line in text.split("\n"):
        s = line.strip()
        if not s or s.startswith("[") or re.match(r"^[ABCD][\.\)]", s):
            if re.match(r"^[ABCD][\.\)]", s):
                break
            continue
        if s == q_first:
            continue
        if re.match(r"^\(\d+\)", s):
            break
        ctx.append(s)
    support = _mcq_support_lines(item, question, statements)
    if support:
        ctx = support
    return ctx


def _required_span(item: dict) -> int:
    question, statements, opts, _ = _extract_mcq_parts(item)
    ctx = _context_lines(item, question, statements)
    if statements:
        return 7 + len(statements)  # q + blank + n stmts + blank + 4 opts
    if ctx:
        return 7 + len(ctx)
    return 6


def _fits_span(item: dict, span: int) -> bool:
    return _required_span(item) <= span


def pick_mcq_pool(rng: random.Random) -> list[dict]:
    pool: list[dict] = []
    for y in _YEARS:
        if y == "2026":
            continue
        slugs = ["Paper1A_MultipleChoice"] if int(y) >= 2025 else ["Paper1_MultipleChoice"]
        for slug in slugs:
            for it in _load_bank_items(y, slug):
                if not _text_ok(it.get("text", "")):
                    continue
                if not _unit_ok(it.get("curriculum_unit", "")):
                    continue
                if not _syllabus_ok(it):
                    continue
                if it.get("options") or re.search(r"^[ABCD]\.", it.get("text", ""), re.M):
                    pool.append({**it, "_year": y})
    seen: dict[str, str] = {}
    unique: list[dict] = []
    for it in pool:
        fp = _stem_fingerprint(it)
        if fp in seen:
            continue
        seen[fp] = it["id"]
        unique.append(it)
    rng.shuffle(unique)
    return unique


def pick_mcq_items(rng: random.Random, used_ids: set[str]) -> list[dict]:
    pool = pick_mcq_pool(rng)
    chosen: list[dict] = []
    chosen_fps: list[str] = []
    for slot_idx, (core, concepts) in enumerate(MCQ_SLOT_PLAN, start=1):
        span = MCQ_TEMPLATE_SPANS[slot_idx - 1]
        pick: dict | None = None
        for require_concepts in (True, False):
            candidates = _slot_candidates(
                pool,
                used_ids=used_ids,
                chosen_fps=chosen_fps,
                core=core,
                concepts=concepts,
                span=span,
                require_concepts=require_concepts,
                require_dedup=True,
            )
            if candidates:
                rng.shuffle(candidates)
                best_work: dict | None = None
                best_sim = 1.0
                for cand in candidates:
                    style = _pick_style_item(pool, cand, rng, used_ids, core, span=span)
                    work = _prepare_bank_item(cand, rng, style_item=style, span=span)
                    sim = _bank_stem_similarity(cand, work)
                    if sim <= best_sim:
                        best_sim, best_work = sim, work
                    if sim <= _BANK_SIM_THRESH:
                        pick = work
                        break
                    alt_styles = [
                        it
                        for it in pool
                        if it["id"] != cand["id"]
                        and it["id"] not in used_ids
                        and _mcq_shape(it) == _mcq_shape(cand)
                    ]
                    rng.shuffle(alt_styles)
                    for alt_style in alt_styles[:8]:
                        work2 = _prepare_bank_item(cand, rng, style_item=alt_style, span=span)
                        sim2 = _bank_stem_similarity(cand, work2)
                        if sim2 <= best_sim:
                            best_sim, best_work = sim2, work2
                        if sim2 <= _BANK_SIM_THRESH:
                            pick = work2
                            break
                    if pick is not None:
                        break
                if pick is None and best_work is not None:
                    if best_sim >= _BANK_SIM_IDENTICAL:
                        best_work = _prepare_bank_item(cand, rng, span=span)
                        best_sim = _bank_stem_similarity(cand, best_work)
                    if best_sim < _BANK_SIM_IDENTICAL:
                        pick = best_work
        if pick is None:
            fb = FALLBACK_BY_SLOT.get(slot_idx)
            if fb and _fits_span(fb, span):
                pick = fb
            else:
                raise RuntimeError(f"No unique MCQ candidate for slot {slot_idx} (concepts={concepts})")
        if pick.get("id") and not str(pick["id"]).startswith("fallback"):
            used_ids.add(pick["id"])
        chosen_fps.append(_stem_fingerprint(pick))
        chosen.append(pick)
    return chosen


def _is_combo_mcq_options(opts: dict[str, str], statements: list[str]) -> bool:
    if len(statements) < 2:
        return False
    combo_opts = sum(1 for v in opts.values() if _COMBO_OPTION_RE.search(v))
    return combo_opts >= 2


def _format_mcq_block(item: dict, span: int, rng: random.Random) -> tuple[list[str], int]:
    """Parse bank item → template lines + correct index (0–3)."""
    if item.get("_distinction_ready"):
        work = {**item}
    else:
        adapted_text = _adapt_text(item.get("text", ""), rng)
        work = {**item, "text": adapted_text}
        if work.get("stem"):
            work["stem"] = _adapt_text(str(work["stem"]), rng)

    question, statements, opts, ans = _extract_mcq_parts(work)
    if question.startswith("假設 N = 0"):
        question = (
            "設計了 M1 和 M2 兩個算法，在自動販賣機內以每 5 個積分輸出一罐汽水。"
            "N 代表積分數量。" + question
        )
    letter_to_idx = {"A": 0, "B": 1, "C": 2, "D": 3}
    correct = letter_to_idx.get(str(ans or "A").strip()[0], 0)
    if _is_combo_mcq_options(opts, statements):
        stem_nums = frozenset(range(1, len(statements) + 1))
        opt_list = [opts[L] for L in "ABCD"]
        sorted_opts, correct = sort_combination_options(opt_list, stem_nums, correct)
        opts = {L: sorted_opts[i] for i, L in enumerate("ABCD")}
    ctx = _context_lines(work, question, statements)
    normalised = _layout_mcq_block(question, statements, opts, span, context=ctx)
    return normalised, correct


MCQ_TEMPLATE_SPANS: tuple[int, ...] = (
    6, 6, 6, 6, 6, 10, 8, 10, 6, 6, 6, 6, 10, 6, 10, 10, 6, 6, 6, 6, 10, 10, 9, 13, 12, 7, 6, 14, 6, 14,
)


def _load_bank_item_by_id(item_id: str) -> dict | None:
    for year in _YEARS:
        if year == "2026":
            continue
        for slug in ("Paper1A_MultipleChoice", "Paper1_MultipleChoice"):
            for it in _load_bank_items(year, slug):
                if it.get("id") == item_id:
                    return it
    return None


def audit_mcq_bank_similarity(
    items: list[dict],
    rows: list[list[str]],
    *,
    threshold: float = _BANK_SIM_THRESH,
) -> list[tuple[int, float, str]]:
    """Return (slot_index, similarity, bank_id) for MCQs still too close to DSE bank."""
    hits: list[tuple[int, float, str]] = []
    for slot, (it, row) in enumerate(zip(items, rows, strict=True), start=1):
        iid = str(it.get("id", ""))
        if iid.startswith("fallback"):
            continue
        orig = _load_bank_item_by_id(iid)
        if not orig:
            continue
        sim = _bank_stem_similarity(orig, {"text": "\n".join(row)})
        if sim > threshold:
            hits.append((slot, sim, iid))
    return hits


def audit_intra_exam_duplicates(rows: list[list[str]], *, threshold: float = _INTRA_EXAM_THRESH) -> list[tuple[int, int, float]]:
    """Return list of (q1, q2, similarity) for MCQ pairs within the same paper."""
    texts = ["\n".join(r) for r in rows]
    hits: list[tuple[int, int, float]] = []
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            sim = text_similarity(texts[i], texts[j])
            if sim > threshold:
                hits.append((i + 1, j + 1, sim))
    return hits


def build_mcq_payload_from_bank(
    rng: random.Random | None = None,
    *,
    max_attempts: int = 120,
) -> tuple[list[list[str]], tuple[int, ...], list[str]]:
    """Return (rows, correct_indices, provenance_ids) for F5 ICT template."""
    base_seed = getattr(rng, "_seed", None) if rng else 252602
    last_err: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            attempt_rng = random.Random((base_seed or 252602) + attempt * 997)
            used: set[str] = set()
            items = pick_mcq_items(attempt_rng, used)
            rows: list[list[str]] = []
            correct: list[int] = []
            prov: list[str] = []
            for it, span in zip(items, MCQ_TEMPLATE_SPANS, strict=True):
                block, idx = _format_mcq_block(it, span, attempt_rng)
                rows.append(block)
                correct.append(idx)
                prov.append(it["id"])
            hits = audit_intra_exam_duplicates(rows)
            if hits:
                raise RuntimeError(f"intra-exam duplicates: {hits[:5]}")
            # Bank <=60% enforced in pick + reported in spec duplicate check (not here)
            seq_errors = verify_core_sequence([c for c, _ in MCQ_SLOT_PLAN])
            if seq_errors:
                raise RuntimeError(f"core sequence: {seq_errors[0]}")
            return rows, tuple(correct), prov
        except RuntimeError as e:
            last_err = e
            continue
    raise RuntimeError(f"Could not build unique MCQ set after {max_attempts} attempts: {last_err}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Preview DSE-sourced MCQ selection for F5 ICT exam.")
    ap.add_argument("--seed", type=int, default=2526)
    ap.add_argument("--out", type=Path, help="Write selected MCQ preview JSON")
    args = ap.parse_args(argv)

    rng = random.Random(args.seed)
    rows, correct, prov = build_mcq_payload_from_bank(rng)
    preview = {
        "seed": args.seed,
        "count": len(rows),
        "items": [
            {"provenance": p, "correct_index": c, "preview": r[0][:80] if r else ""}
            for p, c, r in zip(prov, correct, rows, strict=True)
        ],
    }
    text = json.dumps(preview, ensure_ascii=False, indent=2)
    if args.out:
        args.out.write_text(text, encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
