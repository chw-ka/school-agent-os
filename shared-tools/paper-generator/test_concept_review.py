"""Tests for exam blueprint + concept review."""
import json
from pathlib import Path

from concept_review import run_concept_review
from f5_ict_exam_blueprint import build_f5_exam02_blueprint

_REPO = Path(__file__).resolve().parents[2]
_CMAP = _REPO / "Subjects/DSE-ICT/question-bank/concept_map.json"


def test_blueprint_has_43_slots():
    bp = build_f5_exam02_blueprint()
    assert len(bp["slots"]) == 43  # 30 MCQ + 6 乙 + 7 丙 (no c-04)
    assert bp["meta"]["total_marks"] == 100


def test_concept_review_default_blueprint():
    if not _CMAP.exists():
        return
    bp = build_f5_exam02_blueprint()
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = Path(f.name)
        path.write_text(json.dumps(bp, ensure_ascii=False), encoding="utf-8")
    report = run_concept_review(path, concept_map_path=_CMAP, include_info=False)
    assert report.summary["slot_count"] == 43
    errors = [i for i in report.issues if i.severity == "error"]
    assert not errors, errors


if __name__ == "__main__":
    test_blueprint_has_43_slots()
    test_concept_review_default_blueprint()
    print("ok")
