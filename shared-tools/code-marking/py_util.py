"""Run student Python code safely and capture output."""

from io import StringIO
import sys


def run_code_safely(student_code):
    try:
        exec(student_code)
    except Exception as e:
        print("Program crashed with error:", e)


def test_student_code(student_code, input_value):
    """Execute student_code with the given stdin input and return captured stdout."""
    sys.stdin = StringIO(input_value)
    captured = StringIO()
    sys.stdout = captured
    try:
        exec(student_code)
    except Exception as e:
        return f"Error: {e}"
    finally:
        sys.stdin = sys.__stdin__
        sys.stdout = sys.__stdout__
    return captured.getvalue()
