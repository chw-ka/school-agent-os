import aia_util as aia_utils
import difflib
from contextlib import redirect_stdout
from unittest.mock import patch, MagicMock
import io

# Test cases with different inputs and expected outputs
TEST_CASES = [
    {
        "input": "Warren",
        "expected": "Your name: Mr. Chan: Hi, Warren\nWarren: Hi, Mr. Chan\nMr. Chan: Code on, Warren"
    },
    {
        "input": "Alice",
        "expected": "Your name: Mr. Chan: Hi, Alice\nAlice: Hi, Mr. Chan\nMr. Chan: Code on, Alice"
    },
    {
        "input": "Bob",
        "expected": "Your name: Mr. Chan: Hi, Bob\nBob: Hi, Mr. Chan\nMr. Chan: Code on, Bob"
    },
    {
        "input": "Carol",
        "expected": "Your name: Mr. Chan: Hi, Carol\nCarol: Hi, Mr. Chan\nMr. Chan: Code on, Carol"
    },
    {
        "input": "David",
        "expected": "Your name: Mr. Chan: Hi, David\nDavid: Hi, Mr. Chan\nMr. Chan: Code on, David"
    },
    {
        "input": "Emma",
        "expected": "Your name: Mr. Chan: Hi, Emma\nEmma: Hi, Mr. Chan\nMr. Chan: Code on, Emma"
    },
    {
        "input": "Frank",
        "expected": "Your name: Mr. Chan: Hi, Frank\nFrank: Hi, Mr. Chan\nMr. Chan: Code on, Frank"
    },
    {
        "input": "Grace",
        "expected": "Your name: Mr. Chan: Hi, Grace\nGrace: Hi, Mr. Chan\nMr. Chan: Code on, Grace"
    },
    {
        "input": "Henry",
        "expected": "Your name: Mr. Chan: Hi, Henry\nHenry: Hi, Mr. Chan\nMr. Chan: Code on, Henry"
    },
    {
        "input": "Ivy",
        "expected": "Your name: Mr. Chan: Hi, Ivy\nIvy: Hi, Mr. Chan\nMr. Chan: Code on, Ivy"
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
    
    # Check for string concatenation or formatting
    if '+' in code or 'f"' in code or '.format(' in code:
        score += 1
        explanation.append("✅ 使用字串連接或格式化")
    
    # Check for variable assignment
    if '=' in code and 'input' in code_lower:
        score += 1
        explanation.append("✅ 使用變數儲存輸入")
    
    # Check for multiple print statements
    if code.count('print(') >= 3:
        score += 1
        explanation.append("✅ 使用多個print語句")
    
    return score, explanation

def run_multiple_tests(student_code):
    """Run student code with multiple test cases using fast direct exec()"""
    test_results = []
    
    for test_case in TEST_CASES:
        buffer = io.StringIO()
        
        try:
            with redirect_stdout(buffer):
                with patch('builtins.input', side_effect=[test_case["input"]]):
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

def evaluate_input_output(filepath):
    """Evaluate student's input/output program with multiple test cases"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            student_code = f.read()
    except:
        return 0, "❌ 無法讀取程式碼"

    # Run multiple test cases
    test_results = run_multiple_tests(student_code)
    
    # Count successful runs
    successful_runs = sum(1 for result in test_results if result["success"])
    
    if successful_runs == 0:
        # No successful runs - analyze static code quality
        score, explanation = analyze_code_quality(student_code)
        if score >= 3:
            return 4, f"❌ 所有測試失敗，但程式碼結構良好 (+{score}) | " + " | ".join(explanation)
        elif score >= 2:
            return 3, f"❌ 所有測試失敗，程式碼有基本結構 (+{score}) | " + " | ".join(explanation)
        else:
            return 2, f"❌ 所有測試失敗，程式碼結構不足 (+{score}) | " + " | ".join(explanation)
    
    # Calculate scores based on test results with multiple degrees of partial matching
    perfect_matches = 0
    excellent_matches = 0  # 80-89% similarity
    good_matches = 0       # 70-79% similarity
    fair_matches = 0       # 60-69% similarity
    poor_matches = 0       # 50-59% similarity
    total_outputs = 0
    
    for i, result in enumerate(test_results):
        if result["success"]:
            student_output = result["output"].strip()
            expected_output = TEST_CASES[i]["expected"].strip()
            
            # Check if output has the right number of lines (should be 3 print statements)
            output_lines = [line.strip() for line in student_output.split('\n') if line.strip()]
            expected_lines = [line.strip() for line in expected_output.split('\n') if line.strip()]
            
            if len(output_lines) == len(expected_lines):
                total_outputs += 1
                # Calculate similarity
                similarity = calculate_similarity(student_output, expected_output)
                if similarity >= 0.9:
                    perfect_matches += 1
                elif similarity >= 0.8:
                    excellent_matches += 1
                elif similarity >= 0.7:
                    good_matches += 1
                elif similarity >= 0.6:
                    fair_matches += 1
                elif similarity >= 0.5:
                    poor_matches += 1
    
    # Calculate total quality score based on weighted matches
    total_quality_score = (perfect_matches * 10 + 
                          excellent_matches * 9 + 
                          good_matches * 8 + 
                          fair_matches * 6 + 
                          poor_matches * 4)
    
    # Calculate average quality per successful test
    avg_quality = total_quality_score / max(successful_runs, 1)
    
    # More lenient grading logic - focus on successful runs rather than perfect matches
    total_matches = perfect_matches + excellent_matches + good_matches + fair_matches + poor_matches
    
    if successful_runs == len(TEST_CASES) and perfect_matches >= len(TEST_CASES) - 1:
        return 10, f"✅ 完美！{successful_runs}/{len(TEST_CASES)}個測試通過，{perfect_matches}個完美匹配 (+10)"
    elif successful_runs == len(TEST_CASES) and total_matches >= len(TEST_CASES) - 1:
        return 9, f"✅ 非常好！{successful_runs}/{len(TEST_CASES)}個測試通過，{perfect_matches}個完美匹配，{excellent_matches}個優秀匹配 (+9)"
    elif successful_runs >= len(TEST_CASES) - 1 and total_matches >= len(TEST_CASES) - 1:
        return 8, f"✅ 很好！{successful_runs}/{len(TEST_CASES)}個測試通過，{total_matches}個有效匹配 (+8)"
    elif successful_runs >= len(TEST_CASES) - 1 and total_matches >= len(TEST_CASES) - 2:
        return 7, f"✅ 不錯！{successful_runs}/{len(TEST_CASES)}個測試通過，{total_matches}個有效匹配 (+7)"
    elif successful_runs >= len(TEST_CASES) - 3 and total_matches >= len(TEST_CASES) - 4:
        return 6, f"✅ 基本正確！{successful_runs}/{len(TEST_CASES)}個測試通過，{total_matches}個有效匹配 (+6)"
    elif successful_runs >= len(TEST_CASES) // 2:
        return 5, f"✅ 部分正確！{successful_runs}/{len(TEST_CASES)}個測試通過，需要改進格式 (+5)"
    elif successful_runs > 0:
        return 4, f"⚠️ 少數測試通過！{successful_runs}/{len(TEST_CASES)}個測試通過，需要檢查程式邏輯 (+4)"
    else:
        # Fallback: check if code has good structure even if tests failed
        code_quality_score, explanation = analyze_code_quality(student_code)
        if code_quality_score >= 4:
            return 6, f"✅ 程式結構良好但執行有問題，{code_quality_score}個結構要素正確 (+6) | " + " | ".join(explanation)
        elif code_quality_score >= 2:
            return 5, f"✅ 程式有基本結構，{code_quality_score}個結構要素正確 (+5) | " + " | ".join(explanation)
        else:
            return 2, f"⚠️ 程式結構不足，只有基本提交分數 (+2)"

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

        # (10 marks) The python code handles input/output correctly
        section_description = "Python程式碼處理輸入輸出"
        filepath = row["filepath"]
        section_mark, remarks = evaluate_input_output(filepath)

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
