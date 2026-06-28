import aia_util as aia_utils
import difflib
from contextlib import redirect_stdout
from unittest.mock import patch, MagicMock
import io

# Test cases with different age inputs and expected outputs
TEST_CASES = [
    {
        "input": ["18"],
        "expected": "Your age: Your can vote"
    },
    {
        "input": ["25"],
        "expected": "Your age: Your can vote"
    },
    {
        "input": ["17"],
        "expected": "Your age: You are not eligible to vote yet."
    },
    {
        "input": ["16"],
        "expected": "Your age: You are not eligible to vote yet."
    },
    {
        "input": ["50"],
        "expected": "Your age: Your can vote"
    },
    {
        "input": ["10"],
        "expected": "Your age: You are not eligible to vote yet."
    },
    {
        "input": ["21"],
        "expected": "Your age: Your can vote"
    },
    {
        "input": ["15"],
        "expected": "Your age: You are not eligible to vote yet."
    },
    {
        "input": ["100"],
        "expected": "Your age: Your can vote"
    },
    {
        "input": ["5"],
        "expected": "Your age: You are not eligible to vote yet."
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

def extract_vote_eligibility(output):
    """Extract voting eligibility from output"""
    output_lower = output.lower()
    
    # Check for vote/can vote keywords
    if 'can vote' in output_lower or 'you can vote' in output_lower or 'your can vote' in output_lower:
        return 'can_vote'
    # Check for not eligible/cannot vote keywords
    elif 'not eligible' in output_lower or 'cannot vote' in output_lower or 'can not vote' in output_lower:
        return 'not_eligible'
    
    return None

def calculate_vote_accuracy(student_output, age):
    """Calculate if voting eligibility logic is correct"""
    student_result = extract_vote_eligibility(student_output)
    
    # Determine expected result based on age
    expected_result = 'can_vote' if int(age) >= 18 else 'not_eligible'
    
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
    
    # Check for if statement
    if 'if' in code_lower:
        score += 1
        explanation.append("✅ 使用if條件判斷")
    
    # Check for else statement
    if 'else' in code_lower:
        score += 1
        explanation.append("✅ 使用else分支")
    
    # Check for comparison operator
    if '>=' in code or '<=' in code or '>' in code or '<' in code or '==' in code:
        score += 1
        explanation.append("✅ 使用比較運算符")
    
    # Check for voting-related keywords
    if 'vote' in code_lower or '18' in code:
        score += 1
        explanation.append("✅ 包含投票相關邏輯")
    
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

def evaluate_vote_program(filepath):
    """Evaluate student's voting eligibility program with specific criteria (2 marks each)"""
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
        # Check if output has voting-related content
        sample_result = next((r for r in test_results if r["success"]), None)
        if sample_result and sample_result["output"].strip():
            output = sample_result["output"].lower()
            if 'vote' in output:
                total_marks += 2
                feedback.append("✅ 輸出格式正確(包含投票相關訊息) (+2)")
            else:
                total_marks += 1
                feedback.append("⚠️ 輸出格式部分正確 (+1)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    else:
        # Check static analysis for print statements
        if 'print(' in code_lower and 'vote' in code_lower:
            total_marks += 1
            feedback.append("⚠️ 程式碼有輸出邏輯但執行失敗 (+1)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    
    # 3. Check for nice input handling (2 marks)
    input_count = student_code.count('input(')
    if input_count >= 1:
        total_marks += 2
        feedback.append("✅ 正確使用input函數 (+2)")
    else:
        feedback.append("❌ 未正確使用input函數 (+0)")
    
    # 4. Check for if-else conditional statements (2 marks)
    has_if = 'if' in code_lower
    has_else = 'else' in code_lower
    has_comparison = any(op in student_code for op in ['>=', '<=', '>', '<', '==', '!='])
    
    if has_if and has_else and has_comparison:
        total_marks += 2
        feedback.append("✅ 正確使用if-else條件判斷和比較運算符 (+2)")
    elif has_if and (has_else or has_comparison):
        total_marks += 1
        feedback.append("⚠️ 部分使用條件判斷 (+1)")
    else:
        feedback.append("❌ 未使用必要的條件判斷 (+0)")
    
    # 5. Check for results closely matching model answers (2 marks)
    if successful_runs > 0:
        accurate_vote_matches = 0
        
        for i, result in enumerate(test_results):
            if result["success"]:
                student_output = result["output"].strip()
                age = test_results[i]["input"][0]
                
                # Check if voting eligibility logic is correct
                if calculate_vote_accuracy(student_output, age):
                    accurate_vote_matches += 1
        
        # Check accuracy based on correct logic
        if accurate_vote_matches >= len(TEST_CASES) - 1:
            total_marks += 2
            feedback.append(f"✅ 投票資格判斷完全正確 ({accurate_vote_matches}個準確結果) (+2)")
        elif accurate_vote_matches >= len(TEST_CASES) - 2:
            total_marks += 1
            feedback.append(f"⚠️ 投票資格判斷部分正確 ({accurate_vote_matches}個準確結果) (+1)")
        else:
            feedback.append(f"❌ 投票資格判斷不正確 ({accurate_vote_matches}個準確結果) (+0)")
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

        # (10 marks) The python code determines voting eligibility correctly
        section_description = "Python程式碼判斷投票資格"
        filepath = row["filepath"]
        section_mark, remarks = evaluate_vote_program(filepath)

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
