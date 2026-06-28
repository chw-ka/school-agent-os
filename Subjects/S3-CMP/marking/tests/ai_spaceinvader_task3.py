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

        # (2 marks) New component (Clock) added so that the ufo appear randomly on the top every 3 seconds.
        section_description = "New component (Clock) added so that the ufo appear randomly on the top every 3 seconds."
        section_mark = 0
        if (components_util.assert_has_type(components, ["Clock"])):
            section_mark += 1
            # check the properties of the clock with 3 seconds interval
            if (components_util.assert_has_properties_value(components, "Clock", "TimerInterval", "3000")):
                section_mark += 1
            else:
                remarks += "Clock Interval not set to 3000\n"
        else:
            remarks += "Missing components: Clock\n"
        section_mark = min(section_mark, 2)
        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark)

        # (2 marks) Program the blocks so that the ufo appear randomly on the top every 3 seconds.
        section_description = "Program the blocks so that the ufo appear randomly on the top every 3 seconds."
        section_mark = 0
        # has event for clock timer
        all_blocks = blockly_util.get_all_blocks(blockly)
        event = blockly_util.get_event_block(all_blocks, "Clock", "Timer")
        if (event != None):
            section_mark += 1
            # check the blocks inside the event, should have setting ufo x, and y to random position
            set_x = blockly_util.get_blocks(event, {"@type": "component_set_get",
                                            "mutation": {"@component_type": "ImageSprite"}, "@property_name": "X"})
            set_y = blockly_util.get_blocks(event, {"@type": "component_set_get",
                                            "mutation": {"@component_type": "ImageSprite"}, "@property_name": "Y"})
            if (set_x != None and set_y != None):
                section_mark += 1
            else:
                remarks += "ImageSprite X and Y block not found\n"
        else:
            remarks += "Clock Timer event not found\n"
        section_mark = min(section_mark, 2)
        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark)

        # (2 marks) Program the blocks so that the score plus 1 and the ufo appear at random place immediately when the bullet hit the ufo.
        section_description = "Program the blocks so that the score plus 1 and the ufo appear at random place immediately when the bullet hit the ufo."
        section_mark = 0
        # has event for bullet collision
        event = blockly_util.get_event_block(all_blocks, "ImageSprite", "CollidedWith")
        event2 = blockly_util.get_event_block(all_blocks, "Ball", "CollidedWith")
        if (event != None):
            section_mark += 1
            # check the blocks inside the event, should have setting ufo x, and y to random position
            set_x = blockly_util.get_blocks(event, {"@type": "component_set_get",
                                            "mutation": {"@component_type": "ImageSprite"}, "@property_name": "X"})
            set_y = blockly_util.get_blocks(event, {"@type": "component_set_get",
                                            "mutation": {"@component_type": "ImageSprite"}, "@property_name": "Y"})
            if (set_x != None and set_y != None):
                section_mark += 1
            else:
                remarks += "ImageSprite X and Y block not found\n"
        elif (event2 != None):
            section_mark += 1
            # check the blocks inside the event, should have setting ufo x, and y to random position
            set_x = blockly_util.get_blocks(event2, {"@type": "component_set_get",
                                            "mutation": {"@component_type": "ImageSprite"}, "@property_name": "X"})
            set_y = blockly_util.get_blocks(event2, {"@type": "component_set_get",
                                            "mutation": {"@component_type": "ImageSprite"}, "@property_name": "Y"})
            if (set_x != None and set_y != None):
                section_mark += 1
            else:
                remarks += "ImageSprite X and Y block not found\n"
        else:
            remarks += "ImageSprite CollidedWith event not found\n"
        section_mark = min(section_mark, 2)
        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark)

        # (2 marks) Program the blocks so that bullet cannot be fired when it's fired.
        section_description = "Program the blocks so that bullet cannot be fired when it's fired."
        section_mark = 0
        # has event for bullet collision
        event = blockly_util.get_event_block(all_blocks, "ImageSprite", "Touched")
        if (event != None):
            # have if block to check if bullet is not visible
            if_block = blockly_util.get_blocks(event, {"@type": "math_compare"})
            if_block2 = blockly_util.get_blocks(event, {"@type": "logic_compare"})
            if (if_block != None or if_block2 != None):
                section_mark += 2
            else:
                remarks += "Logic compare block not found\n"
        else:
            remarks += "ImageSprite Touched event not found\n"
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
