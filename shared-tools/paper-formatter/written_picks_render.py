"""
Render 乙／丙 from written_picks (full bank-composed text) into template paragraph lines.

Keeps template skeleton blanks / section headers; replaces substantive lines with
pick text formatted for school DOCX (tabs, subparts, SQL/code indent).
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from written_layout import ANSWER_BLANK, ANSWER_BLANK_LONG, code_line, sql_line, stem, subpart
from written_slot_ranges import PART_B_RANGE, PART_C_RANGE, WRITTEN_SLOT_PARAGRAPHS

if TYPE_CHECKING:
    pass

_SUBPART_LINE = re.compile(
    r"^\s*\(([a-z]{1,2}|[ivx]{1,4})\)\s*(.*)$",
    re.IGNORECASE,
)
_SQL_LINE = re.compile(
    r"^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|FROM|WHERE|UNION|BEGIN|"
    r"COMMIT|ROLLBACK|MINUS|JOIN|GROUP|HAVING|SET|VALUES|INTO)\b",
    re.IGNORECASE,
)
_CODE_HINT = re.compile(
    r"(←|→|程序|執行|當\s|WHILE|REPEAT|IF\s.+則|否則|輸出|傳回|PUSH|POP|ALG\d)",
    re.IGNORECASE,
)
_IMAGE_DESC = re.compile(r"\[圖片描述\]|^\(image ", re.IGNORECASE)


def _fix_typos(text: str) -> str:
    return text.replace("否則則", "否則")


def _subpart_depth(label: str) -> int:
    if len(label) <= 3 and label[0].lower() in "ivx":
        return 2
    return 1


def _format_body_line(line: str) -> str:
    s = line.strip()
    if not s or _IMAGE_DESC.search(s):
        return ""
    m = _SUBPART_LINE.match(s)
    if m:
        label, rest = m.group(1), (m.group(2) or "").strip()
        if not rest:
            return ""
        return subpart(label, rest, depth=_subpart_depth(label))
    if _SQL_LINE.match(s):
        depth = 3 if s.startswith("    ") else 2
        return sql_line(s.strip(), depth=depth)
    if _CODE_HINT.search(s) and not s.endswith("？"):
        depth = 2 if not s[0].isdigit() else 2
        return code_line(s.strip(), depth=depth)
    if s.endswith("？") or s.endswith("?"):
        return stem(s, depth=1)
    return s


def pick_text_to_content_lines(text: str) -> list[str]:
    """Parse bank-composed slot text → layout lines (no answer blanks)."""
    text = _fix_typos(text or "")
    out: list[str] = []
    for raw in text.splitlines():
        line = _format_body_line(raw)
        if line:
            out.append(line)
    return out


def _is_fixed_skeleton_line(s: str) -> bool:
    """Lines that must not be overwritten (blanks, section headers, padding)."""
    if s in (ANSWER_BLANK, ANSWER_BLANK_LONG):
        return True
    if not s.strip():
        return True
    if "部 (" in s or "分)：" in s or "分）：" in s:
        return True
    return False


def _is_replaceable_skeleton_line(s: str) -> bool:
    return not _is_fixed_skeleton_line(s)


def _fit_content_to_skeleton(skeleton: list[str], content: list[str]) -> list[str]:
    """Map content lines onto replaceable skeleton slots; preserve blanks/headers."""
    result = list(skeleton)
    slots = [i for i, s in enumerate(skeleton) if _is_replaceable_skeleton_line(s)]
    if not slots:
        return result

    if len(content) > len(slots):
        # Merge overflow into last content lines (keep last lines which are often subparts)
        merged = content[: len(slots) - 1]
        merged.append(" ".join(content[len(slots) - 1 :]))
        content = merged
    elif len(content) < len(slots):
        content = content + [""] * (len(slots) - len(content))

    for idx, line in zip(slots, content, strict=False):
        result[idx] = line
    return result


def layout_slot_from_pick(pick: dict, skeleton: list[str]) -> list[str]:
    text = pick.get("text") or pick.get("scenario_line") or ""
    content = pick_text_to_content_lines(text)
    return _fit_content_to_skeleton(skeleton, content)


def _slot_skeleton(default_lines: list[str], slot_id: str) -> list[str]:
    start, end, _ = WRITTEN_SLOT_PARAGRAPHS[slot_id]
    base = PART_B_RANGE[0] if slot_id.startswith("b-") else PART_C_RANGE[0]
    return list(default_lines[start - base : end - base + 1])


def build_part_from_picks(
    picks: dict[str, dict],
    *,
    section: str,
    default_builder,
) -> list[str]:
    """
    Build full 乙 or 丙 paragraph array using template skeleton + pick text per slot.
    """
    default_lines = default_builder()
    base = PART_B_RANGE[0] if section == "b" else PART_C_RANGE[0]
    out = list(default_lines)

    for slot_id, (start, end, _marks) in WRITTEN_SLOT_PARAGRAPHS.items():
        if not slot_id.startswith(section):
            continue
        pick = picks.get(slot_id)
        if not pick:
            continue
        skel = _slot_skeleton(default_lines, slot_id)
        merged = layout_slot_from_pick(pick, skel)
        off = start - base
        for i, line in enumerate(merged):
            out[off + i] = line
    return out


def build_part_b_from_picks(picks: dict[str, dict]) -> list[str]:
    from f5_ict_written_content import build_part_b

    return build_part_from_picks(picks, section="b", default_builder=build_part_b)


def build_part_c_from_picks(picks: dict[str, dict]) -> list[str]:
    from f5_ict_written_content import build_part_c

    return build_part_from_picks(picks, section="c", default_builder=build_part_c)


def pick_slot_spec_text(pick: dict, slot_id: str, *, default_builder) -> str:
    """Text stored in exam spec — matches rendered DOCX slot (excludes answer blanks)."""
    skel = _slot_skeleton(default_builder(), slot_id)
    lines = layout_slot_from_pick(pick, skel)
    return "\n".join(
        ln
        for ln in lines
        if ln.strip() and ln not in (ANSWER_BLANK, ANSWER_BLANK_LONG) and "部 (" not in ln
    ).strip()
