import blockly_util as blockly_util
import components_util as components_util
import aia_util as aia_utils
import json

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

        # (2 marks) Place the rocket well before the game start
        section_description = "Place the rocket well before the game start"
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
        section_mark = min(section_mark, 2)
        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark)

        # (2 marks) Added space (Canvas), ufo (ImageSprite) and rocket (ImageSprite) components into gaming layout.
        section_description = "Added space (Canvas), ufo (ImageSprite) and rocket (ImageSprite) components into gaming layout."
        section_mark = 0
        if (components_util.assert_has_type(components, ["Canvas"])):
            section_mark += 0.5
            if (components_util.assert_has_renamed_type(components, "Canvas")):
                section_mark += 0.5
            else:
                remarks += "Canvas not renamed\n"
        else:
            remarks += "Canvas not found\n"

        if (components_util.assert_has_type(components, ["ImageSprite"])):
            section_mark += 0.5
            num = components_util.get_number_of_renamed_type(components, "ImageSprite")
            if (num > 0):
                section_mark += num * 0.5
            else:
                remarks += "ImageSprite not renamed\n"

        section_mark = min(section_mark, 2)
        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark)

        # (2 marks) Added HP (Label) and reset (Button) components into gaming layout.
        section_description = "Added HP (Label) and reset (Button) components into gaming layout."
        section_mark = 0
        if (components_util.assert_has_type(components, ["Label"])):
            section_mark += 0.5
            if (components_util.get_number_of_renamed_type(components, "Label") >= 2):
                section_mark += 0.5
            else:
                remarks += "New Label not renamed\n"
        else:
            remarks += "Label not found\n"

        if (components_util.assert_has_type(components, ["Button"])):
            section_mark += 0.5
            if (components_util.get_number_of_renamed_type(components, "Button") >= 2):
                section_mark += 0.5
            else:
                remarks += "New Button not renamed\n"
        else:
            remarks += "Button not found\n"

        section_mark = min(section_mark, 2)
        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark)

        # (2 marks) The ufo will move in a random direction and bounce when it reaches the edges.
        section_description = "The ufo will move in a random direction and bounce when it reaches the edges."
        section_mark = 0
        all_blocks = blockly_util.get_all_blocks(blockly)
        event = blockly_util.get_event_block(all_blocks, "ImageSprite", "EdgeReached")
        if (event != None):
            section_mark += 1
            block = blockly_util.get_blocks(
                event, {"@type": "component_method", "mutation": {"@component_type": "ImageSprite", "@method_name": "Bounce"}})
            if (block != None):
                section_mark += 1
            else:
                remarks += "ImageSprite Bounce block not found\n"
        else:
            remarks += "ImageSprite EdgeReached event not found\n"

        section_mark = min(section_mark, 2)
        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark)

        # (2 marks) The rocket will move in specific direction according to the gestures detected by the Personal Image Classifier.
        section_description = "The rocket will move in specific direction according to the gestures detected by the Personal Image Classifier."
        section_mark = 0
        event = blockly_util.get_event_block(all_blocks, "PersonalImageClassifier", "GotClassification")
        if (event != None):
            block = blockly_util.get_blocks(
                event, {"@type": "component_method", "mutation": {"@component_type": "ImageSprite", "@property_name": "Heading"}})
            if (block != None):
                section_mark += 2
            else:
                remarks += "ImageSprite Heading block not found\n"
        else:
            remarks += "PersonalImageClassifier GotClassification event not found\n"

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
