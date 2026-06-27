import aia_util as aia_utils
import subprocess
import difflib

def evaluate_task1(filepath):
    # 測試樣本: (num1, num2, symbol, expected result str contains)
    test_cases = [
        ("4", "2", "+", "6"),
        ("4", "2", "-", "2"),
        ("4", "2", "*", "8"),
        ("4", "2", "/", "2.0"),
        ("4", "2", "%", "Invalid symbol."),  # for default case
    ]

    try:
        passed = 0
        for num1, num2, symbol, expected in test_cases:
            full_input = f"{num1}\n{num2}\n{symbol}\n"
            result = subprocess.run(
                ["python", filepath],
                input=full_input,
                capture_output=True,
                text=True,
                timeout=3
            )

            output = result.stdout.strip()
            if expected in output:
                passed += 1

        # 評分邏輯
        if passed == 5:
            return 10, "✅ 功能正確，輸出相似，可給滿分"
        elif passed >= 4:
            return 9, "⚠️ 大致正確，輸出略有遺漏"
        elif passed >= 2:
            return 6 + passed, f"⚠️ 有 {passed}/5 功能通過"
        
        # 輸出幾乎錯誤，但看看有無語法結構
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()
            structure_score = 0
            if "input" in code:
                structure_score += 1
            if "while" in code:
                structure_score += 1
            if "print" in code:
                structure_score += 1
            if "match" in code or "if" in code:
                structure_score += 1
            return structure_score + 1, f"⚠️ 輸出錯，但結構合理，有用 input/while/print/match"

    except Exception:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                student_code = f.read()
        except:
            return 0, "❌ 無法讀取檔案"

        model_code = '''
while True:
    num1 = int(input("Enter the first number:"))
    num2 = int(input("Enter the seond number:"))
    symbol  = input("Enter the symbol ( +, -, *, /):")
    match symbol:
        case "+":
            print(str(num1)+ "  " + symbol + "  =  " + str(num1 + num2))
        case "-":  
            print(str(num1)+ "  " + symbol + "  =  " + str(num1 - num2))            
        case "*":
            print(str(num1)+ "  " + symbol + "  =  " + str(num1 * num2))
        case "/":
            print(str(num1)+ "  " + symbol + "  =  " + str(num1 / num2))
        case _:
            print("Invalid symbol.")
            break
'''
        similarity = difflib.SequenceMatcher(None, student_code, model_code).ratio()
        if similarity > 0.9:
            return 4, "⚠️ 無法執行，但與標準答案非常相似"
        elif similarity > 0.6:
            return 3, "⚠️ 無法執行，但有部分結構"
        else:
            return 1, "❌ 完全錯誤，且不能執行"


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
