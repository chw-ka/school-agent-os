import json
import aia_util as aia_utils


def evaluate(components, blockly):
    score = 0
    remarks = []

    def get_screen_data(screen_name):
        """Get screen data with case-insensitive fallback"""
        screen_data = components.get(screen_name, {})
        if not screen_data:
            # Try case-insensitive match
            for available_screen in components.keys():
                if available_screen.lower() == screen_name.lower():
                    screen_data = components[available_screen]
                    break
        return screen_data

    def get_blocks(screen):
        # Try exact match first
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

    def find_component_in_tree(components_list, comp_type, comp_name_keywords=None):
        """Recursively find components of a specific type"""
        found_components = []
        
        def check_component(comp):
            comp_type_actual = comp.get("$Type", "")
            comp_name = comp.get("$Name", "").lower()
            
            if comp_type_actual == comp_type:
                if comp_name_keywords:
                    # Check if component name matches keywords
                    matches = any(keyword.lower() in comp_name for keyword in comp_name_keywords)
                    if matches:
                        found_components.append(comp)
                else:
                    found_components.append(comp)
            
            # Check nested components
            if "$Components" in comp:
                for sub_comp in comp["$Components"]:
                    check_component(sub_comp)
        
        for comp in components_list:
            check_component(comp)
        
        return found_components
    
    def get_component_properties(comp):
        """Get component properties, handling both direct and nested structures"""
        if isinstance(comp, dict):
            if "Properties" in comp:
                return comp.get("Properties", {})
            else:
                return comp
        return {}

    # Get Screen1 (most likely the main screen)
    screen1_data = get_screen_data("Screen1")
    if not screen1_data:
        # Try to get any available screen
        if components:
            screen1_data = list(components.values())[0]
            screen_name = list(components.keys())[0]
        else:
            screen1_data = None
            screen_name = None
    else:
        screen_name = "Screen1"

    if not screen1_data or not isinstance(screen1_data, dict) or "Properties" not in screen1_data:
        remarks.append("未找到有效畫面 (+0)")
        return round(score, 2), "\n".join(remarks)

    properties = screen1_data["Properties"]
    components_list = properties.get("$Components", [])

    # 1️⃣ Check for all required components (2 marks)
    layout_score = 0
    has_canvas = False
    has_rocket = False
    has_ufo = False
    has_bullet = False
    label_count = 0
    has_reset_button = False
    
    canvas_component = None
    
    # Check for Canvas
    canvas_components = find_component_in_tree(components_list, "Canvas")
    if canvas_components:
        has_canvas = True
        canvas_component = canvas_components[0]
    
    # Check for ImageSprite components (rocket and UFO) and Ball inside Canvas
    if has_canvas:
        canvas_props = get_component_properties(canvas_component)
        canvas_children = canvas_props.get("$Components", [])
        
        # Find all ImageSprites in Canvas - should have at least 2 (rocket and UFO)
        all_imagesprites = find_component_in_tree(canvas_children, "ImageSprite")
        if len(all_imagesprites) >= 2:
            has_rocket = True
            has_ufo = True
        elif len(all_imagesprites) >= 1:
            # At least one ImageSprite found, assume it's either rocket or UFO
            has_rocket = True
        
        # Find Ball component (bullet) - should be any Ball in Canvas
        bullet_components = find_component_in_tree(canvas_children, "Ball")
        if bullet_components:
            has_bullet = True
    
    # Check for Labels (scoreboard - should have 2)
    label_components = find_component_in_tree(components_list, "Label")
    label_count = len(label_components)
    
    # Check for reset button
    button_components = find_component_in_tree(components_list, "Button", ["reset", "重置", "重設"])
    if button_components:
        has_reset_button = True
    
    required_components = {
        "Canvas": has_canvas,
        "Rocket (ImageSprite)": has_rocket,
        "UFO (ImageSprite)": has_ufo,
        "Bullet (Ball)": has_bullet,
        "Labels (x2)": label_count >= 2,
        "Reset Button": has_reset_button
    }
    
    found_count = sum(required_components.values())
    if found_count == len(required_components):
        layout_score = 2
        remarks.append(f"完整的所有元件佈局 ({found_count}/{len(required_components)}) (+2)")
    elif found_count >= len(required_components) - 1:
        missing = [name for name, found in required_components.items() if not found]
        layout_score = 1
        remarks.append(f"缺少部分元件: {', '.join(missing)} ({found_count}/{len(required_components)}) (+1)")
    else:
        missing = [name for name, found in required_components.items() if not found]
        remarks.append(f"缺少多個元件: {', '.join(missing)} ({found_count}/{len(required_components)}) (+0)")
    
    score += layout_score

    # 2️⃣ Check for images attached to rocket and UFO (2 marks)
    image_score = 0
    
    if has_canvas and canvas_component:
        canvas_props = get_component_properties(canvas_component)
        canvas_children = canvas_props.get("$Components", [])
        
        # Check all ImageSprites in Canvas
        all_imagesprites = find_component_in_tree(canvas_children, "ImageSprite")
        imagesprites_with_images = 0
        
        for imagesprite in all_imagesprites:
            imagesprite_props = get_component_properties(imagesprite)
            picture = imagesprite_props.get("Picture", "")
            if picture and picture.strip() != "":
                imagesprites_with_images += 1
        
        if len(all_imagesprites) >= 2 and imagesprites_with_images >= 2:
            image_score = 2
            remarks.append(f"火箭和UFO都有附加圖像 ({imagesprites_with_images}/{len(all_imagesprites)}) (+2)")
        elif len(all_imagesprites) >= 1 and imagesprites_with_images >= 1:
            image_score = 1
            remarks.append(f"部分ImageSprite缺少圖像 ({imagesprites_with_images}/{len(all_imagesprites)}) (+1)")
        else:
            remarks.append(f"ImageSprite都缺少圖像 ({imagesprites_with_images}/{len(all_imagesprites)}) (+0)")
    else:
        remarks.append("未找到Canvas元件，無法檢查圖像 (+0)")
    
    score += image_score

    # 3️⃣ Check for bullet hide and initial position logic (2 marks)
    bullet_logic_score = 0
    
    if has_bullet and has_rocket:
        # Get blocks from the screen
        screen_blocks = get_blocks(screen_name) if screen_name else []
        
        has_hide_logic = False
        has_x_position = False
        has_y_position = False
        
        # Check for Initialize event that hides bullet and sets position
        for block in screen_blocks:
            if block.get("@type") == "component_event":
                mutation = block.get("mutation", {})
                event_name = mutation.get("@event_name")
                
                # Check for Initialize event (screen initialization)
                if event_name == "Initialize":
                    stmt = block.get("statement", {}).get("block", {})
                    if stmt:
                        # Walk through the statement blocks
                        current = stmt
                        while current:
                            block_type = current.get("@type", "")
                            
                            if block_type == "component_set_get":
                                prop_name = current.get("mutation", {}).get("@property_name", "")
                                comp_instance = current.get("mutation", {}).get("@instance_name", "").lower()
                                comp_type = current.get("mutation", {}).get("@component_type", "")
                                set_or_get = current.get("mutation", {}).get("@set_or_get", "")
                                
                                # Check for hide bullet (Visible = FALSE) on Ball component
                                if prop_name == "Visible" and set_or_get == "set" and comp_type == "Ball":
                                    value_block = current.get("value", {}).get("block", {})
                                    if value_block:
                                        if value_block.get("@type") == "logic_boolean":
                                            # Check field->#text for FALSE
                                            field = value_block.get("field", {})
                                            if isinstance(field, dict):
                                                bool_text = field.get("#text", "")
                                                if bool_text == "FALSE":
                                                    has_hide_logic = True
                                            elif isinstance(field, list):
                                                for f in field:
                                                    if f.get("@name") == "BOOL":
                                                        bool_text = f.get("#text", "")
                                                        if bool_text == "FALSE":
                                                            has_hide_logic = True
                                                            break
                                
                                # Check for setting X position from rocket on Ball component
                                if prop_name == "X" and set_or_get == "set" and comp_type == "Ball":
                                    # Check if value comes from rocket.X
                                    value_block = current.get("value", {}).get("block", {})
                                    if value_block and value_block.get("@type") == "component_set_get":
                                        val_set_get = value_block.get("mutation", {}).get("@set_or_get", "")
                                        val_prop = value_block.get("mutation", {}).get("@property_name", "")
                                        val_inst = value_block.get("mutation", {}).get("@instance_name", "").lower()
                                        val_comp_type = value_block.get("mutation", {}).get("@component_type", "")
                                        if val_set_get == "get" and val_prop == "X" and val_comp_type == "ImageSprite" and "rocket" in val_inst:
                                            has_x_position = True
                                
                                # Check for setting Y position from rocket on Ball component
                                if prop_name == "Y" and set_or_get == "set" and comp_type == "Ball":
                                    # Check if value comes from rocket.Y
                                    value_block = current.get("value", {}).get("block", {})
                                    if value_block and value_block.get("@type") == "component_set_get":
                                        val_set_get = value_block.get("mutation", {}).get("@set_or_get", "")
                                        val_prop = value_block.get("mutation", {}).get("@property_name", "")
                                        val_inst = value_block.get("mutation", {}).get("@instance_name", "").lower()
                                        val_comp_type = value_block.get("mutation", {}).get("@component_type", "")
                                        if val_set_get == "get" and val_prop == "Y" and val_comp_type == "ImageSprite" and "rocket" in val_inst:
                                            has_y_position = True
                            
                            # Move to next block
                            next_block = current.get("next", {}).get("block", {})
                            current = next_block if next_block else None
                            
                            if not current:
                                break
        
        has_position_logic = has_x_position and has_y_position
        
        if has_hide_logic and has_position_logic:
            bullet_logic_score = 2
            remarks.append("子彈隱藏並初始位置設置正確 (+2)")
        elif has_hide_logic or has_position_logic:
            missing = []
            if not has_hide_logic:
                missing.append("隱藏")
            if not has_position_logic:
                missing.append("初始位置")
            bullet_logic_score = 1
            remarks.append(f"子彈邏輯不完整: 缺少{', '.join(missing)} (+1)")
        else:
            remarks.append("子彈缺少隱藏和初始位置邏輯 (+0)")
    else:
        remarks.append("未找到子彈或火箭元件，無法檢查邏輯 (+0)")
    
    score += bullet_logic_score

    # 4️⃣ Check for rocket drag movement logic (2 marks)
    drag_score = 0
    
    if has_rocket:
        screen_blocks = get_blocks(screen_name) if screen_name else []
        
        has_drag_logic = False
        
        # Look for Dragged event handler on rocket
        for block in screen_blocks:
            if block.get("@type") == "component_event":
                mutation = block.get("mutation", {})
                event_name = mutation.get("@event_name", "")
                instance_name = mutation.get("@instance_name", "").lower()
                component_type = mutation.get("@component_type", "")
                
                # Check for Dragged event on ImageSprite (rocket)
                if event_name == "Dragged" and component_type == "ImageSprite":
                    stmt = block.get("statement", {}).get("block", {})
                    if stmt:
                        # Check if it sets X position using drag coordinates
                        current = stmt
                        while current:
                            block_type = current.get("@type", "")
                            
                            # Check for setting X position
                            if block_type == "component_set_get":
                                prop_name = current.get("mutation", {}).get("@property_name", "")
                                comp_instance = current.get("mutation", {}).get("@instance_name", "").lower()
                                
                                if prop_name == "X":
                                    # Check if value uses drag parameter (currentX via lexical_variable_get)
                                    value_block = current.get("value", {}).get("block", {})
                                    if value_block:
                                        val_type = value_block.get("@type", "")
                                        # Check for lexical_variable_get with currentX
                                        if val_type == "lexical_variable_get":
                                            eventparam = value_block.get("mutation", {}).get("eventparam", {})
                                            if isinstance(eventparam, dict):
                                                param_name = eventparam.get("@name", "")
                                                if param_name == "currentX":
                                                    has_drag_logic = True
                                                    break
                                        # Also accept if it sets X position in drag handler (any value)
                                        if comp_instance:
                                            has_drag_logic = True
                                            break
                            
                            next_block = current.get("next", {}).get("block", {})
                            current = next_block if next_block else None
                            if not current:
                                break
                        if has_drag_logic:
                            break
        
        # Also accept if there's any Dragged event on ImageSprite
        if not has_drag_logic:
            for block in screen_blocks:
                if block.get("@type") == "component_event":
                    mutation = block.get("mutation", {})
                    event_name = mutation.get("@event_name", "")
                    component_type = mutation.get("@component_type", "")
                    
                    if event_name == "Dragged" and component_type == "ImageSprite":
                        stmt = block.get("statement", {}).get("block", {})
                        if stmt:
                            # Any logic in drag handler is acceptable
                            has_drag_logic = True
                            break
        
        if has_drag_logic:
            drag_score = 2
            remarks.append("火箭拖動時水平移動邏輯正確 (+2)")
        else:
            remarks.append("火箭缺少拖動移動邏輯 (+0)")
    else:
        remarks.append("未找到火箭元件，無法檢查拖動邏輯 (+0)")
    
    score += drag_score

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
            submissions.loc[idx, "comments"] = "沒有提交檔案 - 0分/10分\n"
            continue

        # Evaluate the AIA content
        try:
            components = json.loads(row["components"])
            blockly = json.loads(row["blockly"])
            section_mark, remarks = evaluate(components, blockly)
            
            submissions.loc[idx, "marks"] += section_mark
            # Add 2 marks for file submission (already checked above)
            submissions.loc[idx, "marks"] += 2
            submissions.loc[idx, "comments"] += f"專案評分: {section_mark}/8分\n"
            submissions.loc[idx, "comments"] += "已上傳專案檔案 (+2)\n"
            submissions.loc[idx, "comments"] += f"總分: {submissions.loc[idx, 'marks']}/10分\n"
            
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
