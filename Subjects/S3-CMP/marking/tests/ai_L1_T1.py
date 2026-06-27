import json
import aia_util as aia_utils

def evaluate(components, blockly=None):
    total_score = 0
    remarks = []

    # Step 1: Check project name (2 marks)
    # Look for project name in blockly structure
    project_name_score = 0
    if components and "BPST_" in str(components):
        project_name_score = 2
    else:
        project_name_score = 1
        remarks.append("專案名稱應包含「BPST_2X99」格式，其中2X為班別，99為學號")
    
    total_score += project_name_score

    # Step 2: Check screen names (case-insensitive)
    screen_names = list(components.keys())
    normalized_names = [name.lower() for name in screen_names]

    has_screen1 = "screen1" in normalized_names
    has_game = "game" in normalized_names
    has_result = "result" in normalized_names

    # Step 3: Game screen check (2 marks)
    game_score = 0
    if has_game:
        game_score = 2  # Full marks if Game screen exists
    else:
        game_score = 1
        remarks.append("除主畫面外，應新增一個名為「Game」的畫面")
    
    total_score += game_score

    # Step 4: Result screen check (2 marks)
    result_score = 0
    if has_result:
        result_score = 2  # Full marks if Result screen exists
    else:
        result_score = 1
        remarks.append("除主畫面外，應新增一個名為「Result」的畫面")
    
    total_score += result_score

    # Step 5: Check components in each screen (2 marks)
    component_score = 0
    component_remarks = []

    # Screen1 components check
    if has_screen1:
        screen1_key = next((name for name in screen_names if name.lower() == "screen1"), None)
        if screen1_key and "$Components" in components[screen1_key]["Properties"]:
            screen1_comps = components[screen1_key]["Properties"]["$Components"]
            labels = [c for c in screen1_comps if c.get("$Type") == "Label"]
            buttons = [c for c in screen1_comps if c.get("$Type") == "Button"]
            
            if len(labels) >= 2:  # 遊戲標題 + 時間選擇標題
                component_score += 0.3
            else:
                component_remarks.append("Screen1缺少遊戲標題(Label)或時間選擇標題(Label)")
            
            if len(buttons) >= 3:  # 3個時間選擇按鈕
                component_score += 0.3
            else:
                component_remarks.append("Screen1缺少3個時間選擇按鈕(Button)")
        else:
            component_remarks.append("Screen1畫面中沒有找到元件")
    else:
        component_remarks.append("Screen1畫面不存在")

    # Game screen components check
    if has_game:
        game_key = next((name for name in screen_names if name.lower() == "game"), None)
        if game_key and "$Components" in components[game_key]["Properties"]:
            game_comps = components[game_key]["Properties"]["$Components"]
            labels = [c for c in game_comps if c.get("$Type") == "Label"]
            buttons = [c for c in game_comps if c.get("$Type") == "Button"]
            
            if len(labels) >= 2:  # 遊戲標題 + 剩餘時間
                component_score += 0.3
            else:
                component_remarks.append("Game缺少遊戲標題(Label)或剩餘時間(Label)")
            
            if len(buttons) >= 1:  # 速度測試按鈕
                component_score += 0.3
            else:
                component_remarks.append("Game缺少速度測試按鈕(Button)")
        else:
            component_remarks.append("Game畫面中沒有找到元件")
    else:
        component_remarks.append("Game畫面不存在")

    # Result screen components check
    if has_result:
        result_key = next((name for name in screen_names if name.lower() == "result"), None)
        if result_key and "$Components" in components[result_key]["Properties"]:
            def collect_all_components(comps):
                result = []
                for comp in comps:
                    result.append(comp)
                    if "$Components" in comp:
                        result.extend(collect_all_components(comp["$Components"]))
                return result

            flat_comps = collect_all_components(components[result_key]["Properties"]["$Components"])
            labels = [c for c in flat_comps if c.get("$Type") == "Label"]
            buttons = [c for c in flat_comps if c.get("$Type") == "Button"]
            
            if len(labels) >= 2:  # 剩餘分數標題 + 玩家得分
                component_score += 0.3
            else:
                component_remarks.append("Result缺少剩餘分數標題(Label)或玩家得分(Label)")
            
            if len(buttons) >= 1:  # 返回主畫面按鈕
                component_score += 0.3
            else:
                component_remarks.append("Result缺少返回主畫面按鈕(Button)")
        else:
            component_remarks.append("Result畫面中沒有找到元件")
    else:
        component_remarks.append("Result畫面不存在")

    # Convert component score to 2 marks scale
    component_final_score = min(component_score * 2, 2)
    total_score += component_final_score
    
    # Add component remarks
    if component_final_score < 2:
        remarks.extend(component_remarks)

    # Step 6: File submission check (2 marks)
    # This is handled in the main test function based on filepath
    # We'll add this in the test function

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
            submissions.loc[idx, "comments"] += f"專案結構評分: {section_mark}/8分\n"
            
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
