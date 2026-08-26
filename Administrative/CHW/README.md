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
- **QEF「我的行動承諾」加強版 — 聖道小記者**: `qef-my-commitment-junior-reporters/`
  - 「我的行動承諾」加強版撥款計劃（編號 42）；「聖道小記者」計劃申請書（草稿階段，死線 2026-08-31）

### 原始資料（不入 git）

- **_raw/**: 從校內收到的原始 Excel/CSV 匯出檔（含學生姓名，已加入 `.gitignore`）

### 選修科目資料更新流程（Elective Data Update）

每年收到 MC 的 `S4-6 Name List for Electives_*.xlsx` 後，按以下步驟更新：

1. **複製原始檔** → `Administrative/CHW/_raw/`
2. **執行腳本** → `python scripts/update-elective-basedata.py`
   - 自動讀取 `_raw/` 中最新的 xlsx
   - 處理 S4、S5、S6 分頁（跳過 APL 及「總數」）
   - 處理底部修正列（row > 130）
   - 輸出至 `chw-api/basedata/student_elective_data.csv`
3. **上傳 Google Sheet** → 在 `chw-api/` 目錄執行：
   ```python
   # 強制更新「學生選修資料」分頁
   import gspread, time, pandas as pd
   from google.oauth2.service_account import Credentials
   creds = Credentials.from_service_account_file('credentials.json',
       scopes=['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive'])
   gc = gspread.authorize(creds)
   ss = gc.open_by_key('1jb8TYfVk20ZdRKAE9i5ka9lYY9NPifSRtNFYqMqUeqI')
   ws = ss.worksheet('學生選修資料')
   ws.clear()
   df = pd.read_csv('basedata/student_elective_data.csv')
   ws.update([df.columns.tolist()] + df.fillna('').values.tolist(), 'A1')
   ```
4. **重新整理 API**（可選）→ `POST https://api.chw.edu.hk/refresh-data`（需 API key）

**憑證檔案**: `chw-api/credentials.json`（GCP service account，不入 git）

### 共用工具（放 `shared-tools/`）

如以下能力會跨多個專案重複使用，建議抽離並共建為 `shared-tools/` 內的 CLI 工具：

- **匯入匯出與欄位對照**：CSV/Excel ↔ JSON schema、欄位 mapping、dry-run diff
- **名單/計數/統計**：依規則計分、匯總、產出報表（只用匿名/代碼欄位）
- **文件產生**：用 `templates/` 產出標準格式 Word/PDF（新細明體 12pt / A4 邊距）

> 私隱原則：成績表、學生個人資料、具名學生作品不應提交至 git（僅限本機處理或留存於校內網絡磁碟／雲端平台）。

