"""Model answers for F5 ICT Exam02 — keyed to spec text (teacher reference)."""
from __future__ import annotations

import re
from typing import Any

from exam_spec import spec_items

_SUBPART_BODY = re.compile(
    r"\(([a-z]{1,2}|[ivx]{1,4})\)\s*(.*?)(?=\t\(\s*\d+\s*分\s*\)|\([a-z]{1,2}\)|\([ivx]+\)|$)",
    re.I | re.S,
)


def _subparts(text: str) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for m in _SUBPART_BODY.finditer(text or ""):
        body = re.sub(r"\t\(\s*\d+\s*分\s*\)\s*$", "", m.group(2)).strip()
        if body:
            rows.append((m.group(1).lower(), body))
    return rows


def _mcq_key_lines(key: str) -> list[str]:
    letters = [c for c in (key or "").upper() if c in "ABCD"]
    if len(letters) < 30:
        letters.extend(["?"] * (30 - len(letters)))
    line1 = "".join(letters[:15])
    line2 = "".join(letters[15:30])
    chunks = [line1[i : i + 5] for i in range(0, 15, 5)]
    chunks2 = [line2[i : i + 5] for i in range(0, 15, 5)]
    return [" ".join(chunks), " ".join(chunks2)]


def _answer_b01(text: str) -> list[str]:
    lines = ["1."]
    for lab, body in _subparts(text):
        if lab == "a" or ("IF" in body.upper() and "F2" in body):
            lines.append("\t(a)\t=IF(AND(E2=\"Y\",D2>=5),C2*D2*0.9,C2*D2)")
        elif "COUNTIF" in body.upper() and "會員" in body:
            lines.append("\t(b)\t=COUNTIF(E$2:E$50,\"Y\")")
        elif "COUNTIF" in body.upper():
            lines.append("\t(b)\t=COUNTIF(D$2:D$50,\">=5\")")
        elif "SUMIF" in body.upper():
            m = re.search(r"「([^」]+)」", body)
            item = m.group(1) if m else "項目"
            lines.append(f"\t(b)\t=SUMIF(B$2:B$50,\"{item}\",F$2:F$50)")
        elif "XLOOKUP" in body.upper():
            lines.append("\t(b)\t=XLOOKUP(B2,$H$2:$H$10,$I$2:$I$10)")
        else:
            lines.append(f"\t({lab})\t（參考：依題幹欄位寫出對應公式）")
    return lines


def _answer_b02(_text: str) -> list[str]:
    return [
        "2.",
        "\t(a)\tCPU：執行指令；RAM：暫存執行中資料；儲存：永久保存檔案；顯示器：輸出畫面",
        "\t(b)\t雲端：節省本地硬件成本、易備份；限制：需網絡、私隱風險；"
        "本地：速度快、離線可用；限制：硬件成本高、難擴充",
    ]


def _answer_b03(text: str) -> list[str]:
    m = re.search(r"(\d+)\s*×\s*(\d+)", text)
    n = re.search(r"(\d+)\s*張", text)
    w, h = (int(m.group(1)), int(m.group(2))) if m else (1920, 1080)
    count = int(n.group(1)) if n else 40
    bytes_one = w * h * 3
    mb = bytes_one * count / (1024 * 1024)
    return [
        "3.",
        f"\t(a)\t{w}×{h}×24/8 = {bytes_one:,} bytes/張；{count} 張 ≈ {mb:.1f} MB（展示計算）",
        "\t(b)\tJPEG 檔較細但有損；PNG 無損但檔案較大",
    ]


def _answer_b04(text: str) -> list[str]:
    arr_m = re.search(r"A\s*=\s*\[([^\]]+)\]", text)
    key_m = re.search(r"key\s*=\s*(\d+)", text, re.I)
    arr = arr_m.group(1) if arr_m else "9,8,5,7,9,6"
    key = key_m.group(1) if key_m else "5"
    return [
        "4.",
        f"\t(a)\tkey={key} 不在陣列內 → found 維持 FALSE → 最終 OUTPUT = 0",
        "\t(b)\t逐一比對每個元素，最壞需檢查 n 個位置",
    ]


def _answer_b05(_text: str) -> list[str]:
    return [
        "5.",
        "\t(a)\tCREATE TABLE TRANSACTION (TID CHAR(6) PRIMARY KEY, Item VARCHAR(40) NOT NULL, Qty INTEGER, ADate DATE);",
        "\t(b)\tSELECT Item, Qty FROM TRANSACTION WHERE Qty >= 5;",
    ]


def _answer_b06(_text: str) -> list[str]:
    return [
        "6.",
        "\t(a)\t例：Intel Core i7；AMD Ryzen 7",
        "\t(b)\tRAM 增加可同時運行更多程式／減少換頁",
        "\t(c)\tSSD：快、抗震；HDD：容量大、成本低",
        "\t(d)\t例：升級顯示卡須同時安裝新驅動程式",
    ]


def _answer_c01(_text: str) -> list[str]:
    return [
        "1.",
        "\t(a)\tERD：Member–Booking–Screening–Cinema 四實體；Booking 連 Member、Screening；Screening 連 Cinema",
    ]


def _answer_c02(_text: str) -> list[str]:
    return [
        "2.",
        "\t(a)\tMID CHAR(6) PRIMARY KEY, TITLE VARCHAR(80) NOT NULL, …",
        "\t(b)\t防止借書記錄指向不存在的會員；刪除會員時可限制",
    ]


def _answer_c03(_text: str) -> list[str]:
    return [
        "3.",
        "\t(a)\t姓名／電話重複；更新電話要改多筆 → 更新異常",
        "\t(b)\t分拆 MEMBER(MID, Name, Phone) 與 LOAN(MID, BID, …)",
    ]


def _answer_c05(_text: str) -> list[str]:
    return [
        "4.",
        "\t(a)\tSELECT M.MName, F.FName FROM MEMBER M INNER JOIN RESERVE R ON M.MID=R.MEMID "
        "INNER JOIN FACILITY F ON R.FID=F.FID;",
        "\t(b)\tSELECT F.FName, COUNT(*) FROM RESERVE R JOIN FACILITY F ON R.FID=F.FID "
        "GROUP BY F.FName HAVING COUNT(*)>=2;",
        "\t(c)\tMINUS 或 UNION 擇一；例：曾訂 F01 但未訂 F02 的 MID",
    ]


def _answer_c06(_text: str) -> list[str]:
    return [
        "5.",
        "\t(a)\tGrid[3][2]=1 為牆；Grid[3][3]=0 可向右移",
        "\t(b)\tPOP→5；POP→1；最終頂端=1",
    ]


def _answer_c07(_text: str) -> list[str]:
    return [
        "6.",
        "\t(a)\tDequeue 後 Front 指向下一個輪候者",
        "\t(b)\t二分：mid 取中，比較後縮小範圍（至少兩步）",
    ]


def _answer_c08(text: str) -> list[str]:
    return [
        "7.",
        "\t(a)\t首輪降序：比較 (1,2) 若 72<45 則交換 → 索引 1 與 2",
        "\t(b)\t沿 Next 由 Head 走訪；刪除 Score=45 結點要調整 Next／Head",
    ]


_WRITTEN_HANDLERS = {
    "b-01": _answer_b01,
    "b-02": _answer_b02,
    "b-03": _answer_b03,
    "b-04": _answer_b04,
    "b-05": _answer_b05,
    "b-06": _answer_b06,
    "c-01": _answer_c01,
    "c-02": _answer_c02,
    "c-03": _answer_c03,
    "c-05": _answer_c05,
    "c-06": _answer_c06,
    "c-07": _answer_c07,
    "c-08": _answer_c08,
}

_C_ORDER = ("c-01", "c-02", "c-03", "c-05", "c-06", "c-07", "c-08")


def build_model_answer_lines(spec: dict[str, Any]) -> list[str]:
    """Plain lines for answer pages (paragraph text, tabs preserved)."""
    meta = spec.get("meta") or {}
    footer = meta.get("footer") or {}
    year = footer.get("academic_year", "2025-2026")
    level = footer.get("level", "中五級")
    subject = footer.get("subject", "資訊及通訊科技")
    term = footer.get("term_exam", "下學期考試")

    lines: list[str] = [
        f"{year.replace('-', '–')} 年度　{level}　{subject}科　{term}答案",
        "甲部",
    ]
    lines.extend(_mcq_key_lines(str(meta.get("mcq_answers") or "")))
    lines.append("")
    lines.append("乙部")

    by_id = {it.id: it.text for it in spec_items(spec)}
    for sid in ("b-01", "b-02", "b-03", "b-04", "b-05", "b-06"):
        fn = _WRITTEN_HANDLERS.get(sid)
        if fn and sid in by_id:
            lines.extend(fn(by_id[sid]))
            lines.append("")

    lines.append("丙部")
    c_num = 0
    for sid in _C_ORDER:
        fn = _WRITTEN_HANDLERS.get(sid)
        if fn and sid in by_id:
            c_num += 1
            block = fn(by_id[sid])
            if block and block[0].endswith("."):
                block[0] = f"{c_num}."
            lines.extend(block)
            lines.append("")

    return lines


def attach_model_answers_to_spec(spec: dict[str, Any]) -> None:
    """Store per-slot model answer text on written items (for JSON export / verify)."""
    for row in spec.get("items") or []:
        sid = str(row.get("id") or "")
        fn = _WRITTEN_HANDLERS.get(sid)
        if not fn:
            continue
        text = str(row.get("text") or "")
        row["model_answer"] = "\n".join(fn(text))
