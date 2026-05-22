# S5-ICT

中五資訊及通訊科技（ICT）工作區。

## 建議結構

- `past-papers/`：校內試卷（`{YYYY-YYYY}/Term {01|02}/WrittenExam/`、`_generation/` 等）
- `exam-input/`、`source/`、`notes/`：可按需要新增

DSE 官方卷及 EDB 文件見 [`../DSE-ICT/`](../DSE-ICT/)（F4–F6 共用）。

## 出卷流程（規劃中）

目標：**DSE 題庫藍本 → 逐題 generate → 組裝 spec → formatter 套校內模板**。

- 完整 flow 說明：[`shared-tools/paper-generator/F5_ICT_DSE_BLUEPRINT_FLOW.md`](../../shared-tools/paper-generator/F5_ICT_DSE_BLUEPRINT_FLOW.md)
- Blueprint 模板：`past-papers/2025-2026/Term 02/_generation/exam_blueprint.template.json`
- **Blocker：** `DSE-ICT/question-bank/` 目前只有 2019 Paper1 MCQ JSON，需先補齊 2019–2025 才實作自動抽題

現行 recipe（DSE 題庫抽題 + 24_25 layout + **強制 quality-check**）：

```bash
python shared-tools/paper-generator/f5_ict_blueprint_db_web.py
```

MCQ 必須 **Core A → B → D** 分塊（見 `mcq_core_plan.py`、`curriculum_concepts.json`）；generate 後檢查報告在 `_generation/*.spec.duplicates.json`。

**試卷結構：** 甲部 = MCQ（Core A/B/D）；乙部 = 必修結構題；丙部 = 選修 Module A + C（等同 DSE Paper 2）— **丙部不設 MC 題**。
