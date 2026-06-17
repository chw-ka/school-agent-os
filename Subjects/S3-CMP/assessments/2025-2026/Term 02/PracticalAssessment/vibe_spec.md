# 任務三 Vibe Coding 規格 —《小食部銷售報告》

## 必須使用 Gemini（只限任務三）
本任務測試你的 **提示（Prompt）** 能力：你是總監，Gemini 是程式員。

## 輸入
讀取 `canteen_sales.json`（陣列），每個物件：
- `item`（字串，例如「魚蛋」「汽水」「三文治」）
- `price`（整數，單價）
- `qty`（整數，數量）
- `class`（字串，例如「3A」「3B」「3C」）

## 輸出
寫入 `sales_report.txt`（純文字，utf-8），內容要 **清晰、可讀、帶少少氣氛**，並包含：
1. 標題（例如含 🧾 或 🍟）
2. 全部交易的 **總收入**（revenue = price * qty）
3. **最賺錢** 的 item（合計收入最高）及其收入
4. 各班別（class）的總收入（至少列出 3A/3B/3C；若 JSON 有更多班別亦要列出）
5. 一句結尾（例如提醒同學帶零用錢／支持小食部）

你可以參考 `sales_report_sample.txt` 了解輸出格式與氣氛。

## 建議流程
1. 先用 `canteen_sales_sample.json` 叫 Gemini 寫 `task3_2526.py`
2. 對照 `sales_report_sample.txt`，自己運行測試，確保輸出的格式符合本規格
3. 再改讀 `canteen_sales.json` 生成正式 `sales_report.txt`
4. 把你的提示貼到 `gemini_prompts.txt`（至少 2 則完整提示）

## 提交
- `task3_2526.py`
- `sales_report.txt`
- `gemini_prompts.txt`（至少 2 則完整提示）

