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

        # (2 marks) Add sensor: Clock and set timer interval to 1000.
        section_description = "Add sensor: Clock and set timer interval to 1000."
        section_mark = 0
        if (components_util.assert_has_type(components, ["Clock"])):
            section_mark += 2
        else:
            remarks += "Missing components: Clock\n"
        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark)

        # (2 marks) Program the block so that the golf ball stops at the hole when reaching the hole
        section_description = "Program the block so that the golf ball stops at the hole when reaching the hole"
        section_mark = 0
        all_blocks = blockly_util.get_all_blocks(blockly)
        event1 = blockly_util.get_event_block(all_blocks, "ImageSprite", "CollidedWith")
        event2 = blockly_util.get_event_block(all_blocks, "Ball", "CollidedWith")
        if (event1 != None):
            section_mark += 0.5
            ifstatement = blockly_util.get_if_statement(event1, "EQ",
                                                        {
                                                            "@type": "component_component_block",
                                                            "mutation": {"@component_type": "Ball"}},
                                                        {
                                                            "@type": "lexical_variable_get",
                                                            "mutation": {"eventparam": {"@name": "other"}}, },
                                                        )
            if (ifstatement != None):
                section_mark += 0.5
                set_speed_block = blockly_util.get_blocks(
                    ifstatement, {"@type": "component_set_get", "mutation": {"@component_type": "ImageSprite"}, "@property_name": "Speed"})
                if (set_speed_block != None):
                    section_mark += 0.5
                else:
                    remarks += "Speed block not found\n"
                set_X_block = blockly_util.get_blocks(
                    ifstatement, {"@type": "component_set_get", "mutation": {"@component_type": "ImageSprite"}, "@property_name": "X"})
                if (set_X_block != None):
                    section_mark += 0.5
                else:
                    remarks += "Speed block not found\n"
                set_Y_block = blockly_util.get_blocks(
                    ifstatement, {"@type": "component_set_get", "mutation": {"@component_type": "ImageSprite"}, "@property_name": "Y"})
                if (set_Y_block != None):
                    section_mark += 0.5
                else:
                    remarks += "Speed block not found\n"
            else:
                remarks += "If block not found\n"
        elif (event2 != None):
            section_mark += 0.5
            ifstatement = blockly_util.get_if_statement(event2, "EQ",
                                                        {
                                                            "@type": "component_component_block",
                                                            "mutation": {"@component_type": "ImageSprite"}},
                                                        {
                                                            "@type": "lexical_variable_get",
                                                            "mutation": {"eventparam": {"@name": "other"}}, },
                                                        )
            if (ifstatement != None):
                section_mark += 0.5
                set_speed_block = blockly_util.get_blocks(
                    ifstatement, {"@type": "component_set_get", "mutation": {"@component_type": "ImageSprite"}, "@property_name": "Speed"})
                if (set_speed_block != None):
                    section_mark += 0.5
                else:
                    remarks += "Speed block not found\n"
                set_X_block = blockly_util.get_blocks(
                    ifstatement, {"@type": "component_set_get", "mutation": {"@component_type": "ImageSprite"}, "@property_name": "X"})
                if (set_X_block != None):
                    section_mark += 0.5
                else:
                    remarks += "Speed block not found\n"
                set_Y_block = blockly_util.get_blocks(
                    ifstatement, {"@type": "component_set_get", "mutation": {"@component_type": "ImageSprite"}, "@property_name": "Y"})
                if (set_Y_block != None):
                    section_mark += 0.5
                else:
                    remarks += "Speed block not found\n"
            else:
                remarks += "If block not found\n"
            section_mark += 0.5
        else:
            remarks += "ImageSprite CollidedWith event not found\n"

        section_mark = min(section_mark, 2)
        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark)

        # (2 marks) Program the block so that the golf ball slows down as it moves along
        section_description = "Program the block so that the golf ball slows down as it moves along"
        section_mark = 0
        all_blocks = blockly_util.get_all_blocks(blockly)
        event = blockly_util.get_event_block(all_blocks, "Clock", "Timer")
        if (event != None):
            section_mark += 0.5
            set_speed_block = blockly_util.get_blocks(
                event, {"@type": "component_set_get", "mutation": {"@component_type": "ImageSprite"}, "@property_name": "Speed"})
            if (set_speed_block != None):
                section_mark += 0.5
            else:
                remarks += "Speed block not found\n"

            ifstatement = blockly_util.get_if_statement(event, "LTE", {
                "@type": "component_set_get",
                "mutation": {
                    "@component_type": "ImageSprite",
                    "@set_or_get": "get",
                    "@property_name": "Speed",
                }
            },
                {
                "@type": "math_number",
                "field": {
                    "@name": "NUM",
                    "#text": "0.5"
                }
            })
            if (ifstatement != None):
                section_mark += 0.5
                set_speed_block = blockly_util.get_blocks(
                    ifstatement, {"@type": "component_set_get", "mutation": {"@component_type": "ImageSprite"}, "@property_name": "Speed"})
                if (set_speed_block != None):
                    section_mark += 0.5
                else:
                    remarks += "Speed block not found\n"
            else:
                remarks += "If block not found\n"

        section_mark = min(section_mark, 2)
        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark)

        # (2 marks) Program the block so that the golf ball bounces when reaching the red horizontal obstacle.
        section_description = "Program the block so that the golf ball bounces when reaching the red horizontal obstacle."
        section_mark = 0
        all_blocks = blockly_util.get_all_blocks(blockly)
        event = blockly_util.get_event_block(all_blocks, "ImageSprite", "CollidedWith")
        if (event != None):
            section_mark += 0.5
            ifstatement = blockly_util.get_if_statement(event, "EQ",
                                                        {
                                                            "@type": "component_component_block",
                                                            "mutation": {"@component_type": "ImageSprite"}},
                                                        {
                                                            "@type": "lexical_variable_get",
                                                            "mutation": {"eventparam": {"@name": "other"}}, },
                                                        )
            if (ifstatement != None):
                section_mark += 0.5
                set_speed_block = blockly_util.get_blocks(
                    ifstatement, {"@type": "component_set_get", "mutation": {"@component_type": "ImageSprite"}, "@property_name": "Heading"})
                if (set_speed_block != None):
                    section_mark += 1
                else:
                    remarks += "Heading block not found\n"
            else:
                remarks += "If block not found\n"
        else:
            remarks += "ImageSprite CollidedWith event not found\n"

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