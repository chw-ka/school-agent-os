# STEAM 分享：M5StickS3 — 參與者跟做筆記

**日期：** 2026 年 6 月 22 日（一）14:00 – 15:30  
**地點：** 元朗朗屏邨惠州學校  
**講者：** Warren Chan · 迦密聖道中學  
**形式：** 三人一組 · 每組 1 部 M5StickS3 + 自備 laptop（連 WiFi）

> 截圖位置已預留 — 你可之後將 screen capture 圖放入對應 `[📷 截圖]` 位置。

---

## 今日三個 Task 速覽

| # | Task | 你做乜 | 預計時間 |
|---|------|--------|----------|
| **1** | **Experience** | 試小智英文導師 | 5′ |
| **2** | **Setup** | 裝 UIFlow 2、配對、Run Once | 30′ |
| **3** | **Vibe Coding** | 用 Gemini 整反應遊戲 | 20′ |

---

## 開始前 Checklist

- [ ] 已連上學校 WiFi
- [ ] Laptop 已開瀏覽器，可上 [uiflow2.m5stack.com](https://uiflow2.m5stack.com/)
- [ ] 已加入 Google Classroom 課程（見課堂 QR / 連結）
- [ ] 同組 3 位同事已分好：操作員 / 記錄員 / 支援

---

## StickS3 必記四個操作

| 操作 | 用途 |
|------|------|
| **Power 掣（左側）** — 短按 | 開機 / 喚醒；Task 1 入小智 |
| **BtnA** | UIFlow 遊戲主操作掣 |
| **BtnB** | M5Launcher 見「M5Launcher」字樣 → **立刻按** |
| **Cloud 圖示（螢幕上）** | UIFlow 配對編號 |

`[📷 截圖：StickS3 三粒掣 + Cloud 圖示標示]`

---

## Task 1：體驗小智（5 分鐘）

### 步驟

1. **按一下左側 Power 掣**
2. 等載入（約 10–30 秒）
3. 同 **小智** 用英文傾計 — 可扮小學生試

`[📷 截圖：小智主畫面 / 對話中]`

### 建議試玩指令

| 你可以講（英文） | 觀察重點 |
|------------------|----------|
| Turn on dark mode | 非教學指令都做到 |
| Play a song | 娛樂 / 多模態 |
| What's the weather? | 聯網能力 |
| How do you spell ___? | 英文課堂場景 |

### 我的試玩記錄

| 指令 | 反應如何？ | 若帶入 P4–P6 課堂？ |
|------|------------|---------------------|
| | | |
| | | |
| | | |

> **私隱提示：** 對話可能被錄音（視平台 / 校政設定）。帶 AI 入課室要向家長、IT 交代。

---

## 概念筆記：點解小智咁厲害？

```
你講嘢 → 咪高峰 → WiFi → 小智平台 + LLM → （知識庫 / MCP）→ 喇叭
```

| 概念 | 一句解釋 | 我的理解 / 問題 |
|------|----------|-----------------|
| **LLM** | 大語言模型 — 「識傾計」嘅腦 | |
| **小智平台** | Backend — 裝置、語音、對話流程 | |
| **知識庫** | 似 NotebookLM — 餵校內資料 | |
| **MCP** | AI 统一接駁工具 / 數據嘅「插口」 | |

`[📷 截圖：xiaozhi.me 平台畫面]`

---

## Task 2：安裝 UIFlow 2

> ⚠️ 裝 UIFlow 會改 active app；小智仍留喺 Launcher，之後可切返。

### 步驟（全班同步）

| 步驟 | 你做乜 | ✓ |
|------|--------|---|
| 1 | 開 **M5Launcher** | ☐ |
| 2 | 見 **「M5Launcher」** 字樣 → **即刻按 BtnB** | ☐ |
| 3 | 入 **OTA** → 揀 **UIFlow 2（StickS3）** | ☐ |
| 4 | 等安裝完成 → Reboot | ☐ |

`[📷 截圖：M5Launcher 綠字畫面]`  
`[📷 截圖：OTA 揀 UIFlow 2]`

### 等候時 — STEAM 想像

StickS3 細到可以變成：**AI 手錶**、**筆袋機械人**、**班級 mascot**……

| 我哋組嘅 idea | 適合邊個年級？ |
|---------------|----------------|
| | |
| | |

---

## Task 2（續）：Cloud 配對 + Run Once

| 步驟 | 你做乜 | ✓ |
|------|--------|---|
| 1 | 按 **Cloud 圖示** → 記 **Access Code** | ☐ |
| 2 | 開 [uiflow2.m5stack.com](https://uiflow2.m5stack.com/) | ☐ |
| 3 | **Connect Device** → 輸入編號 | ☐ |
| 4 | 改 label / 背景色 | ☐ |
| 5 | 按 **Run Once** — 畫面即刻上機 | ☐ |

`[📷 截圖：裝置 Access Code]`  
`[📷 截圖：uiflow2 網頁配對成功]`  
`[📷 截圖：Run Once 後機身畫面]`

### 我改咗咩？

- Label 文字：________________
- 背景色：________________
- Run Once 成功？ ☐ 是 ☐ 否

---

## 概念：Chatbot → Vibe Coding → Agentic AI

| 層次 | 意思 | 今日對應 |
|------|------|----------|
| **Chatbot** | 問答、傾計 | 小智 |
| **Vibe Coding** | 描述 → AI 出 code；人 review | UIFlow 2 + Gemini |
| **Agentic AI** | 俾目標 → AI 自己 plan 多步 | Manus；進階課程 |

> 工程師視角：**业界已经唔人手逐行写 code** — 交俾 AI，人 **review 唔好整爛 codebase**。

---

## Task 3：Gemini Vibe Coding — 反應遊戲

### 前置

- Sample prompt 已喺 **Google Classroom** — Copy & Paste 就得
- 或喺 UIFlow 2 內建 AI panel 用 Gemini

### ⚠️ M5 API 技巧（好多同事第一次會 fail）

Generate 前要先俾 AI **StickS3 / UIFlow 2 context** — 否則會写错 platform。

`[📷 截圖：Google Classroom 入面嘅 sample prompt]`

### Sample Prompt（可抄）

```
You are coding for M5StickS3 on UIFlow 2 (MicroPython).
Available: BtnA, BtnB, Widgets.Label, Widgets.fillScreen, time, random.
Write a simple reaction game: show "Wait...", after random 1-5 seconds show "GO!" on green screen,
when BtnA pressed after GO show reaction time in milliseconds, if pressed before GO show "Too early!".
Keep it simple for primary students.
```

### 步驟

| 步驟 | 你做乜 | ✓ |
|------|--------|---|
| 1 | 從 Classroom 複製 prompt | ☐ |
| 2 | 貼入 Gemini / UIFlow AI panel | ☐ |
| 3 | Generate code | ☐ |
| 4 | Copy code → UIFlow | ☐ |
| 5 | **Run Once** 試玩 | ☐ |

`[📷 截圖：Gemini 生成 code]`  
`[📷 截圖：反應遊戲 GO! 畫面]`  
`[📷 截圖：顯示 reaction time ms]`

### 試玩記錄

| 項目 | 結果 |
|------|------|
| 第一次 Generate 成功？ | ☐ 是 ☐ 否 |
| 反應時間（ms） | |
| 太早按有冇 show "Too early!"？ | ☐ 有 ☐ 無 |

### 設計思考

- **纯两粒掣** — 玩法好局限
- **加語音** — 玩法完全不同（例如語音答題 game）
- 我哋組想改進：________________

---

## 今日總結（填完帶走）

1. **小智** — 我感受到成品 AI chatbot 嘅強項係：________________
2. **UIFlow 2** — 學生可以自己整 stick game，我會喺 ________________ 科目試
3. **Vibe Coding** — 唔使怕 programming；流程係：**描述 → AI 寫 code → Run Once**

---

## 疑難排解 Quick Reference

| 問題 | 可能原因 | 試下 |
|------|----------|------|
| 小智開唔到 | WiFi 未連 | 檢查 Launcher WiFi 設定 |
| OTA 揀唔到 UIFlow | 未按 BtnB | 見字立刻按 BtnB |
| 配對失敗 | Code 過期 | 重新按 Cloud 攞新 code |
| Gemini code 跑唔到 | 缺 M5 context | 用 Classroom 完整 prompt |
| Run Once 無反應 | 未配對 / 未 save | 重新 Connect + Run Once |

---

## 有用連結

| 資源 | URL |
|------|-----|
| UIFlow 2 Web IDE | https://uiflow2.m5stack.com/ |
| 小智平台 | https://xiaozhi.me/ |
| StickS3 小智教學 | https://docs.m5stack.com/zh_CN/guide/realtime/xiaozhi/sticks3 |
| StickS3 UIFlow 2 | https://docs.m5stack.com/en/uiflow2/sticks3/program |

---

## 課後 Feedback

請掃描投影最尾 slide 嘅 **QR Code** 填寫 feedback form，或喺 Google Classroom 入面搵連結。

多謝參與！有進階 **Agentic AI / Vibe Coding** 課程興趣，可留低 contact 或喺 form 表示。
