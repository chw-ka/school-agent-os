# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 專案概覽

此倉庫用於籌備一場小學 STEAM 教師 PD 分享會（2026 年 6 月 22 日，元朗惠州學校），主題為 M5StickS3 硬件體驗。包含兩個主要子系統：

1. **根目錄 / `scripts/`** — Python 工具，用於生成 PPT 投影片、Google Form feedback、提取截圖
2. **`m5sticks3-clone/`** — 批量燒錄 M5StickS3 裝置的 shell 腳本及 esptool 工具流程

---

## 環境設定

### 根目錄（PPT / Forms / 圖片生成）

```bash
pip install -r requirements.txt
cp .env.example .env   # 填入 GEMINI_API_KEY
```

`.env` 需要的變數：

- `GEMINI_API_KEY`（或 `GOOGLE_API_KEY`）— 用於 `generate_ppt_slides.py`
- `IMAGEN_MODEL`（可選，預設 `imagen-4.0-generate-001`）

Google API 認證檔案位於 `config/`（`gcp-oauth.keys.json`、`google-forms-oauth-token.json`），由 `create_feedback_form.py` 讀取。

### m5sticks3-clone（燒錄工具）

```bash
cd m5sticks3-clone
./scripts/setup.sh   # 建立 .venv，安裝 esptool
```

---

## 常用指令

### PPT 投影片生成

```bash
# 生成全部 25 張投影片圖片（需要 GEMINI_API_KEY）
python scripts/generate_ppt_slides.py

# 只生成單張（例如第 14 張）
python scripts/generate_ppt_slides.py --slide 14

# Dry run（只印 prompt，不呼叫 API）
python scripts/generate_ppt_slides.py --dry-run
```

生成的 PNG 儲存於 `docs/ppt-output/`（已 gitignore）。

### 組裝 PPTX

```bash
# 將 ppt-output/ 的 PNG 組合成 .pptx
python scripts/build_pptx.py
# 輸出：docs/STEAM-Sharing-M5StickS3.pptx
```

### 建立 Feedback Form（Google Forms API）

```bash
python scripts/create_feedback_form.py
# 輸出 metadata 至 docs/feedback-form-meta.json
```

### 加 QR Code 至 PPTX

```bash
# 需先跑 create_feedback_form.py
python scripts/add_feedback_qr_to_pptx.py
```

### 提取截圖（從 Screen Capture.docx）

```bash
python scripts/extract_screen_captures.py
# 輸出至 docs/screen-captures/extracted/
```

### M5StickS3 燒錄流程

```bash
cd m5sticks3-clone

# 備份 master 機（連 download mode）
./scripts/backup-master.sh /dev/cu.usbmodem1101

# 還原到 target 機
./scripts/provision-device.sh /dev/cu.usbmodem1102

# 只補 bootloader（已 provision 但冇 Launcher）
./scripts/fix-launcher-boot.sh /dev/cu.usbmodem1102

# 進階：跳過 bootloader
INCLUDE_BOOT=0 ./scripts/provision-device.sh /dev/cu.usbmodem1102

# 讀 MAC 地址
.venv/bin/python -m esptool --chip esp32s3 -p /dev/cu.usbmodem1101 read-mac
```

---

## 架構說明

### PPT 生成流程

```
docs/ppt-slides-gemini-prompts.md
        │
        ├──(parse_slides)──▶ generate_ppt_slides.py ──▶ docs/ppt-output/*.png
        │                         Gemini Imagen API
        │
        └──(parse_filename_index)──▶ build_pptx.py ──▶ docs/STEAM-Sharing-M5StickS3.pptx
                                         + BLANK_SLIDES dict（幻燈片 4/11/12/14 用可編輯 placeholder）
```

- `ppt-slides-gemini-prompts.md` 是 **唯一事實來源**：定義每張投影片的編號、檔名、prompt
- 部分幻燈片（4、11、12、14）在 `build_pptx.py` 的 `BLANK_SLIDES` dict 中設定為「留白 placeholder」，不呼叫 API
- 含 `REFERENCE:` 的幻燈片使用 `gemini-2.5-flash-image` + `docs/assets/m5sticks3-product-reference.png` 生成

### Google Forms 流程

```
create_feedback_form.py ──▶ docs/feedback-form-meta.json（含 form_id, responder_uri）
                               │
add_feedback_qr_to_pptx.py ──▶ 讀 meta.json → 生成 QR → 插入 .pptx 最後一張
```

OAuth token 位於 `config/google-forms-oauth-token.json`；token 過期會自動 refresh（需有 refresh_token）。

### M5StickS3 燒錄架構

```
master StickS3
    │
    └── backup-master.sh ──▶ backups/manifest.json + backups/partitions/*.bin
                                    │
                               provision-device.sh ──▶ partition_utils.py ──▶ target StickS3 x20
```

- `partition_utils.py` 處理 manifest 解析及 esptool 寫入邏輯
- `backups/` 已 gitignore，每次從 master 備份產生
- Flash 布局（8MB ESP32-S3）：`app0`=M5Launcher、`sticks/stick1`=小智、`otadata` 控制開機 app

### 文件結構

| 路徑 | 用途 |
|------|------|
| `docs/lesson-plan-sticks3-steam-tasting.md` | 完整教案（90 分鐘、三 Task 流程） |
| `docs/participant-handout.md` | 參與者跟做筆記（含 `[📷 截圖]` 佔位符） |
| `docs/ppt-speaker-notes.md` | 講者全堂稿 |
| `docs/ppt-slides-gemini-prompts.md` | 25 張投影片 prompt 定義 |
| `docs/google-classroom-plan.md` | Google Classroom 課前 / 課中 / 課後運用方案 |
| `docs/feedback-form-meta.json` | Feedback Form URL（由 script 生成） |
| `m5sticks3-clone/docs/device-log.csv` | 裝置記錄表（編號 / MAC / 驗證碼 / 日期） |

---

## 重要注意事項

- `config/` 下的 OAuth token 及 service account JSON **不應** commit（已在 `.gitignore`）
- `docs/ppt-output/` PNG 同樣已 gitignore；重新生成需 API key
- `m5sticks3-clone/backups/` 已 gitignore；每次 `backup-master.sh` 前確認 master 機狀態正確
- 燒錄新機必須用 `INCLUDE_BOOT=1`（預設），否則開機會跳過 M5Launcher 直入小智
