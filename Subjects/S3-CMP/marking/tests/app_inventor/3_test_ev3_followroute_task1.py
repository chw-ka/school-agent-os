import ev3_utils as ev3
import re


def marking(data):
    # (2 marks) Submit a (.uf2) program
    marks = 2
    submarks = [2, 0, 0, 0, 0]
    comments = ""
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

    # (2 marks) The tank can rotate the 1st 90 degree clockwise.
    if "sensors.gyro2.reset()" in data and "motors.stopAll()" in data and ("motors.largeBC.tank(20, -20)" in data or "motors.largeBC.tank(10, -10)" in data) and "while (sensors.gyro2.angle() < 90) {" in data:
        marks += 2
        submarks[3] = 2
    else:
        comments += "Missing code to rotate the tank 90 degrees clockwise.\n"

    # (2 marks) The tank can finish the whole route.
    # check "sensors.gyro2.reset()" appears 6 times
    if data.count("sensors.gyro2.reset()") == 6 and data.count("motors.stopAll()") == 6 and data.count("while (sensors.gyro2.angle() < 90) {") == 4 and data.count("while (sensors.gyro2.angle() > -90) {") == 2:
        marks += 2
        submarks[4] = 2
    elif data.count("for (let i = 0; i < 2; i++) {") == 3 and data.count("sensors.gyro2.reset()") == 3 and data.count("motors.stopAll()") == 3 and data.count("while (sensors.gyro2.angle() < 90) {") == 2 and data.count("while (sensors.gyro2.angle() > -90) {") == 1:
        marks += 2
        submarks[4] = 2
    else:
        comments += "Missing code to finish the whole route.\n"


    return marks, comments, submarks


ev3.mark_ev3("followroute_task1", marking_function=marking)
