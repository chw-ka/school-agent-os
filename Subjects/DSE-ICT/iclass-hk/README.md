# iClass HK — 題庫與教學投影片

來源：iClass HK（SSICT）題庫 DOCX 及投影片 PPTX。用途是 **校準 S5/F5 ICT 出題深淺**（Core A/B/D、選修 EA/EC），唔係 DSE 公開試題庫，亦唔應逐字抄入試卷。

## 規模（最近一次抽取）

| 類型 | 數量 | 說明 |
|------|------|------|
| 題庫 DOCX | 32 | `QB_*.docx`（中／英；Core A1–3、B、D1–6、Di；Elec A1–5、C1–8、綜合） |
| 投影片 PPTX | 29 | `HA1`、`EB`、`HD1/2`、`EA1`、`EElecA/C` 等 |
| 題目 JSON | **517** | `json/*.json`（MCQ 332、短答 134、長答 51） |
| 投影片 JSON | **2006** 張 | 每張 slide 一段文字 |

## 輸出

- `json/index.json` — 完整目錄（所有來源檔 → JSON 路徑）
- `json/CoreA1_hk.json` … `ElecCi_en.json` — 題庫（每題含 stem、options、answer、parts、concepts、difficulty_tier）
- `json/HD2_Ch4_slides.json` 等 — 投影片文字
- `depth_profile.json` — 按課題單元（Core-A-ch1、EA-ch3…）統計深淺分布

## 重新抽取

```bash
.venv/bin/python shared-tools/paper-generator/extract_iclass_hk.py
```

新增 `QB_*.docx` 或 `*.pptx` 後再跑上述指令即可；檔名會自動推斷 `curriculum_unit`（Core-A/B/D、EA、EC）。

## 出卷時（自動）

- `generate_from_blueprint` 對每 slot 附 **`depth_references`**（相關 iClass 題預覽）
- 概念匹配時參考 iClass 問法深度（`iclass_hk_depth.py`）
- 詳見 `.cursor/skills/generate-f5-ict-exam/SKILL.md`

## Git

原始 DOCX/PPTX 與 JSON 可 commit（無學生個人資料）。唔寫 panel share 除非用戶明示。
