import json
import aia_util as aia_utils

def evaluate(components, blockly=None):
    total_score = 0
    remarks = []

    # Step 1: Check screen names (case-insensitive)
    screen_names = list(components.keys())
    normalized_names = [name.lower() for name in screen_names]

    has_screen1 = "screen1" in normalized_names
    has_game = "game" in normalized_names
    has_result = "result" in normalized_names

    if len(screen_names) >= 3:
        total_score += 1
    else:
        remarks.append("請確認你有三個畫面。")

    if has_screen1 and has_game and has_result:
        total_score += 1
    else:
        remarks.append("請確保三個畫面命名為 Screen1、Game 和 Result（不分大小寫）。")

    # Step 2: Screen1 - Check buttons
    screen1_key = next((name for name in screen_names if name.lower() == "screen1"), None)
    if screen1_key and "$Components" in components[screen1_key]["Properties"]:
        screen1_comps = components[screen1_key]["Properties"]["$Components"]
        buttons = [c for c in screen1_comps if c.get("$Type") == "Button"]
        button_texts = [b.get("Text", "").lower() for b in buttons]

        has_quit = any("quit" in text for text in button_texts)
        has_seconds = sum("second" in text or "sec" in text or text.strip().isdigit() for text in button_texts)

        if len(buttons) >= 4 and has_seconds >= 2 and has_quit:
            total_score += 3
        else:
            remarks.append("請在 Screen1 畫面加上至少四個按鈕，包括選擇秒數和結束（Quit）按鈕。")
    else:
        remarks.append("Screen1 畫面中似乎沒有設定任何按鈕。")

    # Step 3: Game screen - check components
    game_key = next((name for name in screen_names if name.lower() == "game"), None)
    label_count = button_count = clock_count = 0
    if game_key and "$Components" in components[game_key]["Properties"]:
        game_comps = components[game_key]["Properties"]["$Components"]
        for comp in game_comps:
            if comp.get("$Type") == "Label":
                label_count += 1
            elif comp.get("$Type") == "Button":
                button_count += 1
            elif comp.get("$Type") == "Clock":
                clock_count += 1

    part3_score = 0
    if label_count >= 2:
        part3_score += 1.5
    else:
        remarks.append("Game 畫面中應該至少有兩個 Label，用於顯示時間和分數。")
    if button_count >= 1:
        part3_score += 0.75
    else:
        remarks.append("Game 畫面應該至少有一個按鈕用作 Click Me。")
    if clock_count >= 1:
        part3_score += 0.75
    else:
        remarks.append("Game 畫面應該有一個 Clock 控件用作計時。")
    total_score += part3_score

    # Step 4: Result screen
    result_key = next((name for name in screen_names if name.lower() == "result"), None)
    r_label = r_button = 0
    if result_key and "$Components" in components[result_key]["Properties"]:
        def collect_all_components(comps):
            result = []
            for comp in comps:
                result.append(comp)
                if "$Components" in comp:
                    result.extend(collect_all_components(comp["$Components"]))
            return result

        flat_comps = collect_all_components(components[result_key]["Properties"]["$Components"])
        r_label = sum(1 for c in flat_comps if c.get("$Type") == "Label")
        r_button = sum(1 for c in flat_comps if c.get("$Type") == "Button")

    part4_score = 0
    if r_label >= 1:
        part4_score += 1
    else:
        remarks.append("Result 畫面應該有一個 Label 顯示得分。")
    if r_button >= 1:
        part4_score += 1
    else:
        remarks.append("Result 畫面應該有一個按鈕返回主畫面。")
    total_score += part4_score

    return round(total_score, 2), "\n".join(remarks)



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