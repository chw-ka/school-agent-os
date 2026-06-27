import aia_util as aia_utils
import difflib
import re
from contextlib import redirect_stdout
from unittest.mock import patch, MagicMock
import io

# Test cases for bank withdrawal program
# Initial balance is 2000
# Each test case is a sequence of withdrawal amounts, ending with 0 to exit
TEST_CASES = [
    {
        "input": ["100", "200", "0"],  # Valid withdrawals then exit
        "expected_final_balance": 1700,
        "description": "Valid withdrawals"
    },
    {
        "input": ["500", "300", "100", "0"],
        "expected_final_balance": 1100,
        "description": "Multiple valid withdrawals"
    },
    {
        "input": ["1000", "500", "300", "200", "0"],
        "expected_final_balance": 0,
        "description": "Withdraw all balance"
    },
    {
        "input": ["50", "0"],  # Invalid: not multiple of 100
        "expected_final_balance": 2000,
        "description": "Invalid amount (not multiple of 100)"
    },
    {
        "input": ["-100", "0"],  # Invalid: negative
        "expected_final_balance": 2000,
        "description": "Invalid amount (negative)"
    },
    {
        "input": ["100", "2500", "0"],  # First valid, second exceeds balance
        "expected_final_balance": 1900,
        "description": "Insufficient balance check"
    },
    {
        "input": ["150", "0"],  # Invalid: not multiple of 100
        "expected_final_balance": 2000,
        "description": "Invalid amount (150 not multiple of 100)"
    },
    {
        "input": ["1000", "1500", "0"],  # First valid, second exceeds remaining balance
        "expected_final_balance": 1000,
        "description": "Insufficient balance after first withdrawal"
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

def extract_initial_balance(output):
    """Extract initial balance from output"""
    output_lower = output.lower()
    
    # Look for "Initial balance = $2000"
    patterns = [
        r'initial\s+balance\s*[=:]\s*\$?\s*(\d+)',
        r'initial\s+balance\s+\$?\s*(\d+)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, output_lower, re.IGNORECASE)
        if matches:
            try:
                return int(matches[0])
            except:
                pass
    
    return None

def extract_final_balance(output):
    """Extract final balance from output"""
    output_lower = output.lower()
    
    # Look for "Final balance = $1000"
    patterns = [
        r'final\s+balance\s*[=:]\s*\$?\s*(\d+)',
        r'final\s+balance\s+\$?\s*(\d+)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, output_lower, re.IGNORECASE)
        if matches:
            try:
                return int(matches[-1])  # Take the last match (final balance)
            except:
                pass
    
    return None

def extract_last_balance(output):
    """Extract the last balance mentioned (could be final or last withdrawal)"""
    output_lower = output.lower()
    
    # Find all balance mentions
    patterns = [
        r'balance\s*[=:]\s*\$?\s*(\d+)',
        r'new\s+balance\s*[=:]\s*\$?\s*(\d+)',
    ]
    
    all_balances = []
    for pattern in patterns:
        matches = re.findall(pattern, output_lower, re.IGNORECASE)
        if matches:
            all_balances.extend([int(m) for m in matches])
    
    if all_balances:
        return all_balances[-1]  # Return the last balance
    
    return None

def check_withdrawal_logic(output, inputs, expected_final):
    """Check if withdrawal logic is correct"""
    output_lower = output.lower()
    
    # Remove the last input (0 for exit)
    withdrawal_amounts = [int(x) for x in inputs[:-1] if x != '0']
    initial_balance = extract_initial_balance(output)
    
    if initial_balance is None:
        initial_balance = 2000  # Default initial balance
    
    current_balance = initial_balance
    
    # Track if invalid/insufficient messages appeared
    invalid_count = output_lower.count('invalid amount')
    insufficient_count = output_lower.count('not enough balance')
    
    # Count valid withdrawals
    success_count = output_lower.count('withdrawal successful')
    
    # Simulate the withdrawal logic
    for amt in withdrawal_amounts:
        # Check validation
        if amt < 0 or amt % 100 != 0:
            # Should show invalid message
            continue
        elif amt > current_balance:
            # Should show insufficient message
            continue
        else:
            # Valid withdrawal
            current_balance -= amt
    
    # Check if final balance matches
    final_balance = extract_final_balance(output)
    if final_balance is None:
        final_balance = extract_last_balance(output)
    
    if final_balance is not None:
        return abs(final_balance - expected_final) <= 1  # Allow small tolerance
    
    return False

def analyze_code_quality(code):
    """Analyze code quality for non-running programs"""
    score = 0
    explanation = []
    
    code_lower = code.lower()
    
    # Check for balance initialization
    if 'balance' in code_lower and ('=' in code or 'int(' in code_lower):
        score += 1
        explanation.append("✅ 初始化balance變數")
    
    # Check for while loop
    if 'while' in code_lower:
        score += 1
        explanation.append("✅ 使用while循環")
    
    # Check for break statement
    if 'break' in code_lower:
        score += 1
        explanation.append("✅ 使用break語句")
    
    # Check for input function
    if 'input(' in code_lower:
        score += 1
        explanation.append("✅ 使用input函數")
    
    # Check for int() conversion
    if 'int(' in code_lower:
        score += 1
        explanation.append("✅ 使用int()轉換")
    
    # Check for if statements with continue
    if 'if' in code_lower and 'continue' in code_lower:
        score += 1
        explanation.append("✅ 使用if條件判斷和continue")
    
    # Check for validation logic (negative check, modulus check)
    if ('<' in code or '>=' in code) and ('%' in code or 'mod' in code_lower):
        score += 1
        explanation.append("✅ 檢查負數和100的倍數")
    
    # Check for balance subtraction
    if '-=' in code or ('balance' in code_lower and '-' in code):
        score += 1
        explanation.append("✅ 更新餘額")
    
    # Check for print statements
    print_count = code.count('print(')
    if print_count >= 3:
        score += 1
        explanation.append("✅ 使用多個print函數輸出訊息")
    
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

def evaluate_withdrawal_program(filepath):
    """Evaluate student's withdrawal program with specific criteria (2 marks each)"""
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
    
    # 1. Check for balance initialization and while loop with break (2 marks)
    code_lower = student_code.lower()
    has_balance_init = 'balance' in code_lower and ('=' in code_lower or 'int(' in code_lower)
    has_while = 'while' in code_lower
    has_break = 'break' in code_lower
    
    if has_balance_init and has_while and has_break:
        total_marks += 2
        feedback.append("✅ 正確初始化balance、使用while循環和break (+2)")
    elif has_balance_init and has_while:
        total_marks += 1
        feedback.append("⚠️ 初始化balance和使用while但缺少break (+1)")
    elif has_balance_init or has_while:
        total_marks += 1
        feedback.append("⚠️ 部分使用balance初始化或while循環 (+1)")
    else:
        feedback.append("❌ 未初始化balance或使用while循環 (+0)")
    
    # 2. Check for input handling and int() conversion (2 marks)
    input_count = student_code.count('input(')
    has_int = 'int(' in code_lower
    
    if input_count >= 1 and has_int:
        # Check if int() is used with input
        if 'int(input(' in code_lower:
            total_marks += 2
            feedback.append("✅ 正確使用input函數和int()轉換 (+2)")
        else:
            total_marks += 1
            feedback.append("⚠️ 使用input和int()但可能未正確結合 (+1)")
    elif input_count >= 1:
        total_marks += 1
        feedback.append("⚠️ 使用input但缺少int()轉換 (+1)")
    else:
        feedback.append("❌ 未正確使用input函數 (+0)")
    
    # 3. Check for validation logic (negative check, multiple of 100, balance check) (2 marks)
    has_negative_check = ('< 0' in code_lower or '<= 0' in code_lower or 'amt < 0' in code_lower)
    has_modulus_check = ('%' in student_code and '100' in code_lower)
    has_balance_check = ('amt' in code_lower and 'balance' in code_lower and ('>' in code or '<' in code))
    has_continue = 'continue' in code_lower
    
    if (has_negative_check or has_modulus_check) and has_balance_check and has_continue:
        total_marks += 2
        feedback.append("✅ 正確檢查負數/100倍數和餘額不足，使用continue (+2)")
    elif (has_negative_check or has_modulus_check) and has_continue:
        total_marks += 1
        feedback.append("⚠️ 部分檢查但缺少餘額檢查或continue (+1)")
    elif has_negative_check or has_modulus_check or has_balance_check:
        total_marks += 1
        feedback.append("⚠️ 部分使用驗證邏輯 (+1)")
    else:
        feedback.append("❌ 未使用必要的驗證邏輯 (+0)")
    
    # 4. Check for appropriate output format (2 marks)
    if successful_runs > 0:
        sample_result = next((r for r in test_results if r["success"]), None)
        if sample_result and sample_result["output"].strip():
            output = sample_result["output"].lower()
            
            has_initial = 'initial balance' in output
            has_final = 'final balance' in output
            has_success = 'withdrawal successful' in output or 'new balance' in output
            has_invalid_msg = 'invalid amount' in output
            has_insufficient_msg = 'not enough balance' in output or 'insufficient' in output
            
            if has_initial and has_final:
                total_marks += 2
                feedback.append("✅ 輸出格式正確(包含Initial balance和Final balance) (+2)")
            elif has_initial or has_final:
                total_marks += 1
                feedback.append("⚠️ 輸出格式部分正確(缺少Initial或Final balance) (+1)")
            else:
                feedback.append("❌ 輸出格式不正確 (+0)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    else:
        if 'print(' in code_lower and ('balance' in code_lower or 'initial' in code_lower):
            total_marks += 1
            feedback.append("⚠️ 程式碼有輸出邏輯但執行失敗 (+1)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    
    # 5. Check for results closely matching model answers (2 marks)
    if successful_runs > 0:
        accurate_matches = 0
        
        for i, result in enumerate(test_results):
            if result["success"]:
                student_output = result["output"].strip()
                inputs = result["input"]
                expected_final = result["expected"]["expected_final_balance"]
                
                # Check if withdrawal logic is correct
                if check_withdrawal_logic(student_output, inputs, expected_final):
                    accurate_matches += 1
        
        # Check accuracy
        if accurate_matches >= len(TEST_CASES) - 1:
            total_marks += 2
            feedback.append(f"✅ 提款邏輯完全正確 ({accurate_matches}個準確結果) (+2)")
        elif accurate_matches >= len(TEST_CASES) - 2:
            total_marks += 1
            feedback.append(f"⚠️ 提款邏輯部分正確 ({accurate_matches}個準確結果) (+1)")
        else:
            feedback.append(f"❌ 提款邏輯不正確 ({accurate_matches}個準確結果) (+0)")
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

        # (10 marks) The python code implements withdrawal system correctly
        section_description = "Python程式碼實現提款系統"
        filepath = row["filepath"]
        section_mark, remarks = evaluate_withdrawal_program(filepath)

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

