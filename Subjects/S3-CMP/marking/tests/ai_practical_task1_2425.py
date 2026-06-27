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

        # (2 marks) No marks if no file found
        if row["filepath"] is None:
            submissions.loc[idx, "marks"] = 0
            submissions.loc[idx, "comments"] = "找不到檔案，沒有分數\n"
            continue
        else:
            submissions.loc[idx, "comments"] = "[O]: 正確地上傳檔案\n"
            submissions.loc[idx, "marks"] += 2
            submissions.loc[idx, "mark0"] = 2

        # (3 分) 加入一個 ImageSprite
        section_description = "加入一個 ImageSprite"
        section_mark = 0
        if (components_util.assert_has_type(components, ["ImageSprite"])):
            section_mark += 1
            if (components_util.assert_has_properties_value(components, "ImageSprite", "$Name", "diamond")):
                section_mark += 0.5
            else:
                remarks += "沒有設定 ImageSprite 的 Name 為 diamond\n"

            if (components_util.assert_has_properties_value(components, "ImageSprite", "Width", "50")):
                section_mark += 0.5
            else:
                remarks += "沒有設定 ImageSprite 的 Width 為 50\n"

            if (components_util.assert_has_properties_value(components, "ImageSprite", "Height", "50")):
                section_mark += 0.5
            else:
                remarks += "沒有設定 ImageSprite 的 Height 為 50\n"

            if (components_util.assert_has_properties_value(components, "ImageSprite", "X", "135")):
                section_mark += 0.5
            else:
                remarks += "沒有設定 ImageSprite 的 X 為 135\n"

            if (components_util.assert_has_properties_value(components, "ImageSprite", "Y", "150")):
                section_mark += 0.5
            else:
                remarks += "沒有設定 ImageSprite 的 Y 為 150\n"

            if (components_util.assert_has_properties_value(components, "ImageSprite", "Picture", "diamond.png")):
                section_mark += 0.5
            else:
                remarks += "沒有設定 ImageSprite 的 Picture 為 diamond.png\n"
        else:
            remarks += "沒有加入 ImageSprite\n"

        if (section_mark == 4):
            submissions.loc[idx, "marks"] += 3
            submissions.loc[idx, "mark1"] = 3
        elif (section_mark > 1):
            submissions.loc[idx, "marks"] += 2
            submissions.loc[idx, "mark1"] = 2
        elif (section_mark > 0):
            submissions.loc[idx, "marks"] += 1
            submissions.loc[idx, "mark1"] = 1
        else:
            submissions.loc[idx, "mark1"] = 0

        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, submissions.loc[idx, "mark1"], 3)


        # (5 分) 每隔一秒鐘，diamond 的位置會被移到畫布 (sky) 上的隨機位置。
        section_description = "每隔一秒鐘，diamond 的位置會被移到畫布 (sky) 上的隨機位置"
        section_mark = 0
        if (blockly_util.assert_has_component_event(blockly, "Clock", "Timer")):
            section_mark += 1
            event = blockly_util.get_blocks_by_type_and_mutation(blockly_util.get_all_blocks(blockly), "component_event", [
                ("@component_type", "Clock"),
                ("@event_name", "Timer")
            ])[0]

            # Check if ImageSprite is moved to a random position
            set_x_block = blockly_util.get_blocks_by_type_and_mutation(event, "component_set_get", [
                ("@component_type", "ImageSprite"),
                ("@set_or_get", "set"),
                ("@property_name", "X")
            ])
            set_y_block = blockly_util.get_blocks_by_type_and_mutation(event, "component_set_get", [
                ("@component_type", "ImageSprite"),
                ("@set_or_get", "set"),
                ("@property_name", "Y")
            ])
            move_to_block = blockly_util.get_blocks_by_type_and_mutation(event, "component_method", [
                ("@component_type", "ImageSprite"),
                ("@method_name", "MoveTo")
            ])

            if (len(set_x_block) > 0 and len(set_y_block) > 0):
                section_mark += 1

                # Check if both X and Y are set to random positions
                random_x_block = blockly_util.get_blocks_by_type(set_x_block[0], "math_random_int")
                if (len(random_x_block) > 0):
                    section_mark += 1
                    zero_block = blockly_util.get_blocks_by_type(random_x_block[0], "math_number")
                    if (len(zero_block) > 0 and zero_block[0]["field"]["#text"] == "0"):
                        section_mark += 1
                    else:
                        remarks += "找不到 math_random_int 的 0 設定區塊\n"
                    
                else:
                    remarks += "找不到 ImageSprite.X 的設定區塊\n"
                    
                # Check if Y is set to a random position
                random_y_block = blockly_util.get_blocks_by_type(set_y_block[0], "math_random_int")
                if (len(random_y_block) > 0):
                    section_mark += 1
                    zero_block = blockly_util.get_blocks_by_type(random_y_block[0], "math_number")
                    if (len(zero_block) > 0 and zero_block[0]["field"]["#text"] == "0"):
                        section_mark += 1
                    else:
                        remarks += "找不到 math_random_int 的 0 設定區塊\n"
                else:
                    remarks += "找不到 ImageSprite.Y 的設定區塊\n"


            elif (len(move_to_block) > 0):
                section_mark += 1
                random_block = blockly_util.get_blocks_by_type(move_to_block[0], "math_random_int")
                if (len(random_block) > 1):
                    section_mark += 2
                    random_x_block = random_block[0]
                    random_y_block = random_block[1]
                    # check if X is set to a random position
                    zero_block = blockly_util.get_blocks_by_type(random_x_block, "math_number")
                    if (len(zero_block) > 0 and zero_block[0]["field"]["#text"] == "0"):
                        section_mark += 1
                    else:
                        remarks += "找不到 math_random_int 的 0 設定區塊\n"

                    # check if Y is set to a random position
                    zero_block = blockly_util.get_blocks_by_type(random_y_block, "math_number")
                    if (len(zero_block) > 0 and zero_block[0]["field"]["#text"] == "0"):
                        section_mark += 1
                    else:
                        remarks += "找不到 math_random_int 的 0 設定區塊\n"
                        
            else:
                remarks += "找不到 ImageSprite.X 或 ImageSprite.Y 的設定區塊\n"
        else:
            remarks += "沒有加入 Clock.Timer 事件\n"

        if (section_mark >= 5):
            submissions.loc[idx, "marks"] += 5
            submissions.loc[idx, "mark2"] = 5
        elif (section_mark > 1):
            submissions.loc[idx, "marks"] += 3
            submissions.loc[idx, "mark2"] = 3
        elif (section_mark > 0):
            submissions.loc[idx, "marks"] += 1
            submissions.loc[idx, "mark2"] = 1
        else:
            submissions.loc[idx, "mark2"] = 0

        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, submissions.loc[idx, "mark2"], 5)


        # (5 分) 當使用者點擊 (Touched) diamond 時：分數 score 加 1。diamond 即時再移至另一個隨機位置。
        section_description = "當使用者點擊 (Touched) diamond 時：分數 score 加 1。diamond 即時再移至另一個隨機位置。"
        section_mark = 0
        touched_event = blockly_util.get_blocks_by_type_and_mutation(blockly_util.get_all_blocks(blockly), "component_event", [
            ("@component_type", "ImageSprite"),
            ("@event_name", "Touched")
        ])
        touchup_event = blockly_util.get_blocks_by_type_and_mutation(blockly_util.get_all_blocks(blockly), "component_event", [
            ("@component_type", "ImageSprite"),
            ("@event_name", "TouchUp")
        ])
        touchdown_event = blockly_util.get_blocks_by_type_and_mutation(blockly_util.get_all_blocks(blockly), "component_event", [
            ("@component_type", "ImageSprite"),
            ("@event_name", "TouchDown")
        ])

        if (len(touched_event) > 0 or len(touchup_event) > 0 or len(touchdown_event) > 0):
            section_mark += 1
            if (len(touched_event) > 0):
                event = [touched_event[0]]
            elif (len(touchup_event) > 0):
                event = [touchup_event[0]]
            else:
                event = [touchdown_event[0]]

            # Check if score is incremented
            score_block = blockly_util.get_blocks_by_type_and_mutation(event[0], "component_set_get", [
                ("@component_type", "Label"),
                ("@set_or_get", "set"),
                ("@property_name", "Text")
            ])
            if (len(score_block) > 0):
                section_mark += 1
                
                # Check add block
                add_block = blockly_util.get_blocks_by_type(score_block[0], "math_add")
                if (len(add_block) > 0):
                    section_mark += 1
                    
                    # Check Label.Text 
                    label_text_block = blockly_util.get_blocks_by_type_and_mutation(add_block[0], "component_set_get", [
                        ("@component_type", "Label"),
                        ("@set_or_get", "get"),
                        ("@property_name", "Text")
                    ])
                    if (len(label_text_block) > 0):
                        section_mark += 1
                    else:
                        remarks += "沒有找到 Label.Text 的設定區塊\n"

                    # Check 1 block
                    one_block = blockly_util.get_blocks_by_type(add_block[0], "math_number")
                    if (len(one_block) > 0 and one_block[0]["field"]["#text"] == "1"):
                        section_mark += 1
                    else:
                        remarks += "沒有找到 math_add 的 1 設定區塊\n"

                else:
                    remarks += "沒有找到 score 的加法設定區塊\n"
            else:
                remarks += "沒有找到 score 的設定區塊\n"

            # Check if diamond is moved to a random position
            set_x_block = blockly_util.get_blocks_by_type_and_mutation(event[0], "component_set_get", [
                ("@component_type", "ImageSprite"),
                ("@set_or_get", "set"),
                ("@property_name", "X")
            ])
            set_y_block = blockly_util.get_blocks_by_type_and_mutation(event[0], "component_set_get", [
                ("@component_type", "ImageSprite"),
                ("@set_or_get", "set"),
                ("@property_name", "Y")
            ])
            move_to_block = blockly_util.get_blocks_by_type_and_mutation(event[0], "component_method", [
                ("@component_type", "ImageSprite"),
                ("@method_name", "MoveTo")
            ])

            if (len(set_x_block) > 0 and len(set_y_block) > 0):
                section_mark += 1

                # Check if both X and Y are set to random positions
                random_x_block = blockly_util.get_blocks_by_type(set_x_block[0], "math_random_int")
                if (len(random_x_block) > 0):
                    section_mark += 1
                    zero_block = blockly_util.get_blocks_by_type(random_x_block[0], "math_number")
                    if (len(zero_block) > 0 and zero_block[0]["field"]["#text"] == "0"):
                        section_mark += 1
                    else:
                        remarks += "找不到 math_random_int 的 0 設定區塊\n"
                else:
                    remarks += "找不到 ImageSprite.X 的設定區塊\n"
                    
                # Check if Y is set to a random position
                random_y_block = blockly_util.get_blocks_by_type(set_y_block[0], "math_random_int")
                if (len(random_y_block) > 0):
                    section_mark += 1
                    zero_block = blockly_util.get_blocks_by_type(random_y_block[0], "math_number")
                    if (len(zero_block) > 0 and zero_block[0]["field"]["#text"] == "0"):
                        section_mark += 1
                    else:
                        remarks += "找不到 math_random_int 的 0 設定區塊\n"
                else:
                    remarks += "找不到 ImageSprite.Y 的設定區塊\n"


            elif (len(move_to_block) > 0):
                section_mark += 1
                random_block = blockly_util.get_blocks_by_type(move_to_block[0], "math_random_int")
                if (len(random_block) > 1):
                    section_mark += 2
                    random_x_block = random_block[0]
                    random_y_block = random_block[1]
                    # check if X is set to a random position
                    zero_block = blockly_util.get_blocks_by_type(random_x_block, "math_number")
                    if (len(zero_block) > 0 and zero_block[0]["field"]["#text"] == "0"):
                        section_mark += 1
                    else:
                        remarks += "找不到 math_random_int 的 0 設定區塊\n"

                    # check if Y is set to a random position
                    zero_block = blockly_util.get_blocks_by_type(random_y_block, "math_number")
                    if (len(zero_block) > 0 and zero_block[0]["field"]["#text"] == "0"):
                        section_mark += 1
                    else:
                        remarks += "找不到 math_random_int 的 0 設定區塊\n"
            else:
                remarks += "找不到 ImageSprite.X 或 ImageSprite.Y 的設定區塊\n"
        else:
            remarks += "沒有加入 ImageSprite.Touched 事件\n"

        if (section_mark > 8):
            submissions.loc[idx, "marks"] += 5
            submissions.loc[idx, "mark3"] = 5
        elif (section_mark > 3):
            submissions.loc[idx, "marks"] += 3
            submissions.loc[idx, "mark3"] = 3
        elif (section_mark > 0):
            submissions.loc[idx, "marks"] += 1
            submissions.loc[idx, "mark3"] = 1
        else:
            submissions.loc[idx, "mark3"] = 0
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, submissions.loc[idx, "mark3"], 5)

        if (remarks != ""):
            submissions.loc[idx, "comments"] += "\n" + remarks
        else:
            submissions.loc[idx, "comments"] += "\n沒有錯誤"
        print("=========================================")
        print("Marks:", submissions.loc[idx, "marks"])
        print(submissions.loc[idx, "comments"])
        print("=========================================")

    # print submissions if comments not empty
    
    
    return submissions


if __name__ == "__main__":
    submissions = aia_utils.read_teams_aias()
    submissions = test(submissions)
    print(submissions)
    submissions.to_csv("marksheets.csv")
