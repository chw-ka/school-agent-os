import ev3_utils as ev3
import re


def marking(data):
    marks = 2
    submarks = [2, 0, 0, 0, 0]
    comments = ""
    # 2 marks: show a sad face on screen whenever you start the program"
    if "brick.showImage(images.expressionsSad)" in data:
        marks += 2
        submarks[1] = 2
    else:
        comments += "Missing code to show sad face at the start of the program.\n"

    # 2 marks: show a smiley face after touch sensor is pressed
    if 'sensors.touch1.onEvent(ButtonEvent.Pressed, function () {\n' in data and ('brick.showImage(images.expressionsBigSmile)' in data or 'brick.showImage(images.expressionsSmile)' in data):
        marks += 2
        submarks[2] = 2
    elif 'sensors.touch1.onEvent(ButtonEvent.Pressed, function () {\n' in data:
        marks += 1
        submarks[2] = 1
        comments += "Missing code to show smiley face.\n"
    elif 'brick.showImage(images.expressionsBigSmile)' in data or 'brick.showImage(images.expressionsSmile)' in data:
        marks += 1
        submarks[2] = 1
        comments += "Missing code to show smiley face when touch sensor is pressed.\n"
    else:
        comments += "Missing code to show smiley face after touch sensor is pressed.\n"

    # 2 marks: turn 2 motors on when touch sensor is pressed
    match = re.search(r"motors\.largeBC\.tank\((\d+),\s*(\d+)\)", data)
    if match:
        param1 = int(match.group(1))
        param2 = int(match.group(2))
        if param1 == param2:
            marks += 2
            submarks[3] = 2
        else:
            marks += 1
            submarks[3] = 1
            comments += "The first and second parameters of motors.largeBC.tank() are not the same.\n"
    else:
        comments += "Unable to find motors.largeBC.tank() function call.\n"

    # 2 marks (bonus): if smiley face already shown on screen, change back to sad face and stop the motors
    if "if (motors.largeB.speed() == 0) {" in data and "brick.showImage(images.expressionsSad)" in data:
        marks += 2
        submarks[4] = 2
    else:
        comments += "Missing code to show sad face and stop motors when touch sensor is pressed again.\n"

    return marks, comments, submarks


ev3.mark_ev3("makecode_task1", marking_function=marking)
