"""Tests for concept_map builder."""
import json
from pathlib import Path

from build_concept_map import build_concept_map

_REPO = Path(__file__).resolve().parents[2]
_BANK = _REPO / "Subjects/DSE-ICT/question-bank"


def test_build_concept_map_tree_shape():
    payload = build_concept_map(
        _BANK,
        _BANK / "curriculum_concepts.json",
        ("2024", "2025"),
        ("Paper1_MultipleChoice", "Paper1A_MultipleChoice"),
        style_patterns_path=None,
    )
    assert payload["version"] == 2
    a = payload["tree"]["compulsory"]["A"]
    assert a["label"] == "資訊處理"
    assert "A-b" in a["topics"]
    ab = a["topics"]["A-b"]
    assert "數據組織" in ab["concepts"] or "欄位" in ab["concepts"]
    assert ab["bank_stats"]["item_count"] >= 0
    assert "試算表" in payload["concept_index"]
    assert payload["concept_index"]["試算表"]["bank_stats"]["item_count"] >= 0


def test_written_output_exists_after_build():
    path = _BANK / "concept_map.json"
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    assert "tree" in data and "concept_index" in data


if __name__ == "__main__":
    test_build_concept_map_tree_shape()
    test_written_output_exists_after_build()
    print("ok")
