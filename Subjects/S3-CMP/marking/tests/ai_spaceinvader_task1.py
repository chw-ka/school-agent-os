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

        # (2 marks) Create the layout with all renamed components, space(canvas), rocket(imageSprite), ufo(imageSprite), bullet(ball)
        section_description = "Create the layout with all renamed components, space(canvas), rocket(imageSprite), ufo(imageSprite), bullet(ball)"
        section_mark = 0
        if (components_util.assert_has_type(components, ["Canvas"])):
            section_mark += 0.5
            if (components_util.assert_has_renamed_type(components, "Canvas")):
                section_mark += 0.5
            else:
                remarks += "Canvas not renamed\n"
        else:
            remarks += "Missing components: Canvas\n"

        if (components_util.assert_has_type(components, ["ImageSprite"])):
            section_mark += 0.5
            if (components_util.assert_has_renamed_type(components, "ImageSprite")):
                section_mark += 0.5
            else:
                remarks += "ImageSprite not renamed\n"

        if (components_util.assert_has_type(components, ["Ball"])):
            section_mark += 0.5
            if (components_util.assert_has_renamed_type(components, "Ball")):
                section_mark += 0.5
            else:
                remarks += "Ball not renamed\n"
        else:
            remarks += "Missing components: Ball\n"
        section_mark  = min(section_mark, 2)
        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark)

        # (2 marks) Attached images on space, rocket and ufo.
        section_description = "Attached images on space, rocket and ufo."
        section_mark = 0
        if (components_util.assert_has_properties_changed_type(components, "Canvas", "BackgroundImage")):
            section_mark += 1
        else:
            remarks += "Missing components: Canvas.BackgroundImage\n"
        if (components_util.assert_has_properties_changed_type(components, "ImageSprite", "Picture")):
            section_mark += 1
        else:
            remarks += "Missing components: ImageSprite.Picture\n"
        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark)

        # (2 marks) Program the block so that the bullet should be hidden and placed at the same position(x,y coordinate) as rocket initially.
        section_description = "Program the block so that the bullet should be hidden and placed at the same position(x,y coordinate) as rocket initially."
        section_mark = 0
        all_blocks = blockly_util.get_all_blocks(blockly)
        event = blockly_util.get_event_block(all_blocks, "Form", "Initialize")
        if (event != None):
            section_mark += 0.5
            set_speed_block = blockly_util.get_blocks(
                event, {"@type": "component_set_get", "mutation": {"@component_type": "Ball"}, "@property_name": "Visible"})
            if (set_speed_block != None):
                section_mark += 0.5
            else:
                remarks += "Visible block not found\n"
                
            set_speed_block = blockly_util.get_blocks(
                event, {"@type": "component_set_get", "mutation": {"@component_type": "Ball"}, "@property_name": "X"})
            if (set_speed_block != None):
                section_mark += 0.5
            else:
                remarks += "Visible block not found\n"
                
            set_speed_block = blockly_util.get_blocks(
                event, {"@type": "component_set_get", "mutation": {"@component_type": "Ball"}, "@property_name": "Y"})
            if (set_speed_block != None):
                section_mark += 0.5
            else:
                remarks += "Visible block not found\n"
        else:
            remarks += "Initialize event not found\n"

        section_mark = min(section_mark, 2)
        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark)

        # (2 marks) Program the block so that the rocket move along horizontally when the user drags the rocket.
        section_description = "Program the block so that the rocket move along horizontally when the user drags the rocket."
        section_mark = 0
        all_blocks = blockly_util.get_all_blocks(blockly)
        event = blockly_util.get_event_block(all_blocks, "ImageSprite", "Dragged")
        if (event != None):
            section_mark += 1
            set_speed_block = blockly_util.get_blocks(
                event, {"@type": "component_set_get", "mutation": {"@component_type": "ImageSprite"}, "@property_name": "X"})
            if (set_speed_block != None):
                section_mark += 1
            else:
                remarks += "X block not found\n"
        else:
            remarks += "ImageSprite Dragged event not found\n"

        section_mark = min(section_mark, 2)
        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark)

        # (2 marks) Export and hand in the correct format file.
        section_description = "Export and hand in the correct format file."
        section_mark = 2
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