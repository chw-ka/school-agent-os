# Google Sheet 設計

## Tabs 總覽

| Tab | 用途 | 邊個寫入 |
|---|---|---|
| `Raw Import` | 貼入圖書館每日匯出(建議要求圖書館提供帶學生編號嘅 CSV) | 同事(貼入) |
| `Review` | 每個學生一行,彙總佢嘅逾期書目,同事喺度覆核/剔選 | Apps Script 生成,同事編輯部分欄 |
| `Username Lookup` | SchooLink 學生帳號快取(用 `getUsers` 建立) | Apps Script |
| `Send Log` | 每次發送嘅審計紀錄(唔可以覆寫,只可以 append) | Apps Script |
| `Config` | 非機密設定(唔存 API key) | 你手動填 |

## Raw Import

一行 = 一本逾期書。要求圖書館匯出時加返「學生編號」一欄 —— 呢個係關鍵,因為淨係得學號/姓名唔夠穩陣分辨學生 vs 教職員/科組虛擬帳號(例如 `BIB2023`、`HIS2022` 呢啲得班別冇學生編號)。

| Col | 欄位 | 例子 |
|---|---|---|
| A | StudentID | `99999999`(虛構例子) |
| B | ClassCode | `1X99`(虛構例子) |
| C | NameEng | `Chan Tai Man`(虛構例子) |
| D | NameChi | `陳大文`(虛構例子,如果匯出冇亂碼) |
| E | BorrowDate | `2026-04-29`(YYYY-MM-DD) |
| F | CallNumber | `CHI 857.7 1142 2019` |
| G | Title | `……有個小部落 / 米奇鼠` |

**濾走教職員/科組行嘅規則**:`StudentID` 為空 = 唔係學生,Apps Script 會自動跳過,唔會出現喺 `Review`。呢個比以前靠 regex 認 `1A22` 呢類 pattern 穩陣好多。

## Review(由 Apps Script 由 Raw Import 彙總生成)

| Col | 欄位 | 說明 |
|---|---|---|
| A | StudentID | |
| B | Username | 對應 SchooLink 帳號(由 Username Lookup 撈,撈唔到會用 `S<StudentID>` 做猜測,標紅要人手核對) |
| C | ClassCode | |
| D | NameEng | |
| E | NameChi | |
| F | ItemCount | 逾期書目數量 |
| G | MaxDaysOverdue | 最耐一本逾期咗幾多日 |
| H | OverdueSummary | 自動生成嘅多行文字(借閱日期｜索書號｜書名｜逾期日數) |
| I | FineAmount | 同事可手動填(如果圖書館有計) |
| J | SendToday | Checkbox,預設 TRUE,同事可以剔走(例如見到已還) |
| K | Notes | 同事自由文字,例如「已聯絡家長」 |
| L | Status | 自動:`Not Sent` / `Sent` / `Error` |
| M | LastSentAt | 自動 timestamp |

## Username Lookup

由 `refreshUsernameLookup()` 用 SchooLink `getUsers` 建立(只取 `userTypeID === "320"` 即學生)。

| Col | 欄位 |
|---|---|
| A | SchooLinkUserID |
| B | Username |
| C | UserTypeID |
| D | NameEng |
| E | NameChi |
| F | StudentID(人手對一次,或者用 CHW API 批量對) |
| G | LastSynced |

**未確認事項**:範例入面 username 係 `S13001` 咁嘅格式,睇落似係 `S` + 學生編號,但未證實全校一致。第一次 sync 之後,建議揀 20 個學生人手核對一次先大量發送。

## Send Log(append-only)

| Col | 欄位 |
|---|---|
| A | Timestamp |
| B | StudentID |
| C | Username |
| D | NameEng |
| E | ItemCount |
| F | MessageBodySnapshot |
| G | APIResult(`Success`/`Error`) |
| H | ErrorDetail |

## Config(非機密)

| Key | Value(例子) |
|---|---|
| MESSAGE_TYPE_ID | `640` |
| SCHOOL_SIGNATURE | `聖公會陳融中學圖書館` |

`SchooLinkKey` **唔放呢度** —— 存喺 Apps Script 嘅 Script Properties(Project Settings → Script Properties),只有你（同你畀權限嘅人）先睇到。

## 未確認/要問廠商嘅事

1. `sendNoticeMessage` 嘅成功回應冇返 `messageID`(睇 spec 頁 22-23 個 sample),但 `getMessageReports` 要用 `messageID` 查已讀狀態 —— 要問廠商點樣攞返啱嘅 messageID(可能實際回應有多個欄位冇喺 sample 顯示,要試一次先知)。
2. `username` 同學校自己嘅學生編號嘅對應規則(係咪一定係 `S` + 編號)。
3. 罰款/繳費喺 SchooLink 入面嘅實際 API(呢份 spec 冇提及家長繳費相關 endpoint)。
