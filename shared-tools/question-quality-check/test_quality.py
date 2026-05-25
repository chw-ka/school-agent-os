"""Smoke tests for question-quality-check."""
from __future__ import annotations

from pathlib import Path

from coherence_check import check_text_coherence
from answer_pattern_check import (
    check_all_answer_patterns,
    generate_random_balanced_letters,
    has_pattern_issues,
)
from concept_check import build_concept_distribution, check_concepts, compare_concept_distributions
from format_check import check_exam_format, check_spec_format
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
    src = Path(
        "Subjects/S3-CMP/past-papers/2025-2026/Term 02/WrittenExam/25_26_S3_CMP_Term02_Exam.docx"
    )
    if not src.exists():
        return
    letters, src_label = mcq_answers_from_docx(src)
    assert len(letters) == 20
    assert src_label == "docx.answer_key_line"


def test_format_backticks_fail() -> None:
    spec = build_spec(
        {"subject": "test"},
        [make_item("m1", "mcq", "use `backtick` here")],
    )
    result = check_spec_format(spec)
    assert not result.ok
    assert "`backtick`" in result.backtick_hits


def test_format_backticks_pass() -> None:
    spec = build_spec(
        {"subject": "test"},
        [make_item("m1", "mcq", "use 'single quotes' here")],
    )
    result = check_spec_format(spec)
    assert result.ok


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


def test_intra_exam_vibe_coding_leak() -> None:
    """S3 CMP pattern: MCQ#10 answer «總監» appears in 丁部 fill stem."""
    from quality_lib import compare_intra_exam_lines

    lines = [
        "甲部 – 多項選擇題",
        "10.\tVibe Coding 下，學生最合適扮演？",
        "A.\t抄襲 AI",
        "B.\t總監（構思、測試、修正）",
        "C.\t只畫圖",
        "D.\t只閱卷",
        "乙部 – 配對題",
        "丙部 – 是非題",
        "丁部 – 填充題",
        "Vibe Coding 中，AI 像________，學生像總監。",
        "戊部 – 短答題",
        "根據筆記，Vibe Coding 為什麼需要「迭代（Iteration）」？請舉一個例子說明。",
    ]
    mcq_key = ["B"]
    matches = compare_intra_exam_lines(lines, mcq_answers=mcq_key)
    leaks = [m for m in matches if m.match_type == "answer_leak"]
    assert leaks, "expected MCQ answer leak into fill blank"
    assert any("丁" in m.reference_label for m in leaks)


def test_intra_exam_cross_section_overlap() -> None:
    from quality_lib import compare_intra_exam_lines

    lines = [
        "甲部 – 多項選擇題",
        "10.\tVibe Coding 下，學生最合適扮演？",
        "A.\tA",
        "B.\tB",
        "C.\tC",
        "D.\tD",
        "乙部 – 配對題",
        "丙部 – 是非題",
        "丁部 – 填充題",
        "Vibe Coding 中，AI 像________，學生像總監。",
        "戊部 – 短答題",
    ]
    matches = compare_intra_exam_lines(lines, mcq_answers=["B"])
    overlaps = [m for m in matches if m.match_type == "intra_exam"]
    assert overlaps, "expected cross-section thematic overlap"


def test_concept_conflict_hallucination_mcq_and_later_sections() -> None:
    from concept_conflict_check import check_concept_conflicts

    spec = build_spec(
        {"subject": "test"},
        [
            make_item(
                "mcq-02",
                "mcq",
                "根據筆記，下列哪一項最能描述「幻覺（Hallucination）」？",
                answer="B",
            ),
            make_item(
                "c-tf-03",
                "section_c",
                "生成式 AI 的「幻覺」是指 AI 故意說謊來欺騙人類。",
                answer="F",
            ),
            make_item(
                "d-fill-a-03",
                "section_d",
                "當 AI 提供虛假資訊時，稱為「 ________ 」。",
                answer="幻覺",
            ),
        ],
    )
    result = check_concept_conflicts(spec)
    assert not result.ok
    assert any(c.topic_id == "hallucination" for c in result.conflicts)


def test_concept_conflict_tm_testing_mcq_and_sa() -> None:
    from concept_conflict_check import check_concept_conflicts

    spec = build_spec(
        {"subject": "test"},
        [
            make_item(
                "mcq-19",
                "mcq",
                "訓練後要『充分測試』模型準確性，下列哪一項是最主要原因？",
                answer="A",
            ),
            make_item(
                "e-sa-01",
                "section_e",
                "為什麼在 Teachable Machine 完成訓練後，必須先進行「充分測試」？",
            ),
        ],
    )
    result = check_concept_conflicts(spec)
    assert not result.ok
    assert any(c.topic_id == "tm_testing" for c in result.conflicts)


def test_concept_conflict_diversified_pass() -> None:
    from concept_conflict_check import check_concept_conflicts

    spec = build_spec(
        {"subject": "test"},
        [
            make_item(
                "mcq-02",
                "mcq",
                "根據筆記，下列哪一項最能描述「幻覺（Hallucination）」？",
                answer="B",
            ),
            make_item(
                "d-fill-a-01",
                "section_d",
                "把長篇文章濃縮成精簡重點，稱為「 ________ 」。",
                answer="摘要",
            ),
            make_item(
                "e-sa-01",
                "section_e",
                "請說明 R-I-C-C-O 中 R 和 C（背景）可以如何設定。",
            ),
        ],
    )
    result = check_concept_conflicts(spec)
    assert result.ok


def test_coherence_meta_bridge() -> None:
    bad = "（以下各題參考上述情境；部分設定取自不同 DSE 試題。）\n\n(a) 寫出公式。"
    issues = check_text_coherence("b-01", bad, section="section_b")
    assert any(i.kind == "meta_bridge" for i in issues)


def test_answer_verify_skips_generated_provenance() -> None:
    from answer_verify_check import verify_spec_answers

    spec = {
        "items": [
            {
                "id": "mcq-01",
                "section": "mcq",
                "text": "stem\n\tA.\ta\n\tB.\tb\n\tC.\tc\n\tD.\td",
                "answer": "A",
                "dse_source": "generated://mcq/mcq-01",
            },
            {
                "id": "b-01",
                "section": "section_b",
                "text": "(a) test",
                "dse_source": "generated://written/b-01",
            },
        ],
        "meta": {"mcq_answers": "A"},
    }
    result = verify_spec_answers(spec)
    assert result.ok
    assert not any(i.kind == "mcq_bank_missing" for i in result.issues)


def test_intra_mcq_stem_and_concept_dup() -> None:
    from check_spec import compare_intra_mcq_extended, compare_intra_spec

    spec = build_spec(
        {"subject": "test"},
        [
            make_item(
                "mcq-17",
                "mcq",
                "下列哪一項屬於實用程式（utility）？\n\n\n\tA.\t磁碟重組工具\n\tB.\t網頁瀏覽器",
                concepts=["軟件", "實用程式"],
            ),
            make_item(
                "mcq-19",
                "mcq",
                "下列哪一項屬於實用程式（utility）？\n\n\tA.\t文書處理軟件\n\tB.\t試算表",
                concepts=["軟件", "實用程式"],
            ),
            make_item(
                "mcq-13",
                "mcq",
                "細看下表所列裝置。以下哪項／些屬於輸入裝置？\n\t(1)\t加速度計\n\n\tA.\t只有 (1)",
                concepts=["硬件", "輸入裝置"],
            ),
            make_item(
                "mcq-20",
                "mcq",
                "下列哪一項屬於輸入裝置？\n\n\n\tA.\t投影機\n\tB.\t喇叭",
                concepts=["硬件", "輸入裝置"],
            ),
        ],
    )
    stem_hits = [d for d in compare_intra_mcq_extended(spec) if d.match_type == "intra_mcq_stem"]
    assert any(d.candidate_id == "mcq-17" and d.reference_id == "mcq-19" for d in stem_hits)
    concept_hits = [d for d in compare_intra_spec(spec) if d.match_type == "intra_mcq_concept"]
    assert any(
        {d.candidate_id, d.reference_id} == {"mcq-13", "mcq-20"} for d in concept_hits
    )


def test_coherence_topic_clash() -> None:
    bad = "SELECT * FROM T\n\n估算 BMP 像素大小。"
    issues = check_text_coherence("b-03", bad, section="section_b")
    assert any(i.kind == "topic_clash" for i in issues)


def test_written_picks_render_b02() -> None:
    import sys
    from pathlib import Path

    fmt = Path(__file__).resolve().parents[1] / "paper-formatter"
    if str(fmt) not in sys.path:
        sys.path.insert(0, str(fmt))
    from written_layout import ANSWER_BLANK
    from written_picks_render import layout_slot_from_pick, pick_text_to_content_lines

    pick = {
        "text": (
            "如果一位員工在欄 D 或欄 E 所對應的數值為 1，他將被視為出席。\n"
            "(a) 說明有效性檢驗。\n"
            "(b) 為班別欄建議規則。"
        )
    }
    lines = pick_text_to_content_lines(pick["text"])
    assert any("(a)" in ln for ln in lines)
    assert "出席" in lines[0]
    skel = ["舊情景：網上報名", "", "", "\t(a)\t舊", ANSWER_BLANK, "\t(b)\t舊", ANSWER_BLANK]
    merged = layout_slot_from_pick(pick, skel)
    assert "出席" in merged[0]
    assert "有效性" in "".join(merged)
    assert "網上報名" not in "".join(merged)


if __name__ == "__main__":
    test_format_backticks_fail()
    test_format_backticks_pass()
    test_concept_distribution()
    test_mcq_balance_even()
    test_mcq_pattern_random_key()
    test_answer_patterns_in_spec()
    test_mcq_balance_uneven()
    test_mcq_parse_key_line()
    test_mcq_docx_s3()
    test_concept_mismatch()
    test_concept_match()
    test_intra_exam_vibe_coding_leak()
    test_intra_exam_cross_section_overlap()
    test_concept_conflict_hallucination_mcq_and_later_sections()
    test_concept_conflict_tm_testing_mcq_and_sa()
    test_concept_conflict_diversified_pass()
    test_coherence_meta_bridge()
    test_intra_mcq_stem_and_concept_dup()
    test_coherence_topic_clash()
    test_written_picks_render_b02()
    print("ok")
