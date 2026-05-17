"""Smoke tests for question-quality-check."""
from __future__ import annotations

from pathlib import Path

from answer_pattern_check import (
    check_all_answer_patterns,
    generate_random_balanced_letters,
    has_pattern_issues,
)
from concept_check import build_concept_distribution, check_concepts, compare_concept_distributions
from mcq_check import apply_pattern_check, check_mcq_balance, mcq_answers_from_docx, parse_answer_letters
from exam_spec import build_spec, make_item


def test_concept_mismatch() -> None:
    cand = build_spec(
        {"subject": "test"},
        [make_item("b-01", "section_b", "text", concepts=["試算表"])],
    )
    ref = build_spec(
        {"subject": "test"},
        [make_item("b-01", "section_b", "other", concepts=["網絡"])],
    )
    result = check_concepts(cand, ref)
    assert not result.ok
    assert len(result.mismatches) == 1


def test_concept_distribution() -> None:
    spec = build_spec(
        {"subject": "test"},
        [
            make_item("a", "mcq", "t1", concepts=["試算表"]),
            make_item("b", "mcq", "t2", concepts=["試算表", "IF"]),
            make_item("c", "section_b", "t3", concepts=["網絡"]),
        ],
    )
    dist = build_concept_distribution(spec)
    assert dist.concept_counts["試算表"] == 2
    assert dist.concept_counts["IF"] == 1
    ref = build_spec(
        {"subject": "test"},
        [make_item("a", "mcq", "t1", concepts=["試算表"])],
    )
    report = compare_concept_distributions(spec, ref)
    assert "網絡" in report.extra_in_candidate


def test_mcq_balance_even() -> None:
    answers = list("ABCD") * 5
    result = check_mcq_balance(answers, total_mcq=20, source="test")
    assert result.balance_ok
    assert result.counts["A"] == 5
    result = apply_pattern_check(result)
    assert not result.pattern_ok
    assert not result.ok


def test_mcq_pattern_random_key() -> None:
    key = generate_random_balanced_letters(20, "ABCD")
    result = apply_pattern_check(
        check_mcq_balance(list(key), total_mcq=20, source="generated"),
    )
    assert result.ok
    assert result.pattern_ok


def test_answer_patterns_in_spec() -> None:
    key = generate_random_balanced_letters(20, "ABCD")
    spec = build_spec(
        {
            "mcq_answers": key,
            "matching_answers": ["EDCBA", "BCADE"],
            "tf_answers": "TFTFT",
            "fill_answers": [["playsound", "gTTS", "yue", "SpeechRecognition", "password.json"]],
            "fill_word_banks": [["gTTS", "playsound", "SpeechRecognition", "yue", "password.json"]],
        },
        [make_item("m1", "mcq", "q", answer="A")],
    )
    bad = check_all_answer_patterns(spec)
    assert not bad.ok
    assert has_pattern_issues(list("ABCD") * 5, alphabet="ABCD")


def test_mcq_balance_uneven() -> None:
    answers = list("B") * 12 + list("A") * 8
    result = check_mcq_balance(answers, total_mcq=20, source="test")
    assert not result.ok


def test_mcq_parse_key_line() -> None:
    assert parse_answer_letters("DBBCB CBCBB BBACB AACBA") == list("DBBCBCBCBBBBACBAACBA")


def test_mcq_docx_s3() -> None:
    src = Path("Subjects/PastPaper/CMP+ICT/2025-2026/S3 CMP/25_26_S3_CMP_Term02_Exam.docx")
    if not src.exists():
        return
    letters, src_label = mcq_answers_from_docx(src)
    assert len(letters) == 20
    assert src_label == "docx.answer_key_line"


def test_concept_match() -> None:
    cand = build_spec(
        {"subject": "test"},
        [make_item("b-01", "section_b", "text", concepts=["試算表", "IF"])],
    )
    ref = build_spec(
        {"subject": "test"},
        [make_item("b-01", "section_b", "other", concepts=["IF", "試算表"])],
    )
    result = check_concepts(cand, ref)
    assert result.ok


if __name__ == "__main__":
    test_concept_distribution()
    test_mcq_balance_even()
    test_mcq_pattern_random_key()
    test_answer_patterns_in_spec()
    test_mcq_balance_uneven()
    test_mcq_parse_key_line()
    test_mcq_docx_s3()
    test_concept_mismatch()
    test_concept_match()
    print("ok")
