"""HKDSE ICT past-paper file naming (legacy short codes → descriptive names)."""
from __future__ import annotations

import re
from pathlib import Path

# Loose files at past-papers/ root: {year}-1A.pdf, {year}-1B.pdf, {year}-2.pdf
SHORT_ROOT_PARTS: dict[str, str] = {
    "1a": "Paper1A_MultipleChoice",
    "1b": "Paper1B_CompulsoryStructured",
    "2": "Paper2_Elective",
}

# Legacy HKEAA filename → stable slug (used in question-bank folders too)
PAPER_SLUGS: dict[str, str] = {
    "p1.pdf": "Paper1_MultipleChoice",
    "p2a.pdf": "Paper2A_Database",
    "p2b.pdf": "Paper2B_DataCommunicationsNetworking",
    "p2c.pdf": "Paper2C_MultimediaWebsiteConstruction",
    "p2d.pdf": "Paper2D_SoftwareDevelopment",
    "ans.pdf": "MarkingScheme",
    "per.pdf": "PerformanceReport",
}

# Pre-2025 Paper 2 = elective part (one booklet per option). See HKEAA sample papers
# and EDB C&A Guide elective modules A–D (2012–2024 syllabus).
PAPER_LABELS: dict[str, str] = {
    "Paper1_MultipleChoice": "Paper 1A — Compulsory Part MCQ (必修部分 甲部)",
    "Paper1A_MultipleChoice": "Paper 1A — Compulsory Part MCQ (必修部分 甲部)",
    "Paper1B_CompulsoryStructured": "Paper 1B — Compulsory Part structured (必修部分 乙丙部)",
    "Paper2_Elective": "Paper 2 — Elective sections (選修部分，2025+ 三選一)",
    "Paper2A_Database": "Paper 2A — Database (數據庫)",
    "Paper2B_DataCommunicationsNetworking": "Paper 2B — Data Communications and Networking (數據通訊及建網)",
    "Paper2C_MultimediaWebsiteConstruction": "Paper 2C — Multimedia Production and Website Construction (多媒體製作及網站建構)",
    "Paper2D_SoftwareDevelopment": "Paper 2D — Software Development (軟件開發)",
    "MarkingScheme": "Marking Scheme (評卷參考)",
    "PerformanceReport": "Performance Report (考生表現)",
}

# Wrong slugs from an earlier rename pass (compulsory-module names).
SLUG_LEGACY_ALIASES: dict[str, str] = {
    "Paper2A_InformationProcessing": "Paper2A_Database",
    "Paper2B_ComputerSystems": "Paper2B_DataCommunicationsNetworking",
    "Paper2C_Networking": "Paper2C_MultimediaWebsiteConstruction",
    "Paper2D_Elective": "Paper2D_SoftwareDevelopment",
}

QUESTION_PAPERS = frozenset(
    {
        "Paper1_MultipleChoice",
        "Paper1A_MultipleChoice",
        "Paper1B_CompulsoryStructured",
        "Paper2_Elective",
        "Paper2A_Database",
        "Paper2B_DataCommunicationsNetworking",
        "Paper2C_MultimediaWebsiteConstruction",
        "Paper2D_SoftwareDevelopment",
    }
)

FOLDER_ALIASES = {
    "Practice Paper": "Practice-Paper",
    "Sample Paper": "Sample-Paper",
}


def normalize_paper_slug(slug: str) -> str:
    return SLUG_LEGACY_ALIASES.get(slug, slug)


def short_root_paper(name: str) -> tuple[str, str] | None:
    """Parse loose root PDFs like 2025-1A.pdf → (year, slug)."""
    m = re.match(r"^(\d{4})-(1a|1b|2)\.pdf$", name, re.I)
    if not m:
        return None
    part = m.group(2).lower()
    slug = SHORT_ROOT_PARTS.get(part)
    if slug is None:
        return None
    return m.group(1), slug


def paper_slug_from_name(name: str) -> str | None:
    lower = name.lower()
    if lower in PAPER_SLUGS:
        return PAPER_SLUGS[lower]
    short = short_root_paper(name)
    if short:
        return short[1]
    m = re.match(r"^DSE_ICT_(?:\d{4}|Practice|Sample)_(.+)\.pdf$", name, re.I)
    if m:
        return normalize_paper_slug(m.group(1))
    return None


def descriptive_pdf_name(*, label: str, slug: str) -> str:
    return f"DSE_ICT_{label}_{slug}.pdf"


def past_paper_folder(year_label: str) -> str:
    if year_label == "Practice":
        return "Practice-Paper"
    if year_label == "Sample":
        return "Sample-Paper"
    return year_label


def past_paper_pdf_path(past_root: Path, year_label: str, slug: str) -> Path:
    return past_root / past_paper_folder(year_label) / descriptive_pdf_name(label=year_label, slug=slug)


def fix_paper2_slug_renames(root: Path) -> list[tuple[Path, Path]]:
    """Rename PDFs that used incorrect compulsory-module slugs."""
    root = root.expanduser().resolve()
    moves: list[tuple[Path, Path]] = []

    for folder in sorted(root.iterdir()):
        if not folder.is_dir():
            continue
        label = folder.name
        if not (re.fullmatch(r"\d{4}", label) or label in ("Practice-Paper", "Sample-Paper")):
            continue

        for old_slug, new_slug in SLUG_LEGACY_ALIASES.items():
            for pdf in sorted(folder.glob(f"DSE_ICT_*_{old_slug}.pdf")):
                new_name = pdf.name.replace(old_slug, new_slug)
                dst = folder / new_name
                if pdf.name == new_name or dst.exists():
                    continue
                pdf.rename(dst)
                moves.append((pdf, dst))

    return moves


def organize_loose_root_pdfs(root: Path) -> list[tuple[Path, Path]]:
    """Move {year}-1A.pdf / -1B.pdf / -2.pdf from past-papers/ root into year folders."""
    root = root.expanduser().resolve()
    moves: list[tuple[Path, Path]] = []

    for pdf in sorted(root.glob("*.pdf")):
        parsed = short_root_paper(pdf.name)
        if not parsed:
            continue
        year_label, slug = parsed
        folder = root / past_paper_folder(year_label)
        folder.mkdir(parents=True, exist_ok=True)
        dst = folder / descriptive_pdf_name(label=year_label, slug=slug)
        if dst.exists():
            continue
        pdf.rename(dst)
        moves.append((pdf, dst))

    return moves


def rename_past_papers(root: Path) -> list[tuple[Path, Path]]:
    """Rename legacy PDFs and year/special folders under past-papers/."""
    root = root.expanduser().resolve()
    moves: list[tuple[Path, Path]] = []

    moves.extend(organize_loose_root_pdfs(root))

    for old_folder, new_folder in FOLDER_ALIASES.items():
        src = root / old_folder
        dst = root / new_folder
        if src.exists() and not dst.exists():
            src.rename(dst)
            moves.append((src, dst))

    for folder in sorted(root.iterdir()):
        if not folder.is_dir():
            continue
        label = folder.name
        if re.fullmatch(r"\d{4}", label):
            year_label = label
        elif label in ("Practice-Paper", "Sample-Paper"):
            year_label = "Practice" if "Practice" in label else "Sample"
        else:
            continue

        for pdf in sorted(folder.glob("*.pdf")):
            slug = paper_slug_from_name(pdf.name)
            if slug is None:
                continue
            new_name = descriptive_pdf_name(label=year_label, slug=slug)
            dst = folder / new_name
            if pdf.name != new_name and not dst.exists():
                pdf.rename(dst)
                moves.append((pdf, dst))

    moves.extend(fix_paper2_slug_renames(root))
    return moves
