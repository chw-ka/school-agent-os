import aia_util as aia_utils
import subprocess
import difflib

def evaluate_task1(filepath):
    model_outputs = {
        "Eric": "Enter your name: Hello Eric, Nice to meet you bro!",
        "Alice": "Enter your name: Hello Alice, Nice to meet you bro!",
        "Bob": "Enter your name: Hello Bob, Nice to meet you bro!"
    }

    try:
        outputs = []
        for test_input, expected_output in model_outputs.items():
            result = subprocess.run(
                ["python", filepath],
                input=test_input + "\n",
                capture_output=True,
                text=True,
                timeout=3
            )

            output_lines = result.stdout.strip().splitlines()
            full_output = " ".join(line.strip() for line in output_lines)
            outputs.append(full_output)

        # ✅ 完全正確
        if all(o == model_outputs[name] for o, name in zip(outputs, model_outputs)):
            return 5, "✅ 完全正確"

        # ⚠️ 格式 / 細微錯誤（大小寫／空格／少幾個字母）：改用 difflib 比對相似度
        similarity_scores = []
        for o, name in zip(outputs, model_outputs):
            expected = model_outputs[name]
            ratio = difflib.SequenceMatcher(None, o, expected).ratio()
            similarity_scores.append(ratio)

        if all(score >= 0.95 for score in similarity_scores):
            return 4, "⚠️ 輸出非常接近（格式錯誤／少字母）"

        # ⚠️ 執行成功但輸出錯誤，分析使用結構
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()
            used_input = "input" in code
            used_print = "print" in code

            if used_input and used_print:
                return 3, "⚠️ 執行成功但輸出錯誤；有使用 input() 和 print()"
            elif used_input or used_print:
                if used_input:
                    return 2, "⚠️ 執行成功但輸出錯誤；有用 input() 但沒有 print()"
                else:
                    return 2, "⚠️ 執行成功但輸出錯誤；有用 print() 但沒有 input()"

            return 1, "⚠️ 執行成功但輸出錯誤；缺 input() 和 print()"

    except Exception:
        # ❌ 程式不能執行 → 比對原始碼相似度
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                student_code = f.read()
        except:
            return 0, "❌ 無法讀取檔案"

        model_code = 'name = input("Enter your name: ")\nprint("Hello " + name + ", Nice to meet you bro!")'
        similarity = difflib.SequenceMatcher(None, student_code, model_code).ratio()

        if similarity > 0.9:
            return 3, "⚠️ 無法執行，但與標準答案非常相似"
        elif similarity > 0.6:
            return 2, "⚠️ 無法執行，但有部分正確邏輯"
        else:
            return 1, "❌ 無法執行，且與標準答案差異大"


def test(submissions):
    for idx, row in submissions.iterrows():
        print("=========================================")
        print(submissions.loc[idx, "class"], submissions.loc[idx, "classnumber"])
        print("=========================================")
        submissions.loc[idx, "marks"] = 0
        submissions.loc[idx, "comments"] = ""

        # (2 marks) No marks if no file found
        if row["filepath"] is None:
            submissions.loc[idx, "marks"] = 0
            submissions.loc[idx, "comments"] = "No file found in the submission\n"
            continue

        # (1 mark) The python code is runnable
        section_description = "The python code is runnable"
        filepath = row["filepath"]
        section_mark, remarks = evaluate_task1(filepath)

        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark, 5)

        if (remarks != ""):
            submissions.loc[idx, "comments"] += "\n" + remarks

        print("=========================================")
        print("Marks:", submissions.loc[idx, "marks"])
        print(submissions.loc[idx, "comments"])
        print("=========================================")

    return submissions


if __name__ == "__main__":
    submissions = aia_utils.read_teams_aias()
    submissions = test(submissions)
    print(submissions)
    submissions.to_csv("marksheets.csv")
