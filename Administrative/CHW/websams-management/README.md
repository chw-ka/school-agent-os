## CloudSAMS / WebSAMS management

對應：`chw-websams-migration`（MS SQL legacy → CloudSAMS，成績表相關資料）。

| 文件 | 用途 |
|------|------|
| `cloudsams-migration-plan.md` | 分階段計劃與時序 |
| `field-mapping.md` | Phase 0/1 欄位對照與 live 發現 |
| `cloudsams-templates/att/` | ATT 空白匯入範本 + 規格表（從 CloudSAMS 下載） |
| `cloudsams-manuals/` | 官方 EDB AUM 手冊（~1.3GB，**gitignored**）— 從 `../cloudsams-analysis/cloudsams-manuals/` 複製 |

**目前阻塞**：ASR 考績綱要未確定（S1/S2 公民經濟與社會、S3 普通電腦科 科目滿分及比重未完成）→ 無法匯出成績範本。

**Cursor 瀏覽器**：
1. **CLO 登入須人手完成**（用戶名／密碼或智方便；agent 不代填）。
2. 登入 CLO 後，agent patch `submitToPopup` 為 same-tab submit（popup 被擋），再按 迦密聖道中學 或 `WebSAMSRedirect('840')` 進 CloudSAMS。
3. 亦可直接開 `https://chw.sams.edu.hk/` →「經統一登入系統登入」（仍須已登入 CLO session）。

