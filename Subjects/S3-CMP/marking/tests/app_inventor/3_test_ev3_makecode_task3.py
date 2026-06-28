import ev3_utils as ev3
import re


def marking(data):
    marks = 2
    submarks = [2, 0, 0, 0, 0]
    comments = ""
    # (2 marks) Play any sound when you start the program.
    if "music.playTone(262, music.beat(BeatFraction." in data:
        marks += 2
        submarks[1] = 2
    else:
        comments += "Missing code to play any sound at the start of the program.\n"

    # (2 marks) Play first bar of `Twinkle, Twinkle, Little Star` with tempo 72 bpm when you start the program.
    if "music.setTempo(72)" in data:
        marks += 1
        submarks[2] = 1
    else:
        comments += "Missing code to set tempo to 72 bpm.\n"

    matches = re.findall(r"music.playTone\((\d+), music.beat\(BeatFraction\.([a-zA-Z]+)", data)
    if len(matches) >= 7:
        marks += 1
        submarks[2] += 1
    else:
        comments += "Missing code to play first bar of `Twinkle, Twinkle, Little Star`.\n"

    # (2 marks) Play second bar of `Twinkle, Twinkle, Little Star` with tempo 72 bpm when you start the program. 
    if len(matches) >= 14:
        marks += 2
        submarks[3] = 2
    else:
        comments += "Missing code to play second bar of `Twinkle, Twinkle, Little Star`.\n"

    # (2 marks) (Bonus) Complete the whole song `Twinkle, Twinkle, Little Star` with tempo 72 bpm when you start the program.
    if len(matches) >= 40:
        marks += 2
        submarks[4] = 2
    else:
        comments += "Missing code to play the whole song `Twinkle, Twinkle, Little Star`.\n"

    return marks, comments, submarks


ev3.mark_ev3("makecode_task3", marking_function=marking)
