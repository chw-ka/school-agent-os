import json
import aia_util as aia_utils

def evaluate(components, blockly):
    total = 0
    remarks = []

    # (2 marks) .aia submitted
    total += 2
    remarks.append("已遞交 .aia 文件 (+2)")

    screen_blocks = blockly.get("Screen1", {}).get("xml", {}).get("block", [])
    if not isinstance(screen_blocks, list):
        screen_blocks = [screen_blocks]

    def recursive_find(blocks, condition):
        found = []
        stack = blocks[:]
        while stack:
            block = stack.pop()
            if condition(block):
                found.append(block)

            for key in ["statement", "next", "else", "value"]:
                v = block.get(key)
                if isinstance(v, dict) and "block" in v:
                    stack.append(v["block"])
                elif isinstance(v, list):
                    for i in v:
                        if isinstance(i, dict) and "block" in i:
                            stack.append(i["block"])
        return found

    # (2 marks) ImageSprite set Y = Canvas.Height - Sprite.Height
    def is_sprite_ground_position(block):
        if block.get("@type") != "component_set_get":
            return False
        mutation = block.get("mutation", {})
        if mutation.get("@component_type") != "ImageSprite":
            return False
        if mutation.get("@property_name") != "Y":
            return False
        value_block = block.get("value", {}).get("block", {})
        if value_block.get("@type") != "math_subtract":
            return False
        texts = str(value_block)
        return "Canvas" in texts and "Height" in texts

    sprite_blocks = recursive_find(screen_blocks, is_sprite_ground_position)
    if sprite_blocks:
        total += 2
        remarks.append("ImageSprite 設定為貼地 (Canvas.Height - Sprite.Height) (+2)")
    else:
        remarks.append("未找到 ImageSprite 正確貼地的設定")

    # (1+1) Ball Heading = 270
    def is_ball_heading_270(block):
        if block.get("@type") != "component_set_get":
            return False
        mutation = block.get("mutation", {})
        if mutation.get("@component_type") != "Ball":
            return False
        if mutation.get("@property_name") != "Heading":
            return False
        value_block = block.get("value", {}).get("block", {})
        return value_block.get("field", {}).get("#text") == "270"

    heading_blocks = recursive_find(screen_blocks, is_ball_heading_270)
    heading_count = len(heading_blocks)
    total += min(heading_count, 2)
    if heading_count >= 2:
        remarks.append("兩個 Ball 設定 Heading = 270 (+2)")
    elif heading_count == 1:
        remarks.append("只有一個 Ball 設定 Heading = 270 (+1)")
    else:
        remarks.append("未有 Ball 設定 Heading = 270")

    # (1+1) Ball reset Y to 0 after falling
    def is_ball_y_reset(block):
        if block.get("@type") != "component_set_get":
            return False
        mutation = block.get("mutation", {})
        if mutation.get("@component_type") != "Ball":
            return False
        if mutation.get("@property_name") != "Y":
            return False
        value_block = block.get("value", {}).get("block", {})
        return value_block.get("field", {}).get("#text") == "0"

    y_reset_blocks = recursive_find(screen_blocks, is_ball_y_reset)
    y_reset_count = len(y_reset_blocks)
    total += min(y_reset_count, 2)
    if y_reset_count >= 2:
        remarks.append("兩個 Ball 落地後 Y 重設為 0 (+2)")
    elif y_reset_count == 1:
        remarks.append("只有一個 Ball 重設 Y 為 0 (+1)")
    else:
        remarks.append("未有 Ball 重設 Y 為 0")

    return total, "\n".join(remarks)



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
