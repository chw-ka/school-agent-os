#!/usr/bin/env python3
"""
Generate F5 ICT exam (Database elective; no networking / HTML / web dev) from template layout.
Always runs post-generation similarity check vs template + past 3 years.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from docx import Document

from f5_ict_spec import F5_MCQ_CORRECT_INDEX, build_f5_ict_exam_spec
from post_check import repo_root, run_spec_check

_FMT = Path(__file__).resolve().parents[1] / "paper-formatter"
if str(_FMT) not in sys.path:
    sys.path.insert(0, str(_FMT))
from docx_inplace import ZhCoverPatch, apply_cmp_cover_zh_on_en_layout
from mcq_answer_keys import build_random_mcq_key

_QCHECK = Path(__file__).resolve().parents[1] / "question-quality-check"
_PCHECK = Path(__file__).resolve().parents[1] / "paper-quality-check"
for _d in (_QCHECK, _PCHECK):
    if str(_d) not in sys.path:
        sys.path.insert(0, str(_d))
from exam_spec import save_spec
from footer import apply_footer_meta

# --- generation logic (template-span preserving) ---


def is_option_line(t: str) -> bool:
    s = t.lstrip()
    return len(s) >= 2 and s[0] in "ABCD" and s[1] == "."


def mcq_blocks(doc: Document) -> list[tuple[int, int]]:
    blocks: list[tuple[int, int]] = []
    i = 1
    while i < 311:
        while i < 311 and not doc.paragraphs[i].text.strip():
            i += 1
        if i >= 311:
            break
        if "甲部" in doc.paragraphs[i].text:
            i += 1
            continue
        start = i
        while i < 311:
            t = doc.paragraphs[i].text
            if is_option_line(t):
                break
            i += 1
        while i < 311 and is_option_line(doc.paragraphs[i].text):
            i += 1
        end = i
        blocks.append((start, end))
        while i < 311 and not doc.paragraphs[i].text.strip():
            i += 1
    return blocks


def opt(a: str, b: str, c: str, d: str) -> list[str]:
    return [f"\tA.\t{a}", f"\tB.\t{b}", f"\tC.\t{c}", f"\tD.\t{d}"]


def build_mcq_payload() -> list[list[str]]:
    o = opt
    rows: list[list[str]] = [
        ["下列哪一項是二進制 1100 0101 的十六進制表示？", ""] + o("0xC5", "0xCA", "0xA5", "0x5C"),
        ["以 8 位元二進制補碼表示十進位 -3，下列哪一項正確？", ""] + o("1111 1101", "1111 1111", "1000 0011", "0000 0011"),
        ["關於 ASCII 與 Unicode（UTF-8）儲存中文，下列敘述何者最恰當？", ""]
        + o("兩者均以 1 字節儲存每個中文字", "UTF-8 的中文字通常比 ASCII 編碼佔更多字節", "ASCII 可完整表示所有繁體中文字", "UTF-8 只能儲存英文字母"),
        ["一段未壓縮音訊：取樣頻率 44.1 kHz、取樣精度 16 bit、立體聲（2 聲道），長度 1 秒。下列何者最接近其檔案大小？", ""]
        + o("約 88 KB", "約 176 KB", "約 352 KB", "約 705 KB"),
        ["在試算表中，VLOOKUP／XLOOKUP 的主要用途是？", ""] + o("合併儲存格", "依關鍵值查找並傳回對應欄位", "計算滿足多條件的個數", "將文字轉為日期格式"),
        [
            "老師要統計「同時滿足：班別為甲班、分數>=60」的學生人數。下列哪個函數最適合？",
            "",
            "\t\t(1)\tCOUNT",
            "\t\t(2)\tCOUNTIF",
            "\t\t(3)\tCOUNTIFS",
            "",
        ]
        + o("只有 (1)", "只有 (2)", "只有 (3)", "(3)（COUNTIFS）最貼切"),
        [
            "在馮·諾伊曼架構中，快取記憶體（Cache）的主要角色是？下列敘述何者正確？",
            "",
            "（提示：快取位於 CPU 與主記憶體之間，用較小但較快的記憶體暫存常用資料以提升效能。）",
            "",
        ]
        + o(
            "在 CPU 與主記憶體之間提供較小但較快的暫存層以提升效能",
            "用作永久儲存作業系統與使用者文件",
            "負責把類比訊號轉為數位訊號",
            "只用作顯示輸出裝置",
        ),
    ]
    rows.extend(
        [
            [
                "比較 SSD 與傳統 HDD，下列敘述何者正確？",
                "",
                "\t\t(1)\tSSD 通常較抗震",
                "\t\t(2)\tHDD 通常讀寫較快",
                "\t\t(3)\t相同容量下 SSD 通常較貴",
                "",
            ]
            + o("只有 (1)", "只有 (1) 和 (3)", "只有 (2) 和 (3)", "(1)、(2) 和 (3)"),
            ["下列哪一項最屬於實用程式（Utility）的典型用途？", ""]
            + o("試算表繪製圖表", "磁碟重組或檔案壓縮等系統維護工作", "編寫 SQL 查詢", "管理使用者帳戶與檔案權限"),
            [
                "一幅 800×600 像素的點陣圖，每像素以 24 bit 真彩色儲存（未壓縮）。下列何者最接近檔案大小？",
                "",
            ]
            + o("約 1.4 MB", "約 14 MB", "約 140 KB", "約 4.8 MB"),
            [
                "關於有損與無損壓縮，下列敘述何者最恰當？",
                "",
            ]
            + o(
                "有損壓縮可還原成與原檔完全相同",
                "無損壓縮常用於 JPEG 相片以縮小檔案",
                "有損壓縮可能犧牲部分畫質／音質以換取較小檔案",
                "兩者均不能減少檔案大小",
            ),
            [
                "資料表 Order(OrderID, CustomerName, ProductName, UnitPrice, Qty) 中，同一 CustomerName 對應多個 ProductName。"
                "下列哪一項最可能違反第一正規化（1NF）？",
                "",
            ]
            + o(
                "OrderID 為主鍵",
                "同一列同時儲存多個產品名稱於一個儲存格（以逗號分隔）",
                "UnitPrice 為數值型別",
                "Qty 必須大於 0",
            ),
            [
                "輸入學號時，系統只接受「一個英文字母 + 五個數字」的格式。這主要屬於哪類數據控制？",
                "",
                "\t\t(1)\t有效性檢驗",
                "\t\t(2)\t奇偶檢測",
                "\t\t(3)\t順序存取檔案",
                "",
            ]
            + o("只有 (1)", "只有 (2)", "只有 (3)", "(1) 正確"),
            [
                "下列哪一項最能說明「資訊」相對於「數據」？",
                "",
            ]
            + o(
                "未經處理的原始符號或數值",
                "經整理後對決策有幫助的內容",
                "硬碟上的二進制位元",
                "壓縮演算法中的位元組",
            ),
            [
                "考慮下列片段（變數 count 初值為 0）：",
                "",
                "\t\tFOR k ← 1 TO 3",
                "\t\t\tFOR m ← 1 TO 2",
                "\t\t\t\tcount ← count + 1",
                "",
            ]
            + o("迴圈結束後 count 為 3", "迴圈結束後 count 為 5", "迴圈結束後 count 為 6", "迴圈結束後 count 為 9"),
            [
                "要找出一組數字中的第三大值，下列哪一種做法較符合「最直接」的解難方向？",
                "",
                "\t\t(1)\t先排序再取適當位置的值",
                "\t\t(2)\t把所有數字相加",
                "\t\t(3)\t只比較前兩個數字",
                "",
            ]
            + o("只有 (1)", "只有 (2)", "只有 (3)", "(1) 較合理（視演算法而定）"),
            [
                "在數據組織層次中，「一筆記錄」是指？",
                "",
            ]
            + o("一個欄位內的單一數值", "由多個欄位值組成的一組相關資料", "整個資料庫的備份檔", "CPU 暫存器內容"),
            [
                "對 n 個未排序整數排序，下列配對何者最恰當？",
                "",
            ]
            + o(
                "冒泡排序：相鄰元素比較並交換",
                "二分搜尋：把陣列由小至大排列",
                "堆疊：先進先出（FIFO）",
                "隊列：後進先出（LIFO）",
            ),
            [
                "超級市場收銀處排隊，先來先服務。下列哪種資料結構最接近此操作？",
                "",
            ]
            + o("堆疊（LIFO）", "隊列（FIFO）", "線性鏈表", "二分搜尋樹"),
            [
                "比較直接存取與順序存取檔案，下列敘述何者最恰當？",
                "",
            ]
            + o(
                "順序存取必須從頭開始逐一讀取直至目標記錄",
                "直接存取可在已知索引下較快定位特定記錄",
                "兩者均不能讀取文字檔",
                "直接存取只能用於堆疊結構",
            ),
            [
                "在關聯式資料庫中，主鍵（Primary Key）的主要作用是？",
                "",
                "\t\t(1)\t唯一識別每一筆記錄",
                "\t\t(2)\t自動把兩個資料表合併",
                "\t\t(3)\t保證所有欄位均為文字型別",
                "",
            ]
            + o("只有 (1)", "只有 (2)", "只有 (3)", "(1) 正確"),
            [
                "外鍵（Foreign Key）的主要用途是？",
                "",
                "\t\t(1)\t建立資料表之間的參照完整性",
                "\t\t(2)\t把資料表所有欄位加密",
                "\t\t(3)\t取代主鍵成為唯一識別碼",
                "",
            ]
            + o("只有 (1)", "只有 (1) 和 (3)", "只有 (2)", "(1) 正確"),
            [
                "下列偽代碼用於找出陣列 L 的次大值（假設長度≥2 且存在次大值）：",
                "\t",
                "",
                "\t若 L = [10, 5, 20, 8, 20, 15]，迴圈結束後 second 的值是？",
                "",
            ]
            + o("10", "15", "20", "8"),
            [
                "下列演算法的輸出是？",
                "",
                "\tN ← 1  ",
                "\tS ← 0  ",
                "\tFOR i ← 1 TO 4  ",
                "\t\tS ← S + N  ",
                "\t\tN ← N + 2  ",
                "\tOUTPUT S  ",
                "",
            ]
            + o("9", "16", "20", "25"),
            [
                "下列關於資料庫正規化的敘述，何者較正確？",
                "",
                "\t\t(1)\t1NF 要求屬性值為不可再分的原子值",
                "\t\t(2)\t2NF 消除非鍵屬性對候選鍵的部分函數相依",
                "\t\t(3)\t3NF 消除遞移函數相依",
                "\t\t（以上為一般課程描述，可能因教材用語略有差異）",
                "\t\t（請以「最合理」為準選擇答案）",
                "",
            ]
            + o("只有 (1)", "只有 (1) 和 (2)", "只有 (3)", "(1)、(2) 和 (3)"),
            [
                "在 n 個已排序元素中尋找特定值，下列哪種方法通常較有效率？",
                "",
                "",
            ]
            + o("線性搜尋", "二分搜尋", "冒泡排序", "逐一列印所有元素"),
            ["在程式設計中，把重複使用的邏輯封裝成可獨立測試的小單元，最能體現哪項原則？", ""]
            + o("循序結構", "模組化（Modularisation）", "無限迴圈", "單一巨型程式檔"),
            [
                "下列關於堆疊（Stack）資料結構，何者較正確？",
                "",
                "\t\t(1)\t後進先出（LIFO）",
                "\t\t(2)\tpush 把元素放到堆疊頂端",
                "\t\t(3)\tpop 從堆疊頂端移除元素",
                "",
                "\t\t（請以「最合理」為準選擇答案）",
                "",
                "",
                "",
            ]
            + o("只有 (1)", "只有 (1) 和 (2)", "只有 (3)", "(1)、(2) 和 (3)"),
            ["下列哪一項最能說明程序設計中「函數（Function）」的用途？", ""]
            + o("把程式拆成可重複呼叫的模組以提升可讀性與重用", "把所有變數改為全域變數", "刪除所有迴圈", "只能處理單一數值"),
            [
                "資料表 Book(ISBN, Title) 與 BookCopy(CopyID, ISBN, Shelf, Status)。",
                "",
                "\t\t要列出 Status =「在架」的書名 Title，",
                "",
                "\t\t下列 SQL 概念組合何者最適合？",
                "",
                "\t\t(1)\tINNER JOIN Book 與 BookCopy",
                "\t\t(2)\tWHERE Status = '在架'",
                "\t\t(3)\tSELECT Title",
                "",
            ]
            + o("只有 (1)", "只有 (1) 和 (2)", "只有 (3)", "(1)、(2) 和 (3)"),
        ]
    )
    expected = [6, 6, 6, 6, 6, 10, 8, 10, 6, 6, 6, 6, 10, 6, 10, 10, 6, 6, 6, 6, 6, 10, 10, 9, 13, 12, 7, 6, 14, 6, 14]
    if len(rows) != len(expected):
        raise RuntimeError(f"MCQ count mismatch {len(rows)} vs {len(expected)}")
    for i, (row, exp) in enumerate(zip(rows, expected, strict=True), start=1):
        if len(row) != exp:
            raise RuntimeError(f"MCQ#{i} len {len(row)} expected {exp}")
    return rows


def apply_mcq(doc: Document, blocks: list[tuple[int, int]], payload: list[list[str]]) -> None:
    if len(blocks) != len(payload):
        raise RuntimeError("blocks/payload mismatch")
    for (start, end), lines in zip(blocks, payload):
        span = end - start
        if span != len(lines):
            raise RuntimeError(f"span {span} != payload {len(lines)} at {start}")
        for j, text in enumerate(lines):
            doc.paragraphs[start + j].text = text


def replace_span(doc: Document, start: int, end_inclusive: int, lines: list[str]) -> None:
    span = end_inclusive - start + 1
    if len(lines) != span:
        raise RuntimeError(f"replace_span {start}-{end_inclusive} need {span} lines got {len(lines)}")
    for k, text in enumerate(lines):
        doc.paragraphs[start + k].text = text


def build_part_b() -> list[str]:
    lines: list[str] = [""] * 110
    base = 313

    def put(offset: int, s: str) -> None:
        lines[offset - base] = s

    put(
        313,
        "「星晴網店」以試算表記錄訂單，欄位包括：A=訂單日期、B=產品類別、C=單價、D=數量、E=會員等級（VIP／一般）。"
        "F 欄為總價。請回答下列問題。",
    )
    put(
        316,
        "(a)\t在 F2 寫出一條公式（可用 IF 與 AND），然後複製到 F3:F200。"
        "規則：若 E2 為「VIP」且 D2>10，則總價為 C2*D2 的 8 折；否則為原價 C2*D2。\t(5 分)",
    )
    put(319, "(b)\t描述如何建立樞紐分析表：以「列」顯示產品類別；以「值」顯示總銷售額（對 F 欄總價求和）。\t(5 分)")
    put(323, "2.\t數據控制與私隱\t(10 分)")
    put(326, "(a)\t說明「有效性檢驗」與「奇偶檢測」的分別，並各舉一個輸入數據的例子。\t(3 分)")
    put(328, "(b)\t比較「直接存取」與「順序存取」讀取檔案記錄的優缺點。\t(4 分)")
    put(331, "(c)\t學校收集學生健康申報資料時，提出兩項保障數據私隱的做法。\t(3 分)")
    put(336, "3.\t算法追蹤\t(10 分)")
    put(
        338,
        "考慮以下偽代碼（陣列 A 索引由 1 開始，長度 n≥2）：\n"
        "largest ← A[1]\n"
        "second_largest ← A[1]\n"
        "FOR i ← 2 TO n\n"
        "    IF A[i] > largest THEN\n"
        "        second_largest ← largest\n"
        "        largest ← A[i]\n"
        "    ELSE IF A[i] > second_largest AND A[i] < largest THEN\n"
        "        second_largest ← A[i]\n"
        "    ENDIF\n"
        "ENDFOR",
    )
    put(343, "(a)\t設 A = [10, 5, 20, 8, 20, 15]（n=6）。完成追蹤表，展示迴圈每次迭代後 largest 與 second_largest 的值。\t(5 分)")
    put(345, "(b)\t若陣列中最大值出現多次（如上例的 20），此算法是否仍能正確找出「次大值」？解釋原因。\t(5 分)")
    return lines


def build_part_c() -> list[str]:
    lines = [""] * 202
    b = 423

    def put(i: int, s: str) -> None:
        lines[i - b] = s

    put(423, "丙部 (40 分)：選修單元問答題（數據庫）")
    put(425, "選修 A：數據庫（Database）")
    put(
        427,
        "某「社區中心活動報名系統」描述如下：一位會員可報名多個工作坊；一個工作坊亦可被多位會員報名。"
        "每次報名產生一筆報名記錄，包含報名日期與付款狀態。",
    )
    put(
        440,
        "(a)\t繪製實體關係圖（ERD）：須包含「會員 Member」「工作坊 Workshop」「報名 Registration」三個實體，標示多對多並以關聯實體拆解；"
        "並在圖中寫出主鍵（PK）與外鍵（FK）欄位名稱。\t(8 分)",
    )
    put(442, "(b)\t設資料表如下：")
    put(444, "Member(MemberID, MemberName, JoinDate)")
    put(445, "Workshop(WorkshopID, Title, Instructor, Fee)")
    put(446, "Registration(RegID, MemberID, WorkshopID, RegDate, PayStatus)")
    put(450, "(i)\t寫出一條 SQL，列出所有報名了 Instructor = 'Peter' 的工作坊之會員姓名（MemberName）。\t(4 分)")
    put(453, "(ii)\t寫出一條 SQL，找出報名人數 **超過 30** 的工作坊名稱（Title）及其報名人數。（需使用 COUNT、GROUP BY、HAVING）\t(6 分)")
    put(455, "(iii)\t寫出一條 SQL，找出 **從未報名任何工作坊** 的會員姓名。（可用 NOT IN 或 NOT EXISTS）\t(6 分)")
    put(457, "2.\t正規化與資料完整性\t(10 分)")
    put(459, "某社團登記表把「學號、姓名、社團名稱、社團會址、會費」全部放在同一工作表的一列中，且同一社團會址重複出現於多行。")
    put(461, "(a)\t指出此設計違反哪一條正規化規則，並說明會造成什麼更新異常（update anomaly）。\t(5 分)")
    put(463, "(b)\t建議如何拆分為至少兩個實體／資料表，並寫出各表的主要屬性。\t(5 分)")
    put(470, "")
    put(482, "3.\t進階 SQL 與資料操作\t(10 分)")
    put(485, "沿用丙部選修 A 的 Member、Workshop、Registration 資料表。")
    put(487, "(a)\t寫出一條 SQL，列出曾報名兩個或以上不同工作坊的會員姓名（需 DISTINCT／COUNT／GROUP BY／HAVING）。\t(5 分)")
    put(489, "(b)\t寫出一條 SQL，把 WorkshopID = 'WS101' 且 PayStatus = '已付款' 的報名記錄 PayStatus 更新為「已確認」。（UPDATE … WHERE）\t(5 分)")
    put(492, "")
    return lines


def _apply_cover(doc: Document) -> None:
    """Patch 24_25 EN-layout cover for 2025-2026 S5 ICT."""
    cell = doc.tables[0].cell(0, 0)
    instr = [cell.paragraphs[i].text for i in range(17, min(22, len(cell.paragraphs)))]
    apply_cmp_cover_zh_on_en_layout(
        cell,
        ZhCoverPatch(
            year_term="2025 – 2026 下學期考試",
            level="中五級 資訊及通訊科技",
            paper="試題簿",
            total_line="總分：100",
        ),
        instructions=instr,
    )


def clear_answer_pages(doc: Document) -> None:
    note = "（本擬題稿不附標準答案；教師可自行增刪。）"
    for i in range(635, len(doc.paragraphs)):
        doc.paragraphs[i].text = ""
    if len(doc.paragraphs) > 635:
        doc.paragraphs[635].text = note


def generate(
    template: Path,
    output: Path,
    *,
    footer_meta: dict | None = None,
    rng: object | None = None,
) -> tuple[list[list[str]], str]:
    """Render DOCX; return (final MCQ rows, mcq answer key)."""
    shutil.copy(template, output)
    doc = Document(str(output))
    _apply_cover(doc)
    blocks = mcq_blocks(doc)
    payload = build_mcq_payload()
    block_map = {i + 1: row for i, row in enumerate(payload)}
    shuffled, mcq_key = build_random_mcq_key(
        block_map,
        correct_indices=F5_MCQ_CORRECT_INDEX,
        rng=rng,
    )
    apply_mcq(doc, blocks, [shuffled[i] for i in range(1, len(shuffled) + 1)])
    replace_span(doc, 313, 422, build_part_b())
    replace_span(doc, 423, 624, build_part_c())
    clear_answer_pages(doc)
    doc.save(str(output))
    if footer_meta:
        apply_footer_meta(output, footer_meta)
    final_rows = [shuffled[i] for i in range(1, len(shuffled) + 1)]
    return final_rows, mcq_key


def main(argv: list[str] | None = None) -> int:
    root = repo_root()
    default_out = root / "Subjects/PastPaper/CMP+ICT/2025-2026"
    template_dir = root / "Subjects/PastPaper/CMP+ICT/2024-2025/2nd Term/F5 ICT"
    ap = argparse.ArgumentParser(
        description="F5 ICT blueprint: build exam spec → compare → optional DOCX render.",
    )
    ap.add_argument(
        "--template",
        type=Path,
        default=template_dir / "24_25_S5_ICT_Exam02.docx",
    )
    ap.add_argument(
        "--output",
        type=Path,
        default=default_out / "25_26_S5_ICT_Exam02.docx",
    )
    ap.add_argument(
        "--spec",
        type=Path,
        default=default_out / "25_26_S5_ICT_Exam02.spec.json",
        help="Exam spec JSON (primary artifact for compare)",
    )
    ap.add_argument("--subject", default="F5 ICT", help="Subject folder for past-paper scan")
    ap.add_argument("--years", type=int, default=3, help="Past academic years to compare")
    ap.add_argument(
        "--duplicate-report",
        type=Path,
        help="Write duplicate report JSON (regenerate_ids for batch fix)",
    )
    ap.add_argument("--skip-check", action="store_true", help="Skip spec similarity check")
    ap.add_argument(
        "--render",
        action="store_true",
        help="Render DOCX after check (default: only render when check passes)",
    )
    ap.add_argument(
        "--render-anyway",
        action="store_true",
        help="Render DOCX even if duplicates found",
    )
    ap.add_argument("--strict", action="store_true", help="Exit 2 on duplicates (legacy hard fail)")
    args = ap.parse_args(argv)

    template = args.template.expanduser().resolve()
    output = args.output.expanduser().resolve()
    spec_path = args.spec.expanduser().resolve()
    dup_report = args.duplicate_report or spec_path.with_suffix(".duplicates.json")

    output.parent.mkdir(parents=True, exist_ok=True)
    footer = {
        "academic_year": "2025-2026",
        "level": "中五級",
        "term_exam": "下學期考試",
        "subject": "資訊及通訊科技",
    }
    if args.skip_check:
        mcq_rows, mcq_key = generate(template, output, footer_meta=footer)
        spec = build_f5_ict_exam_spec(mcq_rows=mcq_rows, mcq_answers=mcq_key)
        save_spec(spec_path, spec)
        print(f"Wrote spec: {spec_path}")
        print(f"Wrote DOCX: {output}")
        return 0

    import random

    check_code = 1
    for attempt in range(1, 41):
        mcq_rows, mcq_key = generate(
            template, output, footer_meta=footer, rng=random.Random(2025_2026 + attempt)
        )
        spec = build_f5_ict_exam_spec(mcq_rows=mcq_rows, mcq_answers=mcq_key)
        save_spec(spec_path, spec)
        check_code = run_spec_check(
            candidate_spec=spec_path,
            template=template,
            candidate_docx=output,
            years=args.years,
            subject_subpath=args.subject,
            json_report=dup_report,
            strict=args.strict,
        )
        if check_code == 0:
            print(f"Wrote spec: {spec_path}")
            print(f"Wrote DOCX: {output}")
            print(f"MCQ key: {mcq_key} (attempt {attempt})")
            break
    else:
        print("Could not pass spec duplicate check after 40 attempts.")
        return check_code

    import importlib.util

    _qdir = Path(__file__).resolve().parents[1] / "question-quality-check"
    _pdir = Path(__file__).resolve().parents[1] / "paper-quality-check"
    if str(_qdir) not in sys.path:
        sys.path.insert(0, str(_qdir))
    if str(_pdir) not in sys.path:
        sys.path.append(str(_pdir))
    _qdocx = importlib.util.spec_from_file_location(
        "qqc_check_docx", _qdir / "check_docx.py"
    )
    assert _qdocx and _qdocx.loader
    _qmod = importlib.util.module_from_spec(_qdocx)
    _qdocx.loader.exec_module(_qmod)
    question_docx_main = _qmod.main
    from check_paper import format_paper_report_text, report_exit_code, run_paper_check

    docx_argv = [
        "--candidate",
        str(output),
        "--candidate-spec",
        str(spec_path),
        "--template",
        str(template),
        "--subject",
        args.subject,
        "--years",
        str(args.years),
    ]
    docx_code = int(question_docx_main(docx_argv))
    p_report = run_paper_check(
        output,
        candidate_spec_path=spec_path,
        template_docx_path=template,
    )
    print("\n--- Paper quality check (DOCX) ---")
    print(format_paper_report_text(p_report))
    final_code = max(check_code, docx_code, report_exit_code(p_report))
    if final_code == 0:
        print("All checks passed.")
    return final_code


if __name__ == "__main__":
    raise SystemExit(main())
