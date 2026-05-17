#!/usr/bin/env python3
"""
Generate F5 ICT exam (Database + Web electives blueprint) from 24_25 template layout.
Always runs post-generation similarity check vs template + past 3 years.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from docx import Document

from f5_ict_spec import build_f5_ict_exam_spec
from post_check import repo_root, run_spec_check

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
        ["下列哪一項是十六進制 0x2A 的二進制表示？", ""] + o("0010 1010", "0011 1010", "0101 0101", "1010 0010"),
        ["以 8 位元二進制補碼表示十進位 -1，下列哪一項正確？", ""] + o("0000 0001", "1000 0001", "1111 1111", "1111 1110"),
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
            "取代路由器進行封包轉送",
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
            ["下列哪一項最屬於實用程式（Utility）的典型用途？", ""] + o("編寫網頁", "磁碟重組或檔案壓縮等系統維護工作", "試算表繪圖", "資料庫正規化分析"),
            ["在 TCP/IP 概念中，HTTP 主要工作層級最接近下列何者？", ""] + o("應用層協定", "網路層路由", "實體層訊號", "資料鏈結層訊框"),
            ["下列哪一項最能描述 TCP 相對於 IP 的分工？", ""]
            + o("TCP 負責可靠傳輸；IP 負責位址與路由", "TCP 負責硬體驅動；IP 負責顯示", "兩者完全相同", "IP 負責加密；TCP 負責壓縮"),
            ["下列何者是合法 IPv6 位址的寫法？", ""] + o("192.168.0.1", "2001:0db8:0000:0000:0000:ff00:0042:8329", "GG::1", "256.1.1.1"),
            [
                "電郵內容：「你的帳戶異常，請立即點擊連結重設密碼」，寄件者顯示為銀行但網址為短網址且與官方網域不符。下列何者最像網絡釣魚（Phishing）跡象？",
                "",
                "\t\t(1)\t要求緊急行動並提供可疑外部連結",
                "\t\t(2)\t使用官方網域且提供可查證聯絡方式",
                "\t\t(3)\t主旨清楚列出學校活動日程",
                "",
            ]
            + o("只有 (1)", "只有 (2)", "只有 (3)", "(1) 和 (2)"),
            ["關於惡意軟件，下列配對何者最適當？", ""]
            + o(
                "蠕蟲：必須依附於試算表巨集且不能自我複製",
                "病毒：常需依附宿主檔案；蠕蟲：常可自我複製並擴散",
                "勒索軟件：只會加快 CPU 風扇",
                "病毒：只感染路由器韌體且不影響檔案",
            ),
            [
                "考慮下列片段：",
                "",
                "\t\tFOR i ← 1 TO 3",
                "\t\t\tFOR j ← 1 TO 2",
                "\t\t\t\tOUTPUT i, j",
                "",
            ]
            + o("內層 OUTPUT 執行 3 次", "內層 OUTPUT 執行 5 次", "內層 OUTPUT 執行 6 次", "內層 OUTPUT 執行 9 次"),
            [
                "要找出一組數字中的第三大值，下列哪一種做法較符合「最直接」的解難方向？",
                "",
                "\t\t(1)\t先排序再取適當位置的值",
                "\t\t(2)\t把所有數字相加",
                "\t\t(3)\t只比較前兩個數字",
                "",
            ]
            + o("只有 (1)", "只有 (2)", "只有 (3)", "(1) 較合理（視演算法而定）"),
            ["下列哪一項最能描述免費軟件（Freeware）？", ""] + o("原始碼必定公開且可自由修改", "可免費使用但未必提供原始碼", "只能試用 30 天", "必須付費取得授權金鑰"),
            ["「數碼足跡（Digital Footprint）」最主要是指？", ""] + o("鍵盤上的灰塵量", "使用者在網上活動留下的可追溯資料與紀錄", "螢幕解析度", "CPU 快取大小"),
            ["下列哪一項最能描述共享軟件（Shareware）？", ""] + o("必定完全免費且無限制", "常以便攜式（試用後付費）模式出現", "等同開源軟件", "只能於伺服器端執行"),
            ["下列哪一項最能描述開源軟件（Open-source）授權特點（一般情況）？", ""] + o("原始碼必定不可檢視", "通常允許檢視／修改與再分發（視授權條款而定）", "必定不能商業使用", "等同免費軟件"),
            [
                "相對於 WPA2，WPA3 在 Wi‑Fi 安全上常見的改進敘述，下列何者較合理？",
                "",
                "\t\t(1)\t更強的加密與金鑰交換機制（概念層面）",
                "\t\t(2)\t保證任何情況下都不需要密碼",
                "\t\t(3)\t只影響有線網路而不影響無線",
                "",
            ]
            + o("只有 (1)", "只有 (2)", "只有 (3)", "(1) 正確"),
            [
                "下列哪些屬於 VPN 的典型用途？",
                "",
                "\t\t(1)\t在公共網絡上建立加密通道連回內部網絡",
                "\t\t(2)\t把螢幕亮度自動調到最大",
                "\t\t(3)\t隱藏或改變對外連線路徑（視設定而定）",
                "",
            ]
            + o("只有 (1)", "只有 (1) 和 (3)", "只有 (2)", "(1)、(2) 和 (3)"),
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
                "\tX ← 2  ",
                "\tY ← 0  ",
                "\tWHILE X < 20 DO  ",
                "\t\tY ← Y + X  ",
                "\t\tX ← X * 2  ",
                "\tOUTPUT Y  ",
                "",
            ]
            + o("6", "14", "22", "30"),
            [
                "瀏覽網站時，DNS／HTTP／TCP／IP 的分工，下列敘述何者較正確？",
                "",
                "\t\t(1)\tDNS：把網域名稱解析為 IP",
                "\t\t(2)\tHTTP：定義網頁資源的傳輸語意（應用層）",
                "\t\t(3)\tTCP：提供可靠傳輸；IP：負責路由",
                "\t\t（以上為一般課程描述，可能因教材用語略有差異）",
                "\t\t（請以「最合理」為準選擇答案）",
                "",
            ]
            + o("只有 (1)", "只有 (1) 和 (2)", "只有 (3)", "(1)、(2) 和 (3)"),
            [
                "下列兩段程式碼同樣搜尋陣列，但哪一段通常執行時間較短？（P1：線性搜尋；P2：已排序陣列的二分搜尋）",
                "",
                "",
            ]
            + o("P1 較快", "P2 較快", "兩者相若", "無法比較"),
            ["下列哪一項最屬於模組化（Modularisation）？", ""] + o("把所有程式寫在同一檔且不重複使用", "把問題拆成小模組分別設計與測試", "只使用一個變數名稱", "刪除所有註解"),
            [
                "某班要為下列分段評級程式設計測試數據，以覆蓋所有分支：",
                "",
                "\t\tINPUT score",
                "\t\tIF score > 80 THEN OUTPUT \"A\"",
                "\t\tELSE IF score >= 50 THEN OUTPUT \"B\"",
                "\t\tELSE OUTPUT \"F\"",
                "",
                "\t哪一組輸入分數最適合？",
                "",
                "",
            ]
            + o("45, 60, 90", "40, 85", "50, 81", "30, 75, 80"),
            ["在演算法設計中使用陣列的主要好處是？", ""] + o("減少記憶體使用量", "適合需要重複運算或儲存多個同類資料", "可儲存不同資料類型", "可提高運算速度"),
            [
                "某校網站使用子網域：",
                "",
                "\t\tlearn.school.edu.hk",
                "",
                "\t\tshop.school.edu.hk",
                "",
                "\t\tmail.school.edu.hk",
                "",
                "\t最少需要註冊多少個網域名稱（domain name）？",
                "",
            ]
            + o("4", "3", "2", "1"),
        ]
    )
    expected = [6, 6, 6, 6, 6, 10, 8, 10, 6, 6, 6, 6, 10, 6, 10, 10, 6, 6, 6, 6, 10, 10, 9, 13, 12, 7, 6, 14, 6, 14]
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
    put(323, "2.\t網絡與保安\t(10 分)")
    put(326, "(a)\t相對於 WPA2，WPA3 在 Wi‑Fi 安全性上的主要改進是什麼？（從加密強度／金鑰交換概念說明）\t(3 分)")
    put(328, "(b)\t學生在家中上網，想安全存取學校內聯網資源。應建議使用哪種技術？說明其原理（加密通道／隧道）。\t(4 分)")
    put(331, "(c)\t除上述技術外，提出兩項可提升家庭網絡安全的做法並解釋。\t(3 分)")
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

    put(423, "丙部 (40 分)：選修單元問答題（數據庫 + 網絡應用程式開發）")
    put(425, "選修 A：數據庫（Database）")
    put(
        427,
        "某「網上課程報名系統」描述如下：一位學員可報名多個課程；一個課程亦可被多位學員報名。"
        "每次報名產生一筆報名記錄，包含報名日期與付款狀態。",
    )
    put(
        440,
        "(a)\t繪製實體關係圖（ERD）：須包含「學員 Student」「課程 Course」「報名 Enrolment」三個實體，標示多對多並以關聯實體拆解；"
        "並在圖中寫出主鍵（PK）與外鍵（FK）欄位名稱。\t(8 分)",
    )
    put(442, "(b)\t設資料表如下：")
    put(444, "Student(StudentID, StudentName, JoinDate)")
    put(445, "Course(CourseID, CourseName, Tutor, Fee)")
    put(446, "Enrolment(EnrolmentID, StudentID, CourseID, EnrolmentDate, Status)")
    put(450, "(i)\t寫出一條 SQL，列出所有報名了 Tutor = 'Peter' 的課程之學生姓名（StudentName）。\t(4 分)")
    put(453, "(ii)\t寫出一條 SQL，找出報名人數 **超過 30** 的課程名稱（CourseName）及其報名人數。（需使用 COUNT、GROUP BY、HAVING）\t(6 分)")
    put(455, "(iii)\t寫出一條 SQL，找出 **從未報名任何課程** 的學生姓名。（可用 NOT IN 或 NOT EXISTS）\t(6 分)")
    put(457, "選修 B：網絡應用程式開發（Web Application Development）")
    put(459, "1.\t註冊表單情境：使用者輸入「用戶名」「密碼」「確認密碼」後按提交。\t(10 分)")
    put(461, "(a)\t「檢查密碼與確認密碼是否一致」應在客戶端、伺服器端，或兩者皆需要？說明優點與原因。\t(4 分)")
    put(463, "(b)\t「檢查用戶名是否已被註冊」為何必須在伺服器端執行？\t(3 分)")
    put(470, "(c)\t此類表單提交應使用 HTTP GET 還是 POST？為什麼？\t(3 分)")
    put(482, "2.\t網頁編程實踐（BMI 小工具）\t(10 分)")
    put(485, "考慮一段網頁包含：輸入框 id=`height`、id=`weight`，按鈕可觸發計算，結果顯示於 id=`result-display` 的 div。")
    put(487, "(a)\t寫出 CSS：把 `#result-display` 的文字顏色設為紅色。\t(2 分)")
    put(489, "(b)\t寫出 JavaScript：讀取兩個輸入框的數值，計算 BMI=體重/(身高米)^2（身高以米計），把結果寫入 `result-display`。\t(5 分)")
    put(492, "(c)\t若要把計算結果儲存到伺服器：描述客戶端按「保存」後應傳送哪些資料；伺服器端（如 PHP）需做哪些步驟（連線資料庫、INSERT 等）。\t(3 分)")
    return lines


def clear_answer_pages(doc: Document) -> None:
    note = "（本擬題稿不附標準答案；教師可自行增刪。）"
    for i in range(635, len(doc.paragraphs)):
        doc.paragraphs[i].text = ""
    if len(doc.paragraphs) > 635:
        doc.paragraphs[635].text = note


def generate(template: Path, output: Path, *, footer_meta: dict | None = None) -> None:
    shutil.copy(template, output)
    doc = Document(str(output))
    # Cover: keep template table 0 unchanged (do not assign cell.text).
    blocks = mcq_blocks(doc)
    apply_mcq(doc, blocks, build_mcq_payload())
    replace_span(doc, 313, 422, build_part_b())
    replace_span(doc, 423, 624, build_part_c())
    clear_answer_pages(doc)
    doc.save(str(output))
    if footer_meta:
        apply_footer_meta(output, footer_meta)


def main(argv: list[str] | None = None) -> int:
    root = repo_root()
    default_out = root / "Subjects/PastPaper/CMP+ICT/2024-2025/2nd Term/F5 ICT"
    ap = argparse.ArgumentParser(
        description="F5 ICT blueprint: build exam spec → compare → optional DOCX render.",
    )
    ap.add_argument(
        "--template",
        type=Path,
        default=default_out / "24_25_S5_ICT_Exam02.docx",
    )
    ap.add_argument(
        "--output",
        type=Path,
        default=default_out / "25_26_S5_ICT_Exam02_Blueprint_DB-Web.docx",
    )
    ap.add_argument(
        "--spec",
        type=Path,
        default=default_out / "25_26_S5_ICT_Exam02_Blueprint_DB-Web.spec.json",
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

    spec = build_f5_ict_exam_spec()
    save_spec(spec_path, spec)
    print(f"Wrote spec: {spec_path}")

    check_code = 0
    if not args.skip_check:
        check_code = run_spec_check(
            candidate_spec=spec_path,
            template=template,
            years=args.years,
            subject_subpath=args.subject,
            json_report=dup_report,
            strict=args.strict,
        )

    should_render = args.render_anyway or args.render or (check_code == 0 and not args.skip_check)
    if args.skip_check:
        should_render = True

    if should_render:
        output.parent.mkdir(parents=True, exist_ok=True)
        generate(template, output, footer_meta=spec.get("meta", {}).get("footer"))
        print(f"Wrote DOCX: {output}")
        if not args.skip_check:
            from footer import check_footer, format_footer_report

            footer_result = check_footer(
                output,
                expected_meta=spec.get("meta", {}).get("footer"),
                template=template,
            )
            print("\n--- Footer banner check (rendered DOCX) ---")
            print(format_footer_report(footer_result))
            if not footer_result.ok:
                print("Footer mismatch — update meta.footer or template footer, then re-render.")
                if args.strict:
                    return 2
                if not args.render_anyway:
                    return 1
    elif check_code != 0:
        print("DOCX not rendered (duplicates found). Fix spec / regenerate IDs, then re-run with --render.")

    return check_code


if __name__ == "__main__":
    raise SystemExit(main())
