# Google Classroom — M5StickS3 Workshop 運用方案

**課程名稱（建議）：** STEAM 分享：M5StickS3（2026-06-22 惠州學校）  
**對象：** 惠州學校及聯校 STEAM / ICT / 英文老師  
**用途：** 課前派發資源、課中 copy prompt、課後 feedback 與延伸閱讀

---

## 點解用 Google Classroom？

| 痛點 | Classroom 點幫到手 |
|------|-------------------|
| Task 3 要 copy 長 prompt | 貼喺 **Material**，老師一鍵複製 |
| 三人一組輪流操作 | **Stream** 發提醒 / 時間線 |
| 課後想睇 feedback | 連結 **Google Form** + QR |
| 延伸資源分散 | 所有 link 集中一處 |
| 聯校老師唔同 domain | 用 **Class Code** join（唔使 same domain） |

---

## 建議課程結構

```
📚 STEAM 分享：M5StickS3
├── 📌 Stream（置頂公告）
│   ├── 歡迎 + 今日三 Task 概覽
│   ├── WiFi / 分組提醒
│   └── 課後 Feedback QR 連結
│
├── 📁 Classwork（按順序）
│   ├── [Material] 參與者跟做筆記 (participant-handout.md → PDF)
│   ├── [Material] Task 3 Sample Prompt（Gemini Vibe Coding）
│   ├── [Material] 有用連結匯總
│   ├── [Material] 簡報 PDF（optional）
│   └── [Question] 課後簡短反思（optional，可取代部分 Form 問題）
│
└── 📋 People
    └── 老師以 Class Code 加入（Co-teacher：琦姐 / 惠州 IT）
```

---

## 課前（分享會前 1–3 天）

1. **建立 Course** — 設定 → 加入 **Class Code**（例如 `abc123de`）
2. **Stream 置頂帖：**
   - 日期時間、地點、帶 laptop + WiFi
   - 三人一組，現場派機
3. **上載 Material：**
   - `docs/participant-handout.md`（轉 PDF 後上載）
   - Task 3 prompt（見下方）
4. **Email / WhatsApp 群** 發 Class Code 俾聯校老師

### Task 3 Prompt Material 內容

```
You are coding for M5StickS3 on UIFlow 2 (MicroPython).
Available: BtnA, BtnB, Widgets.Label, Widgets.fillScreen, time, random.
Write a simple reaction game: show "Wait...", after random 1-5 seconds show "GO!" on green screen,
when BtnA pressed after GO show reaction time in milliseconds, if pressed before GO show "Too early!".
Keep it simple for primary students.
```

---

## 課中（14:00–15:30）

| 時間 | Classroom 用法 |
|------|----------------|
| 開場 | 投影 Class Code — 未 join 嘅同事即場加入 |
| Task 1 前 | Stream 發「Task 1 開始 — 按 Power 掣」 |
| Task 2 前 | 提醒開 uiflow2.m5stack.com（Material 有 link） |
| Task 3 | 指示去 **Classwork → Sample Prompt** copy |
| 收尾 | Stream 發 Feedback form 連結 + 投影 QR slide |

> **Tip：** 課中唔使逐樣 assign 做 assignment（免 marking）；全部用 **Material** 就得，老師自己 copy。

---

## 課後

1. Stream 發 **Feedback Google Form** 連結（見 `docs/feedback-form-meta.json`）
2. 可加 **Material：**
   - StickS3 採購 link
   - xiaozhi.me / UIFlow 文檔
   - 進階 Agentic AI 課程 interest form（如有）
3. **Archive course** 或保留做資源庫 — 視學校政策

---

## 建立 Course Checklist（下次 session 幫你做）

- [ ] OAuth / Classroom API scope（需額外授權 `classroom.courses`）
- [ ] 建立 course + 設定 section / room
- [ ] 上載 participant handout PDF
- [ ] 建立 3 個 Material posts（筆記、prompt、連結）
- [ ] Stream 置頂歡迎帖 + Feedback link
- [ ] 產生 Class Code 俾你派畀老師
- [ ] （Optional）加琦姐做 Co-teacher

---

## API 限制說明

目前 `config/google-forms-oauth-token.json` 只得 **Forms + Drive** scope。  
**Google Classroom** 需要額外 OAuth scope：

- `https://www.googleapis.com/auth/classroom.courses`
- `https://www.googleapis.com/auth/classroom.coursework.students`

下次你話「幫我開 Classroom course」，我會：

1. 跑 OAuth 授權（browser 開一次）
2. 用 Classroom API 自動建立 course + materials
3. 輸出 **Class Code** 同 join link

---

## 同 Feedback Form 配合

| 渠道 | 用途 |
|------|------|
| **PPT 最尾 QR slide** | 現場掃碼（最快） |
| **Classroom Stream link** | 課後補填 |
| **participant-handout.md 最尾** | 紙本 / PDF 版指引 |

Form 問題涵蓋：學校、滿意度、完成 Task、實用性、進階課程興趣等 — 見 `scripts/create_feedback_form.py`。

---

## 小學課堂延伸（PD 之後）

若老師要帶學生做，可另開 **Student Classroom**（唔同 course）：

- 簡化 prompt 做 **Assignment**
- 學生交 screenshot（Run Once 成功畫面）
- 老師用 **Rubric**：有 GO! 畫面 / 有 reaction time / 合作分工

本次 PD course 保持 **Teacher-only**，避免同學生混用。
