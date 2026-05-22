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
if str(_QCHECK) not in sys.path:
    sys.path.insert(0, str(_QCHECK))
if str(_PDF_ENGINE) not in sys.path:
    sys.path.insert(0, str(_PDF_ENGINE))
from quality_lib import normalize_text, text_similarity
from dse_ict_syllabus import is_syllabus_current, load_concepts_cfg
from dse_ict_support_content import mcq_support_lines as _mcq_support_lines

from mcq_core_plan import (
    MCQ_CORE_SEQUENCE,
    MCQ_SLOT_CONCEPTS,
    MCQ_SLOT_PLAN,
    item_matches_core,
    verify_core_sequence,
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

# Within-exam: treat as duplicate if stem similarity exceeds this
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

FALLBACK_BY_SLOT: dict[int, dict] = {5: _FALLBACK_A[0]}
for _slot, _fb in zip(range(21, 31), _FALLBACK_D, strict=True):
    FALLBACK_BY_SLOT[_slot] = _fb

_SYLLABUS_CFG = load_concepts_cfg()
_SUBS = [
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
                pick = candidates[0]
                break
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


def _format_mcq_block(item: dict, span: int, rng: random.Random) -> tuple[list[str], int]:
    """Parse bank item → template lines + correct index (0–3)."""
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
    ctx = _context_lines(work, question, statements)
    normalised = _layout_mcq_block(question, statements, opts, span, context=ctx)
    letter_to_idx = {"A": 0, "B": 1, "C": 2, "D": 3}
    correct = letter_to_idx.get(str(ans or "A").strip()[0], 0)
    return normalised, correct


MCQ_TEMPLATE_SPANS: tuple[int, ...] = (
    6, 6, 6, 6, 6, 10, 8, 10, 6, 6, 6, 6, 10, 6, 10, 10, 6, 6, 6, 6, 10, 10, 9, 13, 12, 7, 6, 14, 6, 14,
)


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
