# 25-26 S5 ICT Exam02 — 圖片生成 Prompt（Gemini / Banana Pro）

試卷內表格已由 formatter 填入 DOCX。以下題目如需參考圖，可人手插入。

---

## C1 — 戲院預訂 ERD（4 分）

**用途：** 丙部第 1 題空白處，供學生參考業務規則（可選；題目要求學生自行繪製 ERD）。

**Prompt（繁中 + 英文混合，方便模型理解）：**

> Clean black-and-white HKDSE exam style diagram, no decorative colors. Entity-relationship diagram for a cinema booking system. Four entities as rectangles with English labels: **Member**, **Booking**, **Screening**, **Cinema**. Relationships with cardinality: Member 1—M Booking (label「建立」); Booking 1—1 Screening (label「預留」); Cinema 1—M Screening (label「舉行」). Use crow's foot notation. White background, thin lines, textbook print quality, A4 portrait, no watermark.

**插入位置：** 丙部 C1 題「繪製 ERD」下方空白區（paragraph ~429）或另頁附圖。

---

## B4 — 線性搜尋追蹤表（2 分）

**用途：** 輔助 (a) 追蹤表；DOCX 已含空白 trace 表格（tables 6–9），此 prompt 可生成**參考答案**給教師。

**Prompt：**

> HKDSE ICT exam worksheet table, monochrome. Title「線性搜尋追蹤 — A = [4, 9, 2, 9, 7, 1], key = 9」. Columns: 迴圈次數, i, A[i], found. Rows for iterations until found=TRUE. Empty cells for student version; or filled teacher version showing i=1..4 progression. Plain grid, no colors.

---

## C6 — Member / Enrol JOIN 追蹤（選用）

**用途：** 教師改卷參考；DOCX tables 20–21 已含樣本數據。

**Prompt：**

> Two small database tables side by side, exam style. **Member(MemberID, MName)**: M01 Amy, M02 Ben, M03 Cal. **Enrol(MemberID, CourseID)**: M01-C01, M01-C02, M02-C01, M03-C03. Black text on white, simple borders, no logo.

---

## C8 — 堆疊操作（選用）

**用途：** DOCX table 31 已含完整操作序列；如需放大圖：

**Prompt：**

> Stack diagram tutorial, LIFO. Horizontal stack boxes left (bottom) to right (top). Show steps: PUSH 3 → stack [3]; PUSH 7 → [3,7]; POP → [3]; PUSH 2 → [3,2]; POP → [3]; POP → empty. Minimal HK school ICT textbook style, black and white.

---

## 不建議生成圖片的題目

| 題號 | 原因 |
|------|------|
| B1, B2, B6 | 試算表／有效性／ORDER 表 — 已由 DOCX table 3, 4, 11 填入 |
| B3 | 純計算題，無需圖 |
| B5 | 文字比較題 |
| C2–C5, C7 | SQL／schema — 文字 + DOCX 表格足夠 |
