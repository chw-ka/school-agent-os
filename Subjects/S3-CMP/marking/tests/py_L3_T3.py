import aia_util as aia_utils
import difflib
from contextlib import redirect_stdout
from unittest.mock import patch, MagicMock
import io

# Test cases with different grade inputs and expected outputs
TEST_CASES = [
    {
        "input": ["60", "70", "80"],
        "expected": "Chinese: English: Math: Average = 70.0\nPass"
    },
    {
        "input": ["40", "45", "50"],
        "expected": "Chinese: English: Math: Average = 45.0\nFail"
    },
    {
        "input": ["90", "85", "95"],
        "expected": "Chinese: English: Math: Average = 90.0\nPass"
    },
    {
        "input": ["50", "50", "50"],
        "expected": "Chinese: English: Math: Average = 50.0\nPass"
    },
    {
        "input": ["30", "40", "35"],
        "expected": "Chinese: English: Math: Average = 35.0\nFail"
    },
    {
        "input": ["75", "80", "70"],
        "expected": "Chinese: English: Math: Average = 75.0\nPass"
    },
    {
        "input": ["49", "49", "51"],
        "expected": "Chinese: English: Math: Average = 49.666666666666664\nFail"
    },
    {
        "input": ["100", "100", "100"],
        "expected": "Chinese: English: Math: Average = 100.0\nPass"
    },
    {
        "input": ["55", "60", "65"],
        "expected": "Chinese: English: Math: Average = 60.0\nPass"
    },
    {
        "input": ["20", "30", "25"],
        "expected": "Chinese: English: Math: Average = 25.0\nFail"
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

def extract_average_and_status(output):
    """Extract average value and pass/fail status from output - More flexible"""
    import re
    
    # Find average value - accept various formats like "Average =", "a =", "avg =", "平均 ="
    # Match any word followed by = and a number
    avg_match = re.search(r'[a-zA-Z\u4e00-\u9fff]+\s*=\s*([\d.]+)', output, re.IGNORECASE)
    
    # Find pass/fail status
    has_pass = 'pass' in output.lower() or '及格' in output or '通過' in output
    has_fail = 'fail' in output.lower() or '不及格' in output or '未通過' in output
    
    if avg_match:
        try:
            average = float(avg_match.group(1))
            status = 'Pass' if has_pass else ('Fail' if has_fail else None)
            return (average, status)
        except ValueError:
            pass
    
    return None

def calculate_grade_accuracy(student_output, expected_output):
    """Calculate if average and pass/fail logic is accurate"""
    student_result = extract_average_and_status(student_output)
    expected_result = extract_average_and_status(expected_output)
    
    if student_result and expected_result:
        student_avg, student_status = student_result
        expected_avg, expected_status = expected_result
        
        # Check if average is close (within 0.1 tolerance)
        avg_close = abs(student_avg - expected_avg) < 0.1
        # Check if pass/fail status is correct
        status_correct = student_status == expected_status
        
        return avg_close and status_correct
    
    return False

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
    
    # Check for division operation
    if '/' in code:
        score += 1
        explanation.append("✅ 使用除法運算")
    
    # Check for addition operation
    if '+' in code:
        score += 1
        explanation.append("✅ 使用加法運算")
    
    # Check for int() function
    if 'int(' in code_lower:
        score += 1
        explanation.append("✅ 使用int()轉換")
    
    # Check for if statement
    if 'if' in code_lower:
        score += 1
        explanation.append("✅ 使用if條件判斷")
    
    # Check for else statement
    if 'else' in code_lower:
        score += 1
        explanation.append("✅ 使用else分支")
    
    # Check for multiple inputs (3 subjects)
    if code.count('input(') >= 3:
        score += 1
        explanation.append("✅ 使用三個input函數")
    
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

def evaluate_grade_program(filepath):
    """Evaluate student's grade average program with specific criteria (2 marks each)"""
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
    
    # 2. Check for appropriate output (2 marks) - Balanced approach
    if successful_runs > 0:
        # Check if output format is reasonable
        sample_result = next((r for r in test_results if r["success"]), None)
        if sample_result and sample_result["output"].strip():
            output = sample_result["output"]
            output_lower = output.lower()
            
            # Check if output has a number (the average) and Pass/Fail
            import re
            has_number = re.search(r'[\d.]+', output)
            has_pass_fail = ('pass' in output_lower or 'fail' in output_lower or 
                           '及格' in output or '不及格' in output)
            has_average_word = 'average' in output_lower or 'avg' in output_lower or '平均' in output
            
            # Full marks if they use proper "Average" label
            if has_average_word and has_number and has_pass_fail:
                total_marks += 2
                feedback.append("✅ 輸出格式正確(包含Average和Pass/Fail) (+2)")
            # 1 mark deduction if they use short variable name like "a" instead of "Average"
            elif has_number and has_pass_fail:
                total_marks += 1
                feedback.append("⚠️ 輸出正確但建議使用'Average'而非縮寫 (+1)")
            elif has_number:
                total_marks += 1
                feedback.append("⚠️ 輸出包含平均分但缺少Pass/Fail判斷 (+1)")
            elif has_pass_fail:
                total_marks += 1
                feedback.append("⚠️ 輸出包含Pass/Fail判斷但缺少平均分 (+1)")
            else:
                feedback.append("❌ 輸出格式不正確 (+0)")
        else:
            feedback.append("❌ 沒有輸出 (+0)")
    else:
        # Check static analysis for print statements
        if 'print(' in code_lower:
            total_marks += 1
            feedback.append("⚠️ 程式碼有輸出邏輯但執行失敗 (+1)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    
    # 3. Check for nice input handling (2 marks)
    input_count = student_code.count('input(')
    if input_count >= 3:
        total_marks += 2
        feedback.append("✅ 正確使用三個input函數 (+2)")
    elif input_count >= 2:
        total_marks += 1
        feedback.append("⚠️ 只使用兩個input函數 (+1)")
    elif input_count >= 1:
        total_marks += 0
        feedback.append("⚠️ 只使用一個input函數 (+0)")
    else:
        feedback.append("❌ 未正確使用input函數 (+0)")
    
    # 4. Check for division and if-else statements (2 marks)
    has_division = '/' in student_code
    has_if = 'if' in code_lower
    has_else = 'else' in code_lower
    
    if has_division and has_if and has_else:
        total_marks += 2
        feedback.append("✅ 正確使用除法運算和if-else條件判斷 (+2)")
    elif (has_division and has_if) or (has_if and has_else):
        total_marks += 1
        feedback.append("⚠️ 部分使用條件判斷和運算 (+1)")
    else:
        feedback.append("❌ 未使用必要的條件判斷或運算 (+0)")
    
    # 5. Check for results closely matching model answers (2 marks)
    if successful_runs > 0:
        perfect_matches = 0
        accurate_grade_matches = 0
        
        for i, result in enumerate(test_results):
            if result["success"]:
                student_output = result["output"].strip()
                expected_output = TEST_CASES[i]["expected"].strip()
                
                # First check if average and pass/fail logic is accurate
                if calculate_grade_accuracy(student_output, expected_output):
                    accurate_grade_matches += 1
                    
                    # Then check similarity for exact format match
                    similarity = calculate_similarity(student_output, expected_output)
                    if similarity >= 0.85:
                        perfect_matches += 1
        
        # Much more lenient - focus on logic correctness
        if accurate_grade_matches >= len(TEST_CASES) - 1:  # 9+ correct
            total_marks += 2
            feedback.append(f"✅ 平均分計算和Pass/Fail判斷完全正確 ({accurate_grade_matches}個準確結果) (+2)")
        elif accurate_grade_matches >= len(TEST_CASES) - 3:  # 7+ correct
            total_marks += 2  # Still give full marks!
            feedback.append(f"✅ 平均分計算和Pass/Fail判斷正確 ({accurate_grade_matches}個準確結果) (+2)")
        elif accurate_grade_matches >= len(TEST_CASES) // 2:  # At least half correct
            total_marks += 2  # Still give full marks if most logic is right!
            feedback.append(f"✅ 平均分計算和Pass/Fail判斷基本正確 ({accurate_grade_matches}個準確結果) (+2)")
        elif accurate_grade_matches >= 2:  # At least some correct
            total_marks += 1
            feedback.append(f"⚠️ 平均分計算和Pass/Fail判斷部分正確 ({accurate_grade_matches}個準確結果) (+1)")
        else:
            feedback.append(f"❌ 平均分計算或Pass/Fail判斷不正確 ({accurate_grade_matches}個準確結果) (+0)")
    else:
        feedback.append("❌ 程式無法執行，無法評估結果 (+0)")
    
    # Generate overall feedback - More encouraging
    if total_marks >= 9:
        overall_feedback = f"🌟 優秀！總分 {total_marks}/10"
    elif total_marks >= 7:
        overall_feedback = f"✅ 良好！總分 {total_marks}/10"
    elif total_marks >= 5:
        overall_feedback = f"✅ 合格！總分 {total_marks}/10"
    elif total_marks >= 3:
        overall_feedback = f"⚠️ 需要改進！總分 {total_marks}/10"
    else:
        overall_feedback = f"⚠️ 繼續努力！總分 {total_marks}/10"
    
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

        # (10 marks) The python code calculates average and determines pass/fail correctly
        section_description = "Python程式碼計算平均分並判斷及格"
        filepath = row["filepath"]
        section_mark, remarks = evaluate_grade_program(filepath)

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
