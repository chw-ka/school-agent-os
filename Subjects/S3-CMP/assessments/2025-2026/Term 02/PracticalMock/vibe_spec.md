# 任務三 Vibe Coding 規格 —《遊戲頒獎典禮》

## 必須使用 Gemini
本任務測試你的 **提示（Prompt）** 能力：你是總監，Gemini 是程式員。

## 輸入
讀取 `game_scores.json`（陣列），每個物件：
- `name`（字串）
- `score`（整數）
- `team`（字串，例如「紅隊」「藍隊」）

## 輸出
寫入 `party_show.txt`（純文字，utf-8），內容要 **有趣、可讀**，並包含：
1. 標題（例如含 🎉）
2. 最高分玩家姓名、分數、隊伍
3. 亞軍（第二高分）姓名、分數、隊伍
4. 兩隊總分比較及勝出隊伍
5. 結尾一句鼓勵說話

## 建議流程
1. 用 `game_scores_sample.json` 向 Gemini 試寫 `task3_2526.py`
2. 對照 `party_show_sample.txt` 修改提示
3. 改讀 `game_scores.json` 產生正式 `party_show.txt`
4. 把提示貼到 `gemini_prompts.txt`

## 提交
- task3_2526.py
- party_show.txt
- gemini_prompts.txt（至少 2 則完整提示）
