import aia_util as aia_utils
import difflib
from contextlib import redirect_stdout
from unittest.mock import patch, MagicMock
import io

# Test cases with different weight and height inputs and expected outputs
TEST_CASES = [
    {
        "input": ["70", "175"],
        "expected": "Weight(kg): Height(cm): BMI = 22.86"
    },
    {
        "input": ["60", "165"],
        "expected": "Weight(kg): Height(cm): BMI = 22.04"
    },
    {
        "input": ["80", "180"],
        "expected": "Weight(kg): Height(cm): BMI = 24.69"
    },
    {
        "input": ["55", "160"],
        "expected": "Weight(kg): Height(cm): BMI = 21.48"
    },
    {
        "input": ["90", "185"],
        "expected": "Weight(kg): Height(cm): BMI = 26.3"
    },
    {
        "input": ["65", "170"],
        "expected": "Weight(kg): Height(cm): BMI = 22.49"
    },
    {
        "input": ["75", "178"],
        "expected": "Weight(kg): Height(cm): BMI = 23.67"
    },
    {
        "input": ["50", "155"],
        "expected": "Weight(kg): Height(cm): BMI = 20.81"
    },
    {
        "input": ["85", "182"],
        "expected": "Weight(kg): Height(cm): BMI = 25.67"
    },
    {
        "input": ["68", "172"],
        "expected": "Weight(kg): Height(cm): BMI = 23.0"
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
    # Normalize for case-insensitive comparison of prompts but case-sensitive for results
    # This allows "height" vs "Height" in prompts to still match
    return difflib.SequenceMatcher(None, output1.strip(), output2.strip()).ratio()

def calculate_bmi_accuracy(student_output, expected_output):
    """Calculate if BMI value is accurate, ignoring prompt case differences"""
    # Extract BMI values from outputs
    import re
    
    # Find BMI value in student output
    student_bmi_match = re.search(r'BMI\s*=\s*([\d.]+)', student_output, re.IGNORECASE)
    expected_bmi_match = re.search(r'BMI\s*=\s*([\d.]+)', expected_output, re.IGNORECASE)
    
    if student_bmi_match and expected_bmi_match:
        try:
            student_bmi = float(student_bmi_match.group(1))
            expected_bmi = float(expected_bmi_match.group(1))
            
            # Check if BMI values are close (within 0.1 tolerance for rounding differences)
            if abs(student_bmi - expected_bmi) < 0.1:
                return True
        except ValueError:
            pass
    
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
    
    # Check for multiplication operation
    if '*' in code:
        score += 1
        explanation.append("✅ 使用乘法運算")
    
    # Check for int() function
    if 'int(' in code_lower:
        score += 1
        explanation.append("✅ 使用int()轉換")
    
    # Check for round() function
    if 'round(' in code_lower:
        score += 1
        explanation.append("✅ 使用round()函數")
    
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

def evaluate_bmi_program(filepath):
    """Evaluate student's BMI calculator program with specific criteria (2 marks each)"""
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
            if 'BMI' in output.upper() and '=' in output:
                total_marks += 2
                feedback.append("✅ 輸出格式正確 (+2)")
            else:
                total_marks += 1
                feedback.append("⚠️ 輸出格式部分正確 (+1)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    else:
        # Check static analysis for print statements
        if 'print(' in code_lower and 'bmi' in code_lower:
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
    
    # 4. Check for division and multiplication operators (2 marks)
    has_division = '/' in student_code
    has_multiplication = '*' in student_code
    has_round = 'round(' in code_lower
    
    if has_division and has_multiplication:
        total_marks += 2
        feedback.append("✅ 正確使用除法和乘法運算 (+2)")
    elif has_division or has_multiplication:
        total_marks += 1
        feedback.append("⚠️ 只使用部分數學運算 (+1)")
    else:
        feedback.append("❌ 未使用必要的數學運算 (+0)")
    
    # 5. Check for results closely matching model answers (2 marks)
    if successful_runs > 0:
        perfect_matches = 0
        accurate_bmi_matches = 0
        
        for i, result in enumerate(test_results):
            if result["success"]:
                student_output = result["output"].strip()
                expected_output = TEST_CASES[i]["expected"].strip()
                
                # First check if BMI calculation is accurate (ignoring prompt case differences)
                if calculate_bmi_accuracy(student_output, expected_output):
                    accurate_bmi_matches += 1
                    
                    # Then check similarity for exact format match
                    similarity = calculate_similarity(student_output, expected_output)
                    if similarity >= 0.85:
                        perfect_matches += 1
        
        # Prioritize BMI accuracy over exact format match
        if accurate_bmi_matches >= len(TEST_CASES) - 1:
            total_marks += 2
            feedback.append(f"✅ BMI計算完全正確 ({accurate_bmi_matches}個準確結果) (+2)")
        elif accurate_bmi_matches >= len(TEST_CASES) - 2:
            total_marks += 1
            feedback.append(f"⚠️ BMI計算部分正確 ({accurate_bmi_matches}個準確結果) (+1)")
        else:
            feedback.append(f"❌ BMI計算不正確 ({accurate_bmi_matches}個準確結果) (+0)")
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

        # (10 marks) The python code calculates BMI correctly
        section_description = "Python程式碼計算BMI"
        filepath = row["filepath"]
        section_mark, remarks = evaluate_bmi_program(filepath)

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
