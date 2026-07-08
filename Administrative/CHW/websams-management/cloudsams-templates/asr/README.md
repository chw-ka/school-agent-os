# ASR export templates (local only — never commit)

CloudSAMS **匯出資料** files contain student registration numbers and embedded **整批號碼 (batch number)**. They must come from the system's own export; hand-built Excel is rejected on import.

## Save location

1. CloudSAMS export → encrypt → **Save** in the browser (defaults to `%USERPROFILE%\Downloads`).
2. Copy/rename into repo workspace (gitignored):

| Export | Suggested `_local/` name |
|--------|--------------------------|
| S1 T1A1 積分與等級 (all classes, all subjects) | `S1-T1A1-scores.zip` |
| 全校 其他考績 T1 (all levels, all classes) | `whole-school-T1-others-export.zip` |
| Decrypted `.xls` | `extracted/` |

## How many exports?

| Mode | Batching rule | Count |
|------|---------------|-------|
| **積分與等級** | One zip per **period**; **全校** S1–S6 + all classes + all subjects (**T2 期除外：S1–S5 only**，中六已畢業) | **7** (T1A1…Annual) |
| **其他考績** | One zip per **period**; **全校** S1–S6 + all classes; **multiple tick-boxes** per export (**T2 期：S1–S5 only**) | **1** for **T1** (上學期 legacy); **+1** for **T2** when needed |

For score template work: **7 score zips** (whole school each) + **1–2 Others zips** (T1, optionally T2).

`_local/` is gitignored.

**Export password** (encrypt on 匯出 only): 8–40 chars, upper+lower+digit+special, no spaces — password manager only.

**Import zip:** decrypt export → edit `.xls` → **plain zip, no password**. Limits: 積分與等級 ≤10 Excel/zip; 其他資料 zip-only ≤12 Excel/zip (flat files, not nested zips).

**Filename rule (critical):** Excel basenames from export are immutable. Reference: `../chw-websams-migration` — scores `DE_524573{date}_{seq}_3_3_S1_1A.xls`; others `3_3_S1_1A_CONDUCT_AND_OVERALL_COMMENT.xls` (not `DE_*`). Re-zip names: scores `DE_{school}{date}_{seq}.zip`; others `OTHERS_T{term}_{n}.zip`.

## Export settings (2025-26 test year)

**積分與等級** (`flows/asr/data_entry/export`):

- 積分與等級 (not 其他考績)
- 按班別 → tick **all levels S1–S6** → **all classes** → one **period** per export
- 搜尋 → tick **all subjects** → 匯出
- Format: **Excel**
- **7 exports** (T1A1 … Annual), each whole-school

**其他考績** (same page, 其他考績 mode):

- Tick **one or more** of: 獎懲資料、缺席紀錄、整體評語、操行、其他考績
- **按班別** → tick **all levels S1–S6** → **all classes** → one **period** per export → Excel
- **上學期 Others:** pick **T1** (not T1A1) — legacy 評語/操行/獎懲/缺席 are per term; batch suffix `1100` not `1101`
- **下學期 Others:** pick **T2** — tick **S1–S5 only**（中六已畢業）；still **one zip** per period
- Reference: `../chw-websams-migration/migrate_others.py` uses 獎懲 + 缺席 + 整體評語 + 操行 (chunks filled xls into ≤12-file import zips)

## After download

```bash
# Inspect column schema (no student data in git)
python Administrative/CHW/websams-management/tools/cloudsams-export/inspect_asr_export.py \
  "_local/extracted/S1-T1A1-1A.xlsx"
```
