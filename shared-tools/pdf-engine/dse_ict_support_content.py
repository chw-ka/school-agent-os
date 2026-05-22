"""Build printable support lines (algorithms, ASCII tables/diagrams) for DSE ICT items.

Gemini JSON often omits middle content (flowcharts, spreadsheet tables, pseudocode)
that still appears in gemini_raw fields or can be inferred from known DSE patterns.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

SUPPORT_STATUS_AUTO = "auto"
SUPPORT_STATUS_NEEDS_REVIEW = "needs_review"


def _diagram_line(image_description: str) -> str | None:
    desc = image_description.strip()
    if not desc:
        return None
    if "層次圖" in desc and "P" in desc and "Q" in desc:
        return "用戶 → P → Q → 電腦；R 位於 Q 與電腦之間"
    if "輸入" in desc and "處理" in desc and "輸出" in desc:
        if "流程" in desc or "->" in desc or "→" in desc or "X" in desc:
            return "輸入 → 處理 → 輸出；X：處理 → 輸入；Y：處理 → 輸出"
    return None


def _static_template_lines(question: str, *, options: dict[str, str] | None = None) -> tuple[list[str], str] | None:
    q = question.strip()
    opts = options or {}

    if "產品零售價" in q:
        return (
            [
                "\t\tA\t\t利潤\t12.5%\t\tB\t\t成本\t\tC\t\t零售價",
                "\t\t4\t\t電腦\t8,000\t\t5\t\t電視\t9,000\t\t6\t\t平板電腦\t5,000",
            ],
            "static_template:retail_price_spreadsheet_2025",
        )

    if q.startswith("假設 N = 0") or ("M1" in q and "M2" in q and "汽水" in q):
        return (
            [
                "M1（後測試）：N ← N - 5；輸出一罐汽水；重複直至 N ≤ 4　"
                "M2（前測試）：當 N > 4 執行 N ← N - 5、輸出一罐汽水",
            ],
            "static_template:vending_m1_m2_2025",
        )

    if "目標搜尋" in q or ("B6" in q and "班費" in q):
        return (
            [
                "\t\tA\t\t\t\tB",
                "\t1\tS6 開支 (30 名同學)\t$",
                "\t2\t參考書 6,000　3\t影印費 900　4\t遊學團預算 30,000",
                "\t6\t每名同學班費 1,230",
            ],
            "static_template:goal_seek_class_fee_2022",
        )

    if "輸入什麼值不會輸出「完成！」" in q or "不會輸出「完成！」" in q:
        return (
            [
                "輸入 N",
                "flag ← TRUE",
                "當 flag = TRUE 執行：如果 (N/4) 的餘數 > 0 則 flag ← FALSE",
                "輸出「完成！」",
            ],
            "static_template:flag_loop_2022_aq29",
        )

    opt_vals = set(opts.values())
    if "下列算法的輸出" in q and {"10", "101", "111", "1001"} & opt_vals:
        return (
            [
                "X ← 9　Y ← 2",
                "重複",
                "   輸出 (X / Y) 的餘數；X ← (X / Y) 的整數部分",
                "直至 X = 0",
            ],
            "static_template:remainder_output_2021_q29",
        )

    if "演算法的目的是" in q and "888" in (q + " ".join(opts.values())):
        return (
            ["j ← 0　輸入 N　當 N <> 888 執行 j ← j + N、輸入 N　輸出 j"],
            "static_template:sum_until_888_2022_aq30",
        )

    if "演算法的目的是" in q and any("總和" in v or "平均" in v for v in opts.values()):
        return (
            ["j ← 0　輸入 N　當 N <> 888 執行 j ← j + N、輸入 N　輸出 j"],
            "static_template:sum_until_888_2022_aq30",
        )

    return None


def _stem_continuation_lines(question_text: str) -> list[str]:
    """Multi-line question_text after the first line (shared scenario blocks)."""
    lines = [s.strip() for s in question_text.split("\n") if s.strip()]
    if len(lines) <= 1:
        return []
    first = lines[0]
    out: list[str] = []
    for s in lines[1:]:
        if re.match(r"^[ABCD][\.\)、]", s) or s.startswith("["):
            break
        if re.match(r"^\(\d+\)", s):
            break
        if s == first:
            continue
        out.append(s)
    return out


def _vending_intro(question: str) -> str | None:
    if question.strip().startswith("假設 N = 0"):
        return (
            "設計了 M1 和 M2 兩個算法，在自動販賣機內以每 5 個積分輸出一罐汽水。"
            "N 代表積分數量。"
        )
    return None


def infer_support_lines(
    *,
    question_text: str,
    options: dict[str, str] | None = None,
    gemini_raw: dict[str, Any] | None = None,
    image_description: str | None = None,
    algorithm_code: str | None = None,
    item_id: str = "",
) -> tuple[list[str], list[str], str]:
    """Return (lines, sources, status)."""
    raw = gemini_raw or {}
    q = (question_text or raw.get("question_text") or "").strip()
    sources: list[str] = []
    status = SUPPORT_STATUS_AUTO

    static = _static_template_lines(q, options=options)
    if static:
        lines, src = static
        return lines, [src], status

    lines: list[str] = []

    algo = (algorithm_code or raw.get("algorithm_code") or "").strip()
    if algo:
        if "不會輸出「完成！」" in q and "flag ← FALSE" not in algo:
            status = SUPPORT_STATUS_NEEDS_REVIEW
        else:
            lines.extend(algo.split("\n"))
            sources.append("gemini_raw.algorithm_code")

    img = (image_description or raw.get("image_description") or "").strip()
    if img and not img.startswith("（"):
        diagram = _diagram_line(img)
        if diagram:
            lines.append(diagram)
            sources.append("image_description.diagram")
        elif not lines and ("試算表" in img or "表格" in img):
            short = img if len(img) <= 120 else img[:117] + "…"
            lines.append(f"[表格式意] {short}")
            sources.append("image_description.table_hint")
            status = SUPPORT_STATUS_NEEDS_REVIEW

    cont = _stem_continuation_lines(q)
    for s in cont:
        if s not in lines and not s.startswith("[Flowchart"):
            lines.append(s)
            if "stem_continuation" not in sources:
                sources.append("question_text.continuation")

    if q.strip().startswith("假設 N = 0"):
        intro = _vending_intro(q)
        vending, src = _static_template_lines("假設 N = 0") or ([], "")
        if intro and not any(intro[:20] in q for q in ([question_text] + lines)):
            pass  # intro goes on stem, not support lines
        if vending:
            lines = vending
            sources = [src]

    if not lines:
        return [], [], status
    return lines, sources, status


def build_support_content(item: dict[str, Any]) -> dict[str, Any] | None:
    raw = item.get("gemini_raw") or {}
    qt = item.get("stem") or raw.get("question_text") or item.get("text") or ""
    if not qt and item.get("text"):
        qt = item["text"].split("\n")[0]

    options = item.get("options")
    if not isinstance(options, dict):
        options = None

    lines, sources, status = infer_support_lines(
        question_text=str(qt),
        options=options,
        gemini_raw=raw if isinstance(raw, dict) else None,
        image_description=item.get("image_description"),
        algorithm_code=item.get("algorithm_code"),
        item_id=str(item.get("id") or ""),
    )
    if not lines:
        return None

    return {
        "lines": lines,
        "sources": sources,
        "status": status,
        "supplemented_at": datetime.now(timezone.utc).isoformat(),
        "note": "Auto-filled middle content (algorithm/table/diagram). Verify against PDF before publishing.",
    }


def mcq_support_lines(item: dict, question: str, statements: list[str]) -> list[str]:
    """Adapter for paper-generator MCQ layout (same shape as f5_ict_from_dse)."""
    if statements:
        return []
    sc = item.get("support_content") or build_support_content(item)
    if sc and sc.get("lines"):
        return list(sc["lines"])
    lines, _, _ = infer_support_lines(
        question_text=question,
        options=item.get("options") if isinstance(item.get("options"), dict) else None,
        gemini_raw=item.get("gemini_raw") if isinstance(item.get("gemini_raw"), dict) else None,
        image_description=item.get("image_description"),
        item_id=str(item.get("id") or ""),
    )
    return lines


def _mcq_stem_only(raw: dict, *, options: dict[str, str] | None) -> str:
    parts: list[str] = []
    qt = raw.get("question_text") or ""
    if qt:
        parts.append(qt.strip().split("\n")[0])
    for key in ("statements", "sub_questions_list"):
        items = raw.get(key)
        if items:
            parts.extend(str(x).strip() for x in items)
    intro = _vending_intro(qt)
    if intro and qt.strip().startswith("假設 N = 0"):
        parts[0] = intro + parts[0]
    return "\n".join(parts).strip()


def _join_mcq_text(stem: str, support_lines: list[str], options: dict[str, str]) -> str:
    parts = [stem]
    parts.extend(support_lines)
    for letter in "ABCD":
        if letter in options:
            parts.append(f"{letter}. {options[letter]}")
    return "\n".join(parts)


def apply_support_to_item(item: dict[str, Any], *, force: bool = False) -> bool:
    """Attach support_content and embed lines into stem/text. Returns True if changed."""
    raw = item.get("gemini_raw") if isinstance(item.get("gemini_raw"), dict) else {}
    options = item.get("options")
    is_mcq = item.get("section") == "mcq" and isinstance(options, dict)

    existing = item.get("support_content")
    if existing and not force:
        return False

    sc = build_support_content(item)
    if not sc:
        if existing and force:
            item.pop("support_content", None)
            return True
        return False

    item["support_content"] = sc
    lines = sc["lines"]

    if is_mcq:
        stem = item.get("stem") or _mcq_stem_only(raw, options=None)
        qt = raw.get("question_text") or stem
        intro = _vending_intro(str(qt))
        if intro and str(stem).startswith("假設 N = 0"):
            stem = intro + stem
        item["stem"] = stem
        item["text"] = _join_mcq_text(stem, lines, options)
    else:
        stem = item.get("stem") or (raw.get("question_text") or "").strip()
        if not lines:
            return True
        if stem:
            item["stem"] = stem
        joined = "\n".join(lines)
        text = item.get("text") or ""
        if joined in text:
            return True
        if stem and text.startswith(stem):
            insert_at = len(stem)
            item["text"] = stem + "\n" + joined + text[insert_at:]
        elif stem:
            item["text"] = stem + "\n" + joined + ("\n\n" + text if text else "")
        else:
            item["text"] = joined + ("\n\n" + text if text else "")

    return True
