import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from quality_lib import extract_lines

for name in ["24_25_S2_CMP_Term02_Exam.docx", "25_26_S2_CMP_Term02_Exam.docx"]:
    p = Path(r"c:\Users\localadmin\Projects\school-agent-os\Subjects\S2-CMP\past-papers")
    if name.startswith("24"):
        docx = p / "2024-2025/Term 02/WrittenExam" / name
    else:
        docx = p / "2025-2026/Term 02/WrittenExam" / name
    lines = extract_lines(docx)
    print("===", name, "lines", len(lines))
    for i, ln in enumerate(lines):
        if any(k in ln for k in ("丙部", "丁部", "全卷完", "標準答案", "試卷完", "是非", "填充")):
            print(f"  {i}: {ln[:120]}")
