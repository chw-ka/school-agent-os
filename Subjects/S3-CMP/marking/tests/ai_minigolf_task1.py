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

        # (2 marks) Add and rename drawing and animation compoents: Canvas(Grassland), Ball(Hole) and ImageSprite(Golfball).
        remarks = ""
        section_description = "Add and rename drawing and animation compoents: Canvas(Grassland), Ball(Hole) and ImageSprite(Golfball)."
        section_mark = 0
        if (components_util.assert_has_type(components, ["Canvas", "ImageSprite", "Ball"])):
            section_mark += 1
        else:
            remarks += "Missing components: Canvas, ImageSprite or Ball\n"
        if (components_util.assert_has_renamed_type(components, "Canvas")):
            section_mark += 0.5
        else:
            remarks += "Canvas not renamed\n"
        if (components_util.assert_has_renamed_type(components, "ImageSprite")):
            section_mark += 0.5
        else:
            remarks += "ImageSprite not renamed\n"
        if (components_util.assert_has_renamed_type(components, "Ball")):
            section_mark += 0.5
        else:
            remarks += "Ball not renamed\n"
        if (section_mark >= 2.5):
            section_mark = 2
        submissions.loc[idx, "marks"] += section_mark
        if (section_mark == 0):
            submissions.loc[idx, "comments"] += "[X] " + section_description + "\n"
        elif (section_mark < 2):
            submissions.loc[idx, "comments"] += "[-] " + section_description + "\n"
        else:
            submissions.loc[idx, "comments"] += "[O] " + section_description + "\n"

        # (2 marks) Changed pictures of "Grassland" and "Golfball" with the image files given.
        section_description = "Changed pictures of \"Grassland\" and \"Golfball\" with the image files given."
        section_mark = 0
        if (components_util.assert_has_properties_changed_type(components, "Canvas", "BackgroundImage")):
            section_mark += 1
        else:
            remarks += "BackgroundImage not changed in Canvas\n"
        if (components_util.assert_has_properties_changed_type(components, "ImageSprite", "Picture")):
            section_mark += 1
        else:
            remarks += "Picture not changed in ImageSprite\n"
        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark)

        # (2 marks) Program the block so that the golf ball move when user flung on the screen
        section_description = "Program the block so that the golf ball move when user flung on the screen"
        section_mark = 0
        if (blockly_util.assert_has_component_event(blockly, "Canvas", "Flung")):
            section_mark += 1
        else:
            remarks += "Canvas Flung event not found\n"
        if (blockly_util.assert_has_set_block_inside_event(blockly, "Canvas", "Flung", "ImageSprite", "Speed")):
            section_mark += 0.5
        else:
            remarks += "ImageSprite Speed not set in Canvas Flung event\n"
        if (blockly_util.assert_has_set_block_inside_event(blockly, "Canvas", "Flung", "ImageSprite", "Heading")):
            section_mark += 0.5
        else:
            remarks += "ImageSprite Heading not set in Canvas Flung event\n"
        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark)

        # (2 marks) Program the block so that the golf ball bounces when reaching the edge of grassland
        section_description = "Program the block so that the golf ball bounces when reaching the edge of grassland"
        section_mark = 0
        if (blockly_util.assert_has_component_event(blockly, "ImageSprite", "EdgeReached")):
            section_mark += 1
        else:
            remarks += "ImageSprite EdgeReached event not found\n"
        if (blockly_util.assert_has_method_block_inside_event(blockly, "ImageSprite", "EdgeReached", "ImageSprite", "Bounce")):
            section_mark += 1
        else:
            remarks += "ImageSprite Bounce not found in ImageSprite EdgeReached event\n"
        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark)

        # (2 marks) Export and hand in the correct format file.
        # auto add 2 marks for all submissions
        submissions.loc[idx, "marks"] += 2
        submissions.loc[idx, "comments"] += "[O] Export and hand in the correct format file.\n"
        if (remarks != ""):
            submissions.loc[idx, "comments"] += "\n" + remarks

        print("=========================================")
        print("Marks:", submissions.loc[idx, "marks"])
        print(submissions.loc[idx, "comments"])
        print("=========================================")

    # print submissions if comments not empty
    aia_utils.check_copycat(submissions)
    
    
    return submissions


if __name__ == "__main__":
    submissions = aia_utils.read_teams_aias()
    submissions = test(submissions)
    print(submissions)
    submissions.to_csv("marksheets.csv")
