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

        # (2 marks) Rtc.Begin();
        if "Rtc.Begin()" in content:
            marks += 2
        elif "Rtc.Begin" in content:
            marks += 1
        else:
            comments += "Rtc.Begin(); not found\n"

        # (2 marks) String t = call_time();
        if "String t = call_time();" in content:
            marks += 2
        elif "call_time();" in content:
            marks += 1
        else:
            comments += "String t = call_time(); not found\n"

        # (2 marks) RtcDateTime now = Rtc.GetDateTime();
        if "RtcDateTime now = Rtc.GetDateTime();" in content:
            marks += 2
        elif "Rtc.GetDateTime" in content:
            marks += 1
        else:
            comments += "RtcDateTime now = Rtc.GetDateTime(); not found\n"

        # (1 mark) String t = with_leading_zero(now.Hour()) + ":" + with_leading_zero(now.Minute());
        if "String t = with_leading_zero(now.Hour()) + \":\" + with_leading_zero(now.Minute());" in content:
            marks += 1
        elif "String t = with_leading_zero" in content:
            marks += 0.5
        else:
            comments += "String t = with_leading_zero(now.Hour()) + \":\" + with_leading_zero(now.Minute()); not found\n"

        # (1 mark) return t;
        if "return t;" in content:
            marks += 1
        elif "return" in content:
            marks += 0.5
        else:
            comments += "return t; not found\n"
        

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
