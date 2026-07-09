# 設置步驟

1. 開一個新 Google Sheet,建立以下 tabs(名稱要完全一致,Apps Script 靠名稱讀取):
   `Raw Import`、`Review`、`Username Lookup`、`Send Log`、`Config`
2. 按 [sheet-design.md](sheet-design.md) 喺每個 tab 第一行填入欄位標題(header)。
3. Extensions → Apps Script,將 `tools/apps-script/` 入面啲 `.gs` 檔案內容複製貼入(建立同名檔案):
   `Config.gs`、`SchooLinkClient.gs`、`UsernameLookup.gs`、`ParseImport.gs`、`Sender.gs`、`Code.gs`
4. Project Settings(左邊齒輪 icon)→ Script Properties → 新增:
   - `SCHOOLINK_KEY` = (廠商俾嘅 key,唔好打入任何會 commit 嘅檔案)
   - `MESSAGE_TYPE_ID` = `640`(暫用 spec 範例值,要向廠商確認正式學校用邊個)
5. 返去 Sheet,重新整理個分頁 → 應該見到自訂選單「圖書館通知」。
6. 首次執行順序:
   1. 「1. 更新學生帳號對照表」— 建立 Username Lookup(留意 StudentID 欄係猜測值,抽 20 個人手核對)
   2. 貼一份逾期匯出入 `Raw Import`(要求圖書館提供帶 StudentID 嘅版本)
   3. 「2. 由 Raw Import 生成 Review」
   4. 人手喺 Review 度剔選 / 刪走已還書嘅學生
   5. 「3. 發送今日通知」— **建議第一次淨係揀 1-2 個測試帳號試發**,確認格式冇問題先大量用

## 未做完 / 需要你決定

- 排程(time-driven trigger)未加 — 建議人手跑幾日確認冇問題,先轉自動。
- `getMessageReports` 嘅已讀查詢未實作,因為 spec 入面 `sendNoticeMessage` 冇話點攞返 `messageID`(見 [sheet-design.md](sheet-design.md) 「未確認/要問廠商嘅事」)。
- 繳費/罰款流程與 SchooLink 嘅實際銜接未落實。
