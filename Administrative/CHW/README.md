## CHW Administrative Projects

本區用以將校務／行政專案固定歸檔於一致的目錄結構，確保跨年度可沿用，並使各專案之間保持相互獨立、互不干擾。

### 專案目錄

- **Migration**: `migration/`
  - 系統/資料搬遷（例如匯入匯出、欄位對照、清洗規則、dry-run 記錄）
- **Homework Diligence Award**: `homework-diligence-award/`
  - 主要於 Google Drive／Google Sheet 執行；此處存放 runbook、欄位定義與腳本（不存放具名名單）
- **Conduct mark**: `conduct-mark/`
  - 對應原專案 `chw-discipline-yellow-form`
- **CloudSAMS / WebSAMS management**: `websams-management/`
  - 對應原專案 `chw-websams-migration`
- **SLP**: `slp/`
  - 對應原專案 `chw-slp-temp`
- **Student report**: `student-report/`
  - 對應原專案 `chw-student-report-old`（已併入；歷年檔案見校內 `T:\`）
- **Sportsday**: `sportsday/`
  - 對應原專案 `chw-sports-day`
- **Digital education**: `digital-education/`
  - 數字教育推廣、資源整合、校內流程
- **QEF e-Learning Grant**: `qef-elearning-grant/`
  - 對應原專案 `chw-workflows`；優質教育基金電子學習撥款計劃（流動電腦裝置及上網支援）

### 共用工具（放 `shared-tools/`）

如以下能力會跨多個專案重複使用，建議抽離並共建為 `shared-tools/` 內的 CLI 工具：

- **匯入匯出與欄位對照**：CSV/Excel ↔ JSON schema、欄位 mapping、dry-run diff
- **名單/計數/統計**：依規則計分、匯總、產出報表（只用匿名/代碼欄位）
- **文件產生**：用 `templates/` 產出標準格式 Word/PDF（新細明體 12pt / A4 邊距）

> 私隱原則：成績表、學生個人資料、具名學生作品不應提交至 git（僅限本機處理或留存於校內網絡磁碟／雲端平台）。

