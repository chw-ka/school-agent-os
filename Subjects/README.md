# Subjects

教學區 — 依 **級別＋科目** 建立工作區（例如 `S3-CMP/`、`S5-ICT/`），方便同一級別的所有素材集中查找。

## 存放策略（Git vs 科組 S:）

本 repo 為 **可攜工作副本**（家中無法連 S: 網絡，靠 `git push/pull` 同步）。科組共用資料夾 `S:\...\08_Others` 僅在校內使用，作發佈與歷史檔案庫。

詳見 **[STORAGE.md](STORAGE.md)**。Agent 技能：`.cursor/skills/panel-storage-sync/`。

## 每科目建議結構

```
S3-CMP/              # 級別工作區：校內出卷、筆記、考古題
├── exam-input/
├── past-papers/
└── notes/

DSE-ICT/             # 共用參考庫（F4–F6）：DSE 官方卷、EDB 文件
├── past-papers/
└── edb/

S5-ICT/              # 級別工作區：僅放該級校內試卷與出卷產物
└── past-papers/{YYYY-YYYY}/
```

## Subjects (English)

Teaching workspace organized by form and subject (e.g. `S3-CMP`, `S5-ICT`).

Per-subject folders hold exam input, past papers, and notes together so one form’s materials stay in one place.

**Storage:** Git is the portable copy for home; the panel share on `S:` is school-only. See [STORAGE.md](STORAGE.md).
