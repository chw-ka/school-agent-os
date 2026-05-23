"""Tests for partial slot regen."""
from f5_ict_exam_blueprint import build_f5_exam02_blueprint
from f5_ict_generate_from_blueprint import (
    build_spec_from_blueprint,
    generate_item_for_slot,
    replace_spec_item,
)
from partial_regen import collect_failed_slot_ids, run_partial_regen, slot_passes_local_check


def test_replace_slot_changes_text():
    bp = build_f5_exam02_blueprint()
    spec = build_spec_from_blueprint(bp, seed=1, style_patterns={})
    slot = next(s for s in bp["slots"] if s["id"] == "mcq-01")
    old = next(i["text"] for i in spec["items"] if i["id"] == "mcq-01")
    new_item = generate_item_for_slot(slot, {}, seed=999, variant=3)
    replace_spec_item(spec, new_item, seed=1)
    new = next(i["text"] for i in spec["items"] if i["id"] == "mcq-01")
    assert old != new or new_item["text"] != old


def test_partial_regen_resolves_clean_slot():
    bp = build_f5_exam02_blueprint()
    spec = build_spec_from_blueprint(bp, seed=2, style_patterns={})
    slot = next(s for s in bp["slots"] if s["id"] == "mcq-01")
    pr = run_partial_regen(spec, bp, {}, ["mcq-01"], seed=100, max_attempts=5, refs=[])
    assert pr.slots[0].slot_id == "mcq-01"
    assert slot_passes_local_check(spec, "mcq-01")


if __name__ == "__main__":
    test_replace_slot_changes_text()
    test_partial_regen_resolves_clean_slot()
    print("ok")
