import json
import aia_util as aia_utils


def evaluate(components, blockly):
    score = 0
    remarks = []

    def get_blocks(screen):
        xml = blockly.get(screen, {}).get("xml", {})
        blocks = xml.get("block", [])
        if isinstance(blocks, dict):
            return [blocks]
        return blocks

    def find_block(blocks, block_type=None, component=None, event=None):
        for block in blocks:
            if block.get("@type") != "component_event":
                continue
            mutation = block.get("mutation", {})
            if block_type and mutation.get("@event_name") != block_type:
                continue
            if event and mutation.get("@component_type") != event:
                continue
            if component and mutation.get("@instance_name") != component:
                continue
            return block
        return None

    # 1️⃣ Check TimerInterval = 10 (2 分)
    clock_score = 0
    game_screen = components.get("Game", {})
    if "$Components" in game_screen.get("Properties", {}):
        for comp in game_screen["Properties"]["$Components"]:
            if comp.get("$Type") == "Clock":
                interval = comp.get("TimerInterval", "")
                if str(interval).strip() == "10":
                    clock_score = 2
                else:
                    remarks.append("Clock1 的 TimerInterval 應設為 10。")
                break
        else:
            remarks.append("Game 畫面中未找到 Clock 元件。")
    else:
        remarks.append("Game 畫面中未設定元件。")
    score += clock_score

    # 2️⃣ On Game.Initialize → Set Score=0 and Clock1 Enabled (4 分)
    init_score = 0
    init_block = find_block(get_blocks("Game"), block_type="Initialize", event="Form", component="Game")
    if init_block:
        stmt = init_block.get("statement", {})
        current = stmt.get("block", {})
        set_score, enable_clock = False, False
        while current:
            if current.get("@type") == "component_set_get":
                mutation = current.get("mutation", {})
                prop = mutation.get("@property_name")
                comp = mutation.get("@instance_name")
                value_block = current.get("value", {}).get("block", {})
                # Score ← 0
                if comp.lower() == "score" and prop == "Text" and value_block.get("@type") == "math_number" and value_block.get("field", {}).get("#text") == "0":
                    set_score = True
                # Clock1.TimerEnabled ← TRUE
                if comp.lower() == "clock1" and prop == "TimerEnabled" and value_block.get("@type") == "logic_boolean" and value_block.get("field", {}).get("#text") == "TRUE":
                    enable_clock = True
            current = current.get("next", {}).get("block", {})
        if set_score and enable_clock:
            init_score = 4
        else:
            if not set_score:
                remarks.append("Game.Initialize 中應將 Score 設為 0。")
            if not enable_clock:
                remarks.append("Game.Initialize 中應啟動 Clock1。")
    else:
        remarks.append("未找到 Game 畫面的 Initialize 區塊。")
    score += init_score

    # 3️⃣ On Click → if Clock1.Enabled then Score += 1 (4 分)
    click_score = 0
    for block in get_blocks("Game"):
        if block.get("@type") == "component_event" and block.get("mutation", {}).get("@event_name") == "Click":
            stmt = block.get("statement", {}).get("block", {})
            if stmt.get("@type") == "controls_if":
                condition_block = stmt.get("value", {}).get("block", {})
                if condition_block.get("@type") == "math_compare":
                    # should be time > 0
                    inner_blocks = stmt.get("statement", {}).get("block", {})
                    if inner_blocks.get("@type") == "component_set_get":
                        if inner_blocks["mutation"]["@instance_name"].lower() == "score":
                            click_score = 4
                            break
    if click_score == 0:
        remarks.append("Click 按鈕未能在 Clock 啟動下增加 Score。")
    score += click_score
    # 4️⃣ Clock1.Timer 減時間／跳 Result 並傳分數 (6 分)
    timer_score = 0
    timer_block = find_block(get_blocks("Game"), block_type="Timer", event="Clock", component="Clock1")
    if timer_block:
        stmt_block = timer_block.get("statement", {}).get("block", {})
        if stmt_block.get("@type") == "controls_if":
            has_gt = has_subtract = has_disable = has_goto_result = False
            if_block = stmt_block.get("value", {}).get("block", {})
            if if_block.get("@type") == "math_compare" and if_block.get("field", {}).get("#text") == "GT":
                has_gt = True

            # ✅ fix: handle if 'statement' is a list
            do0 = stmt_block.get("statement", {})
            if isinstance(do0, list):
                do0_blocks = [b.get("block", {}) for b in do0]
            else:
                do0_blocks = [do0.get("block", {})]

            for b in do0_blocks:
                if b.get("@type") == "component_set_get" and b["mutation"]["@property_name"] == "Text":
                    subtract_block = b.get("value", {}).get("block", {})
                    if subtract_block.get("@type") == "math_subtract":
                        has_subtract = True

            else_stmt = stmt_block.get("statement", {})
            if isinstance(else_stmt, list):
                else_block = next((s.get("block", {}) for s in else_stmt if s.get("@name") == "ELSE"), {})
            else:
                else_block = else_stmt.get("ELSE", {}).get("block", {})

            if else_block.get("@type") == "component_set_get" and else_block["mutation"]["@property_name"] == "TimerEnabled":
                disable_val = else_block.get("value", {}).get("block", {})
                if disable_val.get("@type") == "logic_boolean" and disable_val.get("field", {}).get("#text") == "FALSE":
                    has_disable = True
                next_block = else_block.get("next", {}).get("block", {})
                if next_block.get("@type") == "controls_openAnotherScreenWithStartValue":
                    has_goto_result = True

            if all([has_gt, has_subtract, has_disable, has_goto_result]):
                timer_score = 6
            else:
                remarks.append("Clock1.Timer 的邏輯不完整或出現錯誤。")
    else:
        remarks.append("未找到 Clock1 的 Timer 區塊。")

    score += timer_score


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
