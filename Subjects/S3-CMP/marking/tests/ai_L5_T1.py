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

    def has_background_image(screen_data):
        """Check if screen has background image set"""
        # Handle different data structures
        if isinstance(screen_data, dict):
            if "Properties" in screen_data:
                properties = screen_data.get("Properties", {})
                background_image = properties.get("BackgroundImage", "")
                return background_image and background_image.strip() != ""
            else:
                # Direct properties access
                background_image = screen_data.get("BackgroundImage", "")
                return background_image and background_image.strip() != ""
        return False

    def has_button_image(button_data):
        """Check if button has custom image"""
        # Handle different data structures
        if isinstance(button_data, dict):
            if "Properties" in button_data:
                properties = button_data.get("Properties", {})
                image = properties.get("Image", "")
                return image and image.strip() != ""
            else:
                # Direct properties access
                image = button_data.get("Image", "")
                return image and image.strip() != ""
        return False

    # 1️⃣ Check for 3 screens (5 marks)
    screens_score = 0
    required_screens = ["Screen1", "Game", "Result"]
    found_screens = []
    
    # Check for exact matches first
    for screen_name in required_screens:
        if screen_name in components:
            found_screens.append(screen_name)
    
    # Check for case-insensitive matches for Game and Result
    available_screens = list(components.keys())
    for required_screen in ["Game", "Result"]:
        if required_screen not in found_screens:
            # Look for case-insensitive match
            for available_screen in available_screens:
                if available_screen.lower() == required_screen.lower():
                    found_screens.append(available_screen)
                    break
    
    if len(found_screens) == 3:
        screens_score = 5
        remarks.append("完整的三個畫面 (Screen1、Game、Result) (+5)")
    elif len(found_screens) == 2:
        screens_score = 3
        missing = [s for s in required_screens if s not in found_screens]
        remarks.append(f"缺少畫面: {', '.join(missing)} (+3)")
    elif len(found_screens) == 1:
        screens_score = 1
        missing = [s for s in required_screens if s not in found_screens]
        remarks.append(f"缺少畫面: {', '.join(missing)} (+1)")
    else:
        remarks.append("缺少所有必要畫面 (Screen1、Game、Result) (+0)")
    
    score += screens_score

    # 2️⃣ Check background images for all screens (5 marks)
    background_score = 0
    screens_with_background = 0
    
    for screen_name in found_screens:
        screen_data = get_screen_data(screen_name)
        
        # Handle the actual data structure from AIA files
        if isinstance(screen_data, dict) and "Properties" in screen_data:
            screen_props = screen_data["Properties"]
            background_image = screen_props.get("BackgroundImage", "")
            if background_image and background_image.strip() != "":
                screens_with_background += 1
            else:
                # Check if screen has Image components (alternative to background)
                components_list = screen_props.get("$Components", [])
                has_image_component = False
                
                def check_for_image_components(comp):
                    """Recursively check for Image components"""
                    nonlocal has_image_component
                    if comp.get("$Type") == "Image":
                        has_image_component = True
                        return
                    
                    # Check nested components
                    if "$Components" in comp:
                        for sub_comp in comp["$Components"]:
                            check_for_image_components(sub_comp)
                
                for comp in components_list:
                    check_for_image_components(comp)
                    if has_image_component:
                        break
                
                if has_image_component:
                    screens_with_background += 1
    
    if screens_with_background == len(found_screens) and len(found_screens) >= 2:
        background_score = 5
        remarks.append(f"所有畫面都有背景圖片 ({screens_with_background}/{len(found_screens)}) (+5)")
    elif screens_with_background >= 2:
        background_score = 3
        remarks.append(f"部分畫面缺少背景圖片 ({screens_with_background}/{len(found_screens)}) (+3)")
    elif screens_with_background >= 1:
        background_score = 1
        remarks.append(f"大部分畫面缺少背景圖片 ({screens_with_background}/{len(found_screens)}) (+1)")
    else:
        remarks.append("所有畫面都缺少背景圖片 (+0)")
    
    score += background_score

    # 3️⃣ Check button images (5 marks)
    button_score = 0
    total_buttons = 0
    buttons_with_images = 0
    
    for screen_name in found_screens:
        screen_data = get_screen_data(screen_name)
        if isinstance(screen_data, dict) and "Properties" in screen_data:
            properties = screen_data["Properties"]
            components_list = properties.get("$Components", [])
            
            def check_buttons_recursively(comp):
                """Recursively check for buttons and their customization"""
                nonlocal total_buttons, buttons_with_images
                
                if comp.get("$Type") == "Button":
                    total_buttons += 1
                    # Check for button image
                    button_image = comp.get("Image", "")
                    bg_color = comp.get("BackgroundColor", "")
                    text_color = comp.get("TextColor", "")
                    
                    has_customization = False
                    if button_image and button_image.strip() != "":
                        has_customization = True
                    elif bg_color and bg_color != "&HFF000000":
                        has_customization = True
                    elif text_color and text_color != "&HFF000000":  # Default black text
                        has_customization = True
                    
                    if has_customization:
                        buttons_with_images += 1
                
                # Check nested components
                if "$Components" in comp:
                    for sub_comp in comp["$Components"]:
                        check_buttons_recursively(sub_comp)
            
            for comp in components_list:
                check_buttons_recursively(comp)
    
    if total_buttons > 0:
        if buttons_with_images == total_buttons:
            button_score = 5
            remarks.append(f"所有按鈕都有自訂設計 ({buttons_with_images}/{total_buttons}) (+5)")
        elif buttons_with_images >= total_buttons * 0.5:
            button_score = 3
            remarks.append(f"部分按鈕缺少自訂圖片 ({buttons_with_images}/{total_buttons}) (+3)")
        elif buttons_with_images > 0:
            button_score = 1
            remarks.append(f"大部分按鈕缺少自訂圖片 ({buttons_with_images}/{total_buttons}) (+1)")
        else:
            remarks.append("所有按鈕都缺少自訂圖片 (+0)")
    else:
        remarks.append("未找到任何按鈕元件 (+0)")
    
    score += button_score

    # 4️⃣ Check time limit customization on Screen1 (5 marks)
    time_limit_score = 0
    screen1_data = get_screen_data("Screen1")
    
    if screen1_data and isinstance(screen1_data, dict) and "Properties" in screen1_data:
        properties = screen1_data["Properties"]
        components_list = properties.get("$Components", [])
        
        has_time_input = False
        has_time_label = False
        has_time_buttons = False
        time_button_count = 0
        
        def check_component_for_time_features(comp):
            """Recursively check component and its children for time features"""
            nonlocal time_button_count, has_time_input, has_time_label, has_time_buttons
            comp_type = comp.get("$Type", "")
            comp_name = comp.get("$Name", "").lower()
            comp_text = comp.get("Text", "").lower()
            
            # Check for time-related input components
            if comp_type in ["TextBox", "NumericBox"] and ("time" in comp_name or "limit" in comp_name or "時" in comp_name):
                has_time_input = True
            
            # Check for time-related labels
            if comp_type == "Label" and ("time" in comp_name or "limit" in comp_name or "時" in comp_name or "限" in comp_name or "time" in comp_text.lower() or "sec" in comp_text.lower() or "selection" in comp_text.lower()):
                has_time_label = True
            
            # Check for time selection buttons (any buttons with numbers that could be time values)
            if comp_type == "Button":
                # Look for buttons with numbers that could represent time (5, 10, 15, 20, 30, etc.)
                import re
                numbers = re.findall(r'\d+', comp_text)
                if numbers:
                    time_value = int(numbers[0])
                    # Accept reasonable time values (1-60 seconds)
                    if 1 <= time_value <= 60:
                        time_button_count += 1
                        has_time_buttons = True
            
            # Check nested components (like HorizontalArrangement)
            if "$Components" in comp:
                for sub_comp in comp["$Components"]:
                    check_component_for_time_features(sub_comp)
        
        for comp in components_list:
            check_component_for_time_features(comp)
        
        # Check for time-related blocks in Screen1
        screen1_blocks = get_blocks("Screen1")
        has_time_logic = False
        
        for block in screen1_blocks:
            if block.get("@type") == "component_event":
                mutation = block.get("mutation", {})
                event_name = mutation.get("@event_name")
                
                # Check if there's logic to handle time input
                if event_name in ["Click", "GotFocus", "LostFocus"]:
                    stmt = block.get("statement", {}).get("block", {})
                    if stmt:
                        has_time_logic = True
                        break
        
        # More flexible scoring for time selection
        if time_button_count >= 3:
            time_limit_score = 5
            remarks.append(f"Screen1 有{time_button_count}個時間選擇按鈕 (+5)")
        elif time_button_count >= 2:
            time_limit_score = 4
            remarks.append(f"Screen1 有{time_button_count}個時間選擇按鈕 (+4)")
        elif has_time_buttons or (has_time_input and has_time_label):
            time_limit_score = 3
            remarks.append("Screen1 有時間相關元件但功能不完整 (+3)")
        elif has_time_logic or has_time_input or has_time_label:
            time_limit_score = 1
            remarks.append("Screen1 有時間相關邏輯但缺少完整功能 (+1)")
        else:
            remarks.append("Screen1 缺少時間限制自訂功能 (+0)")
    else:
        remarks.append("未找到 Screen1 畫面 (+0)")
    
    score += time_limit_score

    # 5️⃣ Check counting functionality in Game screen (5 marks)
    counting_score = 0
    game_data = get_screen_data("Game")
    
    if game_data and isinstance(game_data, dict) and "Properties" in game_data:
        properties = game_data["Properties"]
        components_list = properties.get("$Components", [])
        
        has_score_label = False
        has_click_button = False
        
        def check_component_for_counting_features(comp):
            """Recursively check component and its children for counting features"""
            comp_type = comp.get("$Type", "")
            comp_name = comp.get("$Name", "").lower()
            comp_text = comp.get("Text", "").lower()
            
            # Check for score/count display
            if comp_type == "Label" and ("score" in comp_name or "count" in comp_name or "分" in comp_name or "數" in comp_name or "score" in comp_text or "current" in comp_name):
                return "score_label"
            
            # Check for click button
            if comp_type == "Button" and ("click" in comp_name or "按" in comp_name or "click" in comp_text):
                return "click_button"
            
            # Check nested components (like HorizontalArrangement)
            if "$Components" in comp:
                for sub_comp in comp["$Components"]:
                    result = check_component_for_counting_features(sub_comp)
                    if result:
                        return result
            
            return None
        
        for comp in components_list:
            result = check_component_for_counting_features(comp)
            if result == "score_label":
                has_score_label = True
            elif result == "click_button":
                has_click_button = True
        
        # Check for counting logic in Game blocks
        game_blocks = get_blocks("Game")
        has_counting_logic = False
        
        for block in game_blocks:
            if block.get("@type") == "component_event":
                mutation = block.get("mutation", {})
                event_name = mutation.get("@event_name")
                comp_type = mutation.get("@component_type")
                
                if event_name == "Click" and comp_type == "Button":
                    stmt = block.get("statement", {}).get("block", {})
                    if stmt:
                        # Check if it increments a counter
                        current = stmt
                        while current:
                            if current.get("@type") == "component_set_get":
                                prop = current.get("mutation", {}).get("@property_name")
                                if prop == "Text":
                                    value_block = current.get("value", {}).get("block", {})
                                    if value_block and value_block.get("@type") == "math_add":
                                        has_counting_logic = True
                                        break
                            current = current.get("next", {}).get("block", {})
                        if has_counting_logic:
                            break
        
        if has_score_label and has_click_button and has_counting_logic:
            counting_score = 5
            remarks.append("Game 畫面有完整的計數功能 (+5)")
        elif (has_score_label and has_click_button) or (has_counting_logic and (has_score_label or has_click_button)):
            counting_score = 3
            remarks.append("Game 畫面有計數功能但部分元件或邏輯不完整 (+3)")
        elif has_score_label or has_click_button or has_counting_logic:
            counting_score = 1
            remarks.append("Game 畫面有部分計數相關元件但功能不完整 (+1)")
        else:
            remarks.append("Game 畫面缺少計數功能 (+0)")
    else:
        remarks.append("未找到 Game 畫面 (+0)")
    
    score += counting_score

    # 6️⃣ Check result display in Result screen (5 marks)
    result_score = 0
    result_data = get_screen_data("Result")
    
    if result_data and isinstance(result_data, dict) and "Properties" in result_data:
        properties = result_data["Properties"]
        components_list = properties.get("$Components", [])
        
        has_result_label = False
        has_score_display = False
        
        for comp in components_list:
            comp_type = comp.get("$Type", "")
            comp_name = comp.get("$Name", "").lower()
            comp_text = comp.get("Text", "").lower()
            
            # Check for result display
            if comp_type == "Label" and ("result" in comp_name or "score" in comp_name or "final" in comp_name or "結果" in comp_name or "分" in comp_name or "score" in comp_text or "result" in comp_text or "final" in comp_name):
                has_result_label = True
                # Check if it's set to display score
                if comp_text and ("score" in comp_text or "分" in comp_text or "result" in comp_text or "your score" in comp_text):
                    has_score_display = True
        
        # Check for result logic in Result blocks
        result_blocks = get_blocks("Result")
        has_result_logic = False
        
        for block in result_blocks:
            if block.get("@type") == "component_event":
                mutation = block.get("mutation", {})
                event_name = mutation.get("@event_name")
                
                if event_name == "Initialize":
                    stmt = block.get("statement", {}).get("block", {})
                    if stmt:
                        # Check if it sets result display
                        current = stmt
                        while current:
                            if current.get("@type") == "component_set_get":
                                prop = current.get("mutation", {}).get("@property_name")
                                if prop == "Text":
                                    has_result_logic = True
                                    break
                            current = current.get("next", {}).get("block", {})
                        if has_result_logic:
                            break
        
        if has_result_label and has_score_display:
            result_score = 5
            remarks.append("Result 畫面有完整的結果顯示功能 (+5)")
        elif has_result_label and has_result_logic:
            result_score = 3
            remarks.append("Result 畫面有結果顯示但功能不完整 (+3)")
        elif has_result_label or has_result_logic:
            result_score = 1
            remarks.append("Result 畫面有部分結果相關元件但功能不完整 (+1)")
        else:
            remarks.append("Result 畫面缺少結果顯示功能 (+0)")
    else:
        remarks.append("未找到 Result 畫面 (+0)")
    
    score += result_score

    # 7️⃣ Check for bonus creative features (5 marks)
    bonus_score = 0
    creative_features = []
    
    # Check for sound components
    total_sound_components = 0
    for screen_name in found_screens:
        screen_data = get_screen_data(screen_name)
        if isinstance(screen_data, dict) and "Properties" in screen_data:
            properties = screen_data["Properties"]
            components_list = properties.get("$Components", [])
            
            def check_for_sound_components(comp):
                """Recursively check for sound components"""
                nonlocal total_sound_components
                comp_type = comp.get("$Type", "")
                if comp_type in ["Sound", "Player"]:
                    total_sound_components += 1
                
                # Check nested components
                if "$Components" in comp:
                    for sub_comp in comp["$Components"]:
                        check_for_sound_components(sub_comp)
            
            for comp in components_list:
                check_for_sound_components(comp)
    
    if total_sound_components > 0:
        creative_features.append(f"背景聲音 ({total_sound_components} 個音效元件)")
    
    # Check for additional creative components
    total_creative_components = 0
    for screen_name in found_screens:
        screen_data = get_screen_data(screen_name)
        if isinstance(screen_data, dict) and "Properties" in screen_data:
            properties = screen_data["Properties"]
            components_list = properties.get("$Components", [])
            
            def check_for_creative_components(comp):
                """Recursively check for creative components"""
                nonlocal total_creative_components
                comp_type = comp.get("$Type", "")
                comp_name = comp.get("$Name", "").lower()
                
                # Check for creative components beyond basic requirements
                if comp_type in ["Canvas", "ImageSprite", "Ball", "Image", "HorizontalArrangement", "VerticalArrangement"] and comp_type not in ["Button", "Label", "TextBox", "NumericBox", "Clock"]:
                    total_creative_components += 1
                elif "animation" in comp_name or "effect" in comp_name or "動畫" in comp_name or "效果" in comp_name:
                    total_creative_components += 1
                
                # Check nested components
                if "$Components" in comp:
                    for sub_comp in comp["$Components"]:
                        check_for_creative_components(sub_comp)
            
            for comp in components_list:
                check_for_creative_components(comp)
    
    if total_creative_components > 0:
        creative_features.append(f"創意元件 ({total_creative_components} 個額外元件)")
    
    # Check for complex logic blocks
    total_blocks = 0
    for screen_name in found_screens:
        blocks = get_blocks(screen_name)
        total_blocks += len(blocks)
    
    if total_blocks > 10:  # More than basic functionality
        creative_features.append(f"複雜邏輯 ({total_blocks} 個程式區塊)")
    
    # Award bonus points based on creative features
    if len(creative_features) >= 3:
        bonus_score = 5
        remarks.append(f"豐富的創意設計: {', '.join(creative_features)} (+5)")
    elif len(creative_features) == 2:
        bonus_score = 3
    elif len(creative_features) == 1:
        bonus_score = 1
    
    if creative_features:
        remarks.append(f"創意設計: {', '.join(creative_features)} (+{bonus_score})")
    else:
        remarks.append("缺少創意設計元素 (+0)")
    
    score += bonus_score

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
            submissions.loc[idx, "comments"] += f"專案評分: {section_mark}/35分\n"
            
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
