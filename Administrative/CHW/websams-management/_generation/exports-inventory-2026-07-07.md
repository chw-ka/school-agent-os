# CloudSAMS export inventory — 2026-07-07

Checked `Downloads` + `cloudsams-templates/asr/_local/`.

## 積分與等級（全校，每期一 zip）

| Period | Status | File |
|--------|--------|------|
| T1A1 | ✅ Have | `whole-school-T1A1-scores.zip` (24 classes S1–S6) |
| T1A2 | ✅ Have | `whole-school-T1A2-scores.zip` (24 classes) |
| T1 | ❌ Need export | — |
| T2A1 | ❌ Need export | — |
| T2A2 | ❌ Need export | — |
| T2 | ❌ Need export | S1–S5 only (no S6) |
| Annual | ❌ Need export | — |

Duplicates in Downloads (`DE_52457320260707_*.zip`) are same content as above; safe to ignore.

## 其他考績（全校，每期一 zip — T1 = 上學期）

| Period | Status | File |
|--------|--------|------|
| **T1** | ❌ **Need whole-school export** | Target: `whole-school-T1-others-export.zip` (24 classes, 4×4 xls types) |

**Workflow correction (2026-07-07):** Others can be exported **whole-school** (same as 積分與等級) — tick all levels + all classes + period **T1** + all 5 categories. **Do not** loop S1–S6 separately.

**Superseded (optional keep):** per-level zips `S1-T1-others-export.zip` … `S6-T1-others-export.zip` — valid templates but redundant; prefer one whole-school zip.

**Earlier S1-only:** `S1-T1-others-export.zip` (1A–1D only) — still valid for S1 trial import.

### Export automation gotchas (Others)

1. **T1 period:** `widget_fmAsrDataEntryExport_j_idt218.selectValue('1//1100', false)` — `false` = no AJAX reset. Label `'T1'` or `change` event reverts to T1A1.
2. **All 5 tick-boxes:** set `othersList:0..4` via `.checked = true`, then **same turn** `PrimeFaces.ab(saveButton)`. `.click()` or separate steps → only 獎懲 exported.
3. **Whole school:** tick **all** `clsLvlList:0..5` (or leave all selected after Others mode) — **no** per-level loop; no `clsLvlList` AJAX wait needed.
4. **Save before next export:** browser always downloads `OTHERS_T1.zip` — copy to `_local/` with unique name immediately.
