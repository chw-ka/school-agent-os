import ev3_utils as ev3
import re


def marking(data):
    marks = 0
    submarks = [0, 0, 0]
    comments = ""
    
    
    if 'forever(function () {\n    brick.showMood(moods.neutral)' in data:
        marks += 5
        submarks[0] = 5
    elif 'forever(function () {\n    brick.showMood(' in data:
        marks += 3
        submarks[0] = 3
        comments += "The mood is not set to neutral.\n"
    else:
        comments += "No forever block is used.\n"

    if 'brick.buttonUp.onEvent(ButtonEvent.Pressed, function () {' in data and 'brick.buttonDown.onEvent(ButtonEvent.Pressed, function () {' in data:
        marks += 5
        submarks[1] = 5
    elif 'brick.buttonUp.onEvent(ButtonEvent.Pressed, function () {' in data or 'brick.buttonDown.onEvent(ButtonEvent.Pressed, function () {' in data:
        marks += 3
        submarks[1] = 3
        comments += "Only one button event is used.\n"
    elif '.onEvent(ButtonEvent.Pressed, function () {' in data:
        marks += 1
        submarks[1] = 1
        comments += "Use the correct button event for each button.\n"
    else:
        comments += "No button event is used.\n"

    # check brick.showMood(moods.sad) and tired and neutral is used
    if 'brick.showMood(moods.sad)' in data and 'brick.showMood(moods.tired)' in data and 'brick.showMood(moods.neutral)' in data:
        marks += 5
        submarks[2] = 5
    # only two moods are used
    elif 'brick.showMood(moods.sad)' in data and 'brick.showMood(moods.tired)' in data:
        marks += 3
        submarks[2] = 3
        comments += "Missing brick.showMood(moods.neutral) code.\n"
    elif 'brick.showMood(moods.sad)' in data and 'brick.showMood(moods.neutral)' in data:
        marks += 3
        submarks[2] = 3
        comments += "Missing brick.showMood(moods.tired) code.\n"
    elif 'brick.showMood(moods.tired)' in data and 'brick.showMood(moods.neutral)' in data:
        marks += 3
        submarks[2] = 3
        comments += "Missing brick.showMood(moods.sad) code.\n"
    # only one mood is used
    elif 'brick.showMood(moods.sad)' in data or 'brick.showMood(moods.tired)' in data or 'brick.showMood(moods.neutral)' in data:
        marks += 1
        submarks[2] = 1
        comments += "Use all three moods.\n"
    else:
        comments += "Missing mood code.\n"
        
    return marks, comments, submarks


ev3.mark_ev3("practical_task1", marking_function=marking)
