---
name: meeting-minutes
description: >-
  將會議錄音逐字稿或 transcript 轉換為結構化中文會議紀錄。適用於科組會、行政會議、家長會等。Use
  when the user asks to write meeting minutes, 會議紀錄, or process a meeting
  transcript.
---

# 會議紀錄 SKILL

## 觸發條件

當用戶要求撰寫會議紀錄、處理 meeting transcript、或將錄音文字整理成 minutes 時，使用此 SKILL。

## 完整 Workflow（概念）

```
錄音 → 文字（逐字稿）→ + 議程 → 會議紀錄
                              ↓
                    格式來源（二選一）：
                    • 通用範本 `templates/minutes-template.md`（第二步）
                    • 上學年紀錄做格式參考（第三步，可選）
```

- **第一步（轉文字）**：通常由本機轉寫程式完成，非本 SKILL 主責
- **第二、三步（寫紀錄）**：本 SKILL 主責

## 第二步 vs 第三步

| | 第二步 | 第三步（可選） |
|--|--------|----------------|
| **內容來源** | 今年逐字稿 + 今年議程 | 今年逐字稿 + 今年議程 |
| **格式來源** | `templates/minutes-template.md` | 上學年紀錄 `.docx`（跟版面、欄位、語氣） |
| **目的** | 學 workflow | 貼近科組日常做法 |
| **注意** | — | **唔係合併**兩份紀錄；上學年檔只作格式參考，內容不可抄 |

## 執行流程

### Step 1：讀取輸入

必讀：
- **逐字稿** — `.txt` / `.md` 或 `output/transcript-from-audio.txt`
- **議程** — `議程_視藝科組會_20260528.docx` 或同等檔案

格式來源（按用戶指示二選一）：
- **通用範本** — `templates/minutes-template.md`（第二步）
- **上學年紀錄** — `會議紀錄_視藝科組_20250522_上學年.docx`（第三步，**只作格式參考**）

### Step 2：提取關鍵資訊

從**今年逐字稿**中提取：
- 會議名稱、日期、時間、地點
- 出席者、缺席者（含原因）
- 各議程項的討論內容（對照議程編號）
- **決議**（明確的決定，非一般討論）
- **跟進事項**（負責人 + 截止日期）

### Step 3：撰寫紀錄

- 使用**繁體中文書面語**（正式但自然）
- 跟隨指定格式來源的結構（通用範本或上學年紀錄版面）
- 討論摘要：每項 2–4 句
- 決議：編號列表
- 跟進：負責人 + 截止日期；缺則標「待確認」

### Step 4：輸出（雙格式）

**老師日常用 Word（`.docx`）；`.md` 排版文字保留喺 Cursor 內修改同學習。**

| 階段 | 排版文字（.md，Cursor 內） | 正式交付（.docx，用 Word 開） |
|------|---------------------------|------------------------------|
| 第二步 | `output/meeting-minutes-draft.md` | `output/會議紀錄_草稿.docx` |
| 第三步 | `output/meeting-minutes-final.md` | `output/會議紀錄_視藝科組_20260528.docx` |

撰寫流程：
1. 先完成 `.md` 草稿（內容完整、可預覽）
2. 用 `python-docx` 或同等方法轉為 `.docx`，字型建議 **微軟正黑體** 12pt
3. `.docx` 版面應跟格式來源（通用範本或上學年紀錄）一致

向用戶說明：「中間 `.md` 喺 Cursor 改；交俾校內／同事用 `.docx`。」

## 品質要求

- ❌ 不可捏造逐字稿中未出現的決議或數字
- ❌ 不可省略任何議程項
- ❌ 第三步時，不可把上學年紀錄的舊內容抄入今年紀錄
- ✅ 人名、日期、金額必須與今年逐字稿一致

## 學校背景（CHW）

- 學校：迦密聖道中學（Carmel Holy Word Secondary School）
- 語言：繁體中文書面語

## 示例 Prompt

**第二步：**
```
@.cursor/skills/meeting-minutes/SKILL.md
請讀 @sample-meeting-transcript.txt、@議程_視藝科組會_20260528.docx、@templates/minutes-template.md，
撰寫會議紀錄：先存 output/meeting-minutes-draft.md，再轉 output/會議紀錄_草稿.docx
```

**第三步：**
```
@.cursor/skills/meeting-minutes/SKILL.md
請讀 @sample-meeting-transcript.txt、@議程_視藝科組會_20260528.docx、
@會議紀錄_視藝科組_20250522_上學年.docx（格式參考），
撰寫今年會議紀錄：先存 output/meeting-minutes-final.md，再轉 output/會議紀錄_視藝科組_20260528.docx
```

結尾加註：「本紀錄由 AI 輔助起草，請記錄人覆核後方作正式版本。」

