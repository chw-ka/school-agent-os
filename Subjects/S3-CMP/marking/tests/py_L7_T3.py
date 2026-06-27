import aia_util as aia_utils
import difflib
import re
from contextlib import redirect_stdout
from unittest.mock import patch, MagicMock
import io

# Test cases with different clap numbers
# We'll test a few key numbers to verify the logic
TEST_CASES = [
    {
        "input": ["3"],
        "clap_number": 3
    },
    {
        "input": ["5"],
        "clap_number": 5
    },
    {
        "input": ["7"],
        "clap_number": 7
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

def calculate_clap_accuracy(student_output, clap_number):
    """Calculate if clap logic is correct by checking clap count and output structure"""
    output_lower = student_output.lower()
    
    # Calculate expected number of claps
    expected_clap_count = len([n for n in range(1, 101) if (n % clap_number == 0) or (str(clap_number) in str(n))])
    
    # Count actual claps in output
    clap_count = output_lower.count('clap')
    
    # Check if output has reasonable structure (contains numbers and claps)
    has_numbers = any(str(i) in output_lower for i in range(1, 11))
    has_claps = 'clap' in output_lower
    
    # Verify clap count is within reasonable range (allow 15% variance)
    clap_count_ok = abs(clap_count - expected_clap_count) <= expected_clap_count * 0.15
    
    # Check that output has multiple lines (should have newlines every 10 items)
    has_newlines = '\n' in student_output
    
    # If all basic checks pass, consider it correct
    return has_numbers and has_claps and clap_count_ok and has_newlines

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
    
    # Check for modulo operator
    if '%' in code:
        score += 1
        explanation.append("✅ 使用模運算符")
    
    # Check for string conversion
    if 'str(' in code_lower:
        score += 1
        explanation.append("✅ 使用str()轉換")
    
    # Check for 'in' operator
    if ' in ' in code_lower:
        score += 1
        explanation.append("✅ 使用in運算符")
    
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
                "clap_number": test_case["clap_number"]
            })
        except Exception as e:
            test_results.append({
                "input": test_case["input"],
                "success": False,
                "output": buffer.getvalue(),
                "error": str(e),
                "clap_number": test_case["clap_number"]
            })
    
    return test_results

def evaluate_clap_program(filepath):
    """Evaluate student's clap game program with specific criteria (2 marks each)"""
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
        # Check if output has clap-related content
        sample_result = next((r for r in test_results if r["success"]), None)
        if sample_result and sample_result["output"].strip():
            output = sample_result["output"].lower()
            if 'clap' in output:
                total_marks += 2
                feedback.append("✅ 輸出格式正確(包含Clap訊息) (+2)")
            else:
                total_marks += 1
                feedback.append("⚠️ 輸出格式部分正確 (+1)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    else:
        # Check static analysis for print statements
        if 'print(' in code_lower and 'clap' in code_lower:
            total_marks += 1
            feedback.append("⚠️ 程式碼有輸出邏輯但執行失敗 (+1)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    
    # 3. Check for for loop with range(1, 101) (2 marks)
    has_for = 'for' in code_lower
    has_range = 'range(' in code_lower
    
    if has_for and has_range:
        # Check if range is used for 1 to 100 (range(1, 101) or range(1,101))
        if ('range(1' in code_lower and '101' in code_lower) or ('range(1,101' in code_lower):
            total_marks += 2
            feedback.append("✅ 正確使用for循環和range函數(1到100) (+2)")
        else:
            total_marks += 1
            feedback.append("⚠️ 部分使用for循環和range (+1)")
    elif has_for:
        total_marks += 1
        feedback.append("⚠️ 使用for循環但缺少range (+1)")
    else:
        feedback.append("❌ 未使用for循環和range (+0)")
    
    # 4. Check for modulo operator and string checking (2 marks)
    has_modulo = '%' in student_code
    has_str = 'str(' in code_lower
    has_in = ' in ' in code_lower
    has_or = ' or ' in code_lower
    
    if has_modulo and has_str and has_in and has_or:
        total_marks += 2
        feedback.append("✅ 正確使用模運算符、str()轉換、in運算符和OR邏輯 (+2)")
    elif has_modulo and (has_str or has_in):
        total_marks += 1
        feedback.append("⚠️ 部分使用模運算符或字串檢查 (+1)")
    else:
        feedback.append("❌ 未使用必要的運算符和邏輯 (+0)")
    
    # 5. Check for results closely matching model answers (2 marks)
    if successful_runs > 0:
        accurate_clap_matches = 0
        
        for i, result in enumerate(test_results):
            if result["success"]:
                student_output = result["output"].strip()
                clap_number = result.get("clap_number", 3)
                
                # Check if clap logic is correct
                if calculate_clap_accuracy(student_output, clap_number):
                    accurate_clap_matches += 1
        
        # Check accuracy based on correct logic
        if accurate_clap_matches >= len(TEST_CASES) - 1:
            total_marks += 2
            feedback.append(f"✅ Clap邏輯完全正確 ({accurate_clap_matches}個準確結果) (+2)")
        elif accurate_clap_matches >= len(TEST_CASES) - 2:
            total_marks += 1
            feedback.append(f"⚠️ Clap邏輯部分正確 ({accurate_clap_matches}個準確結果) (+1)")
        else:
            feedback.append(f"❌ Clap邏輯不正確 ({accurate_clap_matches}個準確結果) (+0)")
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

        # (10 marks) The python code implements clap game correctly
        section_description = "Python程式碼實現Clap遊戲"
        filepath = row["filepath"]
        section_mark, remarks = evaluate_clap_program(filepath)

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

