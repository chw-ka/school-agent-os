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
_MARKS_SUFFIX = re.compile(r"\t\(\s*\d+\s*分\s*\)\s*$")
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


def _strip_marks_suffix(text: str) -> tuple[str, int | None]:
    m = _MARKS_SUFFIX.search(text)
    if not m:
        return text.strip(), None
    body = text[: m.start()].strip()
    mk = re.search(r"(\d+)", m.group(0))
    return body, int(mk.group(1)) if mk else None


def _format_body_line(line: str) -> str:
    s = line.strip()
    if not s or _IMAGE_DESC.search(s):
        return ""
    m = _SUBPART_LINE.match(s)
    if m:
        label, rest = m.group(1), (m.group(2) or "").strip()
        body, marks = _strip_marks_suffix(rest)
        if not body:
            return ""
        return subpart(label, body, marks, depth=_subpart_depth(label))
    if _SQL_LINE.match(s):
        depth = 3 if s.startswith("    ") else 2
        return sql_line(s.strip(), depth=depth)
    if _CODE_HINT.search(s) and not s.endswith("？"):
        return code_line(s.strip(), depth=2)
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


_SQL_SKELETON = re.compile(
    r"^\s*(CREATE\s+TABLE|PRIMARY\s+KEY|NOT\s+NULL|REFERENCES|FOREIGN\s+KEY|"
    r"CHAR\(|VARCHAR|INTEGER|DATE|\)|MID\s|BID\s|TITLE\s|LOANDATE)",
    re.I,
)


def _is_sql_skeleton_line(s: str) -> bool:
    t = s.strip()
    if not t:
        return False
    if _SQL_SKELETON.search(t):
        return True
    return bool(_SQL_LINE.match(t))


def _is_fixed_skeleton_line(s: str) -> bool:
    """Lines that must not be overwritten (blanks, section headers, padding)."""
    if s in (ANSWER_BLANK, ANSWER_BLANK_LONG):
        return True
    if not s.strip():
        return True
    if "部 (" in s or "分)：" in s or "分）：" in s:
        return True
    if _is_sql_skeleton_line(s):
        return True
    return False


def _fit_content_to_skeleton(skeleton: list[str], content: list[str]) -> list[str]:
    """Map content onto replaceable skeleton slots only; keep answer blanks in place."""
    result = list(skeleton)
    slots = [i for i, s in enumerate(skeleton) if not _is_fixed_skeleton_line(s)]
    if not slots:
        return result

    if len(content) > len(slots):
        merged = content[: len(slots) - 1]
        merged.append(" ".join(content[len(slots) - 1 :]))
        content = merged
    elif len(content) < len(slots):
        for idx, line in zip(slots, content, strict=False):
            if line.strip():
                result[idx] = line
        return result

    for idx, line in zip(slots, content, strict=False):
        result[idx] = line
    return result


def layout_slot_from_pick(pick: dict, skeleton: list[str], *, slot_id: str = "") -> list[str]:
    from written_layout_expand import expand_pick_text_to_layout_lines

    text = pick.get("text") or pick.get("scenario_line") or ""
    expanded = expand_pick_text_to_layout_lines(text, slot_id=slot_id)
    if expanded:
        return _fit_content_to_skeleton(skeleton, expanded)
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
        merged = layout_slot_from_pick(pick, skel, slot_id=slot_id)
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
