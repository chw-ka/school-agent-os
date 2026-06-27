"""
EV3 (MakeCode/PXT) marking utilities.

Prerequisite: export .uf2 projects from pxt-ev3, unzip into ev3/<assignment>/<student>/main.ts.
Scripts run from the subject's marking/ directory.
"""

from os import getcwd, listdir, path
import pandas as pd


def scan_and_mark(folder_path, marksheet, marking_function):
    files_path = path.join(getcwd(), "ev3", folder_path)
    for f in sorted(listdir(files_path)):
        if path.isdir(path.join(files_path, f)):
            mark_submission(folder_path, f, marksheet, marking_function)


def mark_submission(folder_path, submission, marksheet, marking_function):
    print("marking...", submission)
    main_ts = path.join(getcwd(), "ev3", folder_path, submission, "main.ts")
    with open(main_ts) as f:
        data = f.read()

    class_name = submission[0:2]
    class_number = int(submission[2:4])
    marks, comments, submarks = marking_function(data)

    print("marks:", marks)
    print("comments:", comments)

    mask = (marksheet["class"] == class_name) & (marksheet["classnumber"] == class_number)
    marksheet.loc[mask, "marks"] = marks
    marksheet.loc[mask, "comments"] = comments
    marksheet.loc[mask, "submarks"] = str(submarks)


def mark_ev3(marksheet_name="marksheet", marking_function=None):
    marksheet = pd.read_csv(f"marksheets/marksheet_{marksheet_name}.csv")
    marksheet["marks"] = 0
    print("reading...", marksheet_name)
    scan_and_mark(marksheet_name, marksheet, marking_function)
    marksheet.to_csv(f"records/ev3_{marksheet_name}.csv", index=False)
