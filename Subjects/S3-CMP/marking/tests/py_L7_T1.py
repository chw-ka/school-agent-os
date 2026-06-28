import aia_util as aia_utils
import difflib
import re
from contextlib import redirect_stdout
from unittest.mock import patch, MagicMock
import io

# Test cases with different numbers for multiplication table
TEST_CASES = [
    {
        "input": ["2"],
        "expected": "2 x 1 = 2\n2 x 2 = 4\n2 x 3 = 6\n2 x 4 = 8\n2 x 5 = 10\n2 x 6 = 12\n2 x 7 = 14\n2 x 8 = 16\n2 x 9 = 18"
    },
    {
        "input": ["5"],
        "expected": "5 x 1 = 5\n5 x 2 = 10\n5 x 3 = 15\n5 x 4 = 20\n5 x 5 = 25\n5 x 6 = 30\n5 x 7 = 35\n5 x 8 = 40\n5 x 9 = 45"
    },
    {
        "input": ["7"],
        "expected": "7 x 1 = 7\n7 x 2 = 14\n7 x 3 = 21\n7 x 4 = 28\n7 x 5 = 35\n7 x 6 = 42\n7 x 7 = 49\n7 x 8 = 56\n7 x 9 = 63"
    },
    {
        "input": ["3"],
        "expected": "3 x 1 = 3\n3 x 2 = 6\n3 x 3 = 9\n3 x 4 = 12\n3 x 5 = 15\n3 x 6 = 18\n3 x 7 = 21\n3 x 8 = 24\n3 x 9 = 27"
    },
    {
        "input": ["9"],
        "expected": "9 x 1 = 9\n9 x 2 = 18\n9 x 3 = 27\n9 x 4 = 36\n9 x 5 = 45\n9 x 6 = 54\n9 x 7 = 63\n9 x 8 = 72\n9 x 9 = 81"
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

def extract_multiplication_lines(output):
    """Extract multiplication table lines from output"""
    lines = output.strip().split('\n')
    multiplication_lines = []
    
    for line in lines:
        line_lower = line.lower()
        # Check if line contains multiplication pattern (e.g., "2 x 1 = 2" or "2*1=2")
        if ('x' in line_lower or '*' in line_lower) and '=' in line_lower:
            multiplication_lines.append(line.strip())
    
    return multiplication_lines

def calculate_multiplication_accuracy(student_output, n):
    """Calculate if multiplication table is correct"""
    lines = extract_multiplication_lines(student_output)
    
    # Should have 9 lines (for range 1 to 9)
    if len(lines) < 9:
        return False
    
    # Check each expected multiplication (1 to 9)
    # We'll check if all 9 expected results appear in the output
    expected_results = [n * i for i in range(1, 10)]
    found_results = []
    
    # Extract all numbers from output
    all_numbers = re.findall(r'\d+', student_output)
    
    # Check if all expected results are present
    for expected in expected_results:
        if str(expected) in all_numbers:
            found_results.append(expected)
    
    # Consider correct if at least 8 out of 9 results are found (allowing minor formatting differences)
    return len(found_results) >= 8

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
    
    # Check for int() function
    if 'int(' in code_lower:
        score += 1
        explanation.append("✅ 使用int()轉換")
    
    # Check for for loop
    if 'for' in code_lower:
        score += 1
        explanation.append("✅ 使用for循環")
    
    # Check for range function
    if 'range(' in code_lower:
        score += 1
        explanation.append("✅ 使用range函數")
    
    # Check for multiplication operator
    if '*' in code:
        score += 1
        explanation.append("✅ 使用乘法運算符")
    
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

def evaluate_multiplication_table_program(filepath):
    """Evaluate student's multiplication table program with specific criteria (2 marks each)"""
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
    if 'int(' in code_lower:
        # Check if int() is used with input
        if 'int(input(' in code_lower:
            total_marks += 2
            feedback.append("✅ 正確使用int()函數轉換輸入 (+2)")
        else:
            total_marks += 1
            feedback.append("⚠️ 部分使用int()函數 (+1)")
    else:
        feedback.append("❌ 未使用int()函數 (+0)")
    
    # 2. Check for appropriate output (2 marks)
    if successful_runs > 0:
        # Check if output has multiplication table format
        sample_result = next((r for r in test_results if r["success"]), None)
        if sample_result and sample_result["output"].strip():
            output = sample_result["output"].lower()
            lines = output.strip().split('\n')
            # Check if output has multiple lines with multiplication pattern
            if len(lines) >= 9 and ('x' in output or '*' in output) and '=' in output:
                total_marks += 2
                feedback.append("✅ 輸出格式正確(包含乘法表格式) (+2)")
            elif ('x' in output or '*' in output) and '=' in output:
                total_marks += 1
                feedback.append("⚠️ 輸出格式部分正確 (+1)")
            else:
                feedback.append("❌ 輸出格式不正確 (+0)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    else:
        # Check static analysis for print statements
        if 'print(' in code_lower and ('x' in code_lower or '*' in student_code):
            total_marks += 1
            feedback.append("⚠️ 程式碼有輸出邏輯但執行失敗 (+1)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    
    # 3. Check for for loop with range (2 marks)
    has_for = 'for' in code_lower
    has_range = 'range(' in code_lower
    
    if has_for and has_range:
        # Check if range is used appropriately (e.g., range(1, 10) or range(1,10))
        if 'range(1' in code_lower and ('10' in code_lower or '9' in code_lower):
            total_marks += 2
            feedback.append("✅ 正確使用for循環和range函數 (+2)")
        else:
            total_marks += 1
            feedback.append("⚠️ 部分使用for循環和range (+1)")
    elif has_for:
        total_marks += 1
        feedback.append("⚠️ 使用for循環但缺少range (+1)")
    else:
        feedback.append("❌ 未使用for循環和range (+0)")
    
    # 4. Check for multiplication pattern and correct format (2 marks)
    has_multiplication = '*' in student_code
    has_format = ('x' in student_code.lower() or '*' in student_code) and '=' in student_code
    
    if has_multiplication and has_format:
        total_marks += 2
        feedback.append("✅ 正確使用乘法運算符和輸出格式 (+2)")
    elif has_multiplication or has_format:
        total_marks += 1
        feedback.append("⚠️ 部分使用乘法運算符或輸出格式 (+1)")
    else:
        feedback.append("❌ 未使用乘法運算符和輸出格式 (+0)")
    
    # 5. Check for results closely matching model answers (2 marks)
    if successful_runs > 0:
        accurate_multiplication_matches = 0
        
        for i, result in enumerate(test_results):
            if result["success"]:
                student_output = result["output"].strip()
                n = int(test_results[i]["input"][0])
                
                # Check if multiplication table is correct
                if calculate_multiplication_accuracy(student_output, n):
                    accurate_multiplication_matches += 1
        
        # Check accuracy based on correct logic
        if accurate_multiplication_matches >= len(TEST_CASES) - 1:
            total_marks += 2
            feedback.append(f"✅ 乘法表計算完全正確 ({accurate_multiplication_matches}個準確結果) (+2)")
        elif accurate_multiplication_matches >= len(TEST_CASES) - 2:
            total_marks += 1
            feedback.append(f"⚠️ 乘法表計算部分正確 ({accurate_multiplication_matches}個準確結果) (+1)")
        else:
            feedback.append(f"❌ 乘法表計算不正確 ({accurate_multiplication_matches}個準確結果) (+0)")
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

        # (10 marks) The python code generates multiplication table correctly
        section_description = "Python程式碼生成乘法表"
        filepath = row["filepath"]
        section_mark, remarks = evaluate_multiplication_table_program(filepath)

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

