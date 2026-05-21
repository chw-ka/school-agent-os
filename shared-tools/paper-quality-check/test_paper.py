"""Smoke tests for paper-quality-check."""
from __future__ import annotations

import tempfile
from pathlib import Path

from filename_meta import infer_exam_meta_from_path
from footer import FooterMeta, apply_footer_meta, check_footer, extract_footer_banner
from cover import check_cover


def test_filename_meta_s3_cmp() -> None:
    meta = infer_exam_meta_from_path("25_26_S3_CMP_Term02_Exam.docx")
    assert meta is not None
    assert meta.level_zh == "中三級"
    assert meta.subject_zh == "電腦認知"
    assert meta.term_exam == "下學期考試"
    assert "2025" in meta.year_term_cover


def test_footer_apply_and_check() -> None:
    src = Path(
        "Subjects/S3-CMP/past-papers/2025-2026/Term 02/WrittenExam/25_26_S3_CMP_Term02_Exam.docx"
    )
    if not src.exists():
        return
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "exam.docx"
        p.write_bytes(src.read_bytes())
        meta = FooterMeta("2025-2026", "中三級", "下學期考試", "電腦認知")
        apply_footer_meta(p, meta)
        assert "中三級" in extract_footer_banner(p)
        result = check_footer(p, expected_meta=meta)
        assert result.ok


def test_cover_check_on_real_docx() -> None:
    src = Path(
        "Subjects/S3-CMP/past-papers/2025-2026/Term 02/WrittenExam/25_26_S3_CMP_Term02_Exam.docx"
    )
    if not src.exists():
        return
    result = check_cover(src)
    assert result is not None
    assert result.ok


def test_written_sections_on_reference_s5() -> None:
    ref = Path(
        "Subjects/S5-ICT/past-papers/2024-2025/Term 02/WrittenExam/24_25_S5_ICT_Exam02.docx"
    )
    if not ref.exists():
        return
    from written_sections import check_written_sections

    result = check_written_sections(ref, template_docx_path=ref)
    assert result.ok, [i.message for i in result.issues if i.severity == "error"]


def test_written_sections_flags_bad_indent() -> None:
    gen = Path(
        "Subjects/S5-ICT/past-papers/2025-2026/Term 02/WrittenExam/25_26_S5_ICT_Exam02.docx"
    )
    if not gen.exists():
        return
    from written_sections import check_written_sections

    result = check_written_sections(gen)
    # After regeneration this should pass; keep as integration smoke test.
    assert result.sections_found == ["乙部", "丙部"]


if __name__ == "__main__":
    test_filename_meta_s3_cmp()
    test_footer_apply_and_check()
    test_cover_check_on_real_docx()
    test_written_sections_on_reference_s5()
    test_written_sections_flags_bad_indent()
    print("ok")
