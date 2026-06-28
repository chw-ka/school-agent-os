import pandas as pd
import os
import json
import subprocess
import sys
import re
import shutil
import tempfile
from pathlib import Path
import aia_util as aia_utils

TASK_INFO_DIR = Path(__file__).resolve().parents[2] / "task_info" / "S3_下學期實習試_任務三"

RUBRIC = [
    {"key": "mark1", "name": "Prompt Quality & Quantity", "max_marks": 4},
    {"key": "mark2", "name": "Code Structure & Functionality", "max_marks": 6},
    {"key": "mark3", "name": "Output Format", "max_marks": 4},
    {"key": "mark4", "name": "Correctness & Testing", "max_marks": 4},
    {"key": "mark5", "name": "Program Executability", "max_marks": 2},
]

# Sample data matching sales_report_sample.txt ($168 total)
SAMPLE_SALES_168 = [
    {"item": "汽水", "price": 12, "qty": 3, "class": "3A"},
    {"item": "汽水", "price": 12, "qty": 2, "class": "3B"},
    {"item": "汽水", "price": 12, "qty": 1, "class": "3C"},
    {"item": "薯片", "price": 10, "qty": 2, "class": "3A"},
    {"item": "薯片", "price": 10, "qty": 1, "class": "3C"},
    {"item": "朱古力", "price": 8, "qty": 3, "class": "3A"},
    {"item": "朱古力", "price": 8, "qty": 1, "class": "3B"},
    {"item": "糖果", "price": 5, "qty": 4, "class": "3A"},
    {"item": "糖果", "price": 5, "qty": 2, "class": "3C"},
]

EXPECTED_SAMPLE_REPORT = (
    "🧾🍟 小食部銷售報告 🍟🧾\n\n"
    "💰 總收入：$168\n"
    "🏆 最賺錢食品：汽水（$72）\n\n"
    "📊 各班別總收入：\n"
    "- 3A: $78\n"
    "- 3B: $24\n"
    "- 3C: $66"
)


def _read_text(path):
    for encoding in ("utf-8", "latin-1"):
        try:
            with open(path, encoding=encoding) as f:
                return f.read()
        except Exception:
            continue
    return ""


PROMPT_TEMPLATE_TEXT = _read_text(TASK_INFO_DIR / "gemini_prompts.txt")


def _normalize_prompt_text(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def _extract_prompt_bodies(content: str) -> list[str]:
    bodies = []
    matches = list(re.finditer(r"提示\s*[1-9][：:]\s*", content))
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        bodies.append(content[start:end].strip())
    return bodies


def _count_substantive_prompts(content: str, min_chars: int = 8) -> int:
    return sum(1 for body in _extract_prompt_bodies(content) if len(body) >= min_chars)


def _is_blank_prompt_template(content: str) -> bool:
    if not content.strip():
        return True
    if PROMPT_TEMPLATE_TEXT and _normalize_prompt_text(content) == _normalize_prompt_text(PROMPT_TEMPLATE_TEXT):
        return True
    return _count_substantive_prompts(content) == 0


def _resolve_task3_txt_files(txt_files: list[str]) -> tuple[str | None, str | None]:
    prompts_file = None
    report_file = None
    unmatched = []

    for path in txt_files:
        content = _read_text(path)
        lower = content.lower()
        if prompts_file is None and (
            "把你在 gemini" in content or "提示" in content or "gemini" in lower or "prompt" in lower
        ):
            prompts_file = path
        elif report_file is None and (
            "🧾" in content or "小食部銷售報告" in content or "總收入" in content
        ):
            report_file = path
        else:
            unmatched.append(path)

    for path in unmatched:
        if not prompts_file:
            prompts_file = path
        elif not report_file:
            report_file = path

    return prompts_file, report_file


def prepare_student_code(code: str) -> str:
    """Use Gemini-completed code below the template stub when present."""
    if "raise NotImplementedError" not in code:
        return code
    match = re.search(r"raise NotImplementedError[^\n]*\n([\s\S]+)", code)
    if not match:
        return code
    remainder = match.group(1).strip()
    if len(remainder) < 80:
        return code
    return remainder


def normalize_report(text: str) -> str:
    text = text.replace("\r\n", "\n").strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def compare_report_to_sample(report_content: str) -> int:
    """Return 0-2 based on how closely a report matches the sample output."""
    if not report_content:
        return 0
    actual = normalize_report(report_content)
    expected = normalize_report(EXPECTED_SAMPLE_REPORT)
    if actual == expected:
        return 2
    checks = [
        r"🧾🍟.*小食部銷售報告",
        r"💰.*總收入.*\$168",
        r"🏆.*最賺錢食品.*汽水.*\$72",
        r"📊.*各班別總收入",
        r"3A.*\$78",
        r"3B.*\$24",
        r"3C.*\$66",
    ]
    hits = sum(1 for pattern in checks if re.search(pattern, actual))
    if hits >= 6:
        return 2
    if hits >= 4:
        return 1
    return 0


def load_actual_sales_data():
    actual_path = TASK_INFO_DIR / "canteen_sales.json"
    if actual_path.exists():
        with actual_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    return SAMPLE_SALES_168


def run_student_script(task3_file, sales_data, sales_filename="canteen_sales.json"):
    """Run student code in an isolated temp directory."""
    temp_dir = tempfile.mkdtemp()
    try:
        code = prepare_student_code(_read_text(task3_file))
        with open(os.path.join(temp_dir, "task3_test.py"), "w", encoding="utf-8") as f:
            f.write(code)

        for name, data in (
            ("canteen_sales_sample.json", SAMPLE_SALES_168),
            ("canteen_sales.json", sales_data),
        ):
            with open(os.path.join(temp_dir, name), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)

        with open(os.path.join(temp_dir, "sales_report_sample.txt"), "w", encoding="utf-8") as f:
            f.write(EXPECTED_SAMPLE_REPORT + "\n")

        result = subprocess.run(
            [sys.executable, "task3_test.py"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            cwd=temp_dir,
        )
        output = ""
        report_path = os.path.join(temp_dir, "sales_report.txt")
        report_written = os.path.exists(report_path)
        if report_written:
            output = _read_text(report_path)
        elif result.stdout:
            output = result.stdout
        return {
            "returncode": result.returncode,
            "output": output,
            "stderr": result.stderr or "",
            "report_written": report_written,
        }
    except subprocess.TimeoutExpired:
        return {"returncode": -1, "output": "", "stderr": "timeout", "report_written": False}
    except Exception as exc:
        return {"returncode": -1, "output": "", "stderr": str(exc), "report_written": False}
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def check_sample_total(task3_file):
    run = run_student_script(task3_file, SAMPLE_SALES_168)
    output = run["output"]
    if re.search(r"\$168", output):
        return 2
    if re.search(r"\$\d+", output):
        return 1
    return 0


def check_most_profitable(task3_file):
    run = run_student_script(task3_file, SAMPLE_SALES_168)
    output = run["output"]
    if re.search(r"汽水.*\$72", output):
        return 2
    if re.search(r"汽水", output) and re.search(r"\$\d+", output):
        return 1
    return 0


def check_class_revenue(task3_file):
    run = run_student_script(task3_file, SAMPLE_SALES_168)
    output = run["output"]
    if re.search(r"3A.*\$78", output) and re.search(r"3B.*\$24", output) and re.search(r"3C.*\$66", output):
        return 2
    if re.search(r"3A.*\$", output) and re.search(r"3B.*\$", output):
        return 1
    return 0


def check_sample_output_match(task3_file, report_file=None):
    submitted_score = compare_report_to_sample(_read_text(report_file)) if report_file else 0
    run = run_student_script(task3_file, SAMPLE_SALES_168)
    run_score = compare_report_to_sample(run["output"])
    return max(submitted_score, run_score)


def check_actual_output(task3_file):
    actual_data = load_actual_sales_data()
    run = run_student_script(task3_file, actual_data)
    output = run["output"]
    if not output.strip():
        return 0

    total = sum(entry["price"] * entry["qty"] for entry in actual_data)
    item_totals = {}
    class_totals = {}
    for entry in actual_data:
        amount = entry["price"] * entry["qty"]
        item_totals[entry["item"]] = item_totals.get(entry["item"], 0) + amount
        class_totals[entry["class"]] = class_totals.get(entry["class"], 0) + amount
    best_item, best_total = max(item_totals.items(), key=lambda x: x[1])

    checks = 0
    if re.search(rf"\${total}\b", output):
        checks += 1
    if re.search(rf"{re.escape(best_item)}.*\${best_total}", output):
        checks += 1
    class_hits = sum(1 for cls, amount in class_totals.items() if re.search(rf"{cls}.*\${amount}", output))
    if class_hits >= max(1, len(class_totals) // 2):
        checks += 1

    if checks >= 3:
        return 2
    if checks >= 1:
        return 1
    return 0


def check_partial_execution(task3_file, report_file=None):
    if report_file and os.path.exists(report_file):
        content = normalize_report(_read_text(report_file))
        if len(content) > 50:
            return 2 if compare_report_to_sample(content) >= 1 else 1

    run = run_student_script(task3_file, SAMPLE_SALES_168[:1])
    output = normalize_report(run["output"])
    if len(output) > 20:
        return 2
    if output:
        return 1
    return 0


def check_executability(task3_file):
    raw_code = _read_text(task3_file)
    try:
        compile(raw_code, task3_file, "exec")
        syntax_ok = True
    except SyntaxError:
        return False, False

    prepared = prepare_student_code(raw_code)
    try:
        compile(prepared, task3_file, "exec")
    except SyntaxError:
        return False, False

    run = run_student_script(task3_file, SAMPLE_SALES_168[:1])
    runtime_ok = run["returncode"] == 0 and run.get("report_written", False)
    return syntax_ok, runtime_ok


def is_direct_copy(task3_file):
    code = prepare_student_code(_read_text(task3_file))
    if len(code) < 100:
        return True
    meaningful_lines = [line.strip() for line in code.splitlines() if line.strip() and not line.strip().startswith("#")]
    return len(meaningful_lines) < 10


def test(submissions: pd.DataFrame) -> pd.DataFrame:
    max_marks_1 = 4
    max_marks_2 = 6
    max_marks_3 = 4
    max_marks_4 = 4
    max_marks_5 = 2
    total_max = 20

    submissions['mark1'] = 0
    submissions['mark2'] = 0
    submissions['mark3'] = 0
    submissions['mark4'] = 0
    submissions['mark5'] = 0
    submissions['marks'] = 0
    submissions['comments'] = ""

    for idx, row in submissions.iterrows():
        # Get the submission directory path
        filepath = row.get("filepath")
        if filepath is None or (isinstance(filepath, float) and pd.isna(filepath)):
            filepath = ""
        else:
            filepath = str(filepath).strip()
        if not filepath:
            submissions.loc[idx, 'comments'] = "[O]: Correct\n[-]: Minor error\n[X]: Major error\n\n[X]: No submission\n"
            continue
        # Files are saved as {student_name}_{ids}_{index}.ext
        submission_dir = os.path.dirname(filepath)
        # Extract prefix: everything up to the last _N.ext
        basename = os.path.basename(filepath)
        prefix = '_'.join(basename.split('_')[:-1]) + '_'  # e.g. "3A01 Chan_..._uuid_"

        task3_file = None
        prompts_file = None
        report_file = None

        if os.path.isdir(submission_dir):
            py_files = []
            txt_files = []
            for f in os.listdir(submission_dir):
                if f.startswith(prefix):
                    full_path = os.path.join(submission_dir, f)
                    ext = f.rsplit('.', 1)[-1].lower()
                    if ext == 'py':
                        py_files.append(full_path)
                    elif ext == 'txt':
                        txt_files.append(full_path)
            # Prefer the submitted .py filepath; identify txt files by content
            if filepath.endswith(".py") and os.path.exists(filepath):
                task3_file = filepath
            elif py_files:
                task3_file = sorted(py_files)[-1]
            if len(txt_files) >= 1:
                prompts_file, report_file = _resolve_task3_txt_files(txt_files)

        # Initialize scores for this submission
        mark1 = 0
        mark2 = 0
        mark3 = 0
        mark4 = 0
        mark5 = 0
        comments = "[O]: Correct\n[-]: Minor error\n[X]: Major error\n\n"

        # ==================== SECTION 1: Prompt Quality & Quantity (4 marks) ====================
        prompt_content = ""
        if prompts_file and os.path.exists(prompts_file):
            try:
                with open(prompts_file, 'r', encoding='utf-8') as f:
                    prompt_content = f.read()
            except:
                try:
                    with open(prompts_file, 'r', encoding='latin-1') as f:
                        prompt_content = f.read()
                except:
                    pass

        if prompt_content:
            if _is_blank_prompt_template(prompt_content):
                comments += "[X]: gemini_prompts.txt only contains template (no prompts pasted)\n"
            else:
                substantive_prompts = _count_substantive_prompts(prompt_content)
                if substantive_prompts >= 2:
                    mark1 += 1
                    comments += "[O]: Contains at least 2 prompts\n"
                else:
                    comments += "[X]: Less than 2 prompts found\n"

                has_python_ref = re.search(
                    r"python|程式碼|程式|寫.*程式|寫一[個段]|產生.*程式|"
                    r"code|script|write.*program|generate.*code",
                    prompt_content,
                    re.IGNORECASE,
                )
                has_output_ref = re.search(
                    r"output|輸出|結果|result|report|sales_report|報告|報表|"
                    r"寫入|生成.*txt|輸出檔",
                    prompt_content,
                    re.IGNORECASE,
                )
                if has_python_ref and has_output_ref:
                    mark1 += 1
                    comments += "[O]: Prompts guide to generate Python code and output\n"
                else:
                    comments += "[-]: Prompts should guide to generate Python code and output\n"

                has_input_ref = re.search(
                    r"canteen_sales_sample\.json|canteen_sales\.json|canteen_sales|"
                    r"json|輸入檔案|輸入檔|讀取.*json|讀取.*資料|樣本|sample",
                    prompt_content,
                    re.IGNORECASE,
                )
                has_output_ref2 = re.search(
                    r"sales_report_sample\.txt|sales_report\.txt|sales_report|"
                    r"輸出檔案|輸出檔|格式.*要求|報告|\.txt",
                    prompt_content,
                    re.IGNORECASE,
                )
                if has_input_ref and has_output_ref2:
                    mark1 += 1
                    comments += "[O]: Mentions input/output files and format requirements\n"
                else:
                    comments += "[-]: Should specify input/output files and format\n"

                has_step_refs = re.search(
                    r"先|然後|最後|再|其後|跟住|完成後|step|步驟|逐步|"
                    r"first|then|finally|test|測試|改讀|更改|正式",
                    prompt_content,
                    re.IGNORECASE,
                )
                if has_step_refs:
                    mark1 += 1
                    comments += "[O]: Contains step-by-step instructions\n"
                else:
                    comments += "[-]: Should include step-by-step instructions\n"
        else:
            comments += "[X]: gemini_prompts.txt not found or empty\n"

        # ==================== SECTION 2: Code Structure & Functionality (8 marks) ====================
        code_content = ""
        if task3_file and os.path.exists(task3_file):
            try:
                with open(task3_file, 'r', encoding='utf-8') as f:
                    code_content = f.read()
            except:
                try:
                    with open(task3_file, 'r', encoding='latin-1') as f:
                        code_content = f.read()
                except:
                    pass

        if code_content:
            # Check JSON reading capability
            has_json_read = re.search(r'json\.load|open.*\.json|canteen_sales', code_content, re.IGNORECASE)
            if has_json_read:
                mark2 += 2
                comments += "[O]: Successfully reads JSON file\n"
            else:
                comments += "[X]: Cannot read JSON file\n"

            has_total_calc = re.search(r'total|sum|總收入|合計|revenue|income|總和', code_content, re.IGNORECASE)
            if has_total_calc:
                mark2 += 1 if check_sample_total(task3_file) else 0
                if check_sample_total(task3_file):
                    comments += "[O]: Calculates correct total revenue\n"
                else:
                    comments += "[-]: Attempts to calculate total revenue but may be incorrect\n"
            else:
                comments += "[X]: No total revenue calculation\n"

            has_profit_food = re.search(r'max|most.*profitable|best.*selling|最賺錢|highest|top.*revenue', code_content, re.IGNORECASE)
            if has_profit_food:
                mark2_temp = check_most_profitable(task3_file)
                mark2 += min(mark2_temp, 1)
                if mark2_temp >= 1:
                    comments += "[O]: Identifies most profitable food\n" if mark2_temp == 2 else "[-]: Attempts to find most profitable food but may be incorrect\n"
                else:
                    comments += "[X]: Cannot identify most profitable food correctly\n"
            else:
                comments += "[X]: No most profitable food identification logic\n"

            has_class_revenue = re.search(r'class|班別|group|grade|per.*class', code_content, re.IGNORECASE)
            if has_class_revenue:
                mark2_temp = check_class_revenue(task3_file)
                mark2 += min(mark2_temp, 2)
                if mark2_temp == 2:
                    comments += "[O]: Correctly outputs class revenues\n"
                elif mark2_temp == 1:
                    comments += "[-]: Attempts to output class revenues but may be incorrect\n"
                else:
                    comments += "[X]: Cannot output class revenues correctly\n"
            else:
                comments += "[X]: No class revenue calculation\n"
            mark2 = min(mark2, max_marks_2)
        else:
            comments += "[X]: task3_2526.py not found or empty\n"

        # ==================== SECTION 3: Output Format (4 marks) ====================
        report_content = ""
        if report_file and os.path.exists(report_file):
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    report_content = f.read()
            except:
                try:
                    with open(report_file, 'r', encoding='latin-1') as f:
                        report_content = f.read()
                except:
                    pass

        if report_content:
            # Check header line
            if re.search(r'🧾🍟.*小食部銷售報告.*🍟🧾', report_content):
                mark3 += 1
                comments += "[O]: Contains header line\n"
            else:
                comments += "[-]: Header line missing or incorrect format\n"

            # Check total revenue line
            if re.search(r'💰.*總收入.*\$?\d+', report_content):
                mark3 += 1
                comments += "[O]: Contains total revenue line\n"
            else:
                comments += "[-]: Total revenue line missing or incorrect\n"

            # Check most profitable food line
            if re.search(r'🏆.*最賺錢食品.*\$?\d+', report_content):
                mark3 += 1
                comments += "[O]: Contains most profitable food line\n"
            else:
                comments += "[-]: Most profitable food line missing or incorrect\n"

            # Check class revenue section
            if re.search(r'📊.*各班別總收入', report_content) and re.search(r'-\s*\w+:\s*\$\d+', report_content):
                mark3 += 1
                comments += "[O]: Contains class revenue section with correct format\n"
            else:
                comments += "[-]: Class revenue section missing or incorrect format\n"
        else:
            comments += "[X]: sales_report.txt not found or empty\n"

        # ==================== SECTION 4: Correctness & Testing (6 marks) ====================
        if task3_file and os.path.exists(task3_file):
            sample_match = check_sample_output_match(task3_file, report_file)
            if sample_match == 2:
                mark4 += 2
                comments += "[O]: Sample output matches perfectly\n"
            elif sample_match == 1:
                mark4 += 1
                comments += "[-]: Sample output partially correct\n"
            else:
                comments += "[X]: Sample output doesn't match\n"

            actual_correct = check_actual_output(task3_file)
            if actual_correct == 2:
                mark4 += 1
                comments += "[O]: Actual output correct and reasonable\n"
            elif actual_correct == 1:
                mark4 += 1
                comments += "[-]: Actual output partially correct\n"
            else:
                comments += "[X]: Actual output incorrect\n"

            runs_partial = check_partial_execution(task3_file, report_file)
            if runs_partial >= 2:
                mark4 += 1
                comments += "[O]: Code runs successfully or submitted valid report\n"
            elif runs_partial == 1:
                mark4 += 1
                comments += "[-]: Code has errors but produces partial output\n"
            else:
                comments += "[X]: Code execution fails completely\n"
            mark4 = min(mark4, max_marks_4)
        else:
            comments += "[X]: Cannot test correctness - task3_2526.py missing\n"

        # ==================== SECTION 5: Program Executability (4 marks) ====================
        if task3_file and os.path.exists(task3_file):
            # Check if script can be executed without syntax errors
            syntax_ok, runtime_ok = check_executability(task3_file)
            if syntax_ok:
                mark5 += 1
                comments += "[O]: Script runs without syntax errors\n"
                if not is_direct_copy(task3_file) and runtime_ok:
                    mark5 += 1
                    comments += "[O]: Original code with complete logic\n"
                elif not is_direct_copy(task3_file):
                    comments += "[-]: Original code but with some runtime errors\n"
                else:
                    comments += "[-]: Code appears to be a copy but runs\n"
            else:
                comments += "[X]: Script has syntax errors and cannot run\n"
            mark5 = min(mark5, max_marks_5)
        else:
            comments += "[X]: Cannot check executability - task3_2526.py missing\n"

        # Calculate total marks
        total_marks = mark1 + mark2 + mark3 + mark4 + mark5
        submissions.loc[idx, 'mark1'] = mark1
        submissions.loc[idx, 'mark2'] = mark2
        submissions.loc[idx, 'mark3'] = mark3
        submissions.loc[idx, 'mark4'] = mark4
        submissions.loc[idx, 'mark5'] = mark5
        submissions.loc[idx, 'marks'] = total_marks
        
        # Generate final comments
        final_comments = "[O]: Correct\n[-]: Minor error\n[X]: Major error\n\n"
        final_comments += f"Mark1 (Prompt Quality): {mark1}/{max_marks_1}\n"
        final_comments += f"Mark2 (Code Structure): {mark2}/{max_marks_2}\n"
        final_comments += f"Mark3 (Output Format): {mark3}/{max_marks_3}\n"
        final_comments += f"Mark4 (Correctness): {mark4}/{max_marks_4}\n"
        final_comments += f"Mark5 (Executability): {mark5}/{max_marks_5}\n"
        final_comments += f"Total: {total_marks}/{total_max}\n\n"
        final_comments += comments
        submissions.loc[idx, 'comments'] = final_comments

    return submissions