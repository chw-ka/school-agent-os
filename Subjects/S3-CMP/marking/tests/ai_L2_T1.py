import json
import aia_util as aia_utils

def evaluate(components, blockly=None):
    total_score = 0
    remarks = []

    # Step 1: Check project name (same as L1 - included in file submission check)
    # Step 2-3: Check screen names and components (4 marks total)
    screen_names = list(components.keys())
    normalized_names = [name.lower() for name in screen_names]

    has_screen1 = "screen1" in normalized_names
    has_game = "game" in normalized_names
    has_result = "result" in normalized_names

    # Screen components check (4 marks)
    component_score = 0
    component_remarks = []

    # Helper function to collect all components recursively
    def collect_all_components(comps):
        result = []
        for comp in comps:
            result.append(comp)
            if "$Components" in comp:
                result.extend(collect_all_components(comp["$Components"]))
        return result

    # Screen1 components check (1.33 marks)
    if has_screen1:
        screen1_key = next((name for name in screen_names if name.lower() == "screen1"), None)
        if screen1_key and "$Components" in components[screen1_key]["Properties"]:
            flat_comps = collect_all_components(components[screen1_key]["Properties"]["$Components"])
            labels = [c for c in flat_comps if c.get("$Type") == "Label"]
            buttons = [c for c in flat_comps if c.get("$Type") == "Button"]
            
            if len(labels) >= 2:  # 遊戲標題 + 時間選擇標題
                component_score += 0.67
            else:
                component_remarks.append("Screen1缺少遊戲標題(Label)或時間選擇標題(Label)")
            
            if len(buttons) >= 3:  # 3個時間選擇按鈕
                component_score += 0.67
            else:
                component_remarks.append("Screen1缺少3個時間選擇按鈕(Button)")
        else:
            component_remarks.append("Screen1畫面中沒有找到元件")
    else:
        component_remarks.append("Screen1畫面不存在")

    # Game screen components check (1.33 marks)
    if has_game:
        game_key = next((name for name in screen_names if name.lower() == "game"), None)
        if game_key and "$Components" in components[game_key]["Properties"]:
            flat_comps = collect_all_components(components[game_key]["Properties"]["$Components"])
            labels = [c for c in flat_comps if c.get("$Type") == "Label"]
            buttons = [c for c in flat_comps if c.get("$Type") == "Button"]
            
            if len(labels) >= 2:  # 遊戲標題 + 剩餘時間
                component_score += 0.67
            else:
                component_remarks.append("Game缺少遊戲標題(Label)或剩餘時間(Label)")
            
            if len(buttons) >= 1:  # 速度測試按鈕
                component_score += 0.67
            else:
                component_remarks.append("Game缺少速度測試按鈕(Button)")
        else:
            component_remarks.append("Game畫面中沒有找到元件")
    else:
        component_remarks.append("Game畫面不存在")

    # Result screen components check (1.33 marks)
    if has_result:
        result_key = next((name for name in screen_names if name.lower() == "result"), None)
        if result_key and "$Components" in components[result_key]["Properties"]:
            flat_comps = collect_all_components(components[result_key]["Properties"]["$Components"])
            labels = [c for c in flat_comps if c.get("$Type") == "Label"]
            buttons = [c for c in flat_comps if c.get("$Type") == "Button"]
            
            if len(labels) >= 2:  # 剩餘分數標題 + 玩家得分
                component_score += 0.67
            else:
                component_remarks.append("Result缺少剩餘分數標題(Label)或玩家得分(Label)")
            
            if len(buttons) >= 1:  # 返回主畫面按鈕
                component_score += 0.67
            else:
                component_remarks.append("Result缺少返回主畫面按鈕(Button)")
        else:
            component_remarks.append("Result畫面中沒有找到元件")
    else:
        component_remarks.append("Result畫面不存在")

    # Convert component score to 4 marks scale
    component_final_score = min(round(component_score, 2), 4)
    total_score += component_final_score
    
    # Add component remarks
    if component_final_score < 4:
        remarks.extend(component_remarks)

    # Step 2: Check horizontal layout usage (2 marks)
    horizontal_layout_score = 0
    horizontal_layout_remarks = []
    
    # Check all screens for horizontal arrangements
    for screen_name in screen_names:
        screen_key = screen_name
        if "$Components" in components[screen_key]["Properties"]:
            flat_comps = collect_all_components(components[screen_key]["Properties"]["$Components"])
            
            # Look for HorizontalArrangement components
            horizontal_arrangements = [c for c in flat_comps if c.get("$Type") == "HorizontalArrangement"]
            
            if horizontal_arrangements:
                # Check if horizontal arrangements contain multiple components
                for ha in horizontal_arrangements:
                    if "$Components" in ha and len(ha["$Components"]) >= 2:
                        horizontal_layout_score = 2
                        break
                
                if horizontal_layout_score == 0:
                    horizontal_layout_remarks.append("找到水平配置，但配置內元件數量不足（需要2個或以上元件）")
            else:
                horizontal_layout_remarks.append(f"{screen_name}沒有使用水平配置(HorizontalArrangement)")
    
    if horizontal_layout_score == 0:
        remarks.extend(horizontal_layout_remarks)
    else:
        remarks.append("✅ 正確使用水平配置並包含多個元件")
    
    total_score += horizontal_layout_score

    # Step 4: Check component properties modification (2 marks)
    properties_score = 0
    properties_remarks = []
    
    # Check each screen separately - need at least 3 modified components per screen
    screens_with_sufficient_modifications = 0
    total_screens = 0
    
    for screen_name in screen_names:
        screen_key = screen_name
        if "$Components" in components[screen_key]["Properties"]:
            total_screens += 1
            flat_comps = collect_all_components(components[screen_key]["Properties"]["$Components"])
            
            # Get all labels and buttons in this screen
            screen_labels = [c for c in flat_comps if c.get("$Type") == "Label"]
            screen_buttons = [c for c in flat_comps if c.get("$Type") == "Button"]
            
            # Count modified components in this screen
            modified_in_screen = 0
            
            # Check labels with text
            for label in screen_labels:
                label_text = label.get("Text", "")
                if label_text == "" or label_text is None:
                    continue
                    
                has_modified_props = False
                for prop_name, prop_value in label.items():
                    if prop_name not in ["$Type", "$Name", "Text"] and prop_value is not None:
                        # Check if it's a meaningful modification (not default values)
                        if prop_name == "BackgroundColor" and prop_value != 0xFFFFFFFF:  # Not white
                            has_modified_props = True
                            break
                        elif prop_name == "TextColor" and prop_value != 0xFF000000:  # Not black
                            has_modified_props = True
                            break
                        elif prop_name == "FontSize" and prop_value != 14.0:  # Not default size
                            has_modified_props = True
                            break
                        elif prop_name == "FontBold" and prop_value == True:
                            has_modified_props = True
                            break
                        elif prop_name == "FontItalic" and prop_value == True:
                            has_modified_props = True
                            break
                        elif prop_name == "Width" and prop_value != -2:  # Not automatic
                            has_modified_props = True
                            break
                        elif prop_name == "Height" and prop_value != -2:  # Not automatic
                            has_modified_props = True
                            break
                
                if has_modified_props:
                    modified_in_screen += 1
            
            # Check buttons with text
            for button in screen_buttons:
                button_text = button.get("Text", "")
                if button_text == "" or button_text is None:
                    continue
                    
                has_modified_props = False
                for prop_name, prop_value in button.items():
                    if prop_name not in ["$Type", "$Name", "Text"] and prop_value is not None:
                        # Check if it's a meaningful modification (not default values)
                        if prop_name == "BackgroundColor" and prop_value != 0xFFFFFFFF:  # Not white
                            has_modified_props = True
                            break
                        elif prop_name == "TextColor" and prop_value != 0xFF000000:  # Not black
                            has_modified_props = True
                            break
                        elif prop_name == "FontSize" and prop_value != 14.0:  # Not default size
                            has_modified_props = True
                            break
                        elif prop_name == "FontBold" and prop_value == True:
                            has_modified_props = True
                            break
                        elif prop_name == "FontItalic" and prop_value == True:
                            has_modified_props = True
                            break
                        elif prop_name == "Width" and prop_value != -2:  # Not automatic
                            has_modified_props = True
                            break
                        elif prop_name == "Height" and prop_value != -2:  # Not automatic
                            has_modified_props = True
                            break
                        elif prop_name == "Shape" and prop_value != 0:  # Not default shape
                            has_modified_props = True
                            break
                
                if has_modified_props:
                    modified_in_screen += 1
            
            # Check if this screen has at least 3 modified components
            if modified_in_screen >= 3:
                screens_with_sufficient_modifications += 1
            else:
                properties_remarks.append(f"{screen_name}只有{modified_in_screen}個元件修改了屬性，需要至少3個元件修改屬性")
    
    # Calculate properties score based on screens with sufficient modifications
    if total_screens > 0:
        if screens_with_sufficient_modifications == total_screens:  # All screens have 3+ modified components
            properties_score = 2
        elif screens_with_sufficient_modifications >= total_screens * 0.67:  # 67% or more screens
            properties_score = 1
        else:
            properties_score = 0
            if not properties_remarks:
                properties_remarks.append(f"只有{screens_with_sufficient_modifications}/{total_screens}個畫面達到要求（每個畫面需要至少3個元件修改屬性）")
    else:
        properties_remarks.append("沒有找到任何畫面")
    
    if properties_score < 2:
        remarks.extend(properties_remarks)
    else:
        remarks.append("✅ 每個畫面都有至少3個元件修改了屬性")
    
    total_score += properties_score

    return round(total_score, 2), "\n".join(remarks)


def test(submissions):
    submissions = aia_utils.read_all_aias(submissions)
    for idx, row in submissions.iterrows():
        print("=========================================")
        print(submissions.loc[idx, "class"], submissions.loc[idx, "classnumber"])
        print("=========================================")
        submissions.loc[idx, "marks"] = 0
        submissions.loc[idx, "comments"] = ""

        # Check file submission first (2 marks)
        if row["filepath"] is None:
            submissions.loc[idx, "marks"] = 0
            submissions.loc[idx, "comments"] = "沒有提交檔案 - 0分\n"
            continue
        else:
            # File submitted - give 2 marks for submission
            submissions.loc[idx, "marks"] = 2
            submissions.loc[idx, "comments"] = "✅ 已提交 BPST_2X99.aia 檔案 (+2分)\n"

        # Evaluate the AIA content
        try:
            components = json.loads(row["components"])
            blockly = json.loads(row["blockly"])
            section_mark, remarks = evaluate(components, blockly)
            
            # Add the evaluation marks (max 8 marks from evaluation)
            submissions.loc[idx, "marks"] += section_mark
            submissions.loc[idx, "comments"] += f"專案結構與設計評分: {section_mark}/8分\n"
            
            if remarks:
                submissions.loc[idx, "comments"] += "\n詳細評語:\n" + remarks
                
        except Exception as e:
            submissions.loc[idx, "marks"] = 2  # Only submission marks
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

