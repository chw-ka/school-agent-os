## CloudSAMS / WebSAMS management

對應：`chw-websams-migration`（MS SQL legacy → CloudSAMS，成績表相關資料）。

| 文件 | 用途 |
|------|------|
| `cloudsams-migration-plan.md` | 分階段計劃與時序 |
| `field-mapping.md` | Phase 0/1 欄位對照與 live 發現 |
| `data-entry-workflow.md` | Post-confirm checklist: export → UI test → Others → fill script |
| `cloudsams-templates/asr/` | ASR export save location (`_local/` gitignored) |
| `tools/cloudsams-export/` | `inspect_asr_export.py`, `export_scores.py` (scaffold) |
| `cloudsams-templates/att/` | ATT 空白匯入範本 + 規格表（從 CloudSAMS 下載） |
| `cloudsams-manuals/` | 官方 EDB AUM 手冊（~1.3GB，**gitignored**）— 從 `../cloudsams-analysis/cloudsams-manuals/` 複製 |

**目前狀態**：2025-26 考績綱要已 **Confirmed**（2026-07-07）→ ASR **匯出資料** 已解鎖（`flows/asr/data_entry/export`）。

**下一步**：匯出積分與等級範本（本地保存、勿 commit）→ Phase 2 `export_scores.py`；或 數據輸入 → 積分與等級 UI 入分。

**Cursor 瀏覽器**：
1. **CLO 登入須人手完成**（用戶名／密碼或智方便；agent 不代填）。
2. 登入 CLO 後，agent patch `submitToPopup` 為 same-tab submit（popup 被擋），再按 迦密聖道中學 或 `WebSAMSRedirect('840')` 進 CloudSAMS。
3. 亦可直接開 `https://chw.sams.edu.hk/` →「經統一登入系統登入」（仍須已登入 CLO session）。

**考績綱要設定 — agent 必守**（詳見 `legacy-to-cloudsams-weights.md`）：

| 規則 | 說明 |
|------|------|
| **確定綱要紅字** | 按紅字指示返 **科目滿分及比重**（或 **學期及考績**）該 **級別 + 考績** 逐科修正 |
| **⛔ 禁止 Copy / 複製** | 複製紀錄、編輯頁 Copy [n]、分配批量複製 — **一律不用**（會漏嘢） |
| **儲存流程** | 儲存 → 彈出 **確定** → 見 **Record saved successfully.** → **返回再搜尋** 核對有否寫入 |
| **逐格填** | 每個 級別 × 七個考績/學期 × 科目 分開填；T1 完成 ≠ T2 完成 |

