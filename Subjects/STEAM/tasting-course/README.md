# STEAM 嘗鮮課 — AI 小裝置 × M5StickS3
**對象：** 小五學生（約 10–11 歲）  
**時間：** 60 分鐘 × 2 節（同一課，兩班輪流）  
**裝置：** M5StickS3（已預先複製主機設定——UIFlow 2.0 韌體 + 學校 WiFi）  
**IDE：** UIFlow 2.0 — `uiflow2.m5stack.com`（瀏覽器，毋須安裝）  
**Vibe Coding：** Gemini（語音輸入 → MicroPython → 直接跑喺裝置）  
**額外獎勵：** 小智英語對話（提早完成的同學）

---

## 課堂流程（60 分鐘）

| 階段 | 活動 | 時間 |
|------|------|------|
| 1 | 引入——老師示範「考反應遊戲」 | 0–5 分鐘 |
| 2 | 認識 M5StickS3 + 連接 UIFlow 2.0 | 5–17 分鐘 |
| 3 | 第一個積木：畫面文字 + BtnA/BtnB 計分器 | 17–30 分鐘 |
| 4 ⭐ | **核心：Vibe Coding** — 設計遊戲 → 語音告訴 Gemini → 跑喺裝置 | 30–58 分鐘 |
| 5 | 總結 + 小智獎勵（提早完成者） | 58–60 分鐘 |

---

## 資料夾結構

```
tasting-course/
├── README.md
├── docs/
│   ├── lesson-plan.md              ← 完整教師教案 + 時間分配
│   └── handouts/
│       └── student-card.md        ← 可列印：連接步驟 + 遊戲設計表 + Gemini 提示
├── m5sticks3-clone/
│   ├── backups/partitions/        ← 由 backup.sh 從主機裝置備份
│   ├── xiaozhi/                   ← nvs_xiaozhi.bin + otadata_xiaozhi.bin（小智主機備份）
│   └── scripts/
│       ├── setup.sh               ← 安裝 esptool 虛擬環境（只需執行一次）
│       ├── backup.sh              ← 備份主機裝置（只需執行一次）
│       ├── flash_all.sh           ← 複製所有裝置 / --quick 在兩節之間重設
│       └── flash_xiaozhi.sh       ← 切換單一裝置至小智模式（約 5 秒，獎勵活動用）
├── scripts/
│   └── gen_starter.py             ← 將 DeepSeek API 金鑰從根目錄 .env 注入 starter
└── starter/
    ├── demo_reaction_game.py      ← 老師示範用：完整考反應遊戲
    └── main.py                    ← 參考：DeepSeek API 直接從裝置呼叫（下一節用）
```

---

## 課前準備清單（老師）

### 只需做一次（首次上課前）
- [ ] 執行 `m5sticks3-clone/scripts/setup.sh`（安裝 esptool）
- [ ] 為主機裝置刷入 UIFlow 2.0 並連接學校 WiFi
- [ ] 執行 `m5sticks3-clone/scripts/backup.sh` → 備份 UIFlow 分區
- [ ] 將主機切換至小智模式（透過 M5Launcher OTA 選單），然後手動備份：
  ```bash
  esptool.py read_flash 0x9000 0x4000 m5sticks3-clone/xiaozhi/nvs_xiaozhi.bin
  esptool.py read_flash 0xd000 0x2000 m5sticks3-clone/xiaozhi/otadata_xiaozhi.bin
  ```
- [ ] 執行 `m5sticks3-clone/scripts/flash_all.sh` 複製所有學生裝置
- [ ] 確認：每部裝置開機後顯示 UIFlow 2.0 雲端圖示 + 存取碼

### 上課當天（學生入座前）
- [ ] 插好所有裝置的 USB-C 線，確認顯示存取碼
- [ ] 投影機開啟 `uiflow2.m5stack.com` + `gemini.google.com`（各一個分頁）
- [ ] 列印 `docs/handouts/student-card.md`——每人一張

### 兩節之間（約 5 分鐘）
- [ ] `./m5sticks3-clone/scripts/flash_all.sh --quick`——重寫 NVS + SPIFFS，還原乾淨狀態
- [ ] 已切換至小智的裝置：同樣執行 `--quick` 還原 UIFlow 2.0

---

## DeepSeek API——下一節
`starter/main.py` 包含完整的 DeepSeek API 呼叫（在 M5StickS3 上執行）。這是課程橋樑：今日學生用 Gemini 幫自己生成程式碼，下一節將學習讓裝置直接呼叫 AI。詳見 `scripts/gen_starter.py`，可將 API 金鑰從根目錄 `.env` 注入。
