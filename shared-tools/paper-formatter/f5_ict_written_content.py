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
            "E=會員（Y／N）、F=總價。部分資料如下：",
        ),
    )
    put(
        316,
        subpart(
            "a",
            "在 F2 寫出一條公式並複製至 F3:F50。若 E2 為「Y」且 D2≥5，總價為 C2*D2 的 9 折；"
            "否則為 C2*D2。",
            1,
        ),
    )
    put(317, ANSWER_BLANK)
    put(
        319,
        subpart(
            "b",
            "在 H2 寫出一條公式（可用 COUNTIFS），複製至 H3:H5，分別統計："
            "會員訂單數、非會員訂單數及總銷售額。寫出 H2 的公式。",
            3,
        ),
    )
    put(320, ANSWER_BLANK)

    # --- B2: data validation table (5 marks) ---
    put(
        323,
        scenario_override(
            "b-02",
            stem("完成下表，為網上報名欄位選擇適當的數據有效性檢驗。", 3, spaced_marks=True),
        ),
    )
    put(326, subpart("b", "試算表可設定數據有效性以減少輸入錯誤。"))
    put(328, subpart("i", "說明「數據有效性檢驗」與「奇偶檢測」的分別。", 1, depth=2))
    put(329, ANSWER_BLANK)
    put(331, subpart("ii", "為「班別」欄建議一種有效性規則並舉例。", 1, depth=2))
    put(332, ANSWER_BLANK)

    # --- B3: multimedia file size (4 marks) — Core A, no networking ---
    put(
        336,
        scenario_override(
            "b-03",
            "攝影學會以未壓縮 BMP 儲存活動相片：每張 1600×1200 像素、24 bit 真彩色。",
        ),
    )
    put(
        338,
        subpart(
            "a",
            "估算 80 張相片的總檔案大小（以 MB 表示，展示計算）。",
            2,
        ),
    )
    put(339, ANSWER_BLANK)
    put(340, ANSWER_BLANK_LONG)
    put(343, subpart("b", "比較以 JPEG（有損）與 PNG（無損）儲存同一批相片的取捨。"))
    put(345, subpart("i", "哪種格式檔案通常較小？為什麼？", 1, depth=2))
    put(346, ANSWER_BLANK)
    put(349, subpart("ii", "若需保留最高畫質供印刷，應選哪種？簡述。", 1, depth=2))
    put(350, ANSWER_BLANK)

    # --- B4: linear search trace — Core D / Module C (4 marks) ---
    put(
        354,
        scenario_override(
            "b-04",
            "考慮陣列 A（索引由 1 開始，n=6）及以下搜尋算法（尋找值 key）：",
        ),
    )
    put(357, stem("執行下列算法："))
    put(359, code_line("found ← FALSE"))
    put(360, code_line("i ← 1"))
    put(361, code_line("WHILE i ≤ n AND found = FALSE DO"))
    put(362, code_line("    IF A[i] = key THEN", depth=2))
    put(363, code_line("        found ← TRUE", depth=3))
    put(364, code_line("    i ← i + 1", depth=2))
    put(
        366,
        subpart(
            "a",
            "設 A = [4, 9, 2, 9, 7, 1]、key = 9。完成追蹤表，展示每次迴圈後 i 與 found。",
            2,
        ),
    )
    put(367, ANSWER_BLANK)
    put(370, subpart("b", "若 key 不在陣列內，算法結束時 i 的值是多少？解釋。", 2))
    put(371, ANSWER_BLANK)
    put(373, stem("請在答案中說明此算法屬「線性搜尋」的原因。"))

    # --- B5: file access (4 marks) ---
    put(
        377,
        scenario_override("b-05", "校園相簿系統以索引檔記錄每張相片的編號與儲存位置。"),
    )
    put(385, stem("系統可以「直接存取」或「順序存取」索引檔。"))
    put(387, subpart("a", "比較兩種方式查找特定相片編號的優缺點。", 2, spaced_marks=True))
    put(388, ANSWER_BLANK)
    put(
        390,
        subpart("b", "若索引按相片編號排序，查找時哪種方式較適合？舉一項校內應用。", 2, spaced_marks=True),
    )
    put(391, ANSWER_BLANK)
    put(393, ANSWER_BLANK)

    # --- B6: ORDER / CLIENT database (9 marks) — Module A intro ---
    put(
        394,
        scenario_override(
            "b-06",
            "「綠途生活」網店以網上表格收集訂單，並把資料匯入 ORDER 資料表"
            "（OID、CNAME、PHONE、EMAIL、ORDER_DATE）。",
        ),
    )
    put(396, subpart("a", "試指出使用網上表格相對紙本表格的兩項好處。", 2, spaced_marks=True))
    put(398, ANSWER_BLANK)
    put(
        400,
        subpart(
            "b",
            "為電話及電郵欄各建議一種數據有效性檢驗方法，並舉例。",
            2,
            spaced_marks=True,
        ),
    )
    put(401, subpart("i", "電話號碼", depth=1))
    put(402, ANSWER_BLANK)
    put(404, subpart("ii", "電郵地址", depth=2))
    put(407, stem("以下是 ORDER 資料表部分記錄："))
    put(410, subpart("c", "PHONE 欄應使用哪種資料類型？為什麼？", 2, spaced_marks=True))
    put(412, ANSWER_BLANK)
    put(414, subpart("d", "執行以下 SQL 後的輸出是什麼？", 1, spaced_marks=True))
    put(415, ANSWER_BLANK)
    put(416, sql_line("SELECT CNAME FROM ORDER WHERE ORDER_DATE < '2026-03-01';"))
    put(419, subpart("e", "寫出一條 SQL，列出所有於 5 月落單的客戶名稱。", 2, spaced_marks=True))
    put(420, ANSWER_BLANK)

    return lines


def build_part_c() -> list[str]:
    """Return 202 lines for paragraphs 423–624 inclusive."""
    lines: list[str] = [""] * 202
    base = 423

    def put(i: int, s: str) -> None:
        lines[i - base] = s

    put(423, "丙部 (40分)：選修單元問答題（數據庫及程式開發）— 不設多項選擇題")

    # C1 — ERD cinema booking (4 marks) — blueprint: 2024 Paper2A
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
            4,
            spaced_marks=True,
        ),
    )
    put(429, "\t\t")

    # C2 — CREATE / INSERT (2 marks)
    put(440, scenario_override("c-02", "某社企使用 MOVIE 資料表記錄租借影碟。"))
    put(442, subpart("a", "補充以下 SQL，使 MID 不可重複。", 1, spaced_marks=True))
    put(444, sql_line("CREATE TABLE MOVIE ("))
    put(445, sql_line("    MID CHAR(6)\t\t\t\t,", depth=4))
    put(446, sql_line("    TITLE VARCHAR(60),", depth=4))
    put(447, sql_line("    RENTAL INTEGER", depth=4))
    put(448, sql_line(")"))
    put(450, subpart("b", "以下記錄將插入 MOVIE。", 1, spaced_marks=True))
    put(453, sql_line("INSERT INTO MOVIE VALUES (                                )"))
    put(455, stem("寫出此 SQL 語句中未填寫的部分。"))

    # C3 — UNION / UPDATE (3 marks)
    put(457, scenario_override("c-03", "Order2024 與 Order2025 結構相同，部分記錄如下："))
    put(459, "\t\tOrder2024\t\tOrder2025")
    put(461, subpart("a", "執行以下 SQL 後會列出多少筆記錄？", 1, spaced_marks=True))
    put(463, sql_line("SELECT *"))
    put(464, sql_line("FROM Order2024"))
    put(465, sql_line("UNION"))
    put(466, sql_line("SELECT PID, SID, AMT"))
    put(467, sql_line("FROM Order2025;"))
    put(469, ANSWER_BLANK_LONG)
    put(470, subpart("b", "列出執行以下 SQL 後 Order2024 內被更新的記錄。", 2, spaced_marks=True))
    put(472, sql_line("UPDATE Order2024"))
    put(473, sql_line("SET AMT = 0"))
    put(474, sql_line("WHERE AMT > 0 AND"))
    put(475, sql_line("    (EXISTS", depth=4))
    put(476, sql_line("        (SELECT * FROM Order2025", depth=5))
    put(477, sql_line("         WHERE Order2024.PID = Order2025.PID", depth=5))
    put(478, sql_line("           AND Order2025.AMT = 0);", depth=7))

    # C4 — removed (was 3NF sports, 3 marks) — slots left blank for template span

    # C5 — FACILITY / RESERVE (11 marks)
    put(496, scenario_override("c-05", "某社區中心資料庫包含 FACILITY 及 RESERVE 資料表："))
    put(498, "FACILITY")
    put(500, "RESERVE")
    put(502, subpart("a", "寫出 MEMID 欄的合適數據類型並簡略說明。", 1, spaced_marks=True))
    put(504, ANSWER_BLANK_LONG)
    put(506, subpart("b", "為以下任務寫出 SQL："))
    put(
        508,
        subpart(
            "i",
            "列出預約編號以「R26」開頭的記錄，按日期升序。",
            2,
            depth=2,
            spaced_marks=True,
        ),
    )
    put(510, ANSWER_BLANK_LONG)
    put(513, subpart("ii", "列出 2026-07-12 預約的所有設施名稱。", 2, depth=2, spaced_marks=True))
    put(515, ANSWER_BLANK_LONG)
    put(
        518,
        subpart(
            "iii",
            "列出曾預約容量少於 25 的設施之會員編號（不重複）。",
            3,
            depth=2,
            spaced_marks=True,
        ),
    )
    put(520, ANSWER_BLANK_LONG)
    put(526, subpart("c", "簡述以下 SQL 的用途。", 2, spaced_marks=True))
    put(528, sql_line("SELECT FID FROM FACILITY"))
    put(529, sql_line("MINUS"))
    put(530, sql_line("SELECT FID FROM RESERVE;"))
    put(532, ANSWER_BLANK_LONG)
    put(536, subpart("d", "簡述非規範化 FACILITY 與 RESERVE 的一個方法。", 1, spaced_marks=True))

    # C6 — SQL trace (5 marks)
    put(541, scenario_override("c-06", "考慮 Member 與 Enrol 資料表，以下 SQL 逐步執行："))
    put(544, stem("設初始結果為空。"))
    put(547, subpart("a", "第一次 JOIN 後結果包含哪些 MemberID？", 1, spaced_marks=True))
    put(550, subpart("ii", "加入 GROUP BY 後結果如何變化？", 1, depth=2, spaced_marks=True))
    put(553, subpart("iii", "加入 HAVING COUNT(*) > 1 後最終結果是什麼？", 1, depth=2, spaced_marks=True))
    put(556, subpart("b", "此查詢找出哪類會員？", 1, spaced_marks=True))
    put(559, subpart("c", "若改為 LEFT JOIN，結果有何不同？簡述。", 1, spaced_marks=True))

    # C7 — transactions (9 marks)
    put(
        566,
        scenario_override(
            "c-07",
            "校園一卡通系統使用交易（Transaction）確保扣款一致。常用子句如下：",
        ),
    )
    put(569, subpart("a", "寫出 BEGIN…COMMIT 與 ROLLBACK 的用途各一項。", 1, spaced_marks=True))
    put(571, sql_line("UPDATE Account SET Balance = Balance - 30 WHERE StudentID = 'S002';"))
    put(574, subpart("b", "若第二步 UPDATE 失敗，應執行哪個子句？為什麼？", 1, spaced_marks=True))
    put(577, stem("試描述如何確保兩個 UPDATE 同時成功或同時失敗。"))
    put(579, sql_line("BEGIN TRANSACTION"))
    put(580, sql_line("UPDATE Wallet SET Balance = Balance - 50 WHERE SID = 'S001';"))
    put(581, sql_line("UPDATE Canteen SET Income = Income + 50 WHERE ID = 'C01';"))
    put(582, sql_line("IF @@ERROR <> 0"))
    put(583, sql_line("    ROLLBACK"))
    put(584, sql_line("ELSE"))
    put(585, sql_line("    COMMIT"))
    put(588, subpart("c", "寫出 PAY(SID, AMOUNT) 的偽代碼，使用 BEGIN/COMMIT/ROLLBACK。", 3, spaced_marks=True))
    put(590, sql_line("PAY(SID, AMOUNT)"))
    put(592, subpart("d", "說明若無交易控制，扣款中斷可能造成什麼資料不一致。", 4, spaced_marks=True))

    # C8 — stack / Module C (6 marks)
    put(
        595,
        scenario_override(
            "c-08",
            "某程式以堆疊（Stack）儲存運算元，以下為初始狀態及 PUSH／POP 操作：",
        ),
    )
    put(597, "堆疊底在左，頂端在右。")
    put(598, "完成下表（首四步）後，繼續追蹤 PUSH 2、POP、POP。")
    put(600, stem("操作序列：PUSH 3；PUSH 7；POP；PUSH 2；POP；POP"))
    put(602, stem("Stack 狀態", depth=2))
    put(604, stem("老師設計 trace_stack 追蹤每次操作後的堆疊頂端："))
    put(606, code_line("trace_stack"))
    put(607, code_line("10  op ← 1"))
    put(608, code_line("20  WHILE op ≤ 6 DO"))
    put(609, code_line("30      執行第 op 步操作並記錄 stack 頂端"))
    put(610, code_line('40      顯示 "Step op: top = …"'))
    put(611, code_line("50      op ← op + 1"))
    put(613, subpart("a", "完成追蹤表，列出每步後 stack 頂端元素。", 2, spaced_marks=True))
    put(615, subpart("b", "若先 POP 再 PUSH 順序對調，結果有何不同？簡述。", 2, spaced_marks=True))
    put(617, ANSWER_BLANK_LONG)
    put(
        620,
        subpart("c", "說明堆疊「後進先出」在此題中的意義。", 2, spaced_marks=True),
    )
    put(622, ANSWER_BLANK_LONG)

    return lines
