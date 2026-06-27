import json
import aia_util as aia_utils

def evaluate(components, blockly):
    score = 0
    remarks = []

    # 0️⃣ Submission bonus
    if blockly and components:
        score += 2
    else:
        remarks.append("未能檢測到你的 .aia 檔案，請再次上傳。")

    def get_blocks(screen):
        xml = blockly.get(screen, {}).get("xml", {})
        blocks = xml.get("block", [])
        if isinstance(blocks, dict):
            return [blocks]
        return blocks

    # 1️⃣ Screen1: open Game with 3 different numbers (6分)
    passed_values = set()

    for block in get_blocks("Screen1"):
        if block.get("@type") == "component_event" and block.get("mutation", {}).get("@event_name") == "Click":
            action_block = block.get("statement", {}).get("block", {})
            if action_block.get("@type") == "controls_openAnotherScreenWithStartValue":
                values = action_block.get("value", [])
                if not isinstance(values, list):
                    values = [values]
                screen_name = start_value = None
                for val in values:
                    if val["@name"] == "SCREENNAME":
                        screen_name = val["block"]["field"]["#text"]
                    elif val["@name"] == "STARTVALUE":
                        start_value = val["block"]["field"]["#text"]
                if screen_name and screen_name.lower() == "game" and start_value:
                    passed_values.add(start_value)

    if len(passed_values) >= 3:
        score += 3
    else:
        remarks.append("請在 Screen1 中建立三個按鈕，開啟 Game 並傳入三個不同的秒數。")

    # Check if Game receives start value
    game_got_startvalue = False
    for block in get_blocks("Game"):
        if block.get("@type") == "component_event" and block.get("mutation", {}).get("@event_name") == "Initialize":
            inner = block.get("statement", {}).get("block", {})
            if inner.get("@type") == "component_set_get":
                if inner.get("value", {}).get("block", {}).get("@type") == "controls_getStartValue":
                    game_got_startvalue = True

    if game_got_startvalue:
        score += 3
    else:
        remarks.append("Game 畫面未能正確使用傳入的秒數值顯示倒數。")

    # 2️⃣ Quit button (2分)
    found_quit = False
    for block in get_blocks("Screen1"):
        if block.get("@type") == "component_event" and block.get("mutation", {}).get("@event_name") == "Click":
            action_block = block.get("statement", {}).get("block", {})
            if action_block.get("@type") == "controls_closeApplication":
                found_quit = True
                break

    if found_quit:
        score += 2
    else:
        remarks.append("Screen1 的離開按鈕未能正確關閉應用程式。")

    # 3️⃣ Game → Result 傳入 99 (4分)
    game_to_result = False
    for block in get_blocks("Game"):
        if block.get("@type") == "component_event" and block.get("mutation", {}).get("@event_name") == "Click":
            inner = block.get("statement", {}).get("block", {})
            if inner.get("@type") == "controls_openAnotherScreenWithStartValue":
                values = inner.get("value", [])
                if not isinstance(values, list):
                    values = [values]
                screen_name = start_value = None
                for val in values:
                    if val["@name"] == "SCREENNAME":
                        screen_name = val["block"]["field"]["#text"]
                    elif val["@name"] == "STARTVALUE":
                        start_value = val["block"]["field"]["#text"]
                if screen_name and screen_name.lower() == "result" and start_value == "99":
                    game_to_result = True
                    break

    if game_to_result:
        score += 4
    else:
        remarks.append("Game 畫面的按鈕未能跳去 Result 並傳入分數 99。")

    # 4️⃣ Result → Screen1 (2分)
    result_home_button = False
    for block in get_blocks("Result"):
        if block.get("@type") == "component_event" and block.get("mutation", {}).get("@event_name") == "Click":
            inner = block.get("statement", {}).get("block", {})
            if inner.get("@type") == "controls_openAnotherScreen":
                value_block = inner.get("value", {}).get("block", {})
                if value_block.get("field", {}).get("#text", "").lower() == "screen1":
                    result_home_button = True
                    break

    if result_home_button:
        score += 2
    else:
        remarks.append("Result 畫面中的首頁按鈕未能返回 Screen1 畫面。")

    return round(score, 2), "\n".join(remarks)



def test(submissions):
    submissions = aia_utils.read_all_aias(submissions)
    for idx, row in submissions.iterrows():
        print("=========================================")
        print(submissions.loc[idx, "class"], submissions.loc[idx, "classnumber"])
        print("=========================================")
        submissions.loc[idx, "marks"] = 0
        submissions.loc[idx, "comments"] = ""

        # (2 marks) No marks if no file found
        if row["filepath"] is None:
            submissions.loc[idx, "marks"] = 0
            submissions.loc[idx, "comments"] = "No file found in the submission\n"
            continue

        # (1 mark) The python code is runnable
        section_description = "The python code is runnable"
        components = json.loads(row["components"])
        blockly = json.loads(row["blockly"])
        section_mark, remarks = evaluate(components, blockly)

        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark, 5)

        if (remarks != ""):
            submissions.loc[idx, "comments"] += "\n" + remarks

        print("=========================================")
        print("Marks:", submissions.loc[idx, "marks"])
        print(submissions.loc[idx, "comments"])
        print("=========================================")

    return submissions


if __name__ == "__main__":
    submissions = aia_utils.read_teams_aias()
    submissions = test(submissions)
    print(submissions)
    submissions.to_csv("marksheets.csv")