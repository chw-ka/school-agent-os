"""DOCX body format checks: quote style and MCQ option indentation."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from exam_spec import spec_items
from quality_lib import extract_lines, extract_mcq_stems

_BACKTICK_RE = re.compile(r"`[^`]+`")
# Each MCQ option line (or segment) should use tab before A./B./C./D.
_OPTION_LINE_RE = re.compile(r"^\t[ABCD]\.\t", re.MULTILINE)
_BAD_OPTION_RE = re.compile(r"(?<!\t)\n[ABCD]\.\t")


@dataclass
class FormatCheckResult:
    ok: bool
    backtick_hits: list[str] = field(default_factory=list)
    mcq_indent_issues: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "backtick_hits": self.backtick_hits,
            "mcq_indent_issues": self.mcq_indent_issues,
        }


def _find_backticks(text: str, *, max_hits: int = 20) -> list[str]:
    hits: list[str] = []
    for m in _BACKTICK_RE.finditer(text):
        snippet = m.group(0)
        if snippet not in hits:
            hits.append(snippet)
        if len(hits) >= max_hits:
            break
    return hits


def _is_combo_mcq(text: str) -> bool:
    if len(re.findall(r"^\s*\(\d+\)[\s\t]", text, re.MULTILINE)) >= 2:
        return True
    return bool(re.search(r"只有\s*\(\d+\)|皆是", text))


def _check_mcq_option_indent(full_text: str, *, q_index: int) -> list[str]:
    if _is_combo_mcq(full_text):
        return []
    issues: list[str] = []
    if _BAD_OPTION_RE.search(full_text):
        issues.append(
            f"MCQ#{q_index}: option line missing leading tab after newline (use '\\n\\tA.\\t')"
        )
    return issues


def check_exam_format(
    docx_path: Path,
    *,
    check_backticks: bool = True,
    check_mcq_indent: bool = True,
) -> FormatCheckResult:
    lines = extract_lines(docx_path)
    body = "\n".join(lines)

    backtick_hits: list[str] = []
    mcq_issues: list[str] = []

    if check_backticks:
        backtick_hits = _find_backticks(body)

    if check_mcq_indent:
        for m in extract_mcq_stems(lines):
            mcq_issues.extend(_check_mcq_option_indent(m.get("full") or m.get("stem", ""), q_index=m["index"]))

    ok = not backtick_hits and not mcq_issues
    return FormatCheckResult(
        ok=ok,
        backtick_hits=backtick_hits,
        mcq_indent_issues=mcq_issues,
    )


def check_spec_format(spec: dict) -> FormatCheckResult:
    backtick_hits: list[str] = []
    for item in spec_items(spec):
        text = item.text or item.meta.get("stem") or ""
        for hit in _find_backticks(text):
            if hit not in backtick_hits:
                backtick_hits.append(hit)
    ok = not backtick_hits
    return FormatCheckResult(ok=ok, backtick_hits=backtick_hits)


def format_format_report(result: FormatCheckResult) -> str:
    lines = [f"Format: {'OK' if result.ok else 'ISSUES'}"]
    if result.backtick_hits:
        lines.append("Backticks (use single quotes '…' instead):")
        for h in result.backtick_hits:
            lines.append(f"  - {h}")
    if result.mcq_indent_issues:
        lines.append("MCQ indentation:")
        for issue in result.mcq_indent_issues:
            lines.append(f"  - {issue}")
    if result.ok:
        lines.append("Quote style and MCQ option tabs are consistent.")
    return "\n".join(lines)
