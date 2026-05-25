"""Generate 乙／丙 items from blueprint + style_patterns (bank ask shapes, new scenarios).

Uses `style_patterns.json` → `written.section_b|section_c.by_concept` for DSE ask patterns
(redacted). Fills placeholders with synthetic school scenarios — does not copy bank stems.
"""
from __future__ import annotations

import random
import re
from typing import Any

from exam_spec import make_item

_PLACEHOLDER_CELL = re.compile(r"\{CELL\}")
_PLACEHOLDER_N = re.compile(r"\{N\}")
_PLACEHOLDER_TABLE = re.compile(r"\{TABLE\}")
_PLACEHOLDER_STR = re.compile(r'"\{STR\}"')
_PLACEHOLDER_SQL = re.compile(r"\{SQL\}")
_SUBPART_LABEL_RE = re.compile(r"^\s*\(?[0-9]*\)?\s*\(?([a-z]{1,2}|[ivx]{1,4})\)?\s*", re.I)
_GARBAGE_PATTERN_RE = re.compile(
    r"_Q\(|Sheet\d|ctionB_Q|gemini|^\s*-\s*_Q|^\s*\([a-z]\)\s*\([a-z]\)",
    re.I,
)

_ORG_NAMES = ("青禾", "煦風", "朗晴", "博文", "德望", "真光", "培正", "聖心")
_VENUES = ("學會", "圖書館", "社", "網店", "社區中心", "醫務室", "旅行社", "社企")
_SHEET_NAMES = ("Sales", "Donation", "Score", "Order", "Member")
_TABLE_NAMES = ("ORDER", "MEMBER", "PRODUCT", "BOOKING", "ENROL")
_B02_SYSTEM_ASKS: tuple[tuple[str, str], ...] = (
    (
        "hardware",
        "就下表所列部件，各舉一例說明其功能（須與部件直接相關）。",
    ),
    (
        "io",
        "比較輸入設備與輸出設備在{場景}各一項用途。",
    ),
    (
        "os",
        "說明作業系統在此系統中的兩項職責。",
    ),
    (
        "driver",
        "使用打印機時需要驅動程式。說明驅動程式的作用，並舉出使用最新版本的一項好處。",
    ),
)

_B02_FUTURE_ASKS: tuple[str, ...] = (
    "說明人工智能可如何協助{場景}管理日常運作，並舉出一項限制。",
    "描述物聯網感應器如何改善{場景}的環境監控（舉一例）。",
    "比較在此{場景}採用雲端儲存與本地伺服器各一項優缺點。",
)

# b-01 (b) 輪換：COUNTIF / SUMIF / XLOOKUP（義賣情境；不含 RANK）
_B01_FORMULA_B: tuple[tuple[str, str], ...] = (
    (
        "COUNTIF_QTY",
        "在 G2 使用 COUNTIF 統計 D$2:D$50 中數量≥5 的訂單個數，寫出公式。",
    ),
    (
        "COUNTIF_MEMBER",
        "在 G2 使用 COUNTIF 統計 E$2:E$50 中會員訂單（「Y」）的個數，寫出公式。",
    ),
    (
        "SUMIF",
        "在 G2 使用 SUMIF：加總 B 欄為「{item}」的 F 欄總價（範圍 F$2:F$50），寫出公式。",
    ),
    (
        "EXCEL_TABLE_SUMIF",
        "在 G2 使用結構化參照：加總 Order 表格中商品為「{item}」的總價，寫出公式。",
    ),
    (
        "XLOOKUP",
        "在 G2 使用 XLOOKUP 依 B2 的商品名稱從 $H$2:$I$10 查找參考單價，寫出公式。",
    ),
)

_PATTERN_ONLY_WRITTEN = frozenset({
    "b-01", "b-02", "b-03", "b-04", "b-05", "b-06",
    "c-01", "c-02", "c-03", "c-05", "c-06", "c-07", "c-08",
})
_PATTERN_C_SLOTS = _PATTERN_ONLY_WRITTEN  # all written slots use curated stems

_HARDWARE_ASKS = (
    "完成下表，可提升{設備}的硬件規格。",
    "比較兩款{設備}在 RAM 與儲存裝置上的規格差異。",
    "除 CPU 外，舉出兩個編輯視像時須考慮的硬件部件並簡述。",
)


def _pick_weighted(patterns: list[dict[str, Any]], rng: random.Random, *, default: str) -> str:
    if not patterns:
        return default
    weights = [max(1, int(p.get("count", 1))) for p in patterns]
    return str(rng.choices(patterns, weights=weights, k=1)[0].get("text", default))


def _merge_written_patterns(
    style: dict[str, Any],
    section: str,
    concepts: list[str],
) -> dict[str, list[dict[str, Any]]]:
    written = (style.get("written") or {}).get(section) or {}
    by_c = written.get("by_concept") or {}
    verbs: list[dict] = []
    scenarios: list[dict] = []
    subparts: list[dict] = []
    for concept in concepts:
        block = by_c.get(concept) or {}
        verbs.extend(block.get("command_verbs") or [])
        scenarios.extend(block.get("scenario_frames") or [])
        subparts.extend(block.get("subpart_templates") or [])
    global_g = style.get("global") or {}
    verbs.extend(global_g.get("command_verbs") or [])
    scenarios.extend(global_g.get("scenario_frames") or [])
    return {"verbs": verbs, "scenarios": scenarios, "subparts": subparts}


def _fresh_context(rng: random.Random) -> dict[str, str]:
    org = rng.choice(_ORG_NAMES)
    venue = rng.choice(_VENUES)
    col = rng.choice("ABCDEFGH")
    row = rng.randint(2, 5)
    return {
        "org": org,
        "venue": venue,
        "cell": f"{col}{row}",
        "cell2": f"{chr(ord(col) + 1)}{row}",
        "n1": str(rng.randint(3, 9)),
        "n2": str(rng.randint(10, 99)),
        "table": rng.choice(_TABLE_NAMES),
        "sheet": rng.choice(_SHEET_NAMES),
        "year": str(rng.randint(2024, 2027)),
        "scene": f"{org}{venue}",
        "device": rng.choice(("桌上電腦", "筆記本電腦", "工作站")),
    }


def _instantiate_pattern(text: str, ctx: dict[str, str], rng: random.Random) -> str:
    t = text
    t = _PLACEHOLDER_CELL.sub(ctx["cell"], t)
    t = _PLACEHOLDER_TABLE.sub(ctx["table"], t)
    t = _PLACEHOLDER_STR.sub(f'「{ctx["org"]}」', t)
    t = _PLACEHOLDER_SQL.sub("SELECT … FROM … WHERE …", t)

    def _n_sub(_: re.Match[str]) -> str:
        return rng.choice([ctx["n1"], ctx["n2"], "24", "80"])

    t = _PLACEHOLDER_N.sub(_n_sub, t)
    t = t.replace("{場景}", ctx["scene"]).replace("{設備}", ctx["device"])
    return t.strip()


def _valid_ask_pattern(text: str) -> bool:
    t = text.strip()
    if len(t) < 10 or len(t) > 140:
        return False
    if _GARBAGE_PATTERN_RE.search(t):
        return False
    if not re.search(r"[\u4e00-\u9fff]{4,}", t):
        return False
    if re.match(r"^下列哪", t) and ("？" in t or "?" in t):
        return False
    if re.search(r"\{[A-Z_]+\}", t):
        return False
    if "算法的輸出" in t and "試算表" not in t:
        return False
    return True


def _strip_subpart_prefix(template: str) -> str:
    t = _SUBPART_LABEL_RE.sub("", template).strip()
    t = re.sub(r"^[a-z]{1,3}Q\([^)]+\)\s*", "", t, flags=re.I)
    return t.strip()


def _subpart_line(label: str, body: str, marks: int) -> str:
    from written_layout import subpart

    body = body.strip()
    if not body:
        body = "回答此部分。"
    depth = 2 if len(label) <= 3 and label[0].lower() in "ivx" else 1
    return subpart(label, body, marks, depth=depth)


def _pick_or_default(
    patterns: dict[str, list[dict[str, Any]]],
    rng: random.Random,
    *,
    default: str,
    must_match: re.Pattern[str],
) -> str:
    picked = _pick_subpart_ask(patterns, rng, focus="", default=default, filter_re=must_match)
    return picked if must_match.search(picked) else default


def _pick_subpart_ask(
    patterns: dict[str, list[dict[str, Any]]],
    rng: random.Random,
    *,
    focus: str,
    default: str,
    filter_re: re.Pattern[str] | None = None,
) -> str:
    pool = list(patterns.get("subparts") or []) + list(patterns.get("verbs") or [])
    pool = [p for p in pool if _valid_ask_pattern(str(p.get("text", "")))]
    if filter_re:
        filtered = [p for p in pool if filter_re.search(p.get("text", ""))]
        if filtered:
            pool = filtered
    if not pool:
        return default
    raw = _pick_weighted(pool, rng, default=default)
    cleaned = _strip_subpart_prefix(raw)
    return cleaned if _valid_ask_pattern(cleaned) else default


def _scenario_opening(
    patterns: dict[str, list[dict[str, Any]]],
    rng: random.Random,
    ctx: dict[str, str],
    *,
    default: str,
) -> str:
    scenarios = [
        p for p in (patterns.get("scenarios") or []) if _valid_ask_pattern(str(p.get("text", "")))
    ]
    raw = _pick_weighted(scenarios, rng, default=default)
    if raw and "？" not in raw and "?" not in raw and len(raw) > 18:
        inst = _instantiate_pattern(raw, ctx, rng)
        if _valid_ask_pattern(inst):
            return inst
    return default.format(**ctx) if "{" in default else default


def generate_written_text(
    slot: dict[str, Any],
    style: dict[str, Any],
    rng: random.Random,
) -> tuple[str, list[str]]:
    """Return (body text, pattern_sources used for provenance)."""
    sid = str(slot["id"])
    section = str(slot["section"])
    concepts = list(slot.get("concepts") or [])
    subparts = list(slot.get("subparts") or [])
    try:
        from iclass_hk_depth import (
            depth_references_for_slot,
            pick_iclass_written,
            slot_uses_iclass_depth,
        )

        if sid not in _PATTERN_ONLY_WRITTEN and sid not in _PATTERN_C_SLOTS and slot_uses_iclass_depth(slot):
            iclass_body = pick_iclass_written(slot, rng, min_tier="intermediate")
            if iclass_body:
                refs = [
                    f"iclass-hk://depth/{r.get('id')}"
                    for r in depth_references_for_slot(slot, limit=2)
                ]
                return iclass_body, [f"pattern://{section}/{sid}", *refs]
    except ImportError:
        pass

    patterns = _merge_written_patterns(style, section, concepts)
    ctx = _fresh_context(rng)
    sources: list[str] = [f"pattern://{section}/{sid}"]
    lines: list[str] = []

    if sid == "b-01":
        sheet = ctx["sheet"]
        lines.append(
            f"「{ctx['org']}書社」以試算表「{sheet}」記錄義賣收入（{sheet} 範圍已設定為 Excel 表格）；"
            "PriceRef 為參考單價對照。部分資料見下表。"
        )
        mk_a = subparts[0]["marks"] if subparts else 2
        mk_b = subparts[1]["marks"] if len(subparts) > 1 else 2
        lines.append(
            _subpart_line(
                "a",
                "在 F2 寫出一條 IF 公式並複製至 F3:F50：若 E2 為「Y」且 D2≥5，"
                "總價為 C2*D2×0.9；否則為 C2*D2。寫出 F2 的公式。",
                mk_a,
            )
        )
        fn, tpl = rng.choice(_B01_FORMULA_B)
        b = tpl.format(item=rng.choice(["明信片", "布袋", "徽章"]))
        sources.append(f"pattern://formula/{fn}")
        lines.append(_subpart_line("b", b, mk_b))

    elif sid == "b-02":
        lines.append(
            f"「{ctx['org']}」為{ctx['venue']}添置桌上電腦，下表列出電腦 A 與電腦 B 的硬件規格"
            "（請細看下表各列的數值與類型）。"
        )
        mk_a = subparts[0]["marks"] if subparts else 2
        mk_b = subparts[1]["marks"] if len(subparts) > 1 else 3
        lines.append(
            _subpart_line(
                "a",
                "根據下表，說明電腦 A 通常適合甚麼用途？電腦 B 通常適合甚麼用途？"
                "（各舉一例，須寫明引用下表哪一項規格，例如 RAM 或主儲存）",
                mk_a,
            )
        )
        lines.append(
            _subpart_line(
                "b",
                "若須同時開啟病人管理系統及醫療影像軟件，應選購電腦 A 還是電腦 B？"
                "須引用下表至少兩項規格（例如 RAM、主儲存、顯示卡）說明理由。",
                mk_b,
            )
        )

    elif sid == "b-03":
        w, h = rng.choice([(1600, 1200), (1920, 1080)])
        n_img = rng.choice([40, 60, 80])
        lines.append(
            f"{ctx['org']}{ctx['venue']}以未壓縮 BMP 儲存相片："
            f"每張 {w}×{h} 像素、24 bit 真彩色。"
        )
        mk_a = subparts[0]["marks"] if subparts else 2
        mk_b = subparts[1]["marks"] if len(subparts) > 1 else 2
        lines.append(
            _subpart_line(
                "a",
                f"估算 {n_img} 張相片的總檔案大小（MB），須展示計算步驟。",
                mk_a,
            )
        )
        lines.append(
            _subpart_line(
                "b",
                "比較以 JPEG（有損）與 PNG（無損）儲存同一批相片的取捨。",
                mk_b,
            )
        )

    elif sid == "b-04":
        arr = [9, 8, 5, 7, 9, 6]
        key = 5
        lines.append("考慮陣列 A（索引由 1 開始，n=6）及以下線性搜尋算法：")
        lines.append("found ← FALSE")
        lines.append("i ← 1")
        lines.append("WHILE i ≤ n AND found = FALSE DO")
        lines.append("    IF A[i] = key THEN found ← TRUE")
        lines.append("    i ← i + 1")
        lines.append("ENDWHILE")
        lines.append("IF found = TRUE THEN OUTPUT i ELSE OUTPUT 0")
        mk_a = subparts[0]["marks"] if subparts else 2
        mk_b = subparts[1]["marks"] if len(subparts) > 1 else 2
        lines.append(
            _subpart_line(
                "a",
                f"設 A = {arr}、key = {key}。完成追蹤表，列出每次迴圈後 i 與 found 的值，"
                "並寫出最終 OUTPUT。",
                mk_a,
            )
        )
        lines.append(
            _subpart_line("b", "說明此算法屬線性搜尋的原因。", mk_b),
        )

    elif sid == "b-05":
        lines.append(
            f"「{ctx['org']}」網店使用資料表 TRANSACTION(TID, Item, Qty, ADate) 記錄交易，"
            "部分記錄見表。"
        )
        mk_a = subparts[0]["marks"] if subparts else 2
        mk_b = subparts[1]["marks"] if len(subparts) > 1 else 2
        lines.append(
            _subpart_line(
                "a",
                "寫出 CREATE TABLE TRANSACTION（TID 為主鍵，Item 不可為空）。",
                mk_a,
            )
        )
        lines.append(
            _subpart_line(
                "b",
                "寫出一條 SELECT，列出 Qty ≥ 5 的 Item 及 Qty。",
                mk_b,
            )
        )

    elif sid == "b-06":
        lines.append(
            f"攝影學會擬為社員添置{ctx['device']}，完成下表比較兩款候選硬件規格。"
        )
        parts_marks = [sp["marks"] for sp in subparts] if subparts else [2, 2, 2, 3]
        prompts = (
            "列出 CPU 規格欄可填寫的兩個例子。",
            "說明增加 RAM 對多工處理的影響。",
            "比較 SSD 與 HDD 作為系統碟的優缺點。",
            "舉出一項須同時升級硬件與軟件的情況並說明。",
        )
        for lab, pm, pr in zip("abcd", parts_marks, prompts, strict=False):
            lines.append(_subpart_line(lab, pr, pm))

    elif sid == "c-01":
        lines.append(
            f"「{ctx['org']}」開發會員預訂系統：每位會員可建立多筆預訂；"
            "每筆預訂對應一個場次；每個場次屬一間戲院。"
        )
        lines.append(
            _subpart_line(
                "a",
                "繪製實體關係圖（ERD），須包括 Member、Booking、Screening、Cinema，"
                "並標示主鍵及外鍵。",
                slot.get("marks", 6),
            )
        )

    elif sid == "c-02":
        lines.append(f"「{ctx['org']}」圖書館使用 MEMBER 及 LOAN 資料表，須符合欄位限制。")
        mk_a, mk_b = 2, 2
        if subparts and len(subparts) >= 2:
            mk_a, mk_b = subparts[0]["marks"], subparts[1]["marks"]
        lines.append(
            _subpart_line(
                "a",
                "在下列 CREATE TABLE LOAN 補充 MID 主鍵及 TITLE 的 NOT NULL 限制。",
                mk_a,
            )
        )
        lines.append(
            _subpart_line(
                "b",
                "說明外鍵 LOAN(MID) REFERENCES MEMBER(MID) 如何維護參照完整性。",
                mk_b,
            )
        )

    elif sid == "c-03":
        lines.append(
            f"「{ctx['org']}」早期把會員姓名、電話直接寫入每筆 LOAN；"
            "同一會員借多本書時資料重複，更改電話須更新多筆記錄。"
        )
        mk_a, mk_b = 2, 2
        if subparts and len(subparts) >= 2:
            mk_a, mk_b = subparts[0]["marks"], subparts[1]["marks"]
        lines.append(
            _subpart_line(
                "a",
                "指出上述設計的數據冗餘，並說明可能導致的更新異常。",
                mk_a,
            )
        )
        lines.append(
            _subpart_line(
                "b",
                "建議如何分拆資料表以改善完整性（述主鍵／外鍵角色，不須完整 ERD）。",
                mk_b,
            )
        )

    elif sid == "c-05":
        lines.append(
            "社區中心資料庫含 MEMBER(MID, MName)、FACILITY(FID, FName)、"
            "RESERVE(RID, MEMID, FID, RDATE)（見表）。"
        )
        defaults = (
            ("a", "寫出 INNER JOIN：列出每位會員姓名及其預訂的設施名稱。", 2),
            ("b", "寫出 GROUP BY：統計各設施被預約次數，只列出次數≥2 的設施。", 2),
            ("c", "寫出 UNION 或 MINUS：比較兩組設施的會員／預約差異（擇一並說明）。", 2),
        )
        marks_by_label = {sp["label"]: sp["marks"] for sp in subparts} if subparts else {}
        for lab, ask, default_mk in defaults:
            mk = marks_by_label.get(lab, default_mk)
            lines.append(_subpart_line(lab, ask, mk))

    elif sid == "c-06":
        lines.append(
            "某遊戲以二維陣列 Grid[row][col] 表示地圖（0=通道，1=牆）；"
            "玩家移動及「復活」位置以堆疊記錄。"
        )
        mk_a, mk_b = 3, 4
        if subparts and len(subparts) >= 2:
            mk_a, mk_b = subparts[0]["marks"], subparts[1]["marks"]
        lines.append(
            _subpart_line(
                "a",
                "寫出判斷 Grid[3][2] 是否為牆的條件；若 Grid[3][2]=1 且 Grid[3][3]=0，說明能否向右移。",
                mk_a,
            )
        )
        lines.append(
            _subpart_line(
                "b",
                "依次 PUSH 2、5、9、POP、PUSH 1、POP，列出每次 POP 的輸出及最終堆疊頂端。",
                mk_b,
            )
        )

    elif sid == "c-07":
        lines.append(
            "診所輪候系統以隊列處理先到先得；學生證編號已按升序存入陣列 "
            "ID = [\"S1001\", \"S1010\", \"S1042\", \"S1088\", \"S1100\"]（索引 1 至 5）。"
        )
        mk_a, mk_b = 3, 4
        if subparts and len(subparts) >= 2:
            mk_a, mk_b = subparts[0]["marks"], subparts[1]["marks"]
        lines.append(
            _subpart_line(
                "a",
                "說明 Enqueue／Dequeue 如何實現輪候；舉一例 Dequeue 後 Front 及 Rear 的變化。",
                mk_a,
            )
        )
        lines.append(
            _subpart_line(
                "b",
                "用二分搜尋在 ID 中查找「S1042」，描述 mid 如何移動（至少兩步）。",
                mk_b,
            )
        )

    elif sid == "c-08":
        lines.append(
            "電競社以陣列 Next[1..N] 及 Head 模擬鏈表儲存輪候參賽者；每日關閉前須把 Score[1..M] "
            "按降序整理並更新鏈表順序。"
        )
        lines.append(
            "管理員記錄：Score = [72, 45, 90, 45, 61, 88, 33, 77]（索引 1 至 8）；"
            "Head = 1；Next = [2, 3, 4, 5, 6, 7, 8, 0]（0 表示無下一個）。"
        )
        mk_a, mk_b = 2, 4
        if subparts and len(subparts) >= 2:
            mk_a, mk_b = subparts[0]["marks"], subparts[1]["marks"]
        lines.append(
            _subpart_line(
                "a",
                "對 Score 執行一次冒泡排序（降序）的首輪比較，寫出需交換的一對索引。",
                mk_a,
            )
        )
        lines.append(
            _subpart_line(
                "b",
                "說明如何以 Head 及 Next[] 走訪仍參賽者；刪除一個 Score=45 的結點後，"
                "描述 Head／Next 如何更新，並述此結構與陣列模擬鏈表的優點。",
                mk_b,
            )
        )

    else:
        title = slot.get("title", sid)
        lines.append(f"（{title}）")
        concepts_s = "、".join(concepts)
        lines.append(_subpart_line("a", f"解釋與{concepts_s}相關的一個概念。", 2))

    body = "\n\n".join(lines)
    return body, sources


def generate_written_item(
    slot: dict[str, Any],
    style: dict[str, Any],
    rng: random.Random,
) -> dict[str, Any]:
    text, sources = generate_written_text(slot, style, rng)
    sid = str(slot["id"])
    item = make_item(
        sid,
        str(slot["section"]),
        text,
        marks=slot.get("marks", 1),
        title=slot.get("title"),
        concepts=list(slot.get("concepts") or []),
        dse_source=f"generated://pattern/{sid}",
        dse_sources=sources,
        composition="pattern_generate",
    )
    try:
        from iclass_hk_depth import attach_depth_references

        attach_depth_references(item, slot)
    except ImportError:
        pass
    return item


def generate_written_items_from_blueprint(
    blueprint: dict[str, Any],
    style: dict[str, Any],
    *,
    seed: int,
) -> list[dict[str, Any]]:
    from f5_ict_written_from_dse import WRITTEN_SLOT_PLAN

    order = [sid for sid, *_ in WRITTEN_SLOT_PLAN]
    slot_by_id = {
        str(s["id"]): s for s in blueprint.get("slots") or [] if str(s.get("id", "")).startswith(("b-", "c-"))
    }
    items: list[dict] = []
    for sid in order:
        slot = slot_by_id.get(sid)
        if not slot:
            continue
        h = sum(ord(c) for c in f"{seed}:{sid}")
        rng = random.Random(h & 0xFFFFFFFF)
        items.append(generate_written_item(slot, style, rng))
    return items
