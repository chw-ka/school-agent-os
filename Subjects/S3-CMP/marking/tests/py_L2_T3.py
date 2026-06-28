import aia_util as aia_utils
import difflib
from contextlib import redirect_stdout
from unittest.mock import patch, MagicMock
import io

# Test cases with different number inputs and expected outputs
TEST_CASES = [
    {
        "input": ["5", "3"],
        "expected": "Please input a number: Please input another number: 5 + 3 = 8"
    },
    {
        "input": ["10", "7"],
        "expected": "Please input a number: Please input another number: 10 + 7 = 17"
    },
    {
        "input": ["25", "15"],
        "expected": "Please input a number: Please input another number: 25 + 15 = 40"
    },
    {
        "input": ["100", "200"],
        "expected": "Please input a number: Please input another number: 100 + 200 = 300"
    },
    {
        "input": ["0", "0"],
        "expected": "Please input a number: Please input another number: 0 + 0 = 0"
    },
    {
        "input": ["1", "1"],
        "expected": "Please input a number: Please input another number: 1 + 1 = 2"
    },
    {
        "input": ["50", "25"],
        "expected": "Please input a number: Please input another number: 50 + 25 = 75"
    },
    {
        "input": ["12", "8"],
        "expected": "Please input a number: Please input another number: 12 + 8 = 20"
    },
    {
        "input": ["99", "1"],
        "expected": "Please input a number: Please input another number: 99 + 1 = 100"
    },
    {
        "input": ["7", "13"],
        "expected": "Please input a number: Please input another number: 7 + 13 = 20"
    }
]

def run_student_code(student_code, test_input, return_dict):
    """Run student code with mocked input"""
    buffer = io.StringIO()
    
    try:
        with redirect_stdout(buffer):
            with patch('builtins.input', side_effect=test_input):
                exec(student_code, {})
        output = buffer.getvalue()
        return_dict["runs"] = True
        return_dict["output"] = output
    except Exception as e:
        return_dict["runs"] = False
        return_dict["error"] = str(e)

def calculate_similarity(output1, output2):
    """Calculate similarity between two outputs"""
    return difflib.SequenceMatcher(None, output1.strip(), output2.strip()).ratio()

def analyze_code_quality(code):
    """Analyze code quality for non-running programs"""
    score = 0
    explanation = []
    
    code_lower = code.lower()
    
    # Check for input function
    if "input(" in code_lower:
        score += 1
        explanation.append("✅ 使用input函數")
    
    # Check for print function
    if "print(" in code_lower:
        score += 1
        explanation.append("✅ 使用print函數")
    
    # Check for variable assignment
    if '=' in code and 'input' in code_lower:
        score += 1
        explanation.append("✅ 使用變數儲存輸入")
    
    # Check for addition operation
    if '+' in code:
        score += 1
        explanation.append("✅ 使用加法運算")
    
    # Check for int() function
    if 'int(' in code_lower:
        score += 1
        explanation.append("✅ 使用int()轉換")
    
    # Check for multiple inputs
    if code.count('input(') >= 2:
        score += 1
        explanation.append("✅ 使用兩個input函數")
    
    return score, explanation

def run_multiple_tests(student_code):
    """Run student code with multiple test cases using fast direct exec()"""
    test_results = []
    
    for test_case in TEST_CASES:
        buffer = io.StringIO()
        
        try:
            with redirect_stdout(buffer):
                with patch('builtins.input', side_effect=test_case["input"]):
                    exec(student_code, {})
            test_results.append({
                "input": test_case["input"],
                "success": True,
                "output": buffer.getvalue(),
                "error": ""
            })
        except Exception as e:
            test_results.append({
                "input": test_case["input"],
                "success": False,
                "output": buffer.getvalue(),
                "error": str(e)
            })
    
    return test_results

def evaluate_addition_program(filepath):
    """Evaluate student's addition program with specific criteria (2 marks each)"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            student_code = f.read()
    except:
        return 0, "❌ 無法讀取程式碼"

    total_marks = 0
    feedback = []
    
    # Run multiple test cases
    test_results = run_multiple_tests(student_code)
    
    # Count successful runs
    successful_runs = sum(1 for result in test_results if result["success"])
    
    # 1. Check for int() usage appropriately (2 marks)
    code_lower = student_code.lower()
    if 'int(' in code_lower and 'input' in code_lower:
        # Check if int() is used with input
        if 'int(input(' in code_lower:
            total_marks += 2
            feedback.append("✅ 正確使用int()函數 (+2)")
        else:
            total_marks += 1
            feedback.append("⚠️ 部分使用int()函數 (+1)")
    else:
        feedback.append("❌ 未使用int()函數 (+0)")
    
    # 2. Check for appropriate output (2 marks)
    if successful_runs > 0:
        # Check if output format is reasonable
        sample_result = next((r for r in test_results if r["success"]), None)
        if sample_result and sample_result["output"].strip():
            output = sample_result["output"].strip()
            if '+' in output and '=' in output:
                total_marks += 2
                feedback.append("✅ 輸出格式正確 (+2)")
            else:
                total_marks += 1
                feedback.append("⚠️ 輸出格式部分正確 (+1)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    else:
        # Check static analysis for print statements
        if 'print(' in code_lower and ('+' in student_code or '=' in student_code):
            total_marks += 1
            feedback.append("⚠️ 程式碼有輸出邏輯但執行失敗 (+1)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    
    # 3. Check for nice input handling (2 marks)
    input_count = student_code.count('input(')
    if input_count >= 2:
        total_marks += 2
        feedback.append("✅ 正確使用兩個input函數 (+2)")
    elif input_count == 1:
        total_marks += 1
        feedback.append("⚠️ 只使用一個input函數 (+1)")
    else:
        feedback.append("❌ 未正確使用input函數 (+0)")
    
    # 4. Check for + operator usage (2 marks)
    if '+' in student_code:
        total_marks += 2
        feedback.append("✅ 正確使用加法運算符 (+2)")
    else:
        feedback.append("❌ 未使用加法運算符 (+0)")
    
    # 5. Check for results closely matching model answers (2 marks)
    if successful_runs > 0:
        accurate_calculation_matches = 0
        
        for i, result in enumerate(test_results):
            if result["success"]:
                student_output = result["output"].strip()
                test_input = TEST_CASES[i]["input"]
                
                # Extract calculation result from student output
                import re
                # Look for pattern: number + number = result
                match = re.search(r'(\d+)\s*\+\s*(\d+)\s*=\s*(\d+)', student_output)
                
                if match:
                    num1_output = int(match.group(1))
                    num2_output = int(match.group(2))
                    result_output = int(match.group(3))
                    
                    # Check if the calculation is correct
                    num1_input = int(test_input[0])
                    num2_input = int(test_input[1])
                    expected_result = num1_input + num2_input
                    
                    if num1_output == num1_input and num2_output == num2_input and result_output == expected_result:
                        accurate_calculation_matches += 1
        
        if accurate_calculation_matches >= len(TEST_CASES) - 1:
            total_marks += 2
            feedback.append(f"✅ 加法計算完全正確 ({accurate_calculation_matches}個準確結果) (+2)")
        elif accurate_calculation_matches >= len(TEST_CASES) - 2:
            total_marks += 1
            feedback.append(f"⚠️ 加法計算部分正確 ({accurate_calculation_matches}個準確結果) (+1)")
        else:
            feedback.append(f"❌ 加法計算不正確 ({accurate_calculation_matches}個準確結果) (+0)")
    else:
        feedback.append("❌ 程式無法執行，無法評估結果 (+0)")
    
    # Generate overall feedback
    if total_marks >= 9:
        overall_feedback = f"✅ 優秀！總分 {total_marks}/10"
    elif total_marks >= 7:
        overall_feedback = f"✅ 良好！總分 {total_marks}/10"
    elif total_marks >= 5:
        overall_feedback = f"⚠️ 基本合格！總分 {total_marks}/10"
    elif total_marks >= 2:
        overall_feedback = f"❌ 需要改進！總分 {total_marks}/10"
    else:
        overall_feedback = f"❌ 不及格！總分 {total_marks}/10"
    
    detailed_feedback = " | ".join(feedback)
    
    return total_marks, f"{overall_feedback} | {detailed_feedback}"

def test(submissions):
    for idx, row in submissions.iterrows():
        print("=========================================")
        print(submissions.loc[idx, "class"], submissions.loc[idx, "classnumber"])
        print("=========================================")
        submissions.loc[idx, "marks"] = 0
        submissions.loc[idx, "comments"] = ""

        # (0 marks) No marks if no file found
        if row["filepath"] is None:
            submissions.loc[idx, "marks"] = 0
            submissions.loc[idx, "comments"] = "No file found in the submission\n"
            continue

        # (10 marks) The python code performs addition correctly
        section_description = "Python程式碼執行加法運算"
        filepath = row["filepath"]
        section_mark, remarks = evaluate_addition_program(filepath)

        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark, 10)

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
