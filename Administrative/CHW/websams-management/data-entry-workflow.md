# CloudSAMS data entry — one-by-one checklist (2025-26)

Assessment profile **Confirmed** 2026-07-07. Work through in order.

## Step 1 — ASR export template (積分與等級) ✅ 2026-07-07

**Path:** 學生成績 → 數據輸入 → 匯出資料 (`/flows/asr/data_entry/export`)

1. Select **Score and Grade**
2. By Class → tick **all school levels** (S1–S6) → tick **all classes** → pick **one period** (e.g. T1A1) → Excel
3. **Search** → tick **all subjects** (head checkbox) → **Export**
4. Encrypt password → Confirm → **Save** (OS dialog defaults to `Downloads`)
5. Move zip from `Downloads` → `cloudsams-templates/asr/_local/` (agent can do this after you save)
6. Repeat **step 2–5 per period** only (T1A2, T1, T2A1, …) — **not** per class, **not** per form

**Batching (積分與等級):** one zip per **period** for the **whole school** — all levels (S1–S6) + all classes + all subjects in each export. **7 zips total** (T1A1 … Annual). Do **not** export one form at a time.

**Done (partial — redo as whole-school):** earlier `DE_524573…` runs were **S1-only by mistake** (agent used `setupS1Only` — wrong). **Do not** repeat per-form exports.

**Done (2026-07-07, whole-school):**
- `whole-school-T1A2-scores.zip` (~99 KB)
- `whole-school-T1A1-scores.zip` (~93 KB) — 1A→6D verified in subject grid before export

**Still need (上學期 first — Current Term stays 1):** T1 only (dropdown may not show T1 until T1A1/T1A2 complete or term advances). **下學期 later:** T2A1, T2A2, T2, Annual — **S1–S5 only** (中六已畢業); requires Current Term → 2 when ready.

**Do not** change Current Term without explicit approval.

## Step 2 — UI smoke test (積分與等級) ✅ 2026-07-07

**Path:** 學生成績 → 數據輸入 → **Score & Grade** (`/flows/asr/data_entry/score_grade` or menu)

1. Open S1 / 1A / T1A1 / one subject (e.g. Mathematics)
2. Enter one synthetic test score for one student
3. Save → reload → verify persisted
4. Clear test score before production import

**Verified:** S1 / 1A / T1A1 / 數學 — entered **85** for 1A1 區永傑, saved, reload confirmed, then cleared.

### Blocker: E-46206 (考績已鎖定)

If inputs are disabled and page shows `E-46206 : 已人手鎖定考績/學期/年終` → unlock via **數據合併 → 數據整合 → 處理數據**:

1. Search: 現學年 (2025), 中一
2. Tick row checkbox (e.g. T1A1)
3. Click **解鎖** (`unlockScopeButton`) — opens scope dialog
4. Click **解鎖** inside dialog (`unlockButton`)
5. Lock status may change e.g. 全部鎖定 → 其他鎖定 (積分與等級 editable)

### Lock status labels (重要)

| 狀態 | 意思 | 要匯入… | 解鎖步驟 |
|------|------|---------|----------|
| **全部鎖定** | 積分 + 其他都鎖 | 任何 | 解鎖 → 揀 **全部**（或先 **積分與等級** 再 **其他**） |
| **其他鎖定** | 積分已開，**其他考績仍鎖** | 評語/操行/獎懲/缺席 | 解鎖 → 揀 **其他** |
| （空白） | 未鎖 | 任何 | 唔使解鎖 |

**E-46175** = 其他考績被鎖；**E-46206** = 積分被鎖。

2025-26 S1 T1A1/T1A2/T1 were **全部鎖定** (legacy carry-over); partial unlock was enough for score entry.

## Step 3 — Others export (其他考績)

Same **匯出資料** page → select **其他考績** (not 積分與等級).

### Two modes — do not confuse

| | 積分與等級 | 其他考績 |
|---|-----------|----------|
| **Scope** | **全校** — S1–S6, all classes, all subjects | **全校** — S1–S6, all classes (**T2 期除外：S1–S5 only**) |
| **Batching** | 1 zip per **period** (7 total: T1A1…Annual) | 1 zip per **period** (e.g. **T1** for 上學期 legacy) |
| **What you pick** | Subjects (after Search) | Up to **5 tick-boxes** (see below) + all levels + all classes + one period |

### 其他考績 — tick-boxes (can select **multiple**)

- 獎懲資料 → `*_AWARD_PUNISHMENT.xls`
- 缺席紀錄 → `*_NON_ATTENDANCE.xls`
- 整體評語 + 操行 (both ticked) → `*_CONDUCT_AND_OVERALL_COMMENT.xls`
- 其他考績 → `*_OTHER_ASSESS.xls`

For legacy migration (`../chw-websams-migration`), tick **獎懲、缺席、整體評語、操行** in one whole-school export (skip 其他考績 unless scheme uses it).

### Export steps (whole school — same pattern as 積分與等級)

1. **其他考績** mode → tick needed categories above
2. **按班別** → tick **all school levels** (S1–S6) → tick **all classes** (1A–6D) → pick **one period** (e.g. **T1**) → Excel
3. **搜尋** → encrypt password → **Save** → copy/rename to `_local/` (e.g. `whole-school-T1-others-export.zip`)
4. Repeat **step 2–3 per period only** when you need another term (e.g. **T2** later — **exclude 中六**)

**Do not** export one level at a time (S1, then S2, …) — unnecessary; CloudSAMS supports whole-school Others export. **Do not** use 積分與等級 mode for 評語/操行/獎懲.

**Correction (2026-07-07):** earlier agent ran **6 per-level exports** (`S1-T1-others-export.zip` … `S6-T1-others-export.zip`). Content is valid but redundant; prefer **one** `whole-school-T1-others-export.zip` going forward.

**Period — T1 or T1A1? (important)**

| Data type | Export period | Why |
|-----------|---------------|-----|
| **積分與等級** | **T1A1**, T1A2, T1, … (one per zip) | Scores are per assessment phase; 7 whole-school zips |
| **其他考績** (評語/操行/獎懲/缺席) | **T1** for 上學期 legacy data | Legacy `tblStudentComment` / `tblStudentConduct` / reward / absence are **per term** (`*_1` / `*_2`), not T1A1/T1A2 |

**Batch-token check** (last column in `.xls`):

| Period exported | Example suffix | File type |
|-----------------|----------------|-----------|
| **T1** | `…_1100` | `CONDUCT_AND_OVERALL_COMMENT_…_1100` |
| T1A1 | `…_1101` | `OVERALL_COMMENT_…_1101` (評語-only export) |

`chw-websams-migration` used `CURRENT_TERM = 1` and `OTHERS_T1_*.zip` — **not** T1A1.

**Rule:** For 2025-26 上學期 migration, Others export → pick **T1** only. Do **not** use T1A1 for 整體評語/操行 unless you intentionally want phase-1 empty templates (wrong for legacy `comment_*_1`).

### School calendar — 中六與 T2

| 考績 | 適用級別 | 備註 |
|------|----------|------|
| T1 / T1A1 / T1A2（上學期） | **中一–中六** | 全級在學 |
| **T2 / T2A1 / T2A2**（下學期） | **中一–中五 only** | **中六已畢業** — 唔好匯入/填 S6 下學期 Others 或成績 |

- **積分與等級** T2 期 export：全校 tick 時 **exclude 中六**（或預期 S6 無資料）。
- **其他考績** T2 export：**1 個 zip**（全校 S1–S5，**唔 tick 中六**）；唔使分級別 export。
- Legacy `*_2` columns → CloudSAMS **T2**（batch suffix `1200`），對應 **S1–S5** 學生。

**Note:** Others mode opens encrypt dialog on **Search** (no subject grid).

**Done (2026-07-07):**
- `OTHERS_T1A1.zip` (Downloads) — per-class nested zips, **T1A1** / 整體評語 only → inner files `3_3_S1_*_OVERALL_COMMENT.xls`
- `others-extracted/3_3_S1_1A_CONDUCT_AND_OVERALL_COMMENT.xls` — correct **T1 + 整體評語+操行** schema (`評語 (中文)`)

**Wrong export (discard):** `S1-T1-others-all-classes.zip` (`DE_524573…_110435`) — produced **score** `DE_*.xls` files, not Others templates.

**Proven pipeline:** see `../chw-websams-migration` (`migrate_others.py`, `migrate_results.py`) — decrypt export → edit cells only → re-zip with **unchanged Excel basenames** → import plain zip.

**Import trial (needs redo):** earlier `others-trial-import-1A.zip` used `OVERALL_COMMENT` from T1A1 export; likely rejected because filename/batch must match the **same** export you are filling. Redo with `CONDUCT_AND_OVERALL_COMMENT.xls` from a fresh **whole-school T1** Others export (整體評語+操行+獎懲+缺席).

## Step 3b — Import rules (匯入資料)

| Type | Format | Zip limit |
|------|--------|-----------|
| 積分與等級 | Excel or Zip | ≤10 Excel per zip |
| 其他資料 | **Zip only** | ≤12 Excel per zip |

**Export → edit → import:** decrypt export zip → fill `.xls` (**keep filenames**) → plain zip (no password) → upload under the correct section. Do **not** nest zip files inside the import zip.

## Step 4 — Legacy → CloudSAMS fill script

**Tool:** `tools/cloudsams-export/export_scores.py`

1. Run `inspect_asr_export.py` on Step 1 file → `schema.json` in `_generation/`
2. Query legacy `tblStudentPaperScore` for same class/period (local sqlcmd / mssql-legacy)
3. Fill exported xlsx in place (**do not rename file** — batch number must match)
4. Import via 匯入資料 → verify one class

## Parallel (no ASR dependency)

| Module | Path | Status |
|--------|------|--------|
| ATT | 學生出席資料 → 輸入 | Blank template in `cloudsams-templates/att/` |
| Subject remark | 數據輸入 → 科目評語 | UI only |
| ANP awards | 獎懲資料 | No file import — batch UI or skip |
