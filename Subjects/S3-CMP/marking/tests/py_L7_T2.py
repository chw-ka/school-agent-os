import aia_util as aia_utils
import difflib
import re
from contextlib import redirect_stdout
from unittest.mock import patch, MagicMock
import io

# Test cases with mocked random numbers and corresponding answers
# Each test case mocks random.randint to return specific pairs of numbers
# and provides the correct answers as input
TEST_CASES = [
    {
        "input": ["5", "10", "10", "7", "15"],  # Answers for 5 questions
        "random_values": [(2, 3), (5, 5), (8, 2), (4, 3), (10, 5)],  # (num1, num2) pairs
        "expected_score": 5  # All correct: 2+3=5, 5+5=10, 8+2=10, 4+3=7, 10+5=15
    },
    {
        "input": ["0", "0", "0", "0", "0"],  # All wrong answers
        "random_values": [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)],  # (num1, num2) pairs
        "expected_score": 0  # All wrong: correct answers are 3, 7, 11, 15, 19
    },
    {
        "input": ["7", "9", "6", "12", "7"],  # Mixed correct/incorrect
        "random_values": [(3, 4), (5, 5), (2, 4), (6, 6), (3, 5)],  # (num1, num2) pairs
        "expected_score": 3  # 3+4=7✓, 5+5=10✗(answered 9), 2+4=6✓, 6+6=12✓, 3+5=8✗(answered 7)
    }
]

def run_student_code(student_code, test_input, return_dict, random_values=None):
    """Run student code with mocked input and optionally mocked random.randint"""
    buffer = io.StringIO()
    
    try:
        with redirect_stdout(buffer):
            with patch('builtins.input', side_effect=test_input):
                if random_values and 'randint' in student_code.lower():
                    # Create a side_effect that returns values in sequence
                    def randint_side_effect(a, b):
                        if not hasattr(randint_side_effect, 'call_count'):
                            randint_side_effect.call_count = 0
                        # Alternate between num1 and num2
                        pair_idx = randint_side_effect.call_count // 2
                        if pair_idx < len(random_values):
                            if randint_side_effect.call_count % 2 == 0:
                                result = random_values[pair_idx][0]
                            else:
                                result = random_values[pair_idx][1]
                            randint_side_effect.call_count += 1
                            return result
                        return 0
                    
                    with patch('random.randint', side_effect=randint_side_effect):
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

def extract_score(output):
    """Extract final score from output"""
    output_lower = output.lower()
    
    # Try to find the score in the output
    # Look for patterns like "got 3 out of 5" or "score: 3" or similar
    patterns = [
        r'got\s+(\d+)\s+out\s+of\s+5',
        r'score[:\s=]+(\d+)',
        r'(\d+)\s+out\s+of\s+5',
        r'(\d+)\s+correct',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, output_lower)
        if match:
            try:
                return int(match.group(1))
            except:
                pass
    
    # If pattern matching fails, try to extract numbers and find the one that's <= 5
    numbers = re.findall(r'\d+', output)
    for num_str in reversed(numbers):  # Check from end (likely to be the final score)
        try:
            num = int(num_str)
            if 0 <= num <= 5:
                return num
        except:
            pass
    
    return None

def calculate_quiz_accuracy(student_output, expected_score):
    """Calculate if quiz score is correct"""
    student_score = extract_score(student_output)
    return student_score == expected_score

def analyze_code_quality(code):
    """Analyze code quality for non-running programs"""
    score = 0
    explanation = []
    
    code_lower = code.lower()
    
    # Check for import random
    if "import random" in code_lower or "from random import" in code_lower:
        score += 1
        explanation.append("✅ 使用random模組")
    
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
    
    # Check for for loop
    if 'for' in code_lower:
        score += 1
        explanation.append("✅ 使用for循環")
    
    # Check for range function
    if 'range(' in code_lower:
        score += 1
        explanation.append("✅ 使用range函數")
    
    # Check for random.randint
    if 'randint' in code_lower:
        score += 1
        explanation.append("✅ 使用randint函數")
    
    # Check for if statement
    if 'if' in code_lower:
        score += 1
        explanation.append("✅ 使用if條件判斷")
    
    # Check for score variable
    if 'score' in code_lower:
        score += 1
        explanation.append("✅ 使用score變數")
    
    return score, explanation

def run_multiple_tests(student_code):
    """Run student code with multiple test cases using mocked random"""
    test_results = []
    
    for test_case in TEST_CASES:
        buffer = io.StringIO()
        random_values = test_case.get("random_values", [])
        
        try:
            with redirect_stdout(buffer):
                with patch('builtins.input', side_effect=test_case["input"]):
                    if random_values and 'randint' in student_code.lower():
                        # Create a side_effect that returns values in sequence
                        # randint is called twice per question (num1, num2), so we need to alternate
                        call_count = [0]  # Use list to allow modification in nested function
                        
                        def randint_side_effect(a, b):
                            pair_idx = call_count[0] // 2
                            if pair_idx < len(random_values):
                                if call_count[0] % 2 == 0:
                                    result = random_values[pair_idx][0]
                                else:
                                    result = random_values[pair_idx][1]
                                call_count[0] += 1
                                return result
                            # Fallback if called more than expected
                            return 0
                        
                        with patch('random.randint', side_effect=randint_side_effect):
                            exec(student_code, {})
                    else:
                        exec(student_code, {})
            test_results.append({
                "input": test_case["input"],
                "success": True,
                "output": buffer.getvalue(),
                "error": "",
                "expected_score": test_case["expected_score"]
            })
        except Exception as e:
            test_results.append({
                "input": test_case["input"],
                "success": False,
                "output": buffer.getvalue(),
                "error": str(e),
                "expected_score": test_case["expected_score"]
            })
    
    return test_results

def evaluate_quiz_program(filepath):
    """Evaluate student's math quiz program with specific criteria (2 marks each)"""
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
    
    # 1. Check for import random and random.randint usage (2 marks)
    code_lower = student_code.lower()
    has_import_random = "import random" in code_lower or "from random import" in code_lower
    has_randint = 'randint' in code_lower
    
    if has_import_random and has_randint:
        total_marks += 2
        feedback.append("✅ 正確使用random模組和randint函數 (+2)")
    elif has_import_random or has_randint:
        total_marks += 1
        feedback.append("⚠️ 部分使用random模組或randint函數 (+1)")
    else:
        feedback.append("❌ 未使用random模組和randint函數 (+0)")
    
    # 2. Check for appropriate output (2 marks)
    if successful_runs > 0:
        # Check if output has quiz-related content
        sample_result = next((r for r in test_results if r["success"]), None)
        if sample_result and sample_result["output"].strip():
            output = sample_result["output"].lower()
            if ('question' in output or 'correct' in output or 'wrong' in output) and ('score' in output or 'out of' in output):
                total_marks += 2
                feedback.append("✅ 輸出格式正確(包含問題和分數訊息) (+2)")
            elif 'question' in output or 'correct' in output or 'wrong' in output:
                total_marks += 1
                feedback.append("⚠️ 輸出格式部分正確 (+1)")
            else:
                feedback.append("❌ 輸出格式不正確 (+0)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    else:
        # Check static analysis for print statements
        if 'print(' in code_lower and ('question' in code_lower or 'correct' in code_lower or 'score' in code_lower):
            total_marks += 1
            feedback.append("⚠️ 程式碼有輸出邏輯但執行失敗 (+1)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    
    # 3. Check for for loop with range (2 marks)
    has_for = 'for' in code_lower
    has_range = 'range(' in code_lower
    
    if has_for and has_range:
        # Check if range is used for 5 iterations (range(1,6) or range(5))
        if ('range(1' in code_lower and '6' in code_lower) or 'range(5' in code_lower:
            total_marks += 2
            feedback.append("✅ 正確使用for循環和range函數(5次循環) (+2)")
        else:
            total_marks += 1
            feedback.append("⚠️ 部分使用for循環和range (+1)")
    elif has_for:
        total_marks += 1
        feedback.append("⚠️ 使用for循環但缺少range (+1)")
    else:
        feedback.append("❌ 未使用for循環和range (+0)")
    
    # 4. Check for int(input) and if-else for answer checking (2 marks)
    has_int_input = 'int(input(' in code_lower
    has_if = 'if' in code_lower
    has_else = 'else' in code_lower
    has_comparison = '==' in student_code
    
    if has_int_input and has_if and has_else and has_comparison:
        total_marks += 2
        feedback.append("✅ 正確使用int(input)、if-else條件判斷和比較運算符 (+2)")
    elif has_int_input and has_if and has_comparison:
        total_marks += 1
        feedback.append("⚠️ 部分使用輸入轉換和條件判斷(缺少else) (+1)")
    elif has_int_input or (has_if and has_comparison):
        total_marks += 1
        feedback.append("⚠️ 部分使用輸入轉換或條件判斷 (+1)")
    else:
        feedback.append("❌ 未使用必要的輸入轉換和條件判斷 (+0)")
    
    # 5. Check for results closely matching model answers (2 marks)
    if successful_runs > 0:
        accurate_score_matches = 0
        
        for i, result in enumerate(test_results):
            if result["success"]:
                student_output = result["output"].strip()
                expected_score = result.get("expected_score", 0)
                
                # Check if score calculation is correct
                if calculate_quiz_accuracy(student_output, expected_score):
                    accurate_score_matches += 1
        
        # Check accuracy based on correct logic
        if accurate_score_matches >= len(TEST_CASES) - 1:
            total_marks += 2
            feedback.append(f"✅ 分數計算完全正確 ({accurate_score_matches}個準確結果) (+2)")
        elif accurate_score_matches >= len(TEST_CASES) - 2:
            total_marks += 1
            feedback.append(f"⚠️ 分數計算部分正確 ({accurate_score_matches}個準確結果) (+1)")
        else:
            feedback.append(f"❌ 分數計算不正確 ({accurate_score_matches}個準確結果) (+0)")
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

        # (10 marks) The python code implements math quiz correctly
        section_description = "Python程式碼實現數學測驗"
        filepath = row["filepath"]
        section_mark, remarks = evaluate_quiz_program(filepath)

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

