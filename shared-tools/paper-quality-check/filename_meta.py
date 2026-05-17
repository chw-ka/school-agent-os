"""Infer exam metadata from standard past-paper filenames."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# e.g. 25_26_S3_CMP_Term02_Exam.docx, 25_26_S5_ICT_Exam02_Blueprint_DB-Web.docx
_FILENAME_RE = re.compile(
    r"^(?P<y1>\d{2})[_-](?P<y2>\d{2})_(?P<form>S\d+)_(?P<subject>CMP|ICT)_(?P<rest>.+?)(?:\.docx|\.spec\.json)?$",
    re.IGNORECASE,
)

_LEVEL_ZH = {
    "S2": "中二級",
    "S3": "中三級",
    "S4": "中四級",
    "S5": "中五級",
    "S6": "中六級",
}

_SUBJECT_ZH = {
    "CMP": "電腦認知",
    "ICT": "資訊及通訊科技",
}

_TERM_ZH = {
    "term01": "上學期考試",
    "term02": "下學期考試",
    "exam01": "上學期考試",
    "exam02": "下學期考試",
}


@dataclass(frozen=True)
class InferredExamMeta:
    """Expected cover/footer fields derived from filename."""

    academic_year: str  # 2025-2026
    year_term_cover: str  # 2025 – 2026 下學期考試
    level_zh: str  # 中三級
    subject_zh: str  # 電腦認知
    level_line: str  # 中三級 電腦認知
    form: str  # S3
    subject_code: str  # CMP
    term_exam: str  # 下學期考試
    paper_title: str  # 試題簿
    source_filename: str = ""

    def footer_meta(self) -> dict[str, str]:
        return {
            "academic_year": self.academic_year,
            "level": self.level_zh,
            "term_exam": self.term_exam,
            "subject": self.subject_zh,
        }


def _academic_year(y1: str, y2: str) -> tuple[str, str]:
    century = "20"
    full = f"{century}{y1}-{century}{y2}"
    cover = f"{century}{y1} – {century}{y2}"
    return full, cover


def _infer_term_and_paper(rest: str) -> tuple[str, str]:
    low = rest.lower().replace("-", "_")
    term = ""
    paper = "試題簿"

    if "mock" in low or "practicalmock" in low.replace("_", ""):
        paper = "模擬試卷" if "practical" not in low else "實習模擬試"
        if "term01" in low or "exam01" in low:
            term = _TERM_ZH["term01"]
        elif "term02" in low or "exam02" in low:
            term = _TERM_ZH["term02"]
        return term or "模擬試驗", paper

    for key, label in _TERM_ZH.items():
        if key in low:
            term = label
            break

    if not term and re.search(r"exam0?2", low):
        term = _TERM_ZH["exam02"]
    elif not term and re.search(r"exam0?1", low):
        term = _TERM_ZH["exam01"]

    if "written" in low:
        paper = "筆試試題"
    elif "exam" in low or "blueprint" in low:
        paper = "試題簿"

    return term or "", paper


def infer_exam_meta_from_path(path: Path | str) -> Optional[InferredExamMeta]:
    """Parse 25_26_S3_CMP_Term02_Exam-style filenames; return None if unrecognized."""
    name = Path(path).name
    stem = name
    if stem.endswith(".spec.json"):
        stem = stem[: -len(".spec.json")]
    elif "." in stem:
        stem = Path(stem).stem

    m = _FILENAME_RE.match(stem)
    if not m:
        return None

    form = m.group("form").upper()
    subject = m.group("subject").upper()
    level_zh = _LEVEL_ZH.get(form)
    subject_zh = _SUBJECT_ZH.get(subject)
    if not level_zh or not subject_zh:
        return None

    academic_year, year_cover = _academic_year(m.group("y1"), m.group("y2"))
    term_exam, paper_title = _infer_term_and_paper(m.group("rest"))
    if not term_exam:
        return None

    year_term_cover = f"{year_cover} {term_exam}"
    return InferredExamMeta(
        academic_year=academic_year,
        year_term_cover=year_term_cover,
        level_zh=level_zh,
        subject_zh=subject_zh,
        level_line=f"{level_zh} {subject_zh}",
        form=form,
        subject_code=subject,
        term_exam=term_exam,
        paper_title=paper_title,
        source_filename=name,
    )
