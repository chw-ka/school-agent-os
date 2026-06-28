import aia_util as aia_utils
import difflib
import multiprocessing
import re
from contextlib import redirect_stdout
from unittest.mock import patch, MagicMock
import io

# Test cases with different n inputs and expected outputs
TEST_CASES = [
    {
        "input": ["1"],
        "expected": "Sum = 1"
    },
    {
        "input": ["5"],
        "expected": "Sum = 15"
    },
    {
        "input": ["10"],
        "expected": "Sum = 55"
    },
    {
        "input": ["0"],
        "expected": "Sum = 0"
    },
    {
        "input": ["15"],
        "expected": "Sum = 120"
    }
]

EXECUTION_TIMEOUT_SECONDS = 3
TIMEOUT_ERROR_MESSAGE = "Timeout reached while executing student code (possible infinite loop)"

def _student_code_worker(result_queue, student_code, test_input):
    buffer = io.StringIO()
    try:
        with redirect_stdout(buffer):
            with patch('builtins.input', side_effect=test_input):
                exec(student_code, {})
        result_queue.put({
            "runs": True,
            "output": buffer.getvalue(),
            "error": ""
        })
    except Exception as e:
        result_queue.put({
            "runs": False,
            "output": buffer.getvalue(),
            "error": str(e)
        })

def execute_student_code_with_timeout(student_code, test_input, timeout=EXECUTION_TIMEOUT_SECONDS):
    ctx = multiprocessing.get_context("spawn")
    result_queue = ctx.Queue()
    process = ctx.Process(target=_student_code_worker, args=(result_queue, student_code, test_input))
    process.start()
    process.join(timeout)

    if process.is_alive():
        process.terminate()
        process.join()
        result = {
            "runs": False,
            "output": "",
            "error": TIMEOUT_ERROR_MESSAGE
        }
    else:
        if not result_queue.empty():
            result = result_queue.get()
        else:
            result = {
                "runs": False,
                "output": "",
                "error": "No output captured from student code execution"
            }

    result_queue.close()
    result_queue.join_thread()

    return result

def run_student_code(student_code, test_input, return_dict):
    """Run student code with mocked input and enforce timeout via multiprocessing"""
    result = execute_student_code_with_timeout(student_code, test_input)
    
    return_dict["runs"] = result.get("runs", False)
    return_dict["output"] = result.get("output", "")
    if not result.get("runs", False):
        return_dict["error"] = result.get("error", "")

def calculate_similarity(output1, output2):
    """Calculate similarity between two outputs"""
    return difflib.SequenceMatcher(None, output1.strip(), output2.strip()).ratio()

def extract_sum(output):
    """Extract sum value from output"""
    output_lower = output.lower()
    
    # Try to find the sum number in the output
    # Look for patterns like "Sum = 123" or "Sum=123" or similar
    
    # Pattern to match "Sum" followed by equals and a number
    patterns = [
        r'sum\s*=\s*(\d+)',
        r'sum\s*:\s*(\d+)',
        r'(\d+)',  # Just extract any number if sum is found
    ]
    
    if 'sum' in output_lower:
        for pattern in patterns:
            match = re.search(pattern, output_lower)
            if match:
                try:
                    return int(match.group(1))
                except:
                    pass
        # If pattern matching fails, try to extract any number
        numbers = re.findall(r'\d+', output)
        if numbers:
            try:
                return int(numbers[-1])  # Take the last number as it's likely the sum
            except:
                pass
    
    return None

def calculate_sum_accuracy(student_output, n):
    """Calculate if sum calculation is correct"""
    student_sum = extract_sum(student_output)
    
    # Calculate expected sum: 1 + 2 + ... + n = n * (n + 1) / 2
    expected_sum = n * (n + 1) // 2 if n > 0 else 0
    
    return student_sum == expected_sum

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
    
    # Check for comparison operator in while condition
    if ('while' in code_lower) and ('<=' in code or '<' in code or '>=' in code or '>' in code):
        score += 1
        explanation.append("✅ 在while條件中使用比較運算符")
    
    # Check for accumulator pattern
    if ('total' in code_lower or 'sum' in code_lower) and '+=' in code:
        score += 1
        explanation.append("✅ 使用累加器模式")
    elif 'total' in code_lower or 'sum' in code_lower:
        score += 1
        explanation.append("✅ 使用累加變數")
    
    # Check for increment pattern
    if 'i += 1' in code or 'i = i + 1' in code or 'i=i+1' in code_lower:
        score += 1
        explanation.append("✅ 使用計數器遞增")
    
    return score, explanation

def run_multiple_tests(student_code):
    """Run student code with multiple test cases using isolated processes"""
    test_results = []
    
    for test_case in TEST_CASES:
        result = execute_student_code_with_timeout(student_code, test_case["input"])
        
        test_results.append({
            "input": test_case["input"],
            "success": result.get("runs", False),
            "output": result.get("output", ""),
            "error": result.get("error", "")
        })

        if not result.get("runs", False):
            break
    
    return test_results

def evaluate_sum_program(filepath):
    """Evaluate student's sum calculation program with specific criteria (2 marks each)"""
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
        # Check if output has sum-related content
        sample_result = next((r for r in test_results if r["success"]), None)
        if sample_result and sample_result["output"].strip():
            output = sample_result["output"].lower()
            if 'sum' in output:
                total_marks += 2
                feedback.append("✅ 輸出格式正確(包含Sum訊息) (+2)")
            else:
                total_marks += 1
                feedback.append("⚠️ 輸出格式部分正確 (+1)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    else:
        # Check static analysis for print statements
        if 'print(' in code_lower and 'sum' in code_lower:
            total_marks += 1
            feedback.append("⚠️ 程式碼有輸出邏輯但執行失敗 (+1)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    
    # 3. Check for while loop with comparison operator (2 marks)
    has_while = 'while' in code_lower
    has_comparison = '<=' in student_code or '<' in student_code or '>=' in student_code or '>' in student_code
    
    if has_while and has_comparison:
        # Check if while loop has proper condition
        if 'while' in code_lower and ('<=' in student_code or '<' in student_code):
            total_marks += 2
            feedback.append("✅ 正確使用while循環和比較運算符 (+2)")
        else:
            total_marks += 1
            feedback.append("⚠️ 部分使用while循環 (+1)")
    elif has_while:
        total_marks += 1
        feedback.append("⚠️ 使用while循環但缺少比較運算符 (+1)")
    else:
        feedback.append("❌ 未使用while循環 (+0)")
    
    # 4. Check for accumulator and increment patterns (2 marks)
    has_accumulator = ('total' in code_lower or 'sum' in code_lower) and ('+' in student_code or '+=' in student_code)
    has_increment = ('i += 1' in student_code or 'i = i + 1' in student_code or 
                     'i=i+1' in code_lower or 'i = i+1' in code_lower)
    
    # Also check for any variable increment pattern
    if not has_increment:
        # Check for patterns like variable = variable + 1
        increment_patterns = [' += 1', ' = ', '+ 1', '= ', '+1']
        for pattern in increment_patterns:
            if pattern in student_code and ('i' in code_lower or 'counter' in code_lower):
                has_increment = True
                break
    
    if has_accumulator and has_increment:
        total_marks += 2
        feedback.append("✅ 正確使用累加器和計數器遞增 (+2)")
    elif has_accumulator or has_increment:
        total_marks += 1
        feedback.append("⚠️ 部分使用累加器或計數器遞增 (+1)")
    else:
        feedback.append("❌ 未使用累加器和計數器遞增 (+0)")
    
    # 5. Check for results closely matching model answers (2 marks)
    if successful_runs > 0:
        accurate_sum_matches = 0
        
        for i, result in enumerate(test_results):
            if result["success"]:
                student_output = result["output"].strip()
                n = int(test_results[i]["input"][0])
                
                # Check if sum calculation is correct
                if calculate_sum_accuracy(student_output, n):
                    accurate_sum_matches += 1
        
        # Check accuracy based on correct logic
        if accurate_sum_matches >= len(TEST_CASES) - 1:
            total_marks += 2
            feedback.append(f"✅ 求和計算完全正確 ({accurate_sum_matches}個準確結果) (+2)")
        elif accurate_sum_matches >= len(TEST_CASES) - 2:
            total_marks += 1
            feedback.append(f"⚠️ 求和計算部分正確 ({accurate_sum_matches}個準確結果) (+1)")
        else:
            feedback.append(f"❌ 求和計算不正確 ({accurate_sum_matches}個準確結果) (+0)")
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

        # (10 marks) The python code calculates sum correctly
        section_description = "Python程式碼計算求和"
        filepath = row["filepath"]
        section_mark, remarks = evaluate_sum_program(filepath)

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

