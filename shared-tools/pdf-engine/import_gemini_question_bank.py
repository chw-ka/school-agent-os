#!/usr/bin/env python3
"""Import Gemini-extracted DSE ICT JSON into question-bank format."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_SHARED = Path(__file__).resolve().parents[1]
if str(_SHARED) not in sys.path:
    sys.path.insert(0, str(_SHARED))

from dse_ict_naming import PAPER_LABELS, past_paper_pdf_path  # noqa: E402
from dse_ict_support_content import apply_support_to_item  # noqa: E402
from dse_ict_syllabus import infer_concepts_from_text, tag_item  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
DEFAULT_GEMINI = REPO / "Subjects/DSE-ICT/gemini-output"
DEFAULT_BANK = REPO / "Subjects/DSE-ICT/question-bank"
DEFAULT_PAST = REPO / "Subjects/DSE-ICT/past-papers"
CONCEPTS_PATH = DEFAULT_BANK / "curriculum_concepts.json"

GEMINI_PART_MAP: dict[str, str] = {
    "p1": "Paper1_MultipleChoice",
    "p1a": "Paper1_MultipleChoice",
    "p1b": "Paper1B_CompulsoryStructured",
    "p2": "Paper2_Elective",
    "p2a": "Paper2A_Database",
    "p2b": "Paper2B_DataCommunicationsNetworking",
    "p2c": "Paper2C_MultimediaWebsiteConstruction",
    "p2d": "Paper2D_SoftwareDevelopment",
    "ans": "MarkingScheme",
}


def _mcq_slug(year: str) -> str:
    return "Paper1A_MultipleChoice" if int(year) >= 2025 else "Paper1_MultipleChoice"


def _resolve_paper_slug(file_part: str, year: str) -> str:
    slug = GEMINI_PART_MAP[file_part]
    if file_part in ("p1", "p1a") and int(year) >= 2025:
        return _mcq_slug(year)
    return slug


def _flatten_parts(
    parts: list[dict],
    *,
    qnum: str,
    parent: dict,
    path: str = "",
) -> list[dict]:
    out: list[dict] = []
    for part in parts:
        label = str(part.get("part_label", "")).strip()
        sub_path = f"{path}({label})" if label else path
        if part.get("sub_parts"):
            out.extend(_flatten_parts(part["sub_parts"], qnum=qnum, parent=parent, path=sub_path))
            continue
        if part.get("question_text"):
            item: dict[str, Any] = {
                "question_number": f"{qnum}{sub_path}",
                "question_text": part["question_text"],
                "marks": part.get("marks"),
                "page": parent.get("page"),
                "section": parent.get("section"),
                "_gemini_parent": parent,
                "_gemini_part": part,
            }
            out.append(item)
    return out


def _flatten_gemini_rows(rows: list[Any]) -> list[dict]:
    flat: list[dict] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        if row.get("parts"):
            qnum = str(row.get("question_number", ""))
            flat.extend(_flatten_parts(row["parts"], qnum=qnum, parent=row))
            continue
        item = dict(row)
        if "question_number" in item:
            item["question_number"] = str(item["question_number"])
        flat.append(item)
    return flat


def _load_concepts() -> dict:
    return json.loads(CONCEPTS_PATH.read_text(encoding="utf-8"))


def _parse_gemini_filename(name: str) -> tuple[str, str] | None:
    m = re.match(r"^(\d{4})-(.+)\.json$", name)
    if not m:
        return None
    return m.group(1), m.group(2)


def _slugify_id(part: str) -> str:
    s = part.replace("SectionA_", "A").replace("SectionB_", "B").replace("SectionC_", "C")
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-")
    return s or "Q"


def _is_mcq(raw: dict) -> bool:
    qtype = (raw.get("question_type") or "").lower()
    if "multiple_choice" in qtype or qtype == "mcq":
        return True
    if raw.get("options"):
        return True
    return False


def _paper_section_from_number(qnum: str, *, is_mcq: bool) -> str:
    if qnum.startswith("SectionA_") or (is_mcq and not qnum.startswith("Section") and not qnum.startswith("1B-")):
        return "mcq"
    if qnum.startswith("SectionC_"):
        return "section_c"
    if qnum.startswith("SectionB_") or qnum.startswith("1B-"):
        return "section_b"
    if is_mcq:
        return "mcq"
    return "section_b"


def _target_slug_for_question(
    *,
    file_part: str,
    year: str,
    qnum: str,
    raw: dict,
) -> str:
    if file_part not in GEMINI_PART_MAP:
        raise ValueError(f"Unknown gemini part: {file_part}")
    if file_part == "p1":
        if re.match(r"^Section[BC]_", qnum) or qnum.startswith("1B-"):
            return "Paper1B_CompulsoryStructured"
    if file_part == "ans":
        return "MarkingScheme"
    return _resolve_paper_slug(file_part, year)


def _normalize_options(raw: dict) -> dict[str, str] | None:
    opts = raw.get("options")
    if not opts:
        return None
    if isinstance(opts, dict):
        return {str(k).strip(): str(v).strip() for k, v in opts.items()}
    if isinstance(opts, list):
        out: dict[str, str] = {}
        for line in opts:
            line = str(line).strip()
            m = re.match(r"^([A-D])[\.\)、]\s*(.*)$", line)
            if m:
                out[m.group(1)] = m.group(2).strip()
        return out or None
    return None


def _build_stem(raw: dict, *, options: dict[str, str] | None) -> str:
    parts: list[str] = []
    qt = raw.get("question_text") or ""
    if qt:
        parts.append(qt.strip())
    for key in ("statements", "sub_questions_list"):
        items = raw.get(key)
        if items:
            parts.extend(str(x).strip() for x in items)
    if options:
        for letter in sorted(options):
            parts.append(f"{letter}. {options[letter]}")
    return "\n".join(parts).strip()


def _build_text(raw: dict, *, options: dict[str, str] | None, image_desc: str | None) -> str:
    parts: list[str] = []
    stem = _build_stem(raw, options=options)
    if stem:
        parts.append(stem)
    if image_desc:
        parts.append(f"[圖片描述] {image_desc}")
    for key in ("answer_details", "context", "scenario"):
        val = raw.get(key)
        if isinstance(val, str) and val.strip():
            parts.append(val.strip())
        elif isinstance(val, dict) and val:
            parts.append(json.dumps(val, ensure_ascii=False, indent=2))
    return "\n\n".join(parts).strip()


def _elective_code_from_section(section: str) -> str | None:
    if "數據庫" in section or section.startswith("甲部"):
        return "EA"
    if "網絡" in section or section.startswith("乙部"):
        return "EB"
    if "算法" in section or "程式" in section or section.startswith("丙部"):
        return "EC"
    return None


def _infer_tags(text: str, *, paper_slug: str, concepts_cfg: dict, raw: dict | None = None) -> dict[str, Any]:
    return infer_concepts_from_text(
        text,
        paper_slug=paper_slug,
        concepts_cfg=concepts_cfg,
        raw=raw,
    )


def _marks_from_raw(raw: dict) -> float | None:
    for key in ("points", "marks"):
        val = raw.get(key)
        if val is not None:
            try:
                return float(val)
            except (TypeError, ValueError):
                pass
    return None


def _convert_item(
    raw: dict,
    *,
    year: str,
    paper_slug: str,
    seq: int,
    concepts_cfg: dict,
    gemini_file: str,
) -> dict[str, Any]:
    qnum = str(raw.get("question_number") or seq)
    options = _normalize_options(raw)
    is_mcq = _is_mcq(raw)
    section = _paper_section_from_number(qnum, is_mcq=is_mcq)
    image_desc = raw.get("image_description")
    if raw.get("has_image") and not image_desc:
        image_desc = "（原卷含圖像／示意圖，待補充描述）"

    text = _build_text(raw, options=options, image_desc=image_desc)
    tags = _infer_tags(text, paper_slug=paper_slug, concepts_cfg=concepts_cfg, raw=raw)
    item_id = f"{year}-{paper_slug}-{_slugify_id(qnum)}"

    row: dict[str, Any] = {
        "id": item_id,
        "section": section,
        "text": text,
        "number": qnum,
        "concepts": tags["concepts"],
        "curriculum_part": tags["curriculum_part"],
        "curriculum_unit": tags["curriculum_unit"],
    }
    if tags["curriculum_topics"]:
        row["curriculum_topics"] = tags["curriculum_topics"]

    marks = _marks_from_raw(raw)
    if marks is not None:
        row["marks"] = marks
    elif section == "mcq":
        row["marks"] = 1

    if options:
        row["stem"] = _build_stem(raw, options=None)
        row["options"] = options

    if raw.get("question_type"):
        row["question_type"] = raw["question_type"]
    if raw.get("has_image") is not None:
        row["has_image"] = bool(raw["has_image"])
    if image_desc:
        row["image_description"] = image_desc
    if raw.get("correct_answer"):
        row["answer"] = raw["correct_answer"]
    if raw.get("answer_text"):
        row["answer"] = raw["answer_text"]
    if raw.get("answer_details"):
        row["answer_details"] = raw["answer_details"]
    if raw.get("answer_type"):
        row["answer_type"] = raw["answer_type"]
    if raw.get("details"):
        row["marking_notes"] = raw["details"]
    if raw.get("source_page") is not None:
        row["source_page"] = raw["source_page"]
    if raw.get("page") is not None:
        row["source_page"] = raw["page"]
    if raw.get("section"):
        row["elective_section"] = raw["section"]

    gemini_raw = {k: v for k, v in raw.items() if not k.startswith("_gemini")}
    if raw.get("_gemini_parent"):
        gemini_raw = {
            "parent": raw["_gemini_parent"],
            "part": raw.get("_gemini_part"),
            **gemini_raw,
        }
    row["gemini_source"] = gemini_file
    row["gemini_raw"] = gemini_raw
    apply_support_to_item(row)
    tag_item(row, paper_slug=paper_slug, paper_year=year, concepts_cfg=concepts_cfg)
    return row


def _group_questions(
    rows: list[dict],
    *,
    year: str,
    file_part: str,
) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    seq_by_slug: dict[str, int] = {}
    for raw in rows:
        qnum = str(raw.get("question_number") or "")
        slug = _target_slug_for_question(file_part=file_part, year=year, qnum=qnum, raw=raw)
        seq_by_slug[slug] = seq_by_slug.get(slug, 0) + 1
        grouped.setdefault(slug, []).append(raw)
    return grouped


def _build_paper_spec(
    *,
    year: str,
    slug: str,
    items: list[dict],
    gemini_files: list[str],
) -> dict[str, Any]:
    pdf_path = past_paper_pdf_path(DEFAULT_PAST, year, slug)
    rel_pdf = str(pdf_path.relative_to(REPO)).replace("\\", "/")
    meta: dict[str, Any] = {
        "source": "dse-ict-question-bank",
        "import_source": "gemini-output",
        "imported_at": datetime.now(timezone.utc).isoformat(),
        "year_label": year,
        "paper_slug": slug,
        "paper_label": PAPER_LABELS.get(slug, slug),
        "source_pdf": rel_pdf,
        "question_count": len(items),
        "gemini_source_files": sorted(set(gemini_files)),
        "curriculum_guide": "Subjects/DSE-ICT/edb/ICT_C&A Guide_c_final.pdf",
    }

    mcq_answers: dict[str, str] = {}
    if slug == "MarkingScheme":
        for item in items:
            ans = item.get("answer")
            qn = item.get("number")
            if ans and qn and item.get("section") == "mcq":
                mcq_answers[str(qn)] = str(ans)

    paper_questions = []
    for item in items:
        pq = {
            "id": item["id"],
            "type": item.get("question_type") or item["section"],
            "number": item.get("number"),
            "section": item["section"],
            "text": item["text"],
            "marks": item.get("marks"),
            "concepts": item.get("concepts", []),
        }
        if item.get("options"):
            pq["options"] = item["options"]
            pq["stem"] = item.get("stem")
        if item.get("support_content"):
            pq["support_content"] = item["support_content"]
        if item.get("answer"):
            pq["answer"] = item["answer"]
        paper_questions.append(pq)

    spec: dict[str, Any] = {
        "version": 1,
        "meta": meta,
        "items": items,
        "paper": {"id": f"{year}-{slug}", "questions": paper_questions},
    }
    if slug == "MarkingScheme" and mcq_answers:
        spec["paper"]["mcq_answers"] = mcq_answers
    return spec


def _merge_mcq_answers_from_marking(bank_root: Path) -> None:
    for year_dir in sorted(bank_root.iterdir()):
        if not year_dir.is_dir() or not re.fullmatch(r"\d{4}", year_dir.name):
            continue
        ms = year_dir / "MarkingScheme" / "questions.json"
        p1 = year_dir / "Paper1_MultipleChoice" / "questions.json"
        if not p1.exists():
            p1 = year_dir / "Paper1A_MultipleChoice" / "questions.json"
        if not ms.exists() or not p1.exists():
            continue
        ms_data = json.loads(ms.read_text(encoding="utf-8"))
        answers = ms_data.get("paper", {}).get("mcq_answers") or {}
        if not answers:
            for item in ms_data.get("items", []):
                qn = str(item.get("number", ""))
                ans = item.get("answer")
                sec = item.get("section")
                if sec == "mcq" and ans and re.fullmatch(r"\d{1,2}", qn):
                    answers[qn] = ans
                elif sec == "mcq" and ans and qn.startswith("SectionA_Q"):
                    num = re.sub(r"\D", "", qn)
                    if num:
                        answers[num] = ans
        if not answers:
            continue
        p1_data = json.loads(p1.read_text(encoding="utf-8"))
        changed = False
        for item in p1_data.get("items", []):
            qn = str(item.get("number", ""))
            lookup = qn
            if qn.startswith("SectionA_Q"):
                lookup = re.sub(r"\D", "", qn) or qn
            if lookup in answers and not item.get("answer"):
                item["answer"] = answers[lookup]
                changed = True
        if changed:
            p1.write_text(json.dumps(p1_data, ensure_ascii=False, indent=2), encoding="utf-8")


def import_gemini(
    *,
    gemini_root: Path,
    bank_root: Path,
    years: set[str] | None = None,
    force: bool = False,
) -> list[tuple[str, str, int]]:
    concepts_cfg = _load_concepts()
    results: list[tuple[str, str, int]] = []
    by_paper: dict[tuple[str, str], dict[str, Any]] = {}

    for path in sorted(gemini_root.glob("*.json")):
        parsed = _parse_gemini_filename(path.name)
        if not parsed:
            continue
        year, part = parsed
        if years and year not in years:
            continue
        if part not in GEMINI_PART_MAP:
            print(f"skip unknown part: {path.name}")
            continue

        rows = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(rows, list):
            print(f"skip non-list: {path.name}")
            continue

        rows = _flatten_gemini_rows(rows)
        grouped = _group_questions(rows, year=year, file_part=part)
        for slug, raw_items in grouped.items():
            key = (year, slug)
            bucket = by_paper.setdefault(
                key,
                {"items": [], "gemini_files": [], "seq": 0},
            )
            bucket["gemini_files"].append(path.name)
            for raw in raw_items:
                bucket["seq"] += 1
                item = _convert_item(
                    raw,
                    year=year,
                    paper_slug=slug,
                    seq=bucket["seq"],
                    concepts_cfg=concepts_cfg,
                    gemini_file=path.name,
                )
                bucket["items"].append(item)

    for (year, slug), bucket in sorted(by_paper.items()):
        out_dir = bank_root / year / slug
        out_path = out_dir / "questions.json"
        if out_path.exists() and not force:
            existing = json.loads(out_path.read_text(encoding="utf-8"))
            if existing.get("meta", {}).get("import_source") != "gemini-output":
                print(f"skip {year}/{slug}: existing non-gemini questions.json (use --force)")
                continue

        spec = _build_paper_spec(
            year=year,
            slug=slug,
            items=bucket["items"],
            gemini_files=bucket["gemini_files"],
        )
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
        results.append((year, slug, len(bucket["items"])))
        print(f"Wrote {out_path.relative_to(REPO)} ({len(bucket['items'])} items)")

    _merge_mcq_answers_from_marking(bank_root)
    return results


def _patch_index_for_derived_papers(bank_root: Path) -> None:
    """Add index entries for question-bank folders without a separate past-paper PDF."""
    index_path = bank_root / "index.json"
    if not index_path.exists():
        return
    index = json.loads(index_path.read_text(encoding="utf-8"))
    papers = index.get("papers", [])
    existing = {(p["year_label"], p["paper_slug"]) for p in papers}

    for year_dir in sorted(bank_root.iterdir()):
        if not year_dir.is_dir() or not re.fullmatch(r"\d{4}", year_dir.name):
            continue
        year = year_dir.name
        for spec_path in sorted(year_dir.glob("*/questions.json")):
            slug = spec_path.parent.name
            if (year, slug) in existing:
                continue
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
            meta = spec.get("meta", {})
            pdf = meta.get("source_pdf")
            if slug == "Paper1B_CompulsoryStructured" and int(year) < 2024:
                pdf = f"Subjects/DSE-ICT/past-papers/{year}/DSE_ICT_{year}_Paper1_MultipleChoice.pdf"
            entry = {
                "year_label": year,
                "paper_slug": slug,
                "paper_label": meta.get("paper_label") or PAPER_LABELS.get(slug, slug),
                "pdf": pdf,
                "questions_json": str(spec_path.relative_to(REPO)).replace("\\", "/"),
                "ocr_cache": None,
                "derived_from_gemini": True,
            }
            papers.append(entry)
            existing.add((year, slug))

    papers.sort(key=lambda p: (p["year_label"], p.get("paper_slug", "")))
    index["papers"] = papers
    index["generated_at"] = datetime.now(timezone.utc).isoformat()
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--gemini", type=Path, default=DEFAULT_GEMINI)
    ap.add_argument("--bank", type=Path, default=DEFAULT_BANK)
    ap.add_argument("--years", nargs="*", help="Limit to years e.g. 2021 2022")
    ap.add_argument("--force", action="store_true", help="Overwrite existing gemini imports")
    args = ap.parse_args(argv)

    years = set(args.years) if args.years else None
    import_gemini(
        gemini_root=args.gemini.expanduser().resolve(),
        bank_root=args.bank.expanduser().resolve(),
        years=years,
        force=args.force,
    )

    # refresh index via build script
    build_script = Path(__file__).resolve().parent / "build_dse_ict_question_bank.py"
    import subprocess

    subprocess.run(
        [sys.executable, str(build_script), "--index-only"],
        check=True,
        cwd=str(REPO),
    )
    _patch_index_for_derived_papers(args.bank.expanduser().resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
