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

        # (5 marks) Call TMIC to classify video data when timer of clock triggered
        remarks = ""
        section_description = "Call TMIC to classify video data when timer of clock triggered"
        section_mark = 0
        if (blockly_util.assert_has_component_event(blockly, "Clock", "Timer")):
            section_mark += 1

            event = blockly_util.get_blocks_by_type_and_mutation(blockly_util.get_all_blocks(blockly), "component_event", [
                ("@component_type", "Clock"),
                ("@event_name", "Timer")
            ])

            blocks = blockly_util.get_blocks_by_type_and_mutation(event, "component_method", [
                ("@component_type", "TeachableMachineImageClassifier"), ("@method_name", "ClassifyVideoData")])
            if (len(blocks) > 0 and blockly_util.match_blocks_subset(blocks[0], {
                "field": {
                    "@name": "COMPONENT_SELECTOR",
                    "#text": "tmic"
                }
            })):
                section_mark += 1
            else:
                remarks += "Missing TeachableMachineImageClassifier.ClassifyVideoData\n"
        else:
            remarks += "Missing Clock.Timer event\n"

        if (section_mark > 1):
            submissions.loc[idx, "marks"] += 5
            submissions.loc[idx, "mark1"] = 5
        else:
            submissions.loc[idx, "marks"] += section_mark
            submissions.loc[idx, "mark1"] = section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, submissions.loc[idx, "mark1"], 5)

        # (5 marks) Handling when the ImageSprite "basket" is collided with ImageSprite "fruit"."
        section_description = "Handling when the ImageSprite basket is collided with ImageSprite fruit."
        section_mark = 0
        if (blockly_util.assert_has_component_event(blockly, "ImageSprite", "CollidedWith")):
            section_mark += 1

            all_blocks = blockly_util.get_all_blocks(blockly)

            event = blockly_util.get_blocks_by_type_and_mutation(all_blocks, "component_event", [
                ("@component_type", "ImageSprite"),
                ("@event_name", "CollidedWith")
            ])

            blocks = blockly_util.get_blocks_by_type_and_mutation(event, "component_set_get", [
                ("@component_type", "ImageSprite"), ("@property_name", "Y")])
            if (len(blocks) > 0):
                section_mark += 1
                if (blockly_util.match_blocks_subset(blocks[0], {
                    "field": {
                        "@name": "NUM",
                        "#text": "0"
                    }
                })):
                    section_mark += 1
                else:
                    remarks += "Failed to set ImageSprite.Y to 0\n"
            else:
                remarks += "Missing setting ImageSprite.Y\n"

            blocks = blockly_util.get_blocks_by_type_and_mutation(event, "component_set_get", [
                ("@component_type", "Label"), ("@property_name", "Text")])
            if (len(blocks) > 0):
                section_mark += 1
                if (blockly_util.match_blocks_subset(blocks[0], {
                    "value": {
                        "@name": "VALUE",
                        "block": {
                            "@type": "math_add",
                        }
                    }
                })):
                    section_mark += 1
                else:
                    remarks += "Missing Add block in setting Label.Text\n"

                if (blockly_util.match_blocks_subset(blocks[0], {
                    "value": {
                        "@name": "VALUE",
                        "block": {
                            "@type": "math_add",
                            "value": [
                                {
                                    "@name": "NUM0",
                                    "block": {
                                        "@type": "component_set_get",
                                        "mutation": {
                                            "@component_type": "Label",
                                            "@set_or_get": "get",
                                            "@property_name": "Text",
                                            "@is_generic": "false",
                                            "@instance_name": "score"
                                        },
                                        "field": [
                                            {
                                                "@name": "COMPONENT_SELECTOR",
                                                "#text": "score"
                                            },
                                            {
                                                "@name": "PROP",
                                                "#text": "Text"
                                            }
                                        ]
                                    }
                                },
                                {
                                    "@name": "NUM1",
                                    "block": {
                                        "@type": "math_number",
                                        "field": {
                                            "@name": "NUM",
                                            "#text": "1"
                                        }
                                    }
                                }
                            ]
                        }
                    }
                })):
                    section_mark += 1
                else:
                    remarks += "Missing setting Label.Text to score + 1\n"

            else:
                remarks += "Missing setting Label.Text\n"

        else:
            remarks += "Missing ImageSprite.CollidedWith event\n"

        if (section_mark > 4):
            submissions.loc[idx, "marks"] += 5
            submissions.loc[idx, "mark2"] = 5
        elif (section_mark > 1):
            submissions.loc[idx, "marks"] += 3
            submissions.loc[idx, "mark2"] = 3
        else:
            submissions.loc[idx, "marks"] += section_mark
            submissions.loc[idx, "mark2"] = section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, submissions.loc[idx, "mark2"], 5)

        # (5 marks) Change the ImageSprite "fruit" back to top when the ImageSprite "fruit" reaches the edge.
        section_description = "Change the ImageSprite fruit back to top when the ImageSprite fruit reaches the edge."
        section_mark = 0
        if (blockly_util.assert_has_component_event(blockly, "ImageSprite", "EdgeReached")):
            section_mark += 1
            event = blockly_util.get_blocks_by_type_and_mutation(blockly_util.get_all_blocks(blockly), "component_event", [
                ("@component_type", "ImageSprite"),
                ("@event_name", "EdgeReached")
            ])

            blocks = blockly_util.get_blocks_by_type_and_mutation(event, "component_set_get", [
                ("@component_type", "ImageSprite"), ("@property_name", "Y")])
            if (len(blocks) > 0):
                section_mark += 1
                if (blockly_util.match_blocks_subset(blocks[0], {
                    "value": {
                        "@name": "VALUE",
                        "block": {
                            "@type": "math_number",
                            "field": {
                                "@name": "NUM",
                                "#text": "0"
                            }
                        }
                    }
                })):
                    section_mark += 1
                else:
                    remarks += "Failed to set ImageSprite.Y to 0\n"
            else:
                remarks += "Missing setting ImageSprite.Y\n"
            
            if (section_mark == 1):
                moveto_blocks = blockly_util.get_blocks_by_type_and_mutation(event, "component_method", [
                    ("@component_type", "ImageSprite"), ("@method_name", "MoveTo")])
                if (len(moveto_blocks) > 0):
                    section_mark += 1
        else:
            remarks += "Missing ImageSprite.EdgeReached event\n"

        if (section_mark == 3):
            submissions.loc[idx, "marks"] += 5
            submissions.loc[idx, "mark3"] = 5
        elif (section_mark > 1):
            submissions.loc[idx, "marks"] += 3
            submissions.loc[idx, "mark3"] = 3
        else:
            submissions.loc[idx, "marks"] += section_mark
            submissions.loc[idx, "mark3"] = section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, submissions.loc[idx, "mark3"], 5)

        # (5 marks) Handling move left and right by using tmic classification
        section_description = "Handling move left and right by using tmic classification"
        section_mark = 0
        if (blockly_util.assert_has_component_event(blockly, "TeachableMachineImageClassifier", "GotClassification")):
            section_mark += 1
            event = blockly_util.get_blocks_by_type_and_mutation(blockly_util.get_all_blocks(blockly), "component_event", [
                ("@component_type", "TeachableMachineImageClassifier"),
                ("@event_name", "GotClassification")
            ])

            if_block = blockly_util.get_blocks_by_type_and_mutation(event, "controls_if", [])
            if (len(if_block) > 0):
                section_mark += 1
                if (blockly_util.match_blocks_subset(if_block[0], {
                    "value": {
                        "@name": "IF0",
                        "block": {
                            "field": {
                                "@name": "OP",
                                "#text": "GT"
                            },
                        }
                    }
                })) or (blockly_util.match_blocks_subset(if_block[0], {
                    "value": {
                        "@name": "IF0",
                        "block": {
                            "field": {
                                "@name": "OP",
                                "#text": "LT"
                            },
                        }
                    }
                })) or (blockly_util.match_blocks_subset(if_block[0], {
                    "value": {
                        "@name": "IF0",
                        "block": {
                            "field": {
                                "@name": "OP",
                                "#text": "LTE"
                            },
                        }
                    }
                })) or (blockly_util.match_blocks_subset(if_block[0], {
                    "value": {
                        "@name": "IF0",
                        "block": {
                            "field": {
                                "@name": "OP",
                                "#text": "GTE"
                            },
                        }
                    }
                })):
                    section_mark += 1
                    lookup_blocks = blockly_util.get_blocks_by_type_and_mutation(if_block[0], "dictionaries_lookup", [])
                    if (len(lookup_blocks) > 1):
                        section_mark += 1
                        texts = blockly_util.get_blocks_by_type_and_mutation(lookup_blocks[0], "text", [])
                        if (len(texts) > 0 and texts[0]["field"]["#text"] == "Left" or texts[0]["field"]["#text"] == "Right"):
                            section_mark += 1
                        texts = blockly_util.get_blocks_by_type_and_mutation(lookup_blocks[1], "text", [])
                        if (len(texts) > 0 and texts[0]["field"]["#text"] == "Left" or texts[0]["field"]["#text"] == "Right"):
                            section_mark += 1
                        results_blocks = blockly_util.get_blocks_by_type_and_mutation(lookup_blocks[0], "lexical_variable_get", [
                            ("eventparam", {"@name": "result"})
                        ])
                        if (len(results_blocks) > 0):
                            section_mark += 1
                        results_blocks = blockly_util.get_blocks_by_type_and_mutation(lookup_blocks[1], "lexical_variable_get", [
                            ("eventparam", {"@name": "result"})
                        ])
                        if (len(results_blocks) > 0):
                            section_mark += 1

                        set_heading_blocks = blockly_util.get_blocks_by_type_and_mutation(if_block[0], "component_set_get", [
                            ("@component_type", "ImageSprite"), ("@property_name", "Heading")])
                        if (len(set_heading_blocks) > 1):
                            section_mark += 1
                        set_speed_blocks = blockly_util.get_blocks_by_type_and_mutation(if_block[0], "component_set_get", [
                            ("@component_type", "ImageSprite"), ("@property_name", "Speed")])
                        if (len(set_speed_blocks) > 1):
                            section_mark += 1

                    else:
                        remarks += "Missing dictionary_lookup block\n"
                else:
                    remarks += "Missing logic_compare block with GT or LT operator\n"

            else:
                remarks += "Missing if block\n"

        else:
            remarks += "Missing Button.Click event\n"

        if (section_mark > 9):
            submissions.loc[idx, "marks"] += 5
            submissions.loc[idx, "mark4"] = 5
        elif (section_mark > 1):
            submissions.loc[idx, "marks"] += 3
            submissions.loc[idx, "mark4"] = 3
        else:
            submissions.loc[idx, "marks"] += section_mark
            submissions.loc[idx, "mark4"] = section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, submissions.loc[idx, "mark4"], 5)

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