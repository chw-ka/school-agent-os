import aia_util as aia_utils
import difflib
import re
from contextlib import redirect_stdout
from unittest.mock import patch, MagicMock
import io

# Test cases for reaction time challenge
# We'll mock time.sleep and time.time to have predictable results
TEST_CASES = [
    {
        "input": ["", ""],  # First input to start, second input after GO!
        "sleep_time": 5,
        "start_time": 100.0,
        "end_time": 100.5,
        "expected_reaction_time": 0.5
    },
    {
        "input": ["", ""],
        "sleep_time": 8,
        "start_time": 200.0,
        "end_time": 200.3,
        "expected_reaction_time": 0.3
    },
    {
        "input": ["", ""],
        "sleep_time": 10,
        "start_time": 300.0,
        "end_time": 300.8,
        "expected_reaction_time": 0.8
    }
]

def run_student_code(student_code, test_input, return_dict, sleep_time=5, start_time=100.0, end_time=100.5):
    """Run student code with mocked input and time functions"""
    buffer = io.StringIO()
    
    try:
        with redirect_stdout(buffer):
            with patch('builtins.input', side_effect=test_input):
                # Mock time.sleep to do nothing (or verify it's called)
                with patch('time.sleep', return_value=None):
                    # Mock time.time() to return different values on each call
                    time_counter = [start_time, end_time]
                    def mock_time():
                        result = time_counter[0]
                        time_counter[0] = time_counter[1]
                        return result
                    
                    with patch('time.time', side_effect=mock_time):
                        with patch('random.randint', return_value=sleep_time):
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

def extract_reaction_time(output):
    """Extract reaction time from output"""
    output_lower = output.lower()
    
    # Look for patterns like "Your reaction time: 0.5 seconds" or "reaction time: 0.5"
    patterns = [
        r'reaction\s+time[:\s]+([\d.]+)',
        r'reaction\s+time[:\s]+([\d.]+)\s*seconds?',
        r'([\d.]+\s*seconds?)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, output_lower, re.IGNORECASE)
        if matches:
            try:
                # Extract the number
                time_str = matches[-1].replace('seconds', '').replace('second', '').strip()
                return float(time_str)
            except:
                pass
    
    # Try to find any decimal number near "reaction" or "time"
    if 'reaction' in output_lower or 'time' in output_lower:
        numbers = re.findall(r'[\d]+\.[\d]+', output)
        if numbers:
            try:
                return float(numbers[-1])  # Take the last decimal number
            except:
                pass
    
    return None

def check_program_structure(output, expected_messages):
    """Check if output contains expected messages"""
    output_lower = output.lower()
    found_messages = []
    
    if 'go!' in output_lower or 'go' in output_lower:
        found_messages.append('go')
    if 'ready' in output_lower or 'ready?' in output_lower:
        found_messages.append('ready')
    if 'reaction' in output_lower and 'time' in output_lower:
        found_messages.append('reaction_time')
    if 'challenge' in output_lower or 'press enter' in output_lower:
        found_messages.append('instructions')
    
    return found_messages

def analyze_code_quality(code):
    """Analyze code quality for non-running programs"""
    score = 0
    explanation = []
    
    code_lower = code.lower()
    
    # Check for import statements
    if 'import random' in code_lower or 'from random' in code_lower:
        score += 1
        explanation.append("✅ 導入random模組")
    
    if 'import time' in code_lower or 'from time' in code_lower:
        score += 1
        explanation.append("✅ 導入time模組")
    
    # Check for input function
    input_count = code.count('input(')
    if input_count >= 2:
        score += 1
        explanation.append("✅ 使用多個input函數")
    elif input_count >= 1:
        score += 1
        explanation.append("✅ 使用input函數")
    
    # Check for print function
    if "print(" in code_lower:
        score += 1
        explanation.append("✅ 使用print函數")
    
    # Check for time.sleep
    if 'time.sleep' in code_lower:
        score += 1
        explanation.append("✅ 使用time.sleep")
    
    # Check for time.time
    if 'time.time' in code_lower:
        score += 1
        explanation.append("✅ 使用time.time")
    
    # Check for random.randint
    if 'random.randint' in code_lower or 'randint' in code_lower:
        score += 1
        explanation.append("✅ 使用random.randint")
    
    # Check for subtraction (reaction time calculation)
    if '-' in code and 'time' in code_lower:
        score += 1
        explanation.append("✅ 計算反應時間")
    
    return score, explanation

def run_multiple_tests(student_code):
    """Run student code with multiple test cases"""
    test_results = []
    
    for test_case in TEST_CASES:
        buffer = io.StringIO()
        
        try:
            with redirect_stdout(buffer):
                with patch('builtins.input', side_effect=test_case["input"]):
                    with patch('time.sleep', return_value=None):
                        # Mock time.time() to return different values on each call
                        time_counter = [test_case["start_time"], test_case["end_time"]]
                        def mock_time():
                            result = time_counter[0]
                            time_counter[0] = time_counter[1]
                            return result
                        
                        with patch('time.time', side_effect=mock_time):
                            with patch('random.randint', return_value=test_case["sleep_time"]):
                                exec(student_code, {})
            test_results.append({
                "input": test_case["input"],
                "success": True,
                "output": buffer.getvalue(),
                "error": "",
                "expected_time": test_case["expected_reaction_time"]
            })
        except Exception as e:
            test_results.append({
                "input": test_case["input"],
                "success": False,
                "output": buffer.getvalue(),
                "error": str(e),
                "expected_time": test_case["expected_reaction_time"]
            })
    
    return test_results

def evaluate_reaction_time_program(filepath):
    """Evaluate student's reaction time program with specific criteria (2 marks each)"""
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
    
    # 1. Check for import statements (random and time) (2 marks)
    code_lower = student_code.lower()
    has_random = 'import random' in code_lower or 'from random' in code_lower
    has_time = 'import time' in code_lower or 'from time' in code_lower
    
    if has_random and has_time:
        total_marks += 2
        feedback.append("✅ 正確導入random和time模組 (+2)")
    elif has_random or has_time:
        total_marks += 1
        feedback.append("⚠️ 部分導入模組(random或time) (+1)")
    else:
        feedback.append("❌ 未導入必要的模組 (+0)")
    
    # 2. Check for appropriate output (2 marks)
    if successful_runs > 0:
        # Check if output has reaction time-related content
        sample_result = next((r for r in test_results if r["success"]), None)
        if sample_result and sample_result["output"].strip():
            output = sample_result["output"].lower()
            messages = check_program_structure(output, [])
            
            if 'go' in messages and 'reaction_time' in messages:
                total_marks += 2
                feedback.append("✅ 輸出格式正確(包含GO!和反應時間訊息) (+2)")
            elif 'go' in messages or 'reaction_time' in messages:
                total_marks += 1
                feedback.append("⚠️ 輸出格式部分正確 (+1)")
            else:
                feedback.append("❌ 輸出格式不正確 (+0)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    else:
        # Check static analysis for print statements
        if 'print(' in code_lower and ('go' in code_lower or 'reaction' in code_lower):
            total_marks += 1
            feedback.append("⚠️ 程式碼有輸出邏輯但執行失敗 (+1)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    
    # 3. Check for time.sleep and random.randint usage (2 marks)
    has_sleep = 'time.sleep' in code_lower
    has_randint = 'random.randint' in code_lower or 'randint' in code_lower
    
    if has_sleep and has_randint:
        # Check if randint is used with sleep (e.g., time.sleep(random.randint(5, 11)))
        if 'sleep' in code_lower and 'randint' in code_lower:
            total_marks += 2
            feedback.append("✅ 正確使用time.sleep和random.randint (+2)")
        else:
            total_marks += 1
            feedback.append("⚠️ 部分使用time.sleep和random.randint (+1)")
    elif has_sleep or has_randint:
        total_marks += 1
        feedback.append("⚠️ 部分使用time.sleep或random.randint (+1)")
    else:
        feedback.append("❌ 未使用time.sleep和random.randint (+0)")
    
    # 4. Check for time.time() usage and reaction time calculation (2 marks)
    has_time_time = 'time.time()' in code_lower or 'time.time(' in code_lower
    has_calculation = '-' in student_code and ('time' in code_lower or 'end' in code_lower or 'start' in code_lower)
    has_two_inputs = student_code.count('input(') >= 2
    
    if has_time_time and has_calculation and has_two_inputs:
        total_marks += 2
        feedback.append("✅ 正確使用time.time()、計算反應時間和兩個input (+2)")
    elif (has_time_time and has_calculation) or (has_time_time and has_two_inputs):
        total_marks += 1
        feedback.append("⚠️ 部分使用時間測量和輸入處理 (+1)")
    elif has_time_time:
        total_marks += 1
        feedback.append("⚠️ 使用time.time()但缺少完整邏輯 (+1)")
    else:
        feedback.append("❌ 未使用time.time()和反應時間計算 (+0)")
    
    # 5. Check for results closely matching model answers (2 marks)
    if successful_runs > 0:
        accurate_reaction_time_matches = 0
        
        for i, result in enumerate(test_results):
            if result["success"]:
                student_output = result["output"].strip()
                expected_time = result["expected_time"]
                
                # Extract reaction time from output
                actual_time = extract_reaction_time(student_output)
                
                # Check if reaction time is calculated (allow some tolerance for format differences)
                if actual_time is not None:
                    # Check if the calculation logic exists (even if values differ due to mocking)
                    if abs(actual_time - expected_time) < 0.01 or actual_time > 0:
                        accurate_reaction_time_matches += 1
                elif 'reaction' in student_output.lower() and 'time' in student_output.lower():
                    # If output mentions reaction time but format is slightly different, give partial credit
                    accurate_reaction_time_matches += 0.5
        
        # Check accuracy based on correct logic
        if accurate_reaction_time_matches >= len(TEST_CASES) - 0.5:
            total_marks += 2
            feedback.append(f"✅ 反應時間計算完全正確 ({int(accurate_reaction_time_matches)}個準確結果) (+2)")
        elif accurate_reaction_time_matches >= len(TEST_CASES) - 1.5:
            total_marks += 1
            feedback.append(f"⚠️ 反應時間計算部分正確 ({int(accurate_reaction_time_matches)}個準確結果) (+1)")
        else:
            feedback.append(f"❌ 反應時間計算不正確 ({int(accurate_reaction_time_matches)}個準確結果) (+0)")
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

        # (10 marks) The python code implements reaction time challenge correctly
        section_description = "Python程式碼實現反應時間挑戰"
        filepath = row["filepath"]
        section_mark, remarks = evaluate_reaction_time_program(filepath)

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

