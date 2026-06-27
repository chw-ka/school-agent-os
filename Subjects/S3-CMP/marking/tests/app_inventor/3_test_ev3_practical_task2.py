import ev3_utils as ev3


def marking(data):
    marks = 0
    submarks = [0, 0, 0, 0]
    comments = ""
    # match "motors.largeBC.tank()"
    if "motors.largeBC.tank(45, 45, 1.4, MoveUnit.Seconds)" in data and "motors.largeBC.tank(45, 45, 1.6, MoveUnit.Seconds)" in data and "motors.largeBC.tank(45, 45, 3, MoveUnit.Seconds)" in data:
        marks += 5
        submarks[0] = 5
    elif data.count("motors.largeBC.tank(45, 45") == 3:
        marks += 3
        submarks[0] = 3
        comments += "Some duration(s) of move forward is/are incorrect.\n"
    elif data.count("motors.largeBC.tank(45, 45") != 3:
        marks += 1
        submarks[0] = 1
        comments += "Some move forward code is missing.\n"
    else:
        comments += "Incorrect/Missing move forward code.\n"

    if "motors.largeBC.tank(-12, 12, 1.59, MoveUnit.Seconds)" in data or "motors.largeBC.tank(-12, 12, 1.6, MoveUnit.Seconds)" in data or "motors.largeBC.tank(-12, 12, 1.58" in data:
        marks += 5
        submarks[1] = 5
    elif "motors.largeBC.tank(-12, 12" in data:
        marks += 3
        submarks[1] = 3
        comments += "Duration of turn left is incorrect.\n"
    else:
        comments += "Incorrect/Missing turn left code.\n"

    if "motors.largeBC.tank(12, -12, 1.59, MoveUnit.Seconds)" in data or "motors.largeBC.tank(12, -12, 1.6, MoveUnit.Seconds)" in data or "motors.largeBC.tank(12, -12, 1.58" in data:
        marks += 5
        submarks[2] = 5
    elif "motors.largeBC.tank(12, -12" in data:
        marks += 3
        submarks[2] = 3
        comments += "Duration of turn right is incorrect.\n"
    else:
        comments += "Incorrect/Missing turn right code.\n"

    if "brick.buttonEnter.onEvent(ButtonEvent.Pressed" in data:
        marks += 5
        submarks[3] = 5
    elif ".onEvent(ButtonEvent.Pressed" in data:
        marks += 3
        submarks[3] = 3
    else:
        comments += "Incorrect/Missing button pressed code.\n"

    return marks, comments, submarks


ev3.mark_ev3("practical_task2", marking_function=marking)
