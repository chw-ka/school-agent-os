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

        # (6 分) 加入以下程式積木：
#   ➢ 當畫面載入時：
#   ◼ 設定足球 (football) 垂直位置為球場 (pitch) 的底部，水平位置為隨機整數由 0 至球場 (pitch) 的闊度
#   ◼ 設定足球 (football) 向右移動，並起始速度為 4 至 10 的隨機整數。設定足球
#   ◼ 設定守門員 (keeper) 向右移動，並起始速度為 5。
        section_description = "當畫面載入時注意事項：\n"
        section_mark = 0
        if (blockly_util.assert_has_component_event(blockly, "Form", "Initialize")):
            section_mark += 1
            event = blockly_util.get_blocks_by_type_and_mutation(blockly_util.get_all_blocks(blockly), "component_event", [
                ("@component_type", "Form"),
                ("@event_name", "Initialize")
            ])[0]
            
            # Check football headings
            football_heading = blockly_util.get_blocks_by_type_and_mutation(event, "component_set_get", [
                ("@component_type", "Ball"),
                ("@property_name", "Heading"),
                ("@set_or_get", "set")
            ])
            if (len(football_heading) > 0):
                section_mark += 1
                # Check if Heading is set to 0
                heading_value = blockly_util.get_blocks_by_type(football_heading[0], "math_number")
                if (len(heading_value) > 0 and heading_value[0]["field"]["#text"] == "90"):
                    section_mark += 1
                else:
                    remarks += "沒有找到 Ball.Heading 的 90 設定區塊\n"
            else:
                remarks += "沒有找到 Ball.Heading 的設定區塊\n"

            # Check football speed random between 4 and 10
            football_speed = blockly_util.get_blocks_by_type_and_mutation(event, "component_set_get", [
                ("@component_type", "Ball"),
                ("@property_name", "Speed"),
                ("@set_or_get", "set")
            ])
            if (len(football_speed) > 0):
                section_mark += 1
                # Check if Speed is set to random integer between 4 and 10
                speed_value = blockly_util.get_blocks_by_type(football_speed[0], "math_random_int")
                if (len(speed_value) > 0):
                    section_mark += 1
                    # Check if min is 4 and max is 10
                    values = blockly_util.get_blocks_by_type(speed_value[0], "math_number")
                    min_value = values[0]
                    if (len(values) > 1 and min_value["field"]["#text"] == "4"):
                        section_mark += 1
                    else:
                        remarks += "沒有找到 math_random_int 的最小值 4 設定區塊\n"

                    max_value = values[1]
                    if (len(values) > 1 and max_value["field"]["#text"] == "10"):
                        section_mark += 1
                    else:
                        remarks += "沒有找到 math_random_int 的最大值 10 設定區塊\n"
                else:
                    remarks += "沒有找到 Ball.Speed 的隨機整數設定區塊\n"
            else:
                remarks += "沒有找到 Ball.Speed 的設定區塊\n"


            # Check football X is random between 0 and pitch width
            football_x = blockly_util.get_blocks_by_type_and_mutation(event, "component_set_get", [
                ("@component_type", "Ball"),
                ("@property_name", "X"),
                ("@set_or_get", "set")
            ])
            if (len(football_x) > 0):
                section_mark += 1
                # Check if X is set to random integer between 0 and pitch width
                x_value = blockly_util.get_blocks_by_type(football_x[0], "math_random_int")
                if (len(x_value) > 0):
                    section_mark += 1
                    # Check if min is 0
                    values = blockly_util.get_blocks_by_type(x_value[0], "math_number")
                    if (len(values) >= 2):
                        min_value = values[0]
                        if (len(values) > 1 and min_value["field"]["#text"] == "0"):
                            section_mark += 1
                        else:
                            remarks += "沒有找到 math_random_int 的最小值 0 設定區塊\n"

                        # Check if max is pitch width
                        max_value = values[1]
                        pitch_width_block = blockly_util.get_blocks_by_type_and_mutation(football_x[0], "component_set_get", [
                            ("@component_type", "Canvas"),
                            ("@property_name", "Width"),
                            ("@set_or_get", "get")
                        ])
                        if (len(pitch_width_block) > 0):
                            section_mark += 1
                        else:
                            remarks += "沒有找到 Canvas.Width 的設定區塊\n"
                    elif (len(values) == 1):
                        section_mark += 1
                        min_value = values[0]
                        if (len(values) > 1 and min_value["field"]["#text"] == "0"):
                            section_mark += 1
                        else:
                            remarks += "沒有找到 math_random_int 的最小值 0 設定區塊\n"
                    else:
                        remarks += "沒有找到 math_random_int 的最小值 0 和最大值的設定區塊\n"

                else:
                    remarks += "沒有找到 Ball.X 的隨機整數設定區塊\n"
            else:
                remarks += "沒有找到 Ball.X 的設定區塊\n"


            # Check keeper heading is set to 0
            keeper_heading = blockly_util.get_blocks_by_type_and_mutation(event, "component_set_get", [
                ("@component_type", "ImageSprite"),
                ("@property_name", "Heading"),
                ("@set_or_get", "set")
            ])
            if (len(keeper_heading) > 0):
                section_mark += 1
                # Check if Heading is set to 0
                heading_value = blockly_util.get_blocks_by_type(keeper_heading[0], "math_number")
                if (len(heading_value) > 0 and heading_value[0]["field"]["#text"] == "0"):
                    section_mark += 1
                else:
                    remarks += "沒有找到 ImageSprite.Heading 的 0 設定區塊\n"
            else:
                remarks += "沒有找到 ImageSprite.Heading 的設定區塊\n"

            # Check keeper speed is set to 5
            keeper_speed = blockly_util.get_blocks_by_type_and_mutation(event, "component_set_get", [
                ("@component_type", "ImageSprite"),
                ("@property_name", "Speed"),
                ("@set_or_get", "set")
            ])
            if (len(keeper_speed) > 0):
                section_mark += 1
                # Check if Speed is set to 5
                speed_value = blockly_util.get_blocks_by_type(keeper_speed[0], "math_number")
                if (len(speed_value) > 0 and speed_value[0]["field"]["#text"] == "5"):
                    section_mark += 1
                else:
                    remarks += "沒有找到 ImageSprite.Speed 的 5 設定區塊\n"
            else:
                remarks += "沒有找到 ImageSprite.Speed 的設定區塊\n"
        else:
            remarks += "沒有加入 Form.Initialize 事件\n"

        if (section_mark >= 10):
            submissions.loc[idx, "marks"] += 5
            submissions.loc[idx, "mark1"] = 5
        elif (section_mark > 4):
            submissions.loc[idx, "marks"] += 3
            submissions.loc[idx, "mark1"] = 3
        elif (section_mark >= 1):
            submissions.loc[idx, "marks"] += 1
            submissions.loc[idx, "mark1"] = 1
        else:
            submissions.loc[idx, "mark1"] = 0

        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, submissions.loc[idx, "mark1"], 5)

        # (3 分) 當每 1 秒計時時，呼叫 AI 模型 (tmic) 進行影像辨識
        section_description = "每 1 秒計時時呼叫 AI 模型進行影像辨識：\n"
        section_mark = 0
        if (blockly_util.assert_has_component_event(blockly, "Clock", "Timer")):
            section_mark += 1
            event = blockly_util.get_blocks_by_type_and_mutation(blockly_util.get_all_blocks(blockly), "component_event", [
                ("@component_type", "Clock"),
                ("@event_name", "Timer")
            ])[0]

            # Check if AI model is called
            ai_model_call = blockly_util.get_blocks_by_type_and_mutation(event, "component_method", [
                ("@component_type", "TeachableMachineImageClassifier"),
                ("@method_name", "ClassifyVideoData")
            ])
            if (len(ai_model_call) > 0):
                section_mark += 1
            else:
                remarks += "沒有找到 AI 模型呼叫區塊\n"
        else:
            remarks += "沒有加入 Clock.Timer 事件\n"

        if (section_mark >= 2):
            submissions.loc[idx, "marks"] += 3
            submissions.loc[idx, "mark2"] = 3
        elif (section_mark >= 1):
            submissions.loc[idx, "marks"] += 1
            submissions.loc[idx, "mark2"] = 1
        else:
            submissions.loc[idx, "mark2"] = 0
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, submissions.loc[idx, "mark2"], 3)

        # (5 分) 當足球 (football) 與其他物件碰撞時
        section_description = "當足球與其他物件碰撞時注意事項：\n"
        section_mark = 0
        if (blockly_util.assert_has_component_event(blockly, "Ball", "CollidedWith")):
            section_mark += 1
            event = blockly_util.get_blocks_by_type_and_mutation(blockly_util.get_all_blocks(blockly), "component_event", [
                ("@component_type", "Ball"),
                ("@event_name", "CollidedWith")
            ])[0]

            # Check if-block in the event
            if_block = blockly_util.get_blocks_by_type(event, "controls_if")
            if (len(if_block) > 0):
                section_mark += 1
                # Check if the condition is a collision with ImageSprite
                get_other_block = blockly_util.get_blocks_by_type(if_block, "lexical_variable_get")
                if (len(get_other_block) > 0):
                    section_mark += 1
                else:
                    remarks += "沒有找到碰撞物件的變數區塊\n"
                # Check if the condition is a collision with ImageSprite keeper
                keeper_block = blockly_util.get_blocks_by_type_and_mutation(if_block, "component_component_block", [
                    ("@component_type", "ImageSprite"),
                    ("@instance_name", "keeper")
                ])
                if (len(keeper_block) > 0):
                    section_mark += 1
                else:
                    remarks += "沒有找到 ImageSprite.keeper 的碰撞區塊\n"
                # Check if the condition is a collision with ImageSprite goal
                goal_block = blockly_util.get_blocks_by_type_and_mutation(if_block, "component_component_block", [
                    ("@component_type", "ImageSprite"),
                    ("@instance_name", "goal")
                ])
                if (len(goal_block) > 0):
                    section_mark += 1
                else:
                    remarks += "沒有找到 ImageSprite.goal 的碰撞區塊\n"
            else:
                remarks += "沒有找到 if 區塊\n"

            # Check if set homescore increment
            homescore_block = blockly_util.get_blocks_by_type_and_mutation(event, "component_set_get", [
                ("@component_type", "Label"),
                ("@property_name", "Text"),
                ("@set_or_get", "set"),
                ("@instance_name", "homeScore")
            ])
            if (len(homescore_block) > 0):
                section_mark += 1
                # Check if the text is set to homescore + 1
                add_block = blockly_util.get_blocks_by_type(homescore_block[0], "math_addition")
                if (len(add_block) > 0):
                    section_mark += 1
                    get_homescore_block = blockly_util.get_blocks_by_type_and_mutation(add_block[0], "component_set_get", [
                        ("@component_type", "Label"),
                        ("@property_name", "Text"),
                        ("@set_or_get", "get"),
                        ("@instance_name", "homeScore")
                    ])
                    if (len(get_homescore_block) > 0):
                        section_mark += 1
                    else:
                        remarks += "沒有找到 Label.homeScore 的取得區塊\n"

                    one_block = blockly_util.get_blocks_by_type(add_block[0], "math_number")
                    if (len(one_block) > 0 and one_block[0]["field"]["#text"] == "1"):
                        section_mark += 1
                    else:
                        remarks += "沒有找到數字 1 的設定區塊\n"

                # Check if the text is set to awayscore + 1
                awayscore_block = blockly_util.get_blocks_by_type_and_mutation(event, "component_set_get", [
                    ("@component_type", "Label"),
                    ("@property_name", "Text"),
                    ("@set_or_get", "set"),
                    ("@instance_name", "awayScore")
                ])
                if (len(awayscore_block) > 0):
                    section_mark += 1
                    # Check if the text is set to awayscore + 1
                    add_block = blockly_util.get_blocks_by_type(awayscore_block[0], "math_addition")
                    if (len(add_block) > 0):
                        section_mark += 1
                        get_awayscore_block = blockly_util.get_blocks_by_type_and_mutation(add_block[0], "component_set_get", [
                            ("@component_type", "Label"),
                            ("@property_name", "Text"),
                            ("@set_or_get", "get"),
                            ("@instance_name", "awayScore")
                        ])
                        if (len(get_awayscore_block) > 0):
                            section_mark += 1
                        else:
                            remarks += "沒有找到 Label.awayScore 的取得區塊\n"

                        one_block = blockly_util.get_blocks_by_type(add_block[0], "math_number")
                        if (len(one_block) > 0 and one_block[0]["field"]["#text"] == "1"):
                            section_mark += 1
                        else:
                            remarks += "沒有找到數字 1 的設定區塊\n"
                    else:
                        remarks += "沒有找到 Label.awayScore 的加法區塊\n"
                else:
                    remarks += "沒有找到 Label.awayScore 的設定區塊\n"
            else:
                remarks += "沒有找到 Label.homeScore 的設定區塊\n"

            # 重新設定足球 (football) 速度為 4 至 10 的隨機整數。
            football_speed = blockly_util.get_blocks_by_type_and_mutation(event, "component_set_get", [
                ("@component_type", "Ball"),
                ("@property_name", "Speed"),
                ("@set_or_get", "set")
            ])
            if (len(football_speed) > 0):
                section_mark += 1
                # Check if Speed is set to random integer between 4 and 10
                speed_value = blockly_util.get_blocks_by_type(football_speed[0], "math_random_int")
                if (len(speed_value) > 0):
                    section_mark += 1
                    # Check if min is 4 and max is 10
                    values = blockly_util.get_blocks_by_type(speed_value[0], "math_number")
                    if (len(values) >= 2):
                        min_value = values[0]
                        if (len(values) > 1 and min_value["field"]["#text"] == "4"):
                            section_mark += 1
                        else:
                            remarks += "沒有找到 math_random_int 的最小值 4 設定區塊\n"

                        max_value = values[1]
                        if (len(values) > 1 and max_value["field"]["#text"] == "10"):
                            section_mark += 1
                        else:
                            remarks += "沒有找到 math_random_int 的最大值 10 設定區塊\n"
                    elif (len(values) == 1):
                        section_mark += 1
                        min_value = values[0]
                        if (len(values) > 1 and min_value["field"]["#text"] == "4"):
                            section_mark += 1
                        else:
                            remarks += "沒有找到 math_random_int 的最小值 4 設定區塊\n"
                    else:
                        remarks += "沒有找到 math_random_int 的最小值 4 和最大值的設定區塊\n"
                else:
                    remarks += "沒有找到 Ball.Speed 的隨機整數設定區塊\n"
            else:
                remarks += "沒有找到 Ball.Speed 的設定區塊\n"

        # 重新設定足球 (football) 垂直位置為球場 (pitch) 的底部，水平位置為隨機整數由 0 至球場 (pitch) 的闊度。
        set_x_block = blockly_util.get_blocks_by_type_and_mutation(event, "component_set_get", [
            ("@component_type", "Ball"),
            ("@property_name", "X"),
            ("@set_or_get", "set")
        ])
        if (len(set_x_block) > 0):
            section_mark += 1
            # Check if X is set to random integer between 0 and pitch width
            x_value = blockly_util.get_blocks_by_type(set_x_block[0], "math_random_int")
            if (len(x_value) > 0):
                section_mark += 1
                # Check if min is 0
                values = blockly_util.get_blocks_by_type(x_value[0], "math_number")
                if (len(values) >= 2):
                    min_value = values[0]
                    if (len(values) > 1 and min_value["field"]["#text"] == "0"):
                        section_mark += 1
                    else:
                        remarks += "沒有找到 math_random_int 的最小值 0 設定區塊\n"

                    # Check if max is pitch width
                    max_value = values[1]
                    pitch_width_block = blockly_util.get_blocks_by_type_and_mutation(set_x_block[0], "component_set_get", [
                        ("@component_type", "Canvas"),
                        ("@property_name", "Width"),
                        ("@set_or_get", "get")
                    ])
                    if (len(pitch_width_block) > 0):
                        section_mark += 1
                    else:
                        remarks += "沒有找到 Canvas.Width 的設定區塊\n"
                elif (len(values) == 1):
                    section_mark += 1
                    min_value = values[0]
                    if (len(values) > 1 and min_value["field"]["#text"] == "0"):
                        section_mark += 1
                    else:
                        remarks += "沒有找到 math_random_int 的最小值 0 設定區塊\n"
                else:
                    remarks += "沒有找到 math_random_int 的最小值 0 和最大值的設定區塊\n"

            else:
                remarks += "沒有找到 Ball.X 的隨機整數設定區塊\n"
        else:
            remarks += "沒有找到 Ball.X 的設定區塊\n"

        # 重新設定足球 (football) 垂直位置為球場 (pitch) 的底部
        set_y_block = blockly_util.get_blocks_by_type_and_mutation(event, "component_set_get", [
            ("@component_type", "Ball"),
            ("@property_name", "Y"),
            ("@set_or_get", "set")
        ])
        if (len(set_y_block) > 0):
            section_mark += 1
            # Check if Y is set to pitch height
            y_value = blockly_util.get_blocks_by_type(set_y_block[0], "component_set_get")
            if (len(y_value) > 0):
                section_mark += 1
                # Check if Y is set to pitch height
                pitch_height_block = blockly_util.get_blocks_by_type_and_mutation(set_y_block[0], "component_set_get", [
                    ("@component_type", "Canvas"),
                    ("@property_name", "Height"),
                    ("@set_or_get", "get")
                ])
                if (len(pitch_height_block) > 0):
                    section_mark += 1
                else:
                    remarks += "沒有找到 Canvas.Height 的設定區塊\n"
            else:
                remarks += "沒有找到 Ball.Y 的設定區塊\n"
        else:
            remarks += "沒有找到 Ball.Y 的設定區塊\n"
        if (section_mark >= 8):
            submissions.loc[idx, "marks"] += 5
            submissions.loc[idx, "mark3"] = 5
        elif (section_mark >= 4):
            submissions.loc[idx, "marks"] += 3
            submissions.loc[idx, "mark3"] = 3
        elif (section_mark >= 1):
            submissions.loc[idx, "marks"] += 1
            submissions.loc[idx, "mark3"] = 1
        else:
            submissions.loc[idx, "mark3"] = 0
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, submissions.loc[idx, "mark3"], 5)

        # (5 分) 當 AI 模型 (tmic) 回傳結果時
        section_description = "當 AI 模型回傳結果時注意事項：\n"
        section_mark = 0
        if (blockly_util.assert_has_component_event(blockly, "TeachableMachineImageClassifier", "GotClassification")):
            section_mark += 1
            event = blockly_util.get_blocks_by_type_and_mutation(blockly_util.get_all_blocks(blockly), "component_event", [
                ("@component_type", "TeachableMachineImageClassifier"),
                ("@event_name", "GotClassification")
            ])

            if_block = blockly_util.get_blocks_by_type_and_mutation(event, "controls_if", [])
            if (len(if_block) > 0):
                section_mark += 1
                if (blockly_util.match_blocks_subset(if_block[0], {
                    "value": {
                        "@name": "IF0",
                        "block": {
                            "field": {
                                "@name": "OP",
                                "#text": "GT"
                            },
                        }
                    }
                })) or (blockly_util.match_blocks_subset(if_block[0], {
                    "value": {
                        "@name": "IF0",
                        "block": {
                            "field": {
                                "@name": "OP",
                                "#text": "LT"
                            },
                        }
                    }
                })) or (blockly_util.match_blocks_subset(if_block[0], {
                    "value": {
                        "@name": "IF0",
                        "block": {
                            "field": {
                                "@name": "OP",
                                "#text": "LTE"
                            },
                        }
                    }
                })) or (blockly_util.match_blocks_subset(if_block[0], {
                    "value": {
                        "@name": "IF0",
                        "block": {
                            "field": {
                                "@name": "OP",
                                "#text": "GTE"
                            },
                        }
                    }
                })):
                    section_mark += 1
                    lookup_blocks = blockly_util.get_blocks_by_type_and_mutation(if_block[0], "dictionaries_lookup", [])
                    if (len(lookup_blocks) > 1):
                        section_mark += 1
                        texts = blockly_util.get_blocks_by_type_and_mutation(lookup_blocks[0], "text", [])
                        if (len(texts) > 0 and texts[0]["field"]["#text"] == "Left" or texts[0]["field"]["#text"] == "Right"):
                            section_mark += 1
                        texts = blockly_util.get_blocks_by_type_and_mutation(lookup_blocks[1], "text", [])
                        if (len(texts) > 0 and texts[0]["field"]["#text"] == "Left" or texts[0]["field"]["#text"] == "Right"):
                            section_mark += 1
                        results_blocks = blockly_util.get_blocks_by_type_and_mutation(lookup_blocks[0], "lexical_variable_get", [
                            ("eventparam", {"@name": "result"})
                        ])
                        if (len(results_blocks) > 0):
                            section_mark += 1
                        results_blocks = blockly_util.get_blocks_by_type_and_mutation(lookup_blocks[1], "lexical_variable_get", [
                            ("eventparam", {"@name": "result"})
                        ])
                        if (len(results_blocks) > 0):
                            section_mark += 1

                        set_heading_blocks = blockly_util.get_blocks_by_type_and_mutation(if_block[0], "component_set_get", [
                            ("@component_type", "ImageSprite"), ("@property_name", "Heading")])
                        if (len(set_heading_blocks) > 1):
                            section_mark += 1
                        set_speed_blocks = blockly_util.get_blocks_by_type_and_mutation(if_block[0], "component_set_get", [
                            ("@component_type", "ImageSprite"), ("@property_name", "Speed")])
                        if (len(set_speed_blocks) > 1):
                            section_mark += 1

                    else:
                        remarks += "沒有找到字典查找區塊\n"
                else:
                    remarks += "沒有找到 if 區塊的比較運算符\n"

            else:
                remarks += "沒有找到 if 區塊\n"

        else:
            remarks += "沒有加入 TeachableMachineImageClassifier.GotClassification 事件\n"

        if (section_mark >= 8):
            submissions.loc[idx, "marks"] += 5
            submissions.loc[idx, "mark4"] = 5
        elif (section_mark > 1):
            submissions.loc[idx, "marks"] += 3
            submissions.loc[idx, "mark4"] = 3
        else:
            submissions.loc[idx, "marks"] += section_mark
            submissions.loc[idx, "mark4"] = section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, submissions.loc[idx, "mark4"], 5)


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
