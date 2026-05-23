"""Tests for blueprint → spec generation."""
from f5_ict_exam_blueprint import build_f5_exam02_blueprint
from f5_ict_generate_from_blueprint import build_spec_from_blueprint


def test_build_spec_item_count():
    bp = build_f5_exam02_blueprint()
    spec = build_spec_from_blueprint(bp, seed=42, style_patterns={})
    assert len(spec["items"]) == 43
    assert len(spec["meta"]["mcq_answers"]) == 30
    assert all(not p.startswith("202") for p in spec["meta"]["mcq_provenance"])


def test_generated_stems_not_empty():
    spec = build_spec_from_blueprint(build_f5_exam02_blueprint(), seed=1)
    for it in spec["items"]:
        assert len(it["text"]) >= 20
        assert it.get("dse_source", "").startswith("generated://")


if __name__ == "__main__":
    test_build_spec_item_count()
    test_generated_stems_not_empty()
    print("ok")
