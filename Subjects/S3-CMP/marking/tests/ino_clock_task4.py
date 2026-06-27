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

        # (1 mark) #include "Air_Quality_Sensor.h"
        if '#include "Air_Quality_Sensor.h"' in content:
            marks += 1
        elif 'Air_Quality_Sensor.h' in content:
            marks += 0.5
        else:
            comments += '#include "Air_Quality_Sensor.h" not found\n'
        
        # (1 mark) AirQualitySensor sensor(A0);
        if 'AirQualitySensor sensor(A0);' in content:
            marks += 1
        elif 'AirQualitySensor sensor' in content:
            marks += 0.5
        else:
            comments += 'AirQualitySensor sensor(A0); not found\n'

        # (2 marks) sensor.init()
        if 'sensor.init()' in content:
            marks += 2
        elif 'sensor.init' in content:
            marks += 1
        else:
            comments += 'sensor.init() not found\n'

        # (2 marks) call_air();
        if 'call_air();' in content:
            marks += 2
        elif 'call_air' in content:
            marks += 1
        else:
            comments += 'call_air(); not found\n'

        # (1 mark) sensor.slope();
        if 'sensor.slope();' in content:
            marks += 1
        elif 'sensor.slope' in content:
            marks += 0.5
        else:
            comments += 'sensor.slope(); not found\n'

        # (1 mark) Serial.println(sensor.getValue());
        if 'Serial.println(sensor.getValue());' in content:
            marks += 1
        elif 'Serial.println(sensor.getValue())' in content:
            marks += 0.5
        else:
            comments += 'Serial.println(sensor.getValue()); not found\n'


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
