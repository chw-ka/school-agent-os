import json
import blockly_util as blockly_util
import components_util as components_util
import aia_util as aia_utils


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

        # (2 marks) 將預設佈局更改為橫向（Landscape）。
        section_description = "將預設佈局更改為橫向（Landscape）。"
        section_mark = 0
        if (components_util.assert_has_properties_value(components, "Form", "ScreenOrientation", "landscape")):
            section_mark += 2
        else:
            remarks += "沒有將預設佈局更改為橫向（Landscape）\n"
        section_mark = min(section_mark, 2)
        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark)

        # (6 marks) 在遊戲佈局中加入公園（Canvas）、狗（ImageSprite）和球（Ball）等元件。
        section_description = "在遊戲佈局中加入公園（Canvas）、狗（ImageSprite）和球（Ball）等元件。"
        section_mark = 0
        if (components_util.assert_has_type(components, ["Canvas"])):
            section_mark += 0.5
            if (components_util.assert_has_renamed_type(components, "Canvas")):
                section_mark += 0.5
            else:
                remarks += "Canvas 沒有重新命名\n"
        else:
            remarks += "Canvas 沒有找到\n"

        if (components_util.assert_has_type(components, ["ImageSprite"])):
            section_mark += 0.5
            num = components_util.get_number_of_renamed_type(components, "ImageSprite")
            if (num > 0):
                section_mark += num * 0.5
            else:
                remarks += "ImageSprite 沒有重新命名\n"
        else:
            remarks += "ImageSprite 沒有找到\n"

        if (components_util.assert_has_type(components, ["Ball"])):
            section_mark += 0.5
            num = components_util.get_number_of_renamed_type(components, "Ball")
            if (num > 0):
                section_mark += num * 0.5
            else:
                remarks += "Ball 沒有重新命名\n"
        else:
            remarks += "Ball 沒有找到\n"
        
        if (components_util.assert_has_type(components, ["Canvas"])):
            section_mark += 0.5
            if (components_util.assert_has_renamed_type(components, "Canvas")):
                section_mark += 0.5
            else:
                remarks += "Canvas 沒有重新命名\n"
        else:
            remarks += "Canvas 沒有找到\n"
        
        if (components_util.assert_has_type(components, ["Button"])):
            section_mark += 0.5
            if (components_util.assert_has_renamed_type(components, "Button")):
                section_mark += 0.5
            else:
                remarks += "Button 沒有重新命名\n"
        else:
            remarks += "Button 沒有找到\n"
        
        if (components_util.assert_has_type(components, ["WebViewer"])):
            section_mark += 1
        else:
            remarks += "WebViewer 沒有找到\n"

        if (components_util.assert_has_type(components, ["Label"])):
            section_mark += 0.5
            count = components_util.get_number_of_type(components, "Label")
            if (count >= 4):
                section_mark += 0.5
            else:
                remarks += "有一些 Label 沒有找到\n"
            section_mark += 1
        else:
            remarks += "Labels 沒有找到\n"

        section_mark = min(section_mark, 6)
        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark)

        # (2 marks) 上傳專案檔案 (.aia) 至 Teams
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
