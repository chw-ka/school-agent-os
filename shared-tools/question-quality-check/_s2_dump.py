import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from quality_lib import extract_lines, extract_comparable_units, extract_mcq_stems

docx = Path(r"c:\Users\localadmin\Projects\school-agent-os\Subjects\S2-CMP\past-papers\2025-2026\Term 02\WrittenExam\25_26_S2_CMP_Term02_Exam.docx")
lines = extract_lines(docx)
parts = []
active = None
for i, ln in enumerate(lines[:140]):
    if "甲部" in ln and "多項" in ln:
        active = "A"
        parts.append(f"\n## {i} {ln}")
        continue
    if ln.startswith("乙部"):
        active = "B"
        parts.append(f"\n## {i} {ln}")
        continue
    if ln.startswith("丙部"):
        active = "C"
        parts.append(f"\n## {i} {ln}")
        continue
    if ln.startswith("丁部"):
        active = "D"
        parts.append(f"\n## {i} {ln}")
        continue
    if "~全卷完~" in ln or ln.strip() == "全卷完":
        parts.append(f"\n## {i} END")
        break
    if active:
        parts.append(f"{i}: {ln}")
Path(__file__).with_suffix(".out.txt").write_text("\n".join(parts), encoding="utf-8")
print("written")
