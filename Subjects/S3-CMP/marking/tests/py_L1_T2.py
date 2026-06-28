import aia_util as aia_utils
import difflib
from contextlib import redirect_stdout
from unittest.mock import patch, MagicMock
import io

# Model answer for cat pattern
MODEL_CAT = """ /\\_/\\
( o.o )
 > ^ <"""

def run_cat_pattern(student_code):
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

def calculate_similarity(student_output, model_output):
    """Calculate similarity between student output and model answer"""
    # Normalize outputs for comparison
    student_norm = student_output.strip()
    model_norm = model_output.strip()
    
    # Exact match
    if student_norm == model_norm:
        return 1.0
    
    # Use difflib to calculate similarity ratio
    similarity = difflib.SequenceMatcher(None, student_norm, model_norm).ratio()
    return similarity

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
    
    # Check for cat-related symbols
    cat_symbols = ['/', '\\', '(', ')', 'o', '^', '_', '>', '<']
    found_symbols = [symbol for symbol in cat_symbols if symbol in code]
    if found_symbols:
        score += 1
        explanation.append(f"✅ 包含貓咪符號: {', '.join(found_symbols)}")
    
    # Check for proper structure (multiple lines)
    if '\n' in code and code.count('\n') >= 2:
        score += 1
        explanation.append("✅ 多行結構")
    
    # Check for escape sequence issues
    if '\\_' in code or '\\/' in code or '\\(' in code or '\\)' in code:
        explanation.append("⚠️ 發現轉義字符問題：在字串中，反斜線 '\\' 需要寫成 '\\\\'")
    
    return score, explanation

def evaluate_cat_pattern(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            student_code = f.read()
    except:
        return 0, "❌ 無法讀取程式碼"

    # Try to run the code using fast direct exec()
    result = run_cat_pattern(student_code)

    # Code ran successfully
    if result.get("runs"):
        student_output = result.get("output", "")
        
        # Calculate similarity with model answer
        similarity = calculate_similarity(student_output, MODEL_CAT)
        
        if similarity >= 0.95:  # Almost identical
            return 10, "✅ 完美！輸出與標準答案幾乎相同 (+10)"
        elif similarity >= 0.8:  # Very similar
            return 9, f"✅ 非常好！輸出非常接近標準答案 (相似度: {similarity:.2f}) (+9)"
        elif similarity >= 0.6:  # Similar
            return 8, f"✅ 很好！輸出與標準答案相似 (相似度: {similarity:.2f}) (+8)"
        elif similarity >= 0.4:  # Somewhat similar
            return 7, f"✅ 不錯！輸出有一定相似度 (相似度: {similarity:.2f}) (+7)"
        elif similarity >= 0.2:  # Some similarity
            return 6, f"✅ 可以！輸出有部分相似 (相似度: {similarity:.2f}) (+6)"
        elif len(student_output.strip()) > 0:  # Has output but not similar
            # Check if it's still a reasonable cat pattern attempt
            lines = student_output.strip().split('\n')
            if len(lines) >= 3:
                return 5, f"✅ 有輸出但與標準答案差異較大 (相似度: {similarity:.2f}) (+5)"
            else:
                return 4, f"⚠️ 有輸出但結構簡單 (相似度: {similarity:.2f}) (+4)"
        else:
            return 2, "⚠️ 程式可執行但無輸出，只有基本提交分數 (+2)"
    else:
        # Code didn't run - analyze static quality
        score, explanation = analyze_code_quality(student_code)
        error_msg = result.get("error", "未知錯誤")
        
        # Check for specific escape sequence errors
        if "invalid escape sequence" in error_msg.lower() or "syntaxwarning" in error_msg.lower():
            explanation.append("💡 提示：在字串中使用反斜線 '\\' 時，需要寫成 '\\\\' 來避免轉義字符錯誤")
        
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

        # (10 marks) The python code creates a cat pattern
        section_description = "Python程式碼輸出貓咪圖案"
        filepath = row["filepath"]
        section_mark, remarks = evaluate_cat_pattern(filepath)

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
