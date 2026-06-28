import aia_util as aia_utils
import difflib
import re
from contextlib import redirect_stdout
from unittest.mock import patch, MagicMock
import io
import multiprocessing as mp

# Test cases for shopping program
# Initial balance is 500
# Each test case is a sequence of prices, ending with 0 to exit
TEST_CASES = [
    {
        "input": ["100", "200", "0"],  # Valid purchases then exit
        "expected_final_balance": 200,
        "description": "Valid purchases"
    },
    {
        "input": ["50", "100", "150", "0"],
        "expected_final_balance": 200,
        "description": "Multiple valid purchases"
    },
    {
        "input": ["500", "0"],  # Purchase all balance
        "expected_final_balance": 0,
        "description": "Purchase all balance"
    },
    {
        "input": ["25", "0"],  # Invalid: not multiple of 5
        "expected_final_balance": 500,
        "description": "Invalid price (not multiple of 5)"
    },
    {
        "input": ["-50", "0"],  # Invalid: negative
        "expected_final_balance": 500,
        "description": "Invalid price (negative)"
    },
    {
        "input": ["100", "600", "0"],  # First valid, second exceeds balance
        "expected_final_balance": 400,
        "description": "Insufficient balance check"
    },
    {
        "input": ["75", "0"],  # Valid: multiple of 5
        "expected_final_balance": 425,
        "description": "Valid purchase (75 is multiple of 5)"
    },
    {
        "input": ["23", "0"],  # Invalid: not multiple of 5
        "expected_final_balance": 500,
        "description": "Invalid price (23 not multiple of 5)"
    },
    {
        "input": ["200", "350", "0"],  # First valid, second exceeds remaining balance
        "expected_final_balance": 300,
        "description": "Insufficient balance after first purchase"
    },
    {
        "input": ["5", "10", "15", "20", "0"],  # Multiple small purchases
        "expected_final_balance": 450,
        "description": "Multiple small valid purchases"
    },
    {
        "input": ["0"],  # Exit immediately
        "expected_final_balance": 500,
        "description": "Exit without purchase"
    }
]

def _exec_student_code_in_subprocess(student_code, test_input, result_queue):
    """Child process target: run student code and return output / errors via queue."""
    buffer = io.StringIO()
    try:
        with redirect_stdout(buffer):
            with patch('builtins.input', side_effect=test_input):
                exec(student_code, {})
        result_queue.put(
            {
                "runs": True,
                "output": buffer.getvalue(),
                "error": "",
            }
        )
    except Exception as e:
        result_queue.put(
            {
                "runs": False,
                "output": buffer.getvalue(),
                "error": str(e),
            }
        )


def run_student_code(student_code, test_input, timeout_seconds=2.0):
    """Run student code with mocked input, with a hard timeout to prevent infinite loops."""
    ctx = mp.get_context("fork")
    result_queue = ctx.Queue()
    p = ctx.Process(
        target=_exec_student_code_in_subprocess, args=(student_code, test_input, result_queue)
    )
    p.start()
    p.join(timeout_seconds)

    if p.is_alive():
        p.terminate()
        p.join(0.2)
        return {
            "runs": False,
            "output": "",
            "error": f"Timeout: program did not finish within {timeout_seconds:.1f}s",
            "timed_out": True,
        }

    try:
        result = result_queue.get_nowait()
    except Exception:
        result = {"runs": False, "output": "", "error": "No result returned", "timed_out": False}

    result["timed_out"] = False
    return result

def calculate_similarity(output1, output2):
    """Calculate similarity between two outputs"""
    return difflib.SequenceMatcher(None, output1.strip(), output2.strip()).ratio()

def extract_initial_balance(output):
    """Extract initial balance from output"""
    output_lower = output.lower()
    
    # Look for "Initial balance = $500"
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
    
    # Look for "Final balance = $200"
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
    """Extract the last balance mentioned (could be final or last purchase)"""
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

def check_purchase_logic(output, inputs, expected_final):
    """Check if purchase logic is correct"""
    output_lower = output.lower()
    
    # Remove the last input (0 for exit)
    prices = [int(x) for x in inputs[:-1] if x != '0']
    initial_balance = extract_initial_balance(output)
    
    if initial_balance is None:
        initial_balance = 500  # Default initial balance
    
    current_balance = initial_balance
    
    # Simulate the purchase logic
    for price in prices:
        # Check validation
        if price < 0 or price % 5 != 0:
            # Should show invalid message - don't deduct
            continue
        elif price > current_balance:
            # Should show insufficient message - don't deduct
            continue
        else:
            # Valid purchase - deduct
            current_balance -= price
    
    # Check if final balance matches
    final_balance = extract_final_balance(output)
    if final_balance is None:
        final_balance = extract_last_balance(output)
    
    if final_balance is not None:
        # Allow small tolerance for rounding or minor differences
        return abs(final_balance - expected_final) <= 1
    
    # If we can't extract final balance, check if the calculated balance matches expected
    return abs(current_balance - expected_final) <= 1

def analyze_code_quality(code):
    """Analyze code quality for non-running programs"""
    score = 0
    explanation = []
    
    code_lower = code.lower()
    
    # Check for balance initialization
    if 'balance' in code_lower and ('=' in code or 'int(' in code_lower):
        if 'balance' in code_lower and '500' in code:
            score += 1
            explanation.append("✅ 初始化balance = 500")
        else:
            score += 1
            explanation.append("✅ 初始化balance變數")
    
    # Check for while True loop
    if 'while true' in code_lower:
        score += 1
        explanation.append("✅ 使用while True循環")
    
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
    
    # Check for if-elif-else statements
    if 'if' in code_lower and 'elif' in code_lower and 'else' in code_lower:
        score += 1
        explanation.append("✅ 使用if-elif-else條件判斷")
    
    # Check for validation logic (negative check, modulus check)
    if ('<' in code or '>=' in code) and ('%' in code or 'mod' in code_lower):
        score += 1
        explanation.append("✅ 檢查負數和5的倍數")
    
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
        run_result = run_student_code(student_code, test_case["input"], timeout_seconds=2.0)
        test_results.append(
            {
                "input": test_case["input"],
                "success": bool(run_result.get("runs")),
                "output": run_result.get("output", ""),
                "error": run_result.get("error", ""),
                "timed_out": bool(run_result.get("timed_out", False)),
                "expected": test_case,
            }
        )
    
    return test_results

def evaluate_shopping_program(filepath):
    """Evaluate student's shopping program according to rubrics (total 16 marks)"""
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
    
    # Rubric 2: 正確地初始化變量 (1分) - balance = 500
    code_lower = student_code.lower()
    has_balance_init = 'balance' in code_lower and '=' in code_lower
    
    if has_balance_init and '500' in student_code:
        total_marks += 1
        feedback.append("✅ 正確地初始化變量(balance = 500) (+1)")
    elif has_balance_init:
        total_marks += 0.5
        feedback.append("⚠️ 初始化balance但值可能不正確 (+0.5)")
    else:
        feedback.append("❌ 未正確初始化變量 (+0)")
    
    # Round up if we have 0.5
    if total_marks % 1 == 0.5:
        total_marks = int(total_marks) + 1
    else:
        total_marks = int(total_marks)
    
    # Rubric 3: 正確地定義無限循環 (1分) - while True:
    has_while_true = 'while true' in code_lower
    
    if has_while_true:
        total_marks += 1
        feedback.append("✅ 正確地定義無限循環(while True:) (+1)")
    else:
        feedback.append("❌ 未正確定義無限循環 (+0)")
    
    # Rubric 4: 正確地讀取用戶輸入 (3分) - variable naming, input(), int()
    has_input = 'input(' in code_lower
    has_int = 'int(' in code_lower
    input_count = student_code.count('input(')
    
    # Check for proper variable naming (price or similar)
    has_price_var = 'price' in code_lower
    
    if has_input and has_int and has_price_var and input_count >= 1:
        # Check if int() is used with input
        if 'int(input(' in code_lower:
            total_marks += 3
            feedback.append("✅ 正確地讀取用戶輸入(變量命名、input()、int()) (+3)")
        else:
            total_marks += 2
            feedback.append("⚠️ 使用input()和int()但可能未正確結合 (+2)")
    elif has_input and has_int:
        total_marks += 2
        feedback.append("⚠️ 使用input()和int()但變量命名可能不正確 (+2)")
    elif has_input or has_int:
        total_marks += 1
        feedback.append("⚠️ 部分使用input()或int() (+1)")
    else:
        feedback.append("❌ 未正確讀取用戶輸入 (+0)")
    
    # Rubric 5: 正確使用若/否則運算 (4分) - if price == 0, elif price < 0 or price % 5 != 0, elif price > balance, else
    has_if = 'if' in code_lower
    has_elif = 'elif' in code_lower
    has_else = 'else' in code_lower
    
    # Check for price == 0 condition (can be 'price == 0' or 'price==0')
    has_zero_check = ('price' in code_lower and '== 0' in code_lower) or ('price' in code_lower and '==0' in code_lower)
    
    # Check for price < 0 or price % 5 != 0 condition
    has_negative_check = ('price' in code_lower and '< 0' in code_lower) or ('price' in code_lower and '<0' in code_lower)
    has_modulus_check = 'price' in code_lower and '%' in student_code and '5' in code_lower and '!=' in code_lower
    has_or_operator = ' or ' in code_lower
    
    # Check for price > balance condition
    has_balance_check = 'price' in code_lower and 'balance' in code_lower and ('>' in student_code or '>=' in student_code)
    
    # Count elif statements (should have at least 2)
    elif_count = code_lower.count('elif')
    
    if has_if and has_elif and has_else and has_zero_check:
        if has_negative_check and has_modulus_check and has_balance_check and has_or_operator and elif_count >= 2:
            total_marks += 4
            feedback.append("✅ 正確使用if-elif-else條件判斷(price == 0, price < 0 or price % 5 != 0, price > balance, else) (+4)")
        elif (has_negative_check or has_modulus_check) and has_balance_check and elif_count >= 2:
            total_marks += 3
            feedback.append("⚠️ 部分使用條件判斷(缺少完整條件) (+3)")
        elif has_balance_check and elif_count >= 1:
            total_marks += 2
            feedback.append("⚠️ 部分使用條件判斷(缺少部分條件) (+2)")
        else:
            total_marks += 1
            feedback.append("⚠️ 使用if-elif-else但條件可能不完整 (+1)")
    elif has_if and has_elif and has_else:
        total_marks += 1
        feedback.append("⚠️ 使用if-elif-else但條件可能不正確 (+1)")
    else:
        feedback.append("❌ 未正確使用條件判斷 (+0)")
    
    # Rubric 6: 正確跳出無限循環 (1分) - break
    has_break = 'break' in code_lower
    
    if has_break and has_while_true:
        total_marks += 1
        feedback.append("✅ 正確跳出無限循環(使用break) (+1)")
    elif has_break:
        total_marks += 0.5
        feedback.append("⚠️ 使用break但可能未在while True中使用 (+0.5)")
    else:
        feedback.append("❌ 未正確跳出無限循環 (+0)")
    
    # Round up if we have 0.5
    if total_marks % 1 == 0.5:
        total_marks = int(total_marks) + 1
    else:
        total_marks = int(total_marks)
    
    # Rubric 7: 正確輸出 (2分) - print()
    if successful_runs > 0:
        sample_result = next((r for r in test_results if r["success"]), None)
        if sample_result and sample_result["output"].strip():
            output = sample_result["output"].lower()
            
            has_initial = 'initial balance' in output
            has_final = 'final balance' in output
            has_success = 'purchase successful' in output or 'new balance' in output
            has_invalid_msg = 'invalid price' in output
            has_insufficient_msg = 'not enough balance' in output or 'insufficient' in output
            
            if has_initial and has_final:
                total_marks += 2
                feedback.append("✅ 正確輸出(包含Initial balance和Final balance) (+2)")
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
    
    # Rubric 8: 執行沒有錯誤 (3分) - execution correctness
    if successful_runs > 0:
        accurate_matches = 0
        
        for i, result in enumerate(test_results):
            if result["success"]:
                student_output = result["output"].strip()
                inputs = result["input"]
                expected_final = result["expected"]["expected_final_balance"]
                
                # Check if purchase logic is correct
                if check_purchase_logic(student_output, inputs, expected_final):
                    accurate_matches += 1
        
        # Check accuracy: 3分 for all correct, 2分 for mostly correct, 1分 for partially correct
        if accurate_matches >= len(TEST_CASES) - 1:
            total_marks += 3
            feedback.append(f"✅ 能執行且輸出正確 ({accurate_matches}個準確結果) (+3)")
        elif accurate_matches >= len(TEST_CASES) * 0.7:
            total_marks += 2
            feedback.append(f"⚠️ 能執行部份輸出正確 ({accurate_matches}個準確結果) (+2)")
        elif accurate_matches >= len(TEST_CASES) * 0.4:
            total_marks += 1
            feedback.append(f"⚠️ 能執行但只有少部份輸出正確 ({accurate_matches}個準確結果) (+1)")
        else:
            feedback.append(f"❌ 執行錯誤或輸出不正確 ({accurate_matches}個準確結果) (+0)")
    else:
        feedback.append("❌ 程式無法執行 (+0)")
    
    # Generate overall feedback
    if total_marks >= 15:
        overall_feedback = f"✅ 優秀！總分 {total_marks}/16"
    elif total_marks >= 13:
        overall_feedback = f"✅ 良好！總分 {total_marks}/16"
    elif total_marks >= 10:
        overall_feedback = f"⚠️ 基本合格！總分 {total_marks}/16"
    elif total_marks >= 5:
        overall_feedback = f"❌ 需要改進！總分 {total_marks}/16"
    else:
        overall_feedback = f"❌ 不及格！總分 {total_marks}/16"
    
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

        # (16 marks) The python code implements shopping system correctly
        section_description = "Python程式碼實現購物系統"
        filepath = row["filepath"]
        section_mark, remarks = evaluate_shopping_program(filepath)

        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark, 16)

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

