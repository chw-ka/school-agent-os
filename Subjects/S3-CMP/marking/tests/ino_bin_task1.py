import ino_util as ino_util

def test(submissions):
    for idx, row in submissions.iterrows():
        print("=========================================")
        print(row["class"], row["classnumber"])
        print("=========================================")

        if row["filepath"] is None:
            print("No file path found, skipping")
            continue
        if row['filepath'].endswith('.ino') is False:
            print("File is not an ino file, skipping")
            continue

        # (2 marks) submitted correctly        
        marks = 2
        comments = ""
        content = ino_util.load_file(row["filepath"])
        # trim all leading and trailing whitespaces everyline, then remove all newlines
        content = "\n".join([line.strip() for line in content.split("\n")]).replace("\n", "")

        # (2 marks) Serial.println("Enter an integer angle between 0 and 180:");
        if "Serial.println(\"Enter an integer angle between 0 and 180:\");" in content or "Serial.println('Enter an integer angle between 0 and 180:');" in content:
            marks += 2
        elif "Serial.println(\"Enter" in content or "Serial.println('Enter" in content:
            marks += 1
        else:
            comments += "Serial.println(\"Enter an integer angle between 0 and 180:\"); not found\n"

        # (2 marks)  int angle = Serial.parseInt();
        if "int angle = Serial.parseInt();" in content:
            marks += 2
        elif "Serial.parseInt();" in content:
            marks += 1
        else:
            comments += "int angle = Serial.parseInt(); not found\n"

        # (2 marks) if (angle >= 0 && angle <= 180) {
        if "if (angle >= 0 && angle <= 180) {" in content:
            marks += 2
        else:
            comments += "if (angle >= 0 && angle <= 180) { not found\n"

        # (2 marks) myServo.write(angle);
        if "myServo.write(angle);" in content:
            marks += 2
        elif "myServo.write" in content:
            marks += 1
        else:
            comments += "servo.write(angle); not found\n"

        # (2 marks) Serial.print("Moved to angle: ");
        if "Serial.print(\"Moved to angle: \");" in content or "Serial.print('Moved to angle: ');" in content:
            marks += 2
        elif "Serial.print(\"Moved to angle: " in content or "Serial.print('Moved to angle: '" in content:
            marks += 1
        else:
            comments += "Serial.print(\"Moved to angle: \"); not found\n"

        # (2 marks) Serial.println(angle);
        if "Serial.println(angle);" in content:
            marks += 2
        elif "Serial.println" in content:
            marks += 1
        else:
            comments += "Serial.println(angle); not found\n"

        # (2 marks) Serial.println("Invalid angle. Please enter an integer angle between 0 and 180.");
        if "Serial.println(\"Invalid angle. Please enter an integer angle between 0 and 180.\");" in content or "Serial.println('Invalid angle. Please enter an integer angle between 0 and 180.');" in content:
            marks += 2
        elif "Serial.println(\"Invalid angle." in content or "Serial.println('Invalid angle." in content:
            marks += 1
        else:
            comments += "Serial.println(\"Invalid angle. Please enter an integer angle between 0 and 180.\"); not found\n"

        # (2 marks) while (Serial.available() > 0) {
        if "while (Serial.available() > 0) {" in content:
            marks += 2
        elif "Serial.available" in content:
            marks += 1
        else:
            comments += "while (Serial.available() > 0) { not found\n"

        # (2 marks) delay(5000);myServo.write(90); 
        if "delay(5000);myServo.write(90);" in content:
            marks += 4
        elif "delay(5000)" in content:
            marks += 2
        else:
            comments += "delay(5000);myServo.write(90); not found\n"

        print("=========================================")
        print("marks: ", marks)
        print("comments: ", comments)
        print("=========================================")
        submissions.loc[idx, "marks"] = round(marks / 2, 0)
        submissions.loc[idx, "comments"] = comments
    
    return submissions


# if __name__ == "__main__":
#     submissions = aia_utils.read_teams_aias()
#     submissions = test(submissions)
#     print(submissions)
#     submissions.to_csv("marksheets.csv")
