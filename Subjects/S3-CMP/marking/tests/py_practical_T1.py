import aia_util as aia_utils
import difflib
import re
from contextlib import redirect_stdout
from unittest.mock import patch, MagicMock
import io

# Test cases for travel expense grading program
TEST_CASES = [
    {
        "input": ["Alice", "2000", "1500", "1000"],  # Name, Transport, Hotel, Food
        "expected_total": 4500,
        "expected_avg": 1500.0,
        "expected_grade": "A",
        "expected_remark": "Luxury trip"
    },
    {
        "input": ["Bob", "1800", "1600", "1100"],
        "expected_total": 4500,
        "expected_avg": 1500.0,
        "expected_grade": "A",
        "expected_remark": "Luxury trip"
    },
    {
        "input": ["Charlie", "5000", "3000", "2000"],
        "expected_total": 10000,
        "expected_avg": 3333.33,
        "expected_grade": "A",
        "expected_remark": "Luxury trip"
    },
    {
        "input": ["David", "1000", "800", "600"],
        "expected_total": 2400,
        "expected_avg": 800.0,
        "expected_grade": "B",
        "expected_remark": "Standard trip"
    },
    {
        "input": ["Eve", "900", "850", "750"],
        "expected_total": 2500,
        "expected_avg": 833.33,
        "expected_grade": "B",
        "expected_remark": "Standard trip"
    },
    {
        "input": ["Frank", "1200", "1000", "400"],
        "expected_total": 2600,
        "expected_avg": 866.67,
        "expected_grade": "B",
        "expected_remark": "Standard trip"
    },
    {
        "input": ["Grace", "500", "400", "300"],
        "expected_total": 1200,
        "expected_avg": 400.0,
        "expected_grade": "C",
        "expected_remark": "Budget trip"
    },
    {
        "input": ["Henry", "600", "500", "400"],
        "expected_total": 1500,
        "expected_avg": 500.0,
        "expected_grade": "C",
        "expected_remark": "Budget trip"
    },
    {
        "input": ["Iris", "799", "799", "799"],
        "expected_total": 2397,
        "expected_avg": 799.0,
        "expected_grade": "C",
        "expected_remark": "Budget trip"
    },
    {
        "input": ["Jack", "1500", "1500", "1500"],
        "expected_total": 4500,
        "expected_avg": 1500.0,
        "expected_grade": "A",
        "expected_remark": "Luxury trip"
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

def extract_total(output):
    """Extract total expense from output"""
    output_lower = output.lower()
    
    # Look for "Total = 4500" or "Total: 4500"
    patterns = [
        r'total\s*[=:]\s*(\d+)',
        r'total\s+(\d+)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, output_lower, re.IGNORECASE)
        if matches:
            try:
                return int(matches[0])
            except:
                pass
    
    return None

def extract_average(output):
    """Extract average expense from output"""
    output_lower = output.lower()
    
    # Look for "Average = 1500.0" or "Average: 1500.0" or "avg: 1500.0"
    patterns = [
        r'average\s*[=:]\s*([\d.]+)',
        r'avg\s*[=:]\s*([\d.]+)',
        r'average\s+([\d.]+)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, output_lower, re.IGNORECASE)
        if matches:
            try:
                return float(matches[0])
            except:
                pass
    
    # Try to find decimal numbers near "average"
    if 'average' in output_lower or 'avg' in output_lower:
        numbers = re.findall(r'[\d]+\.[\d]+', output)
        if numbers:
            try:
                return float(numbers[0])
            except:
                pass
    
    return None

def extract_grade(output):
    """Extract grade from output"""
    output_lower = output.lower()
    
    # Look for "Grade: A" or "Grade = A"
    patterns = [
        r'grade\s*[=:]\s*([ABC])',
        r'grade\s+([ABC])',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, output_lower, re.IGNORECASE)
        if matches:
            return matches[0].upper()
    
    return None

def extract_remark(output):
    """Extract remark from output"""
    output_lower = output.lower()
    
    # Look for "Remark: Luxury trip" or "Remark: Standard trip" or "Remark: Budget trip"
    if 'remark' in output_lower:
        if 'luxury' in output_lower:
            return 'Luxury trip'
        elif 'standard' in output_lower:
            return 'Standard trip'
        elif 'budget' in output_lower:
            return 'Budget trip'
    
    return None

def calculate_grade_logic(average):
    """Calculate expected grade and remark based on average"""
    if average >= 1500:
        return "A", "Luxury trip"
    elif average >= 800:
        return "B", "Standard trip"
    else:
        return "C", "Budget trip"

def analyze_code_quality(code):
    """Analyze code quality for non-running programs"""
    score = 0
    explanation = []
    
    code_lower = code.lower()
    
    # Check for input function
    input_count = code.count('input(')
    if input_count >= 4:
        score += 1
        explanation.append("✅ 使用多個input函數(姓名和三個費用)")
    elif input_count >= 1:
        score += 1
        explanation.append("✅ 使用input函數")
    
    # Check for int() function
    int_count = code.count('int(')
    if int_count >= 3:
        score += 1
        explanation.append("✅ 使用int()轉換三個費用")
    elif int_count >= 1:
        score += 1
        explanation.append("✅ 使用int()轉換")
    
    # Check for addition (total calculation)
    if '+' in code and ('total' in code_lower or '=' in code):
        score += 1
        explanation.append("✅ 計算總費用")
    
    # Check for division (average calculation)
    if '/' in code and ('average' in code_lower or 'avg' in code_lower):
        score += 1
        explanation.append("✅ 計算平均費用")
    
    # Check for round() function
    if 'round(' in code_lower:
        score += 1
        explanation.append("✅ 使用round()函數")
    
    # Check for if-elif-else
    if 'if' in code_lower and 'elif' in code_lower and 'else' in code_lower:
        score += 1
        explanation.append("✅ 使用if-elif-else條件判斷")
    
    # Check for comparison operators
    if '>=' in code or '<=' in code:
        score += 1
        explanation.append("✅ 使用比較運算符")
    
    # Check for print statements
    print_count = code.count('print(')
    if print_count >= 4:
        score += 1
        explanation.append("✅ 使用多個print函數輸出結果")
    
    return score, explanation

def run_multiple_tests(student_code):
    """Run student code with multiple test cases"""
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
                "error": "",
                "expected": test_case
            })
        except Exception as e:
            test_results.append({
                "input": test_case["input"],
                "success": False,
                "output": buffer.getvalue(),
                "error": str(e),
                "expected": test_case
            })
    
    return test_results

def evaluate_travel_expense_program(filepath):
    """Evaluate student's travel expense program according to rubrics (total 15 marks)"""
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
    
    # Rubric 1: 正確地上傳檔案 (1分) - This is handled by file existence check, give 1 mark if file exists
    total_marks += 1
    feedback.append("✅ 正確地上傳檔案 (+1)")
    
    # Rubric 2: 正確地讀取用戶輸入 (3分) - variable naming, input(), int()
    code_lower = student_code.lower()
    input_count = student_code.count('input(')
    int_count = student_code.count('int(')
    
    # Check for proper variable naming (name, transport, hotel, food or similar)
    has_name_var = 'name' in code_lower
    has_transport_var = 'transport' in code_lower
    has_hotel_var = 'hotel' in code_lower
    has_food_var = 'food' in code_lower
    
    proper_vars = sum([has_name_var, has_transport_var, has_hotel_var, has_food_var])
    
    if input_count >= 4 and int_count >= 3 and proper_vars >= 3:
        total_marks += 3
        feedback.append("✅ 正確地讀取用戶輸入(變量命名、input()、int()) (+3)")
    elif input_count >= 4 and int_count >= 3:
        total_marks += 2
        feedback.append("⚠️ 使用input()和int()但變量命名可能不正確 (+2)")
    elif input_count >= 1 and int_count >= 1:
        total_marks += 1
        feedback.append("⚠️ 部分使用input()和int() (+1)")
    else:
        feedback.append("❌ 未正確讀取用戶輸入 (+0)")
    
    # Rubric 3: 正確運算 (2分) - total and average calculations
    has_total = '+' in student_code and ('total' in code_lower or 't' in code_lower)
    has_average = '/' in student_code and ('average' in code_lower or 'avg' in code_lower)
    
    if has_total and has_average:
        # Check if total = transport + hotel + food and avg = total / 3
        if 'total' in code_lower and ('transport' in code_lower or 'hotel' in code_lower or 'food' in code_lower):
            if 'avg' in code_lower and ('total' in code_lower or '3' in code_lower):
                total_marks += 2
                feedback.append("✅ 正確運算total和average (+2)")
            else:
                total_marks += 1
                feedback.append("⚠️ 部分運算正確 (+1)")
        else:
            total_marks += 1
            feedback.append("⚠️ 部分運算正確 (+1)")
    elif has_total or has_average:
        total_marks += 1
        feedback.append("⚠️ 部分運算正確 (+1)")
    else:
        feedback.append("❌ 未正確運算 (+0)")
    
    # Rubric 4: 正確使用若/否則運算 (3分) - if avg >= 1500, elif avg >= 800, else
    has_if = 'if' in code_lower
    has_elif = 'elif' in code_lower
    has_else = 'else' in code_lower
    has_1500_check = '1500' in student_code and '>=' in student_code
    has_800_check = '800' in student_code and '>=' in student_code
    has_avg_in_condition = 'avg' in code_lower or 'average' in code_lower
    
    if has_if and has_elif and has_else and has_1500_check and has_800_check and has_avg_in_condition:
        total_marks += 3
        feedback.append("✅ 正確使用if-elif-else條件判斷(avg >= 1500, avg >= 800, else) (+3)")
    elif has_if and has_elif and has_else and (has_1500_check or has_800_check):
        total_marks += 2
        feedback.append("⚠️ 部分使用條件判斷(缺少完整條件) (+2)")
    elif has_if and has_elif and has_else:
        total_marks += 1
        feedback.append("⚠️ 使用if-elif-else但條件可能不正確 (+1)")
    else:
        feedback.append("❌ 未正確使用條件判斷 (+0)")
    
    # Rubric 5: 正確輸出 (3分) - print(), round() for average
    if successful_runs > 0:
        sample_result = next((r for r in test_results if r["success"]), None)
        if sample_result and sample_result["output"].strip():
            output = sample_result["output"].lower()
            
            has_total_output = 'total' in output
            has_average_output = 'average' in output or 'avg' in output
            has_grade_output = 'grade' in output
            has_remark_output = 'remark' in output
            
            # Check for round() usage
            has_round = 'round(' in code_lower
            
            if has_total_output and has_average_output and has_grade_output and has_remark_output:
                if has_round:
                    total_marks += 3
                    feedback.append("✅ 正確輸出(包含Total、Average、Grade、Remark，使用round()) (+3)")
                else:
                    total_marks += 2
                    feedback.append("⚠️ 輸出格式正確但未使用round() (+2)")
            elif (has_total_output and has_average_output) or (has_grade_output and has_remark_output):
                if has_round:
                    total_marks += 2
                    feedback.append("⚠️ 輸出格式部分正確但使用round() (+2)")
                else:
                    total_marks += 1
                    feedback.append("⚠️ 輸出格式部分正確且未使用round() (+1)")
            else:
                feedback.append("❌ 輸出格式不正確 (+0)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    else:
        # Check static analysis
        has_print = 'print(' in code_lower
        has_round = 'round(' in code_lower
        has_output_vars = ('total' in code_lower or 'grade' in code_lower)
        
        if has_print and has_output_vars:
            if has_round:
                total_marks += 2
                feedback.append("⚠️ 程式碼有輸出邏輯和round()但執行失敗 (+2)")
            else:
                total_marks += 1
                feedback.append("⚠️ 程式碼有輸出邏輯但執行失敗且未使用round() (+1)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    
    # Rubric 6: 執行沒有錯誤 (3分) - execution correctness
    if successful_runs > 0:
        accurate_matches = 0
        
        for i, result in enumerate(test_results):
            if result["success"]:
                student_output = result["output"].strip()
                expected = result["expected"]
                
                # Extract values from output
                total = extract_total(student_output)
                avg = extract_average(student_output)
                grade = extract_grade(student_output)
                remark = extract_remark(student_output)
                
                # Check accuracy with tolerance
                total_correct = (total == expected["expected_total"])
                avg_correct = avg is not None and abs(avg - expected["expected_avg"]) < 0.1
                grade_correct = (grade == expected["expected_grade"])
                # Remark check (allow case variations)
                remark_correct = remark is not None and expected["expected_remark"].lower() in remark.lower()
                
                if total_correct and avg_correct and grade_correct and remark_correct:
                    accurate_matches += 1
                elif (total_correct and avg_correct) or (grade_correct and remark_correct):
                    accurate_matches += 0.5  # Partial credit
        
        # Check accuracy: 3分 for all correct, 2分 for mostly correct, 1分 for partially correct
        if accurate_matches >= len(TEST_CASES) - 0.5:
            total_marks += 3
            feedback.append(f"✅ 能執行且輸出正確 ({int(accurate_matches)}個準確結果) (+3)")
        elif accurate_matches >= len(TEST_CASES) * 0.7:
            total_marks += 2
            feedback.append(f"⚠️ 能執行部份輸出正確 ({int(accurate_matches)}個準確結果) (+2)")
        elif accurate_matches >= len(TEST_CASES) * 0.4:
            total_marks += 1
            feedback.append(f"⚠️ 能執行但只有少部份輸出正確 ({int(accurate_matches)}個準確結果) (+1)")
        else:
            feedback.append(f"❌ 執行錯誤或輸出不正確 ({int(accurate_matches)}個準確結果) (+0)")
    else:
        feedback.append("❌ 程式無法執行 (+0)")
    
    # Generate overall feedback
    if total_marks >= 14:
        overall_feedback = f"✅ 優秀！總分 {total_marks}/15"
    elif total_marks >= 12:
        overall_feedback = f"✅ 良好！總分 {total_marks}/15"
    elif total_marks >= 9:
        overall_feedback = f"⚠️ 基本合格！總分 {total_marks}/15"
    elif total_marks >= 5:
        overall_feedback = f"❌ 需要改進！總分 {total_marks}/15"
    else:
        overall_feedback = f"❌ 不及格！總分 {total_marks}/15"
    
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

        # (15 marks) The python code implements travel expense grading correctly
        section_description = "Python程式碼實現旅行費用評級"
        filepath = row["filepath"]
        section_mark, remarks = evaluate_travel_expense_program(filepath)

        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark, 15)

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

