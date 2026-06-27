import aia_util as aia_utils
import difflib
import re
from contextlib import redirect_stdout
from unittest.mock import patch, MagicMock
import io
import multiprocessing as mp

# Test cases for Lucky Number Battle game
# Each test case defines the random numbers for 5 rounds
# Format: [(user_num, cpu_num), ...] for 5 rounds
TEST_CASES = [
    {
        "random_values": [(8, 3), (5, 7), (10, 2), (4, 4), (6, 9)],  # User wins 3, CPU wins 2, 1 draw, 1 great win
        "expected_user_score": 3,
        "expected_cpu_score": 2,
        "expected_winner": "You win the game!",
        "description": "User wins with great win"
    },
    {
        "random_values": [(2, 9), (1, 8), (3, 7), (4, 6), (5, 10)],  # CPU wins all
        "expected_user_score": 0,
        "expected_cpu_score": 5,
        "expected_winner": "CPU wins the game!",
        "description": "CPU wins all rounds"
    },
    {
        "random_values": [(9, 1), (8, 2), (7, 3), (6, 4), (5, 5)],  # User wins 4, 1 draw, multiple great wins
        "expected_user_score": 4,
        "expected_cpu_score": 0,
        "expected_winner": "You win the game!",
        "description": "User wins with multiple great wins"
    },
    {
        "random_values": [(5, 5), (5, 5), (5, 5), (5, 5), (5, 5)],  # All draws
        "expected_user_score": 0,
        "expected_cpu_score": 0,
        "expected_winner": "It's a draw!",
        "description": "All rounds are draws"
    },
    {
        "random_values": [(7, 4), (3, 8), (9, 6), (2, 2), (10, 1)],  # User wins 3, CPU wins 1, 1 draw
        "expected_user_score": 3,
        "expected_cpu_score": 1,
        "expected_winner": "You win the game!",
        "description": "User wins majority"
    },
    {
        "random_values": [(1, 10), (2, 9), (3, 8), (4, 7), (5, 6)],  # CPU wins all
        "expected_user_score": 0,
        "expected_cpu_score": 5,
        "expected_winner": "CPU wins the game!",
        "description": "CPU wins all (low user numbers)"
    },
    {
        "random_values": [(10, 7), (9, 6), (8, 5), (7, 4), (6, 3)],  # User wins all with great wins
        "expected_user_score": 5,
        "expected_cpu_score": 0,
        "expected_winner": "You win the game!",
        "description": "User wins all with great wins"
    },
    {
        "random_values": [(6, 3), (4, 7), (8, 2), (5, 5), (9, 1)],  # User wins 3, CPU wins 1, 1 draw
        "expected_user_score": 3,
        "expected_cpu_score": 1,
        "expected_winner": "You win the game!",
        "description": "Mixed results user wins"
    },
    {
        "random_values": [(3, 6), (7, 4), (2, 8), (5, 5), (1, 9)],  # User wins 1, CPU wins 3, 1 draw
        "expected_user_score": 1,
        "expected_cpu_score": 3,
        "expected_winner": "CPU wins the game!",
        "description": "CPU wins majority"
    },
    {
        "random_values": [(5, 5), (6, 4), (4, 6), (5, 5), (7, 3)],  # User wins 2, CPU wins 1, 2 draws
        "expected_user_score": 2,
        "expected_cpu_score": 1,
        "expected_winner": "You win the game!",
        "description": "User wins with draws"
    }
]

def _exec_student_code_in_subprocess(student_code, random_values, result_queue):
    """Child process target: run student code and return output / errors via queue."""
    buffer = io.StringIO()
    try:
        # Create side_effect for random.randint: first call for user_num, second for cpu_num, repeat
        random_side_effect = []
        for user_num, cpu_num in random_values:
            random_side_effect.extend([user_num, cpu_num])
        
        # Input side_effect: 5 Enter key presses
        input_side_effect = [""] * 5
        
        with redirect_stdout(buffer):
            with patch('builtins.input', side_effect=input_side_effect):
                with patch('random.randint', side_effect=random_side_effect):
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


def run_student_code(student_code, random_values, timeout_seconds=2.0):
    """Run student code with mocked random and input, with a hard timeout to prevent infinite loops."""
    ctx = mp.get_context("fork")
    result_queue = ctx.Queue()
    p = ctx.Process(
        target=_exec_student_code_in_subprocess, args=(student_code, random_values, result_queue)
    )
    p.start()
    p.join(timeout=timeout_seconds)
    if p.is_alive():
        p.terminate()
        p.join(timeout=1.0)
        if p.is_alive():
            p.kill()
        return {
            "runs": False,
            "output": "",
            "error": "Code execution timed out (possible infinite loop)",
            "timed_out": True,
        }
    if result_queue.empty():
        result = {"runs": False, "output": "", "error": "No result returned", "timed_out": False}
    else:
        result = result_queue.get()
    result["timed_out"] = False
    return result

def calculate_similarity(output1, output2):
    """Calculate similarity between two outputs"""
    return difflib.SequenceMatcher(None, output1.strip(), output2.strip()).ratio()

def extract_start_message(output):
    """Check if start message is present"""
    output_lower = output.lower()
    has_title = "lucky number battle" in output_lower
    has_description = "pick a number 5 times" in output_lower or "pick a number" in output_lower
    return has_title and has_description

def extract_scores(output):
    """Extract final scores from output"""
    output_lower = output.lower()
    
    # Look for "Final score: You X : Y CPU"
    patterns = [
        r'final\s+score[:\s]+you\s+(\d+)\s*:\s*(\d+)\s*cpu',
        r'final\s+score[:\s]+(\d+)\s*:\s*(\d+)',
        r'you\s+(\d+)\s*:\s*(\d+)\s*cpu',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, output_lower, re.IGNORECASE)
        if matches:
            try:
                user_score = int(matches[0][0])
                cpu_score = int(matches[0][1])
                return user_score, cpu_score
            except:
                pass
    
    return None, None

def extract_winner_message(output):
    """Extract winner message from output"""
    output_lower = output.lower()
    
    if "you win the game" in output_lower:
        return "You win the game!"
    elif "cpu wins the game" in output_lower:
        return "CPU wins the game!"
    elif "it's a draw" in output_lower or "its a draw" in output_lower or "draw" in output_lower:
        return "It's a draw!"
    
    return None

def check_game_logic(output, random_values, expected_user_score, expected_cpu_score, expected_winner):
    """Check if game logic is correct"""
    user_score, cpu_score = extract_scores(output)
    winner_message = extract_winner_message(output)
    
    if user_score is None or cpu_score is None:
        return False
    
    # Check scores match
    if user_score != expected_user_score or cpu_score != expected_cpu_score:
        return False
    
    # Check winner message matches
    if winner_message != expected_winner:
        return False
    
    return True

def remove_comments(code):
    """Remove comment lines from code (both # comments and docstrings)"""
    lines = code.split('\n')
    cleaned_lines = []
    in_multiline_string = False
    multiline_delimiter = None
    
    for line in lines:
        stripped = line.strip()
        
        # Skip empty lines
        if not stripped:
            cleaned_lines.append('')
            continue
        
        # Handle multiline strings (docstrings)
        if stripped.startswith('"""') or stripped.startswith("'''"):
            if stripped.count('"""') == 2 or stripped.count("'''") == 2:
                # Single-line docstring, skip it
                continue
            else:
                # Start of multiline string
                in_multiline_string = True
                multiline_delimiter = '"""' if '"""' in stripped else "'''"
                continue
        
        if in_multiline_string:
            # Check if we're ending the multiline string
            if multiline_delimiter in line:
                in_multiline_string = False
                multiline_delimiter = None
            continue
        
        # Skip lines that are only comments
        if stripped.startswith('#'):
            continue
        
        # Remove inline comments (everything after #)
        if '#' in line:
            # Check if # is inside a string
            in_string = False
            string_char = None
            comment_pos = -1
            for i, char in enumerate(line):
                if char in ['"', "'"] and (i == 0 or line[i-1] != '\\'):
                    if not in_string:
                        in_string = True
                        string_char = char
                    elif char == string_char:
                        in_string = False
                        string_char = None
                elif char == '#' and not in_string:
                    comment_pos = i
                    break
            
            if comment_pos >= 0:
                line = line[:comment_pos].rstrip()
        
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)


def analyze_code_quality(code):
    """Analyze code quality for non-running programs"""
    score = 0
    explanation = []
    
    # Remove comments before checking
    code_without_comments = remove_comments(code)
    code_lower = code_without_comments.lower()
    
    # Check for import random
    if 'import random' in code_lower:
        score += 1
        explanation.append("✅ 匯入random函數庫")
    
    # Check for start message
    if 'lucky number battle' in code_lower:
        score += 1
        explanation.append("✅ 輸出開始訊息")
    
    # Check for score initialization
    if 'user_score' in code_lower and 'cpu_score' in code_lower:
        if '= 0' in code_lower or '=0' in code_lower:
            score += 1
            explanation.append("✅ 初始化分數變量")
    
    # Check for for loop
    if 'for' in code_lower and 'range(1, 6)' in code_lower:
        score += 1
        explanation.append("✅ 使用for迴圈")
    
    # Check for random.randint
    if 'random.randint' in code_lower:
        score += 1
        explanation.append("✅ 使用random.randint")
    
    # Check for if-elif-else
    if 'if' in code_lower and 'elif' in code_lower and 'else' in code_lower:
        score += 1
        explanation.append("✅ 使用if-elif-else條件判斷")
    
    return score, explanation

def run_multiple_tests(student_code):
    """Run student code with multiple test cases"""
    test_results = []
    
    for test_case in TEST_CASES:
        run_result = run_student_code(student_code, test_case["random_values"])
        
        test_results.append({
            "random_values": test_case["random_values"],
            "success": run_result["runs"],
            "output": run_result["output"],
            "error": run_result.get("error", ""),
            "expected": test_case,
            "timed_out": bool(run_result.get("timed_out", False)),
        })
    
    return test_results

def evaluate_lucky_number_battle(filepath):
    """Evaluate student's Lucky Number Battle program according to rubrics (total 20 marks)"""
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
    
    # Remove comments before checking code patterns
    code_without_comments = remove_comments(student_code)
    code_lower = code_without_comments.lower()
    
    # Rubric 2: 正確地匯入函數庫 (1分) - import random
    has_import_random = 'import random' in code_lower
    
    if has_import_random:
        total_marks += 1
        feedback.append("✅ 正確地匯入函數庫(import random) (+1)")
    else:
        feedback.append("❌ 未正確匯入函數庫 (+0)")
    
    # Rubric 3: 正確地輸出開始訊息 (1分) - print() start message
    if successful_runs > 0:
        sample_result = next((r for r in test_results if r["success"]), None)
        if sample_result and sample_result["output"].strip():
            if extract_start_message(sample_result["output"]):
                total_marks += 1
                feedback.append("✅ 正確地輸出開始訊息 (+1)")
            else:
                feedback.append("❌ 未正確輸出開始訊息 (+0)")
        else:
            feedback.append("❌ 未正確輸出開始訊息 (+0)")
    else:
        if 'lucky number battle' in code_lower and 'print(' in code_lower:
            total_marks += 0.5
            feedback.append("⚠️ 程式碼有開始訊息但執行失敗 (+0.5)")
        else:
            feedback.append("❌ 未正確輸出開始訊息 (+0)")
    
    # Round up if we have 0.5
    if total_marks % 1 == 0.5:
        total_marks = int(total_marks) + 1
    else:
        total_marks = int(total_marks)
    
    # Rubric 4: 正確地初始化變量 (1分) - user_score = 0, cpu_score = 0
    has_user_score = 'user_score' in code_lower
    has_cpu_score = 'cpu_score' in code_lower
    has_zero_init = ('user_score' in code_lower and '= 0' in code_lower) or ('user_score' in code_lower and '=0' in code_lower)
    has_cpu_zero_init = ('cpu_score' in code_lower and '= 0' in code_lower) or ('cpu_score' in code_lower and '=0' in code_lower)
    
    if has_user_score and has_cpu_score and has_zero_init and has_cpu_zero_init:
        total_marks += 1
        feedback.append("✅ 正確地初始化變量(user_score = 0, cpu_score = 0) (+1)")
    elif has_user_score and has_cpu_score:
        total_marks += 0.5
        feedback.append("⚠️ 初始化變量但值可能不正確 (+0.5)")
    else:
        feedback.append("❌ 未正確初始化變量 (+0)")
    
    # Round up if we have 0.5
    if total_marks % 1 == 0.5:
        total_marks = int(total_marks) + 1
    else:
        total_marks = int(total_marks)
    
    # Rubric 5: 正確地定義迴圈 (3分) - for round_num in range(1, 6):
    has_for_loop = 'for' in code_lower
    has_range_1_6 = 'range(1, 6)' in code_lower or 'range(1,6)' in code_lower
    has_round_num = 'round_num' in code_lower or 'round' in code_lower
    
    if has_for_loop and has_range_1_6 and has_round_num:
        total_marks += 3
        feedback.append("✅ 正確地定義迴圈(for round_num in range(1, 6):) (+3)")
    elif has_for_loop and has_range_1_6:
        total_marks += 2
        feedback.append("⚠️ 使用for迴圈和range(1, 6)但變量命名可能不正確 (+2)")
    elif has_for_loop:
        total_marks += 1
        feedback.append("⚠️ 使用for迴圈但可能未正確使用range(1, 6) (+1)")
    else:
        feedback.append("❌ 未正確定義迴圈 (+0)")
    
    # Rubric 6: 正確地讀取用戶輸入 (2分) - print() Round number, input()
    has_round_print = 'round' in code_lower and 'print(' in code_lower
    has_input = 'input(' in code_lower
    
    if has_round_print and has_input:
        total_marks += 2
        feedback.append("✅ 正確地讀取用戶輸入(輸出Round數目、使用input()) (+2)")
    elif has_round_print or has_input:
        total_marks += 1
        feedback.append("⚠️ 部分使用輸出Round或input() (+1)")
    else:
        feedback.append("❌ 未正確讀取用戶輸入 (+0)")
    
    # Rubric 7: 正確地讀取隨機數字 (2分) - random.randint(1, 10) for both user_num and cpu_num
    has_random_randint = 'random.randint' in code_lower
    has_user_num = 'user_num' in code_lower
    has_cpu_num = 'cpu_num' in code_lower
    has_randint_1_10 = 'randint(1, 10)' in code_lower or 'randint(1,10)' in code_lower
    
    if has_random_randint and has_user_num and has_cpu_num and has_randint_1_10:
        # Check if both are assigned with random.randint
        user_num_assignments = code_lower.count('user_num') >= 2  # Declaration and usage
        cpu_num_assignments = code_lower.count('cpu_num') >= 2
        
        if user_num_assignments and cpu_num_assignments:
            total_marks += 2
            feedback.append("✅ 正確地讀取隨機數字(random.randint(1, 10) for user_num and cpu_num) (+2)")
        else:
            total_marks += 1
            feedback.append("⚠️ 使用random.randint但可能未正確賦值給兩個變量 (+1)")
    elif has_random_randint and has_randint_1_10:
        total_marks += 1
        feedback.append("⚠️ 使用random.randint(1, 10)但變量可能不正確 (+1)")
    else:
        feedback.append("❌ 未正確讀取隨機數字 (+0)")
    
    # Rubric 8: 正確使用若/否則運算 (3分) - if user_num > cpu_num, elif user_num < cpu_num, else
    has_if = 'if' in code_lower
    has_elif = 'elif' in code_lower
    has_else = 'else' in code_lower
    has_user_gt_cpu = ('user_num' in code_lower and 'cpu_num' in code_lower and '>' in code_without_comments)
    has_user_lt_cpu = ('user_num' in code_lower and 'cpu_num' in code_lower and '<' in code_without_comments)
    
    if has_if and has_elif and has_else and has_user_gt_cpu and has_user_lt_cpu:
        total_marks += 3
        feedback.append("✅ 正確使用若/否則運算(if user_num > cpu_num, elif user_num < cpu_num, else) (+3)")
    elif has_if and has_elif and has_else and (has_user_gt_cpu or has_user_lt_cpu):
        total_marks += 2
        feedback.append("⚠️ 使用if-elif-else但條件可能不完整 (+2)")
    elif has_if and has_elif and has_else:
        total_marks += 1
        feedback.append("⚠️ 使用if-elif-else但條件可能不正確 (+1)")
    else:
        feedback.append("❌ 未正確使用條件判斷 (+0)")
    
    # Rubric 9: 正確地判斷 Big Win (1分) - if user_num - cpu_num >= 3:
    # Check for pattern: user_num - cpu_num >= 3
    has_big_win_check = False
    if 'user_num' in code_lower and 'cpu_num' in code_lower:
        # Look for subtraction pattern with >= 3
        pattern = r'user_num\s*-\s*cpu_num\s*>=\s*3'
        if re.search(pattern, code_without_comments, re.IGNORECASE):
            has_big_win_check = True
        # Also check for simpler patterns (all components present)
        elif ('user_num' in code_lower and '-' in code_without_comments and 'cpu_num' in code_lower and 
              '>=' in code_without_comments and '3' in code_without_comments):
            has_big_win_check = True
    
    has_great_win_print = 'great win' in code_lower
    
    if has_big_win_check and has_great_win_print:
        total_marks += 1
        feedback.append("✅ 正確地判斷Big Win(if user_num - cpu_num >= 3:) (+1)")
    elif has_big_win_check:
        total_marks += 0.5
        feedback.append("⚠️ 有Big Win判斷但可能未輸出訊息 (+0.5)")
    else:
        feedback.append("❌ 未正確判斷Big Win (+0)")
    
    # Round up if we have 0.5
    if total_marks % 1 == 0.5:
        total_marks = int(total_marks) + 1
    else:
        total_marks = int(total_marks)
    
    # Rubric 10: 正確輸出 (2分) - if-elif-else for final winner message
    if successful_runs > 0:
        sample_result = next((r for r in test_results if r["success"]), None)
        if sample_result and sample_result["output"].strip():
            winner_message = extract_winner_message(sample_result["output"])
            if winner_message:
                total_marks += 2
                feedback.append("✅ 正確輸出(使用if-elif-else輸出最後結束語句) (+2)")
            else:
                feedback.append("❌ 未正確輸出最後結束語句 (+0)")
        else:
            feedback.append("❌ 未正確輸出最後結束語句 (+0)")
    else:
        # Check code structure for final if-elif-else
        has_final_if = 'if' in code_lower and 'user_score' in code_lower and 'cpu_score' in code_lower
        has_final_elif = 'elif' in code_lower and 'user_score' in code_lower and 'cpu_score' in code_lower
        has_final_else = 'else' in code_lower
        
        if has_final_if and has_final_elif and has_final_else:
            total_marks += 1
            feedback.append("⚠️ 程式碼有最後判斷邏輯但執行失敗 (+1)")
        else:
            feedback.append("❌ 未正確輸出最後結束語句 (+0)")
    
    # Rubric 11: 執行沒有錯誤 (3分) - execution correctness
    if successful_runs > 0:
        accurate_matches = 0
        
        for i, result in enumerate(test_results):
            if result["success"]:
                student_output = result["output"].strip()
                random_values = result["random_values"]
                expected_user_score = result["expected"]["expected_user_score"]
                expected_cpu_score = result["expected"]["expected_cpu_score"]
                expected_winner = result["expected"]["expected_winner"]
                
                # Check if game logic is correct
                if check_game_logic(student_output, random_values, expected_user_score, expected_cpu_score, expected_winner):
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
    if total_marks >= 18:
        overall_feedback = f"✅ 優秀！總分 {total_marks}/20"
    elif total_marks >= 15:
        overall_feedback = f"✅ 良好！總分 {total_marks}/20"
    elif total_marks >= 12:
        overall_feedback = f"⚠️ 基本合格！總分 {total_marks}/20"
    elif total_marks >= 6:
        overall_feedback = f"❌ 需要改進！總分 {total_marks}/20"
    else:
        overall_feedback = f"❌ 不及格！總分 {total_marks}/20"
    
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

        # (20 marks) The python code implements Lucky Number Battle game correctly
        section_description = "Python程式碼實現幸運數字對戰遊戲"
        filepath = row["filepath"]
        section_mark, remarks = evaluate_lucky_number_battle(filepath)

        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark, 20)

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

