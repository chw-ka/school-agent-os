import aia_util as aia_utils
import difflib
import re
from contextlib import redirect_stdout
from unittest.mock import patch, MagicMock
import io

# Test cases for student grading program
TEST_CASES = [
    {
        "input": ["John", "90", "85", "88"],  # Name, Chinese, English, Math
        "expected_total": 263,
        "expected_avg": 87.67,
        "expected_grade": "A",
        "expected_remark": "EXcellent"
    },
    {
        "input": ["Mary", "95", "92", "96"],
        "expected_total": 283,
        "expected_avg": 94.33,
        "expected_grade": "A",
        "expected_remark": "EXcellent"
    },
    {
        "input": ["Tom", "60", "65", "70"],
        "expected_total": 195,
        "expected_avg": 65.0,
        "expected_grade": "B",
        "expected_remark": "Pass"
    },
    {
        "input": ["Alice", "50", "55", "50"],
        "expected_total": 155,
        "expected_avg": 51.67,
        "expected_grade": "B",
        "expected_remark": "Pass"
    },
    {
        "input": ["Bob", "40", "45", "35"],
        "expected_total": 120,
        "expected_avg": 40.0,
        "expected_grade": "C",
        "expected_remark": "Fail"
    },
    {
        "input": ["Eve", "30", "25", "20"],
        "expected_total": 75,
        "expected_avg": 25.0,
        "expected_grade": "C",
        "expected_remark": "Fail"
    },
    {
        "input": ["Sam", "80", "80", "80"],
        "expected_total": 240,
        "expected_avg": 80.0,
        "expected_grade": "A",
        "expected_remark": "EXcellent"
    },
    {
        "input": ["Kate", "79", "79", "79"],
        "expected_total": 237,
        "expected_avg": 79.0,
        "expected_grade": "B",
        "expected_remark": "Pass"
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
    """Extract total score from output"""
    output_lower = output.lower()
    
    # Look for "Total= 263" or "Total = 263" or "Total: 263"
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
    """Extract average score from output"""
    output_lower = output.lower()
    
    # Look for "Average: 87.67" or "Average = 87.67" or "avg: 87.67"
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
    
    # Try to find A, B, or C near "grade"
    if 'grade' in output_lower:
        if 'grade: a' in output_lower or 'grade = a' in output_lower:
            return 'A'
        elif 'grade: b' in output_lower or 'grade = b' in output_lower:
            return 'B'
        elif 'grade: c' in output_lower or 'grade = c' in output_lower:
            return 'C'
    
    return None

def extract_remark(output):
    """Extract remark from output"""
    output_lower = output.lower()
    
    # Look for "Remark: EXcellent" or "Remark: Pass" or "Remark: Fail"
    if 'remark' in output_lower:
        if 'excellent' in output_lower or 'excellent' in output_lower:
            return 'EXcellent'
        elif 'pass' in output_lower:
            return 'Pass'
        elif 'fail' in output_lower:
            return 'Fail'
    
    return None

def calculate_grade_logic(average):
    """Calculate expected grade and remark based on average"""
    if average >= 80:
        return "A", "EXcellent"
    elif average >= 50:
        return "B", "Pass"
    else:
        return "C", "Fail"

def analyze_code_quality(code):
    """Analyze code quality for non-running programs"""
    score = 0
    explanation = []
    
    code_lower = code.lower()
    
    # Check for input function
    input_count = code.count('input(')
    if input_count >= 4:
        score += 1
        explanation.append("✅ 使用多個input函數(姓名和三個成績)")
    elif input_count >= 1:
        score += 1
        explanation.append("✅ 使用input函數")
    
    # Check for int() function
    int_count = code.count('int(')
    if int_count >= 3:
        score += 1
        explanation.append("✅ 使用int()轉換三個成績")
    elif int_count >= 1:
        score += 1
        explanation.append("✅ 使用int()轉換")
    
    # Check for addition (total calculation)
    if '+' in code and ('total' in code_lower or '=' in code):
        score += 1
        explanation.append("✅ 計算總分")
    
    # Check for division (average calculation)
    if '/' in code and ('average' in code_lower or 'avg' in code_lower):
        score += 1
        explanation.append("✅ 計算平均分")
    
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

def evaluate_grading_program(filepath):
    """Evaluate student's grading program with specific criteria (2 marks each)"""
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
    
    # 1. Check for input handling and int() conversion (2 marks)
    code_lower = student_code.lower()
    input_count = student_code.count('input(')
    int_count = student_code.count('int(')
    
    if input_count >= 4 and int_count >= 3:
        total_marks += 2
        feedback.append("✅ 正確使用input函數(姓名和三個成績)和int()轉換 (+2)")
    elif input_count >= 4 and int_count >= 1:
        total_marks += 1
        feedback.append("⚠️ 使用input函數但int()轉換不完整 (+1)")
    elif input_count >= 1 and int_count >= 1:
        total_marks += 1
        feedback.append("⚠️ 部分使用input和int()函數 (+1)")
    else:
        feedback.append("❌ 未正確使用input和int()函數 (+0)")
    
    # 2. Check for total and average calculation (2 marks)
    has_total = '+' in student_code and ('total' in code_lower or 't' in code_lower)
    has_average = '/' in student_code and ('average' in code_lower or 'avg' in code_lower or 'a' in code_lower)
    has_round = 'round(' in code_lower
    
    if has_total and has_average:
        if has_round:
            total_marks += 2
            feedback.append("✅ 正確計算總分和平均分(含round函數) (+2)")
        else:
            total_marks += 1
            feedback.append("⚠️ 計算總分和平均分但缺少round函數 (+1)")
    elif has_total or has_average:
        total_marks += 1
        feedback.append("⚠️ 部分計算總分或平均分 (+1)")
    else:
        feedback.append("❌ 未計算總分和平均分 (+0)")
    
    # 3. Check for appropriate output format (2 marks)
    if successful_runs > 0:
        sample_result = next((r for r in test_results if r["success"]), None)
        if sample_result and sample_result["output"].strip():
            output = sample_result["output"].lower()
            
            has_total_output = 'total' in output
            has_average_output = 'average' in output or 'avg' in output
            has_grade_output = 'grade' in output
            has_remark_output = 'remark' in output
            
            if has_total_output and has_average_output and has_grade_output and has_remark_output:
                total_marks += 2
                feedback.append("✅ 輸出格式正確(包含Total、Average、Grade、Remark) (+2)")
            elif (has_total_output and has_average_output) or (has_grade_output and has_remark_output):
                total_marks += 1
                feedback.append("⚠️ 輸出格式部分正確 (+1)")
            else:
                feedback.append("❌ 輸出格式不正確 (+0)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    else:
        if 'print(' in code_lower and ('total' in code_lower or 'grade' in code_lower):
            total_marks += 1
            feedback.append("⚠️ 程式碼有輸出邏輯但執行失敗 (+1)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    
    # 4. Check for if-elif-else conditional statements with grade logic (2 marks)
    has_if = 'if' in code_lower
    has_elif = 'elif' in code_lower
    has_else = 'else' in code_lower
    has_comparison = '>=' in student_code or '<=' in student_code
    has_grade_logic = ('grade' in code_lower or 'remark' in code_lower) and ('80' in code or '50' in code)
    
    if has_if and has_elif and has_else and has_comparison and has_grade_logic:
        total_marks += 2
        feedback.append("✅ 正確使用if-elif-else條件判斷和等級邏輯 (+2)")
    elif has_if and has_elif and has_comparison:
        total_marks += 1
        feedback.append("⚠️ 部分使用條件判斷(缺少else或等級邏輯) (+1)")
    elif has_if and has_comparison:
        total_marks += 1
        feedback.append("⚠️ 部分使用條件判斷(缺少elif/else) (+1)")
    else:
        feedback.append("❌ 未使用必要的條件判斷 (+0)")
    
    # 5. Check for results closely matching model answers (2 marks)
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
        
        # Check accuracy
        if accurate_matches >= len(TEST_CASES) - 0.5:
            total_marks += 2
            feedback.append(f"✅ 計算和邏輯完全正確 ({int(accurate_matches)}個準確結果) (+2)")
        elif accurate_matches >= len(TEST_CASES) - 1.5:
            total_marks += 1
            feedback.append(f"⚠️ 計算和邏輯部分正確 ({int(accurate_matches)}個準確結果) (+1)")
        else:
            feedback.append(f"❌ 計算和邏輯不正確 ({int(accurate_matches)}個準確結果) (+0)")
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

        # (10 marks) The python code implements student grading correctly
        section_description = "Python程式碼實現學生成績評級"
        filepath = row["filepath"]
        section_mark, remarks = evaluate_grading_program(filepath)

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

