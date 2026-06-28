import aia_util as aia_utils
import difflib
import re
from contextlib import redirect_stdout
from unittest.mock import patch, MagicMock
import io

# Test cases for Tic-Tac-Toe game
# Each test case represents moves in sequence (positions 1-9)
TEST_CASES = [
    {
        "input": ["1", "4", "2", "5", "3"],  # X wins horizontally (top row: 1,2,3)
        "expected_winner": "X",
        "description": "X wins horizontally"
    },
    {
        "input": ["1", "2", "3", "5", "4", "8"],  # O wins vertically (middle column: 2,5,8)
        "expected_winner": "O",
        "description": "O wins vertically"
    },
    {
        "input": ["1", "2", "5", "3", "9"],  # X wins diagonally (1,5,9)
        "expected_winner": "X",
        "description": "X wins diagonally"
    },
    {
        "input": ["1", "2", "3", "5", "4", "6", "8", "7", "9"],  # Draw (full board)
        "expected_winner": "draw",
        "description": "Draw game"
    },
    {
        "input": ["3", "2", "5", "1", "7"],  # X wins diagonal (3,5,7)
        "expected_winner": "X",
        "description": "X wins diagonal 3-5-7"
    },
    {
        "input": ["7", "1", "8", "2", "9"],  # O wins horizontally (bottom row: 7,8,9) - Wait, this would be X. Let me fix
        "expected_winner": "X",
        "description": "X wins bottom row"
    }
]

def run_student_code(student_code, test_input, return_dict):
    """Run student code with mocked input"""
    buffer = io.StringIO()
    
    try:
        with redirect_stdout(buffer):
            with patch('builtins.input', side_effect=test_input):
                # Handle exit() calls by catching SystemExit
                try:
                    exec(student_code, {})
                except SystemExit:
                    pass  # exit() is expected when game ends
        output = buffer.getvalue()
        return_dict["runs"] = True
        return_dict["output"] = output
    except Exception as e:
        return_dict["runs"] = False
        return_dict["error"] = str(e)

def calculate_similarity(output1, output2):
    """Calculate similarity between two outputs"""
    return difflib.SequenceMatcher(None, output1.strip(), output2.strip()).ratio()

def extract_winner(output):
    """Extract winner from output"""
    output_lower = output.lower()
    
    # Look for "Player X wins!" or "Player O wins!" or "It's a draw!"
    if 'player x wins' in output_lower or 'x wins' in output_lower:
        return 'X'
    elif 'player o wins' in output_lower or 'o wins' in output_lower:
        return 'O'
    elif 'draw' in output_lower or "it's a draw" in output_lower:
        return 'draw'
    
    return None

def check_board_format(output):
    """Check if board is displayed in correct format"""
    output_lines = output.split('\n')
    
    # Look for board pattern: " 1 | 2 | 3" and "---+---+---"
    has_separators = any('---+' in line or '---' in line for line in output_lines)
    has_pipes = any('|' in line for line in output_lines)
    has_board_positions = any(re.search(r'\s*\d+\s*\|\s*\d+\s*\|\s*\d+', line) for line in output_lines)
    
    return has_separators and has_pipes and has_board_positions

def calculate_game_result(moves, expected_winner):
    """Calculate expected game result from moves"""
    # Create board (1-9 positions)
    board = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    current_player = 'X'
    
    for move_str in moves:
        move = int(move_str) - 1  # Convert to 0-indexed
        
        if 0 <= move < 9 and board[move] in '123456789':
            board[move] = current_player
            
            # Check for win
            win_conditions = [
                [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
                [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
                [0, 4, 8], [2, 4, 6]  # Diagonals
            ]
            
            for condition in win_conditions:
                if board[condition[0]] == board[condition[1]] == board[condition[2]]:
                    return current_player
            
            # Switch player
            current_player = 'O' if current_player == 'X' else 'X'
    
    # No winner, check if draw
    if all(pos in 'XO' for pos in board):
        return 'draw'
    
    return None  # Game not finished

def analyze_code_quality(code):
    """Analyze code quality for non-running programs"""
    score = 0
    explanation = []
    
    code_lower = code.lower()
    
    # Check for print function
    print_count = code.count('print(')
    if print_count >= 5:
        score += 1
        explanation.append("✅ 使用多個print函數顯示棋盤")
    elif print_count >= 1:
        score += 1
        explanation.append("✅ 使用print函數")
    
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
    
    # Check for while loop (for input validation)
    if 'while' in code_lower:
        score += 1
        explanation.append("✅ 使用while循環")
    
    # Check for if-elif-else
    if 'if' in code_lower and 'elif' in code_lower:
        score += 1
        explanation.append("✅ 使用if-elif條件判斷")
    
    # Check for turn switching logic
    if ('turn' in code_lower or 'player' in code_lower) and ('x' in code_lower or 'o' in code_lower):
        score += 1
        explanation.append("✅ 實現玩家輪換")
    
    # Check for win condition checking
    if ('win' in code_lower or '==' in code) and ('or' in code_lower or 'and' in code_lower):
        score += 1
        explanation.append("✅ 檢查獲勝條件")
    
    return score, explanation

def run_multiple_tests(student_code):
    """Run student code with multiple test cases"""
    test_results = []
    
    for test_case in TEST_CASES:
        buffer = io.StringIO()
        
        try:
            with redirect_stdout(buffer):
                with patch('builtins.input', side_effect=test_case["input"]):
                    try:
                        exec(student_code, {})
                    except SystemExit:
                        pass  # exit() is expected
            test_results.append({
                "input": test_case["input"],
                "success": True,
                "output": buffer.getvalue(),
                "error": "",
                "expected_winner": test_case["expected_winner"]
            })
        except Exception as e:
            test_results.append({
                "input": test_case["input"],
                "success": False,
                "output": buffer.getvalue(),
                "error": str(e),
                "expected_winner": test_case["expected_winner"]
            })
    
    return test_results

def evaluate_tic_tac_toe_program(filepath):
    """Evaluate student's Tic-Tac-Toe program with specific criteria (2 marks each)"""
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
    
    # 1. Check for board display format (2 marks)
    code_lower = student_code.lower()
    if successful_runs > 0:
        sample_result = next((r for r in test_results if r["success"]), None)
        if sample_result and sample_result["output"].strip():
            output = sample_result["output"]
            
            if check_board_format(output):
                total_marks += 2
                feedback.append("✅ 棋盤顯示格式正確(包含分隔符和位置) (+2)")
            elif '|' in output and '---' in output:
                total_marks += 1
                feedback.append("⚠️ 棋盤顯示格式部分正確 (+1)")
            else:
                feedback.append("❌ 棋盤顯示格式不正確 (+0)")
        else:
            feedback.append("❌ 棋盤顯示格式不正確 (+0)")
    else:
        # Check static analysis
        if 'print(' in code_lower and '|' in student_code:
            total_marks += 1
            feedback.append("⚠️ 程式碼有棋盤輸出邏輯但執行失敗 (+1)")
        else:
            feedback.append("❌ 棋盤顯示格式不正確 (+0)")
    
    # 2. Check for for loop with range and turn switching (2 marks)
    has_for = 'for' in code_lower
    has_range = 'range(' in code_lower
    has_turn_switch = (('turn' in code_lower or 'player' in code_lower) and 
                       ('x' in code_lower and 'o' in code_lower))
    
    if has_for and has_range and has_turn_switch:
        total_marks += 2
        feedback.append("✅ 正確使用for循環、range和玩家輪換 (+2)")
    elif has_for and has_range:
        total_marks += 1
        feedback.append("⚠️ 部分使用for循環和range但缺少玩家輪換 (+1)")
    elif has_for:
        total_marks += 1
        feedback.append("⚠️ 使用for循環但缺少range或玩家輪換 (+1)")
    else:
        feedback.append("❌ 未使用for循環和range (+0)")
    
    # 3. Check for input validation and while loop (2 marks)
    has_input = 'input(' in code_lower
    has_while = 'while' in code_lower
    has_validation = ('isdigit' in code_lower or 'int(' in code_lower) and ('invalid' in code_lower or 'already' in code_lower or 'taken' in code_lower)
    
    if has_input and has_while and has_validation:
        total_marks += 2
        feedback.append("✅ 正確使用input、while循環和輸入驗證 (+2)")
    elif has_input and has_while:
        total_marks += 1
        feedback.append("⚠️ 部分使用input和while循環但缺少驗證 (+1)")
    elif has_input:
        total_marks += 1
        feedback.append("⚠️ 使用input但缺少while循環或驗證 (+1)")
    else:
        feedback.append("❌ 未正確使用input和驗證 (+0)")
    
    # 4. Check for win condition checking and if-elif-else (2 marks)
    has_if_elif = 'if' in code_lower and 'elif' in code_lower
    has_win_check = ('win' in code_lower or '==' in student_code) and ('or' in code_lower or 'and' in code_lower)
    has_win_conditions = code_lower.count('==') >= 3  # Should have multiple win condition checks
    
    if has_if_elif and has_win_check and has_win_conditions:
        total_marks += 2
        feedback.append("✅ 正確使用if-elif條件判斷和獲勝條件檢查 (+2)")
    elif has_if_elif and has_win_check:
        total_marks += 1
        feedback.append("⚠️ 部分使用條件判斷和獲勝條件檢查 (+1)")
    elif has_if_elif:
        total_marks += 1
        feedback.append("⚠️ 使用條件判斷但缺少獲勝條件檢查 (+1)")
    else:
        feedback.append("❌ 未使用必要的條件判斷和獲勝條件檢查 (+0)")
    
    # 5. Check for results closely matching model answers (2 marks)
    if successful_runs > 0:
        accurate_game_matches = 0
        
        for i, result in enumerate(test_results):
            if result["success"]:
                student_output = result["output"].strip()
                moves = result["input"]
                expected_winner = result["expected_winner"]
                
                # Extract winner from output
                actual_winner = extract_winner(student_output)
                
                # Check if winner matches expected
                if actual_winner and actual_winner.upper() == expected_winner.upper():
                    accurate_game_matches += 1
                elif expected_winner == 'draw' and actual_winner == 'draw':
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

        # (10 marks) The python code implements Tic-Tac-Toe game correctly
        section_description = "Python程式碼實現井字棋遊戲"
        filepath = row["filepath"]
        section_mark, remarks = evaluate_tic_tac_toe_program(filepath)

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

