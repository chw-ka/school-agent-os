# Subjects

教學區 — 依 **級別＋科目** 建立工作區（例如 `S3-CMP/`、`S5-ICT/`），以便集中管理同一級別之教學內容與評核材料。

## 存放策略（Git vs 科組 S:）

本 repo 為 **可攜工作副本**（家中無法連線至 `S:` 校內網絡磁碟，需以 `git push/pull` 同步）。科組共用資料夾 `S:\...\08_Others` 僅供校內網絡使用，用於發佈與歷史檔案庫保存。

詳見 **[STORAGE.md](STORAGE.md)**。相關技能：`.qoder/skills/panel-storage-sync/`、`.qoder/skills/tidy-up/`（結構整理）。

## 每科目建議結構

```
S3-CMP/              # 級別工作區：校內出卷、筆記、考古題
├── assessments/      # 出卷工作區（草稿/輸入/spec/_generation）— 只留 git
├── past-papers/      # 終稿庫（可派發/可存檔版本）— 盡量乾淨
├── notes/
└── resources/        # 教學資源（worksheet assets / reference）

DSE-ICT/             # 共用參考庫（F4–F6）：DSE 官方卷、EDB 文件
├── past-papers/
└── edb/

S5-ICT/              # 級別工作區：僅放該級校內試卷與出卷產物
├── assessments/
└── past-papers/{YYYY-YYYY}/
```

### `assessments/` vs `past-papers/`（解決「混埋一齊」）

- **`assessments/`**：用於存放進行中之工作（出卷、批改、功課製作、功課核對等）  
  - 例：`assessments/2025-2026/Term 02/WrittenExam/_generation/`、`*.spec.json`
- **`past-papers/`**：僅存放可發佈與可歸檔之「終稿」  
  - 例：可派發的 `.pdf` / `.docx`、marking scheme（不含草稿及生成中間檔）

## Subjects (English)

Teaching workspace organized by form and subject (e.g. `S3-CMP`, `S5-ICT`).

Separate working drafts (`assessments/`) from final deliverables (`past-papers/`) so browsing past papers stays clean.

**Storage:** Git is the portable copy for home; the panel share on `S:` is school-only. See [STORAGE.md](STORAGE.md).
