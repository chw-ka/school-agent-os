import json
import blockly_util as blockly_util
import components_util as components_util
import aia_util as aia_utils

def test(submissions):
    submissions = aia_utils.read_all_aias(submissions)
    for idx, row in submissions.iterrows():
        print("=========================================")
        print(submissions.loc[idx, "class"], submissions.loc[idx, "classnumber"])
        print("=========================================")
        submissions.loc[idx, "marks"] = 0
        submissions.loc[idx, "comments"] = ""
        components = json.loads(row["components"])
        blockly = json.loads(row["blockly"])
        remarks = "[O]: Correct\n[-]: Minor error\n[X]: Major error\n\n"

        # (2 marks) Export and hand in the correct format file.
        # auto add 2 marks for all submissions
        if (row['components'] == "{}"):
            submissions.loc[idx, "comments"] += "[X] Export and hand in the correct format file.\n"
            submissions.loc[idx, "comments"] += "No .aia found in the submission\n"
            continue

        # (2 marks) Create the layout with all components of score board, horizontal arrangement, score (label), reset (button).
        section_description = "Create the layout with all components of score board, horizontal arrangement, score (label), reset (button)."
        section_mark = 0
        if (components_util.assert_has_type(components, ["HorizontalArrangement"])):
            section_mark += 0.5
        else:
            remarks += "Missing components: HorizontalArrangement\n"
        if (components_util.assert_has_type(components, ["Label"])):
            section_mark += 0.5
            if (components_util.assert_has_renamed_type(components, "Label")):
                section_mark += 0.5
            else:
                remarks += "Label not renamed\n"
        else:
            remarks += "Missing components: Label\n"
        if (components_util.assert_has_type(components, ["Button"])):
            section_mark += 0.5
            if (components_util.assert_has_renamed_type(components, "Button")):
                section_mark += 0.5
            else:
                remarks += "Button not renamed\n"
        else:
            remarks += "Missing components: Button\n"
        section_mark = min(section_mark, 2)
        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark)

        # (2 marks) Program the block so that the scoreboard can show the score and the reset button can reset the score to 0.
        section_description = "Program the block so that the scoreboard can show the score and the reset button can reset the score to 0."
        section_mark = 0
        all_blocks = blockly_util.get_all_blocks(blockly)
        # get button.click event
        event = blockly_util.get_event_block(all_blocks, "Button", "Click")
        if (event != None):
            section_mark += 1
            # check have set label.text block to 0
            set_score_block = blockly_util.get_blocks(
                event, {"@type": "component_set_get", "mutation": {"@component_type": "Label"}, "@property_name": "Text"})
            if (set_score_block != None):
                section_mark += 1
            else:
                remarks += "Label Text block not found\n"
        else:
            remarks += "Button Click event not found\n"
        section_mark = min(section_mark, 2)
        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark)

        # (2 marks) Program the block so that the rocket will fire a bullet upward after user tapped on the rocket.
        section_description = "Program the block so that the rocket will fire a bullet upward after user tapped on the rocket."
        section_mark = 0
        event = blockly_util.get_event_block(all_blocks, "ImageSprite", "Touched")
        if (event != None):
            section_mark += 1
            # check have set bullet speed block
            set_speed_block = blockly_util.get_blocks(
                event, {"@type": "component_set_get", "mutation": {"@component_type": "Ball"}, "@property_name": "Speed"})
            if (set_speed_block != None):
                section_mark += 0.5
            else:
                remarks += "Speed block not found\n"
            # check have set bullet visible block
            set_visible_block = blockly_util.get_blocks(
                event, {"@type": "component_set_get", "mutation": {"@component_type": "Ball"}, "@property_name": "Visible"})
            if (set_visible_block != None):
                section_mark += 0.5
            else:
                remarks += "Visible block not found\n"
        else:
            remarks += "ImageSprite Touched event not found\n"
        section_mark = min(section_mark, 2)
        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark)

        # (2 marks) Program the block so that the bullet should be hidden and placed to the same position(x,y coordinate) as the rocket when it hits the edge of the Canvas.
        section_description = "Program the block so that the bullet should be hidden and placed to the same position(x,y coordinate) as the rocket when it hits the edge of the Canvas."
        section_mark = 0
        event = blockly_util.get_event_block(all_blocks, "Ball", "EdgeReached")
        if (event != None):
            section_mark += 0.5
            set_Y_block = blockly_util.get_blocks(
                event, {"@type": "component_set_get", "mutation": {"@component_type": "Ball"}, "@property_name": "Y"})
            if (set_Y_block != None):
                section_mark += 0.5
            else:
                remarks += "Speed block not found\n"
            set_visible_block = blockly_util.get_blocks(
                event, {"@type": "component_set_get", "mutation": {"@component_type": "Ball"}, "@property_name": "Visible"})
            if (set_visible_block != None):
                section_mark += 0.5
            else:
                remarks += "Speed block not found\n"
            set_header_block = blockly_util.get_blocks(
                event, {"@type": "component_set_get", "mutation": {"@component_type": "Ball"}, "@property_name": "Header"})
            if (set_header_block != None):
                section_mark += 0.5
            else:
                remarks += "Speed block not found\n"
        else:
            remarks += "Ball EdgeReached block not found\n"
        section_mark = min(section_mark, 2)
        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark)

        # (2 marks) Export and hand in the correct format file.
        section_description = "Export and hand in the correct format file."
        section_mark = 2
        section_mark = min(section_mark, 2)
        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark)

        if (remarks != ""):
            submissions.loc[idx, "comments"] += "\n" + remarks
        print("=========================================")
        print(submissions.loc[idx, "class"], submissions.loc[idx, "classnumber"])
        print(submissions.loc[idx, "comments"])
        print(submissions.loc[idx, "marks"])
        print("=========================================")


    # print submissions if comments not empty
    aia_utils.check_copycat(submissions)
    
    
    return submissions


if __name__ == "__main__":
    submissions = aia_utils.read_teams_aias()
    submissions = test(submissions)
    print(submissions)
    submissions.to_csv("marksheets.csv")