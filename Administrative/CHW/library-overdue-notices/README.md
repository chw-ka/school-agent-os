# Library Overdue Notices

目標:圖書館現時每日產出逾期還書 txt(見 `_local/`,例：`KA-sample-20260707.txt`),由職員手動追人。改為透過 **SchooLink API** 直接向逾期學生(不含教職員)推送 App 通知,並視乎方案處理逾期罰款提示。

## 背景

- 逾期名單由圖書館系統每日匯出,格式為班別+學號+中英文姓名 + 逾期書目清單。
  - 中文欄位有亂碼(疑似匯出時已損毀,非單純編碼問題),暫以英文姓名 + 班別學號做比對依據。
  - 名單內夾雜教職員/科組虛擬帳號(如 `AW`、`BIB2023`、`HIS2022`、`PS`、`PT`、`TW`、`TY`、`WS`),與學生行(如 `1A22`)格式不同,需要濾走。
- SchooLink API spec 見 `docs/SchooLink API Specification (CHW)_v1.0.pdf`。
  - `sendNoticeMessage`:可指定 `usernames`(個別學生)或 `groups`(全班),支援 `sendDate`/`sendTime` 排程。
  - `getMessageReports`:查已讀/已回覆狀態,方便追收升級。
  - 家長帳號透過 SchooLink 可直接繳費(校方已確認),故罰款追收都可透過同一渠道處理,唯本 spec 未列明繳費/收款相關 API,需要另外向 SchooLink 確認欄位。

## 資料處理原則

- `_local/` 存放帶學生姓名/逾期紀錄嘅原始匯出樣本 — **已加入 .gitignore,不入 git**。
- `docs/` 存放廠商規格文件等非學生資料 — 可入 git。
- `SchooLinkKey`(API credential)不可寫入任何會 commit 嘅檔案,一律用本機 `.env` 或本機設定檔存放。

## 設計方案:Google Sheet + Apps Script

決定用 Google Sheet(同事覆核/剔選)+ Apps Script(呼叫 SchooLink API),唔起獨立 platform 原因見上面討論。詳細設計:

- Sheet 欄位設計:[docs/sheet-design.md](docs/sheet-design.md)
- 設置步驟:[docs/setup.md](docs/setup.md)
- Apps Script 程式碼(複製去 Google Sheet 嘅 Apps Script editor):`tools/apps-script/`

## 待決事項

- 發送排程:即日發,定係夜晚/翌日早上批量發?(先人手跑幾日,穩定先加 time-driven trigger)
- `username` 對應學生編號嘅規則未證實(暫假設 `S<StudentID>`),要抽樣核對。
- `getMessageReports` 已讀查詢:spec 嘅 `sendNoticeMessage` 回應冇 `messageID`,要問廠商點樣攞。
- 罰款/繳費流程與 SchooLink 之間嘅實際銜接,需要再問廠商確認。
