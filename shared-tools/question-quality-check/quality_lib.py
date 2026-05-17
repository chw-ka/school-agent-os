"""
Reusable exam paper similarity comparison (DOCX / PDF).

Rule: similarity **greater than 60%** → treated as the same question (duplicate).
Comparisons are **cross-number**: MCQ#3 on the new paper can match MCQ#15 on a reference.
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from typing import Iterable, Optional

try:
    from docx import Document
except ImportError as e:  # pragma: no cover
    raise ImportError("question-quality-check requires python-docx. Install: pip install python-docx") from e


# Similarity **>** this value ⇒ duplicate (「多於 60%」)
THRESH_DUPLICATE = 0.60

STOP_MARKERS = ("試卷完", "附表", "下期考試答案", "本擬題稿", "2024-2025 年度", "－　試卷完")

EXCLUDE_NAME_PARTS = (
    "answer",
    "ans",
    "mock",
    "practical",
    "sample",
    "backup",
    "任務",
    "sp_dse",
    "full_sp",
)

INCLUDE_NAME_PARTS = ("exam", "試題", "writtenexam", "paper")

# Legacy aliases for CLI help text
THRESH_EXACT = THRESH_DUPLICATE
THRESH_SIMILAR = THRESH_DUPLICATE
THRESH_PARTIAL = THRESH_DUPLICATE


@dataclass(frozen=True)
class Match:
    reference: str
    match_type: str  # mcq_stem | mcq_full | written | line | section
    similarity: float
    candidate_label: str
    reference_label: str
    candidate_snippet: str
    reference_snippet: str

    def is_duplicate(self) -> bool:
        return self.similarity > THRESH_DUPLICATE

    def severity(self) -> str:
        return "duplicate" if self.is_duplicate() else "ok"


@dataclass
class CompareReport:
    candidate: str
    template: Optional[str]
    references_checked: list[str] = field(default_factory=list)
    matches: list[Match] = field(default_factory=list)
    threshold: float = THRESH_DUPLICATE

    @property
    def duplicate_count(self) -> int:
        return sum(1 for m in self.matches if m.is_duplicate())

    @property
    def exact_count(self) -> int:
        return self.duplicate_count

    @property
    def similar_count(self) -> int:
        return self.duplicate_count

    def to_dict(self) -> dict:
        d = asdict(self)
        d["matches"] = [asdict(m) for m in self.matches]
        d["summary"] = {
            "threshold": self.threshold,
            "duplicate": self.duplicate_count,
            "rule": f"similarity > {self.threshold:.0%} treated as same question",
        }
        return d

    def exit_code(self, *, fail_on_exact: bool = False, fail_on_similar: bool = False) -> int:
        """
        0 = no duplicates
        1 = duplicates found (full report; default, non-blocking)
        2 = strict abort (fail_on_exact or fail_on_similar)
        """
        if self.duplicate_count == 0:
            return 0
        if fail_on_exact or fail_on_similar:
            return 2
        return 1


def normalize_text(s: str) -> str:
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"[（）()【】\[\]「」""''\'\t]", "", s)
    return s.lower()


def text_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, normalize_text(a), normalize_text(b)).ratio()


def is_option_line(t: str) -> bool:
    s = t.lstrip()
    return len(s) >= 2 and s[0] in "ABCD" and s[1] == "."


def _read_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as e:
        raise ImportError("PDF support requires pypdf. Install: pip install pypdf") from e
    reader = PdfReader(str(path))
    return "\n".join((p.extract_text() or "") for p in reader.pages)


def extract_lines(path: Path) -> list[str]:
    path = path.expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(path)

    if path.suffix.lower() == ".docx":
        doc = Document(str(path))
        lines: list[str] = []
        for p in doc.paragraphs:
            t = p.text.strip()
            if t:
                lines.append(t)
        for tbl in doc.tables:
            for row in tbl.rows:
                for cell in row.cells:
                    t = cell.text.strip()
                    if t:
                        lines.append(t)
        return _trim_exam_body(lines)

    if path.suffix.lower() == ".pdf":
        raw = _read_pdf(path)
        lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
        return _trim_exam_body(lines)

    raise ValueError(f"Unsupported format: {path.suffix}")


def _trim_exam_body(lines: list[str]) -> list[str]:
    out: list[str] = []
    for t in lines:
        if any(m in t for m in STOP_MARKERS):
            break
        out.append(t)
    return out


def extract_mcq_stems(lines: list[str]) -> list[dict]:
    """Each MCQ: {index, stem, full} — index is position in paper only (for display)."""
    stems: list[dict] = []
    i = 0
    qn = 0
    while i < len(lines):
        if "乙部" in lines[i]:
            break
        if "甲部" in lines[i] or "多項選擇" in lines[i]:
            i += 1
            continue
        if is_option_line(lines[i]) or len(lines[i]) < 6:
            i += 1
            continue
        parts: list[str] = []
        while i < len(lines) and not is_option_line(lines[i]) and "乙部" not in lines[i]:
            if lines[i] and "甲部" not in lines[i]:
                parts.append(lines[i])
            i += 1
        opts: list[str] = []
        while i < len(lines) and is_option_line(lines[i]):
            opts.append(lines[i])
            i += 1
        if parts and opts:
            qn += 1
            stem = "\n".join(parts)
            stems.append({"index": qn, "stem": stem, "full": "\n".join(parts + opts)})
    return stems


def _section_lines(lines: list[str], start_kw: str, end_kws: tuple[str, ...]) -> list[str]:
    buf: list[str] = []
    active = False
    for t in lines:
        if start_kw in t:
            active = True
            continue
        if active and any(k in t for k in end_kws):
            break
        if active:
            buf.append(t)
    return buf


def extract_written_units(lines: list[str]) -> list[dict]:
    """
    Extract 乙/丙 question units for cross-number comparison.
    Splits on numbered main questions (1. 2.) or keeps (a)(b) groups with context.
    """
    units: list[dict] = []
    uid = 0

    for sec_name, end_kws in (("乙部", ("丙部",)), ("丙部", ("試卷完", "附表"))):
        sec_lines = _section_lines(lines, sec_name, end_kws)
        if not sec_lines:
            continue

        current: list[str] = []
        label = ""

        def flush() -> None:
            nonlocal uid, current, label
            text = "\n".join(current).strip()
            if len(normalize_text(text)) < 20:
                current = []
                return
            uid += 1
            units.append(
                {
                    "index": uid,
                    "section": sec_name,
                    "label": label or f"{sec_name}#{uid}",
                    "text": text,
                }
            )
            current = []

        for t in sec_lines:
            if _is_boilerplate_line(t) and "分)" not in t and "分）" not in t:
                continue
            if re.match(r"^\d+\.\s", t):
                flush()
                label = f"{sec_name}-{t.split(chr(9))[0].strip()[:20]}"
                current = [t]
            elif re.match(r"^\([a-z]\)", t, re.I) and len(t) > 25:
                if current and len(current) > 3:
                    flush()
                label = f"{sec_name}-{t[:24]}"
                current.append(t)
            else:
                if t:
                    current.append(t)

        flush()

    return units


def _is_boilerplate_line(t: str) -> bool:
    if len(t) < 12:
        return True
    if is_option_line(t):
        return True
    # Generic MCQ option patterns — not substantive unique content
    s = t.lstrip()
    if re.match(r"^[ABCD]\.\s*只有\s*\(", s):
        return True
    boiler = (
        "甲部",
        "多項選擇",
        "請選擇最合適",
        "HB 鉛筆",
        "乙部",
        "丙部",
        "丁部",
        "戊部",
        "配對題",
        "填充題",
        "是非題",
        "短答題",
        "核心單元",
        "選修單元",
        "試題答題簿",
        "考生須知",
        "評分準則",
        "選修 A",
        "選修 B",
        "請判斷下列",
        "請在空格",
        "將最合適的答案",
        "從字庫中選擇",
        "班別：",
        "姓名：",
        "________________",
    )
    if any(b in t for b in boiler) and len(t) < 50:
        return True
  # Cover / instruction blocks (shared across term papers from same template)
    if any(
        x in t
        for x in (
            "迦密聖道中學",
            "試題簿",
            "考生須知",
            "時限:",
            "頁數:",
            "總分:",
            "學期考試",
            "評分準則",
        )
    ):
        return True
    if re.match(r"^\d{4}\s*[–\-]\s*\d{4}", t.strip()):
        return True
    return False


def _add_match(matches: list[Match], m: Match) -> None:
    matches.append(m)


def compare_documents(
    candidate_path: Path,
    reference_path: Path,
    *,
    reference_label: Optional[str] = None,
    template_mode: bool = False,
) -> list[Match]:
    ref_label = reference_label or str(reference_path)
    cand_lines = extract_lines(candidate_path)
    ref_lines = extract_lines(reference_path)

    matches: list[Match] = []

    cand_mcq = extract_mcq_stems(cand_lines)
    ref_mcq = extract_mcq_stems(ref_lines)

    # MCQ: cross-number (all pairs, not same index only)
    for c in cand_mcq:
        for r in ref_mcq:
            for field_name, match_type in (("stem", "mcq_stem"), ("full", "mcq_full")):
                sim = text_similarity(c[field_name], r[field_name])
                if sim > THRESH_DUPLICATE:
                    _add_match(
                        matches,
                        Match(
                            reference=ref_label,
                            match_type=match_type,
                            similarity=sim,
                            candidate_label=f"MCQ#{c['index']}",
                            reference_label=f"MCQ#{r['index']}",
                            candidate_snippet=c[field_name].replace("\n", " ")[:160],
                            reference_snippet=r[field_name].replace("\n", " ")[:160],
                        ),
                    )

    # 乙/丙 written units: cross-number
    if not template_mode:
        cand_w = extract_written_units(cand_lines)
        ref_w = extract_written_units(ref_lines)
        for c in cand_w:
            for r in ref_w:
                sim = text_similarity(c["text"], r["text"])
                if sim > THRESH_DUPLICATE:
                    _add_match(
                        matches,
                        Match(
                            reference=ref_label,
                            match_type="written",
                            similarity=sim,
                            candidate_label=c["label"],
                            reference_label=r["label"],
                            candidate_snippet=c["text"].replace("\n", " ")[:160],
                            reference_snippet=r["text"].replace("\n", " ")[:160],
                        ),
                    )

    # Line-level: cross-position (different line numbers OK)
    for i, cl in enumerate(cand_lines):
        if _is_boilerplate_line(cl):
            continue
        for j, rl in enumerate(ref_lines):
            if _is_boilerplate_line(rl):
                continue
            sim = text_similarity(cl, rl)
            if sim > THRESH_DUPLICATE:
                _add_match(
                    matches,
                    Match(
                        reference=ref_label,
                        match_type="line",
                        similarity=sim,
                        candidate_label=f"line:{i}",
                        reference_label=f"line:{j}",
                        candidate_snippet=cl[:120],
                        reference_snippet=rl[:120],
                    ),
                )

    # Section-level (whole 乙/丙) — only for past papers, not template layout
    if not template_mode:
        for sec, end in (("乙部", ("丙部",)), ("丙部", ("試卷完", "附表"))):
            cs = "\n".join(_section_lines(cand_lines, sec, end))
            rs = "\n".join(_section_lines(ref_lines, sec, end))
            if cs and rs:
                sim = text_similarity(cs, rs)
                if sim > THRESH_DUPLICATE:
                    _add_match(
                        matches,
                        Match(
                            reference=ref_label,
                            match_type="section",
                            similarity=sim,
                            candidate_label=sec,
                            reference_label=sec,
                            candidate_snippet=cs[:120],
                            reference_snippet=rs[:120],
                        ),
                    )

    # Dedupe: keep strongest match per (candidate_label, reference file, match_type)
    best: dict[tuple, Match] = {}
    for m in matches:
        key = (m.match_type, m.candidate_label, m.reference)
        if key not in best or m.similarity > best[key].similarity:
            best[key] = m
    return sorted(best.values(), key=lambda m: (-m.similarity, m.reference))


def parse_academic_year(folder_name: str) -> Optional[int]:
    m = re.match(r"^(\d{4})-(\d{4})$", folder_name)
    if not m:
        return None
    return int(m.group(1))


def discover_past_papers(
    root: Path,
    *,
    years: int = 3,
    subject_subpath: Optional[str] = None,
    include_candidate: Optional[Path] = None,
) -> list[Path]:
    root = root.expanduser().resolve()
    if not root.is_dir():
        return []

    year_dirs: list[tuple[int, Path]] = []
    for p in sorted(root.iterdir()):
        if not p.is_dir():
            continue
        y = parse_academic_year(p.name)
        if y is not None:
            year_dirs.append((y, p))

    if not year_dirs:
        candidates = _filter_exam_files(root.rglob("*"))
    else:
        year_dirs.sort(key=lambda x: -x[0])
        selected_years = {y for y, _ in year_dirs[:years]}
        files: list[Path] = []
        for y, ydir in year_dirs:
            if y not in selected_years:
                continue
            files.extend(_filter_exam_files(ydir.rglob("*")))
        candidates = files

    if subject_subpath:
        sub = subject_subpath.replace("\\", "/").strip("/")
        candidates = [p for p in candidates if sub.lower() in str(p).replace("\\", "/").lower()]

    by_stem: dict[str, Path] = {}
    for p in sorted(candidates, key=lambda x: (x.suffix != ".docx", str(x))):
        stem = p.stem.lower()
        if stem not in by_stem:
            by_stem[stem] = p

    out = sorted(by_stem.values(), key=lambda p: str(p))
    if include_candidate:
        out = [p for p in out if p.resolve() != include_candidate.resolve()]
    return out


def _filter_exam_files(paths: Iterable[Path]) -> list[Path]:
    result: list[Path] = []
    for p in paths:
        if not p.is_file():
            continue
        if p.suffix.lower() not in (".docx", ".pdf"):
            continue
        name = p.name.lower()
        if any(x in name for x in EXCLUDE_NAME_PARTS):
            continue
        if not any(x in name for x in INCLUDE_NAME_PARTS):
            continue
        result.append(p)
    return result


def infer_subject_subpath(path: Path) -> Optional[str]:
    parts = path.parts
    for part in parts:
        if re.match(r"^F[2-6]\s", part) or part in ("F5 ICT", "S2 CMP", "S3 CMP"):
            return part
    return None


def run_full_check(
    candidate: Path,
    *,
    template: Optional[Path] = None,
    past_papers_root: Optional[Path] = None,
    years: int = 3,
    subject_subpath: Optional[str] = None,
    extra_references: Optional[list[Path]] = None,
) -> CompareReport:
    candidate = candidate.expanduser().resolve()
    if subject_subpath is None:
        subject_subpath = infer_subject_subpath(candidate)

    refs: list[Path] = []
    if template:
        refs.append(template.expanduser().resolve())
    if past_papers_root:
        refs.extend(
            discover_past_papers(
                past_papers_root,
                years=years,
                subject_subpath=subject_subpath,
                include_candidate=candidate,
            )
        )
    if extra_references:
        refs.extend([r.expanduser().resolve() for r in extra_references])

    seen: set[str] = set()
    unique_refs: list[Path] = []
    for r in refs:
        key = str(r.resolve())
        if key in seen or key == str(candidate):
            continue
        seen.add(key)
        if r.exists():
            unique_refs.append(r)

    report = CompareReport(
        candidate=str(candidate),
        template=str(template) if template else None,
        references_checked=[str(r) for r in unique_refs],
    )

    template_resolved = str(template.expanduser().resolve()) if template else None

    for ref in unique_refs:
        try:
            is_template = template_resolved is not None and str(ref.resolve()) == template_resolved
            report.matches.extend(
                compare_documents(
                    candidate,
                    ref,
                    reference_label=str(ref),
                    template_mode=is_template,
                )
            )
        except Exception as e:  # pragma: no cover
            report.matches.append(
                Match(
                    reference=str(ref),
                    match_type="error",
                    similarity=0.0,
                    candidate_label="",
                    reference_label="",
                    candidate_snippet=str(e),
                    reference_snippet="",
                )
            )

    return report


def format_report_text(report: CompareReport, *, min_similarity: float = THRESH_DUPLICATE) -> str:
    pct = int(THRESH_DUPLICATE * 100)
    lines = [
        f"Candidate: {report.candidate}",
        f"Template: {report.template or '(none)'}",
        f"References checked: {len(report.references_checked)}",
        f"Rule: similarity > {pct}% → same question (duplicate)",
        f"Duplicates found: {report.duplicate_count}",
        "Note: question numbers may differ (cross-number matching).",
        "",
    ]
    shown = [
        m
        for m in report.matches
        if m.is_duplicate() and m.similarity >= min_similarity and m.match_type != "error"
    ]
    shown.sort(key=lambda m: (-m.similarity, m.reference))

    if not shown:
        lines.append(f"No duplicates (all pairs ≤ {pct}% similarity).")
        return "\n".join(lines)

    lines.append("Duplicates:")
    for m in shown:
        lines.append(
            f"\n[DUPLICATE {m.similarity:.0%}] {m.match_type} "
            f"{m.candidate_label} ↔ {m.reference_label}"
        )
        lines.append(f"  Ref file: {Path(m.reference).name}")
        lines.append(f"  Cand: {m.candidate_snippet}")
        lines.append(f"  Ref:  {m.reference_snippet}")
    return "\n".join(lines)


def write_report_json(report: CompareReport, path: Path) -> None:
    path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
