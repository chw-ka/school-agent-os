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

        # (5 marks) Insert a balloon
        remarks = "Remarks:\n"
        section_description = "Screen initialize"
        section_mark = 0
        if (blockly_util.assert_has_component_event(blockly, "Form", "Initialize")):
            section_mark += 1
            if (blockly_util.assert_has_set_block_inside_event(blockly, "Form", "Initialize", "Ball", "Heading")):
                section_mark += 1
            else:
                remarks += "Missing Set Ball.Heading method\n"

            if (blockly_util.assert_has_set_block_inside_event(blockly, "Form", "Initialize", "Ball", "Speed")):
                section_mark += 1
            else:
                remarks += "Missing Set Ball.Speed method\n"

            set_heading_blocks = blockly_util.get_blocks_by_type_and_mutation(blockly_util.get_all_blocks(blockly), "component_set_get", [
                ("@component_type", "Ball"), ("@property_name", "Heading")])
            if (len(set_heading_blocks) > 0 and blockly_util.match_blocks_subset(set_heading_blocks[0], {
                "value": {
                    "@name": "VALUE",
                    "block": {
                        "@type": "math_random_int",
                        "value": [
                            {
                                "@name": "FROM",
                                "block": {
                                    "@type": "math_number",
                                    "field": {
                                        "@name": "NUM",
                                        "#text": "0"
                                    }
                                }
                            },
                            {
                                "@name": "TO",
                                "block": {
                                    "@type": "math_number",
                                    "field": {
                                        "@name": "NUM",
                                        "#text": "360"
                                    }
                                }
                            }
                        ]
                    }
                },
            })):
                section_mark += 1
            else:
                remarks += "Missing Random block for Ball.Heading\n"

            set_spped_blocks = blockly_util.get_blocks_by_type_and_mutation(blockly_util.get_all_blocks(blockly), "component_set_get", [
                ("@component_type", "Ball"), ("@property_name", "Speed")])
            if (len(set_spped_blocks) > 0 and blockly_util.match_blocks_subset(set_spped_blocks[0], {
                "value": {
                    "@name": "VALUE",
                    "block": {
                        "@type": "math_random_int",
                        "value": [
                            {
                                "@name": "FROM",
                                "block": {
                                    "@type": "math_number",
                                    "field": {
                                        "@name": "NUM",
                                        "#text": "5"
                                    }
                                }
                            },
                            {
                                "@name": "TO",
                                "block": {
                                    "@type": "math_number",
                                    "field": {
                                        "@name": "NUM",
                                        "#text": "15"
                                    }
                                }
                            }
                        ]
                    }
                }
            })):
                section_mark += 1
            else:
                remarks += "Missing Random block for Ball.Speed\n"

        if (section_mark > 4):
            submissions.loc[idx, "marks"] += 5
            submissions.loc[idx, "mark1"] = 5
        elif (section_mark > 1):
            submissions.loc[idx, "marks"] += 3
            submissions.loc[idx, "mark1"] = 3
        elif (section_mark > 0):
            submissions.loc[idx, "marks"] += 1
            submissions.loc[idx, "mark1"] = 1
        else:
            submissions.loc[idx, "mark1"] = 0
        submissions.loc[idx,
                        "comments"] += aia_utils.get_comments(section_description, submissions.loc[idx, "mark1"], 5)

        # (5 marks) The Ball movingBall bounces when reaches edge
        section_description = "The Ball movingBall bounces when reaches edge"
        section_mark = 0
        all_blocks = blockly_util.get_all_blocks(blockly)
        event = blockly_util.get_blocks_by_type_and_mutation(all_blocks, "component_event", [
            ("@component_type", "Ball"), ("@event_name", "EdgeReached")
        ])
        if (len(event) > 0):
            section_mark += 1

            blocks = blockly_util.get_blocks_by_type_and_mutation(event[0], "component_method", [
                ("@component_type", "Ball"), ("@method_name", "Bounce")])
            if (len(blocks) > 0):
                section_mark += 1
                if (len(blocks) > 0 and blockly_util.match_blocks_subset(blocks[0], {
                    "value": {
                        "@name": "ARG0",
                        "block": {
                            "@type": "lexical_variable_get",
                            "mutation": {
                                "eventparam": {
                                    "@name": "edge"
                                }
                            },
                            "field": {
                                "@name": "VAR",
                                "#text": "edge"
                            }
                        }
                    }
                })):
                    section_mark += 1
                else:
                    remarks += "Missing edge parameter in Ball.EdgeReached event\n"
            else:
                remarks += "Missing Ball.Bounce method\n"

        else:
            remarks += "Missing Ball.EdgeReached event\n"

        if (section_mark == 3):
            submissions.loc[idx, "marks"] += 5
            submissions.loc[idx, "mark2"] = 5
        elif (section_mark > 1):
            submissions.loc[idx, "marks"] += 3
            submissions.loc[idx, "mark2"] = 3
        elif (section_mark > 0):
            submissions.loc[idx, "marks"] += 1
            submissions.loc[idx, "mark2"] = 1
        else:
            submissions.loc[idx, "mark2"] = 0
        submissions.loc[idx,
                        "comments"] += aia_utils.get_comments(section_description, submissions.loc[idx, "mark2"], 5)

        # (5 marks) Make the ImageSprite player draggable
        section_description = "Make the ImageSprite player draggable"
        section_mark = 0
        if (blockly_util.assert_has_component_event(blockly, "ImageSprite", "Dragged")):
            section_mark += 1
            event = blockly_util.get_blocks_by_type_and_mutation(blockly_util.get_all_blocks(blockly), "component_event", [
                ("@component_type", "ImageSprite"), ("@event_name", "Dragged")
            ])

            blocks = blockly_util.get_blocks_by_type_and_mutation(event, "component_set_get", [
                ("@component_type", "ImageSprite"), ("@property_name", "X")])
            if (len(blocks) > 0):
                section_mark += 1
                if (blockly_util.match_blocks_subset(blocks[0], {
                    "value": {
                        "@name": "VALUE",
                        "block": {
                            "@type": "lexical_variable_get",
                            "mutation": {
                                "eventparam": {
                                    "@name": "currentX"
                                }
                            },
                            "field": {
                                "@name": "VAR",
                                "#text": "currentX"
                            }
                        }
                    },
                })):
                    section_mark += 1
                else:
                    remarks += "Missing set ImageSprite.X method to currentX\n"
            else:
                remarks += "Missing set ImageSprite.X method\n"

            blocks = blockly_util.get_blocks_by_type_and_mutation(event, "component_set_get", [
                ("@component_type", "ImageSprite"), ("@property_name", "Y")])
            if (len(blocks) > 0):
                section_mark += 1
                if (blockly_util.match_blocks_subset(blocks[0], {
                    "value": {
                        "@name": "VALUE",
                        "block": {
                            "@type": "lexical_variable_get",
                            "mutation": {
                                "eventparam": {
                                    "@name": "currentY"
                                }
                            },
                            "field": {
                                "@name": "VAR",
                                "#text": "currentY"
                            }
                        }
                    },
                })):
                    section_mark += 1
                else:
                    remarks += "Missing set ImageSprite.Y method to currentY\n"
            else:
                remarks += "Missing set ImageSprite.Y method\n"

            if (section_mark == 1):
                moveto_blocks = blockly_util.get_blocks_by_type_and_mutation(event[0], "component_method", [
                    ("@component_type", "ImageSprite"), ("@method_name", "MoveTo")])
                if (len(moveto_blocks) > 0):
                    section_mark += 2
                    currentx_block = blockly_util.get_blocks_by_type_and_mutation(moveto_blocks[0], "lexical_variable_get", [
                        ("eventparam", {"@name": "currentX"})])
                    if (len(currentx_block) > 0):
                        section_mark += 1
                    else:
                        remarks += "Missing MoveTo method with currentX\n"

                    currenty_block = blockly_util.get_blocks_by_type_and_mutation(moveto_blocks[0], "lexical_variable_get", [
                        ("eventparam", {"@name": "currentY"})])
                    if (len(currenty_block) > 0):
                        section_mark += 1
                    else:
                        remarks += "Missing MoveTo method with currentY\n"

        else:
            remarks += "Missing ImageSprite.Dragged event\n"

        if (section_mark > 4):
            submissions.loc[idx, "marks"] += 5
            submissions.loc[idx, "mark3"] = 5
        elif (section_mark > 1):
            submissions.loc[idx, "marks"] += 3
            submissions.loc[idx, "mark3"] = 3
        elif (section_mark > 0):
            submissions.loc[idx, "marks"] += 1
            submissions.loc[idx, "mark3"] = 1
        else:
            submissions.loc[idx, "mark3"] = 0
        submissions.loc[idx,
                        "comments"] += aia_utils.get_comments(section_description, submissions.loc[idx, "mark3"], 5)

        if (remarks != ""):
            submissions.loc[idx, "comments"] += "\n" + remarks
        else:
            submissions.loc[idx, "comments"] += "\nAll correct"
        print("=========================================")
        print("Marks:", submissions.loc[idx, "marks"])
        print(submissions.loc[idx, "comments"])
        print("=========================================")

    # print submissions if comments not empty
    
    
    return submissions


if __name__ == "__main__":
    submissions = aia_utils.read_teams_aias()
    submissions = test(submissions)
    print(submissions)
    submissions.to_csv("marksheets.csv")
