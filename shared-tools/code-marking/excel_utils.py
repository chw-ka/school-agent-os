"""Utilities for marking Excel (.xlsx) submissions."""

import re
from os import getcwd, listdir, path

import pandas as pd
from openpyxl import load_workbook


def scan_and_mark(folder_path, marksheet, marking_function):
    files_path = path.join(getcwd(), "attachments", folder_path)
    for f in sorted(listdir(files_path)):
        if not path.isdir(path.join(files_path, f)) and f.endswith(".xlsx"):
            mark_submission(folder_path, f, marksheet, marking_function)


def mark_submission(folder_path, submission, marksheet, marking_function):
    wb = load_workbook(path.join(getcwd(), "attachments", folder_path, submission))
    class_name = submission[0:2]
    class_number = int(submission[2:4])

    marks, comments, submarks = marking_function(wb)
    wb.close()

    mask = (marksheet["class"] == class_name) & (marksheet["classnumber"] == class_number)
    marksheet.loc[mask, "marks"] = marks
    marksheet.loc[mask, "comments"] = str(comments)
    marksheet.loc[mask, "submarks"] = str(submarks)


def mark_excel(marksheet_name="marksheet", marking_function=None):
    marksheet = pd.read_csv(f"marksheets/marksheet_{marksheet_name}.csv")
    marksheet["marks"] = 0
    print("reading...", marksheet_name)
    scan_and_mark(marksheet_name, marksheet, marking_function)
    marksheet.to_csv(f"records/excel_{marksheet_name}.csv", index=False)


def parse_formula(formula):
    if formula is None or formula[0] != "=":
        return None, []
    formula = formula.replace(" ", "")
    function_name = formula[1:formula.find("(")]
    arguments = formula[formula.find("(") + 1:formula.find(")")].split(",")
    return function_name, arguments


def parse_range(range_str):
    """Parse an Excel range string into [col_start, row_start, col_end, row_end]."""
    if ":" not in range_str:
        parts = re.match(r"([A-Z]+)([0-9]*)", range_str)
        if parts is None:
            return None
        g = list(parts.groups())
        g[1] = 1 if g[1] == "" else int(g[1])
        return [g[0], g[1], g[0], g[1]]

    parts = re.match(r"[$]*([A-Z]+)[$]*([0-9]*)[:]*[$]*([A-Z]+)[$]*([0-9]*)", range_str)
    if parts is None:
        return None
    g = list(parts.groups())
    g[1] = 1 if g[1] == "" else int(g[1])
    g[3] = 1048576 if g[3] == "" else int(g[3])
    return g
