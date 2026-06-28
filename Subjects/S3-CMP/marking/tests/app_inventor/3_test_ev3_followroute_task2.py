import ev3_utils as ev3
import re


def marking(data):
    # (2 marks) Submit a (.uf2) program
    marks = 0
    submarks = [0, 0, 0, 0, 0]
    comments = ""
    # (2 marks) The tank can move along the diagonal correctly (direction and distance)
    if "motors.largeBC.tank(50, 50, 6.8, MoveUnit.Seconds)" in data or "motors.largeBC.tank(50, 50, 6.79, MoveUnit.Seconds)" in data or "motors.largeBC.tank(50, 50, 6.788, MoveUnit.Seconds)" in data:
        marks += 2
        submarks[0] = 2
    else:
        comments += "Missing code to move the tank along the diagonal correctly.\n"

    # (2 makrs) The tank moves after the button "ENTER" pressed.
    if "brick.buttonEnter.onEvent(ButtonEvent.Pressed, function () {" in data:
        marks += 2
        submarks[1] = 2
    elif ".onEvent(ButtonEvent.Pressed, function () {" in data:
        marks += 1
        submarks[1] = 1
        comments += "Missing code to move the tank after the button ENTER is pressed.\n"
    else:
        comments += "Missing code to move the tank after the button ENTER is pressed.\n"

    # (2 marks) The tank can move the 1st 60cm.
    if "motors.largeBC.tank(50, 50, 2.4, MoveUnit.Seconds)" in data:
        marks += 2
        submarks[2] = 2
    else:
        comments += "Missing code to move the tank the 1st 60cm.\n"

    # (2 marks) The tank can rotate the 1st 90 degree.
    if "sensors.gyro2.reset()" in data and "motors.stopAll()" in data and ("motors.largeBC.tank(20, -20)" in data or "motors.largeBC.tank(10, -10)" in data) and "while (sensors.gyro2.angle() < 90) {" in data:
        marks += 2
        submarks[3] = 2
    else:
        comments += "Missing code to rotate the tank 90 degrees clockwise.\n"

    # (2 marks) The tank can finish all 60cm paths and rotations.
    if data.count("sensors.gyro2.reset()") == 4 and data.count("motors.stopAll()") == 4 and data.count("while (sensors.gyro2.angle() < 90) {") == 2 and data.count("while (sensors.gyro2.angle() > -90) {") == 1 and data.count("while (sensors.gyro2.angle() < 135) {") == 1:
        marks += 2
        submarks[4] = 2
    else:
        comments += "Missing code to finish the whole route.\n"


    return marks, comments, submarks


ev3.mark_ev3("followroute_task2", marking_function=marking)
