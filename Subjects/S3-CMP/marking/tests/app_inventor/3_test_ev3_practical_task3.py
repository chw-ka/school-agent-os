import ev3_utils as ev3
import re


def marking(data):
    marks = 0
    submarks = [0, 0, 0, 0, 0]
    comments = ""
    # match "motors.largeBC.tank()"
    if "motors.largeBC.tank(30, 30, 4.38, MoveUnit.Seconds)" in data and "motors.largeBC.tank(30, 30, 3.54, MoveUnit.Seconds)" in data and "motors.largeBC.tank(30, 30, 3.12, MoveUnit.Seconds)" in data:
        marks += 5
        submarks[0] = 5
    elif data.count("motors.largeBC.tank(30, 30") == 3:
        marks += 3
        submarks[0] = 3
        comments += "Some duration(s) of move forward is/are incorrect.\n"
    elif data.count("motors.largeBC.tank(30, 30") != 3:
        marks += 1
        submarks[0] = 1
        comments += "Some move forward code is missing.\n"
    else:
        comments += "Incorrect/Missing move forward code.\n"

    if data.count("sensors.gyro2.reset()") == 2:
        marks += 5
        submarks[1] = 5
    elif data.count("sensors.gyro2.reset()") == 1:
        marks += 3
        submarks[1] = 3
        comments += "one of the Gyro reset code is missing.\n"
    else:
        comments += "Missing gyro reset code.\n"

    if "while (sensors.gyro2.angle() < 149)" in data and "while (sensors.gyro2.angle() > -90)" in data:
        marks += 5
        submarks[2] = 5
    elif "while (sensors.gyro2.angle() < 149)" in data or "while (sensors.gyro2.angle() > -90)" in data:
        marks += 3
        submarks[2] = 3
        comments += "One of the turning condition is incorrect.\n"
    elif "while (sensors.gyro2.angle() <= 149)" in data or "while (sensors.gyro2.angle() >= -90)" in data:
        marks += 3
        submarks[2] = 3
        comments += "use < / > instead of <= / >= when turn right\n"
    elif "while (" in data:
        marks += 1
        submarks[2] = 1
        comments += "Wrong condition(s) in while loop.\n"
    elif "if (sensors.gyro2.angle() < 149)" in data and "if (sensors.gyro2.angle() > -90)" in data:
        marks += 1
        submarks[2] = 1
        comments += "Use while loop instead of if-statement.\n"
    else:
        comments += "Incorrect/Missing turn right code.\n"

    
    tank_pattern = r"motors\.largeBC\.tank\(-(\d+), (\d+)"
    tank_match = re.search(tank_pattern, data)
    angle_pattern = r"while \(sensors\.gyro2\.angle\(\) ([<|>]) -(\d+)\)"
    angle_match = re.search(angle_pattern, data)
    print(angle_match)
    if (tank_match and int(tank_match.group(1)) == int(tank_match.group(2)) and int(tank_match.group(1)) < 30) and (angle_match and angle_match.group(1) == ">" and int(angle_match.group(2)) == 90):
        marks += 5
        submarks[3] = 5
    elif (tank_match and int(tank_match.group(1)) == int(tank_match.group(2)) and int(tank_match.group(1)) < 30) or (angle_match and angle_match.group(1) == ">" and int(angle_match.group(2)) == 90):
        marks += 3
        submarks[3] = 3
        comments += "The first and second values in the tank function are not the same or are not less than 30 or the angle condition is incorrect.\n"
    elif tank_match or angle_match:
        marks += 1
        submarks[3] = 1
        comments += "Some turn left code is missing.\n"
    else:
        comments += "Missing tank function call for turning left.\n"


    tank_pattern = r"motors\.largeBC\.tank\((\d+), -(\d+)"
    tank_match = re.search(tank_pattern, data)
    angle_pattern = r"while \(sensors\.gyro2\.angle\(\) ([<|>]) (\d+)\)"
    angle_match = re.search(angle_pattern, data)
    if (tank_match and int(tank_match.group(1)) == int(tank_match.group(2)) and int(tank_match.group(1)) < 30) and (angle_match and angle_match.group(1) == "<" and int(angle_match.group(2)) == 149):
        marks += 5
        submarks[4] = 5
    elif (tank_match and int(tank_match.group(1)) == int(tank_match.group(2)) and int(tank_match.group(1)) < 30) or (angle_match and angle_match.group(1) == "<" and int(angle_match.group(2)) == 149):
        marks += 3
        submarks[4] = 3
        comments += "The first and second values in the tank function are not the same or are not less than 30 or the angle condition is incorrect.\n"
    elif tank_match or angle_match:
        marks += 1
        submarks[4] = 1
        comments += "Some turn right code is missing.\n"
    else:
        comments += "Missing tank function call for turning right.\n"
        
    return marks, comments, submarks


ev3.mark_ev3("practical_task3", marking_function=marking)
