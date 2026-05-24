"""Tests for spec → MCQ template rows."""
import sys
from pathlib import Path

_Q = Path(__file__).resolve().parents[1] / "question-quality-check"
if str(_Q) not in sys.path:
    sys.path.insert(0, str(_Q))

from exam_spec import load_spec
from f5_ict_exam_blueprint import build_f5_exam02_blueprint
from f5_ict_generate_from_blueprint import build_spec_from_blueprint
from spec_mcq_render import MCQ_SPANS, spec_mcq_to_final_rows


def test_spec_mcq_spans_match_template():
    spec = build_spec_from_blueprint(build_f5_exam02_blueprint(), seed=42, style_patterns={})
    rows, key = spec_mcq_to_final_rows(spec)
    assert len(rows) == 30
    assert len(key) == 30
    assert all(len(r) <= e for r, e in zip(rows, MCQ_SPANS))


if __name__ == "__main__":
    test_spec_mcq_spans_match_template()
    print("ok")
