# 校內外活動申請表

從校務處官方範本複製並填寫 **校內/外活動通告申請表**。

## 官方範本

`S:\01_School Administration\11_Useful Forms\校內外活動申請表_20240819.docx`

## CLI

```bash
# 由 JSON spec 產生 DOCX（輸出至活動資料夾）
python shared-tools/activity-form/fill_activity_form.py path/to/activity.spec.json --activity-folder "S:\...\活動資料夾"

# 指定輸出路徑
python shared-tools/activity-form/fill_activity_form.py spec.json --out "S:\...\校內外活動申請表_202604.docx"

# 從已填好的舊表提取 spec（方便複製修改）
python shared-tools/activity-form/extract_activity_spec.py "S:\...\校內外活動申請表_202509.docx" --out _generation/activity.spec.json
```

## Spec 欄位（摘要）

| 欄位 | JSON key | 備註 |
|------|----------|------|
| 校內負責單位 | `department` | |
| 負責老師 | `teacher_in_charge` | |
| 帶隊老師 | `escort_teachers` | 範本有此行才填 |
| 須查看電子通告的老師 | `notice_teachers` | |
| 活動名稱 | `activity_name_zh`, `activity_name_en` | |
| 主辦機構 | `organizer_zh`, `organizer_en` | |
| 活動目的 | `purpose` | |
| 活動日期 | `activity_dates` | |
| 活動地點 | `venue` | |
| 集合/解散 | `meeting_point`, `dismissal_point`, `meeting_times`, `dismissal_times` | 遠征：港鐵站集合（寫明出口＋大堂/地面）；解散在現場；集合時間提早15–30分鐘 |
| 交通工具 | `transport` | `self` / `coach` / `other`；或 `transport_text` |
| 參加人數 | `participant_count` | |
| 費用 | `fee` | `free` / `subsidized` / `per_student`；或 `fee_text` |
| 服飾 | `dress` | 見 spec 範例；或 `dress_text` |
| 回覆 | `reply` | `mandatory` / `optional` |
| 出通告/交回條 | `notice_issue`, `reply_slip` | |
| 備註 | `notes` | |
| 學生名單 | `students` | `[{class, number, name}, …]` 最多 40 人 |

完整範例：`examples/ai_entrepreneur_bootcamp.spec.json`

## 私隱

- `*.spec.json` 含學生姓名時，**勿 commit 入 git**；放活動資料夾 `_generation/` 或 S: 即可。
