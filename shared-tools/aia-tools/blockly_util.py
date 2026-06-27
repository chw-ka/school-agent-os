import json

# block @type values:
#   component_event   — e.g. when Button1.Click
#   component_set_get — e.g. Button1.Text / set Button1.Text to "Hello"
#   component_method  — e.g. call Button1.Click
#   controls_if       — if/then/else


def match_blocks_subset(block, match):
    """Recursive subset match: returns True if match is a structural subset of block."""
    if isinstance(match, dict) and isinstance(block, dict):
        return all(k in block and match_blocks_subset(block[k], match[k]) for k in match)
    if isinstance(match, list) and isinstance(block, list):
        return all(
            any(match_blocks_subset(b, m) for b in block)
            for m in match
        )
    return match == block


def get_all_blocks(blockly):
    """Flatten all top-level blocks across all screens into a single list."""
    blocks_list = []
    for screen_name in blockly:
        if "xml" not in blockly[screen_name] or "block" not in blockly[screen_name]["xml"]:
            continue
        blocks = blockly[screen_name]["xml"]["block"]
        if isinstance(blocks, list):
            blocks_list += blocks
        else:
            blocks_list.append(blocks)
    return blocks_list


def get_number_of_screens(blocks):
    return len(blocks) if isinstance(blocks, list) else 1


def get_all_ids(blocks):
    ids = []
    if isinstance(blocks, list):
        for block in blocks:
            ids += get_all_ids(block)
    else:
        if "@id" in blocks:
            ids.append(blocks["@id"])
        if "statement" in blocks and "block" in blocks["statement"]:
            ids += get_all_ids(blocks["statement"]["block"])
        if "next" in blocks and "block" in blocks["next"]:
            ids += get_all_ids(blocks["next"]["block"])
        if "value" in blocks and "@id" in blocks["value"]:
            ids.append(blocks["value"]["@id"])
    return ids


def get_event_block(blocks, component_type, event_name):
    for block in blocks:
        if match_blocks_subset(block, {
            "@type": "component_event",
            "mutation": {"@event_name": event_name, "@component_type": component_type},
        }):
            return block
    return None


def get_blocks(blocks, subset):
    if blocks is None:
        return []
    blocks_list = []
    if isinstance(blocks, list):
        for block in blocks:
            blocks_list += get_blocks(block, subset)
    else:
        if match_blocks_subset(blocks, subset):
            blocks_list.append(blocks)
        if "statement" in blocks and "block" in blocks["statement"]:
            blocks_list += get_blocks(blocks["statement"]["block"], subset)
        if "next" in blocks and "block" in blocks["next"]:
            blocks_list += get_blocks(blocks["next"]["block"], subset)
        if "value" in blocks and "@id" in blocks["value"]:
            blocks_list += get_blocks(blocks["value"]["block"], subset)
    return blocks_list


def get_if_statement(blocks, compare_op, left_value, right_value):
    if isinstance(blocks, list):
        for block in blocks:
            b = get_if_statement(block, compare_op, left_value, right_value)
            if b is not None:
                return b
    else:
        if match_blocks_subset(blocks, {"@type": "controls_if"}):
            match = {
                "field": {"@name": "OP", "#text": compare_op},
                "value": [{"block": left_value}, {"block": right_value}],
            }
            if "value" not in blocks:
                return blocks
            if isinstance(blocks["value"], list):
                for i, v in enumerate(blocks["value"]):
                    if match_blocks_subset(v["block"], match):
                        return blocks["statement"][i] if isinstance(blocks["statement"], list) else blocks["statement"]
            else:
                if match_blocks_subset(blocks["value"]["block"], match):
                    return blocks["statement"]
            return blocks
        if "statement" in blocks and "block" in blocks["statement"]:
            return get_if_statement(blocks["statement"]["block"], compare_op, left_value, right_value)
        if "next" in blocks and "block" in blocks["next"]:
            return get_if_statement(blocks["next"]["block"], compare_op, left_value, right_value)
        if "value" in blocks and "@id" in blocks["value"]:
            return get_if_statement(blocks["value"]["block"], compare_op, left_value, right_value)
    return None


def get_blocks_by_type(blocks, type, logging=False):
    blocks_list = []
    if isinstance(blocks, list):
        for block in blocks:
            blocks_list += get_blocks_by_type(block, type, logging)
    else:
        if "@type" in blocks and blocks["@type"] == type:
            if logging:
                print("Matched block:", blocks)
            blocks_list.append(blocks)
        for key in ["statement", "next", "value"]:
            if key in blocks:
                sub = blocks[key]
                if isinstance(sub, list):
                    for b in sub:
                        if "block" in b:
                            blocks_list += get_blocks_by_type(b["block"], type, logging)
                elif isinstance(sub, dict) and "block" in sub:
                    blocks_list += get_blocks_by_type(sub["block"], type, logging)
    return blocks_list


def get_blocks_by_type_and_mutation(blocks, type, mutation_check_list, logging=False):
    blocks_list = []
    if isinstance(blocks, list):
        for block in blocks:
            blocks_list += get_blocks_by_type_and_mutation(block, type, mutation_check_list)
    else:
        if "@type" in blocks and blocks["@type"] == type:
            has_mutation = all(
                mt in blocks["mutation"] and (
                    (isinstance(mv, str) and blocks["mutation"][mt] == mv) or
                    str(blocks["mutation"][mt]) in str(mv)
                )
                for mt, mv in mutation_check_list
            )
            if has_mutation:
                blocks_list.append(blocks)
        if "statement" in blocks:
            stmt = blocks["statement"]
            if isinstance(stmt, list):
                for b in stmt:
                    blocks_list += get_blocks_by_type_and_mutation(b["block"], type, mutation_check_list)
            elif "block" in stmt:
                blocks_list += get_blocks_by_type_and_mutation(stmt["block"], type, mutation_check_list)
        if "next" in blocks and "block" in blocks["next"]:
            blocks_list += get_blocks_by_type_and_mutation(blocks["next"]["block"], type, mutation_check_list)
        if "value" in blocks:
            val = blocks["value"]
            if isinstance(val, list):
                for b in val:
                    blocks_list += get_blocks_by_type_and_mutation(b["block"], type, mutation_check_list)
            elif "block" in val:
                blocks_list += get_blocks_by_type_and_mutation(val["block"], type, mutation_check_list)
    return blocks_list


def get_if_block_inside_event(blockly, event_component_type, event_name):
    blocks = get_all_blocks(blockly)
    for block in blocks:
        if (block["@type"] == "component_event"
                and block["mutation"]["@event_name"] == event_name
                and block["mutation"]["@component_type"] == event_component_type):
            statement_block = block["statement"]["block"]
            if statement_block["@type"] == "controls_if":
                return statement_block
            if "next" in statement_block:
                nxt = statement_block["next"]["block"]
                while True:
                    if nxt["@type"] == "controls_if":
                        return nxt
                    if "next" in nxt:
                        nxt = nxt["next"]["block"]
                    else:
                        break
    return None


def check_block_match_mutation(statement_block, type, mutation_check_list):
    if statement_block["@type"] != type:
        return False
    return all(
        mt in statement_block["mutation"] and statement_block["mutation"][mt] == mv
        for mt, mv in mutation_check_list
    )


def has_block_inside_block(block, type, mutation_check_list):
    if isinstance(block, list):
        return any(has_block_inside_block(b, type, mutation_check_list) for b in block)
    if block["@type"] == type:
        if all(
            mt in block["mutation"] and block["mutation"][mt] == mv
            for mt, mv in mutation_check_list
        ):
            return True
    if "statement" in block:
        stmt = block["statement"]
        if isinstance(stmt, list):
            if any(has_block_inside_block(b["block"], type, mutation_check_list) for b in stmt):
                return True
        elif "block" in stmt:
            if has_block_inside_block(stmt["block"], type, mutation_check_list):
                return True
    if "next" in block:
        nxt = block["next"]
        if isinstance(nxt, list):
            if any(has_block_inside_block(b["block"], type, mutation_check_list) for b in nxt):
                return True
        elif "block" in nxt:
            if has_block_inside_block(nxt["block"], type, mutation_check_list):
                return True
    if "value" in block:
        val = block["value"]
        if isinstance(val, list):
            if any(has_block_inside_block(b["block"], type, mutation_check_list) for b in val):
                return True
        elif "@id" in val:
            if has_block_inside_block(val["block"], type, mutation_check_list):
                return True
    return False


def assert_has_component_event(blockly, component_type, event_name):
    for block in get_all_blocks(blockly):
        if "@type" in block and block["@type"] == "component_event":
            m = block.get("mutation", {})
            if m.get("@event_name") == event_name and m.get("@component_type") == component_type:
                return True
    return False


def assert_has_block_inside_event(blockly, event_component_type, event_name, type, mutation_check_list):
    for block in get_all_blocks(blockly):
        if (block["@type"] == "component_event"
                and block["mutation"]["@event_name"] == event_name
                and block["mutation"]["@component_type"] == event_component_type):
            if "statement" in block and "block" in block["statement"]:
                if has_block_inside_block(block["statement"]["block"], type, mutation_check_list):
                    return True
    return False


def assert_has_set_block_inside_event(blockly, event_component_type, event_name, component_type, property_name):
    return assert_has_block_inside_event(
        blockly, event_component_type, event_name,
        "component_set_get", [("@set_or_get", "set"), ("@component_type", component_type), ("@property_name", property_name)],
    )


def assert_has_method_block_inside_event(blockly, event_component_type, event_name, component_type, method_name):
    return assert_has_block_inside_event(
        blockly, event_component_type, event_name,
        "component_method", [("@component_type", component_type), ("@method_name", method_name)],
    )


def assert_has_if_block_inside_event(blockly, event_component_type, event_name):
    return assert_has_block_inside_event(blockly, event_component_type, event_name, "controls_if", [])


def assert_no_copycat_blockly(submissions):
    id_dicts = {}
    copycat_list = set()
    for idx, row in submissions.iterrows():
        blockly = json.loads(row["blockly"])
        student = str(row["class"]) + str(row["classnumber"])
        for screen_name in blockly:
            if "xml" not in blockly[screen_name] or "block" not in blockly[screen_name]["xml"]:
                continue
            for id_ in get_all_ids(blockly[screen_name]["xml"]["block"]):
                if id_ in id_dicts and id_dicts[id_] != student:
                    copycat_list.add((id_dicts[id_], student))
                else:
                    id_dicts[id_] = student
    for orig, copier in copycat_list:
        print(f"Copycat detected: {copier} copied from {orig}")
