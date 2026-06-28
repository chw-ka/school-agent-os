# shared-tools/code-marking

Utilities for marking code-based submissions: Python scripts, Arduino (.ino), EV3 MakeCode, and AI-usage detection.

## Modules

| Module | Purpose |
|--------|---------|
| `py_util.py` | Execute student Python code safely; capture stdout |
| `ino_util.py` | Load Arduino/C++ submission files |
| `ev3_utils.py` | Scan EV3 `main.ts` files and apply a marking function |
| `pai_util.py` | Detect AI-generated code; cap marks for restricted chapters |
| `pai_forms_util.py` | Score MS Forms responses for Ch4T1 (OpenCV tracker) |
| `docx_util.py` | Extract images and text from `.docx` submissions |
| `excel_utils.py` | Mark Excel `.xlsx` submissions against a marksheet |
| `vision_util.py` | Send images to Gemini vision API; cache responses |

`test.py` (the marking runner) adds `shared-tools/code-marking/` to `sys.path` automatically.

## Usage in tester modules

```python
import py_util
import pai_util
```

### Run student Python code

```python
output = py_util.test_student_code(student_code, input_value="5\n")
# output is the captured stdout string
```

### AI-usage detection (PAI chapters 1–4)

```python
marks, comments = pai_util.finalize_ch1_4_mark(marks, comments, filepath, chapter=2)
# caps marks at 2 if AI usage detected; adds explanatory comment
```

### MS Forms scoring (PAI Ch4T1)

```python
import pai_forms_util

scores = pai_forms_util.load_ch4t1_forms_scores()
# scores: {"3A01": (marks, comments), ...}
```

Looks for Forms data at `task_info/Python與人工智能_第四章_任務一/...xlsx`
and student ID map at `records/stuid_class_map.json` or `student_data/student_data.csv`
— all resolved relative to the subject's `marking/` working directory.

### EV3

```python
import ev3_utils

def my_marking_fn(main_ts_code):
    marks, comments, submarks = 0, "", {}
    # ... inspect code ...
    return marks, comments, submarks

ev3_utils.mark_ev3(marksheet_name="ev3_task1", marking_function=my_marking_fn)
```

Reads student files from `ev3/<marksheet_name>/<student>/main.ts`.
