"""
Question-level quality checks on exam specs (JSON):
- duplicate detection vs template / past papers
- concept alignment vs template spec
- MCQ balance and answer-key randomness
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

from answer_pattern_check import AllAnswerPatternsResult, check_all_answer_patterns, format_all_patterns_report
from concept_check import (
    ConceptCheckResult,
    check_concepts as run_concept_check,
    check_mcq_core_sequence,
    compare_concept_distributions,
    format_concept_report,
)
from concept_conflict_check import (
    ConceptConflictResult,
    check_concept_conflicts,
    format_concept_conflict_report,
)
from exam_spec import DuplicateEntry, DuplicateReport, load_spec, spec_items
from format_check import FormatCheckResult, check_exam_format, check_spec_format, format_format_report
from mcq_check import McqCheckResult, check_mcq, format_mcq_report
from quality_lib import (
    THRESH_DUPLICATE,
    THRESH_INTRA_CROSS,
    _is_section_header,
    compare_intra_exam,
    discover_past_papers,
    infer_subject_subpath,
    text_similarity,
)
from spec_from_docx import docx_to_spec


@dataclass
class QuestionQualityReport:
    candidate: str
    threshold: float = THRESH_DUPLICATE
    duplicates: DuplicateReport = field(default_factory=lambda: DuplicateReport("", THRESH_DUPLICATE))
    concepts: Optional[ConceptCheckResult] = None
    mcq: Optional[McqCheckResult] = None
    answer_patterns: Optional[AllAnswerPatternsResult] = None
    format: Optional[FormatCheckResult] = None
    concept_conflicts: Optional[ConceptConflictResult] = None

    @property
    def has_duplicates(self) -> bool:
        return self.duplicates.has_duplicates

    @property
    def has_concept_issues(self) -> bool:
        if self.concepts is None:
            return False
        if not self.concepts.ok:
            return True
        if not self.concepts.core_sequence_ok:
            return True
        return not self.concepts.distribution_ok

    @property
    def has_concept_conflict_issues(self) -> bool:
        return self.concept_conflicts is not None and not self.concept_conflicts.ok

    @property
    def has_mcq_issues(self) -> bool:
        return self.mcq is not None and not self.mcq.ok

    @property
    def has_answer_pattern_issues(self) -> bool:
        return self.answer_patterns is not None and not self.answer_patterns.ok

    @property
    def has_format_issues(self) -> bool:
        return self.format is not None and not self.format.ok

    @property
    def ok(self) -> bool:
        return (
            not self.has_duplicates
            and not self.has_concept_issues
            and not self.has_concept_conflict_issues
            and not self.has_mcq_issues
            and not self.has_answer_pattern_issues
            and not self.has_format_issues
        )

    @property
    def regenerate_ids(self) -> list[str]:
        return self.duplicates.regenerate_ids

    def to_dict(self) -> dict:
        d: dict = {
            "ok": self.ok,
            "candidate": self.candidate,
            "threshold": self.threshold,
            "duplicates": self.duplicates.to_dict(),
        }
        if self.concepts is not None:
            d["concepts"] = self.concepts.to_dict()
        if self.mcq is not None:
            d["mcq"] = self.mcq.to_dict()
        if self.answer_patterns is not None:
            d["answer_patterns"] = self.answer_patterns.to_dict()
        if self.format is not None:
            d["format"] = self.format.to_dict()
        if self.concept_conflicts is not None:
            d["concept_conflicts"] = self.concept_conflicts.to_dict()
        return d


# Backward-compatible alias
QualityReport = QuestionQualityReport


def compare_spec_to_spec(
    candidate: dict,
    reference: dict,
    *,
    reference_path: str,
    threshold: float = THRESH_DUPLICATE,
) -> list[DuplicateEntry]:
    cand_items = spec_items(candidate)
    ref_items = spec_items(reference)
    out: list[DuplicateEntry] = []

    for c in cand_items:
        for r in ref_items:
            sim = text_similarity(c.text, r.text)
            if sim > threshold:
                out.append(
                    DuplicateEntry(
                        candidate_id=c.id,
                        reference=reference_path,
                        reference_id=r.id,
                        similarity=sim,
                        match_type=c.section if c.section == r.section else f"{c.section}/{r.section}",
                        candidate_text=c.text[:200],
                        reference_text=r.text[:200],
                    )
                )

    best: dict[tuple[str, str], DuplicateEntry] = {}
    for d in out:
        key = (d.candidate_id, d.reference)
        if key not in best or d.similarity > best[key].similarity:
            best[key] = d
    return sorted(best.values(), key=lambda x: (-x.similarity, x.candidate_id))


DSE_ICT_BANK_MCQ_SLUGS = ("Paper1_MultipleChoice", "Paper1A_MultipleChoice")
DSE_ICT_BANK_WRITTEN_SLUGS = (
    "Paper1B_CompulsoryStructured",
    "Paper2A_Database",
    "Paper2_Elective",
    "Paper2D_SoftwareDevelopment",
)


def _load_dse_ict_bank_items(
    slugs: tuple[str, ...],
    *,
    years: tuple[str, ...] = ("2021", "2022", "2023", "2024", "2025"),
    bank_root: Path | None = None,
) -> list[dict]:
    root = bank_root or Path(__file__).resolve().parents[2] / "Subjects/DSE-ICT/question-bank"
    items: list[dict] = []
    for year in years:
        for slug in slugs:
            path = root / year / slug / "questions.json"
            if not path.exists():
                continue
            data = json.loads(path.read_text(encoding="utf-8"))
            items.extend(data.get("items", []))
    return items


def load_dse_ict_bank_mcq_spec(
    *,
    years: tuple[str, ...] = ("2021", "2022", "2023", "2024", "2025"),
    bank_root: Path | None = None,
) -> dict:
    """Merge DSE Paper1 MCQ question-bank JSON into one spec-shaped dict."""
    items = _load_dse_ict_bank_items(DSE_ICT_BANK_MCQ_SLUGS, years=years, bank_root=bank_root)
    return {"meta": {"source": "DSE-ICT/question-bank (MCQ)"}, "items": items}


def load_dse_ict_bank_written_spec(
    *,
    years: tuple[str, ...] = ("2021", "2022", "2023", "2024", "2025"),
    bank_root: Path | None = None,
) -> dict:
    """Merge DSE Paper1B / Paper2 written question-bank JSON into one spec-shaped dict."""
    items = _load_dse_ict_bank_items(DSE_ICT_BANK_WRITTEN_SLUGS, years=years, bank_root=bank_root)
    return {"meta": {"source": "DSE-ICT/question-bank (written)"}, "items": items}


def load_dse_ict_bank_spec(
    *,
    years: tuple[str, ...] = ("2021", "2022", "2023", "2024", "2025"),
    bank_root: Path | None = None,
) -> dict:
    """MCQ + 乙丙 structured bank merged for duplicate / similarity checks."""
    mcq = load_dse_ict_bank_mcq_spec(years=years, bank_root=bank_root)
    written = load_dse_ict_bank_written_spec(years=years, bank_root=bank_root)
    return {
        "meta": {"source": "DSE-ICT/question-bank"},
        "items": mcq["items"] + written["items"],
    }


def compare_spec_to_dse_bank(
    candidate: dict,
    *,
    threshold: float = THRESH_DUPLICATE,
    bank_root: Path | None = None,
) -> list[DuplicateEntry]:
    """Flag exam items too close to DSE question-bank (MCQ + 乙丙 written)."""
    ref = load_dse_ict_bank_spec(bank_root=bank_root)
    return compare_spec_to_spec(
        candidate,
        ref,
        reference_path="DSE-ICT/question-bank",
        threshold=threshold,
    )


def compare_intra_spec(
    candidate: dict,
    *,
    threshold: float = THRESH_DUPLICATE,
) -> list[DuplicateEntry]:
    """Detect duplicate question pairs within the same exam spec (all sections)."""
    cand_items = spec_items(candidate)
    out: list[DuplicateEntry] = []
    for i, a in enumerate(cand_items):
        for b in cand_items[i + 1 :]:
            if _is_section_header(a.text) or _is_section_header(b.text):
                continue
            if a.id.startswith("d-fill-") and b.id.startswith("d-fill-"):
                continue
            cross = a.section != b.section
            thresh = THRESH_INTRA_CROSS if cross else threshold
            sim = text_similarity(a.text, b.text)
            if sim > thresh:
                out.append(
                    DuplicateEntry(
                        candidate_id=a.id,
                        reference="(within exam)",
                        reference_id=b.id,
                        similarity=sim,
                        match_type="intra_spec" if not cross else "intra_cross_section",
                        candidate_text=a.text[:200],
                        reference_text=b.text[:200],
                    )
                )
    return sorted(out, key=lambda x: (-x.similarity, x.candidate_id))


def compare_intra_exam_docx(
    docx_path: Path,
    spec: Optional[dict] = None,
) -> list[DuplicateEntry]:
    """Intra-exam overlap / answer leaks from rendered DOCX (甲–戊)."""
    mcq_answers: Optional[list[str]] = None
    if spec is not None:
        from mcq_check import mcq_answers_from_spec

        entries, _ = mcq_answers_from_spec(spec)
        if entries:
            mcq_answers = [e.letter for e in entries]

    out: list[DuplicateEntry] = []
    for m in compare_intra_exam(docx_path, mcq_answers=mcq_answers):
        if m.match_type == "error":
            continue
        out.append(
            DuplicateEntry(
                candidate_id=m.candidate_label,
                reference="(within exam)",
                reference_id=m.reference_label,
                similarity=m.similarity,
                match_type=m.match_type,
                candidate_text=m.candidate_snippet[:200],
                reference_text=m.reference_snippet[:200],
            )
        )
    return out


def run_spec_check(
    candidate_spec_path: Path,
    *,
    template_spec_path: Optional[Path] = None,
    template_docx_path: Optional[Path] = None,
    past_papers_root: Optional[Path] = None,
    years: int = 3,
    subject_subpath: Optional[str] = None,
    extra_reference_specs: Optional[list[Path]] = None,
    extra_reference_docx: Optional[list[Path]] = None,
    threshold: float = THRESH_DUPLICATE,
) -> DuplicateReport:
    """Duplicate detection only (backward-compatible)."""
    report = run_question_check(
        candidate_spec_path,
        template_spec_path=template_spec_path,
        template_docx_path=template_docx_path,
        past_papers_root=past_papers_root,
        years=years,
        subject_subpath=subject_subpath,
        extra_reference_specs=extra_reference_specs,
        extra_reference_docx=extra_reference_docx,
        threshold=threshold,
        verify_concepts=False,
        verify_mcq=False,
    )
    return report.duplicates


def run_question_check(
    candidate_spec_path: Path,
    *,
    template_spec_path: Optional[Path] = None,
    template_docx_path: Optional[Path] = None,
    candidate_docx_path: Optional[Path] = None,
    past_papers_root: Optional[Path] = None,
    years: int = 3,
    subject_subpath: Optional[str] = None,
    extra_reference_specs: Optional[list[Path]] = None,
    extra_reference_docx: Optional[list[Path]] = None,
    threshold: float = THRESH_DUPLICATE,
    verify_concepts: bool = True,
    verify_mcq: bool = True,
    verify_format: bool = True,
    verify_concept_conflicts: bool = True,
) -> QuestionQualityReport:
    candidate_spec_path = candidate_spec_path.expanduser().resolve()
    candidate = load_spec(candidate_spec_path)

    if subject_subpath is None:
        subject_subpath = candidate.get("meta", {}).get("subject") or infer_subject_subpath(candidate_spec_path)

    refs: list[tuple[str, dict]] = []
    template_spec: Optional[dict] = None
    template_label: Optional[str] = None

    if template_spec_path:
        p = template_spec_path.expanduser().resolve()
        template_spec = load_spec(p)
        template_label = str(p)
        refs.append((str(p), template_spec))
    elif template_docx_path:
        p = template_docx_path.expanduser().resolve()
        template_spec = docx_to_spec(p)
        template_label = str(p)
        refs.append((str(p), template_spec))

    if past_papers_root:
        for p in discover_past_papers(
            past_papers_root,
            years=years,
            subject_subpath=subject_subpath,
            include_candidate=None,
        ):
            refs.append((str(p), docx_to_spec(p)))

    for p in extra_reference_specs or []:
        p = p.expanduser().resolve()
        refs.append((str(p), load_spec(p)))
    for p in extra_reference_docx or []:
        p = p.expanduser().resolve()
        refs.append((str(p), docx_to_spec(p)))

    seen: set[str] = set()
    unique_refs: list[tuple[str, dict]] = []
    for label, spec in refs:
        if label in seen:
            continue
        seen.add(label)
        unique_refs.append((label, spec))

    dup_report = DuplicateReport(
        candidate=str(candidate_spec_path),
        threshold=threshold,
        references_checked=[label for label, _ in unique_refs],
    )

    for label, ref_spec in unique_refs:
        dup_report.duplicates.extend(
            compare_spec_to_spec(candidate, ref_spec, reference_path=label, threshold=threshold)
        )
    meta = candidate.get("meta") or {}
    if meta.get("dse_sources") or meta.get("style_guide"):
        dup_report.duplicates.extend(compare_spec_to_dse_bank(candidate, threshold=threshold))
        if "DSE-ICT/question-bank" not in dup_report.references_checked:
            dup_report.references_checked.append("DSE-ICT/question-bank")
    dup_report.duplicates.extend(compare_intra_spec(candidate, threshold=threshold))
    docx_path = candidate_docx_path
    if docx_path is None and candidate_spec_path.with_suffix(".docx").exists():
        docx_path = candidate_spec_path.with_suffix(".docx")
    if docx_path is not None and docx_path.exists():
        dup_report.duplicates.extend(compare_intra_exam_docx(docx_path, candidate))
    dup_report.duplicates.sort(key=lambda d: (-d.similarity, d.candidate_id))

    quality = QuestionQualityReport(
        candidate=str(candidate_spec_path),
        threshold=threshold,
        duplicates=dup_report,
    )

    if verify_concepts:
        if template_spec is not None:
            quality.concepts = run_concept_check(
                candidate,
                template_spec,
                candidate_label=str(candidate_spec_path),
                reference_label=template_label or "",
            )
        else:
            dist = compare_concept_distributions(candidate, None)
            core_errors = check_mcq_core_sequence(candidate)
            if dist.candidate.items_with_concepts > 0 or candidate.get("meta", {}).get("concept_targets") or core_errors:
                quality.concepts = ConceptCheckResult(
                    candidate=str(candidate_spec_path),
                    reference="",
                    ok=True,
                    distribution=dist,
                    core_sequence_errors=core_errors,
                )

    if verify_mcq:
        docx_path = candidate_docx_path
        if docx_path is None and candidate_spec_path.with_suffix(".docx").exists():
            docx_path = candidate_spec_path.with_suffix(".docx")
        quality.mcq = check_mcq(
            spec=candidate,
            spec_path=candidate_spec_path,
            docx_path=docx_path,
        )
        quality.answer_patterns = check_all_answer_patterns(candidate)

    if verify_format:
        spec_fmt = check_spec_format(candidate)
        docx_path = candidate_docx_path
        if docx_path is None and candidate_spec_path.with_suffix(".docx").exists():
            docx_path = candidate_spec_path.with_suffix(".docx")
        if docx_path is not None and docx_path.exists():
            docx_fmt = check_exam_format(docx_path)
            quality.format = FormatCheckResult(
                ok=spec_fmt.ok and docx_fmt.ok,
                backtick_hits=list(dict.fromkeys(spec_fmt.backtick_hits + docx_fmt.backtick_hits)),
                mcq_indent_issues=docx_fmt.mcq_indent_issues,
            )
        else:
            quality.format = spec_fmt

    if verify_concept_conflicts:
        quality.concept_conflicts = check_concept_conflicts(candidate)

    return quality


# Alias for callers that used run_quality_check
run_quality_check = run_question_check


def format_spec_report_text(report: DuplicateReport) -> str:
    pct = int(report.threshold * 100)
    lines = [
        f"Candidate spec: {report.candidate}",
        f"References checked: {len(report.references_checked)}",
        f"Rule: similarity > {pct}% → duplicate (cross-id matching)",
        f"Cross-section within exam: similarity > {int(THRESH_INTRA_CROSS * 100)}% also flagged",
        f"Also checks rendered DOCX for 甲–戊 overlap and MCQ answer leaks",
        f"Spec also checks cross-section concept conflicts (same topic in 甲 + 乙–戊)",
        f"Duplicates: {len(report.duplicates)}",
        f"IDs to regenerate: {', '.join(report.regenerate_ids) or '(none)'}",
        "",
    ]
    if not report.duplicates:
        lines.append(f"No duplicates (all pairs ≤ {pct}% similarity).")
        return "\n".join(lines)

    lines.append("All duplicates:")
    for d in report.duplicates:
        lines.append(
            f"\n[{d.similarity:.0%}] {d.candidate_id} ↔ {d.reference_id} "
            f"({d.match_type})"
        )
        lines.append(f"  Ref: {Path(d.reference).name}")
        lines.append(f"  Cand: {d.candidate_text}")
        lines.append(f"  Ref:  {d.reference_text}")
    return "\n".join(lines)


def format_quality_report_text(report: QuestionQualityReport) -> str:
    sections = [
        "=== Duplicate check (past papers + template) ===",
        format_spec_report_text(report.duplicates),
    ]
    if report.concepts is not None:
        sections.extend(["", "=== Concept alignment (vs template) ===", format_concept_report(report.concepts)])
    if report.mcq is not None:
        sections.extend(["", "=== MCQ answers (balance + pattern) ===", format_mcq_report(report.mcq)])
    if report.answer_patterns is not None:
        sections.extend(["", "=== All answer keys (randomness) ===", format_all_patterns_report(report.answer_patterns)])
    if report.format is not None:
        sections.extend(["", "=== Format (quotes + MCQ indent) ===", format_format_report(report.format)])
    if report.concept_conflicts is not None:
        sections.extend(
            [
                "",
                "=== Concept conflicts (cross-section) ===",
                format_concept_conflict_report(report.concept_conflicts),
            ]
        )
    sections.append("")
    sections.append(f"Overall: {'PASS' if report.ok else 'ISSUES FOUND'}")
    return "\n".join(sections)


def write_duplicate_report_json(report: DuplicateReport, path: Path) -> None:
    path = path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    import json

    path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")


def write_quality_report_json(report: QuestionQualityReport, path: Path) -> None:
    path = path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    import json

    path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")


def report_exit_code(report: DuplicateReport | QuestionQualityReport, *, strict: bool = False) -> int:
    if isinstance(report, QuestionQualityReport):
        has_issues = not report.ok
    else:
        has_issues = report.has_duplicates
    if not has_issues:
        return 0
    return 2 if strict else 1
