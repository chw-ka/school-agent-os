## School-Agent-OS Navigation

本頁為一頁式索引，用以由「工作項目」直接定位至相應資料夾，便於日常查找及跨年度沿用。

### 行政／校務專案（CHW）

- **Migration（資料/系統搬遷）**: `Administrative/CHW/migration/`
- **Homework Diligence Award（Google Drive 流程）**: `Administrative/CHW/homework-diligence-award/`
- **Conduct mark（discipline yellow form）**: `Administrative/CHW/conduct-mark/`
- **CloudSAMS / WebSAMS management**: `Administrative/CHW/websams-management/` — migration plan: `cloudsams-migration-plan.md` (target: Term 1 2026–27)
- **SLP**: `Administrative/CHW/slp/`
- **Student report**: `Administrative/CHW/student-report/`
- **Sportsday**: `Administrative/CHW/sportsday/`
- **數字教育（校內政策/資源整合/推廣）**: `Administrative/CHW/digital-education/`
- **QEF「我的行動承諾」加強版撥款計劃**: `Administrative/CHW/my-action-promise-enhanced/`

### 教學（出卷／批改／功課／資源）

教學素材統一存放於 `Subjects/`，並按 **級別＋科目** 建立工作區：

- **STEAM（初中）**: `Subjects/STEAM/`（例：`tasting-course/`）
- **CMP（初中）**: `Subjects/S2-CMP/`, `Subjects/S3-CMP/`（可按需要增設 `S1-CMP/`）
- **ICT（高中）**: `Subjects/S5-ICT/`, `Subjects/S6-ICT/`, `Subjects/DSE-ICT/`（共用參考庫）
- **科組教學行政（選書等）**: `Subjects/TechEd/`

### 教師培訓 / 數字教育推廣（Training/）

與教學課程無直接關係，屬「數字教育」職責範疇：對外分享、教師 PD、學生體驗活動等。

- **M5StickS3 教師 PD 分享（2026-06-22 惠州學校）**: `Training/primary-staff-training/`
- **M5StickS3 小五 STEAM 體驗課**: `Training/primary-steam-tasting-p5/`

### 可共用工具（共建 platform submodule）

- **Platform submodule**: `_platform/` → [school-agent-os-platform](https://github.com/chw-ka/school-agent-os-platform)
- **文件/試卷模板**: `templates/`（symlink → `_platform/templates/`）
- **可重用自動化工具（CLI）**: `shared-tools/`（symlink → `_platform/shared-tools/`）
- **設定**: [docs/PLATFORM-SETUP.md](docs/PLATFORM-SETUP.md)
- **輸出暫存（不建議長期保存大量檔案）**: `output/`

#### shared-tools 索引

| 工具 | 路徑 | 用途 |
|------|------|------|
| marking | `shared-tools/marking/` | 自動批改作業（下載→評分→提交）；Teams connector 已完成，Classroom 待開發 |
| aia-tools | `shared-tools/aia-tools/` | MIT App Inventor .aia 解壓、Blockly 樹查詢、組件樹檢查 |
| code-marking | `shared-tools/code-marking/` | Python exec、Arduino 讀檔、EV3 批改、AI 使用偵測、MS Forms 評分 |
| paper-generator | `shared-tools/paper-generator/` | 試卷藍圖 → spec JSON |
| paper-formatter | `shared-tools/paper-formatter/` | spec JSON → DOCX |
| question-quality-check | `shared-tools/question-quality-check/` | 題目去重、概念覆蓋檢查 |
| paper-quality-check | `shared-tools/paper-quality-check/` | DOCX 格式審查 |
| exam-marking | `shared-tools/exam-marking/` | 掃描答題紙 OCR 批改（實驗性）|

