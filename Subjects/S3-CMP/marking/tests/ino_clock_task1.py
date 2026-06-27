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

        # (1 marks) Serial.begin(9600);
        if "Serial.begin(9600);" in content:
            marks += 1
        elif "Serial.begin" in content:
            marks += 0.5
        else:
            comments += "Serial.begin(9600); not found\n"

        # (1 marks) matrix.begin();
        if "matrix.begin();" in content:
            marks += 1
        elif "matrix.begin" in content:
            marks += 0.5
        else:
            comments += "matrix.begin(); not found\n"


        # (2 marks) matrix_print(
        if "matrix_print(" in content:
            marks += 2
        elif "matrix_print" in content:
            marks += 1
        else:
            comments += "matrix_print(t); not found\n"

        # (2 marks) delay(1000);
        if "delay(1000);" in content:
            marks += 2
        elif "delay" in content:
            marks += 1
        else:
            comments += "delay(1000); not found\n"

        # (2 marks) matrix.setRotation(1);
        if "matrix.setRotation(1);" in content:
            marks += 2
        elif "matrix.setRotation" in content:
            marks += 1
        else:
            comments += "matrix.setRotation(1); not found\n"

        # (2 marks) matrix.setBrightness(5);
        if "matrix.setBrightness(5);" in content:
            marks += 2
        elif "matrix.setBrightness" in content:
            marks += 1
        else:
            comments += "matrix.setBrightness(5); not found\n"

        # (2 marks) matrix.fillScreen(0);
        if "matrix.fillScreen(0);" in content:
            marks += 2
        elif "matrix.fillScreen" in content:
            marks += 1
        else:
            comments += "matrix.fillScreen(0); not found\n"

        # (1 marks) matrix.print(text);
        if "matrix.print(text);" in content:
            marks += 1
        elif "matrix.print" in content:
            marks += 0.5
        else:
            comments += "matrix.print(text); not found\n"

        # (1 marks) matrix.show();
        if "matrix.show();" in content:
            marks += 1
        elif "matrix.show" in content:
            marks += 0.5
        else:
            comments += "matrix.show(); not found\n"

        # (Bonus)  < 10
        if "< 10" in content:
            marks += 1
        if "String(" in content:
            marks += 1



        print("=========================================")
        print("marks: ", marks)
        print("comments: ", comments)
        print("=========================================")
        submissions.loc[idx, "marks"] = round(marks, 0)
        submissions.loc[idx, "comments"] = comments

    return submissions


# if __name__ == "__main__":
#     submissions = aia_utils.read_teams_aias()
#     submissions = test(submissions)
#     print(submissions)
#     submissions.to_csv("marksheets.csv")
