"""Run question-quality-check + paper-quality-check on exam specs and DOCX."""
from __future__ import annotations

import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _ensure_paths() -> tuple[Path, Path]:
    root = Path(__file__).resolve().parents[1]
    qdir = root / "question-quality-check"
    pdir = root / "paper-quality-check"
    for d in (qdir, pdir):
        if str(d) not in sys.path:
            sys.path.insert(0, str(d))
    return qdir, pdir


def run_spec_check(
    *,
    candidate_spec: Path,
    template: Path | None = None,
    candidate_docx: Path | None = None,
    past_papers_root: Path | None = None,
    years: int = 3,
    subject_subpath: str | None = None,
    json_report: Path | None = None,
    strict: bool = False,
    skip_concepts: bool = False,
    skip_footer: bool = False,
    skip_cover: bool = False,
    skip_mcq: bool = False,
) -> int:
    """
    Full pre-render check: question (duplicates, concepts, answers) + paper (footer/cover if DOCX).
    Exit 0 = pass; 1 = issues; 2 = strict fail.
    """
    _ensure_paths()
    from check_spec import (
        format_quality_report_text as format_question_report,
        report_exit_code as question_exit_code,
        run_question_check,
        write_quality_report_json,
    )
    from check_paper import format_paper_report_text, run_paper_check

    root = past_papers_root or (repo_root() / "Subjects" / "PastPaper" / "CMP+ICT")
    spec_path = candidate_spec.expanduser().resolve()
    docx_path = candidate_docx.expanduser().resolve() if candidate_docx else None
    if docx_path is None and spec_path.with_suffix(".docx").exists():
        docx_path = spec_path.with_suffix(".docx")

    q_report = run_question_check(
        spec_path,
        template_docx_path=template.expanduser().resolve() if template else None,
        candidate_docx_path=docx_path,
        past_papers_root=root,
        years=years,
        subject_subpath=subject_subpath,
        verify_concepts=not skip_concepts,
        verify_mcq=not skip_mcq,
    )

    print("\n--- Question quality check (spec) ---")
    print(format_question_report(q_report))

    codes = [question_exit_code(q_report, strict=strict)]

    if docx_path is not None and docx_path.exists() and (not skip_footer or not skip_cover):
        p_report = run_paper_check(
            docx_path,
            candidate_spec_path=spec_path,
            template_docx_path=template.expanduser().resolve() if template else None,
            verify_footer=not skip_footer,
            verify_cover=not skip_cover,
        )
        print("\n--- Paper quality check (DOCX) ---")
        print(format_paper_report_text(p_report))
        from check_paper import report_exit_code as paper_exit_code

        codes.append(paper_exit_code(p_report, strict=strict))

    if json_report:
        import json

        payload = {"question": q_report.to_dict()}
        if docx_path and docx_path.exists():
            payload["paper"] = run_paper_check(
                docx_path,
                candidate_spec_path=spec_path,
                verify_footer=not skip_footer,
                verify_cover=not skip_cover,
            ).to_dict()
        json_report.expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
        json_report.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Quality report: {json_report}")
        if q_report.regenerate_ids:
            print(f"Regenerate IDs: {', '.join(q_report.regenerate_ids)}")

    code = max(codes)
    if code == 0:
        print("All checks passed.")
    elif code == 1:
        print("Issues listed above — revise spec then re-run.")
    else:
        print("Check FAILED (strict) — generation aborted.")
    return code


def run_post_generation_check(
    *,
    output: Path,
    template: Path,
    candidate_spec: Path | None = None,
    past_papers_root: Path | None = None,
    years: int = 3,
    subject_subpath: str | None = None,
    json_report: Path | None = None,
    fail_on_exact: bool = True,
    fail_on_similar: bool = False,
    skip_footer: bool = False,
    skip_cover: bool = False,
) -> int:
    """DOCX post-check: question (duplicates, concepts, MCQ) + paper (footer, cover)."""
    _ensure_paths()
    from check_docx import main as question_docx_main
    from check_paper import report_exit_code as paper_exit_code, run_paper_check

    out = output.expanduser().resolve()
    tmpl = template.expanduser().resolve()

    argv = [
        "--candidate",
        str(out),
        "--template",
        str(tmpl),
        "--years",
        str(years),
    ]
    if subject_subpath:
        argv.extend(["--subject", subject_subpath])
    if candidate_spec:
        argv.extend(["--candidate-spec", str(candidate_spec.expanduser().resolve())])
    if json_report:
        argv.extend(["--json", str(json_report)])
    if fail_on_exact or fail_on_similar:
        argv.append("--fail-on-duplicate")

    code = int(question_docx_main(argv))

    if not skip_footer or not skip_cover:
        p_report = run_paper_check(
            out,
            candidate_spec_path=candidate_spec.expanduser().resolve() if candidate_spec else None,
            template_docx_path=tmpl,
            verify_footer=not skip_footer,
            verify_cover=not skip_cover,
        )
        print("\n--- Paper quality check (DOCX) ---")
        from check_paper import format_paper_report_text

        print(format_paper_report_text(p_report))
        paper_code = paper_exit_code(p_report)
        code = max(code, paper_code)

    return code
