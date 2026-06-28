import blockly_util as blockly_util
import components_util as components_util
import aia_util as aia_utils
import json

def test(submissions):
    submissions = aia_utils.read_all_aias(submissions)
    for idx, row in submissions.iterrows():
        print("=========================================")
        print(submissions.loc[idx, "class"], submissions.loc[idx, "classnumber"])
        print("=========================================")
        submissions.loc[idx, "marks"] = 0
        submissions.loc[idx, "comments"] = ""
        components = json.loads(row["components"])
        blockly = json.loads(row["blockly"])
        remarks = "[O]: 正確\n[-]: 小錯誤\n[X]: 大錯誤\n\n"

        # （2 分）將專案檔案 (.aia) 上傳至 Teams。
        # auto add 2 marks for all submissions
        if (row['components'] == "{}"):
            submissions.loc[idx, "comments"] += "[X] 將專案檔案 (.aia) 上傳至 Teams。\n"
            submissions.loc[idx, "comments"] += "沒有 .aia 檔案在提交中\n"
            continue

        # (2 marks) Upload the teachable machine image classifier, TMIC, extension into the project.
        section_description = "將TeachableMachineImageClassifier（TMIC）擴展上傳至專案中。"
        section_mark = 0
        if (components_util.assert_has_type(components, ["TeachableMachineImageClassifier"])):
            section_mark += 2
        else:
            remarks += "缺少組件: TeachableMachineImageClassifier\n"
        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark)

        # (2 marks) 創建正確的佈局，包含所有組件：網頁檢視器 (WebViewer)、檢測手勢面板（Label x2）、時鐘 (Clock) 和 TMIC。
        section_description = "創建正確的佈局，包含所有組件：網頁檢視器 (WebViewer)、檢測手勢面板（Label x2）、時鐘 (Clock) 和 TMIC。"
        section_mark = 0
        if (components_util.assert_has_type(components, ["WebViewer"])):
            section_mark += 0.5
        else:
            remarks += "缺少組件: WebViewer\n"
        if (components_util.assert_has_type(components, ["Label"])):
            section_mark += 0.5
        else:
            remarks += "缺少組件: Label\n"
        if (components_util.assert_has_type(components, ["Clock"])):
            section_mark += 0.5
        else:
            remarks += "缺少組件: Clock\n"
        if (components_util.assert_has_type(components, ["TeachableMachineImageClassifier"])):
            section_mark += 0.5
        else:
            remarks += "缺少組件: TeachableMachineImageClassifier\n"
        section_mark = min(section_mark, 2)
        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark)

        # (2 marks) 編程區塊，使 TMIC 每秒進行連續分類。
        section_description = "編程區塊，使 TMIC 每秒進行連續分類。"
        section_mark = 0
        all_blocks = blockly_util.get_all_blocks(blockly)
        event = blockly_util.get_event_block(all_blocks, "Clock", "Timer")
        if (event != None):
            section_mark += 1
            # check TeachableMachineImageClassifier.ClassifyVideoData block
            block = blockly_util.get_blocks(
                event, {"@component_type": "TeachableMachineImageClassifier", "@method_name": "ClassifyVideoData"})
            if (block != None):
                section_mark += 1
            else:
                remarks += "TeachableMachineImageClassifier ClassifyVideoData 積木塊未找到\n"
        else:
            remarks += "Clock Timer 事件未找到\n"
        section_mark = min(section_mark, 2)
        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark)

        # (2 marks) 編程區塊，使手勢標籤在 TMIC 接收到分類時顯示。
        section_description = "編程區塊，使手勢標籤在 TMIC 接收到分類時顯示。"
        section_mark = 0
        # has event for TMIC classification
        event = blockly_util.get_event_block(all_blocks, "TeachableMachineImageClassifier", "GotClassification")
        if (event != None):
            section_mark += 1
            # check the blocks inside the event, should have setting label text
            set_text = blockly_util.get_blocks(event, {"@type": "component_set_get", "mutation": {"@component_type": "Label"}, "@property_name": "Text"})
            if (set_text != None):
                section_mark += 1
            else:
                remarks += "未找到 Label Text 積木塊\n"
        else:
            remarks += "TeachableMachineImageClassifier GotClassification 事件未找到\n"
        section_mark = min(section_mark, 2)
        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark)

        # (2 marks) "上傳專案檔案 (.aia) 至 Teams"
        section_description = "上傳專案檔案 (.aia) 至 Teams"
        section_mark = 2
        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark)

        if (remarks != ""):
            submissions.loc[idx, "comments"] += "\n" + remarks
        print("=========================================")
        print(submissions.loc[idx, "class"], submissions.loc[idx, "classnumber"])
        print(submissions.loc[idx, "comments"])
        print(submissions.loc[idx, "marks"])
        print("=========================================")


    # print submissions if comments not empty
    aia_utils.check_copycat(submissions)
    
    
    return submissions


if __name__ == "__main__":
    submissions = aia_utils.read_teams_aias()
    submissions = test(submissions)
    print(submissions)
    submissions.to_csv("marksheets.csv")