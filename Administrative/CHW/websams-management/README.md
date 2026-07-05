## CloudSAMS / WebSAMS management

對應：`chw-websams-migration`（MS SQL legacy → CloudSAMS，成績表相關資料）。

| 文件 | 用途 |
|------|------|
| `cloudsams-migration-plan.md` | 分階段計劃與時序 |
| `field-mapping.md` | Phase 0/1 欄位對照與 live 發現 |
| `cloudsams-templates/att/` | ATT 空白匯入範本 + 規格表（從 CloudSAMS 下載） |

**目前阻塞**：ASR 考績綱要未確定（S1/S2 公民經濟與社會、S3 普通電腦科 科目滿分及比重未完成）→ 無法匯出成績範本。

**Cursor 瀏覽器**：CLO → CloudSAMS 需 patch `submitToPopup` 為 same-tab submit（popup 被擋）。

