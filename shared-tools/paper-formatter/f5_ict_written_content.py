"""Paragraph content for F5 ICT Exam02 — matches 24_25 template slot layout (6 × 乙部, 8 × 丙部)."""

from __future__ import annotations

from written_layout import ANSWER_BLANK, ANSWER_BLANK_LONG, code_line, sql_line, stem, subpart


def build_part_b() -> list[str]:
    """Return 110 lines for paragraphs 313–422 inclusive."""
    lines: list[str] = [""] * 110
    base = 313

    def put(i: int, s: str) -> None:
        lines[i - base] = s

    # --- B1: spreadsheet (4 marks) ---
    put(
        313,
        "「星晴網店」以試算表記錄訂單，欄位包括：A=訂單日期、B=產品類別、C=單價、D=數量、"
        "E=會員等級（VIP／一般）。F 欄為總價。資料如下：",
    )
    put(
        316,
        subpart(
            "a",
            "在 F2 寫出一條公式，然後複製到 F3:F200。規則：若 E2 為「VIP」且 D2>10，"
            "則總價為 C2*D2 的 8 折；否則為原價 C2*D2。",
            1,
        ),
    )
    put(317, ANSWER_BLANK)
    put(
        319,
        subpart(
            "b",
            "在 H2 寫出一條公式（可用 COUNTIFS），然後複製到 H3:H6，"
            "分別統計 VIP 訂單數、一般訂單數、總訂單數及總銷售額。寫出 H2 的公式。",
            3,
        ),
    )
    put(320, ANSWER_BLANK)

    # --- B2: data validation table (5 marks) ---
    put(323, stem("完成下表，為網上商店登記欄位選擇適當的數據有效性檢驗。", 3, spaced_marks=True))
    put(326, subpart("b", "試算表可設定數據有效性以減少輸入錯誤。"))
    put(328, subpart("i", "說明「數據有效性檢驗」與「奇偶檢測」的分別。", 1, depth=2))
    put(329, ANSWER_BLANK)
    put(331, subpart("ii", "為電郵欄建議一種有效性規則並舉例。", 1, depth=2))
    put(332, ANSWER_BLANK)

    # --- B3: multimedia / file transfer (4 marks) ---
    put(
        336,
        "志文把一段 250 MB 的評審短片上載至校內伺服器，並以電郵通知評審下載。",
    )
    put(
        338,
        subpart(
            "a",
            "上載頻寬為 200 Mbps。估算上載 40 段相同短片所需的最短時間。展示你的計算。",
            2,
        ),
    )
    put(339, ANSWER_BLANK)
    put(340, ANSWER_BLANK_LONG)
    put(343, subpart("b", "志文以電郵方式將以下訊息發送給評審："))
    put(345, subpart("i", "評審輸入 URL 亦能下載同一檔案。為什麼？", 1, depth=2))
    put(346, "http://203.186.200.12/ict2026/demo.zip")
    put(347, ANSWER_BLANK)
    put(349, subpart("ii", "使用附有超連結的電郵，而非直接附加檔案，有什麼優點？", 1, depth=2))
    put(350, ANSWER_BLANK)

    # --- B4: algorithm trace (4 marks) ---
    put(354, "考慮陣列 A（索引由 1 開始，n≥6）及以下偽代碼：")
    put(357, stem("執行下列算法："))
    put(359, code_line("largest ← A[1]"))
    put(360, code_line("second_largest ← A[1]"))
    put(361, code_line("FOR i ← 2 TO n"))
    put(362, code_line("    IF A[i] > largest THEN", depth=2))
    put(363, code_line("        second_largest ← largest; largest ← A[i]", depth=3))
    put(364, code_line("    ENDIF", depth=2))
    put(
        366,
        subpart(
            "a",
            "設 A = [10, 5, 20, 8, 20, 15]。完成追蹤表，展示每次迭代後 largest 與 second_largest。",
            2,
        ),
    )
    put(367, ANSWER_BLANK)
    put(370, subpart("b", "若最大值出現多次，此算法能否正確找出次大值？解釋。", 2))
    put(371, ANSWER_BLANK)
    put(373, stem("請在答案中說明重複最大值對 second_largest 的影響。"))

    # --- B5: file access (4 marks) — no diagram table ---
    put(377, "學校圖書館以電子化系統儲存學生借閱記錄。")
    put(385, stem("系統可以「直接存取」或「順序存取」記錄檔。"))
    put(387, subpart("a", "比較直接存取與順序存取讀取記錄的優缺點。", 2, spaced_marks=True))
    put(388, ANSWER_BLANK)
    put(
        390,
        subpart("b", "若記錄按學號排序，查找特定學號時哪種方式較適合？舉一項應用例子。", 2, spaced_marks=True),
    )
    put(391, ANSWER_BLANK)
    put(393, ANSWER_BLANK)

    # --- B6: CUSTOMER database (9 marks) ---
    put(
        394,
        "阿文與同學建立網上商店，以表格收集顧客資料（姓名、電話、電郵等），"
        "並把資料儲存至 CUSTOMER 資料表。",
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
    put(407, stem("以下是 CUSTOMER 資料表部分記錄："))
    put(410, subpart("c", "PHONE 欄應使用哪種資料類型？為什麼？", 2, spaced_marks=True))
    put(412, ANSWER_BLANK)
    put(414, subpart("d", "執行以下 SQL 後的輸出是什麼？", 1, spaced_marks=True))
    put(415, ANSWER_BLANK)
    put(416, sql_line("SELECT CNAME FROM CUSTOMER WHERE LAST_ORDER < '2026-04-01';"))
    put(419, subpart("e", "寫出一條 SQL，列出所有於 6 月下單的客戶名稱。", 2, spaced_marks=True))
    put(420, ANSWER_BLANK)

    return lines


def build_part_c() -> list[str]:
    """Return 202 lines for paragraphs 423–624 inclusive."""
    lines: list[str] = [""] * 202
    base = 423

    def put(i: int, s: str) -> None:
        lines[i - base] = s

    put(423, "丙部 (43分)：選修單元問答題（數據庫）")

    # C1 — ERD (4 marks)
    put(
        425,
        "某社區中心活動報名系統：一位會員可報名多個工作坊；一個工作坊可被多位會員報名。"
        "每次報名產生一筆記錄（報名日期、付款狀態）。",
    )
    put(427, stem("繪製實體關係圖（ERD），標示 Member、Workshop、Registration 及主鍵／外鍵。", 4, spaced_marks=True))
    put(429, "\t\t")

    # C2 — CREATE / INSERT (2 marks)
    put(440, "某活動中心使用 BOOKSALE 資料表記錄商品銷售。")
    put(442, subpart("a", "補充以下 SQL，使 SALEID 不可重複。", 1, spaced_marks=True))
    put(444, sql_line("CREATE TABLE BOOKSALE ("))
    put(445, sql_line("    SALEID CHAR(8)\t\t\t\t,", depth=4))
    put(446, sql_line("    TITLE VARCHAR(50),", depth=4))
    put(447, sql_line("    PRICE INTEGER", depth=4))
    put(448, sql_line(")"))
    put(450, subpart("b", "以下記錄將插入 BOOKSALE。", 1, spaced_marks=True))
    put(453, sql_line("INSERT INTO BOOKSALE VALUES (                                )"))
    put(455, stem("寫出此 SQL 語句中未填寫的部分。"))

    # C3 — UNION / UPDATE (3 marks)
    put(457, "Sales2023 與 Sales2024 結構相同，部分記錄如下：")
    put(459, "\t\tSales2023\t\tSales2024")
    put(461, subpart("a", "執行以下 SQL 後會列出多少筆記錄？", 1, spaced_marks=True))
    put(463, sql_line("SELECT *"))
    put(464, sql_line("FROM Sales2023"))
    put(465, sql_line("UNION"))
    put(466, sql_line("SELECT PID, SID, AMT"))
    put(467, sql_line("FROM Sales2024;"))
    put(469, ANSWER_BLANK_LONG)
    put(470, subpart("b", "列出執行以下 SQL 後 Sales2023 內被更新的記錄。", 2, spaced_marks=True))
    put(472, sql_line("UPDATE Sales2023"))
    put(473, sql_line("SET AMT = 0"))
    put(474, sql_line("WHERE AMT > 0 AND"))
    put(475, sql_line("    (EXISTS", depth=4))
    put(476, sql_line("        (SELECT * FROM Sales2024", depth=5))
    put(477, sql_line("         WHERE Sales2023.PID = Sales2024.PID", depth=5))
    put(478, sql_line("           AND Sales2024.AMT = 0);", depth=7))

    # C4 — 3NF schema (3 marks)
    put(482, "某校以單一表格儲存學生比賽成績（學號、姓名、比賽、分數）。以下為示例：")
    put(485, stem("學校欲建立第三範式（3NF）模式，草擬如下："))
    put(487, stem("STUDENT(SID, SNAME)", depth=2))
    put(488, stem("EVENT(EID, ENAME)", depth=2))
    put(489, stem("TASK(\t\t\t\t\t\t\t\t\t\t\t\t  )", depth=2))
    put(490, stem("SCOREBOARD(\t\t\t\t\t\t\t\t\t\t   )", depth=2))
    put(492, stem("寫出未填寫部分，並在主鍵下加底線。", 3, spaced_marks=True))

    # C5 — ROOM / BOOKING (11 marks)
    put(496, "某健身中心資料庫包含 ROOM 及 BOOKING 資料表：")
    put(498, "ROOM")
    put(500, "BOOKING")
    put(502, subpart("a", "寫出 MID 欄的合適數據類型並簡略說明。", 1, spaced_marks=True))
    put(504, ANSWER_BLANK_LONG)
    put(506, subpart("b", "為以下任務寫出 SQL："))
    put(
        508,
        subpart(
            "i",
            "列出預約編號以「B12」開頭的記錄，按日期升序。",
            2,
            depth=2,
            spaced_marks=True,
        ),
    )
    put(510, ANSWER_BLANK_LONG)
    put(513, subpart("ii", "列出 2026-06-18 預約的所有活動室名稱。", 2, depth=2, spaced_marks=True))
    put(515, ANSWER_BLANK_LONG)
    put(
        518,
        subpart(
            "iii",
            "列出曾預約容量少於 30 的活動室之會員編號（不重複）。",
            3,
            depth=2,
            spaced_marks=True,
        ),
    )
    put(520, ANSWER_BLANK_LONG)
    put(526, subpart("c", "簡述以下 SQL 的用途。", 2, spaced_marks=True))
    put(528, sql_line("SELECT RID FROM ROOM"))
    put(529, sql_line("MINUS"))
    put(530, sql_line("SELECT RID FROM BOOKING;"))
    put(532, ANSWER_BLANK_LONG)
    put(536, subpart("d", "簡述非規範化 ROOM 與 BOOKING 的一個方法。", 1, spaced_marks=True))

    # C6 — SQL trace (5 marks) — replaces sorting elective
    put(541, "考慮 Member 與 Registration 資料表，以下 SQL 逐步執行：")
    put(544, stem("設初始結果為空。"))
    put(547, subpart("a", "第一次 JOIN 後結果包含哪些 MemberID？", 1, spaced_marks=True))
    put(550, subpart("ii", "加入 GROUP BY 後結果如何變化？", 1, depth=2, spaced_marks=True))
    put(553, subpart("iii", "加入 HAVING COUNT(*) > 1 後最終結果是什麼？", 1, depth=2, spaced_marks=True))
    put(556, subpart("b", "此查詢找出哪類會員？", 1, spaced_marks=True))
    put(559, subpart("c", "若改為 LEFT JOIN，結果有何不同？簡述。", 1, spaced_marks=True))

    # C7 — transactions (9 marks) — replaces stack elective
    put(566, "銀行轉帳系統使用交易（Transaction）確保資料一致。常用子句如下：")
    put(569, subpart("a", "寫出 BEGIN…COMMIT 與 ROLLBACK 的用途各一項。", 1, spaced_marks=True))
    put(571, sql_line("UPDATE Account SET Balance = Balance - 100 WHERE ID = 'A1';"))
    put(574, subpart("b", "若第二步 UPDATE 失敗，應執行哪個子句？為什麼？", 1, spaced_marks=True))
    put(577, stem("試描述如何確保兩個 UPDATE 同時成功或同時失敗。"))
    put(579, sql_line("BEGIN TRANSACTION"))
    put(580, sql_line("UPDATE Account SET Balance = Balance - 100 WHERE ID = 'A1';"))
    put(581, sql_line("UPDATE Account SET Balance = Balance + 100 WHERE ID = 'B2';"))
    put(582, sql_line("IF @@ERROR <> 0"))
    put(583, sql_line("    ROLLBACK"))
    put(584, sql_line("ELSE"))
    put(585, sql_line("    COMMIT"))
    put(588, subpart("c", "寫出 TRANSFER(A, B, AMOUNT) 的偽代碼，使用 BEGIN/COMMIT/ROLLBACK。", 3, spaced_marks=True))
    put(590, sql_line("TRANSFER(A, B, AMOUNT)"))
    put(592, subpart("d", "說明若無交易控制，轉帳中斷可能造成什麼資料不一致。", 4, spaced_marks=True))

    # C8 — attendance DB (6 marks)
    put(595, "某校以 ATTENDANCE 資料表記錄點名（StudentID, DayNo, Status）。當中：")
    put(597, "Status = 'P' 表示出席，'A' 表示缺席。")
    put(598, "系統要找出連續兩天缺席的學生。")
    put(600, stem("以下為 3 位學生、4 天的示例："))
    put(602, stem("ATTENDANCE", depth=2))
    put(604, stem("老師設計 warn(s) 檢查學生 s 是否連續兩天缺席："))
    put(606, code_line("warn(s)"))
    put(607, code_line("10  t ← 1"))
    put(608, code_line("20  WHILE t < 4 DO"))
    put(609, code_line("30      IF Status[t-1,s] = 'A' AND Status[t,s] = 'A' THEN"))
    put(610, code_line('40          顯示 "學生 s 連續缺席：第 (t-1) 天及第 t 天"'))
    put(611, code_line("50      t ← t + 1"))
    put(613, subpart("a", "根據上表，列出 warn(1) 的輸出。", 2, spaced_marks=True))
    put(615, subpart("b", "若改為 5 天點名，應修改哪一行？寫出改動。", 2, spaced_marks=True))
    put(617, ANSWER_BLANK_LONG)
    put(
        620,
        subpart("c", "若要檢查「連續缺席三天」，應如何修改判斷條件？簡述。", 2, spaced_marks=True),
    )
    put(622, ANSWER_BLANK_LONG)

    return lines
