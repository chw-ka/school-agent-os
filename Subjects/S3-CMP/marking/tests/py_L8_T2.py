import aia_util as aia_utils
import difflib
import re
from contextlib import redirect_stdout
from unittest.mock import patch, MagicMock
import io

# Test cases for Rock Paper Scissors game
# Each test case has 5 rounds of inputs and computer choices (via mocked randint)
TEST_CASES = [
    {
        "input": ["r", "p", "s", "r", "p"],  # 5 player choices
        "computer_choices": [1, 2, 3, 1, 2],  # r, p, s, r, p
        "expected_result": "draw"  # Based on win/loss logic
    },
    {
        "input": ["r", "r", "r", "r", "r"],  # All rock
        "computer_choices": [2, 2, 2, 2, 2],  # All paper (CPU wins all)
        "expected_result": "cpu_wins"
    },
    {
        "input": ["s", "s", "s", "s", "s"],  # All scissors
        "computer_choices": [3, 3, 3, 3, 3],  # All scissors (all draws)
        "expected_result": "draw"
    },
    {
        "input": ["p", "r", "s", "p", "r"],
        "computer_choices": [1, 3, 1, 3, 2],  # Mixed scenarios
        "expected_result": "player_wins"
    },
    {
        "input": ["r", "p", "s", "r", "s"],
        "computer_choices": [3, 1, 2, 2, 1],  # Mixed scenarios
        "expected_result": "player_wins"
    }
]

def run_student_code(student_code, test_input, return_dict, computer_choices=None):
    """Run student code with mocked input and random.randint"""
    buffer = io.StringIO()
    
    if computer_choices is None:
        computer_choices = [1, 2, 3, 1, 2]  # Default
    
    try:
        with redirect_stdout(buffer):
            with patch('builtins.input', side_effect=test_input):
                # Mock random.randint to return computer choices in sequence
                with patch('random.randint', side_effect=computer_choices):
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
    """Extract player and computer scores from output"""
    output_lower = output.lower()
    
    # Look for patterns like "Final : You 2 : 3 CPU" or "You 2 : 3 CPU"
    patterns = [
        r'you\s+(\d+)\s*:\s*(\d+)\s*cpu',
        r'final\s*:\s*you\s+(\d+)\s*:\s*(\d+)\s*cpu',
        r'(\d+)\s*:\s*(\d+)',  # Simple pattern for final score
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, output_lower, re.IGNORECASE)
        if matches:
            try:
                # Take the last match (should be the final score)
                player_score, cpu_score = matches[-1]
                return int(player_score), int(cpu_score)
            except:
                pass
    
    # Try to extract any two numbers that might be scores
    numbers = re.findall(r'\d+', output)
    if len(numbers) >= 2:
        try:
            # Try the last two numbers as scores
            return int(numbers[-2]), int(numbers[-1])
        except:
            pass
    
    return None, None

def calculate_winner(output):
    """Determine winner from output"""
    output_lower = output.lower()
    
    if 'you win' in output_lower or 'you win!' in output_lower:
        return 'player_wins'
    elif 'cpu win' in output_lower or 'cpu wins' in output_lower:
        return 'cpu_wins'
    elif 'draw' in output_lower:
        return 'draw'
    
    return None

def calculate_game_accuracy(player_choices, computer_choices, player_score, cpu_score, winner):
    """Calculate if game logic is correct based on choices"""
    # Convert computer choices (1,2,3) to r,p,s
    comp_map = {1: 'r', 2: 'p', 3: 's'}
    computer_moves = [comp_map[c] for c in computer_choices]
    
    # Calculate expected scores
    expected_player_score = 0
    expected_cpu_score = 0
    
    for p, c in zip(player_choices, computer_moves):
        # Win conditions: r beats s, s beats p, p beats r
        if (p == 'r' and c == 's') or (p == 's' and c == 'p') or (p == 'p' and c == 'r'):
            expected_player_score += 1
        elif p == c:
            pass  # Draw, no points
        else:
            expected_cpu_score += 1
    
    # Check if scores match
    score_correct = (player_score == expected_player_score and cpu_score == expected_cpu_score)
    
    # Check if winner determination is correct
    if expected_player_score > expected_cpu_score:
        expected_winner = 'player_wins'
    elif expected_cpu_score > expected_player_score:
        expected_winner = 'cpu_wins'
    else:
        expected_winner = 'draw'
    
    winner_correct = (winner == expected_winner)
    
    return score_correct and winner_correct

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
    if 'range(' in code_lower:
        score += 1
        explanation.append("✅ 使用range函數")
    
    # Check for input function
    input_count = code.count('input(')
    if input_count >= 1:
        score += 1
        explanation.append("✅ 使用input函數")
    
    # Check for random.randint
    if 'random.randint' in code_lower or 'randint' in code_lower:
        score += 1
        explanation.append("✅ 使用random.randint")
    
    # Check for if-elif-else
    if 'if' in code_lower and 'elif' in code_lower and 'else' in code_lower:
        score += 1
        explanation.append("✅ 使用if-elif-else條件判斷")
    
    # Check for score tracking
    if ('ps' in code_lower or 'player' in code_lower or 'score' in code_lower) and ('cs' in code_lower or 'cpu' in code_lower or 'computer' in code_lower):
        score += 1
        explanation.append("✅ 追蹤玩家和電腦分數")
    
    # Check for comparison operators
    if '==' in code and ('and' in code_lower or 'or' in code_lower):
        score += 1
        explanation.append("✅ 使用比較運算符和邏輯運算符")
    
    return score, explanation

def run_multiple_tests(student_code):
    """Run student code with multiple test cases"""
    test_results = []
    
    for test_case in TEST_CASES:
        buffer = io.StringIO()
        
        try:
            with redirect_stdout(buffer):
                with patch('builtins.input', side_effect=test_case["input"]):
                    with patch('random.randint', side_effect=test_case["computer_choices"]):
                        exec(student_code, {})
            test_results.append({
                "input": test_case["input"],
                "computer_choices": test_case["computer_choices"],
                "success": True,
                "output": buffer.getvalue(),
                "error": ""
            })
        except Exception as e:
            test_results.append({
                "input": test_case["input"],
                "computer_choices": test_case["computer_choices"],
                "success": False,
                "output": buffer.getvalue(),
                "error": str(e)
            })
    
    return test_results

def evaluate_rps_program(filepath):
    """Evaluate student's Rock Paper Scissors program with specific criteria (2 marks each)"""
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
        # Check if range is used for 5 rounds (range(1, 6) or range(5) or similar)
        if 'range(1' in code_lower and '6' in code_lower:
            total_marks += 2
            feedback.append("✅ 正確導入random模組和使用for循環與range (+2)")
        elif 'range(5' in code_lower or 'range(1,6' in code_lower:
            total_marks += 2
            feedback.append("✅ 正確導入random模組和使用for循環與range (+2)")
        else:
            total_marks += 1
            feedback.append("⚠️ 部分使用random模組和for循環 (+1)")
    elif has_random and has_for:
        total_marks += 1
        feedback.append("⚠️ 使用random和for循環但缺少range (+1)")
    else:
        feedback.append("❌ 未使用random模組或for循環 (+0)")
    
    # 2. Check for appropriate output (2 marks)
    if successful_runs > 0:
        # Check if output has game-related content
        sample_result = next((r for r in test_results if r["success"]), None)
        if sample_result and sample_result["output"].strip():
            output = sample_result["output"].lower()
            
            # Check for round outputs, final score, and winner
            has_rounds = 'round' in output or 'you:' in output or 'cpu:' in output
            has_final = 'final' in output or ('you' in output and 'cpu' in output and ':' in output)
            has_winner = 'win' in output or 'draw' in output
            
            if has_rounds and has_final and has_winner:
                total_marks += 2
                feedback.append("✅ 輸出格式正確(包含回合、最終分數和勝負) (+2)")
            elif has_rounds or (has_final and has_winner):
                total_marks += 1
                feedback.append("⚠️ 輸出格式部分正確 (+1)")
            else:
                feedback.append("❌ 輸出格式不正確 (+0)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    else:
        # Check static analysis for print statements
        if 'print(' in code_lower and ('round' in code_lower or 'win' in code_lower):
            total_marks += 1
            feedback.append("⚠️ 程式碼有輸出邏輯但執行失敗 (+1)")
        else:
            feedback.append("❌ 輸出格式不正確 (+0)")
    
    # 3. Check for random.randint usage and input handling (2 marks)
    has_randint = 'random.randint' in code_lower or 'randint' in code_lower
    has_input = 'input(' in code_lower
    input_count = student_code.count('input(')
    # Check if input is used in a for loop (will be called 5 times in runtime)
    has_input_in_loop = has_input and has_for
    
    if has_randint and has_input and has_input_in_loop:
        # Check if randint is used appropriately (e.g., random.randint(1, 3))
        if 'randint(1' in code_lower and ('3' in code_lower or '2' in code_lower):
            total_marks += 2
            feedback.append("✅ 正確使用random.randint和input處理5回合 (+2)")
        else:
            total_marks += 1
            feedback.append("⚠️ 部分使用random.randint和input (+1)")
    elif has_randint and has_input:
        total_marks += 1
        feedback.append("⚠️ 使用random.randint和input但可能不夠完整 (+1)")
    else:
        feedback.append("❌ 未使用random.randint或input (+0)")
    
    # 4. Check for win/loss/draw logic and score tracking (2 marks)
    has_if_elif = 'if' in code_lower and 'elif' in code_lower
    has_comparison = '==' in student_code
    has_score_tracking = (('ps' in code_lower or 'player' in code_lower) and 
                          ('cs' in code_lower or 'cpu' in code_lower or 'computer' in code_lower))
    has_logic = 'and' in code_lower or 'or' in code_lower
    
    if has_if_elif and has_comparison and has_score_tracking and has_logic:
        total_marks += 2
        feedback.append("✅ 正確使用條件判斷、分數追蹤和邏輯運算符 (+2)")
    elif has_if_elif and has_comparison and has_score_tracking:
        total_marks += 1
        feedback.append("⚠️ 部分使用條件判斷和分數追蹤 (+1)")
    elif has_if_elif and has_comparison:
        total_marks += 1
        feedback.append("⚠️ 部分使用條件判斷但缺少分數追蹤 (+1)")
    else:
        feedback.append("❌ 未使用必要的條件判斷和分數追蹤 (+0)")
    
    # 5. Check for results closely matching model answers (2 marks)
    if successful_runs > 0:
        accurate_game_matches = 0
        
        for i, result in enumerate(test_results):
            if result["success"]:
                student_output = result["output"].strip()
                player_choices = result["input"]
                computer_choices = result["computer_choices"]
                
                # Extract scores and winner
                player_score, cpu_score = extract_scores(student_output)
                winner = calculate_winner(student_output)
                
                # Check if game logic is correct
                if player_score is not None and cpu_score is not None and winner:
                    if calculate_game_accuracy(player_choices, computer_choices, player_score, cpu_score, winner):
                        accurate_game_matches += 1
        
        # Check accuracy based on correct logic
        if accurate_game_matches >= len(TEST_CASES) - 1:
            total_marks += 2
            feedback.append(f"✅ 遊戲邏輯完全正確 ({accurate_game_matches}個準確結果) (+2)")
        elif accurate_game_matches >= len(TEST_CASES) - 2:
            total_marks += 1
            feedback.append(f"⚠️ 遊戲邏輯部分正確 ({accurate_game_matches}個準確結果) (+1)")
        else:
            feedback.append(f"❌ 遊戲邏輯不正確 ({accurate_game_matches}個準確結果) (+0)")
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

        # (10 marks) The python code implements Rock Paper Scissors game correctly
        section_description = "Python程式碼實現猜拳遊戲"
        filepath = row["filepath"]
        section_mark, remarks = evaluate_rps_program(filepath)

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

