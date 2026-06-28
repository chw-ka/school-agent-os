import json


def get_components_by_types(root, type):
    components = []
    if "$Type" in root and root["$Type"] == type:
        components.append(root)
    if "$Components" in root:
        for sub in root["$Components"]:
            components += get_components_by_types(sub, type)
    return components


def get_number_of_components(components):
    count = 0
    for screen_name in components:
        form = components[screen_name]["Properties"]
        count += len(get_all_ids(form))
    return count


def get_all_ids(component):
    ids = []
    if component["Uuid"] != "0":
        ids.append(component["Uuid"])
    if "$Components" in component:
        for sub in component["$Components"]:
            ids += get_all_ids(sub)
    return ids


def get_all_types(component):
    types = []
    if "$Type" in component:
        types.append(component["$Type"])
    if "$Components" in component:
        for sub in component["$Components"]:
            types += get_all_types(sub)
    return types


def get_all_components_by_type(components, type):
    results = []
    for screen_name in components:
        form = components[screen_name]["Properties"]
        results += get_components_by_types(form, type)
    return results


def get_number_of_type(components, check_type):
    return len(get_all_components_by_type(components, check_type))


def get_number_of_renamed_type(components, check_type):
    return sum(
        1 for c in get_all_components_by_type(components, check_type)
        if check_type not in c["$Name"]
    )


def assert_has_type(components, check_types):
    for screen_name in components:
        form = components[screen_name]["Properties"]
        types_in_components = get_all_types(form)
        for t in check_types:
            if t not in types_in_components:
                return False
    return True


def assert_has_renamed_type(components, check_type):
    return any(
        check_type not in c["$Name"]
        for c in get_all_components_by_type(components, check_type)
    )


def assert_has_properties_changed_type(components, component_type, property_name):
    return any(
        property_name in c
        for c in get_all_components_by_type(components, component_type)
    )


def assert_has_properties_value(components, component_type, property_name, property_value):
    return any(
        c.get(property_name) == property_value
        for c in get_all_components_by_type(components, component_type)
    )


def assert_no_copycat_components(submissions):
    id_dicts = {}
    copycat_list = set()
    for idx, row in submissions.iterrows():
        components = json.loads(row["components"])
        student = str(row["class"]) + str(row["classnumber"])
        for screen_name in components:
            form = components[screen_name]["Properties"]
            for id_ in get_all_ids(form):
                if id_ in id_dicts and id_dicts[id_] != student:
                    copycat_list.add((id_dicts[id_], student))
                else:
                    id_dicts[id_] = student
    for orig, copier in copycat_list:
        print(f"Copycat detected: {copier} copied from {orig}")
