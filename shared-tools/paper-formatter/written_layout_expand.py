"""Expand written pick text into template layout lines (tabs; blanks stay in skeleton)."""

from __future__ import annotations

import re

from written_layout import subpart

_MARKS_SUFFIX = re.compile(r"\t\(\s*\d+\s*分\s*\)\s*$")
_SUBPART_LINE = re.compile(
    r"^\s*\(([a-z]{1,2}|[ivx]{1,4})\)\s*(.*)$",
    re.IGNORECASE | re.DOTALL,
)


def _strip_marks_suffix(text: str) -> tuple[str, int | None]:
    m = _MARKS_SUFFIX.search(text)
    if not m:
        return text.strip(), None
    body = text[: m.start()].strip()
    mk = re.search(r"(\d+)", m.group(0))
    return body, int(mk.group(1)) if mk else None


def _subpart_depth(label: str) -> int:
    if len(label) <= 3 and label[0].lower() in "ivx":
        return 2
    return 1


def expand_pick_text_to_layout_lines(text: str, *, slot_id: str = "") -> list[str]:
    """
    Parse spec / pick plain text into ``\\t(a)\\t…`` lines for replaceable skeleton slots.

    Does not insert answer-blank lines — the template skeleton keeps those fixed.
    """
    del slot_id  # reserved for slot-specific rules
    raw_blocks = [b.strip() for b in re.split(r"\n\s*\n", text.strip()) if b.strip()]
    if not raw_blocks:
        return []

    lines: list[str] = []

    for block in raw_blocks:
        sub_lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
        if not sub_lines:
            continue

        scenario_parts: list[str] = []
        subpart_rows: list[tuple[str, str, int | None, int]] = []

        for ln in sub_lines:
            sm = _SUBPART_LINE.match(ln)
            if sm:
                label, rest = sm.group(1), sm.group(2)
                body, marks = _strip_marks_suffix(rest)
                depth = _subpart_depth(label)
                subpart_rows.append((label, body, marks, depth))
            else:
                scenario_parts.append(ln)

        if scenario_parts and not subpart_rows:
            lines.extend(scenario_parts)
            continue

        if scenario_parts:
            lines.append(" ".join(scenario_parts))

        for label, body, marks, depth in subpart_rows:
            lines.append(subpart(label, body, marks, depth=depth))

    return lines
