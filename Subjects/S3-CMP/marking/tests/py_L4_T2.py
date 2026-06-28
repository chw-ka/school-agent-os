import aia_util as aia_utils
import difflib
from contextlib import redirect_stdout
from unittest.mock import patch, MagicMock
import io

# Test cases with different score inputs and expected outputs
TEST_CASES = [
    {
        "input": ["90"],
        "expected": "Score:Excellent"
    },
    {
        "input": ["85"],
        "expected": "Score:Excellent"
    },
    {
        "input": ["80"],
        "expected": "Score:Excellent"
    },
    {
        "input": ["75"],
        "expected": "Score:Pass"
    },
    {
        "input": ["60"],
        "expected": "Score:Pass"
    },
    {
        "input": ["50"],
        "expected": "Score:Pass"
    },
    {
        "input": ["45"],
        "expected": "Score:Fail"
    },
    {
        "input": ["30"],
        "expected": "Score:Fail"
    },
    {
        "input": ["79"],
        "expected": "Score:Pass"
    },
    {
        "input": ["49"],
        "expected": "Score:Fail"
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

def extract_grade_classification(output):
    """Extract grade classification from output"""
    output_lower = output.lower()
    
    # Check for classification keywords
    if 'excellent' in output_lower:
        return 'excellent'
    elif 'pass' in output_lower:
        return 'pass'
    elif 'fail' in output_lower:
        return 'fail'
    
    return None

def calculate_classification_accuracy(student_output, score):
    """Calculate if grade classification logic is correct"""
    student_result = extract_grade_classification(student_output)
    
    # Determine expected result based on score
    score_val = int(score)
    if score_val >= 80:
        expected_result = 'excellent'
    elif score_val >= 50:
        expected_result = 'pass'
    else:
        expected_result = 'fail'
    
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
    
    # Check for int() function
    if 'int(' in code_lower:
        score += 1
        explanation.append("✅ 使用int()轉換")
    
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
    
    # Check for multiple print statements
    if code.count('print(') >= 3:
        score += 1
        explanation.append("✅ 使用多個print語句")
    
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

def evaluate_grade_classification(filepath):
    """Evaluate student's grade classification program with specific criteria (2 marks each)"""
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
        # Check if output has grade classifications
        sample_result = next((r for r in test_results if r["success"]), None)
        if sample_result and sample_result["output"].strip():
            output = sample_result["output"].lower()
            if any(word in output for word in ['excellent', 'pass', 'fail']):
                total_marks += 2
                feedback.append("✅ 輸出格式正確(包含成績分類) (+2)")
            else:
                total_marks += 1
                feedback.append("⚠️ 輸出格式部分正確 (+1)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    else:
        # Check static analysis for print statements
        if 'print(' in code_lower and any(word in code_lower for word in ['excellent', 'pass', 'fail']):
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
    
    # 4. Check for if-elif-else conditional statements (2 marks)
    has_if = 'if' in code_lower
    has_elif = 'elif' in code_lower
    has_else = 'else' in code_lower
    has_comparison = any(op in student_code for op in ['>=', '<=', '>', '<', '==', '!='])
    
    if has_if and has_elif and has_else and has_comparison:
        total_marks += 2
        feedback.append("✅ 正確使用if-elif-else條件判斷和比較運算符 (+2)")
    elif has_if and (has_elif or has_else) and has_comparison:
        total_marks += 1
        feedback.append("⚠️ 部分使用條件判斷(建議使用elif) (+1)")
    elif has_if:
        total_marks += 0
        feedback.append("❌ 只有if條件，缺少elif和else分支 (+0)")
    else:
        feedback.append("❌ 未使用必要的條件判斷 (+0)")
    
    # 5. Check for results closely matching model answers (2 marks)
    if successful_runs > 0:
        accurate_classification_matches = 0
        
        for i, result in enumerate(test_results):
            if result["success"]:
                student_output = result["output"].strip()
                score_input = test_results[i]["input"][0]
                
                # Check if grade classification logic is correct
                if calculate_classification_accuracy(student_output, score_input):
                    accurate_classification_matches += 1
        
        # Check accuracy based on correct logic
        if accurate_classification_matches >= len(TEST_CASES) - 1:
            total_marks += 2
            feedback.append(f"✅ 成績分類判斷完全正確 ({accurate_classification_matches}個準確結果) (+2)")
        elif accurate_classification_matches >= len(TEST_CASES) - 2:
            total_marks += 1
            feedback.append(f"⚠️ 成績分類判斷部分正確 ({accurate_classification_matches}個準確結果) (+1)")
        else:
            feedback.append(f"❌ 成績分類判斷不正確 ({accurate_classification_matches}個準確結果) (+0)")
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

        # (10 marks) The python code classifies grades correctly
        section_description = "Python程式碼分類成績"
        filepath = row["filepath"]
        section_mark, remarks = evaluate_grade_classification(filepath)

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
