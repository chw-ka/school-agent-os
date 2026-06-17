"""MCQ layout: no internal padding blanks; all four options present."""
import sys
from pathlib import Path

_PG = Path(__file__).resolve().parent
_QCHECK = _PG.parent / "question-quality-check"
_PCHECK = _PG.parent / "paper-quality-check"
_FMT = _PG.parent / "paper-formatter"
for p in (_PG, _QCHECK, _PCHECK, _FMT):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from exam_spec import load_spec
from f5_ict_from_dse import _layout_mcq_block
from mcq_blank_check import check_mcq_block_lines
from spec_mcq_render import MCQ_SPANS, parse_spec_mcq_text, spec_mcq_to_final_rows

_SPEC = (
    Path(__file__).resolve().parents[2]
    / "Subjects/S5-ICT/assessments/2025-2026/Term 02/_generation/25_26_S5_ICT_Exam02.spec.json"
)


def test_simple_mcq_one_blank_before_options():
    q, stmts, opts = parse_spec_mcq_text(
        "8 位元二進制補碼可表示的整數範圍是什麼？\n\n\tA.\tx\n\tB.\ty\n\tC.\tz\n\tD.\tw"
    )
    r = _layout_mcq_block(q, stmts, opts, span=10)
    assert MCQ_SPANS[5] == 10
    assert len(r) == 6
    assert r[1] == ""
    assert r[2].startswith("\tA.")
    assert r[5].startswith("\tD.")
    assert sum(1 for x in r[2:6] if x == "") == 0
    assert len(r) <= 10
    issues = check_mcq_block_lines(6, r, para_start=0)
    assert not issues, issues


def test_pseudocode_mcq_has_four_options():
    spec = load_spec(_SPEC)
    items = {it["id"]: it for it in spec["items"] if it.get("section") == "mcq"}
    for qi in [6, 8, 13, 15, 16, 21, 22, 24, 28, 30]:
        it = items[f"mcq-{qi:02d}"]
        q, stmts, opts = parse_spec_mcq_text(str(it.get("text") or ""))
        r = _layout_mcq_block(q, stmts, opts, MCQ_SPANS[qi - 1])
        assert len(r) <= MCQ_SPANS[qi - 1], qi
        assert any(x.startswith("\tA.") for x in r), qi
        assert any(x.startswith("\tD.") for x in r), qi
        issues = check_mcq_block_lines(qi, r, para_start=0)
        assert not issues, (qi, issues)


if __name__ == "__main__":
    test_simple_mcq_one_blank_before_options()
    test_pseudocode_mcq_has_four_options()
    print("ok")
