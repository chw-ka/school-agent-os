import aia_util as aia_utils
import difflib
import signal
from contextlib import redirect_stdout, contextmanager
from unittest.mock import patch
import io

# Test cases with different age inputs, student card responses, and expected outputs
# Each test case ends with 'q' to exit the while loop
TEST_CASES = [
    {
        "input": ["3", "q"],
        "expected": "Free"
    },
    {
        "input": ["2", "q"],
        "expected": "Free"
    },
    {
        "input": ["65", "q"],
        "expected": "Free"
    },
    {
        "input": ["70", "q"],
        "expected": "Free"
    },
    {
        "input": ["100", "q"],
        "expected": "Free"
    },
    {
        "input": ["25", "y", "q"],
        "expected": "Half Fare"
    },
    {
        "input": ["25", "n", "q"],
        "expected": "Full Fare"
    },
    {
        "input": ["20", "y", "q"],
        "expected": "Half Fare"
    },
    {
        "input": ["20", "n", "q"],
        "expected": "Full Fare"
    },
    {
        "input": ["15", "y", "q"],
        "expected": "Half Fare"
    },
    {
        "input": ["15", "n", "q"],
        "expected": "Full Fare"
    },
    {
        "input": ["4", "y", "q"],
        "expected": "Half Fare"
    },
    {
        "input": ["26", "q"],
        "expected": "Full Fare"
    },
    {
        "input": ["30", "q"],
        "expected": "Full Fare"
    },
    {
        "input": ["50", "q"],
        "expected": "Full Fare"
    },
    {
        "input": ["64", "q"],
        "expected": "Full Fare"
    }
]

EXECUTION_TIMEOUT_SECONDS = 3
TIMEOUT_ERROR_MESSAGE = "Timeout reached while executing student code (possible infinite loop)"

class ExecutionTimeoutError(Exception):
    """Raised when student code execution exceeds allowed time."""

def _timeout_handler(signum, frame):
    raise ExecutionTimeoutError

@contextmanager
def execution_timeout(seconds):
    previous_handler = signal.getsignal(signal.SIGALRM)
    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous_handler)

def run_student_code(student_code, test_input, return_dict):
    """Run student code with mocked input and enforce timeout"""
    buffer = io.StringIO()
    
    try:
        with execution_timeout(EXECUTION_TIMEOUT_SECONDS):
            with redirect_stdout(buffer):
                with patch('builtins.input', side_effect=test_input):
                    exec(student_code, {})
        return_dict["runs"] = True
        return_dict["output"] = buffer.getvalue()
    except ExecutionTimeoutError:
        return_dict["runs"] = False
        return_dict["output"] = buffer.getvalue()
        return_dict["error"] = TIMEOUT_ERROR_MESSAGE
    except Exception as e:
        return_dict["runs"] = False
        return_dict["output"] = buffer.getvalue()
        return_dict["error"] = str(e)

def calculate_similarity(output1, output2):
    """Calculate similarity between two outputs"""
    return difflib.SequenceMatcher(None, output1.strip(), output2.strip()).ratio()

def extract_fare(output):
    """Extract fare information from output"""
    output_lower = output.lower()
    
    # Check for Free
    if 'free' in output_lower:
        return 'free'
    # Check for Half Fare
    elif 'half fare' in output_lower or ('half' in output_lower and 'fare' in output_lower):
        return 'half_fare'
    # Check for Full Fare
    elif 'full fare' in output_lower or ('full' in output_lower and 'fare' in output_lower):
        return 'full_fare'
    
    return None

def calculate_fare_accuracy(student_output, age, student_card=None):
    """Calculate if fare logic is correct"""
    student_result = extract_fare(student_output)
    
    # Determine expected result based on age and student card
    age_int = int(age)
    
    if age_int < 4 or age_int >= 65:
        expected_result = 'free'
    elif age_int <= 25:
        if student_card and student_card.lower() == 'y':
            expected_result = 'half_fare'
        else:
            expected_result = 'full_fare'
    else:
        expected_result = 'full_fare'
    
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
    
    # Check for while loop
    if 'while' in code_lower:
        score += 1
        explanation.append("✅ 使用while循環")
    
    # Check for break statement
    if 'break' in code_lower:
        score += 1
        explanation.append("✅ 使用break語句")
    
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
    
    return score, explanation

def run_multiple_tests(student_code):
    """Run student code with multiple test cases using timeout enforcement"""
    test_results = []
    
    for test_case in TEST_CASES:
        buffer = io.StringIO()
        try:
            with execution_timeout(EXECUTION_TIMEOUT_SECONDS):
                with redirect_stdout(buffer):
                    with patch('builtins.input', side_effect=test_case["input"]):
                        exec(student_code, {})
            test_results.append({
                "input": test_case["input"],
                "success": True,
                "output": buffer.getvalue(),
                "error": ""
            })
        except ExecutionTimeoutError:
            test_results.append({
                "input": test_case["input"],
                "success": False,
                "output": buffer.getvalue(),
                "error": TIMEOUT_ERROR_MESSAGE
            })
            break
        except Exception as e:
            test_results.append({
                "input": test_case["input"],
                "success": False,
                "output": buffer.getvalue(),
                "error": str(e)
            })
    
    return test_results

def evaluate_fare_program(filepath):
    """Evaluate student's fare calculation program with specific criteria (2 marks each)"""
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
    
    # 1. Check for while loop with break (2 marks)
    code_lower = student_code.lower()
    has_while = 'while' in code_lower
    has_break = 'break' in code_lower
    
    if has_while and has_break:
        # Check if while True is used
        if 'while true' in code_lower or 'while( true' in code_lower:
            total_marks += 2
            feedback.append("✅ 正確使用while True循環和break語句 (+2)")
        else:
            total_marks += 1
            feedback.append("⚠️ 部分使用while循環和break (+1)")
    elif has_while:
        total_marks += 1
        feedback.append("⚠️ 使用while循環但缺少break (+1)")
    else:
        feedback.append("❌ 未使用while循環和break (+0)")
    
    # 2. Check for int() usage appropriately (2 marks)
    if 'int(' in code_lower:
        # Check if int() is used with input or variable for age
        if 'int(input(' in code_lower or ('int(' in code_lower and ('age' in code_lower)):
            total_marks += 2
            feedback.append("✅ 正確使用int()函數轉換年齡 (+2)")
        else:
            total_marks += 1
            feedback.append("⚠️ 部分使用int()函數 (+1)")
    else:
        feedback.append("❌ 未使用int()函數 (+0)")
    
    # 3. Check for appropriate output (2 marks)
    if successful_runs > 0:
        # Check if output has fare-related content
        sample_result = next((r for r in test_results if r["success"]), None)
        if sample_result and sample_result["output"].strip():
            output = sample_result["output"].lower()
            if 'free' in output or 'fare' in output or ('half' in output and 'full' in output):
                total_marks += 2
                feedback.append("✅ 輸出格式正確(包含車費訊息) (+2)")
            else:
                total_marks += 1
                feedback.append("⚠️ 輸出格式部分正確 (+1)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    else:
        # Check static analysis for print statements
        if 'print(' in code_lower and ('free' in code_lower or 'fare' in code_lower):
            total_marks += 1
            feedback.append("⚠️ 程式碼有輸出邏輯但執行失敗 (+1)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    
    # 4. Check for if-elif-else conditional statements with comparison operators and nested logic (2 marks)
    has_if = 'if' in code_lower
    has_elif = 'elif' in code_lower
    has_else = 'else' in code_lower
    has_comparison = any(op in student_code for op in ['<', '>=', '<=', '==', '!='])
    has_or = ' or ' in code_lower
    
    # Check for nested if (student card check)
    if_count = code_lower.count(' if ')
    has_nested = if_count >= 2
    has_student_card_input = 'student' in code_lower and 'card' in code_lower
    
    if has_if and has_elif and has_else and has_comparison:
        if has_or and has_nested and has_student_card_input:
            total_marks += 2
            feedback.append("✅ 正確使用if-elif-else條件判斷、比較運算符、OR運算符和嵌套條件 (+2)")
        elif has_or or (has_nested and has_student_card_input):
            total_marks += 1
            feedback.append("⚠️ 部分使用條件判斷(缺少OR運算符或嵌套條件) (+1)")
        else:
            total_marks += 1
            feedback.append("⚠️ 部分使用條件判斷(缺少進階功能) (+1)")
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
        accurate_fare_matches = 0
        
        for i, result in enumerate(test_results):
            if result["success"]:
                student_output = result["output"].strip()
                inputs = test_results[i]["input"]
                age = inputs[0]
                
                # Extract student card response if present
                student_card = None
                if len(inputs) > 2:  # More than just age and 'q'
                    # Find student card response (should be 'y' or 'n')
                    for inp in inputs[1:-1]:  # Skip first (age) and last ('q')
                        if inp.lower() in ['y', 'n', 'yes', 'no']:
                            student_card = inp
                            break
                
                # Check if fare logic is correct
                if calculate_fare_accuracy(student_output, age, student_card):
                    accurate_fare_matches += 1
        
        # Check accuracy based on correct logic
        if accurate_fare_matches >= len(TEST_CASES) - 1:
            total_marks += 2
            feedback.append(f"✅ 車費判斷完全正確 ({accurate_fare_matches}個準確結果) (+2)")
        elif accurate_fare_matches >= len(TEST_CASES) - 2:
            total_marks += 1
            feedback.append(f"⚠️ 車費判斷部分正確 ({accurate_fare_matches}個準確結果) (+1)")
        else:
            feedback.append(f"❌ 車費判斷不正確 ({accurate_fare_matches}個準確結果) (+0)")
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

        # (10 marks) The python code determines fare calculation correctly
        section_description = "Python程式碼判斷車費"
        filepath = row["filepath"]
        section_mark, remarks = evaluate_fare_program(filepath)

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

