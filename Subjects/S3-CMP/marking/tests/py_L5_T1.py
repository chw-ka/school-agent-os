import aia_util as aia_utils
import difflib
from contextlib import redirect_stdout
from unittest.mock import patch, MagicMock
import io

# Test cases with different grade inputs and expected outputs
TEST_CASES = [
    {
        "input": ["F1"],
        "expected": "Group C (Junior)"
    },
    {
        "input": ["F2"],
        "expected": "Group C (Junior)"
    },
    {
        "input": ["F3"],
        "expected": "Group B (Intermediate)"
    },
    {
        "input": ["F4"],
        "expected": "Group B (Intermediate)"
    },
    {
        "input": ["F5"],
        "expected": "Group A (Senior)"
    },
    {
        "input": ["F6"],
        "expected": "Group A (Senior)"
    },
    {
        "input": ["F7"],
        "expected": "Invalid grade"
    },
    {
        "input": ["F0"],
        "expected": "Invalid grade"
    },
    {
        "input": ["abc"],
        "expected": "Invalid grade"
    },
    {
        "input": ["F"],
        "expected": "Invalid grade"
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

def extract_group(output):
    """Extract group assignment from output"""
    output_lower = output.lower()
    
    # Check for Group A (Senior)
    if 'group a' in output_lower or ('senior' in output_lower and 'group' in output_lower):
        return 'group_a'
    # Check for Group B (Intermediate)
    elif 'group b' in output_lower or ('intermediate' in output_lower and 'group' in output_lower):
        return 'group_b'
    # Check for Group C (Junior)
    elif 'group c' in output_lower or ('junior' in output_lower and 'group' in output_lower):
        return 'group_c'
    # Check for invalid
    elif 'invalid' in output_lower:
        return 'invalid'
    
    return None

def calculate_group_accuracy(student_output, grade):
    """Calculate if group assignment logic is correct"""
    student_result = extract_group(student_output)
    
    # Determine expected result based on grade
    if grade in ["F5", "F6"]:
        expected_result = 'group_a'
    elif grade in ["F3", "F4"]:
        expected_result = 'group_b'
    elif grade in ["F1", "F2"]:
        expected_result = 'group_c'
    else:
        expected_result = 'invalid'
    
    return student_result == expected_result

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
    
    # Check for if statement
    if 'if' in code_lower:
        score += 1
        explanation.append("✅ 使用if條件判斷")
    
    # Check for elif statement
    if 'elif' in code_lower:
        score += 1
        explanation.append("✅ 使用elif分支")
    
    # Check for else statement
    if 'else' in code_lower:
        score += 1
        explanation.append("✅ 使用else分支")
    
    # Check for comparison operator
    if '>=' in code or '<=' in code or '>' in code or '<' in code or '==' in code:
        score += 1
        explanation.append("✅ 使用比較運算符")
    
    # Check for grade-related keywords
    if any(grade in code.upper() for grade in ['F1', 'F2', 'F3', 'F4', 'F5', 'F6']) or 'grade' in code_lower:
        score += 1
        explanation.append("✅ 包含年級相關邏輯")
    
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
    """Evaluate student's grade grouping program with specific criteria (2 marks each)"""
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
    
    # 1. Check for input function usage appropriately (2 marks)
    code_lower = student_code.lower()
    input_count = student_code.count('input(')
    if input_count >= 1:
        # Check if input is used with variable assignment
        if '=' in student_code and 'input(' in code_lower:
            total_marks += 2
            feedback.append("✅ 正確使用input函數和變數儲存 (+2)")
        else:
            total_marks += 1
            feedback.append("⚠️ 部分使用input函數 (+1)")
    else:
        feedback.append("❌ 未使用input函數 (+0)")
    
    # 2. Check for appropriate output (2 marks)
    if successful_runs > 0:
        # Check if output has group-related content
        sample_result = next((r for r in test_results if r["success"]), None)
        if sample_result and sample_result["output"].strip():
            output = sample_result["output"].lower()
            if 'group' in output or 'invalid' in output:
                total_marks += 2
                feedback.append("✅ 輸出格式正確(包含分組訊息) (+2)")
            else:
                total_marks += 1
                feedback.append("⚠️ 輸出格式部分正確 (+1)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    else:
        # Check static analysis for print statements
        if 'print(' in code_lower and ('group' in code_lower or 'invalid' in code_lower):
            total_marks += 1
            feedback.append("⚠️ 程式碼有輸出邏輯但執行失敗 (+1)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    
    # 3. Check for string comparison usage (2 marks)
    if '==' in student_code:
        # Check if == is used for string comparison
        if 'form' in code_lower or 'grade' in code_lower:
            total_marks += 2
            feedback.append("✅ 正確使用==進行字串比較 (+2)")
        else:
            total_marks += 1
            feedback.append("⚠️ 部分使用字串比較 (+1)")
    else:
        feedback.append("❌ 未使用字串比較 (+0)")
    
    # 4. Check for if-elif-else conditional statements (2 marks)
    has_if = 'if' in code_lower
    has_elif = 'elif' in code_lower
    has_else = 'else' in code_lower
    has_comparison = '==' in student_code
    
    if has_if and has_elif and has_else and has_comparison:
        total_marks += 2
        feedback.append("✅ 正確使用if-elif-else條件判斷和==運算符 (+2)")
    elif has_if and has_elif and has_comparison:
        total_marks += 1
        feedback.append("⚠️ 部分使用條件判斷(缺少else) (+1)")
    elif has_if and has_comparison:
        total_marks += 1
        feedback.append("⚠️ 部分使用條件判斷(缺少elif) (+1)")
    else:
        feedback.append("❌ 未使用必要的條件判斷 (+0)")
    
    # 5. Check for results closely matching model answers (2 marks)
    if successful_runs > 0:
        accurate_group_matches = 0
        
        for i, result in enumerate(test_results):
            if result["success"]:
                student_output = result["output"].strip()
                grade = test_results[i]["input"][0]
                
                # Check if group assignment logic is correct
                if calculate_group_accuracy(student_output, grade):
                    accurate_group_matches += 1
        
        # Check accuracy based on correct logic
        if accurate_group_matches >= len(TEST_CASES) - 1:
            total_marks += 2
            feedback.append(f"✅ 年級分組判斷完全正確 ({accurate_group_matches}個準確結果) (+2)")
        elif accurate_group_matches >= len(TEST_CASES) - 2:
            total_marks += 1
            feedback.append(f"⚠️ 年級分組判斷部分正確 ({accurate_group_matches}個準確結果) (+1)")
        else:
            feedback.append(f"❌ 年級分組判斷不正確 ({accurate_group_matches}個準確結果) (+0)")
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

        # (10 marks) The python code determines grade grouping correctly
        section_description = "Python程式碼判斷年級分組"
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

