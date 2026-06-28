import aia_util as aia_utils
import difflib
from contextlib import redirect_stdout
from unittest.mock import patch, MagicMock
import io

# Test cases with different level and amount inputs and expected outputs
TEST_CASES = [
    {
        "input": ["gold", "200"],
        "expected": "15% off"
    },
    {
        "input": ["gold", "250"],
        "expected": "15% off"
    },
    {
        "input": ["gold", "199"],
        "expected": "No discount"
    },
    {
        "input": ["gold", "100"],
        "expected": "No discount"
    },
    {
        "input": ["silver", "500"],
        "expected": "10% off"
    },
    {
        "input": ["silver", "600"],
        "expected": "10% off"
    },
    {
        "input": ["silver", "499"],
        "expected": "No discount"
    },
    {
        "input": ["silver", "300"],
        "expected": "No discount"
    },
    {
        "input": ["silver", "500"],
        "expected": "No discount"
    },
    {
        "input": ["silver", "1000"],
        "expected": "No discount"
    },
    {
        "input": ["gold", "0"],
        "expected": "No discount"
    },
    {
        "input": ["abc", "100"],
        "expected": "No discount"
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

def extract_discount(output):
    """Extract discount information from output"""
    output_lower = output.lower()
    
    # Check for 15% off
    if '15%' in output_lower or ('15' in output_lower and '%' in output_lower and 'off' in output_lower):
        return 'discount_15'
    # Check for 10% off
    elif '10%' in output_lower or ('10' in output_lower and '%' in output_lower and 'off' in output_lower):
        return 'discount_10'
    # Check for no discount
    elif 'no discount' in output_lower or ('no' in output_lower and 'discount' in output_lower):
        return 'no_discount'
    
    return None

def calculate_discount_accuracy(student_output, level, amount):
    """Calculate if discount logic is correct"""
    student_result = extract_discount(student_output)
    
    # Determine expected result based on level and amount
    amount_int = int(amount)
    
    if level.lower() == "gold" and amount_int >= 200:
        expected_result = 'discount_15'
    elif level.lower() == "silver" and amount_int >= 500:
        expected_result = 'discount_10'
    else:
        expected_result = 'no_discount'
    
    return student_result == expected_result

def analyze_code_quality(code):
    """Analyze code quality for non-running programs"""
    score = 0
    explanation = []
    
    code_lower = code.lower()
    
    # Check for input function
    input_count = code.count('input(')
    if input_count >= 1:
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
    
    # Check for AND operator
    if ' and ' in code_lower or 'and' in code_lower:
        score += 1
        explanation.append("✅ 使用AND運算符")
    
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

def evaluate_discount_program(filepath):
    """Evaluate student's discount program with specific criteria (2 marks each)"""
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
        # Check if int() is used with input for amount
        if 'int(input(' in code_lower or ('int(' in code_lower and 'amount' in code_lower):
            total_marks += 2
            feedback.append("✅ 正確使用int()函數轉換金額 (+2)")
        else:
            total_marks += 1
            feedback.append("⚠️ 部分使用int()函數 (+1)")
    else:
        feedback.append("❌ 未使用int()函數 (+0)")
    
    # 2. Check for appropriate output (2 marks)
    if successful_runs > 0:
        # Check if output has discount-related content
        sample_result = next((r for r in test_results if r["success"]), None)
        if sample_result and sample_result["output"].strip():
            output = sample_result["output"].lower()
            if '%' in output or 'discount' in output or 'off' in output:
                total_marks += 2
                feedback.append("✅ 輸出格式正確(包含折扣訊息) (+2)")
            else:
                total_marks += 1
                feedback.append("⚠️ 輸出格式部分正確 (+1)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    else:
        # Check static analysis for print statements
        if 'print(' in code_lower and ('%' in code_lower or 'discount' in code_lower):
            total_marks += 1
            feedback.append("⚠️ 程式碼有輸出邏輯但執行失敗 (+1)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    
    # 3. Check for two input() calls (2 marks)
    input_count = student_code.count('input(')
    if input_count >= 2:
        total_marks += 2
        feedback.append("✅ 正確使用兩個input函數(等級和金額) (+2)")
    elif input_count >= 1:
        total_marks += 1
        feedback.append("⚠️ 部分使用input函數(需要兩個) (+1)")
    else:
        feedback.append("❌ 未正確使用input函數 (+0)")
    
    # 4. Check for if-elif-else conditional statements with AND operator (2 marks)
    has_if = 'if' in code_lower
    has_elif = 'elif' in code_lower
    has_else = 'else' in code_lower
    has_comparison = '==' in student_code or '>=' in student_code
    has_and = ' and ' in code_lower
    
    if has_if and has_elif and has_else and has_comparison and has_and:
        total_marks += 2
        feedback.append("✅ 正確使用if-elif-else條件判斷、比較運算符和AND運算符 (+2)")
    elif has_if and has_elif and has_comparison and has_and:
        total_marks += 1
        feedback.append("⚠️ 部分使用條件判斷(缺少else或AND) (+1)")
    elif has_if and has_comparison:
        total_marks += 1
        feedback.append("⚠️ 部分使用條件判斷(缺少elif/else/AND) (+1)")
    else:
        feedback.append("❌ 未使用必要的條件判斷 (+0)")
    
    # 5. Check for results closely matching model answers (2 marks)
    if successful_runs > 0:
        accurate_discount_matches = 0
        
        for i, result in enumerate(test_results):
            if result["success"]:
                student_output = result["output"].strip()
                level = test_results[i]["input"][0]
                amount = test_results[i]["input"][1]
                
                # Check if discount logic is correct
                if calculate_discount_accuracy(student_output, level, amount):
                    accurate_discount_matches += 1
        
        # Check accuracy based on correct logic
        if accurate_discount_matches >= len(TEST_CASES) - 1:
            total_marks += 2
            feedback.append(f"✅ 折扣判斷完全正確 ({accurate_discount_matches}個準確結果) (+2)")
        elif accurate_discount_matches >= len(TEST_CASES) - 2:
            total_marks += 1
            feedback.append(f"⚠️ 折扣判斷部分正確 ({accurate_discount_matches}個準確結果) (+1)")
        else:
            feedback.append(f"❌ 折扣判斷不正確 ({accurate_discount_matches}個準確結果) (+0)")
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

        # (10 marks) The python code determines discount eligibility correctly
        section_description = "Python程式碼判斷折扣資格"
        filepath = row["filepath"]
        section_mark, remarks = evaluate_discount_program(filepath)

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

