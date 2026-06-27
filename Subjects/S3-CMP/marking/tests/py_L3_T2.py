import aia_util as aia_utils
import difflib
from contextlib import redirect_stdout
from unittest.mock import patch, MagicMock
import io

# Test cases with different second inputs and expected outputs
TEST_CASES = [
    {
        "input": ["3661"],
        "expected": "How many seconds you need?You need 1 hour(s) 1 minute(s) 1 second(s)"
    },
    {
        "input": ["7200"],
        "expected": "How many seconds you need?You need 2 hour(s) 0 minute(s) 0 second(s)"
    },
    {
        "input": ["3723"],
        "expected": "How many seconds you need?You need 1 hour(s) 2 minute(s) 3 second(s)"
    },
    {
        "input": ["5000"],
        "expected": "How many seconds you need?You need 1 hour(s) 23 minute(s) 20 second(s)"
    },
    {
        "input": ["86400"],
        "expected": "How many seconds you need?You need 24 hour(s) 0 minute(s) 0 second(s)"
    },
    {
        "input": ["125"],
        "expected": "How many seconds you need?You need 0 hour(s) 2 minute(s) 5 second(s)"
    },
    {
        "input": ["3600"],
        "expected": "How many seconds you need?You need 1 hour(s) 0 minute(s) 0 second(s)"
    },
    {
        "input": ["60"],
        "expected": "How many seconds you need?You need 0 hour(s) 1 minute(s) 0 second(s)"
    },
    {
        "input": ["45"],
        "expected": "How many seconds you need?You need 0 hour(s) 0 minute(s) 45 second(s)"
    },
    {
        "input": ["10825"],
        "expected": "How many seconds you need?You need 3 hour(s) 0 minute(s) 25 second(s)"
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

def extract_time_values(output):
    """Extract hour, minute, second values from output"""
    import re
    
    # Try to find patterns like "1 hour(s) 2 minute(s) 3 second(s)"
    hour_match = re.search(r'(\d+)\s*hour', output, re.IGNORECASE)
    min_match = re.search(r'(\d+)\s*minute', output, re.IGNORECASE)
    sec_match = re.search(r'(\d+)\s*second', output, re.IGNORECASE)
    
    if hour_match and min_match and sec_match:
        try:
            hours = int(hour_match.group(1))
            minutes = int(min_match.group(1))
            seconds = int(sec_match.group(1))
            return (hours, minutes, seconds)
        except ValueError:
            pass
    
    return None

def calculate_time_accuracy(student_output, expected_output):
    """Calculate if time conversion is accurate"""
    student_time = extract_time_values(student_output)
    expected_time = extract_time_values(expected_output)
    
    if student_time and expected_time:
        return student_time == expected_time
    
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
    if '//' in code or '/' in code:
        score += 1
        explanation.append("✅ 使用除法運算")
    
    # Check for modulo operation
    if '%' in code:
        score += 1
        explanation.append("✅ 使用餘數運算(%)")
    
    # Check for int() function
    if 'int(' in code_lower:
        score += 1
        explanation.append("✅ 使用int()轉換")
    
    # Check for 3600 (seconds in hour)
    if '3600' in code:
        score += 1
        explanation.append("✅ 使用3600常數(小時換算)")
    
    # Check for 60 (seconds in minute)
    if '60' in code:
        score += 1
        explanation.append("✅ 使用60常數(分鐘換算)")
    
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

def evaluate_time_conversion(filepath):
    """Evaluate student's time conversion program with specific criteria (2 marks each)"""
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
            output = sample_result["output"].lower()
            if ('hour' in output or 'hr' in output) and ('minute' in output or 'min' in output) and ('second' in output or 'sec' in output):
                total_marks += 2
                feedback.append("✅ 輸出格式正確(包含小時、分鐘、秒) (+2)")
            elif ('hour' in output or 'minute' in output or 'second' in output):
                total_marks += 1
                feedback.append("⚠️ 輸出格式部分正確 (+1)")
            else:
                feedback.append("❌ 輸出格式不正確 (+0)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    else:
        # Check static analysis for print statements
        if 'print(' in code_lower and ('hour' in code_lower or 'minute' in code_lower or 'second' in code_lower):
            total_marks += 1
            feedback.append("⚠️ 程式碼有輸出邏輯但執行失敗 (+1)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    
    # 3. Check for nice input handling (2 marks)
    input_count = student_code.count('input(')
    if input_count >= 1:
        total_marks += 2
        feedback.append("✅ 正確使用input函數 (+2)")
    else:
        feedback.append("❌ 未正確使用input函數 (+0)")
    
    # 4. Check for modulo and division operators (2 marks)
    has_modulo = '%' in student_code
    has_division = '//' in student_code or '/' in student_code
    has_3600 = '3600' in student_code
    has_60 = '60' in student_code
    
    if has_modulo and has_division and has_3600 and has_60:
        total_marks += 2
        feedback.append("✅ 正確使用除法、餘數運算和時間常數 (+2)")
    elif (has_modulo or has_division) and (has_3600 or has_60):
        total_marks += 1
        feedback.append("⚠️ 部分使用時間轉換運算 (+1)")
    else:
        feedback.append("❌ 未使用必要的時間轉換運算 (+0)")
    
    # 5. Check for results closely matching model answers (2 marks)
    if successful_runs > 0:
        perfect_matches = 0
        accurate_time_matches = 0
        
        for i, result in enumerate(test_results):
            if result["success"]:
                student_output = result["output"].strip()
                expected_output = TEST_CASES[i]["expected"].strip()
                
                # First check if time conversion is accurate
                if calculate_time_accuracy(student_output, expected_output):
                    accurate_time_matches += 1
                    
                    # Then check similarity for exact format match
                    similarity = calculate_similarity(student_output, expected_output)
                    if similarity >= 0.85:
                        perfect_matches += 1
        
        # Prioritize time conversion accuracy over exact format match
        if accurate_time_matches >= len(TEST_CASES) - 1:
            total_marks += 2
            feedback.append(f"✅ 時間轉換完全正確 ({accurate_time_matches}個準確結果) (+2)")
        elif accurate_time_matches >= len(TEST_CASES) - 2:
            total_marks += 1
            feedback.append(f"⚠️ 時間轉換部分正確 ({accurate_time_matches}個準確結果) (+1)")
        else:
            feedback.append(f"❌ 時間轉換不正確 ({accurate_time_matches}個準確結果) (+0)")
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

        # (10 marks) The python code converts seconds to time correctly
        section_description = "Python程式碼轉換秒數為時間"
        filepath = row["filepath"]
        section_mark, remarks = evaluate_time_conversion(filepath)

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
