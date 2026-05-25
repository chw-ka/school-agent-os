"""Paragraph content for F5 ICT Exam02 — 25-26 DSE blueprint (Core A/B/D + Module A/C)."""

from __future__ import annotations

from written_layout import ANSWER_BLANK, ANSWER_BLANK_LONG, code_line, sql_line, stem, subpart

try:
    from f5_ict_written_from_dse import scenario_override
except ImportError:
    def scenario_override(_slot_id: str, default: str) -> str:  # type: ignore[misc]
        return default


def build_part_b() -> list[str]:
    """Return 110 lines for paragraphs 313–422 inclusive."""
    lines: list[str] = [""] * 110
    base = 313

    def put(i: int, s: str) -> None:
        lines[i - base] = s

    # --- B1: spreadsheet — charity sale (4 marks) ---
    put(
        313,
        scenario_override(
            "b-01",
            "「煦風書社」以試算表記錄義賣收入。欄位：A=日期、B=商品、C=單價、D=數量、"
            "E=會員（Y／N）、F=總價；$H$2:$I$10 為參考單價對照表。部分資料見下表。",
        ),
    )
    put(
        314,
        subpart(
            "a",
            "在 F2 寫出一條 IF 公式並複製至 F3:F50：若 E2 為「Y」且 D2≥5，"
            "總價為 C2*D2×0.9；否則為 C2*D2。寫出 F2 的公式。",
            2,
        ),
    )
    put(315, ANSWER_BLANK)
    put(
        316,
        subpart(
            "b",
            "在 G2 使用 COUNTIF 統計 D$2:D$50 中數量≥5 的個數，寫出公式。",
            2,
        ),
    )
    put(317, ANSWER_BLANK)

    # --- B2: computer system + future tech (5 marks) — blueprint 25-26 ---
    put(
        323,
        scenario_override(
            "b-02",
            "「煦風書社」擬為社企添置桌上電腦，主要部件包括 CPU、RAM、儲存裝置及顯示器。"
            "下表列出兩款候選規格。",
        ),
    )
    put(
        324,
        subpart(
            "a",
            "就下表所列部件，各舉一例說明其功能（須與部件直接相關）。",
            2,
        ),
    )
    put(325, ANSWER_BLANK)
    put(
        326,
        subpart(
            "b",
            "說明人工智能可如何協助社企管理日常運作，並舉出一項限制。",
            3,
        ),
    )
    put(327, ANSWER_BLANK)
    put(328, "")
    put(329, "")
    put(330, "")
    put(331, "")
    put(332, "")
    put(333, "")
    put(334, "")
    put(335, "")

    # --- B3: multimedia file size (4 marks) — Core A, no networking ---
    put(
        336,
        scenario_override(
            "b-03",
            "攝影學會以未壓縮 BMP 儲存活動相片：每張 1600×1200 像素、24 bit 真彩色。"
            "規格見下表。",
        ),
    )
    put(
        337,
        subpart(
            "a",
            "估算 80 張相片的總檔案大小（以 MB 表示，展示計算）。",
            2,
        ),
    )
    put(338, ANSWER_BLANK)
    put(339, ANSWER_BLANK_LONG)
    put(340, subpart("b", "比較以 JPEG（有損）與 PNG（無損）儲存同一批相片的取捨。", 2))
    put(341, ANSWER_BLANK)
    put(343, "")
    put(345, subpart("i", "哪種格式檔案通常較小？為什麼？", 1, depth=2))
    put(346, ANSWER_BLANK)
    put(349, subpart("ii", "若需保留最高畫質供印刷，應選哪種？簡述。", 1, depth=2))
    put(350, ANSWER_BLANK)

    # --- B4: linear search trace (4 marks) ---
    put(354, scenario_override("b-04", "考慮陣列 A（索引由 1 開始，n=6）及以下線性搜尋算法："))
    put(355, "")
    put(356, code_line("found ← FALSE"))
    put(357, code_line("i ← 1"))
    put(358, code_line("WHILE i ≤ n AND found = FALSE DO"))
    put(359, code_line("    IF A[i] = key THEN found ← TRUE"))
    put(360, code_line("    i ← i + 1"))
    put(361, code_line("ENDWHILE"))
    put(362, code_line("IF found = TRUE THEN OUTPUT i ELSE OUTPUT 0"))
    put(363, "")
    put(
        366,
        subpart(
            "a",
            "設 A = [9, 8, 5, 7, 9, 6]、key = 5。完成追蹤表，列出每次迴圈後 i 與 found 的值，並寫出最終 OUTPUT。",
            2,
        ),
    )
    put(367, ANSWER_BLANK)
    put(368, "")
    put(370, subpart("b", "說明此算法屬線性搜尋的原因。", 2))
    put(371, ANSWER_BLANK)
    for i in (372, 373, 374, 375, 376):
        put(i, "")

    # --- B5: SQL (4 marks) ---
    put(
        377,
        scenario_override(
            "b-05",
            "「煦風」網店使用資料表 TRANSACTION(TID, Item, Qty, ADate) 記錄交易，部分記錄見下表。",
        ),
    )
    put(378, subpart("a", "寫出 CREATE TABLE TRANSACTION（TID 為主鍵，Item 不可為空）。", 2, spaced_marks=True))
    put(379, ANSWER_BLANK)
    put(380, subpart("b", "寫出一條 SELECT，列出 Qty ≥ 5 的 Item 及 Qty。", 2, spaced_marks=True))
    put(381, ANSWER_BLANK)
    put(382, "")
    put(383, "")
    put(384, "")
    put(385, "")
    put(386, "")
    put(387, "")
    put(388, "")
    put(389, "")
    put(390, "")
    put(391, "")
    put(392, "")
    put(393, "")

    # --- B6: hardware comparison (9 marks) ---
    put(
        394,
        scenario_override(
            "b-06",
            "攝影學會擬為社員添置筆記本電腦，完成下表比較兩款候選硬件規格。",
        ),
    )
    put(395, subpart("a", "列出 CPU 規格欄可填寫的兩個例子。", 2, spaced_marks=True))
    put(396, ANSWER_BLANK)
    put(397, subpart("b", "說明增加 RAM 對多工處理的影響。", 2, spaced_marks=True))
    put(398, ANSWER_BLANK)
    put(399, "")
    put(400, subpart("c", "比較 SSD 與 HDD 作為系統碟的優缺點。", 2, spaced_marks=True))
    put(401, ANSWER_BLANK)
    put(402, "")
    put(403, subpart("d", "舉出一項須同時升級硬件與軟件的情況並說明。", 3, spaced_marks=True))
    put(404, ANSWER_BLANK)
    put(405, ANSWER_BLANK_LONG)
    for i in range(406, 423):
        put(i, "")

    return lines


def build_part_c() -> list[str]:
    """Return 202 lines for paragraphs 423–624 inclusive."""
    lines: list[str] = [""] * 202
    base = 423

    def put(i: int, s: str) -> None:
        lines[i - base] = s

    put(
        423,
        "丙部 (40分)：Module A 數據庫 (20分) + Module C 程式開發 (20分) — 不設多項選擇題",
    )
    put(424, "— Module A 數據庫（20 分）—")

    # C1 — ERD (6 marks)
    put(
        425,
        scenario_override(
            "c-01",
            "某院線公司開發會員預訂系統：每位會員可建立多張預訂；每張預訂對應一個場次；"
            "每間戲院每日有多個場次。",
        ),
    )
    put(
        427,
        stem(
            "繪製實體關係圖（ERD），標示 Member、Booking、Screening、Cinema 及主鍵／外鍵。",
            6,
            spaced_marks=True,
        ),
    )
    put(429, "\t\t")

    # C2 — 欄位限制 (4 marks)
    put(440, scenario_override("c-02", "某社企圖書館使用 MEMBER 及 LOAN 資料表，須符合欄位限制。"))
    put(442, subpart("a", "在下列 CREATE TABLE 補充 MID 主鍵及 TITLE 的 NOT NULL。", 2, spaced_marks=True))
    put(444, sql_line("CREATE TABLE LOAN ("))
    put(445, sql_line("    MID CHAR(6),", depth=4))
    put(446, sql_line("    BID CHAR(8),", depth=4))
    put(447, sql_line("    TITLE VARCHAR(80),", depth=4))
    put(448, sql_line("    LOANDATE DATE", depth=4))
    put(449, sql_line(")"))
    put(451, subpart("b", "說明外鍵 LOAN(MID) REFERENCES MEMBER(MID) 如何維護參照完整性。", 2, spaced_marks=True))
    put(452, ANSWER_BLANK_LONG)
    put(454, ANSWER_BLANK_LONG)

    # C3 — 冗餘與完整性 (4 marks)
    put(
        457,
        scenario_override(
            "c-03",
            "早期設計把會員姓名、電話直接寫入每筆 LOAN 記錄；同一會員借多本書時資料重複，"
            "更改電話須更新多筆記錄。",
        ),
    )
    put(461, subpart("a", "指出上述設計的數據冗餘，並說明可能導致的更新異常。", 2, spaced_marks=True))
    put(462, ANSWER_BLANK_LONG)
    put(464, subpart("b", "建議如何分拆資料表以改善完整性（述主鍵／外鍵角色，不須完整 ERD）。", 2, spaced_marks=True))
    put(465, ANSWER_BLANK_LONG)

    # C5 — SQL 綜合 (6 marks) — still Module A; Module C header before c-06
    put(
        496,
        scenario_override(
            "c-05",
            "社區中心資料庫含 MEMBER(MID, MName)、FACILITY(FID, FName)、"
            "RESERVE(RID, MEMID, FID, RDATE)。樣本資料見下表。",
        ),
    )
    put(497, subpart("a", "寫出 INNER JOIN：列出每位會員姓名及其預訂的設施名稱。", 2, spaced_marks=True))
    put(498, ANSWER_BLANK_LONG)
    put(499, subpart("b", "寫出 GROUP BY：統計各設施被預約次數，只列出次數≥2 的設施。", 2, spaced_marks=True))
    put(500, ANSWER_BLANK_LONG)
    put(501, subpart("c", "寫出 UNION 或 MINUS：比較兩組設施的會員／預約差異（擇一並說明）。", 2, spaced_marks=True))
    put(502, ANSWER_BLANK_LONG)
    for i in range(503, 540):
        put(i, "")

    put(540, "— Module C 程式開發（20 分）—")

    # C6 — 二維陣列 + 堆疊 (7 marks)
    put(
        541,
        scenario_override(
            "c-06",
            "某遊戲以二維陣列 Grid[row][col] 表示地圖（0=通道，1=牆）；玩家移動及「復活」"
            "位置以堆疊記錄。地圖見下表。",
        ),
    )
    put(542, subpart("a", "寫出判斷 Grid[3][2] 是否為牆的條件；若 Grid[3][2]=1 且 Grid[3][3]=0，說明能否向右移。", 3, spaced_marks=True))
    put(543, ANSWER_BLANK_LONG)
    put(544, subpart("b", "依次 PUSH 2、5、9、POP、PUSH 1、POP，列出每次 POP 的輸出及最終堆疊頂端。", 4, spaced_marks=True))
    put(545, ANSWER_BLANK_LONG)
    put(546, ANSWER_BLANK_LONG)
    for i in range(547, 566):
        put(i, "")

    # C7 — 隊列 + 二分搜尋 (7 marks)
    put(
        566,
        scenario_override(
            "c-07",
            "診所輪候系統以隊列處理先到先得；學生證編號已按升序存入陣列 ID[1..N] 供登入核對。",
        ),
    )
    put(569, subpart("a", "說明 Enqueue／Dequeue 如何實現輪候；舉一例 Dequeue 後 Front 及 Rear 的變化。", 3, spaced_marks=True))
    put(570, ANSWER_BLANK_LONG)
    put(572, subpart("b", "用二分搜尋在 ID 中查找「S1042」，描述 mid 如何移動（至少兩步）。", 4, spaced_marks=True))
    put(573, ANSWER_BLANK_LONG)
    put(574, ANSWER_BLANK_LONG)

    # C8 — 排序 + 陣列鏈表 (6 marks)
    put(
        595,
        scenario_override(
            "c-08",
            "電競社以陣列 Next[1..N] 及 Head 模擬鏈表儲存輪候參賽者；每日關閉前須把 Score[1..M] "
            "按降序整理並更新鏈表順序。",
        ),
    )
    put(
        597,
        "管理員記錄：Score = [72, 45, 90, 45, 61, 88, 33, 77]（索引 1 至 8），Head 指向第一個"
        "有效參賽者；刪除 Score=45 的結點後須重新連結 Next 指標。",
    )
    put(598, subpart("a", "對 Score 執行一次冒泡排序（降序）的首輪比較，寫出需交換的一對索引。", 2, spaced_marks=True))
    put(599, ANSWER_BLANK)
    put(600, "")
    put(
        601,
        subpart(
            "b",
            "說明如何以 Head 及 Next[] 走訪仍參賽者；刪除一個 Score=45 的結點後，"
            "描述 Head／Next 如何更新，並述此結構與陣列模擬鏈表的優點。",
            4,
            spaced_marks=True,
        ),
    )
    put(602, ANSWER_BLANK_LONG)
    put(603, ANSWER_BLANK_LONG)
    put(604, ANSWER_BLANK_LONG)

    return lines
