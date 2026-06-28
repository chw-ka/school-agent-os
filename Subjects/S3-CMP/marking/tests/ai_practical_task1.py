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
        remarks = "[O]: Correct\n[-]: Minor error\n[X]: Major error\n\n"
        section_description = "Insert an ImageSprite `balloon` on the Canvas."
        section_mark = 0
        if (components_util.assert_has_type(components, ["ImageSprite"])):
            section_mark += 1
            if (components_util.assert_has_properties_value(components, "ImageSprite", "$Name", "balloon")):
                section_mark += 0.5
            else:
                remarks += "Rename $Name to \"balloon\" Failed.\n"

            if (components_util.assert_has_properties_value(components, "ImageSprite", "Width", "50")):
                section_mark += 0.5
            else:
                remarks += "Change balloon Width to 50 Failed.\n"

            if (components_util.assert_has_properties_value(components, "ImageSprite", "Height", "70")):
                section_mark += 0.5
            else:
                remarks += "Change balloon Height to 70 Failed.\n"

            if (components_util.assert_has_properties_value(components, "ImageSprite", "X", "135")):
                section_mark += 0.5
            else:
                remarks += "Change balloon X to 135 Failed.\n"

            if (components_util.assert_has_properties_value(components, "ImageSprite", "Y", "150")):
                section_mark += 0.5
            else:
                remarks += "Change balloon Y to 150 Failed.\n"

            if (components_util.assert_has_properties_value(components, "ImageSprite", "Picture", "balloon.png")):
                section_mark += 0.5
            else:
                remarks += "Change balloon Picture to balloon.png Failed.\n"

        else:
            remarks += "Missing components: ImageSprite for balloon\n"
        if (section_mark == 4):
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

        # (5 marks) The balloon moves upward when touched
        section_description = "The balloon moves upward when touched"
        section_mark = 0
        if (blockly_util.assert_has_component_event(blockly, "ImageSprite", "Touched")):
            section_mark += 1
            event = blockly_util.get_blocks_by_type_and_mutation(blockly_util.get_all_blocks(blockly), "component_event", [
                ("@component_type", "ImageSprite"),
                ("@event_name", "Touched")
            ])

            section_mark += 1
            if (blockly_util.match_blocks_subset(event[0], {
                    "statement": {
                        "@name": "DO",
                        "block": {
                            "@type": "component_set_get",
                            "mutation": {
                                "@component_type": "ImageSprite",
                                "@set_or_get": "set",
                                "@property_name": "Y",
                            },
                        }
                    }
            })):
                section_mark += 1
            else:
                remarks += "Missing ImageSprite.Y block\n"

            if (blockly_util.match_blocks_subset(event[0], {
                "value": {
                    "@name": "VALUE",
                    "block": {
                        "@type": "math_subtract",
                    }
                }
            })):
                section_mark += 1
            else:
                remarks += "Missing math_subtract block\n"

            if (blockly_util.match_blocks_subset(event[0], {
                "@name": "B",
                "block": {
                    "@type": "math_number",
                    "field": {
                        "@name": "NUM",
                        "#text": "10"
                    }
                }
            })):
                section_mark += 1
            else:
                remarks += "Missing math_subtract 10 block\n"

            if section_mark == 1:
                blocks = blockly_util.get_blocks_by_type_and_mutation(event[0], "component_method", [
                    ("@component_type", "ImageSprite"),
                    ("@method_name", "MoveTo")
                ])
                if (len(blocks) > 0):
                    section_mark += 1
                    if (blockly_util.match_blocks_subset(blocks[0], {
                            "value": [
                                {
                                    "block": {
                                        "@type": "component_set_get",
                                        "mutation": {
                                            "@component_type": "ImageSprite",
                                            "@set_or_get": "get",
                                            "@property_name": "X",
                                        },
                                    }
                                },
                                {
                                    "block": {
                                        "@type": "math_subtract",
                                        "value": [
                                            {
                                                "block": {
                                                    "@type": "component_set_get",
                                                    "mutation": {
                                                        "@component_type": "ImageSprite",
                                                        "@set_or_get": "get",
                                                        "@property_name": "Y",
                                                    },
                                                }
                                            },
                                            {
                                                "block": {
                                                    "@type": "math_number",
                                                    "field": {
                                                        "@name": "NUM",
                                                        "#text": "10"
                                                    }
                                                }
                                            }
                                        ]
                                    }
                                }
                            ]

                    })):
                        section_mark += 3
                    else:
                        remarks += "Error: Wrong MoveTo block settings\n"
                else:
                    remarks += "Missing ImageSprite.Y block\n"

        else:
            remarks += "Missing event: balloon.Touched\n"

        if (section_mark == 5):
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

        # (5 marks) The balloon breaks when reaches top
        section_description = "The balloon breaks when reaches top"
        section_mark = 0
        if (blockly_util.assert_has_component_event(blockly, "ImageSprite", "EdgeReached")):
            section_mark += 1
            all_blocks = blockly_util.get_all_blocks(blockly)
            events = blockly_util.get_blocks_by_type_and_mutation(
                all_blocks, "component_event", [("@component_type", "ImageSprite"), ("@event_name", "EdgeReached")])
            if (blockly_util.assert_has_set_block_inside_event(blockly, "ImageSprite", "EdgeReached", "ImageSprite", "Picture")):
                section_mark += 1
                blocks = blockly_util.get_blocks_by_type_and_mutation(events[0], "component_set_get", [(
                    "@component_type", "ImageSprite"), ("@set_or_get", "set"), ("@property_name", "Picture")])
                if (len(blocks) > 0):
                    section_mark += 1
                    if (blockly_util.match_blocks_subset(blocks[0], {
                        "value": {
                            "@name": "VALUE",
                            "block": {
                                "@type": "helpers_assets",
                                "field": {
                                    "@name": "ASSET",
                                    "#text": "balloon_break.png"
                                }
                            }
                        },
                    })):
                        section_mark += 1
                    else:
                        remarks += "Missing balloon_break.png block\n"
        else:
            remarks += "Missing event: car.Touched\n"

        if (section_mark == 4):
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
