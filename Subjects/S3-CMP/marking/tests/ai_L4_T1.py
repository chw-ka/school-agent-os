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
                interval = comp.get("TimerInterval", "1000")
                if str(interval).strip() == "10":
                    clock_score = 2
                else:
                    remarks.append(f"Clock 的 TimerInterval 應設為 10，目前為 {interval}。")
                break
        else:
            remarks.append("Game 畫面中未找到 Clock 元件。")
    else:
        remarks.append("Game 畫面中未設定元件。")
    score += clock_score

    # 2️⃣ On Game.Initialize → Set Score=0 and Clock1 Enabled (2 分)
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
                if prop == "Text" and value_block.get("@type") == "math_number" and value_block.get("field", {}).get("#text") == "0":
                    set_score = True
                # Clock1.TimerEnabled ← TRUE
                if comp.lower() == "clock1" and prop == "TimerEnabled" and value_block.get("@type") == "logic_boolean" and value_block.get("field", {}).get("#text") == "TRUE":
                    enable_clock = True
            current = current.get("next", {}).get("block", {})
        if set_score and enable_clock:
            init_score = 2
        else:
            if not set_score:
                remarks.append("Game.Initialize 中應將分數標籤設為 0。")
            if not enable_clock:
                remarks.append("Game.Initialize 中應啟動 Clock1 元件。")
    else:
        remarks.append("未找到 Game 畫面的 Initialize 區塊。")
    score += init_score

    # 3️⃣ On ClickMe Button Click → if Clock1.Enabled then Score += 1 (2 分)
    click_score = 0
    game_blocks = get_blocks("Game")
    
    has_if_control = False
    has_score_increment = False
    
    for block in game_blocks:
        if block.get("@type") == "component_event":
            mutation = block.get("mutation", {})
            event_name = mutation.get("@event_name")
            comp_type = mutation.get("@component_type")
            
            # Looking for Button Click event
            if event_name == "Click" and comp_type == "Button":
                stmt = block.get("statement", {}).get("block", {})
                
                # Check if has if-control block
                if stmt and stmt.get("@type") == "controls_if":
                    has_if_control = True
                    
                    # Check condition - should check if Clock is enabled
                    condition_block = stmt.get("value", {}).get("block", {})
                    checks_clock = False
                    
                    # Direct check: Clock1.TimerEnabled
                    if condition_block and condition_block.get("@type") == "component_set_get":
                        cond_mutation = condition_block.get("mutation", {})
                        if cond_mutation.get("@instance_name", "").lower() == "clock1" and cond_mutation.get("@property_name") == "TimerEnabled":
                            checks_clock = True
                    
                    # Comparison check: Clock1.TimerEnabled == TRUE
                    elif condition_block and condition_block.get("@type") == "math_compare":
                        # Check if comparing Clock1.TimerEnabled
                        comp_values = condition_block.get("value", [])
                        if isinstance(comp_values, list):
                            for val in comp_values:
                                val_block = val.get("block", {})
                                if val_block.get("@type") == "component_set_get":
                                    val_mutation = val_block.get("mutation", {})
                                    if val_mutation.get("@instance_name", "").lower() == "clock1" and val_mutation.get("@property_name") == "TimerEnabled":
                                        checks_clock = True
                                        break
                    
                    # Check statement - should increment score
                    inner_stmt = stmt.get("statement", {}).get("block", {})
                    
                    if inner_stmt and inner_stmt.get("@type") == "component_set_get":
                        inner_mutation = inner_stmt.get("mutation", {})
                        if inner_mutation.get("@property_name") == "Text":
                            # Check if it's adding 1
                            value_block = inner_stmt.get("value", {}).get("block", {})
                            if value_block and value_block.get("@type") == "math_add":
                                has_score_increment = True
                    
                    if checks_clock and has_score_increment:
                        click_score = 2
                        break
                    elif has_if_control or has_score_increment:
                        click_score = 1
                        break
                else:
                    # Check if there's score increment without if-control
                    if stmt and stmt.get("@type") == "component_set_get":
                        stmt_mutation = stmt.get("mutation", {})
                        if stmt_mutation.get("@property_name") == "Text":
                            value_block = stmt.get("value", {}).get("block", {})
                            if value_block and value_block.get("@type") == "math_add":
                                has_score_increment = True
                                click_score = 1
                                break
    
    if click_score == 2:
        pass  # Full marks, no remark needed
    elif click_score == 1:
        if has_if_control and not has_score_increment:
            remarks.append("ClickMe 按鈕有if條件判斷但缺少分數增加邏輯 (+1)")
        elif has_score_increment and not has_if_control:
            remarks.append("ClickMe 按鈕有分數增加但缺少Clock啟動狀態檢查 (+1)")
        else:
            remarks.append("ClickMe 按鈕邏輯部分正確 (+1)")
    else:
        remarks.append("ClickMe 按鈕未能在 Clock 啟動狀態下正確增加分數 (+0)")
    
    score += click_score

    # 4️⃣ Clock1.Timer 減時間／跳 Result 並傳分數 (4 分)
    timer_score = 0
    timer_block = find_block(get_blocks("Game"), block_type="Timer", event="Clock", component="Clock1")
    if timer_block:
        stmt_block = timer_block.get("statement", {}).get("block", {})
        if stmt_block and stmt_block.get("@type") == "controls_if":
            has_gt = has_subtract = has_disable = has_goto_result = False
            
            # Check condition: time > 0
            if_block = stmt_block.get("value", {}).get("block", {})
            if if_block and if_block.get("@type") == "math_compare" and if_block.get("field", {}).get("#text") == "GT":
                has_gt = True

            # Check DO statement: subtract 0.01 from time
            do0 = stmt_block.get("statement", {})
            if isinstance(do0, list):
                do0_blocks = [b.get("block", {}) for b in do0]
            else:
                do0_blocks = [do0.get("block", {})]

            for b in do0_blocks:
                if b and b.get("@type") == "component_set_get" and b.get("mutation", {}).get("@property_name") == "Text":
                    subtract_block = b.get("value", {}).get("block", {})
                    if subtract_block and subtract_block.get("@type") == "math_subtract":
                        # Check if subtracting 0.01
                        right_value = subtract_block.get("value", {})
                        if isinstance(right_value, list) and len(right_value) >= 2:
                            right_block = right_value[1].get("block", {})
                            if right_block and right_block.get("@type") == "math_number":
                                num_value = right_block.get("field", {}).get("#text", "")
                                if num_value in ["0.01", "0.1", "1"]:  # Accept different values
                                    has_subtract = True

            # Check ELSE statement: disable clock and go to Result
            else_stmt = stmt_block.get("statement", {})
            if isinstance(else_stmt, list):
                else_blocks = []
                for s in else_stmt:
                    if s.get("@name") == "ELSE":
                        else_blocks.append(s.get("block", {}))
                else_block = else_blocks[0] if else_blocks else {}
            else:
                else_block = else_stmt if isinstance(else_stmt, dict) and else_stmt.get("@name") == "ELSE" else {}
                if not else_block:
                    else_block = stmt_block.get("statement", {})
                    if isinstance(else_block, dict):
                        else_block = else_block.get("block", {})

            # Traverse else block to find disable and goto
            current = else_block
            while current:
                if current.get("@type") == "component_set_get" and current.get("mutation", {}).get("@property_name") == "TimerEnabled":
                    disable_val = current.get("value", {}).get("block", {})
                    if disable_val and disable_val.get("@type") == "logic_boolean" and disable_val.get("field", {}).get("#text") == "FALSE":
                        has_disable = True
                
                if current.get("@type") == "controls_openAnotherScreenWithStartValue":
                    has_goto_result = True
                
                current = current.get("next", {}).get("block", {})

            if all([has_gt, has_subtract, has_disable, has_goto_result]):
                timer_score = 4
            elif sum([has_gt, has_subtract, has_disable, has_goto_result]) >= 3:
                timer_score = 3
                remarks.append("Clock1.Timer 的邏輯大部分正確，但有部分缺失。")
            elif sum([has_gt, has_subtract, has_disable, has_goto_result]) >= 2:
                timer_score = 2
                remarks.append("Clock1.Timer 的邏輯部分正確。")
            else:
                timer_score = 0
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

        # No marks if no file found
        if row["filepath"] is None:
            submissions.loc[idx, "marks"] = 0
            submissions.loc[idx, "comments"] = "沒有提交檔案 - 0分\n"
            continue

        # Evaluate the AIA content
        try:
            components = json.loads(row["components"])
            blockly = json.loads(row["blockly"])
            section_mark, remarks = evaluate(components, blockly)
            
            submissions.loc[idx, "marks"] += section_mark
            submissions.loc[idx, "comments"] += f"專案評分: {section_mark}/10分\n"
            
            if remarks:
                submissions.loc[idx, "comments"] += "\n詳細評語:\n" + remarks
                
        except Exception as e:
            submissions.loc[idx, "marks"] = 0
            submissions.loc[idx, "comments"] += f"❌ 無法解析AIA檔案: {str(e)}\n"

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
