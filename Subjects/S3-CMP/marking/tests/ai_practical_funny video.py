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

        # (6 分) 當每 0.01 秒計時時：
        #       ◼ 若果時間已經少於或等於 0：
        #           ◆ 停止計時器 (Clock1)。
        #           ◆ 把時間 (Time) 設為 0.00 秒。
        #           ◆ 把按鈕 (ClickMe) 文字改為「開始」 。
        #       ◼ 否則：
        #           ◆ 每次減少時間 (Time) 0.01 秒（即 0.01） 。
        section_description = "當每 0.01 秒計時時：\n"
        section_mark = 0
        if (blockly_util.assert_has_component_event(blockly, "Clock", "Timer")):
            section_mark += 1
            event = blockly_util.get_blocks_by_type_and_mutation(blockly_util.get_all_blocks(blockly), "component_event", [
                ("@component_type", "Clock"),
                ("@event_name", "Timer")
            ])[0]

            # Check IF-block in event is Clock.Timer
            if_block = blockly_util.get_blocks_by_type(event, "controls_if")
            if (len(if_block) > 0):
                section_mark += 1
                if_block = if_block[0]

                # Check condition in IF-block
                condition = blockly_util.get_blocks_by_type(if_block, "math_compare")
                if (len(condition) == 0):
                    condition = blockly_util.get_blocks_by_type(if_block, "logic_compare")

                if (len(condition) > 0):
                    section_mark += 1

                    # Check if Time is less than or equal to 0
                    time_block = blockly_util.get_blocks_by_type_and_mutation(condition[0], "component_set_get", [
                        ("@component_type", "Label"),
                        ("@set_or_get", "get"),
                        ("@property_name", "Text")
                    ])
                    if (len(time_block) > 0):
                        section_mark += 1
                    else:
                        remarks += "在 if 的比較中，沒有找到 Label.Text 的設定區塊"

                    # zero block
                    zero_block = blockly_util.get_blocks_by_type(condition[0], "math_number")
                    if (len(zero_block) > 0 and zero_block[0]["field"]["#text"] == "0"):
                        section_mark += 1
                    else:
                        remarks += "在 if 的比較中，沒有找到 math_number 的 0 設定區塊\n"
                else:
                    remarks += "沒有找到 Clock.Timer 的 IF 區塊\n"


                # Check stop Clock
                stop_clock_block = blockly_util.get_blocks_by_type_and_mutation(event, "component_set_get", [
                    ("@component_type", "Clock"),
                    ("@property_name", "TimerEnabled"),
                    ("@set_or_get", "set")
                ])
                if (len(stop_clock_block) > 0):
                    section_mark += 1

                    # Check if TimerEnabled is set to false
                    false_block = blockly_util.get_blocks_by_type(stop_clock_block[0], "logic_false")
                    if (len(false_block) > 0 and false_block[0]["field"]["#text"] == "FALSE"):
                        section_mark += 1
                    else:
                        remarks += "沒有找到 Clock.TimerEnabled 的 false 設定區塊\n"
                else:
                    remarks += "沒有找到 Clock.TimerEnabled 的設定區塊\n"


                # Check set Time to 0.00
                set_time_blocks = blockly_util.get_blocks_by_type_and_mutation(if_block, "component_set_get", [
                    ("@component_type", "Label"),
                    ("@property_name", "Text"),
                    ("@set_or_get", "set")
                ])
                if (len(set_time_blocks) > 0):
                    section_mark += 1

                    # Check if Text is set to 0.00
                    zero_block = blockly_util.get_blocks_by_type(set_time_blocks, "math_number")
                    if (len(zero_block) > 0 and (zero_block[0]["field"]["#text"] == "0" or zero_block[0]["field"]["#text"] == "0.00")):
                        section_mark += 1
                    else:
                        remarks += "沒有找到 Label.Text 的 0.00 設定區塊\n"
                else:
                    remarks += "沒有找到 Label.Text 的設定區塊2\n"

                # Check set ClickMe text to "開始"
                set_clickme_block = blockly_util.get_blocks_by_type_and_mutation(event, "component_set_get", [
                    ("@component_type", "Button"),
                    ("@property_name", "Text"),
                    ("@set_or_get", "set")
                ])
                if (len(set_clickme_block) > 0):
                    section_mark += 1

                    # Check if Text is set to "開始"
                    start_block = blockly_util.get_blocks_by_type(set_clickme_block[0], "text")
                    if (len(start_block) > 0):
                        section_mark += 1
                    else:
                        remarks += "沒有找到 Button.Text 的 開始 設定區塊\n"
                else:
                    remarks += "沒有找到 Button.Text 的設定區塊\n"


                # Check set Time to Time - 0.01
                set_time_blocks = blockly_util.get_blocks_by_type_and_mutation(if_block, "component_set_get", [
                    ("@component_type", "Label"),
                    ("@property_name", "Text"),
                    ("@set_or_get", "set")
                ])
                if (len(set_time_blocks) > 0):
                    section_mark += 1

                    # Check if Text is set to Time - 0.01
                    time_block = blockly_util.get_blocks_by_type(if_block, "math_subtract")
                    if (len(time_block) > 0):
                        section_mark += 1

                        # Check if Time is set to Label.Text
                        time_label_block = blockly_util.get_blocks_by_type_and_mutation(time_block[0], "component_set_get", [
                            ("@component_type", "Label"),
                            ("@set_or_get", "get"),
                            ("@property_name", "Text")
                        ])
                        if (len(time_label_block) > 0):
                            section_mark += 1

                        else:
                            remarks += "沒有找到 Label.Text 的設定區塊\n"
                    else:
                        remarks += "沒有找到 Label.Text 的減法設定區塊\n"
                else:
                    remarks += "沒有找到 Label.Text 的設定區塊\n"

            else:
                remarks += "沒有找到 Clock.Timer 的 IF 區塊\n"
        else:
            remarks += "沒有加入 Clock.Timer 事件\n"

        if (section_mark >= 6):
            submissions.loc[idx, "marks"] += 6
            submissions.loc[idx, "mark2"] = 6
        elif (section_mark > 3):
            submissions.loc[idx, "marks"] += 4
            submissions.loc[idx, "mark2"] = 4
        elif (section_mark >= 1):
            submissions.loc[idx, "marks"] += 2
            submissions.loc[idx, "mark2"] = 2
        else:
            submissions.loc[idx, "mark2"] = 0

        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, submissions.loc[idx, "mark2"], 6)


        # (7 分) 當玩家按下按鈕 (ClickMe) 時：
        #   ◼ 若果按鈕上寫住的是「開始」：
        #   ◆ 將按鈕 (ClickMe) 文字改為「按我」 。
        #   ◆ 啟動計時器 (Clock1) 。
        #   ◆ 將時間 (Time) 設為 5.00 秒。
        #   ◆ 將分數 (Score) 設為 0。
        #    ◼ 否則（即遊戲進行中）：
        #    ◆ 每按一次，分數 (Score) 加 1 分。
        section_description = "當玩家按下按鈕 (ClickMe) 時注意事項：\n"
        section_mark = 0

        event = blockly_util.get_blocks_by_type_and_mutation(blockly_util.get_all_blocks(blockly), "component_event", [
                ("@component_type", "Button"),
                ("@event_name", "Click")
            ])
        if (event is not None):
            section_mark += 1
            if_block = blockly_util.get_blocks_by_type(event, "controls_if")
            # Check IF-block in event is Button.Click
            if (len(if_block) > 0):
                section_mark += 1
                if_block = if_block[0]

                # Check condition in IF-block
                condition = blockly_util.get_blocks_by_type(if_block, "logic_compare")
                if (len(condition) == 0):
                    condition = blockly_util.get_blocks_by_type(if_block, "math_compare")
                if (len(condition) > 0):
                    section_mark += 1

                    # Check if ClickMe.Text is equal to "開始"
                    clickme_block = blockly_util.get_blocks_by_type_and_mutation(condition[0], "component_set_get", [
                        ("@component_type", "Button"),
                        ("@set_or_get", "get"),
                        ("@property_name", "Text")
                    ])
                    if (len(clickme_block) > 0):
                        section_mark += 1

                    else:
                        remarks += "沒有找到 Button.Text 的設定區塊\n"

                    # Check set ClickMe text to "按我"
                    set_clickme_block = blockly_util.get_blocks_by_type_and_mutation(if_block, "component_set_get", [
                        ("@component_type", "Button"),
                        ("@property_name", "Text"),
                        ("@set_or_get", "set")
                    ])
                    if (len(set_clickme_block) > 0):
                        section_mark += 1

                        # Check if Text is set to "按我"
                        press_me_block = blockly_util.get_blocks_by_type(set_clickme_block[0], "text")
                        if (len(press_me_block) > 0 and press_me_block[0]["field"]["#text"] == "按我"):
                            section_mark += 1
                        else:
                            remarks += "沒有找到 Button.Text 的 按我 設定區塊\n"
                    else:
                        remarks += "沒有找到 Button.Text 的設定區塊\n"

                    # Check start Clock
                    start_clock_block = blockly_util.get_blocks_by_type_and_mutation(if_block, "component_set_get", [
                        ("@component_type", "Clock"),
                        ("@property_name", "TimerEnabled"),
                        ("@set_or_get", "set")
                    ])
                    if (len(start_clock_block) > 0):
                        section_mark += 1

                    else:
                        remarks += "沒有找到 Clock.TimerEnabled 的設定區塊\n"

                    # Check set Time to 5.00
                    set_time_blocks = blockly_util.get_blocks_by_type_and_mutation(if_block, "component_set_get", [
                        ("@component_type", "Label"),
                        ("@property_name", "Text"),
                        ("@set_or_get", "set")
                    ])
                    if (len(set_time_blocks) > 0):
                        section_mark += 1

                    else:
                        remarks += "沒有找到 Label.Text 的設定區塊\n"

                    # Check set Score to 0
                    set_score_block = blockly_util.get_blocks_by_type_and_mutation(if_block, "component_set_get", [
                        ("@component_type", "Label"),
                        ("@property_name", "Text"),
                        ("@set_or_get", "set")
                    ])
                    if (len(set_score_block) > 0):
                        section_mark += 1

                        # Check if Text is set to 0
                        print("set_score_block:", set_score_block)
                        zero_block = blockly_util.get_blocks_by_type(set_score_block, "math_number")
                        if (len(zero_block) > 0 and zero_block[0]["field"]["#text"] == "0"):
                            section_mark += 1
                        else:
                            remarks += "沒有找到 Label.Text 的 0 設定區塊\n"
                    else:
                        remarks += "沒有找到 Label.Text 的設定區塊\n"


                    # Check set Score to Score + 1
                    set_score_blocks = blockly_util.get_blocks_by_type_and_mutation(if_block, "component_set_get", [
                        ("@component_type", "Label"),
                        ("@property_name", "Text"),
                        ("@set_or_get", "set")
                    ])
                    if (len(set_score_blocks) > 0):
                        section_mark += 1

                        # Check if Text is set to Score + 1
                        score_block = blockly_util.get_blocks_by_type(set_score_blocks, "math_add")
                        if (len(score_block) > 0):
                            section_mark += 1

                            # Check if Score is set to Label.Text
                            score_label_block = blockly_util.get_blocks_by_type_and_mutation(score_block[0], "component_set_get", [
                                ("@component_type", "Label"),
                                ("@set_or_get", "get"),
                                ("@property_name", "Text")
                            ])
                            if (len(score_label_block) > 0):
                                section_mark += 1

                                # Check if 1 is added
                                one_block = blockly_util.get_blocks_by_type(score_block[0], "math_number")
                                if (len(one_block) > 0 and one_block[0]["field"]["#text"] == "1"):
                                    section_mark += 1
                                else:
                                    remarks += "沒有找到 math_add 的 1 設定區塊\n"
                            else:
                                remarks += "沒有找到 Label.Text 的設定區塊\n"
                        else:
                            remarks += "沒有找到 Label.Text 的加法設定區塊\n"
                    else:
                        remarks += "沒有找到 Label.Text 的設定區塊\n"

                else:
                    remarks += "沒有找到 Button.Click 的 IF 區塊\n"
            else:
                remarks += "沒有找到 Button.Click 的事件區塊\n"
        else:
            remarks += "沒有加入 Button.Click 事件\n"

        print("section_mark2:", section_mark)
        if (section_mark > 8):
            submissions.loc[idx, "marks"] += 7
            submissions.loc[idx, "mark3"] = 7
        elif (section_mark > 3):
            submissions.loc[idx, "marks"] += 5
            submissions.loc[idx, "mark3"] = 5
        elif (section_mark > 0):
            submissions.loc[idx, "marks"] += 3
            submissions.loc[idx, "mark3"] = 3
        else:
            submissions.loc[idx, "mark3"] = 0
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, submissions.loc[idx, "mark3"], 7)

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
