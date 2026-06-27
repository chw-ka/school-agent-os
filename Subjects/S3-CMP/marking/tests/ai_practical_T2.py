import json
import components_util as components_util
import aia_util as aia_utils


def find_component_by_name(components, component_name):
    """Find a component by name (case-insensitive)"""
    for screen_name in components:
        form = components[screen_name].get("Properties", {})
        result = _search_component_by_name(form, component_name)
        if result:
            return result
    return None


def _search_component_by_name(component, target_name):
    """Recursively search for a component by name (case-insensitive)"""
    comp_name = component.get("$Name", "")
    if comp_name.lower() == target_name.lower():
        return component
    
    if "$Components" in component:
        for subcomponent in component["$Components"]:
            result = _search_component_by_name(subcomponent, target_name)
            if result:
                return result
    
    return None


def get_blocks(screen, blockly):
    """Get blocks from a screen"""
    if screen in blockly:
        xml = blockly[screen].get("xml", {})
    else:
        # Try case-insensitive match
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
    """Find an event block matching the criteria"""
    for block in blocks:
        if block.get("@type") == "component_event":
            mutation = block.get("mutation", {})
            
            match = True
            if component_type and mutation.get("@component_type") != component_type:
                match = False
            if event_name and mutation.get("@event_name") != event_name:
                match = False
            if instance_name and mutation.get("@instance_name", "").lower() != instance_name.lower():
                match = False
            
            if match:
                return block
    return None


def evaluate(components, blockly):
    """Evaluate the practical assessment task 2"""
    score = 0
    remarks = []

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
        Handles both:
        - statement: { "@name": "DO", "block": {...} }
        - statement: [ { "@name": "DO0", "block": {...}}, { "@name": "DO1", "block": {...}} ]
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

    def find_math_random_int(block_node):
        """Return True if any nested block is a math_random_int."""
        for b in iter_nested_blocks(block_node):
            if b.get("@type") == "math_random_int":
                return True
        return False
    
    # Get screen name (usually Screen1)
    screen_name = None
    for name in components.keys():
        screen_name = name
        break
    
    if not screen_name:
        remarks.append("未找到畫面")
        return round(score, 2), "\n".join(remarks)
    
    # 1️⃣ File upload check (1 mark) - handled in test() function
    
    # 2️⃣ Check for HorizontalArrangement (1 mark)
    arrangement_score = 0
    all_arrangements = components_util.get_all_components_by_type(components, "HorizontalArrangement")
    if all_arrangements:
        arrangement_score = 1
        remarks.append("✅ 已加入水平配置 (+1)")
    else:
        remarks.append("❌ 未找到水平配置 (+0)")
    
    score += arrangement_score
    
    # 3️⃣ Check for two labels with specified names and properties (4 marks)
    labels_score = 0
    
    label1 = find_component_by_name(components, "label1")
    score_label = find_component_by_name(components, "score")
    
    if label1:
        text = label1.get("Text", "")
        if text == "分數：" or text == "分數:":
            labels_score += 2
            remarks.append("✅ label1 文字正確 (+2)")
        else:
            remarks.append(f"❌ label1 文字應設為 '分數：'，目前為 '{text}' (+0)")
    else:
        remarks.append("❌ 未找到 label1 元件 (+0)")
    
    if score_label:
        text = score_label.get("Text", "")
        if text == "100":
            labels_score += 2
            remarks.append("✅ score 文字正確 (+2)")
        else:
            remarks.append(f"❌ score 文字應設為 '100'，目前為 '{text}' (+0)")
    else:
        remarks.append("❌ 未找到 score 元件 (+0)")
    
    score += labels_score
    
    # 4️⃣ Check Clock1.Timer block (6 marks)
    clock_timer_score = 0
    
    # Check Clock component TimerInterval = 500 (0.5 seconds)
    clock1 = find_component_by_name(components, "Clock1")
    if clock1:
        interval = clock1.get("TimerInterval", "")
        if str(interval) == "500":
            clock_timer_score += 2
            remarks.append("✅ Clock1 TimerInterval 設為 0.5 秒 (500ms) (+2)")
        else:
            remarks.append(f"❌ Clock1 TimerInterval 應設為 500 (0.5秒)，目前為 {interval} (+0)")
    else:
        remarks.append("❌ 未找到 Clock1 元件 (+0)")
    
    # Check Clock1.Timer event block
    screen_blocks = get_blocks(screen_name, blockly) if screen_name else []
    timer_block = find_event_block(screen_blocks, "Clock", "Timer", "Clock1")
    
    if timer_block:
        stmt_roots = get_event_statement_roots(timer_block)
        if stmt_roots:
            has_x_random = False
            has_y_random = False
            has_radius_random = False

            # Scan all nested blocks under all statement roots (covers DO0/DO1 list and nested math_subtract)
            for root in stmt_roots:
                for b in iter_nested_blocks(root):
                    if b.get("@type") != "component_set_get":
                        continue
                    mut = b.get("mutation", {})
                    if mut.get("@component_type") != "Ball":
                        continue
                    if mut.get("@set_or_get") != "set":
                        continue
                    if mut.get("@instance_name", "").lower() != "ball1":
                        continue

                    prop_name = mut.get("@property_name", "")
                    value_block = b.get("value", {}).get("block", {})

                    if prop_name in ("X", "Y"):
                        # Accept math_random_int even if nested (e.g., random_int TO uses math_subtract)
                        if find_math_random_int(value_block):
                            if prop_name == "X":
                                has_x_random = True
                            else:
                                has_y_random = True

                    if prop_name == "Radius":
                        if isinstance(value_block, dict) and value_block.get("@type") == "math_random_int":
                            from_val = None
                            to_val = None
                            vlist = value_block.get("value", [])
                            if isinstance(vlist, list):
                                for val_item in vlist:
                                    if val_item.get("@name") == "FROM":
                                        from_block = val_item.get("block", {})
                                        field = from_block.get("field", {}) if isinstance(from_block, dict) else {}
                                        if isinstance(field, dict):
                                            from_val = field.get("#text", "")
                                    elif val_item.get("@name") == "TO":
                                        to_block = val_item.get("block", {})
                                        field = to_block.get("field", {}) if isinstance(to_block, dict) else {}
                                        if isinstance(field, dict):
                                            to_val = field.get("#text", "")
                            if from_val == "5" and to_val == "20":
                                has_radius_random = True
            
            if has_x_random and has_y_random:
                clock_timer_score += 2
                remarks.append("✅ ball1 位置設為隨機位置 (+2)")
            else:
                missing = []
                if not has_x_random:
                    missing.append("X")
                if not has_y_random:
                    missing.append("Y")
                remarks.append(f"❌ ball1 缺少隨機位置設定: {', '.join(missing)} (+0)")
            
            if has_radius_random:
                clock_timer_score += 2
                remarks.append("✅ ball1 半徑設為 5-20 隨機整數 (+2)")
            else:
                remarks.append("❌ ball1 半徑未設為 5-20 隨機整數 (+0)")
    else:
        remarks.append("❌ 未找到 Clock1.Timer 事件 (+0)")
    
    score += clock_timer_score
    
    # 5️⃣ Check ball1.Touched block (4 marks)
    ball_touched_score = 0
    
    ball_touched_block = find_event_block(screen_blocks, "Ball", "Touched", "ball1")
    
    if ball_touched_block:
        stmt_roots = get_event_statement_roots(ball_touched_block)
        if stmt_roots:
            has_increase = False
            uses_radius = False

            for root in stmt_roots:
                for b in iter_nested_blocks(root):
                    if b.get("@type") != "component_set_get":
                        continue
                    mut = b.get("mutation", {})
                    if mut.get("@component_type") != "Label":
                        continue
                    if mut.get("@set_or_get") != "set":
                        continue
                    if mut.get("@instance_name", "").lower() != "score":
                        continue
                    if mut.get("@property_name") != "Text":
                        continue

                    value_block = b.get("value", {}).get("block", {})
                    if not isinstance(value_block, dict):
                        continue

                    if value_block.get("@type") == "math_add":
                        has_increase = True
                        vlist = value_block.get("value", [])
                        has_score_get = False
                        has_radius_get = False
                        if isinstance(vlist, list):
                            for val_item in vlist:
                                if not str(val_item.get("@name", "")).startswith("NUM"):
                                    continue
                                vb = val_item.get("block", {})
                                if vb.get("@type") != "component_set_get":
                                    continue
                                vm = vb.get("mutation", {})
                                if vm.get("@set_or_get") != "get":
                                    continue
                                if vm.get("@component_type") == "Label" and vm.get("@instance_name", "").lower() == "score" and vm.get("@property_name") == "Text":
                                    has_score_get = True
                                if vm.get("@component_type") == "Ball" and vm.get("@instance_name", "").lower() == "ball1" and vm.get("@property_name") == "Radius":
                                    has_radius_get = True
                        if has_score_get and has_radius_get:
                            uses_radius = True
            
            if has_increase:
                ball_touched_score += 2
                remarks.append("✅ ball1.Touched 事件已加入 (+2)")
            else:
                remarks.append("❌ ball1.Touched 未正確增加分數 (+0)")
            
            if uses_radius:
                ball_touched_score += 2
                remarks.append("✅ 分數增加 ball1.半徑 (+2)")
            else:
                remarks.append("❌ 分數未使用 ball1.半徑 (+0)")
    else:
        remarks.append("❌ 未找到 ball1.Touched 事件 (+0)")
    
    score += ball_touched_score
    
    # 6️⃣ Check Canvas1.Touched block (4 marks)
    canvas_touched_score = 0
    
    # Find canvas component (might be named "畫布1" or "Canvas1")
    canvas1 = None
    all_canvases = components_util.get_all_components_by_type(components, "Canvas")
    if all_canvases:
        # Try to find one that might be canvas1
        for canvas in all_canvases:
            name = canvas.get("$Name", "")
            if "畫布" in name or name.lower() == "canvas1":
                canvas1 = canvas
                break
        if not canvas1:
            canvas1 = all_canvases[0]  # Use first canvas if found
    
    canvas_name = canvas1.get("$Name", "") if canvas1 else None
    
    if canvas_name:
        canvas_touched_block = find_event_block(screen_blocks, "Canvas", "Touched", canvas_name)
        
        if canvas_touched_block:
            stmt_roots = get_event_statement_roots(canvas_touched_block)
            if stmt_roots:
                has_decrease = False
                uses_radius = False

                for root in stmt_roots:
                    for b in iter_nested_blocks(root):
                        if b.get("@type") != "component_set_get":
                            continue
                        mut = b.get("mutation", {})
                        if mut.get("@component_type") != "Label":
                            continue
                        if mut.get("@set_or_get") != "set":
                            continue
                        if mut.get("@instance_name", "").lower() != "score":
                            continue
                        if mut.get("@property_name") != "Text":
                            continue

                        value_block = b.get("value", {}).get("block", {})
                        if not isinstance(value_block, dict):
                            continue
                        if value_block.get("@type") == "math_subtract":
                            has_decrease = True
                            vlist = value_block.get("value", [])
                            has_score_get = False
                            has_radius_get = False
                            if isinstance(vlist, list):
                                for val_item in vlist:
                                    if val_item.get("@name") not in ("A", "B"):
                                        continue
                                    vb = val_item.get("block", {})
                                    if vb.get("@type") != "component_set_get":
                                        continue
                                    vm = vb.get("mutation", {})
                                    if vm.get("@set_or_get") != "get":
                                        continue
                                    if vm.get("@component_type") == "Label" and vm.get("@instance_name", "").lower() == "score" and vm.get("@property_name") == "Text":
                                        has_score_get = True
                                    if vm.get("@component_type") == "Ball" and vm.get("@instance_name", "").lower() == "ball1" and vm.get("@property_name") == "Radius":
                                        has_radius_get = True
                            if has_score_get and has_radius_get:
                                uses_radius = True
                
                if has_decrease:
                    canvas_touched_score += 2
                    remarks.append(f"✅ {canvas_name}.Touched 事件已加入 (+2)")
                else:
                    remarks.append(f"❌ {canvas_name}.Touched 未正確減少分數 (+0)")
                
                if uses_radius:
                    canvas_touched_score += 2
                    remarks.append("✅ 分數減少 ball1.半徑 (+2)")
                else:
                    remarks.append("❌ 分數未使用 ball1.半徑 (+0)")
        else:
            remarks.append(f"❌ 未找到 {canvas_name}.Touched 事件 (+0)")
    else:
        remarks.append("❌ 未找到畫布元件 (+0)")
    
    score += canvas_touched_score
    
    # Add summary of marks breakdown
    remarks.append(f"\n📊 評分明細：水平配置 {arrangement_score}/1 + 標籤 {labels_score}/4 + 計時器 {clock_timer_score}/6 + 球觸碰 {ball_touched_score}/4 + 畫布觸碰 {canvas_touched_score}/4 = {score}/19 分（不含檔案上傳）")
    
    return round(score, 2), "\n".join(remarks)


def test(submissions):
    submissions = aia_utils.read_all_aias(submissions)
    for idx, row in submissions.iterrows():
        print("=========================================")
        print(submissions.loc[idx, "class"], submissions.loc[idx, "classnumber"])
        print("=========================================")
        submissions.loc[idx, "marks"] = 0
        submissions.loc[idx, "comments"] = ""

        # 1️⃣ File upload check (1 mark)
        if row["filepath"] is None:
            submissions.loc[idx, "marks"] = 0
            submissions.loc[idx, "comments"] = "❌ 沒有提交檔案 - 0分/20分"
            continue
        else:
            submissions.loc[idx, "marks"] += 1
            file_upload_feedback = "✅ 正確地上傳檔案 (+1)"

        # Evaluate the AIA content
        try:
            components = json.loads(row["components"])
            blockly = json.loads(row["blockly"])
            section_mark, remarks = evaluate(components, blockly)
            
            submissions.loc[idx, "marks"] += section_mark
            total_marks = submissions.loc[idx, "marks"]
            
            # Format overall feedback with grade
            if total_marks >= 18:
                overall_feedback = f"✅ 優秀！總分 {total_marks}/20"
            elif total_marks >= 15:
                overall_feedback = f"✅ 良好！總分 {total_marks}/20"
            elif total_marks >= 12:
                overall_feedback = f"⚠️ 基本合格！總分 {total_marks}/20"
            elif total_marks >= 8:
                overall_feedback = f"❌ 需要改進！總分 {total_marks}/20"
            else:
                overall_feedback = f"❌ 不及格！總分 {total_marks}/20"
            
            # Combine all feedback items with | separator
            all_feedback = [file_upload_feedback]
            if remarks:
                # Split remarks by newline and filter out empty lines
                remark_lines = [r.strip() for r in remarks.split("\n") if r.strip()]
                all_feedback.extend(remark_lines)
            
            detailed_feedback = " | ".join(all_feedback)
            submissions.loc[idx, "comments"] = f"{overall_feedback} | {detailed_feedback}"
                
        except Exception as e:
            submissions.loc[idx, "marks"] = 1  # Still get file upload mark
            submissions.loc[idx, "comments"] = f"❌ 不及格！總分 1/20 | ✅ 正確地上傳檔案 (+1) | ❌ 無法解析AIA檔案: {str(e)} (+0)"

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
