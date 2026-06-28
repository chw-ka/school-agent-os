# STEAM 體驗課：M5StickS3 — 教案（小五學生版）

**主題：** 《AI 可以住喺小機器？》  
**對象：** 小學五年級學生（約 10–11 歲）  
**人數：** 視班級；**2 人一組**（每組 1 部 M5StickS3）  
**時間：** 45–60 分鐘  
**場地：** 電腦室 / 有 WiFi 的課室  
**硬件：** M5StickS3（預載 M5Launcher + 小智 + 學校 WiFi）

> **改編來源：** `../primary-staff-training/docs/lesson-plan-sticks3-steam-tasting.md`（教師 PD 版）

---

## 課堂目標

學生完成後能夠：

1. 親手操作 M5StickS3，用小智對話（英文）
2. 用「**咪 → 腦 → 嘴**」描述 AI 硬件的工作流程
3. 通過 UIFlow 2 用 block coding 改機器顯示的畫面
4. 跟隨 prompt 卡，讓 Gemini 幫忙生成一個小遊戲

---

## 概念框架（三層 AI，學生版）

```
你說話 → 咪高峰（耳）→ WiFi → AI 大腦 → 喇叭（嘴）
```

| 部分 | 比喻 | 今日體驗 |
|------|------|---------|
| **耳**（咪）| 聽你說話 | StickS3 錄音 |
| **腦**（AI）| 想答案 | 小智 / Gemini |
| **嘴**（喇叭）| 講出答案 | 小智播放 |

---

## 硬件操作——三粒掣（上課前必講）

| 掣 | 在哪 | 用途 |
|----|------|------|
| **Power** | 左側 | 短按開機；Task 1 開小智 |
| **BtnA** | 正面右上 | UIFlow 遊戲主掣 |
| **BtnB** | 正面右下 | OTA 確認（見到字即刻按） |

---

## 流程總覽

| 段落 | 內容 | 時間 |
|------|------|------|
| 開場 | 主題、三粒掣、分組 | 5′ |
| **Task 1** | 小智對話 | 8′ |
| 概念講解 | 咪 → 腦 → 嘴；三層 AI | 7′ |
| **Task 2** | OTA 裝 UIFlow；配對；改畫面 | 15′ |
| **Task 3** | Prompt 卡 → Gemini → 反應遊戲 | 15′ |
| 收尾 | 分享 + 問答 | 5′ |

---

## Task 1：玩小智（8 分鐘）

### 操作

1. 按一下 **Power 掣**
2. 等小智載入
3. 用**英文**對話（老師可示範）

### 建議試玩

| 指令 | 學習點 |
|------|--------|
| `How do you spell "challenge"?` | AI 識英文 |
| `What's the weather today?` | 聯網能力 |
| `Play a song` | 多模態 |
| `Turn on dark mode` | 可自訂 |

### 教師提示

- 老師先說明：「同小智的對話，平台有機會記錄，不要說個人私隱。」
- 學生傾向一直問英文詞彙——鼓勵試不同類型指令

---

## 概念講解（7 分鐘）

### 板書 / 投影

```
你講嘢 → [咪高峰] → WiFi → [AI 大腦] → [喇叭]
            耳                  腦          嘴
```

### 問學生

- 「AI 大腦喺邊？」（在雲端伺服器，不在機器本身）
- 「如果冇 WiFi？」（小智不能用 — 引導思考離線 vs 在線 AI）
- 「呢部機仲有什麼感應器？」（IMU 加速度、溫度、紅外線）

---

## Task 2：UIFlow 積木編程（15 分鐘）

> UIFlow 2 = block coding，同學已識用 Scratch / App Inventor — 概念一樣

### 步驟

1. 機器開機 → 見 **「M5Launcher」** 字樣 → **立刻按 BtnB**
2. 進 **OTA** → 揀 **UIFlow 2（StickS3）** → 等安裝 → Reboot
3. 按 **Cloud 圖示** → 記下 **Access Code**（4 位數字）
4. 開電腦瀏覽器：[uiflow2.m5stack.com](https://uiflow2.m5stack.com/) → Connect Device → 輸入 code
5. 拖積木，改機器屏幕：
   - 改**背景顏色**（`fillScreen`）
   - 加**文字 label**（`Widgets.Label`）
6. 按 **Run Once** → 畫面即時上機

### 等待安裝時（老師口頭）

「這部機除了做 AI 對話，還可以做什麼？手錶？筆袋機械人？步數計？大家想一想。」

---

## Task 3：Gemini Vibe Coding（15 分鐘）

### 概念橋接

「剛才我們自己用積木寫程式。現在試試叫 AI 幫你寫——你只需要**描述**想做什麼。」

### 使用 Prompt 卡

老師發 **prompt 卡**（見 `docs/prompt-card.md`）或投影以下文字：

```
You are coding for M5StickS3 on UIFlow 2 (MicroPython).
Available: BtnA, BtnB, Widgets.Label, Widgets.fillScreen, time, random.
Write a simple reaction game:
- Show "Wait..." on screen
- After random 1 to 5 seconds, show "GO!" on green screen
- When BtnA is pressed after GO, show how many milliseconds it took
- If BtnA is pressed before GO, show "Too early!"
Keep it simple.
```

### 步驟

1. 打開 **Gemini**（[gemini.google.com](https://gemini.google.com/)）
2. **Copy & Paste** prompt 卡
3. 把 Gemini 生成的 code **貼入 UIFlow 2**（Custom Code block）
4. **Run Once** → 試玩！

### 教師提示

- 若 Gemini 生成的 code 出錯，引導學生修改 prompt（「試試問 AI 點解有 error」）
- 有餘時間：讓學生嘗試修改 prompt，加入自己的想法（例如：換顏色、換文字）

---

## 收尾（5 分鐘）

### 討論問題

- 「今日哪個 Task 最好玩？為什麼？」
- 「AI 寫的 code 同你自己寫的有什麼分別？」
- 「如果你有一部 StickS3，你想它做什麼？」

### 教師結語

「今日大家做了 **三件事**：和 AI 對話、用積木控制機器、叫 AI 幫你寫程式。這三件事，代表了 AI 時代三個重要能力。」

---

## 課前 Checklist（教師）

- [ ] 所有機器已連學校 WiFi + 小智可用
- [ ] 已告知學生對話私隱政策
- [ ] 印好 / 投影 prompt 卡
- [ ] uiflow2.m5stack.com 可從課室網絡訪問
- [ ] 備用：預先生成好的反應遊戲 code（Gemini 出錯時用）

---

## 時間壓縮（30 分鐘版本）

| 削減 | 做法 |
|------|------|
| Task 2 | 課前預裝 UIFlow，現場只配對 + Run Once |
| 概念講解 | 壓縮至 3 分鐘，只講「咪→腦→嘴」 |
| Task 3 | 全班跟講者 copy 同一 prompt，不讓學生自由修改 |

---

## 延伸學習

| 方向 | 資源 |
|------|------|
| 更多 UIFlow block | [UIFlow 2 文件](https://uiflow2.m5stack.com/docs) |
| M5StickS3 感應器 | 同目錄 `../primary-staff-training/docs/M5StickS3-Device-Manual.pdf` |
| 小智平台 | [M5Stack 小智教學](https://docs.m5stack.com/zh_CN/guide/realtime/xiaozhi/sticks3) |
