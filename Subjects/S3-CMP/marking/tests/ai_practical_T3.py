import json
import aia_util as aia_utils


def get_blocks(screen, blockly):
    """Get blocks from a screen (case-insensitive screen match)."""
    if screen in blockly:
        xml = blockly[screen].get("xml", {})
    else:
        xml = {}
        for available_screen in blockly.keys():
            if available_screen.lower() == screen.lower():
                xml = blockly[available_screen].get("xml", {})
                break

    blocks = xml.get("block", [])
    if isinstance(blocks, dict):
        return [blocks]
    return blocks


def find_event_block(blocks, component_type=None, event_name=None, instance_name=None):
    """Find a component_event block matching the criteria (instance_name case-insensitive)."""
    for block in blocks:
        if block.get("@type") != "component_event":
            continue
        mutation = block.get("mutation", {})
        if component_type and mutation.get("@component_type") != component_type:
            continue
        if event_name and mutation.get("@event_name") != event_name:
            continue
        if instance_name and mutation.get("@instance_name", "").lower() != instance_name.lower():
            continue
        return block
    return None


def iter_nested_blocks(node):
    """Yield all nested Blockly blocks (dicts with '@type') under node."""
    if isinstance(node, dict):
        if "@type" in node:
            yield node
        for v in node.values():
            yield from iter_nested_blocks(v)
    elif isinstance(node, list):
        for item in node:
            yield from iter_nested_blocks(item)


def get_event_statement_roots(event_block):
    """
    Return a list of top-level statement blocks for a component_event.
    Handles:
    - statement: { "@name": "DO", "block": {...} }
    - statement: [ { "@name": "DO0", "block": {...}}, ... ]
    """
    st = event_block.get("statement", {})
    roots = []
    if isinstance(st, dict):
        b = st.get("block")
        if isinstance(b, dict):
            roots.append(b)
    elif isinstance(st, list):
        for s in st:
            if isinstance(s, dict):
                b = s.get("block")
                if isinstance(b, dict):
                    roots.append(b)
    return roots


def _logic_boolean_is_false(block_node):
    """Return True if block is logic_boolean with field BOOL = FALSE."""
    if not isinstance(block_node, dict):
        return False
    if block_node.get("@type") != "logic_boolean":
        return False
    field = block_node.get("field", {})
    if isinstance(field, dict):
        return field.get("#text", "") == "FALSE"
    if isinstance(field, list):
        for f in field:
            if f.get("@name") == "BOOL" and f.get("#text", "") == "FALSE":
                return True
    return False


def _helpers_assets_name(block_node):
    """Return asset filename for helpers_assets block, else None."""
    if not isinstance(block_node, dict):
        return None
    if block_node.get("@type") != "helpers_assets":
        return None
    field = block_node.get("field", {})
    if isinstance(field, dict):
        return field.get("#text")
    if isinstance(field, list):
        for f in field:
            if f.get("@name") == "ASSET":
                return f.get("#text")
    return None


def evaluate(components, blockly):
    """
    Task 3 rubrics (excluding file upload mark):
    - 3 marks: Screen1.Initialize exists, sets Time.Text=5.0, disables Clock1.TimerEnabled
    - 6 marks: Button1.Click exists, IF condition checks Button1.Image == start.png,
               THEN block sets Button1.Image to stop.png and enables Clock1,
               ELSE block sets Button1.Image to start.png and disables Clock1
    Total here: 9 marks; +1 mark for file upload in test()
    """
    score = 0
    remarks = []

    screen_blocks = get_blocks("Screen1", blockly)

    # 1) Screen1.Initialize (3)
    init_score = 0
    init_block = find_event_block(screen_blocks, component_type="Form", event_name="Initialize", instance_name="Screen1")
    if init_block:
        stmt_roots = get_event_statement_roots(init_block)

        set_time_text = False
        disable_clock = False

        for root in stmt_roots:
            for b in iter_nested_blocks(root):
                if b.get("@type") != "component_set_get":
                    continue
                mut = b.get("mutation", {})
                if mut.get("@set_or_get") != "set":
                    continue

                # Time.Text = 5.0
                if (
                    mut.get("@component_type") == "Label"
                    and mut.get("@instance_name", "").lower() == "time"
                    and mut.get("@property_name") == "Text"
                ):
                    vb = b.get("value", {}).get("block", {})
                    if isinstance(vb, dict) and vb.get("@type") == "math_number":
                        field = vb.get("field", {})
                        val = None
                        if isinstance(field, dict):
                            val = field.get("#text")
                        elif isinstance(field, list):
                            for f in field:
                                if f.get("@name") == "NUM":
                                    val = f.get("#text")
                                    break
                        if val == "5.0":
                            set_time_text = True

                # Clock1.TimerEnabled = FALSE
                if (
                    mut.get("@component_type") == "Clock"
                    and mut.get("@instance_name", "").lower() == "clock1"
                    and mut.get("@property_name") == "TimerEnabled"
                ):
                    vb = b.get("value", {}).get("block", {})
                    if _logic_boolean_is_false(vb):
                        disable_clock = True

        init_score += 1  # Event exists
        remarks.append("✅ Screen1.Initialize 事件存在 (+1)")
        
        if set_time_text:
            init_score += 1
            remarks.append("✅ Screen1.Initialize 將 Time.Text 設為 5.0 (+1)")
        else:
            remarks.append("❌ Screen1.Initialize 未將 Time.Text 設為 5.0 (+0)")

        if disable_clock:
            init_score += 1
            remarks.append("✅ Screen1.Initialize 停用 Clock1.TimerEnabled (+1)")
        else:
            remarks.append("❌ Screen1.Initialize 未停用 Clock1.TimerEnabled (+0)")
    else:
        remarks.append("❌ 未找到 Screen1.Initialize (+0)")

    score += init_score

    # 2) Button1.Click (6)
    click_score = 0
    click_block = find_event_block(screen_blocks, component_type="Button", event_name="Click", instance_name="Button1")
    if click_block:

        # Find controls_if
        if_block = None
        for root in get_event_statement_roots(click_block):
            for b in iter_nested_blocks(root):
                if b.get("@type") == "controls_if":
                    if_block = b
                    break
            if if_block:
                break

        if not if_block:
            remarks.append("❌ Button1.Click 未找到 if 區塊 (+0)")
        else:
            # Check if condition: Button1.Image == start.png
            condition_ok = False
            val_if0 = if_block.get("value", {}).get("block", {})
            if isinstance(val_if0, dict) and val_if0.get("@type") in ("math_compare", "logic_compare"):
                # compare expects A and B
                comp_values = val_if0.get("value", [])
                a_block = None
                b_block = None
                if isinstance(comp_values, list):
                    for item in comp_values:
                        if item.get("@name") == "A":
                            a_block = item.get("block", {})
                        elif item.get("@name") == "B":
                            b_block = item.get("block", {})

                # A should be Button1.Image get, B should be helpers_assets (either side acceptable)
                def is_button1_image_get(node):
                    if not isinstance(node, dict):
                        return False
                    if node.get("@type") != "component_set_get":
                        return False
                    mut = node.get("mutation", {})
                    return (
                        mut.get("@component_type") == "Button"
                        and mut.get("@set_or_get") == "get"
                        and mut.get("@instance_name", "").lower() == "button1"
                        and mut.get("@property_name") == "Image"
                    )

                def get_asset_name(node):
                    return _helpers_assets_name(node)

                # Check if condition compares Button1.Image to start.png
                if is_button1_image_get(a_block):
                    asset_name = get_asset_name(b_block)
                    if asset_name == "start.png":
                        condition_ok = True
                elif is_button1_image_get(b_block):
                    asset_name = get_asset_name(a_block)
                    if asset_name == "start.png":
                        condition_ok = True

            if condition_ok:
                click_score += 1
                remarks.append("✅ Button1.Click if 條件檢查 Button1.Image == start.png (+1)")
            else:
                remarks.append("❌ Button1.Click if 條件未檢查 Button1.Image == start.png (+0)")

            # Check THEN and ELSE blocks
            # THEN should set Button1.Image to stop.png and enable Clock1
            # ELSE should set Button1.Image to start.png and disable Clock1
            then_set_stop = False
            then_enable_clock = False
            else_set_start = False
            else_disable_clock = False

            # statements can be list: DO0 ... and ELSE ...
            stmts = if_block.get("statement", [])
            if isinstance(stmts, dict):
                stmts = [stmts]

            for st in stmts:
                if not isinstance(st, dict):
                    continue
                name = st.get("@name", "")
                root = st.get("block", {})
                if not isinstance(root, dict):
                    continue

                for b in iter_nested_blocks(root):
                    if b.get("@type") != "component_set_get":
                        continue
                    mut = b.get("mutation", {})
                    if mut.get("@set_or_get") != "set":
                        continue

                    # Button1.Image set
                    if (
                        mut.get("@component_type") == "Button"
                        and mut.get("@instance_name", "").lower() == "button1"
                        and mut.get("@property_name") == "Image"
                    ):
                        asset = _helpers_assets_name(b.get("value", {}).get("block", {}))
                        if asset:  # Only check if asset was successfully detected
                            if name.startswith("DO"):
                                if asset == "stop.png":
                                    then_set_stop = True
                            if name == "ELSE":
                                if asset == "start.png":
                                    else_set_start = True

                    # Clock1.TimerEnabled set
                    if (
                        mut.get("@component_type") == "Clock"
                        and mut.get("@instance_name", "").lower() == "clock1"
                        and mut.get("@property_name") == "TimerEnabled"
                    ):
                        vb = b.get("value", {}).get("block", {})
                        if name.startswith("DO"):
                            # Check if enabling (TRUE)
                            if isinstance(vb, dict) and vb.get("@type") == "logic_boolean":
                                field = vb.get("field", {})
                                txt = None
                                if isinstance(field, dict):
                                    txt = field.get("#text")
                                elif isinstance(field, list):
                                    for f in field:
                                        if f.get("@name") == "BOOL":
                                            txt = f.get("#text")
                                            break
                                if txt == "TRUE":
                                    then_enable_clock = True
                            elif isinstance(vb, dict) and vb.get("@type") == "logic_true":
                                then_enable_clock = True
                        if name == "ELSE":
                            # Check if disabling (FALSE)
                            if _logic_boolean_is_false(vb):
                                else_disable_clock = True
                            elif isinstance(vb, dict) and vb.get("@type") == "logic_boolean":
                                field = vb.get("field", {})
                                txt = None
                                if isinstance(field, dict):
                                    txt = field.get("#text")
                                elif isinstance(field, list):
                                    for f in field:
                                        if f.get("@name") == "BOOL":
                                            txt = f.get("#text")
                                            break
                                if txt == "FALSE":
                                    else_disable_clock = True

            # Verify THEN block: should set stop.png and enable clock
            if then_set_stop:
                click_score += 1
                remarks.append("✅ Button1.Click THEN 將 Button1.Image 設為 stop.png (+1)")
            else:
                remarks.append("❌ Button1.Click THEN 未將 Button1.Image 設為 stop.png (+0)")

            if then_enable_clock:
                click_score += 1
                remarks.append("✅ Button1.Click THEN 啟動 Clock1.TimerEnabled (+1)")
            else:
                remarks.append("❌ Button1.Click THEN 未啟動 Clock1.TimerEnabled (+0)")

            # Verify ELSE block: should set start.png and disable clock
            if else_set_start:
                click_score += 1
                remarks.append("✅ Button1.Click ELSE 將 Button1.Image 設為 start.png (+1)")
            else:
                remarks.append("❌ Button1.Click ELSE 未將 Button1.Image 設為 start.png (+0)")

            if else_disable_clock:
                click_score += 1
                remarks.append("✅ Button1.Click ELSE 停用 Clock1.TimerEnabled (+1)")
            else:
                remarks.append("❌ Button1.Click ELSE 未停用 Clock1.TimerEnabled (+0)")
        
        # Add event existence mark at the beginning
        click_score += 1
        remarks.insert(0, "✅ Button1.Click 事件存在 (+1)")
    else:
        remarks.append("❌ 未找到 Button1.Click (+0)")

    score += click_score

    # Add summary of marks breakdown
    remarks.append(f"\n📊 評分明細：Screen1.Initialize {init_score}/3 + Button1.Click {click_score}/6 = {score}/9 分（不含檔案上傳）")

    return round(score, 2), "\n".join(remarks)


def test(submissions):
    submissions = aia_utils.read_all_aias(submissions)
    for idx, row in submissions.iterrows():
        print("=========================================")
        print(submissions.loc[idx, "class"], submissions.loc[idx, "classnumber"])
        print("=========================================")
        submissions.loc[idx, "marks"] = 0
        submissions.loc[idx, "comments"] = ""

        # File upload (1 mark)
        if row["filepath"] is None:
            submissions.loc[idx, "marks"] = 0
            submissions.loc[idx, "comments"] = "❌ 沒有提交檔案 - 0分/10分"
            continue
        else:
            submissions.loc[idx, "marks"] += 1
            file_upload_feedback = "✅ 正確地上傳檔案 (+1)"

        try:
            components = json.loads(row["components"])
            blockly = json.loads(row["blockly"])
            section_mark, remarks = evaluate(components, blockly)

            submissions.loc[idx, "marks"] += section_mark
            total_marks = submissions.loc[idx, "marks"]
            
            # Format overall feedback with grade
            if total_marks >= 9:
                overall_feedback = f"✅ 優秀！總分 {total_marks}/10"
            elif total_marks >= 7:
                overall_feedback = f"✅ 良好！總分 {total_marks}/10"
            elif total_marks >= 5:
                overall_feedback = f"⚠️ 基本合格！總分 {total_marks}/10"
            elif total_marks >= 3:
                overall_feedback = f"❌ 需要改進！總分 {total_marks}/10"
            else:
                overall_feedback = f"❌ 不及格！總分 {total_marks}/10"
            
            # Combine all feedback items with | separator
            all_feedback = [file_upload_feedback]
            if remarks:
                # Split remarks by newline and filter out empty lines
                remark_lines = [r.strip() for r in remarks.split("\n") if r.strip()]
                all_feedback.extend(remark_lines)
            
            detailed_feedback = " | ".join(all_feedback)
            submissions.loc[idx, "comments"] = f"{overall_feedback} | {detailed_feedback}"
        except Exception as e:
            submissions.loc[idx, "marks"] = 1
            submissions.loc[idx, "comments"] = f"❌ 不及格！總分 1/10 | ✅ 正確地上傳檔案 (+1) | ❌ 無法解析AIA檔案: {str(e)} (+0)"

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

