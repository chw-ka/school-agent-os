import aia_util as aia_utils
import difflib
import re
from contextlib import redirect_stdout
from unittest.mock import patch, MagicMock
import io

# Test cases with different number sequences ending with -1
TEST_CASES = [
    {
        "input": ["-1"],
        "expected": "Total = 0"
    },
    {
        "input": ["5", "-1"],
        "expected": "Total = 5"
    },
    {
        "input": ["10", "-1"],
        "expected": "Total = 10"
    },
    {
        "input": ["1", "2", "3", "-1"],
        "expected": "Total = 6"
    },
    {
        "input": ["5", "10", "15", "-1"],
        "expected": "Total = 30"
    },
    {
        "input": ["0", "-1"],
        "expected": "Total = 0"
    },
    {
        "input": ["-2", "-1"],
        "expected": "Total = -2"
    },
    {
        "input": ["10", "-5", "-1"],
        "expected": "Total = 5"
    },
    {
        "input": ["1", "2", "3", "4", "5", "-1"],
        "expected": "Total = 15"
    },
    {
        "input": ["100", "200", "300", "-1"],
        "expected": "Total = 600"
    },
    {
        "input": ["7", "8", "9", "10", "-1"],
        "expected": "Total = 34"
    },
    {
        "input": ["20", "30", "50", "-1"],
        "expected": "Total = 100"
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

def extract_total(output):
    """Extract total value from output"""
    output_lower = output.lower()
    
    # Try to find the total number in the output
    # Look for patterns like "Total = 123" or "Total=123" or similar
    
    # Pattern to match "Total" followed by equals and a number (including negative)
    patterns = [
        r'total\s*=\s*(-?\d+)',
        r'total\s*:\s*(-?\d+)',
        r'total\s*(-?\d+)',
    ]
    
    if 'total' in output_lower:
        for pattern in patterns:
            match = re.search(pattern, output_lower)
            if match:
                try:
                    return int(match.group(1))
                except:
                    pass
        # If pattern matching fails, try to extract any number (including negative)
        numbers = re.findall(r'-?\d+', output)
        if numbers:
            try:
                # Take the last number as it's likely the total
                return int(numbers[-1])
            except:
                pass
    
    return None

def calculate_total_accuracy(student_output, inputs):
    """Calculate if total calculation is correct"""
    student_total = extract_total(student_output)
    
    # Calculate expected total: sum all numbers except -1
    expected_total = sum(int(x) for x in inputs if x != '-1')
    
    return student_total == expected_total

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
    
    # Check for while True loop
    if 'while true' in code_lower:
        score += 1
        explanation.append("✅ 使用while True循環")
    
    # Check for break statement
    if 'break' in code_lower:
        score += 1
        explanation.append("✅ 使用break語句")
    
    # Check for accumulator pattern
    if ('total' in code_lower) and ('+' in code or '+=' in code):
        score += 1
        explanation.append("✅ 使用累加器模式")
    
    # Check for comparison with -1
    if '-1' in code and ('==' in code or '!=' in code):
        score += 1
        explanation.append("✅ 檢查哨兵值(-1)")
    
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

def evaluate_total_program(filepath):
    """Evaluate student's total accumulator program with specific criteria (2 marks each)"""
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
        # Check if output has total-related content
        sample_result = next((r for r in test_results if r["success"]), None)
        if sample_result and sample_result["output"].strip():
            output = sample_result["output"].lower()
            if 'total' in output:
                total_marks += 2
                feedback.append("✅ 輸出格式正確(包含Total訊息) (+2)")
            else:
                total_marks += 1
                feedback.append("⚠️ 輸出格式部分正確 (+1)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    else:
        # Check static analysis for print statements
        if 'print(' in code_lower and 'total' in code_lower:
            total_marks += 1
            feedback.append("⚠️ 程式碼有輸出邏輯但執行失敗 (+1)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    
    # 4. Check for accumulator pattern and sentinel value check (2 marks)
    has_accumulator = ('total' in code_lower) and ('+' in student_code or '+=' in student_code)
    has_sentinel_check = '-1' in student_code and ('==' in student_code or '!=' in student_code)
    
    if has_accumulator and has_sentinel_check:
        total_marks += 2
        feedback.append("✅ 正確使用累加器模式和哨兵值檢查(-1) (+2)")
    elif has_accumulator or has_sentinel_check:
        total_marks += 1
        feedback.append("⚠️ 部分使用累加器或哨兵值檢查 (+1)")
    else:
        feedback.append("❌ 未使用累加器模式和哨兵值檢查 (+0)")
    
    # 5. Check for results closely matching model answers (2 marks)
    if successful_runs > 0:
        accurate_total_matches = 0
        
        for i, result in enumerate(test_results):
            if result["success"]:
                student_output = result["output"].strip()
                inputs = test_results[i]["input"]
                
                # Check if total calculation is correct
                if calculate_total_accuracy(student_output, inputs):
                    accurate_total_matches += 1
        
        # Check accuracy based on correct logic
        if accurate_total_matches >= len(TEST_CASES) - 1:
            total_marks += 2
            feedback.append(f"✅ 總和計算完全正確 ({accurate_total_matches}個準確結果) (+2)")
        elif accurate_total_matches >= len(TEST_CASES) - 2:
            total_marks += 1
            feedback.append(f"⚠️ 總和計算部分正確 ({accurate_total_matches}個準確結果) (+1)")
        else:
            feedback.append(f"❌ 總和計算不正確 ({accurate_total_matches}個準確結果) (+0)")
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

        # (10 marks) The python code calculates total correctly
        section_description = "Python程式碼計算累加總和"
        filepath = row["filepath"]
        section_mark, remarks = evaluate_total_program(filepath)

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

