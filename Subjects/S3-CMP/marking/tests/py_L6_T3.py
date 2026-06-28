import aia_util as aia_utils
import difflib
import re
from contextlib import redirect_stdout
from unittest.mock import patch, MagicMock
import io

# Test cases: We'll use a fixed secret number (73) by mocking randint
# Each test case provides guesses leading to correct answer
SECRET_NUMBERS = [50, 25, 75, 10, 90, 1, 100, 42, 73]

def extract_secret_number(code):
    """Extract secret number from code (either from randint or hardcoded)"""
    code_lower = code.lower()
    
    # Check for hardcoded secret number
    # Pattern: secret = number or secret=number
    patterns = [
        r'secret\s*=\s*(\d+)',
        r'secret\s*=\s*randint\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, code_lower)
        if matches:
            if len(matches[0]) == 1:
                # Hardcoded value
                return int(matches[0])
            elif len(matches[0]) == 2:
                # randint(1, 100) - we'll use a fixed value for testing
                return 50  # Default for testing
    
    # If we can't extract, assume it uses randint and we'll mock it
    if 'randint' in code_lower:
        return None  # Will be mocked
    else:
        # Try to find any number assignment to secret
        numbers = re.findall(r'secret\s*=\s*(\d+)', code)
        if numbers:
            return int(numbers[0])
    
    return None

def create_test_cases_for_secret(secret):
    """Create test cases for a given secret number"""
    return [
        {
            "input": [str(secret)],
            "expected": "Bingo!!!",
            "secret": secret
        },
        {
            "input": [str(secret + 10), str(secret)],
            "expected": "Too big!\nBingo!!!",
            "secret": secret
        },
        {
            "input": [str(secret - 10), str(secret)],
            "expected": "Too small!\nBingo!!!",
            "secret": secret
        },
        {
            "input": ["100", "1", str(secret)],
            "expected": "Too big!\nToo small!\nBingo!!!",
            "secret": secret
        },
        {
            "input": [str(secret + 5), str(secret - 5), str(secret)],
            "expected": "Too big!\nToo small!\nBingo!!!",
            "secret": secret
        }
    ]

# Default test cases using secret = 50 (when randint is mocked)
TEST_CASES = create_test_cases_for_secret(50)

def run_student_code(student_code, test_input, return_dict, secret_number=None):
    """Run student code with mocked input and optionally mocked randint"""
    buffer = io.StringIO()
    
    try:
        with redirect_stdout(buffer):
            # Mock randint to return a fixed secret if needed
            with patch('builtins.input', side_effect=test_input):
                if secret_number is not None and 'randint' in student_code.lower():
                    with patch('random.randint', return_value=secret_number):
                        exec(student_code, {})
                else:
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

def extract_feedback(output):
    """Extract feedback messages from output"""
    output_lower = output.lower()
    
    messages = []
    if 'bingo' in output_lower or 'bingo!!!' in output_lower:
        messages.append('bingo')
    if 'too big' in output_lower or 'too large' in output_lower:
        messages.append('too_big')
    if 'too small' in output_lower:
        messages.append('too_small')
    
    return messages

def calculate_guess_accuracy(student_output, guesses, secret_number):
    """Calculate if guess logic is correct for each guess"""
    output_lower = student_output.lower()
    lines = output_lower.split('\n')
    lines = [line.strip() for line in lines if line.strip()]
    
    # Get the sequence of feedback messages
    messages = extract_feedback(student_output)
    
    # Check each guess and corresponding feedback
    correct_feedbacks = 0
    guess_index = 0
    
    for i, line in enumerate(lines):
        if guess_index >= len(guesses):
            break
            
        guess = int(guesses[guess_index])
        
        # Determine expected feedback
        if guess == secret_number:
            expected = 'bingo'
        elif guess > secret_number:
            expected = 'too_big'
        else:
            expected = 'too_small'
        
        # Check if the feedback matches
        if expected == 'bingo' and 'bingo' in line:
            correct_feedbacks += 1
            guess_index += 1
            break  # Game ends with bingo
        elif expected == 'too_big' and ('too big' in line or 'too large' in line):
            correct_feedbacks += 1
            guess_index += 1
        elif expected == 'too_small' and 'too small' in line:
            correct_feedbacks += 1
            guess_index += 1
    
    # The logic is correct if we get feedbacks for all guesses or until bingo
    return correct_feedbacks >= min(len(guesses), len(lines))

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
    
    # Check for while True loop
    if 'while true' in code_lower:
        score += 1
        explanation.append("✅ 使用while True循環")
    
    # Check for break statement
    if 'break' in code_lower:
        score += 1
        explanation.append("✅ 使用break語句")
    
    # Check for if-elif-else
    if 'if' in code_lower and 'elif' in code_lower and 'else' in code_lower:
        score += 1
        explanation.append("✅ 使用if-elif-else條件判斷")
    
    # Check for comparison operators
    if '==' in code or '>' in code or '<' in code:
        score += 1
        explanation.append("✅ 使用比較運算符")
    
    # Check for secret/random
    if 'secret' in code_lower or 'randint' in code_lower:
        score += 1
        explanation.append("✅ 包含秘密數字邏輯")
    
    return score, explanation

def run_multiple_tests(student_code, secret_number=50):
    """Run student code with multiple test cases"""
    test_results = []
    
    # Create test cases for the specific secret number
    test_cases = create_test_cases_for_secret(secret_number)
    
    for test_case in test_cases:
        buffer = io.StringIO()
        
        try:
            with redirect_stdout(buffer):
                with patch('builtins.input', side_effect=test_case["input"]):
                    if 'randint' in student_code.lower():
                        with patch('random.randint', return_value=secret_number):
                            exec(student_code, {})
                    else:
                        exec(student_code, {})
            test_results.append({
                "input": test_case["input"],
                "success": True,
                "output": buffer.getvalue(),
                "error": "",
                "secret": secret_number
            })
        except Exception as e:
            test_results.append({
                "input": test_case["input"],
                "success": False,
                "output": buffer.getvalue(),
                "error": str(e),
                "secret": secret_number
            })
    
    return test_results

def evaluate_guessing_program(filepath):
    """Evaluate student's number guessing program with specific criteria (2 marks each)"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            student_code = f.read()
    except:
        return 0, "❌ 無法讀取程式碼"

    total_marks = 0
    feedback = []
    
    # Extract secret number from code
    secret_number = extract_secret_number(student_code)
    if secret_number is None:
        # Use default secret for testing (will be mocked if randint is used)
        secret_number = 50
    
    # Run multiple test cases
    test_results = run_multiple_tests(student_code, secret_number)
    
    # Count successful runs
    successful_runs = sum(1 for result in test_results if result["success"])
    
    # 1. Check for while True loop with break (2 marks)
    code_lower = student_code.lower()
    has_while_true = 'while true' in code_lower
    has_break = 'break' in code_lower
    
    if has_while_true and has_break:
        total_marks += 2
        feedback.append("✅ 正確使用while True循環和break語句 (+2)")
    elif has_while_true:
        total_marks += 1
        feedback.append("⚠️ 使用while True但缺少break (+1)")
    elif 'while' in code_lower:
        total_marks += 1
        feedback.append("⚠️ 使用while循環但非True或缺少break (+1)")
    else:
        feedback.append("❌ 未使用while True循環和break (+0)")
    
    # 2. Check for int() usage appropriately (2 marks)
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
    
    # 3. Check for appropriate output (2 marks)
    if successful_runs > 0:
        # Check if output has guessing-related content
        sample_result = next((r for r in test_results if r["success"]), None)
        if sample_result and sample_result["output"].strip():
            output = sample_result["output"].lower()
            if 'bingo' in output or 'too big' in output or 'too small' in output:
                total_marks += 2
                feedback.append("✅ 輸出格式正確(包含猜測反饋訊息) (+2)")
            else:
                total_marks += 1
                feedback.append("⚠️ 輸出格式部分正確 (+1)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    else:
        # Check static analysis for print statements
        if 'print(' in code_lower and ('bingo' in code_lower or 'too' in code_lower):
            total_marks += 1
            feedback.append("⚠️ 程式碼有輸出邏輯但執行失敗 (+1)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    
    # 4. Check for if-elif-else conditional statements with comparison operators (2 marks)
    has_if = 'if' in code_lower
    has_elif = 'elif' in code_lower
    has_else = 'else' in code_lower
    has_comparison = '==' in student_code and ('>' in student_code or '<' in student_code)
    
    if has_if and has_elif and has_else and has_comparison:
        total_marks += 2
        feedback.append("✅ 正確使用if-elif-else條件判斷和比較運算符(+2)")
    elif has_if and has_elif and has_comparison:
        total_marks += 1
        feedback.append("⚠️ 部分使用條件判斷(缺少else) (+1)")
    elif has_if and has_comparison:
        total_marks += 1
        feedback.append("⚠️ 部分使用條件判斷(缺少elif/else) (+1)")
    else:
        feedback.append("❌ 未使用必要的條件判斷 (+0)")
    
    # 5. Check for results closely matching model answers (2 marks)
    if successful_runs > 0:
        accurate_guess_matches = 0
        
        for i, result in enumerate(test_results):
            if result["success"]:
                student_output = result["output"].strip()
                guesses = test_results[i]["input"]
                secret = result.get("secret", secret_number)
                
                # Check if guess logic is correct
                if calculate_guess_accuracy(student_output, guesses, secret):
                    accurate_guess_matches += 1
        
        # Check accuracy based on correct logic
        if accurate_guess_matches >= len(test_results) - 1:
            total_marks += 2
            feedback.append(f"✅ 猜測邏輯完全正確 ({accurate_guess_matches}個準確結果) (+2)")
        elif accurate_guess_matches >= len(test_results) - 2:
            total_marks += 1
            feedback.append(f"⚠️ 猜測邏輯部分正確 ({accurate_guess_matches}個準確結果) (+1)")
        else:
            feedback.append(f"❌ 猜測邏輯不正確 ({accurate_guess_matches}個準確結果) (+0)")
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

        # (10 marks) The python code implements number guessing game correctly
        section_description = "Python程式碼實現數字猜測遊戲"
        filepath = row["filepath"]
        section_mark, remarks = evaluate_guessing_program(filepath)

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

