"""
Paper-level quality checks (layout / metadata on rendered DOCX):
- footer banner vs meta.footer or filename
- cover page vs filename
- 乙部 / 丙部 written-question structure (short / long sections)
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from cover import CoverCheckResult, check_cover, format_cover_report
from filename_meta import infer_exam_meta_from_path
from footer import FooterCheckResult, FooterMeta, check_footer, format_footer_report
from written_sections import WrittenSectionCheckResult, check_written_sections

try:
    from mcq_blank_check import McqBlankCheckResult, check_mcq_blank_lines, format_mcq_blank_report
except ImportError:
    McqBlankCheckResult = None  # type: ignore[misc, assignment]
    check_mcq_blank_lines = None  # type: ignore[assignment]
    format_mcq_blank_report = None  # type: ignore[assignment]


@dataclass
class PaperQualityReport:
    candidate: str
    footer: Optional[FooterCheckResult] = None
    cover: Optional[CoverCheckResult] = None
    written: Optional[WrittenSectionCheckResult] = None
    mcq_blanks: Optional["McqBlankCheckResult"] = None

    @property
    def has_footer_issues(self) -> bool:
        return self.footer is not None and not self.footer.ok

    @property
    def has_cover_issues(self) -> bool:
        return self.cover is not None and not self.cover.ok

    @property
    def has_written_issues(self) -> bool:
        return self.written is not None and not self.written.ok

    @property
    def has_mcq_blank_issues(self) -> bool:
        return self.mcq_blanks is not None and not self.mcq_blanks.ok

    @property
    def ok(self) -> bool:
        return (
            not self.has_footer_issues
            and not self.has_cover_issues
            and not self.has_written_issues
            and not self.has_mcq_blank_issues
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"ok": self.ok, "candidate": self.candidate}
        if self.footer is not None:
            d["footer"] = self.footer.to_dict()
        if self.cover is not None:
            d["cover"] = self.cover.to_dict()
        if self.written is not None:
            d["written"] = self.written.to_dict()
        if self.mcq_blanks is not None:
            d["mcq_blanks"] = self.mcq_blanks.to_dict()
        return d


def run_paper_check(
    candidate_docx: Path,
    *,
    candidate_spec_path: Optional[Path] = None,
    template_docx_path: Optional[Path] = None,
    verify_footer: bool = True,
    verify_cover: bool = True,
    verify_written: bool = True,
    verify_mcq_blanks: bool = True,
    mcq_blocks: tuple[tuple[int, int], ...] | None = None,
    footer_meta: Optional[dict] = None,
) -> PaperQualityReport:
    candidate_docx = candidate_docx.expanduser().resolve()
    spec_meta: dict = {}
    if candidate_spec_path and candidate_spec_path.exists():
        import sys

        qdir = Path(__file__).resolve().parents[1] / "question-quality-check"
        if str(qdir) not in sys.path:
            sys.path.insert(0, str(qdir))
        from exam_spec import load_spec

        spec_meta = load_spec(candidate_spec_path).get("meta", {})

    report = PaperQualityReport(candidate=str(candidate_docx))

    if verify_footer:
        expected = footer_meta or spec_meta.get("footer")
        if not expected:
            inferred = infer_exam_meta_from_path(candidate_spec_path or candidate_docx)
            if inferred:
                expected = inferred.footer_meta()
        report.footer = check_footer(
            candidate_docx,
            expected_meta=FooterMeta.from_dict(expected) if expected else None,
            template=template_docx_path if not expected else None,
        )

    if verify_cover:
        report.cover = check_cover(
            candidate_docx,
            filename_for_infer=candidate_spec_path or candidate_docx,
        )

    if verify_written:
        report.written = check_written_sections(
            candidate_docx,
            template_docx_path=template_docx_path,
        )

    if verify_mcq_blanks and check_mcq_blank_lines is not None:
        blocks = mcq_blocks
        if blocks is None:
            import sys

            fmt = Path(__file__).resolve().parents[1] / "paper-formatter"
            if str(fmt) not in sys.path:
                sys.path.insert(0, str(fmt))
            from f5_ict_layout import F5_ICT_MCQ_BLOCKS

            blocks = F5_ICT_MCQ_BLOCKS
        report.mcq_blanks = check_mcq_blank_lines(candidate_docx, blocks)

    return report


def format_paper_report_text(report: PaperQualityReport) -> str:
    sections: list[str] = []
    if report.footer is not None:
        sections.extend(["=== Footer banner check ===", format_footer_report(report.footer)])
    if report.cover is not None:
        sections.extend(["", "=== Cover page check ===", format_cover_report(report.cover)])
    if report.written is not None:
        from written_sections import format_written_report

        sections.extend(["", format_written_report(report.written)])
    if report.mcq_blanks is not None and format_mcq_blank_report is not None:
        sections.extend(["", format_mcq_blank_report(report.mcq_blanks)])
    sections.append("")
    sections.append(f"Overall: {'PASS' if report.ok else 'ISSUES FOUND'}")
    return "\n".join(sections)


def write_paper_report_json(report: PaperQualityReport, path: Path) -> None:
    import json

    path = path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")


def report_exit_code(report: PaperQualityReport, *, strict: bool = False) -> int:
    if report.ok:
        return 0
    return 2 if strict else 1
