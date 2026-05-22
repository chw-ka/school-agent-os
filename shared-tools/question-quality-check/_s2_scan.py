import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from quality_lib import extract_lines, _mcq_key_from_lines, extract_mcq_stems

docx = Path(r"c:\Users\localadmin\Projects\school-agent-os\Subjects\S2-CMP\past-papers\2025-2026\Term 02\WrittenExam\25_26_S2_CMP_Term02_Exam.docx")
lines = extract_lines(docx)
out = []
for i, ln in enumerate(lines):
    if any(k in ln for k in ("甲部", "乙部", "丙部", "丁部", "全卷完", "標準答案", "下期", "試卷完")):
        out.append(f"{i}: {ln[:100]}")
out.append("\n--- MCQ KEY ---")
stems = extract_mcq_stems(lines)
key = _mcq_key_from_lines(lines, expected_count=20)
out.append(f"stems={len(stems)} key={''.join(key)} len={len(key)}")
from collections import Counter
out.append(f"counts={dict(Counter(key))}")
Path(__file__).with_suffix(".out.txt").write_text("\n".join(out), encoding="utf-8")
