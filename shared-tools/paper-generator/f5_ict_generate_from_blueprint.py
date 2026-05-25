"""Generate exam spec items from blueprint + style_patterns (no DSE bank copy)."""
from __future__ import annotations

import json
import random
import re
import sys
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[2]
_QCHECK = Path(__file__).resolve().parents[1] / "question-quality-check"
_FMT = Path(__file__).resolve().parents[1] / "paper-formatter"
for _p in (_QCHECK, _FMT):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from dse_ict_style import COMBO_OPTS_1_AND_3, style_meta  # noqa: E402
from exam_spec import build_spec, make_item  # noqa: E402
from spec_mcq_render import MCQ_SPANS  # noqa: E402

# Combo MCQ needs span ≥ 10 (stem + (1)(2)(3) + blank + A–D); six 組合題 per paper.
# Template row spans (MCQ_SPANS) must be ≥10 for (1)(2)(3)+options — see spec_mcq_render.MCQ_SPANS.
# Slots 14/23 have span 6/9 in 24_25 template — use 13/15 instead (both span ≥10).
_COMBO_SLOT_IDS = (6, 8, 13, 15, 21, 28)
_COMBO_SLOTS = frozenset(
    i for i in _COMBO_SLOT_IDS if MCQ_SPANS[i - 1] >= 10
)
# Curated 試算表／數據庫 MCQ (text-only); mcq-06/13/15 get DOCX tables on render.
_CURATED_MCQ_SLOTS = frozenset({3, 4, 10})
_COMBO_EXTRA: dict[int, str] = {
    6: "試算表「Sale」部分資料見下表。",
    8: "學生以數位相機拍攝活動相片。",
    13: "試算表「Donate」及「Target」部分資料見下表。",
    15: "圖書館借書記錄見下表。",
    21: "編寫程式時把任務分成多個子程式。",
    28: "陣列與鏈表模擬輪候名單。",
}
_COMBO_SCENARIOS = (
    "某校使用資訊系統管理學與教數據。",
    "某圖書館以電腦記錄借還書及罰款。",
    "某校運動會以試算表記錄各項成績。",
    "某網店以系統處理訂單與庫存。",
    "某醫務室以電腦登記求診記錄。",
    "某校學會以系統管理會員及活動報名。",
    "某旅行社以電腦處理機票預訂。",
)


def _load_json(path: Path) -> dict:
    return json.loads(path.expanduser().resolve().read_text(encoding="utf-8"))


def _slot_rng(slot_id: str, seed: int) -> random.Random:
    h = sum(ord(c) for c in f"{seed}:{slot_id}")
    return random.Random(h & 0xFFFFFFFF)


def _pick_pattern(
    patterns: list[dict[str, Any]],
    rng: random.Random,
    *,
    default: str,
) -> str:
    if not patterns:
        return default
    weights = [max(1, int(p.get("count", 1))) for p in patterns]
    chosen = rng.choices(patterns, weights=weights, k=1)[0]
    return str(chosen.get("text", default))


def _concept_style(
    style: dict[str, Any],
    concepts: list[str],
) -> dict[str, list[dict[str, Any]]]:
    by = style.get("by_concept") or {}
    verbs: list[dict] = []
    terms: list[dict] = []
    scenarios: list[dict] = []
    for c in concepts:
        block = by.get(c) or {}
        verbs.extend(block.get("command_verbs") or [])
        terms.extend(block.get("terminology") or [])
        scenarios.extend(block.get("scenario_frames") or [])
    global_g = style.get("global") or {}
    verbs.extend(global_g.get("command_verbs") or [])
    terms.extend(global_g.get("terminology") or [])
    scenarios.extend(global_g.get("scenario_frames") or [])
    return {"verbs": verbs, "terms": terms, "scenarios": scenarios}


def _format_mcq(stem: str, options: list[str], correct_idx: int, rng: random.Random) -> tuple[str, str]:
    pairs = list(enumerate(options))
    rng.shuffle(pairs)
    letters = "ABCD"
    lines = [stem.rstrip(), ""]
    correct_letter = "A"
    for i, (orig_i, text) in enumerate(pairs):
        letter = letters[i]
        if orig_i == correct_idx:
            correct_letter = letter
        lines.append(f"\t{letter}.\t{text}")
    return "\n".join(lines), correct_letter


def _format_mcq_fixed(stem: str, options: list[str], correct_idx: int) -> tuple[str, str]:
    """Combo MCQ: do not shuffle options (DSE combination order)."""
    lines = [stem.rstrip(), ""]
    for i, text in enumerate(options):
        lines.append(f"\t{'ABCD'[i]}.\t{text}")
    return "\n".join(lines), "ABCD"[correct_idx]


def _combo_subitems(
    primary: str,
    concepts: list[str],
    idx: int,
    *,
    variant: int = 0,
) -> tuple[str, str, str]:
    if idx == 13:
        sheet_sets = (
            (
                "XLOOKUP 可依關鍵值在對照範圍查找並傳回結果",
                "COUNTIF 用於加總兩欄的乘積",
                "SUMIF 只能統計儲存格個數",
            ),
        )
        return sheet_sets[variant % len(sheet_sets)]
    if idx == 15:
        db_sets = (
            (
                "主鍵可唯一識別資料表內每一筆記錄",
                "同一欄位可同時儲存文字與圖片檔",
                "記錄與欄位是相同的概念",
            ),
            (
                "SELECT 可從資料表讀取記錄",
                "主鍵值可以重複以方便搜尋",
                "欄位名稱必須與記錄數目相同",
            ),
        )
        return db_sets[variant % len(db_sets)]
    if idx == 2:
        db_sets = (
            (
                "主鍵可唯一識別資料表內每一筆記錄",
                "同一欄位可同時儲存文字與圖片檔",
                "記錄與欄位是相同的概念",
            ),
            (
                "外鍵欄位用於連結兩個資料表",
                "主鍵值可以重複以方便搜尋",
                "欄位名稱必須與記錄數目相同",
            ),
        )
        return db_sets[variant % len(db_sets)]
    if idx == 6:
        sheet_sets = (
            (
                "COUNTIF 可統計符合條件的儲存格個數",
                "SUMIF 加總時毋須指定條件範圍",
                "XLOOKUP 只能查找同一欄內的數字",
            ),
            (
                "SUMIF 可按條件加總指定欄",
                "COUNTIF 只能加總數值欄的總和",
                "合併儲存格後所有函數仍不受影響",
            ),
        )
        return sheet_sets[variant % len(sheet_sets)]
    c2 = concepts[1] if len(concepts) > 1 else primary
    c3 = concepts[2] if len(concepts) > 2 else concepts[-1] if concepts else primary
    if primary == "多媒體" or "多媒體" in concepts:
        media_sets = (
            ("JPEG 可用有損壓縮減少檔案大小", "向量圖以像素逐點描述", "解析度不影響相片像素數目"),
            ("無損壓縮適合醫學影像備份", "BMP 必定比 MP3 細小", "顏色深度與聲道數相同"),
        )
        return media_sets[variant % len(media_sets)]
    if primary == "排序" or "排序" in concepts:
        sort_sets = (
            ("氣泡排序可把相鄰逆序元素交換", "已排序陣列無需任何比較", "排序只適用於文字檔"),
            ("合併排序需要額外記憶空間", "排序後主鍵會改變", "搜尋必定比排序快"),
            ("偽代碼 WHILE 迴圈可實現冒泡排序", "陣列索引由 0 開始", "排序必定比搜尋快"),
        )
        return sort_sets[variant % len(sort_sets)]
    if "程式測試" in concepts or "邊界值" in concepts:
        test_sets = (
            ("邊界值可檢驗極端輸入", "語法錯誤必定增加儲存空間", "邏輯錯誤只適用於試算表"),
            ("測試應包含正常與異常情況", "只測試輸出格式即可", "不必測試 IF 分支"),
        )
        return test_sets[variant % len(test_sets)]
    variants = (
        (f"{primary}可提高數據準確性", f"{c2}只適用於紙本文件", f"{c3}屬於輸出階段"),
        (f"{primary}屬於數據處理的一環", f"{c2}與硬件無關", f"{c3}不能與欄位同時使用"),
        (f"{primary}有助防止輸入錯誤", f"{c2}必定增加儲存空間", f"{c3}只適用於試算表"),
        (f"{primary}可在輸入階段使用", f"{c2}會取代備份程序", f"{c3}只適用於圖像檔案"),
        (f"{primary}與數據完整性有關", f"{c2}只適用於網絡傳輸", f"{c3}屬於輸入階段"),
        (f"{primary}可減少重複輸入", f"{c2}不能與記錄並存", f"{c3}只適用於音訊"),
        (f"{primary}有助驗證輸入", f"{c2}只適用於輸出裝置", f"{c3}與進制無關"),
    )
    return variants[(idx + variant) % len(variants)]


def _curated_mcq_database(idx: int, rng: random.Random, *, variant: int = 0) -> tuple[str, str]:
    """Curated Core A 數據組織／檔案（無附表）。"""
    sets = (
        (
            "圖書館資料表 MEMBER(MID, Name) 與 LOAN(MID, BookID)。下列哪項正確？",
            ["LOAN.MID 是外鍵，對應 MEMBER.MID", "Name 是主鍵", "BookID 是外鍵", "MID 可重複出現於 MEMBER"],
            0,
        ),
        (
            "學生檔案以學號、姓名、班別三個欄位儲存。下列哪項正確？",
            ["一筆記錄對應一名學生", "一個欄位對應一名學生", "學號是記錄", "記錄與欄位相同"],
            0,
        ),
        (
            "資料表 BOOK(BookID, Title) 中，BookID 設定為主鍵。下列哪項正確？",
            ["BookID 值不可重複", "Title 必須是數字", "每個欄位只能有一筆記錄", "主鍵可留空"],
            0,
        ),
    )
    stem, opts, ans = sets[(idx + variant) % len(sets)]
    return _format_mcq(stem, list(opts), ans, rng)


def _curated_mcq_spreadsheet(idx: int, rng: random.Random, *, variant: int = 0) -> tuple[str, str]:
    """Curated Core A 試算表（情境與儲存格寫在題幹，無附表）。"""
    sets = (
        (
            "義賣工作表：B 欄商品、C 欄單價、D 欄數量、F 欄總價（=C×D）。"
            "要在 G2 統計 D 欄數量≥5 的個數，應使用？",
            ["COUNTIF", "SUMIF", "XLOOKUP", "IF"],
            0,
        ),
        (
            "捐款工作表：A 欄班別、C 欄金額。要在 D2 依 A2 從 $H$2:$I$10 查找目標金額，應使用？",
            ["XLOOKUP", "COUNTIF", "SUMIF", "RANK"],
            0,
        ),
        (
            "工作表 F 欄記錄總價。要在 G2 加總 B 欄為「明信片」的 F 欄金額，應使用？",
            ["SUMIF", "COUNTIF", "XLOOKUP", "AVERAGE"],
            0,
        ),
    )
    stem, opts, ans = sets[(idx + variant) % len(sets)]
    return _format_mcq(stem, list(opts), ans, rng)


def _curated_mcq_file_access(idx: int, rng: random.Random, *, variant: int = 0) -> tuple[str, str]:
    sets = (
        (
            "圖書館以書號作索引，輸入書號即可讀取該書資料。這屬於哪種存取方式？",
            ["直接存取", "順序存取", "只能順序存取", "與索引無關"],
            0,
        ),
        (
            "MEMBER 表的 MID 為主鍵。新增會員時 MID 不可與現有記錄重複，主要為了維護哪項完整性？",
            ["實體完整性", "參照完整性", "域完整性", "檔案完整性"],
            0,
        ),
    )
    stem, opts, ans = sets[variant % len(sets)]
    return _format_mcq(stem, list(opts), ans, rng)


def _permute_mcq_to_letter(text: str, current: str, target: str) -> tuple[str, str]:
    if current == target:
        return text, target
    lines = text.splitlines()
    opt_re = re.compile(r"^\t([A-D])\.\t(.+)$")
    prefix: list[str] = []
    opts: list[tuple[str, str]] = []
    suffix: list[str] = []
    phase = "prefix"
    for line in lines:
        m = opt_re.match(line)
        if m:
            phase = "opts"
            opts.append((m.group(1), m.group(2)))
        elif phase == "opts" and not m and line.strip():
            suffix.append(line)
        elif phase == "prefix":
            prefix.append(line)
        else:
            suffix.append(line)
    if len(opts) != 4:
        return text, current
    correct_text = next(t for L, t in opts if L == current)
    wrong = [t for L, t in opts if L != current]
    rng = random.Random(sum(ord(c) for c in text + target))
    rng.shuffle(wrong)
    new_opts = wrong[: ord(target) - ord("A")] + [correct_text] + wrong[ord(target) - ord("A") :]
    new_lines = prefix + [""] + [f"\t{L}.\t{t}" for L, t in zip("ABCD", new_opts)] + suffix
    return "\n".join(new_lines).rstrip() + "\n", target


def _remap_combo_mcq(text: str, target: str) -> tuple[str, str]:
    lines = text.splitlines()
    sub: list[str] = []
    prefix: list[str] = []
    for line in lines:
        m = re.match(r"^\t\((\d+)\)\t(.+)$", line)
        if m:
            sub.append(m.group(2))
        elif not re.match(r"^\t[A-D]\.", line) and line.strip() and not sub:
            prefix.append(line)
    if len(sub) != 3:
        return text, target
    stem = "\n".join(prefix)
    return _format_combo_mcq(stem, tuple(sub), "ABCD".index(target), random.Random(0))


def _rebalance_mcq_answers(items: list[dict], *, seed: int) -> None:
    from answer_pattern_check import generate_random_balanced_letters

    mcq = [it for it in items if it.get("section") == "mcq"]
    if not mcq:
        return
    target_key = generate_random_balanced_letters(
        len(mcq), "ABCD", rng=random.Random(seed ^ 0xA5A5)
    )
    for it, tgt in zip(mcq, target_key):
        cur = str(it.get("answer") or "A")[:1].upper()
        idx = int(re.search(r"(\d+)$", it["id"]).group(1)) if re.search(r"(\d+)$", it["id"]) else 1
        if idx in _COMBO_SLOTS:
            it["text"], it["answer"] = _remap_combo_mcq(it["text"], tgt)
        else:
            it["text"], it["answer"] = _permute_mcq_to_letter(it["text"], cur, tgt)


def _format_combo_mcq(
    stem: str,
    subitems: tuple[str, str, str],
    correct_combo_idx: int,
    rng: random.Random,
) -> tuple[str, str]:
    body = stem.rstrip() + "\n" + "\n".join(
        f"\t({i})\t{t}\t" for i, t in enumerate(subitems, 1)
    )
    opts = list(COMBO_OPTS_1_AND_3)
    return _format_mcq_fixed(body, opts, correct_combo_idx)


def _generate_core_d_mcq(
    idx: int,
    concepts: list[str],
    rng: random.Random,
    *,
    variant: int = 0,
) -> tuple[str, str]:
    """Core D MCQ (slots 21–30): prefer pseudocode / Python trace questions."""
    v = (idx + variant) % 8
    templates: dict[int, tuple[str, list[str], int]] = {
        21: (
            "考慮以下程序 CalcSum(n)，把 1 至 n 的總和輸出：\n"
            "total ← 0\n"
            "重複 i 由 1 至 n：total ← total + i\n"
            "輸出 total\n"
            "下列哪項最能描述此設計運用的計算思維技巧？",
            ["問題分解", "備份", "編譯", "格式化"],
            0,
        ),
        22: (
            "考慮以下偽代碼：\n"
            "count ← 0\n"
            "當 count < 3：輸出 count；count ← count + 1\n"
            "執行後會輸出什麼？",
            ["0, 1, 2", "1, 2, 3", "0, 1, 2, 3", "3"],
            0,
        ),
        23: (
            "執行下列 Python 程式後，變數 i 的最終值是多少？\n"
            "i = 1\n"
            "while i <= 8:\n"
            "    i = i * 2",
            ["16", "8", "4", "2"],
            0,
        ),
        24: (
            "執行下列 Python 程式後，列表 nums 的內容是什麼？\n"
            "nums = [3, 1, 4, 2]\n"
            "for k in range(1, len(nums)):\n"
            "    if nums[k] < nums[k - 1]:\n"
            "        nums[k], nums[k - 1] = nums[k - 1], nums[k]",
            ["[1, 3, 4, 2]", "[3, 1, 2, 4]", "[3, 4, 1, 2]", "[1, 2, 3, 4]"],
            0,
        ),
        25: (
            "考慮以下偽代碼，陣列 A[1..5]=[3,1,4,2,9]，尋找 4：\n"
            "found ← 假；i ← 1\n"
            "當 i ≤ 5 且 found = 假\n"
            "  若 A[i] = 4 則 found ← 真；i ← i + 1\n"
            "輸出 i\n"
            "輸出是？",
            ["3", "1", "5", "0"],
            0,
        ),
        26: (
            "考慮以下偽代碼：\n"
            "x ← 2\n"
            "y ← x + 3\n"
            "x ← x + 1\n"
            "輸出 y\n"
            "輸出是？",
            ["5", "3", "6", "2"],
            0,
        ),
        27: (
            "考慮以下偽代碼：\n"
            "若 (score ≥ 60) 且 (score ≤ 100) 則 grade ←「合格」，否則 grade ←「不合格」\n"
            "若 score = 60，grade 是？",
            ["合格", "不合格", "60", "100"],
            0,
        ),
        28: (
            "執行下列 Python 程式後，輸出是什麼？\n"
            "total = 0\n"
            "for n in [2, 5, 0, 3]:\n"
            "    if n == 0:\n"
            "        break\n"
            "    total = total + n\n"
            "print(total)",
            ["7", "10", "0", "5"],
            0,
        ),
        29: (
            "測試「輸入 n；若 n = 0 則輸出 zero」時，下列哪個是適當邊界個案？",
            ["n = 0", "n = 5", "n = 10", "只測試 n = 1"],
            0,
        ),
        30: (
            "考慮以下偽代碼：\n"
            "total ← 0\n"
            "重複 i 由 1 至 5\n"
            "  total ← total + A[i]\n"
            "輸出 total\n"
            "變數 total 的作用是什麼？",
            ["累加陣列元素總和", "儲存迴圈次數", "輸出單一元素", "重置索引 i"],
            0,
        ),
    }
    if idx in templates:
        stem, opts, ans = templates[idx]
        return _format_mcq(stem, opts, ans, rng)
    if "流程圖" in concepts:
        return _format_mcq(
            "在流程圖中，菱形符號通常表示什麼？",
            ["判斷／分支", "輸入", "輸出", "程序開始"],
            0,
            rng,
        )
    if "排序" in concepts:
        return _format_mcq(
            "以冒泡排序處理陣列 [3, 1, 4, 2]，第一趟完成後陣列會變成什麼？",
            ["[1, 3, 2, 4]", "[1, 3, 4, 2]", "[3, 1, 2, 4]", "[1, 2, 3, 4]"],
            0,
            rng,
        )
    if "模組" in concepts:
        return _format_mcq(
            "把程式分成多個子程式（模組）的主要好處是什麼？",
            ["提高可讀性與重用性", "減少變量數目", "取消測試需要", "只能執行一次"],
            0,
            rng,
        )
    fallbacks = (
        (
            "下列哪一項正確描述「迭代」？",
            ["重複執行某步驟直至條件成立", "只執行一次", "不能與迴圈並用", "必定用遞歸實現"],
            0,
        ),
        (
            "下列哪一項是正確的賦值語句（偽代碼）？",
            ["count ← count + 1", "count + 1 ← count", "count == count + 1", "count ← ← 1"],
            0,
        ),
    )
    stem, opts, ans = fallbacks[v % len(fallbacks)]
    return _format_mcq(stem, list(opts), ans, rng)


def _generate_mcq(
    slot: dict[str, Any],
    style: dict[str, Any],
    rng: random.Random,
    *,
    variant: int = 0,
) -> tuple[str, str]:
    concepts = list(slot.get("concepts") or [])
    core = str(slot.get("core") or "A")
    primary = concepts[0] if concepts else "資訊處理"
    idx = int(re.search(r"(\d+)$", slot["id"]).group(1)) if re.search(r"(\d+)$", slot["id"]) else 1

    if idx in _CURATED_MCQ_SLOTS:
        if idx == 10:
            return _curated_mcq_spreadsheet(idx, rng, variant=variant)
        if idx == 4:
            return _curated_mcq_file_access(idx, rng, variant=variant)
        return _curated_mcq_database(idx, rng, variant=variant)

    if idx in _COMBO_SLOTS:
        sub = _combo_subitems(primary, concepts, idx, variant=variant)
        scenario = _COMBO_SCENARIOS[(idx - 1 + variant) % len(_COMBO_SCENARIOS)]
        extra = _COMBO_EXTRA.get(idx, "")
        topic = primary
        if idx in (6, 13):
            topic = "試算表"
        elif idx == 15:
            topic = "數據庫"
        if idx == 6:
            stem = f"{scenario}{extra}以下哪項（些）關於{topic}的敘述是正確的？"
        else:
            stem_tpls = (
                f"{scenario}{extra}以下哪項（些）關於{topic}的敘述是正確的？",
                f"{scenario}{extra}下列哪項（些）與{topic}有關的說法正確？",
                f"就{topic}而言，{scenario}{extra}以下哪項（些）正確？",
                f"{scenario}在處理{topic}時，{extra}以下哪項（些）成立？",
            )
            stem = stem_tpls[variant % len(stem_tpls)]
        # Subitems curated so (1) only is true → A
        return _format_combo_mcq(stem, sub, 0, rng)

    try:
        from iclass_hk_depth import try_iclass_mcq

        adapted = try_iclass_mcq(slot, rng, variant=variant)
        if adapted is not None:
            stem, opts, ans = adapted
            return _format_mcq(stem, opts, ans, rng)
    except ImportError:
        pass

    if core == "A":
        stems = {
            "資訊處理": (
                "以下哪一項最能描述「資訊」與「數據」的關係？",
                ["數據經處理後成為資訊", "資訊必定以數字儲存", "數據不能重複使用", "資訊不需要儲存"],
                0,
            ),
            "數據組織": (
                "下列哪一項正確描述欄位與記錄？",
                ["欄位是記錄內的一個項目", "記錄是欄位內的一個項目", "欄位與記錄相同", "記錄不能包含多個欄位"],
                0,
            ),
            "進制": (
                "8 位元二進制補碼可表示的整數範圍是什麼？",
                ["-128 至 127", "-255 至 255", "0 至 255", "-127 至 128"],
                0,
            ),
            "多媒體": (
                "下列哪項較可能採用無損壓縮？",
                ["醫學掃描影像的備份", "串流音樂檔案", "網上影片串流", "社交媒體相片"],
                0,
            ),
            "試算表": (
                "工作表記錄各班捐款。要依「班別」欄查找對應「目標金額」，最適合使用哪個函數？",
                ["XLOOKUP", "COUNTIF", "SUMIF", "IF"],
                0,
            ),
        }
        if "欄位" in concepts and "記錄" in concepts:
            return _curated_mcq_database(idx, rng, variant=variant)
        if "直接存取" in concepts or "檔案存取" in concepts:
            return _curated_mcq_file_access(idx, rng, variant=variant)
        for key, tpl in stems.items():
            if key in concepts:
                return _format_mcq(tpl[0], list(tpl[1]), tpl[2], rng)
        stem = f"下列哪一項關於{primary}的敘述是正確的？"
        opts = [
            f"{primary}是有效的資訊處理概念",
            f"{primary}只適用於硬件",
            f"{primary}與數據無關",
            f"{primary}不能應用於軟件",
        ]
        return _format_mcq(stem, opts, 0, rng)

    if core == "B":
        has_cache = any("快取" in c for c in concepts)
        if has_cache and "RAM" in concepts:
            return _format_mcq(
                "下列哪一項正確描述 RAM 與快取記憶體？",
                ["RAM 在斷電後資料會消失", "快取比硬碟慢", "RAM 容量通常小於快取", "快取不能加快 CPU 存取"],
                0,
                rng,
            )
        if "輸入裝置" in concepts:
            if len(concepts) <= 2 and "RAM" not in concepts:
                return _format_mcq(
                    "下列哪一組均屬於輸入裝置？",
                    ["鍵盤與滑鼠", "投影機與喇叭", "繪圖儀與顯示器", "硬碟與光碟機"],
                    0,
                    rng,
                )
            return _format_mcq(
                "下列哪一項屬於輸入裝置？",
                ["條碼掃描器", "投影機", "繪圖儀", "喇叭"],
                0,
                rng,
            )
        if "驅動程式" in concepts:
            return _format_mcq(
                "下列哪一項最能描述「驅動程式」的作用？",
                ["讓作業系統控制硬件", "編寫網頁", "壓縮檔案", "設計數據庫"],
                0,
                rng,
            )
        if "實用程式" in concepts:
            return _format_mcq(
                "下列哪一項屬於實用程式（utility）？",
                ["磁碟重組工具", "文書處理軟件", "試算表", "網頁瀏覽器"],
                0,
                rng,
            )
        if "專用軟件" in concepts:
            return _format_mcq(
                "下列哪一項屬於專用軟件（application software）？",
                ["文書處理軟件", "作業系統", "驅動程式", "編譯器"],
                0,
                rng,
            )
        if "輸出裝置" in concepts:
            return _format_mcq(
                "下列哪一項屬於輸出裝置？",
                ["投影機", "鍵盤", "滑鼠", "麥克風"],
                0,
                rng,
            )
        if "RAM" in concepts:
            ram_variants = (
                (
                    "下列哪一項正確描述 RAM？",
                    ["斷電後內容會消失", "用於長期備份", "比硬碟慢", "只能讀不能寫"],
                    0,
                ),
                (
                    "RAM 與硬碟比較，下列哪項正確？",
                    ["RAM 存取較快但斷電後資料消失", "RAM 用於長期備份", "硬碟較快", "兩者相同"],
                    0,
                ),
            )
            tpl = ram_variants[(idx + variant) % len(ram_variants)]
            return _format_mcq(tpl[0], list(tpl[1]), tpl[2], rng)
        if "軟件" in concepts or "作業系統" in concepts:
            return _format_mcq(
                "下列哪一項是作業系統的職責？",
                ["管理硬件資源", "設計網頁版面", "編寫 SQL 查詢", "繪製 ERD"],
                0,
                rng,
            )
        return _format_mcq(
            f"下列哪項關於{primary}的敘述是正確的？",
            [f"{primary}屬於電腦系統的一部分", f"{primary}只存在於網絡", f"{primary}不能升級", f"{primary}與輸入無關"],
            0,
            rng,
        )

    return _generate_core_d_mcq(idx, concepts, rng, variant=variant)


def _written_generators() -> dict[str, Any]:
    return {
        "b-01": _gen_b01,
        "b-02": _gen_b02,
        "b-03": _gen_b03,
        "b-04": _gen_b04,
        "b-05": _gen_b05,
        "b-06": _gen_b06,
        "c-01": _gen_c01,
        "c-02": _gen_c02,
        "c-03": _gen_c03,
        "c-05": _gen_c05,
        "c-06": _gen_c06,
        "c-07": _gen_c07,
        "c-08": _gen_c08,
    }


def _gen_b01(rng: random.Random) -> str:
    fn, tpl = rng.choice(
        [
            ("COUNTIF", "在 G2 使用 COUNTIF 統計 C 欄金額≥100 的個數，寫出公式。"),
            ("SUMIF", "在 G2 使用 SUMIF 加總班別為「5A」的 C 欄捐款，寫出公式。"),
            ("RANK", "在 G2 使用 RANK 為 C2 在 C$2:C$50 中排名（降序），寫出公式。"),
            ("XLOOKUP", "在 G2 使用 XLOOKUP 依 A2 班別從 $H$2:$I$10 查找目標金額，寫出公式。"),
        ]
    )
    return (
        "某校以試算表「Donation」記錄捐款：欄 A 班別、欄 B 學號、欄 C 金額（港元）、"
        "欄 D 達標與否；$H$2:$I$10 為班別目標對照表。\n"
        "在 D2 使用 IF：若 C2≥100 顯示「達標」，否則「未達標」，複製至 D3:D50。\n\n"
        f"(a) 寫出 D2 的 IF 公式。\t(2 分)\n\n"
        f"(b) {tpl}\t(2 分)"
    )


def _gen_b02(rng: random.Random) -> str:
    return (
        "某系統以 8 位元傳送數據，並在最高位加入奇偶檢驗位（偶校驗）。\n"
        "第一組：0101 0110\n第二組：1100 1011\n第三組：1110 0100\n\n"
        "(a) 指出哪兩組在傳送時可能已損壞，並說明理由。\t(3 分)\n\n"
        "(b) 描述一個適用於學號欄（文字，長度 8）的有效性檢驗。\t(2 分)"
    )


def _gen_b03(rng: random.Random) -> str:
    return (
        "學生以 1920×1080 像素、24 bit 真彩色拍攝 30 秒短片，每秒 24 幀，未壓縮。\n\n"
        "(a) 估算影片檔案大小（MB），列出計算步驟。\t(3 分)\n\n"
        "(b) 說明使用 H.264 壓縮可如何減少檔案大小。\t(1 分)"
    )


def _gen_b04(rng: random.Random) -> str:
    return (
        "考慮以下偽代碼，在陣列 A[1..n] 中尋找最大值並輸出其索引。\n"
        "max ← A[1]; pos ← 1\n"
        "FOR i ← 2 TO n\n"
        "  IF A[i] > max THEN max ← A[i]; pos ← i\n"
        "ENDFOR\n"
        "OUTPUT pos\n\n"
        "(a) 若 n=5 且 A=[3,9,2,9,1]，寫出輸出。\t(2 分)\n\n"
        "(b) 說明此算法屬於哪類搜尋。\t(2 分)"
    )


def _gen_b05(rng: random.Random) -> str:
    return (
        "圖書館以隨機存取檔案儲存書籍，主鍵為書號；另以順序存取檔案記錄每日借還記錄。\n\n"
        "(a) 比較兩種存取方式各適合上述哪項用途。\t(2 分)\n\n"
        "(b) 若要以書號快速找書，應使用哪種存取？說明理由。\t(2 分)"
    )


def _gen_b06(rng: random.Random) -> str:
    return (
        "網店「TechShop」使用關聯式數據庫，含 CUSTOMER(CID, CName) 及 ORDER(OID, CID, Amount, ODate)。\n\n"
        "(a) 寫出 CREATE TABLE ORDER 的 SQL（含主鍵及外鍵）。\t(4 分)\n\n"
        "(b) 寫出一條 INSERT，新增 CID='C01' 的訂單，金額 250，日期 '2026-03-01'。\t(3 分)\n\n"
        "(c) 為 Amount 欄建議一個合適的資料類型並說明。\t(2 分)"
    )


def _gen_c01(rng: random.Random) -> str:
    return (
        "戲院「StarCinema」預訂系統含實體：CINEMA、SCREEN、SHOWTIME、BOOKING。\n"
        "一場放映在一個影廳；一筆預訂對應一場放映及一位顧客。\n\n"
        "(a) 繪製 ERD（標示主鍵、外鍵及 cardinality）。\t(3 分)\n\n"
        "(b) 說明 BOOKING 與 SHOWTIME 之間的參照完整性。\t(1 分)"
    )


def _gen_c02(rng: random.Random) -> str:
    return (
        "表 FILM(FID, Title, Year) 及 RENTAL(RID, FID, MemberID, RentDate)。\n\n"
        "(a) 寫出建立 FILM 的 CREATE TABLE（FID 為主鍵）。\t(1 分)\n\n"
        "(b) 寫出 INSERT 一條 FILM 記錄的 SQL。\t(1 分)"
    )


def _gen_c03(rng: random.Random) -> str:
    return (
        "表 STAFF(SID, Name, Dept) 及 PROJECT(PID, PName, LeadSID)。\n\n"
        "(a) 寫出 UPDATE，把 LeadSID='S03' 的專案改為 'S05'。\t(1 分)\n\n"
        "(b) 使用 UNION 合併兩個 SELECT（SID, Name），分別來自 STAFF 與外聘顧問表 GUEST。\t(2 分)"
    )


def _gen_c05(rng: random.Random) -> str:
    return (
        "表 FACILITY(FID, FName, Capacity) 及 RESERVE(RID, FID, ClubID, RDate, Slot)。\n"
        "Club 表含 CID, CName。\n\n"
        "(a) 寫出查詢：列出 2026 年 4 月曾預訂的設施名稱（DISTINCT）。\t(3 分)\n\n"
        "(b) 寫出使用 MINUS：曾預訂 F01 但未預訂 F02 的 ClubID。\t(4 分)\n\n"
        "(c) 說明 MINUS 與 NOT IN 的差異（一句）。\t(1 分)\n\n"
        "(d) 寫出 GROUP BY 統計各設施預訂次數。\t(3 分)"
    )


def _gen_c06(rng: random.Random) -> str:
    return (
        "表 MEMBER(MID, MName) 及 LOAN(LID, MID, BID, LDate)。\n"
        "SQL：SELECT MName, COUNT(*) FROM MEMBER M JOIN LOAN L ON M.MID=L.MID GROUP BY MName;\n\n"
        "(a) 描述此查詢的輸出欄位。\t(2 分)\n\n"
        "(b) 若改為 LEFT JOIN，結果有何不同？\t(3 分)"
    )


def _gen_c07(rng: random.Random) -> str:
    return (
        "一卡通系統以 Transaction 處理扣款：BEGIN; UPDATE ACCOUNT SET Balance=Balance-50 WHERE AID='A1'; "
        "INSERT INTO LOG VALUES(...); COMMIT;\n\n"
        "(a) 說明 COMMIT 的作用。\t(2 分)\n\n"
        "(b) 若在 UPDATE 後發生錯誤而執行 ROLLBACK，Balance 會如何？\t(3 分)\n\n"
        "(c) 舉出一個應使用 Transaction 的學校場景。\t(4 分)"
    )


def _gen_c08(rng: random.Random) -> str:
    return (
        "堆疊 S 初為空。依次執行：PUSH 3; PUSH 7; POP; PUSH 2; POP; PUSH 9。\n\n"
        "(a) 列出每次 POP 的輸出值。\t(3 分)\n\n"
        "(b) 完成後堆疊頂端元素是什麼？\t(1 分)\n\n"
        "(c) 說明堆疊適合處理「復原上次操作」的原因。\t(2 分)"
    )


def _generate_written(slot: dict[str, Any], style: dict[str, Any], rng: random.Random) -> str:
    from written_generate_from_patterns import generate_written_text

    text, _ = generate_written_text(slot, style, rng)
    return text


def _find_slot(blueprint: dict[str, Any], slot_id: str) -> dict[str, Any] | None:
    for slot in blueprint.get("slots") or []:
        if str(slot.get("id")) == slot_id:
            return slot
    return None


def generate_item_for_slot(
    slot: dict[str, Any],
    style: dict[str, Any],
    *,
    seed: int,
    variant: int = 0,
) -> dict[str, Any]:
    """Generate one spec item for a blueprint slot (for partial regen)."""
    sid = str(slot["id"])
    section = slot["section"]
    rng = _slot_rng(sid, seed + variant * 1009)
    concepts = list(slot.get("concepts") or [])
    marks = slot.get("marks", 1)
    title = slot.get("title")

    if section == "mcq":
        text, letter = _generate_mcq(slot, style, rng, variant=variant)
        item = make_item(
            sid,
            "mcq",
            text,
            marks=marks,
            concepts=concepts,
            core=slot.get("core"),
            answer=letter,
            dse_source=f"generated://mcq/{sid}",
        )
    else:
        text = _generate_written(slot, style, rng)
        item = make_item(
            sid,
            section,
            text,
            marks=marks,
            title=title,
            concepts=concepts,
            dse_source=f"generated://pattern/{sid}",
            composition="pattern_generate",
        )
    try:
        from iclass_hk_depth import attach_depth_references

        attach_depth_references(item, slot)
    except ImportError:
        pass
    return item


def sync_mcq_meta(spec: dict[str, Any], *, seed: int) -> None:
    """Rebalance MCQ keys and update meta after item edits."""
    items = list(spec.get("items") or [])
    _rebalance_mcq_answers(items, seed=seed)
    letters = [str(it.get("answer") or "A")[:1].upper() for it in items if it.get("section") == "mcq"]
    meta = spec.setdefault("meta", {})
    meta["mcq_answers"] = "".join(letters)
    prov = meta.get("mcq_provenance") or []
    if len(prov) < len(letters):
        prov = list(prov) + [f"generated://mcq/mcq-{i:02d}" for i in range(len(prov) + 1, len(letters) + 1)]
    meta["mcq_provenance"] = prov[: len(letters)]


def replace_spec_item(spec: dict[str, Any], new_item: dict[str, Any], *, seed: int) -> None:
    items = spec.setdefault("items", [])
    for i, it in enumerate(items):
        if it.get("id") == new_item.get("id"):
            items[i] = new_item
            break
    else:
        raise KeyError(f"slot not in spec: {new_item.get('id')}")
    if new_item.get("section") == "mcq":
        sync_mcq_meta(spec, seed=seed)


def template_written_items() -> list[dict]:
    """Legacy curated 乙／丙 from f5_ict_written_content (tables, blanks, SQL traces)."""
    if str(_FMT) not in sys.path:
        sys.path.insert(0, str(_FMT))
    from f5_ict_spec import _part_b_items, _part_c_items
    from f5_ict_written_content import build_part_b, build_part_c

    items = _part_b_items(build_part_b) + _part_c_items(build_part_c)
    for it in items:
        it["dse_source"] = f"template://written/{it['id']}"
        it["composition"] = "template"
    return items


def pattern_written_items(
    blueprint: dict[str, Any],
    style: dict[str, Any],
    *,
    seed: int,
) -> list[dict]:
    """乙／丙 from bank ask patterns + blueprint (not verbatim bank copy)."""
    from written_generate_from_patterns import generate_written_items_from_blueprint

    return generate_written_items_from_blueprint(blueprint, style, seed=seed)


def written_picks_from_items(items: list[dict]) -> dict[str, dict]:
    """Build written_picks dict for DOCX render from spec written items."""
    picks: dict[str, dict] = {}
    for it in items:
        if not str(it.get("id", "")).startswith(("b-", "c-")):
            continue
        picks[it["id"]] = {
            "id": it["id"],
            "section": it["section"],
            "text": it["text"],
            "marks": it.get("marks"),
            "title": it.get("title", ""),
            "concepts": list(it.get("concepts") or []),
            "dse_source": it.get("dse_source", "generated"),
            "dse_sources": it.get("dse_sources") or ["generated"],
            "composition": "generated",
        }
    return picks


def build_spec_from_blueprint(
    blueprint: dict[str, Any],
    *,
    seed: int = 20252026,
    style_patterns: dict[str, Any] | None = None,
) -> dict[str, Any]:
    style = style_patterns or {}
    items: list[dict] = []
    provenance: list[str] = []

    for slot in blueprint.get("slots") or []:
        sid = str(slot["id"])
        section = slot["section"]
        if section != "mcq":
            continue
        rng = _slot_rng(sid, seed)
        concepts = list(slot.get("concepts") or [])
        marks = slot.get("marks", 1)
        text, letter = _generate_mcq(slot, style, rng, variant=0)
        prov = f"generated://mcq/{sid}"
        item = make_item(
            sid,
            "mcq",
            text,
            marks=marks,
            concepts=concepts,
            core=slot.get("core"),
            answer=letter,
            dse_source=prov,
        )
        try:
            from iclass_hk_depth import attach_depth_references

            attach_depth_references(item, slot)
        except ImportError:
            pass
        provenance.append(prov)
        items.append(item)

    written_items = pattern_written_items(blueprint, style, seed=seed)
    try:
        from iclass_hk_depth import attach_depth_references

        for it in written_items:
            wslot = next(
                (s for s in blueprint.get("slots") or [] if str(s.get("id")) == str(it.get("id"))),
                None,
            )
            if wslot:
                attach_depth_references(it, wslot)
    except ImportError:
        pass
    items.extend(written_items)

    bmeta = blueprint.get("meta") or {}
    meta: dict[str, Any] = {
        "title": "25-26 S5 ICT Exam02",
        "subject": bmeta.get("subject", "F5 ICT"),
        "level": bmeta.get("level", "S5"),
        "total_marks": bmeta.get("total_marks", 100),
        "academic_year": bmeta.get("academic_year", "2025-2026"),
        "footer": {
            "academic_year": bmeta.get("academic_year", "2025-2026"),
            "level": "中五級",
            "term_exam": "下學期考試",
            "subject": "資訊及通訊科技",
        },
        "curriculum_units": ["Core-A", "Core-B", "Core-D", "Module-A", "Module-C"],
        "mcq_core_sequence": list(bmeta.get("mcq_core_sequence") or []),
        "mcq_combo_slots": list(_COMBO_SLOT_IDS),
        "mcq_table_slots": [6, 13, 15],
        "exam_structure": {
            "section_a": "MCQ — compulsory Core A/B/D only (DSE Paper 1A style)",
            "section_b": "Structured — compulsory (DSE Paper 1B style)",
            "section_c": "Structured — elective Module A + C (DSE Paper 2); no MCQ",
        },
        "concept_targets": dict(bmeta.get("concept_targets") or {}),
        "generation": {
            "method": "blueprint_generate",
            "seed": seed,
            "style_patterns": bmeta.get("style_patterns"),
            "blueprint": "exam_blueprint.json",
        },
        **style_meta(),
    }
    try:
        from iclass_hk_depth import depth_calibration_meta

        meta["depth_calibration"] = depth_calibration_meta()
    except ImportError:
        pass
    meta["phrasing"] = "HKDSE ICT style — generated from blueprint (not bank copy)"
    meta["mcq_provenance"] = provenance[:30]
    meta["written_render"] = "patterns"
    meta["written_picks_source"] = "style_patterns.written + blueprint"

    spec = build_spec(meta, items)
    sync_mcq_meta(spec, seed=seed)
    return spec
