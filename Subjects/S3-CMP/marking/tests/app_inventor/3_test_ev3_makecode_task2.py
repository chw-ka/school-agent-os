import ev3_utils as ev3
import re


def marking(data):
    marks = 2
    submarks = [2, 0, 0, 0, 0]
    comments = ""
    # 2 marks: Show a red light whenever you start the program."
    if "brick.setStatusLight(StatusLight.Red)" in data:
        marks += 2
        submarks[1] = 2
    else:
        comments += "Missing code to show red light at the start of the program.\n"

    # 2 marks: Repeatedly change light color follow the following sequence. `Red` --> `Orange` --> `Green` --> `Orange` --> `Red`
    pattern = r"brick\.setStatusLight\(StatusLight\.[a-zA-Z]+\)\n    pause\(\d+\)"
    matches = re.findall(pattern, data)
    if len(matches) >= 4:
        marks += 2
        submarks[2] = 2
    else:
        comments += "The desired light pattern does not occur 4 times in series.\n"

    # 2 marks: Apply different delay between each color change. `2 second (Red)` --> `0.2 second (Orange)` --> `1 second (Green)` --> `0.5 second (Orange)` 
    match = re.search(r"brick\.setStatusLight\(StatusLight\.[a-zA-Z]+\)\n\s+pause\(\d+\)\n\s+brick\.setStatusLight\(StatusLight\.[a-zA-Z]+\)\n\s+pause\(\d+\)\n\s+brick\.setStatusLight\(StatusLight\.[a-zA-Z]+\)\n\s+pause\(\d+\)\n\s+brick\.setStatusLight\(StatusLight\.[a-zA-Z]+\)\n\s+pause\(\d+\)\n\s+brick\.setStatusLight\(StatusLight\.[a-zA-Z]+\)\n\s+pause\(\d+\)", data)
    if match:
        marks += 2
        submarks[3] = 2
    else:
        comments += "Missing code to turn on motors when touch sensor is pressed.\n"

    # 2 marks (bonus): (Bonus) When the motors are already running, reduce the delay time of the red light to 1 second.
    match = re.search(r"pause\([a-zA-Z]+\)", data)
    if match:
        marks += 6
        submarks[2] = 2
        submarks[3] = 2
        submarks[4] = 2
        comments = ""
    else:
        comments += "Missing code to reduce the delay time of the red light to 1 second.\n"

    return marks, comments, submarks


ev3.mark_ev3("makecode_task2", marking_function=marking)
