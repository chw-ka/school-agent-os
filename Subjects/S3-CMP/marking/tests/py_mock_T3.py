import aia_util as aia_utils
import difflib
import re
from contextlib import redirect_stdout
from unittest.mock import patch, MagicMock
import io

# Test cases for Dice Battle Game
# Each test case has 5 rounds, each round needs Enter key press
# Computer dice values are mocked via random.randint
TEST_CASES = [
    {
        "input": ["", "", "", "", ""],  # 5 Enter presses
        "user_dice": [6, 5, 4, 3, 2],  # User rolls
        "cpu_dice": [1, 2, 3, 4, 5],   # CPU rolls (user wins all)
        "expected_user_score": 5,
        "expected_cpu_score": 0,
        "description": "User wins all rounds"
    },
    {
        "input": ["", "", "", "", ""],
        "user_dice": [1, 2, 3, 4, 5],
        "cpu_dice": [6, 5, 4, 3, 2],   # CPU wins all
        "expected_user_score": 0,
        "expected_cpu_score": 5,
        "description": "CPU wins all rounds"
    },
    {
        "input": ["", "", "", "", ""],
        "user_dice": [3, 4, 5, 2, 6],
        "cpu_dice": [2, 5, 3, 4, 1],   # Mixed: user wins 3, CPU wins 2
        "expected_user_score": 3,
        "expected_cpu_score": 2,
        "description": "Mixed results"
    },
    {
        "input": ["", "", "", "", ""],
        "user_dice": [6, 3, 4, 5, 2],
        "cpu_dice": [1, 6, 1, 1, 5],   # User wins 3, CPU wins 2
        "expected_user_score": 3,
        "expected_cpu_score": 2,
        "description": "User wins majority"
    },
    {
        "input": ["", "", "", "", ""],
        "user_dice": [1, 2, 3, 4, 5],
        "cpu_dice": [1, 2, 3, 4, 5],   # All ties (no scores)
        "expected_user_score": 0,
        "expected_cpu_score": 0,
        "description": "All ties"
    },
    {
        "input": ["", "", "", "", ""],
        "user_dice": [4, 6, 2, 5, 3],
        "cpu_dice": [3, 4, 6, 2, 5],   # All ties (no scores)
        "expected_user_score": 0,
        "expected_cpu_score": 0,
        "description": "All ties (different pattern)"
    },
    {
        "input": ["", "", "", "", ""],
        "user_dice": [5, 6, 4, 3, 6],
        "cpu_dice": [2, 1, 3, 4, 1],   # User wins 4, CPU wins 1
        "expected_user_score": 4,
        "expected_cpu_score": 1,
        "description": "User wins most rounds"
    }
]

def run_student_code(student_code, test_input, return_dict, user_dice=None, cpu_dice=None):
    """Run student code with mocked input and random.randint"""
    buffer = io.StringIO()
    
    if user_dice is None:
        user_dice = [1, 2, 3, 4, 5]
    if cpu_dice is None:
        cpu_dice = [1, 2, 3, 4, 5]
    
    try:
        with redirect_stdout(buffer):
            with patch('builtins.input', side_effect=test_input):
                # Mock random.randint to alternate between user and CPU dice
                dice_sequence = []
                for u, c in zip(user_dice, cpu_dice):
                    dice_sequence.extend([u, c])  # First call for user, second for CPU
                
                with patch('random.randint', side_effect=dice_sequence):
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

def extract_scores(output):
    """Extract user and CPU scores from output"""
    output_lower = output.lower()
    
    # Look for "Final score: You 3 : 2 CPU" or "You 3 : 2 CPU"
    patterns = [
        r'final\s+score[:\s]+you\s+(\d+)\s*:\s*(\d+)\s*cpu',
        r'you\s+(\d+)\s*:\s*(\d+)\s*cpu',
        r'(\d+)\s*:\s*(\d+)',  # Simple pattern
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, output_lower, re.IGNORECASE)
        if matches:
            try:
                # Take the last match (should be final score)
                user_score, cpu_score = matches[-1]
                return int(user_score), int(cpu_score)
            except:
                pass
    
    # Try to extract any two numbers near "final" or "score"
    if 'final' in output_lower or 'score' in output_lower:
        numbers = re.findall(r'\d+', output)
        if len(numbers) >= 2:
            try:
                # Try the last two numbers as scores
                return int(numbers[-2]), int(numbers[-1])
            except:
                pass
    
    return None, None

def calculate_game_accuracy(output, user_dice, cpu_dice):
    """Calculate if game logic is correct based on dice values"""
    # Calculate expected scores
    expected_user_score = 0
    expected_cpu_score = 0
    
    for u, c in zip(user_dice, cpu_dice):
        if u > c:
            expected_user_score += 1
        elif c > u:
            expected_cpu_score += 1
        # If equal, no score (tie)
    
    # Extract actual scores from output
    user_score, cpu_score = extract_scores(output)
    
    if user_score is not None and cpu_score is not None:
        return user_score == expected_user_score and cpu_score == expected_cpu_score
    
    return False

def analyze_code_quality(code):
    """Analyze code quality for non-running programs"""
    score = 0
    explanation = []
    
    code_lower = code.lower()
    
    # Check for import random
    if 'import random' in code_lower or 'from random' in code_lower:
        score += 1
        explanation.append("✅ 導入random模組")
    
    # Check for for loop
    if 'for' in code_lower:
        score += 1
        explanation.append("✅ 使用for循環")
    
    # Check for range function
    if 'range(' in code_lower and ('5' in code or 'range(5' in code_lower):
        score += 1
        explanation.append("✅ 使用range(5)進行5局比賽")
    
    # Check for input function
    input_count = code.count('input(')
    if input_count >= 1:
        score += 1
        explanation.append("✅ 使用input函數")
    
    # Check for random.randint
    if 'random.randint' in code_lower or 'randint' in code_lower:
        score += 1
        explanation.append("✅ 使用random.randint")
    
    # Check for score variables
    if ('user_score' in code_lower or 'user' in code_lower and 'score' in code_lower) and ('cpu_score' in code_lower or 'cpu' in code_lower and 'score' in code_lower):
        score += 1
        explanation.append("✅ 使用分數變數(user_score和cpu_score)")
    
    # Check for if-elif statements
    if 'if' in code_lower and ('elif' in code_lower or 'else' in code_lower):
        score += 1
        explanation.append("✅ 使用if-elif條件判斷")
    
    # Check for comparison operators
    if '>' in code or '<' in code:
        score += 1
        explanation.append("✅ 使用比較運算符")
    
    # Check for print statements
    print_count = code.count('print(')
    if print_count >= 5:
        score += 1
        explanation.append("✅ 使用多個print函數輸出")
    
    return score, explanation

def run_multiple_tests(student_code):
    """Run student code with multiple test cases"""
    test_results = []
    
    for test_case in TEST_CASES:
        buffer = io.StringIO()
        
        try:
            with redirect_stdout(buffer):
                with patch('builtins.input', side_effect=test_case["input"]):
                    # Mock random.randint to return dice values in sequence
                    dice_sequence = []
                    for u, c in zip(test_case["user_dice"], test_case["cpu_dice"]):
                        dice_sequence.extend([u, c])  # First for user, then CPU
                    
                    with patch('random.randint', side_effect=dice_sequence):
                        exec(student_code, {})
            test_results.append({
                "input": test_case["input"],
                "user_dice": test_case["user_dice"],
                "cpu_dice": test_case["cpu_dice"],
                "success": True,
                "output": buffer.getvalue(),
                "error": "",
                "expected": test_case
            })
        except Exception as e:
            test_results.append({
                "input": test_case["input"],
                "user_dice": test_case["user_dice"],
                "cpu_dice": test_case["cpu_dice"],
                "success": False,
                "output": buffer.getvalue(),
                "error": str(e),
                "expected": test_case
            })
    
    return test_results

def evaluate_dice_game_program(filepath):
    """Evaluate student's dice battle game program with specific criteria (2 marks each)"""
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
    
    # 1. Check for import random and for loop with range (2 marks)
    code_lower = student_code.lower()
    has_random = 'import random' in code_lower or 'from random' in code_lower
    has_for = 'for' in code_lower
    has_range = 'range(' in code_lower
    
    if has_random and has_for and has_range:
        # Check if range is for 5 rounds
        if 'range(5' in code_lower or 'range(1,6' in code_lower:
            total_marks += 2
            feedback.append("✅ 正確導入random模組和使用for循環與range(5局) (+2)")
        else:
            total_marks += 1
            feedback.append("⚠️ 使用random和for循環但range可能不正確 (+1)")
    elif has_random and has_for:
        total_marks += 1
        feedback.append("⚠️ 使用random和for循環但缺少range (+1)")
    else:
        feedback.append("❌ 未導入random模組或使用for循環 (+0)")
    
    # 2. Check for appropriate output format (2 marks)
    if successful_runs > 0:
        sample_result = next((r for r in test_results if r["success"]), None)
        if sample_result and sample_result["output"].strip():
            output = sample_result["output"].lower()
            
            has_initial = 'dice battle' in output or 'dice' in output and 'game' in output
            has_rounds = 'round' in output
            has_dice_output = 'rolled' in output or 'dice' in output
            has_final = 'final score' in output or ('you' in output and 'cpu' in output and ':' in output)
            
            if has_initial and has_rounds and has_dice_output and has_final:
                total_marks += 2
                feedback.append("✅ 輸出格式正確(包含遊戲標題、回合、骰子結果和最終分數) (+2)")
            elif (has_initial or has_rounds) and (has_dice_output or has_final):
                total_marks += 1
                feedback.append("⚠️ 輸出格式部分正確 (+1)")
            else:
                feedback.append("❌ 輸出格式不正確 (+0)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    else:
        if 'print(' in code_lower and ('dice' in code_lower or 'round' in code_lower):
            total_marks += 1
            feedback.append("⚠️ 程式碼有輸出邏輯但執行失敗 (+1)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    
    # 3. Check for random.randint usage and input handling (2 marks)
    has_randint = 'random.randint' in code_lower or 'randint' in code_lower
    has_input = 'input(' in code_lower
    
    if has_randint and has_input:
        # Check if randint is used for dice (1, 6)
        if 'randint(1' in code_lower and ('6' in code_lower or '5' in code_lower):
            total_marks += 2
            feedback.append("✅ 正確使用random.randint(1,6)和input函數 (+2)")
        else:
            total_marks += 1
            feedback.append("⚠️ 使用random.randint和input但可能參數不正確 (+1)")
    elif has_randint or has_input:
        total_marks += 1
        feedback.append("⚠️ 部分使用random.randint或input (+1)")
    else:
        feedback.append("❌ 未使用random.randint或input (+0)")
    
    # 4. Check for score tracking and win/loss logic (2 marks)
    has_score_vars = (('user_score' in code_lower or 'user' in code_lower and 'score' in code_lower) and 
                      ('cpu_score' in code_lower or 'cpu' in code_lower and 'score' in code_lower))
    has_if_elif = 'if' in code_lower and 'elif' in code_lower
    has_comparison = '>' in student_code or '<' in student_code
    has_score_update = '+=' in student_code or ('=' in code_lower and 'score' in code_lower and '+' in code_lower)
    
    if has_score_vars and has_if_elif and has_comparison and has_score_update:
        total_marks += 2
        feedback.append("✅ 正確使用分數變數、條件判斷和分數更新 (+2)")
    elif has_score_vars and has_if_elif and has_comparison:
        total_marks += 1
        feedback.append("⚠️ 部分使用分數變數和條件判斷但缺少分數更新 (+1)")
    elif has_score_vars or (has_if_elif and has_comparison):
        total_marks += 1
        feedback.append("⚠️ 部分使用分數追蹤或條件判斷 (+1)")
    else:
        feedback.append("❌ 未使用必要的分數追蹤和條件判斷 (+0)")
    
    # 5. Check for results closely matching model answers (2 marks)
    if successful_runs > 0:
        accurate_matches = 0
        
        for i, result in enumerate(test_results):
            if result["success"]:
                student_output = result["output"].strip()
                user_dice = result["user_dice"]
                cpu_dice = result["cpu_dice"]
                
                # Check if game logic is correct
                if calculate_game_accuracy(student_output, user_dice, cpu_dice):
                    accurate_matches += 1
        
        # Check accuracy
        if accurate_matches >= len(TEST_CASES) - 1:
            total_marks += 2
            feedback.append(f"✅ 遊戲邏輯完全正確 ({accurate_matches}個準確結果) (+2)")
        elif accurate_matches >= len(TEST_CASES) - 2:
            total_marks += 1
            feedback.append(f"⚠️ 遊戲邏輯部分正確 ({accurate_matches}個準確結果) (+1)")
        else:
            feedback.append(f"❌ 遊戲邏輯不正確 ({accurate_matches}個準確結果) (+0)")
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

        # (10 marks) The python code implements dice battle game correctly
        section_description = "Python程式碼實現骰子大戰遊戲"
        filepath = row["filepath"]
        section_mark, remarks = evaluate_dice_game_program(filepath)

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

