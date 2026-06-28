import ev3_utils as ev3
import re


def marking(data):
    # (2 marks) Submit a (.uf2) program
    marks = 2
    submarks = [2, 0, 0, 0, 0]
    comments = ""
    # checking automated door program:
    '''let n = 0
n = 20
forever(function () {
    if (sensors.ultrasonic4.distance() < n) {
        if (motors.largeA.angle() >= 0) {
            motors.largeA.run(10, -90, MoveUnit.Degrees)
        }
    } else {
        if (motors.largeA.angle() <= -90) {
            motors.largeA.run(10, 90, MoveUnit.Degrees)
        }
    }
})'''

    # (2 marks) Defined a variable, the variable name can be any name.
    if re.search(r'\blet\s+\w+\s*=', data):
        marks += 2
        submarks[1] = 2
    else:
        comments += "Missing code to define a variable.\n"

    # (2 marks) Using forever loop
    if "forever(function () {" in data:
        marks += 2
        submarks[2] = 2
    else:
        comments += "Missing code to use forever loop.\n"

    # (2 marks) Checking distance by ultrasonic sensor
    if "if (sensors.ultrasonic4.distance() <" in data:
        marks += 2
        submarks[3] = 2
    else:
        comments += "Missing code to check distance by ultrasonic sensor.\n"

    # (2 marks) The motor can open and close the door
    if "motors.largeA.run(10, -90, MoveUnit.Degrees)" in data and "motors.largeA.run(10, 90, MoveUnit.Degrees)" in data:
        marks += 2
        submarks[4] = 2
    elif "motors.mediumA.run(10, -90, MoveUnit.Degrees)" in data and "motors.mediumA.run(10, 90, MoveUnit.Degrees)" in data:
        marks += 2
        submarks[4] = 2
    else:
        comments += "Missing code to open and close the door.\n"

    return marks, comments, submarks


ev3.mark_ev3("automated_door", marking_function=marking)
