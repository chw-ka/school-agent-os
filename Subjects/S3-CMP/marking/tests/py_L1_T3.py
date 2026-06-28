import aia_util as aia_utils
import difflib
from contextlib import redirect_stdout
from unittest.mock import patch, MagicMock
import io

def run_ascii_art(student_code):
    """Run student code using direct exec() - fast version"""
    buffer = io.StringIO()

    try:
        with redirect_stdout(buffer):
            exec(student_code, {})
        output = buffer.getvalue()
        return {
            "runs": True,
            "output": output,
            "error": ""
        }
    except Exception as e:
        return {
            "runs": False,
            "output": buffer.getvalue(),
            "error": str(e)
        }

def analyze_ascii_quality(output):
    """Analyze the quality of ASCII art output"""
    score = 0
    explanation = []
    
    if len(output.strip()) == 0:
        return 0, ["❌ 沒有輸出內容"]
    
    lines = output.strip().split('\n')
    
    # Check for multi-line structure
    if len(lines) >= 3:
        score += 2
        explanation.append("✅ 多行ASCII藝術結構 (+2)")
    elif len(lines) >= 2:
        score += 1
        explanation.append("✅ 基本多行結構 (+1)")
    
    # Check for ASCII art characters
    ascii_chars = ['*', '#', '@', '%', '&', '/', '\\', '|', '-', '_', '=', '+', '~', '^', '<', '>', 'v', 'V', 'o', 'O', 'x', 'X']
    found_chars = [char for char in ascii_chars if char in output]
    if len(found_chars) >= 5:
        score += 2
        explanation.append(f"✅ 豐富的ASCII字符使用 (+2)")
    elif len(found_chars) >= 2:
        score += 1
        explanation.append(f"✅ 使用ASCII字符: {', '.join(found_chars[:5])} (+1)")
    
    # Check for pattern complexity
    total_chars = len(output.replace('\n', ''))
    if total_chars >= 50:
        score += 2
        explanation.append("✅ 複雜的圖案設計 (+2)")
    elif total_chars >= 20:
        score += 1
        explanation.append("✅ 適中的圖案內容 (+1)")
    
    # Check for artistic elements
    if any(char in output for char in ['(', ')', '{', '}', '[', ']']):
        score += 1
        explanation.append("✅ 使用藝術性符號 (+1)")
    
    # Check for symmetry or structure
    if len(lines) >= 3:
        # Check if middle lines are different from top/bottom
        middle_line = len(lines) // 2
        if middle_line > 0 and middle_line < len(lines):
            if lines[middle_line] != lines[0] and lines[middle_line] != lines[-1]:
                score += 1
                explanation.append("✅ 圖案具有結構層次 (+1)")
    
    # Check for spacing and alignment
    max_length = max(len(line) for line in lines if line.strip())
    if max_length >= 10:
        score += 1
        explanation.append("✅ 適當的圖案寬度 (+1)")
    
    return min(score, 10), explanation

def analyze_code_quality(code):
    """Analyze code quality for non-running programs"""
    score = 0
    explanation = []
    
    code_lower = code.lower()
    
    # Check for print function
    if "print(" in code_lower:
        score += 1
        explanation.append("✅ 使用print函數")
    
    # Check for string output
    if '"""' in code or "'''" in code or ('"' in code and "'" in code):
        score += 1
        explanation.append("✅ 使用多行字串")
    
    # Check for ASCII art related symbols
    ascii_symbols = ['*', '#', '@', '%', '/', '\\', '|', '-', '_', '=', '+', '~', '^', '<', '>', 'v', 'V', 'o', 'O', 'x', 'X']
    found_symbols = [symbol for symbol in ascii_symbols if symbol in code]
    if found_symbols:
        score += 1
        explanation.append(f"✅ 包含ASCII字符: {', '.join(found_symbols[:5])}")
    
    # Check for proper structure (multiple lines)
    if '\n' in code and code.count('\n') >= 2:
        score += 1
        explanation.append("✅ 多行結構")
    
    # Check for escape sequence issues
    if '\\_' in code or '\\/' in code or '\\(' in code or '\\)' in code or '\\|' in code:
        explanation.append("⚠️ 發現轉義字符問題：在字串中，反斜線 '\\' 需要寫成 '\\\\'")
    
    return score, explanation

def evaluate_ascii_art(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            student_code = f.read()
    except:
        return 0, "❌ 無法讀取程式碼"

    # Try to run the code using fast direct exec()
    result = run_ascii_art(student_code)

    # Code ran successfully
    if result.get("runs"):
        student_output = result.get("output", "")
        
        # Analyze ASCII art quality
        score, explanation = analyze_ascii_quality(student_output)
        
        # Add escape sequence warning if detected in code
        if '\\_' in student_code or '\\/' in student_code or '\\(' in student_code or '\\)' in student_code or '\\|' in student_code:
            explanation.append("💡 提示：在字串中使用反斜線 '\\' 時，需要寫成 '\\\\' 來避免轉義字符錯誤")
        
        # Add grading system explanation
        grading_info = "📋 評分標準：多行結構(2分) + ASCII字符使用(2分) + 圖案複雜度(2分) + 藝術元素(1分) + 結構層次(1分) + 圖案寬度(1分) = 最高10分"
        explanation.insert(0, grading_info)
        
        if score >= 8:
            return 10, f"✅ 優秀的ASCII藝術作品！ (+{score}) | " + " | ".join(explanation)
        elif score >= 6:
            return 9, f"✅ 很好的ASCII藝術！ (+{score}) | " + " | ".join(explanation)
        elif score >= 4:
            return 8, f"✅ 不錯的ASCII藝術 (+{score}) | " + " | ".join(explanation)
        elif score >= 2:
            return 7, f"✅ 基本的ASCII藝術 (+{score}) | " + " | ".join(explanation)
        elif score >= 1:
            return 6, f"✅ 簡單的ASCII輸出 (+{score}) | " + " | ".join(explanation)
        elif len(student_output.strip()) == 0:
            return 2, "⚠️ 程式可執行但無輸出，只有基本提交分數 (+2)"
        else:
            return 5, f"⚠️ 有輸出但ASCII藝術質量較低 (+{score}) | " + " | ".join(explanation)
    else:
        # Code didn't run - analyze static quality
        score, explanation = analyze_code_quality(student_code)
        error_msg = result.get("error", "未知錯誤")
        
        # Check for specific escape sequence errors
        if "invalid escape sequence" in error_msg.lower() or "syntaxwarning" in error_msg.lower():
            explanation.append("💡 提示：在字串中使用反斜線 '\\' 時，需要寫成 '\\\\' 來避免轉義字符錯誤")
        
        # Add grading system explanation for failed cases
        grading_info = "📋 評分標準：程式碼結構分析 - print函數(1分) + 多行字串(1分) + ASCII字符(1分) + 多行結構(1分) = 最高4分"
        explanation.insert(0, grading_info)
        
        if score >= 3:
            return 4, f"❌ 程式執行失敗，但程式碼結構良好 (+{score}) | " + " | ".join(explanation)
        elif score >= 1:
            return 3, f"❌ 程式執行失敗，程式碼有基本結構 (+{score}) | " + " | ".join(explanation)
        else:
            return 2, f"❌ 程式執行失敗，程式碼結構不足 (+{score}) | 錯誤: {error_msg} | " + " | ".join(explanation)


def test(submissions):
    for idx, row in submissions.iterrows():
        print("=========================================")
        print(submissions.loc[idx, "class"], submissions.loc[idx, "classnumber"])
        print("=========================================")
        submissions.loc[idx, "marks"] = 0
        submissions.loc[idx, "comments"] = ""

        # (2 marks) No marks if no file found
        if row["filepath"] is None:
            submissions.loc[idx, "marks"] = 0
            submissions.loc[idx, "comments"] = "No file found in the submission\n"
            continue

        # (10 marks) The python code creates ASCII art
        section_description = "Python程式碼輸出ASCII藝術"
        filepath = row["filepath"]
        section_mark, remarks = evaluate_ascii_art(filepath)

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
