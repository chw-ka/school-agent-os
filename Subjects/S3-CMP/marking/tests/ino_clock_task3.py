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

        marks = 2
        comments = ""
        content = ino_util.load_file(row["filepath"])
        # trim all leading and trailing whitespaces everyline, then remove all newlines
        content = "\n".join([line.strip() for line in content.split("\n")]).replace("\n", "")

        # (1 mark) byte temperature = 0;
        if "byte temperature = 0;" in content:
            marks += 1
        elif "byte temperature" in content:
            marks += 0.5
        else:
            comments += "byte temperature = 0; not found\n"

        # (1 mark) dht11.read(2, &temperature, NULL, NULL);
        if "dht11.read(2, &temperature, NULL, NULL);" in content:
            marks += 1
        elif "dht11.read" in content and "&temperature" in content:
            marks += 0.5
        else:
            comments += "dht11.read(2, &temperature, NULL, NULL); not found\n"

        # (1 mark) return String(temperature);   
        if "return String(temperature);" in content:
            marks += 1
        elif "return" in content:
            marks += 0.5
        else:
            comments += "return String(temperature); not found\n"

        # (1 mark)  byte humidity = 0;
        if "byte humidity = 0;" in content:
            marks += 1
        elif "byte humidity" in content:
            marks += 0.5
        else:
            comments += "byte humidity = 0; not found\n"

        # (1 mark)  dht11.read(2, NULL, &humidity, NULL);
        if "dht11.read(2, NULL, &humidity, NULL);" in content:
            marks += 1
        elif "dht11.read" in content and "&humidity" in content:
            marks += 0.5
        else:
            comments += "dht11.read(2, NULL, &humidity, NULL); not found\n"

        # (1 mark)  return String(humidity);
        if "return String(humidity);" in content:
            marks += 1
        elif "return" in content:
            marks += 0.5
        else:
            comments += "return String(humidity); not found\n"

        # (2 marks) String t = call_time(); or String t = call_humi(); or String t = call_temp();
        if "String t = call_time();" in content or "String t = call_humi();" in content or "String t = call_temp();" in content:
            marks += 2
        elif "String t = call" in content:
            marks += 1
        else:
            comments += "String t = call_time(); or String t = call_humi(); or String t = call_temp(); not found\n"


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
