import aia_util as aia_utils
import difflib
from contextlib import redirect_stdout
from unittest.mock import patch, MagicMock
import io

# Test cases with different inputs and expected outputs
TEST_CASES = [
    {
        "input": ["*", "U"],
        "expected": "Eye: Mouth: -------\n|     |\n| * * |\n|  U  |\n|     |\n-------"
    },
    {
        "input": ["O", "V"],
        "expected": "Eye: Mouth: -------\n|     |\n| O O |\n|  V  |\n|     |\n-------"
    },
    {
        "input": ["@", "X"],
        "expected": "Eye: Mouth: -------\n|     |\n| @ @ |\n|  X  |\n|     |\n-------"
    },
    {
        "input": ["^", "o"],
        "expected": "Eye: Mouth: -------\n|     |\n| ^ ^ |\n|  o  |\n|     |\n-------"
    },
    {
        "input": ["#", "-"],
        "expected": "Eye: Mouth: -------\n|     |\n| # # |\n|  -  |\n|     |\n-------"
    },
    {
        "input": ["+", "~"],
        "expected": "Eye: Mouth: -------\n|     |\n| + + |\n|  ~  |\n|     |\n-------"
    },
    {
        "input": ["%", "="],
        "expected": "Eye: Mouth: -------\n|     |\n| % % |\n|  =  |\n|     |\n-------"
    },
    {
        "input": ["&", "W"],
        "expected": "Eye: Mouth: -------\n|     |\n| & & |\n|  W  |\n|     |\n-------"
    },
    {
        "input": ["$", "P"],
        "expected": "Eye: Mouth: -------\n|     |\n| $ $ |\n|  P  |\n|     |\n-------"
    },
    {
        "input": ["!", "?"],
        "expected": "Eye: Mouth: -------\n|     |\n| ! ! |\n|  ?  |\n|     |\n-------"
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
    
    # Check for string concatenation or formatting
    if '+' in code or 'f"' in code or '.format(' in code:
        score += 1
        explanation.append("✅ 使用字串連接或格式化")
    
    # Check for variable assignment
    if '=' in code and 'input' in code_lower:
        score += 1
        explanation.append("✅ 使用變數儲存輸入")
    
    # Check for multiple print statements
    if code.count('print(') >= 6:  # Should have 6 print statements for the face pattern
        score += 1
        explanation.append("✅ 使用多個print語句")
    
    # Check for face pattern elements
    if '|' in code and '-' in code:
        score += 1
        explanation.append("✅ 包含臉部圖案元素")
    
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

def detect_hardcoded_values(student_code):
    """Detect if student is using hardcoded values instead of variables"""
    # Check for common hardcoded face patterns in print statements
    hardcoded_patterns = [
        'print("| ^ ^ |")', 'print("| ^^ |")', 'print("| ^  ^ |")',
        'print("| o o |")', 'print("| oo |")', 'print("| o  o |")',
        'print("| * * |")', 'print("| ** |")', 'print("| *  * |")',
        'print("| @ @ |")', 'print("| @@ |")', 'print("| @  @ |")',
        'print("| -  |")', 'print("|  -  |")', 'print("| _  |")', 'print("|  _  |")',
        'print("| u  |")', 'print("|  u  |")', 'print("| v  |")', 'print("|  v  |")',
        'print("| ~  |")', 'print("|  ~  |")', 'print("| =  |")', 'print("|  =  |")'
    ]
    
    for pattern in hardcoded_patterns:
        if pattern in student_code:
            return True, f"發現硬編碼值: {pattern}"
    
    # Check for hardcoded characters in print statements
    lines = student_code.split('\n')
    for line in lines:
        if 'print(' in line and ('"' in line or "'" in line):
            # Extract the content between quotes
            if '|' in line and ('^' in line or 'o' in line or '*' in line or '@' in line):
                return True, f"發現硬編碼字符: {line.strip()}"
            if '|' in line and ('-' in line or '_' in line or 'u' in line or 'v' in line or '~' in line or '=' in line):
                return True, f"發現硬編碼字符: {line.strip()}"
    
    return False, ""

def check_variable_usage_in_print(student_code):
    """Check if variables are properly used in print statements"""
    lines = student_code.split('\n')
    print_lines = [line for line in lines if 'print(' in line]
    
    variable_usage_score = 0
    issues = []
    
    for line in print_lines:
        # Check if line contains variables (not just hardcoded strings)
        if '"' in line or "'" in line:
            # This might be a hardcoded string
            if '|' in line and not any(char in line for char in ['eye', 'mouth', '+', 'format']):
                issues.append(f"硬編碼字串: {line.strip()}")
            else:
                variable_usage_score += 1
        elif any(var in line for var in ['eye', 'mouth']):
            # Variable usage detected
            variable_usage_score += 1
    
    return variable_usage_score, issues

def evaluate_face_pattern(filepath):
    """Evaluate student's face pattern program with specific criteria (2 marks each)"""
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
    
    # 1. Check for correct input() usage (2 marks) - More lenient
    input_count = student_code.count('input(')
    if input_count >= 2:
        total_marks += 2
        feedback.append("✅ 正確使用兩個input函數 (+2)")
    elif input_count >= 1:
        total_marks += 2  # Still give full marks if they use at least 1 input
        feedback.append("✅ 使用input函數 (+2)")
    else:
        total_marks += 1  # Give 1 mark even if no input (they might hardcode for testing)
        feedback.append("⚠️ 未使用input函數，可能使用硬編碼測試 (+1)")
    
    # 2. Check for correct number of print() statements (2 marks) - Correct expectation: 6 prints
    print_count = student_code.count('print(')
    if print_count >= 6:  # Model answer has 6 prints
        total_marks += 2
        feedback.append(f"✅ 正確使用{print_count}個print函數 (+2)")
    elif print_count >= 4:  # At least 4 prints (reasonable attempt)
        total_marks += 2  # Still give full marks
        feedback.append(f"✅ 使用{print_count}個print函數 (+2)")
    elif print_count >= 2:
        total_marks += 1
        feedback.append(f"⚠️ 使用{print_count}個print函數，建議使用6個 (+1)")
    else:
        feedback.append(f"❌ print函數太少 (+0)")
    
    # 3. Check for variable usage in print() functions (2 marks) - Much more lenient
    has_variables_in_print = False
    has_hardcoded = False
    
    lines = student_code.split('\n')
    for line in lines:
        if 'print(' in line:
            # Check if line contains variables (eye, mouth) or string concatenation/formatting
            if any(var in line.lower() for var in ['eye', 'mouth']) or ('+' in line and ('"' in line or "'" in line)) or 'f"' in line or '.format(' in line:
                has_variables_in_print = True
            # Only mark as hardcoded if it's clearly copying the pattern without any logic
            elif '|' in line and ('^' in line or 'o' in line or '*' in line or '@' in line or 
                                '-' in line or '_' in line or 'u' in line or 'v' in line):
                has_hardcoded = True
    
    # Be more forgiving - focus on whether they're trying to solve the problem
    if has_variables_in_print:
        total_marks += 2
        feedback.append("✅ 正確在print函數中使用變數 (+2)")
    elif has_hardcoded:
        total_marks += 2  # Still give full marks even if hardcoded - they solved the problem!
        feedback.append("✅ 使用print函數輸出圖案 (+2)")
    else:
        total_marks += 1  # Give 1 mark for effort
        feedback.append("⚠️ 程式碼結構基本正確 (+1)")
    
    # 4. Check if program is runnable (2 marks)
    if successful_runs > 0:
        total_marks += 2
        feedback.append(f"✅ 程式可執行，{successful_runs}/{len(TEST_CASES)}個測試通過 (+2)")
    else:
        # Check if it has basic structure even if not runnable
        if 'input(' in student_code and 'print(' in student_code:
            total_marks += 1
            feedback.append("⚠️ 程式有基本結構但無法執行 (+1)")
        else:
            feedback.append("❌ 程式無法執行且結構不完整 (+0)")
    
    # 5. Check for correct output (2 marks) - Much more lenient
    if successful_runs > 0:
        perfect_matches = 0
        good_matches = 0
        fair_matches = 0
        
        for i, result in enumerate(test_results):
            if result["success"]:
                student_output = result["output"].strip()
                expected_output = TEST_CASES[i]["expected"].strip()
                
                # Calculate similarity
                similarity = calculate_similarity(student_output, expected_output)
                if similarity >= 0.85:  # Lowered from 0.9
                    perfect_matches += 1
                elif similarity >= 0.6:  # Lowered from 0.7
                    good_matches += 1
                elif similarity >= 0.4:  # Even lower threshold
                    fair_matches += 1
        
        total_matches = perfect_matches + good_matches + fair_matches
        
        # Much more lenient grading
        if perfect_matches >= 5:  # At least half perfect
            total_marks += 2
            feedback.append(f"✅ 輸出非常正確 ({perfect_matches}個完美匹配) (+2)")
        elif perfect_matches >= 2 or good_matches >= 5:  # Some good attempts
            total_marks += 2
            feedback.append(f"✅ 輸出正確 ({perfect_matches}個完美匹配, {good_matches}個良好匹配) (+2)")
        elif total_matches >= 3:  # At least some matches
            total_marks += 2  # Still give full marks!
            feedback.append(f"✅ 輸出基本正確 ({total_matches}個有效匹配) (+2)")
        elif successful_runs >= 5:  # At least half run successfully
            total_marks += 1
            feedback.append(f"⚠️ 程式可執行但輸出需改進 ({successful_runs}個測試通過) (+1)")
        else:
            total_marks += 1  # Give 1 mark for trying
            feedback.append(f"⚠️ 程式部分可執行 ({successful_runs}個測試通過) (+1)")
    else:
        # Give 0 only if nothing works
        feedback.append("❌ 程式無法執行，無法評估輸出 (+0)")
    
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

        # (10 marks) The python code creates face pattern correctly
        section_description = "Python程式碼輸出臉部圖案"
        filepath = row["filepath"]
        section_mark, remarks = evaluate_face_pattern(filepath)

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
