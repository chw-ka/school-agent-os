---
name: school-activity-form
description: >-
  複製並填寫校內/外活動通告申請表（校務處範本 DOCX）。適用於外出活動、比賽、訓練營等需交
  校內外活動申請表、活動通告申請、S: 活動資料夾填表。Use when filling 校內外活動申請表 or
  school activity application form.
---

# 校內外活動申請表

## 觸發

用戶要填 **校內/外活動通告申請表**、外出活動申請、或提供活動資料夾／活動詳情要求產生 DOCX。

## 官方範本（唯讀來源）

```
S:\01_School Administration\11_Useful Forms\校內外活動申請表_20240819.docx
```

**只複製，不修改範本。** 輸出寫入活動資料夾（通常 S: STEAM / 各科 `0_Activities\…`）。

## 工具（必用）

| 步驟 | 指令 |
|------|------|
| 填表 | `python shared-tools/activity-form/fill_activity_form.py <spec.json> --activity-folder "<活動資料夾>"` |
| 從舊表提取 | `python shared-tools/activity-form/extract_activity_spec.py "<已填.docx>" --out "<活動資料夾>/_generation/activity.spec.json"` |

欄位說明見 `shared-tools/activity-form/README.md`；結構範例見 `shared-tools/activity-form/examples/ai_entrepreneur_bootcamp.spec.json`。

## 執行流程

### 1. 確認活動資料夾

例（STEAM）：

```
S:\02_Teaching and Learning\03_Key Learning Areas\STEAM\04_others\{學年}\0_Activities\{YYYY_MM_DD}_活動名稱
```

資料夾內可能有 PDF 海報、舊版申請表、相片——可作填表參考。

### 2. 收集／建立 spec

在 `<活動資料夾>/_generation/activity.spec.json` 撰寫結構化資料。

**優先順序：**

1. 用戶直接提供欄位
2. 同資料夾內 **已填過的申請表** → `extract_activity_spec.py` 提取後修改
3. 活動 PDF／海報／議程 → 補活動名稱、日期、地點、主辦機構、目的

**必填（標 *）：** `department`, `teacher_in_charge`, `notice_teachers`, `activity_name_zh`

**常見預設：**

| 欄位 | 建議 |
|------|------|
| `transport` | 校外比賽多為 `self`（自行前往） |
| `fee` | 校方資助活動用 `subsidized` |
| `dress` | 按季節；7月用 `summer_uniform` |
| `reply` | 外出活動用 `mandatory` |
| `form_updated_date` | 今日 `D/M/YYYY` |
| `meeting_point` | **遠征／跨區**：最近港鐵站，須寫明站名、出口、大堂或地面（見下） |
| `meeting_times` | 比主辦方開始時間 **提早 15–30 分鐘**（點名、轉車、升降機） |
| `dismissal_point` | 通常為 **活動現場**；學生頒獎／活動結束後自行離開 |

### 集合／解散慣例（STEAM 遠征）

跨區或需轉車的活動，**集合在港鐵站**，解散在**活動現場**：

1. **查證集合點**：用 WebSearch 查最近港鐵站及出口，並對照主辦方／會場官網步行指引。
2. **寫清楚三項**：站名、出口編號（如 A2）、**大堂或地面**。
3. **深層車站**（如香港大學站）：大堂在 **C層（地庫）**；A2 出口升降機通往 **校園上層地面**——集合宜寫 **大堂 A2 升降機大堂**，勿與出口地面層混淆。
4. **集合時間**：主辦方「進場／報到」時間再 **提早 15–30 分鐘**。
5. **解散**：寫活動場地全名；備註可加「頒獎禮後於現場解散、自行離開」。

**例（HKU Innovation Wing）：**

| 欄位 | 內容 |
|------|------|
| 集合地點 | 港鐵港島綫香港大學站大堂（地庫C層）A2出口升降機大堂 |
| 集合時間 | 08:45（主辦進場 09:00） |
| 活動地點 | 香港大學許愛周科學大樓地下 Tam Wing Fan Innovation Wing One |
| 解散地點 | 同上（現場） |
| 依據 | [Innovation Wing 官網](https://innowings.engg.hku.hk/innowing1/contact/)：由 HKU 站 **A2** 出口前往；港鐵 A2 連接本部校園上層 |

缺資料時向用戶確認，**勿猜學生名單**。

### 3. 執行填表

```bash
python shared-tools/activity-form/fill_activity_form.py "<活動資料夾>/_generation/activity.spec.json" --activity-folder "<活動資料夾>"
```

預設檔名：`校內外活動申請表_{YYYYMM}.docx`；spec 內可設 `output_basename` 覆寫。

### 4. 覆核

打開產出的 DOCX，檢查：

- [ ] 活動名稱、日期、地點
- [ ] 集合／解散時間與地點
- [ ] 參加人數與 P.2 學生名單一致
- [ ] 出通告／交回條日期
- [ ] 負責老師簽署欄（健康狀況）留空供手簽

## Spec 模板（複製修改）

```json
{
  "activity_folder": "S:\\...\\0_Activities\\YYYY_MM_DD_活動名稱",
  "output_basename": "校內外活動申請表_YYYYMM",
  "form_updated_date": "26/6/2026",
  "department": "STEAM",
  "teacher_in_charge": "老師姓名縮寫",
  "notice_teachers": "老師姓名縮寫",
  "activity_name_zh": "活動中文名稱",
  "organizer_zh": "主辦機構",
  "purpose": "活動目的（一至三段）",
  "activity_dates": "D/M/YYYY",
  "venue": "活動地點（全名＋樓層）",
  "meeting_point": "港鐵○○站大堂（C層）○出口升降機大堂",
  "dismissal_point": "活動現場（同 venue 或簡稱）",
  "meeting_times": "D/M/YYYY  HH:MM（較主辦開始提早15–30分鐘）",
  "dismissal_times": "D/M/YYYY  HH:MM（頒獎禮後，現場解散）",
  "transport": "self",
  "participant_count": 0,
  "fee": "subsidized",
  "dress": "winter_uniform",
  "reply": "mandatory",
  "notice_issue": "M月D日",
  "reply_slip": "M月D日",
  "notes": "",
  "students": [
    {"class": "3A", "number": "1", "name": "姓名"}
  ]
}
```

選項值：`transport` → `self`|`coach`|`other`；`fee` → `free`|`subsidized`|`per_student`；`dress` → `summer_uniform`|`winter_uniform`|`sports`|`casual`|`team`|`other`。

任意欄位可用 `*_text` 覆寫（如 `transport_text`）以完全自訂表格內文。

## 私隱與存放

- 含真實學生姓名的 `activity.spec.json` **勿 commit 入 git**；只放 S: 活動資料夾 `_generation/`。
- 範本在 `S:\01_School Administration\`；**勿寫入**該目錄，只讀複製。
- 同一活動多次申請（訓練日／決賽）→ 不同 `output_basename`（例：`校內外活動申請表_202509`、`校內外活動申請表_總決賽`）。

## 範例

**活動資料夾：**

`S:\02_Teaching and Learning\03_Key Learning Areas\STEAM\04_others\2025-2026\0_Activities\2026_04_11_港澳校際AI普通話創業家大賽`

可從內有 `校內外活動申請表_202509.docx` 提取 spec，再改日期／階段（訓練營 vs 決賽）後重新填表。

Git 內匿名範例：`shared-tools/activity-form/examples/ai_entrepreneur_bootcamp.spec.json`
