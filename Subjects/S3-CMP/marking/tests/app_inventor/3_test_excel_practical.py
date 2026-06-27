from excel_utils import mark_excel, parse_formula, parse_range


def marking_function(workbook):
    marks = 0
    comments = ""
    submarks = [0, 0, 0, 0, 0, 0, 0, 0, 0]

    active_sheet = workbook.active

    v = str(active_sheet['L2'].value)
    function_name, arguments = parse_formula(v)
    if v is None:
        comments += "L2: No formula\n"
    elif function_name != "SUM":
        comments += "L2: Wrong function\n"
    else:
        range = parse_range(arguments[0])
        if range[0] != "C" and range[2] != "C":
            marks += 1
            submarks[0] = 1
            comments += "L2: Wrong range\n"
        elif range[1] > 2 or range[3] < 31:
            marks += 2
            submarks[0] = 2
            comments += "L2: Range is not including all the items\n"
        else:
            marks += 3
            submarks[0] = 3

    v = str(active_sheet['L3'].value)
    function_name, arguments = parse_formula(v)
    if v is None:
        comments += "L3: No formula\n"
    elif function_name != "COUNT":
        comments += "L3: Wrong function\n"
    else:
        range = parse_range(arguments[0])
        if range[0] not in ["A", "B", "C", "D", "E", "F"] and range[2] not in ["A", "B", "C", "D", "E", "F"]:
            marks += 1
            submarks[1] = 1
            comments += "L3: Wrong range\n"
        elif range[1] > 2 or range[3] < 31:
            marks += 2
            submarks[1] = 2
            comments += "L3: Range is not including all the items\n"
        else:
            marks += 3
            submarks[1] = 3

    v = str(active_sheet['L4'].value)
    function_name, arguments = parse_formula(v)
    if v is None:
        comments += "L4: No formula\n"
    elif function_name != "AVERAGE":
        comments += "L4: Wrong function\n"
    else:
        range = parse_range(arguments[0])
        if range[0] not in ["D"] and range[2] not in ["D"]:
            marks += 1
            submarks[2] = 1
            comments += "L4: Wrong range\n"
        elif range[1] > 2 or range[3] < 31:
            marks += 2
            submarks[2] = 2
            comments += "L4: Range is not including all the items\n"
        else:
            marks += 3
            submarks[2] = 3

    v = str(active_sheet['L5'].value)
    function_name, arguments = parse_formula(v)
    if v is None:
        comments += "L5: No formula\n"
    elif function_name != "MAX":
        comments += "L5: Wrong function\n"
    else:
        range = parse_range(arguments[0])
        if range[0] not in ["D"] and range[2] not in ["D"]:
            marks += 1
            submarks[3] = 1
            comments += "L5: Wrong range\n"
        elif range[1] > 2 or range[3] < 31:
            marks += 2
            submarks[3] = 2
            comments += "L5: Range is not including all the items\n"
        else:
            marks += 3
            submarks[3] = 3

    v = str(active_sheet['L6'].value)
    function_name, arguments = parse_formula(v)
    if v is None:
        comments += "L6: No formula\n"
    elif function_name != "MIN":
        comments += "L6: Wrong function\n"
    else:
        range = parse_range(arguments[0])
        if range[0] not in ["D"] and range[2] not in ["D"]:
            marks += 1
            submarks[4] = 1
            comments += "L6: Wrong range\n"
        elif range[1] > 2 or range[3] < 31:
            marks += 2
            submarks[4] = 2
            comments += "L6: Range is not including all the items\n"
        else:
            marks += 3
            submarks[4] = 3

    v = str(active_sheet['L9'].value)
    function_name, arguments = parse_formula(v)
    if v is None:
        comments += "L9: No formula\n"
    elif function_name != "SUMIF":
        comments += "L9: Wrong function\n"
    elif len(arguments) != 3:
        marks += 1
        submarks[5] = 1
        comments += "L9: Wrong number of arguments\n"
    else:
        range = parse_range(arguments[0])
        range3 = parse_range(arguments[2])
        if range[0] not in ["H"] or range[2] not in ["H"]:
            marks += 1
            submarks[5] = 1
            comments += "L9: Wrong range\n"
        elif range[1] > 2 or range[3] < 31:
            marks += 3
            submarks[5] = 3
            comments += "L9: Range is not including all the items\n"
        elif arguments[1] != "L8":
            marks += 3
            submarks[5] = 3
            comments += "L9: Wrong range\n"
        elif range3[0] not in ["C"] and range3[2] not in ["C"]:
            marks += 3
            submarks[5] = 3
            comments += "L9: Wrong range\n"
        elif range3[1] > 2 or range3[3] < 31:
            marks += 3
            submarks[5] = 3
            comments += "L9: Range is not including all the items\n"
        else:
            marks += 5
            submarks[5] = 5

    v = str(active_sheet['L10'].value)
    function_name, arguments = parse_formula(v)
    if v is None:
        comments += "L10: No formula\n"
    elif function_name != "COUNTIF":
        comments += "L10: Wrong function\n"
    else:
        range = parse_range(arguments[0])
        if range[0] not in ["D"] or range[2] not in ["D"]:
            marks += 1
            submarks[6] = 1
            comments += "L10: Wrong range\n"
        elif range[1] > 2 or range[3] < 31:
            marks += 3
            submarks[6] = 3
            comments += "L10: Range is not including all the items\n"
        elif arguments[1] != "\"<=30\"":
            marks += 3
            submarks[6] = 3
            comments += "L10: Wrong criteria\n"
        else:
            marks += 5
            submarks[6] = 5

    v = str(active_sheet['L12'].value)
    function_name, arguments = parse_formula(v)
    if v is None:
        comments += "L12: No formula\n"
    elif function_name != "VLOOKUP":
        comments += "L12: Wrong function\n"
    else:
        range = parse_range(arguments[1])
        if len(arguments) < 3:
            marks += 1
            submarks[7] = 1
            comments += "L12: Wrong number of arguments\n"
        elif range[0] not in ["A"] or range[2] < "B":
            marks += 1
            submarks[7] = 1
            comments += "L12: Wrong range\n"
        elif range[1] > 2 or range[3] < 31:
            marks += 3
            submarks[7] = 3
            comments += "L12: Range is not including all the items\n"
        elif arguments[0] != "L11" or arguments[2] != "2":
            marks += 3
            submarks[7] = 3
            comments += "L12: Wrong criteria\n"
        else:
            marks += 5
            submarks[7] = 5

    v = str(active_sheet['G2'].value)
    function_name, arguments = parse_formula(v)
    if v is None:
        comments += "G2: No formula\n"
    elif function_name != "_xlfn.RANK.EQ" and function_name != "RANK":
        comments += "G2: Wrong function\n"
    else:
        range = parse_range(arguments[1])
        if len(arguments) < 3:
            marks += 1
            submarks[8] = 1
            comments += "G2: Wrong number of arguments\n"
        elif range[0] not in ["F"] or range[2] not in ["F"]:
            marks += 1
            submarks[8] = 1
            comments += "G2: Wrong range\n"
        elif range[1] > 2 or range[3] < 31:
            marks += 3
            submarks[8] = 3
            comments += "G2: Range is not including all the items\n"
        elif arguments[0] != "F2" or arguments[2] != "0":
            marks += 3
            submarks[8] = 3
            comments += "G2: Wrong criteria\n"
        else:
            marks += 5
            submarks[8] = 5

    return marks, comments, submarks


assignment = "中一級下學期實習試"
mark_excel(assignment, marking_function)
