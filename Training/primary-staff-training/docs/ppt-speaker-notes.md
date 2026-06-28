# STEAM 分享：M5StickS3 — 講者稿（Speaker Notes）

> 配合 `ppt-slides-gemini-prompts.md` 使用。  
> **主題：** 《STEAM 分享：M5StickS3》  
> **分享者：** Warren Chan · 迦密聖道中學（Carmel Holy Word Secondary School）  
> **分享場地：** 元朗朗屏邨惠州學校（YL Long Ping Estate Wai Chow School）  
> **日期時間：** 2026 年 6 月 22 日 14:00 – 15:30  
> **對象：** 惠州學校及聯校 STEAM 老師（教師 PD）

---

## Slide 01 — Title

**講稿：**

各位同事好！歡迎嚟到 **YL Long Ping Estate Wai Chow School（元朗朗屏邨惠州學校）** 今日嘅 **《STEAM 分享：M5StickS3》**（2026 年 6 月 22 日，14:00–15:30）。  
我係 **Warren Chan**，來自 **Carmel Holy Word Secondary School**，會帶大家試一部好細、但功能好勁嘅 M5Stack 裝置，入面仲預載咗 **小智** 英文導師。  
今日唔係純 demo，而係 **三個 task**：先 **體驗 AI**，再 **裝 UIFlow 自己整 game**，最後 **Vibe Coding** — 睇下而家軟件工程界點寫 program。

---

## Slide 02 — About Me

**講稿：**

先介紹自己 — 我係 **Warren Chan**，喺 **Carmel Holy Word Secondary School（迦密聖道中學）** 任教。

簡歷（配合 slide）：

- **Software Engineer — 10+ years**  
- **Secondary School teaching — 9+ years**  
- 做過 **NGO、startups**  
- **Mentor 過一啲好出名嘅大學生** — 例如 **MIT、Stanford、Chicago** 等  

我對 **小學教學** 已經 **唔係好識**；好多時透過 **我個仔（小五）** 去認識。今日如有講得唔啱，**請多多包涵**。

**可選補充：**

- 我分享嘅唔係「官方 STEAM 課程」，而係 **工程師視角** 點將 hardware + AI 帶入課室。
- 我個仔就係我嘅 **user testing** — 佢話闷我先知要改。

---

## Slide 03 — Three Tasks

**講稿：**

今日 **三個 task**（slide 上三個字）：

| # | Task | 做乜 |
|---|------|------|
| **1** | **Experience** | 試小智 — 感受有幾厲害 |
| **2** | **Setup** | 裝 UIFlow 2、配對、Run Once |
| **3** | **Vibe Coding M5StickS3** | 用 Gemini 寫 game |

如果有時間先會提 **DeepSeek**；深度 **Agentic AI** 課程就 **下次** 再講。

---

## Slide 04 — Three Buttons (blank slide — you add in PPT)

**講稿：**

（呢張 slide 留空 — 你會喺 PPT **自己加** StickS3 相同三粒掣 label）

口頭仍然要講清三粒掣：

| 掣 | 用途 |
|----|------|
| **Power（左）** | 短按 → 小智 |
| **BtnA** | 遊戲 / UIFlow |
| **BtnB** | M5Launcher 見字 **立刻按** |

---

## Slide 05 — StickS3 Features

**講稿：**

除咗三粒掣，部機仲有：

- **1.14" 彩色螢幕** — 顯示字、UI、遊戲  
- **ESP32-S3 晶片** — WiFi、Bluetooth  
- **咪高峰 + 喇叭** — 小智語音對話  
- **六軸 IMU** — 感應傾斜、動作（整 motion game 用得著）  
- **紅外線發射** — 可玩遙控相關 project  
- **RTC 時鐘** — 顯示時間、定時  
- **內置電池 + USB-C 充電** — 拎得走  

所以話佢係「小玩具」其實唔公平 — **STEAM 五科都踩到**：Science（sensor）、Technology（WiFi/AI）、Engineering（按掣/電路）、Arts（UI）、Math（遊戲計分、反應毫秒）。

---

## Slide 06 — Grouping (20 Units)

**講稿：**

事不宜遲 — 而家 **派機**。

坦白講：M5Stack **而家缺貨**，我 **暫時只買到 20 部**。  
請各位老師 **三人一組**，一部機輪流試，旁邊同事幫手記低步驟同感受。

（派機時確認 WiFi 已連、小智可開）

---

## Slide 07 — Task 1: Experience Xiaozhi

**講稿：**

**第一個 task：體驗一下佢嘅強勁。**

操作好簡單：

1. **按一下左面 Power 掣**  
2. **等一陣**（開機 / 載入 app）  
3. 你就可以 **同佢傾計**

佢係一個叫 **小智** 嘅 **英語導師** — 隨住佢可以 **教你英文**。  
你而家可以 **扮一個小學生** 同佢傾，感受若果派俾 P4–P6 會係咩體驗。

---

## Slide 08 — Task 1: Things to Try

**講稿：**

唔使淨係問 spelling — 試下佢嘅 **多功能**：

| 你可以講（英文） | 效果 |
|------------------|------|
| Teach me English / 問生字 | 英文導師模式 |
| **Turn on dark mode** | 轉 dark mode |
| **Play a song** | 播歌 |
| **What's the weather?** | 問天氣 |
| Tell me a joke | 輕鬆對話 |

**Task 1 計時 5 分鐘** — 呢段我唔解釋技術，請大家 **尽情試**。

---

## Slide 09 — Recording Notice

**講稿：**

**提提大家：** 為提高教學質素，你哋同小智嘅 **對話可能會被錄音**（若學校政策 / 平台設定有開啟）。  
如有顾虑，可以用 **較短嘅試探性對話**。  
呢個亦係帶 AI 入課室時 **一定要同家長、IT 交代** 嘅位。

---

## Slide 10 — Why So Powerful? (architecture — no duplicate slide 11)

**講稿：**

（5 分鐘後 — **只講呢一張**，唔再重複 architecture）

部 StickS3 有 **sensor**，但真正嘅腦喺 **网上**：

- **小智平台** backend  
- 背後 **LLM**  
- 可加 **Knowledge Base**（似 NotebookLM）  
- 可駁 **MCP** — AI 用外部工具  

```
你講嘢 → 咪高峰 → WiFi → 小智平台 + LLM → 喇叭
```

---

## Slide 11 — Live Demo: xiaozhi.me

**講稿：**

（切 browser — **live demo**）

而家帶大家睇 **xiaozhi.me** 平台 — 裝置點 bind、對話 log、設定等。  
Slide 留空俾你 **screenshot 或 live 展示**。

---

## Slide 12 — Task 2: Install UIFlow 2 (blank — add screenshots in PPT)

**講稿：**

**第二個 task — Setup。** 同小智講拜拜，裝 **UIFlow 2**。

（PPT 留空 — 你會加 **M5Launcher** screenshot，例如綠字 **M5Launcher** 嗰張）

步驟：

1. **按一下** 開啟 **M5Launcher**  
2. **一見「M5Launcher」呢個字樣，即刻按 BtnB**  
3. 入 **OTA**（Over-The-Air 更新 / 安裝）  
4. **揀 UIFlow 2**（如 PPT 圖）  
5. **等佢安裝** — 全班會有一陣 idle，可以講下面呢段

---

## Slide 13 — Infinite Possibilities (Side Talk)

**講稿：**

（等 OTA 時口頭講 — 唔使長）

而家 AI 變成 **會行會走嘅機械人**，真係 **好多地方都搵到**。  
StickS3 細到你可以 **想像**：

- **配帶喺手** → 一隻 **AI 手錶**  
- **放入筆袋** → **筆袋機械人**  
- 加 case、3D print shell → **角色 IP、班級 mascot**

玩法 **千變萬化** — 今日只係 **入門 taste**，希望大家帶走 **「細 device + AI」** 嘅 imagination。

---

## Slide 14 — Cloud & Access Code (blank — add screenshots in PPT)

**講稿：**

（PPT 留空 — 你會加 **Cloud 編號** 同 **uiflow2.m5stack.com** screenshot）

好，差唔多 **安裝好** 喇。

大家 **按一按螢幕上嘅 Cloud 圖示**（或 UIFlow 入面嘅 cloud / connect）— 會見到 **一組編號（Access Code）**。

而家 **一齊去** 呢個網頁：

**https://uiflow2.m5stack.com** （UIFlow 2.0）

1. 登入 M5Stack 帳號  
2. **Connect Device** → 輸入編號 → 配對  
3. 試 **改一改畫面**（加 label、改背景色）  
4. 按 **Run Once** — 你嘅圖案就 **即刻出喺部機**

---

## Slide 15 — Familiar Block Coding?

**講稿：**

如果你係 **STEAM 老師**，對呢類 **網頁 block coding** 應該 **一啲都唔陌生** — Scratch、micro:bit、好多平台都係 **拖積木**。

但我要講句 **心裡話** — 我相信在座 **好多都唔想面對編程**。  
唔止小學老師，就连 **中學 ICT** 同事，都有同感。

---

## Slide 16 — Software Engineers Don't Code Anymore

**講稿：**

我作為 **軟件工程師**，可以好老實咁講：

> **我哋業界，已經無乜人逐行「純人手編程」。**  
> **全部交俾 AI** — 顶多多 **睇一睇 AI 寫咗啲乜**，**唔好整爛我哋個 code base**。

所以 **Task 3** 唔係要大家變 programmer，而係體驗 **2020 年代嘅寫 code 方式** — **Vibe Coding**。

---

## Slide 17–18 — Chatbot → Vibe Coding → Agentic AI

**講稿（核心 — 同 primary 教案共用概念，但語氣對老師）：**

| 層次 | 意思 | 今日對應 |
|------|------|----------|
| **Chatbot** | 問答、傾計 | 小智（Gemini 本身都係 chat） |
| **Vibe Coding** | 用自然語言 **描述 program**，AI **出 code** | UIFlow 2 + Gemini 整反應 game |
| **Agentic AI** | 俾 **目標**，AI **自己 plan 多步、用工具** | Manus 呢類；我嘅 **深度課程** |

**Vibe Coding 正正係由 Chatbot AI（Gemini）走去 Agentic AI 嘅「中轉站」** —  
學生同 **我哋老師** 都應該 **有啲體驗**，先至 **教導到 AI 做啲乜**、**唔好亂做啲乜**。

---

## Slide 19 — Task 3: Vibe Coding with Gemini

**講稿：**

**第三個 task：Vibe Coding。**

我聽 **琦姐** 講，大家 **學過 Gemini** — 我唔多介紹 Gemini 本身。  
大家可以用佢 **試下寫 code** — 喺 **UIFlow 2 嘅 AI panel** 或者直接 **Google Classroom 我發咗嘅 sample prompt** — **copy and paste** 就得。

---

## Slide 20 — The M5 API Trick

**講稿：**

**呢度有個小小技巧** — 好多同事第一次 generate 會 **fail**：

> **問 AI 之前，你要俾佢知 M5 嘅 API 點運作** — 即係 **StickS3 有咩 library、咩掣、咩 Widgets 用得**。

Gemini **睇完 context** 就 **識寫**；唔俾 context，佢會寫 **错 platform** 嘅 code。

Sample prompt 我已放 **Google Classroom** — 入面已包括 **UIFlow 2 / StickS3 / BtnA BtnB** 等提示。  
大家可以 **跟住試**，整一隻 **反應遊戲（reaction game）**。

---

## Slide 21 — Two Buttons vs Voice

**講稿：**

**留意：** StickS3 **實際玩 game 主要得兩粒掣（BtnA、BtnB）** — 玩法 **好局限**  if 淨係 thinking 「街機掣」。

但如果 **計埋語音輸入（咪高峰 + 小智 / 語音 API）**，**玩嘅嘢就好唔同** —  
例如 **語音答題 game**、**英文指令控制**。  
呢度我 **唔介紹太多**，交俾大家 **同學生慢慢試** — 你哋先 **感受 Vibe Coding 出到 game** 已經好够。

---

## Slide 22 — DeepSeek: Next Time

**講稿：**

今日 **差不多** 喇。

如果有時間，本來想俾大家睇 **点駁 DeepSeek API** — 自己 backend、自己 key，**似小智但慢好多**。  
**下次先啦** — 今日 focus **Vibe Coding** 已够。

（若有多 5 分鐘：口头提 **HTTP POST + requests2**，唔使 live demo）

---

## Slide 23 — Agentic AI (advanced workshops)

**講稿：**

我 **唔係** 專門教 **Manus** — 我嘅 **強項** 係教 **Agentic AI** 同 **Professional Vibe Coding**。

如果大家 **有興趣**，可以 **搵我** — 但建議：

- **小班教學**  
- **有興趣先好學** — 無興趣好難入門  
- 有興趣學咗，會 **好解放** — 我喺自己學校教過，覺得 **好正**

（唔需要提 Manus 做賣點）

---

## Slide 24 — Summary

**講稿：**

今日總結三句：

1. **小智** — 感受 **成品 AI chatbot** 幾強（英文 + 語音 + 平台）  
2. **UIFlow 2** — 學生 **自己整 stick game** 嘅入口  
3. **Vibe Coding** — **唔使怕 programming**；**描述 → AI 寫 code → Run Once**

由 **Chatbot** 到 **Vibe Coding** 到 **Agentic AI** — 你哋而家行緊 **中間嗰步**，最重要。

---

## Slide 25 — Q&A / Thank You

**講稿：**

多謝 **惠州學校** 今日嘅安排，多謝各位同事！

有冇問題？例如：采购、WiFi、小智账号、Google Classroom prompt、进阶课程——

記得 **Run Once** 試完，有满意 project 可以 **Run Always** 留喺機度；要返小智就 **M5Launcher 切 app**。

---

## 附：MCP / NotebookLM 若被追问

**NotebookLM：** Google 工具，可 **upload 文件** 做 RAG，AI 答嘢 **基于你嘅资料** 而唔係乱估。

**MCP：** Anthropic 等推嘅 **开放协议**，令 AI assistant **统一咁接 tools**（calendar、database、search）。小智 / 其他平台若支持，就可以 **扩展能力** 而唔使重写 integration。

## 附：三粒掣速查（派机时可投影）

| 掣 | 动作 |
|----|------|
| Power（左） | 短按 → 等小智 |
| BtnB | M5Launcher 见字 **立刻按** |
| BtnA | 游戏 / UIFlow 主操作 |
| Cloud（屏） | UIFlow 配对编号 |
