"""
F5 ICT Exam02 paragraph roles and line-type → role mapping.

Roles are formatting patterns (not paragraph indices). Render picks a role profile
when writing content so a new DOCX reproduces tab stops / alignment / fonts.
"""

from __future__ import annotations

import re
from typing import Literal

McqLineKind = Literal[
    "stem",
    "blank",
    "combo_sub",
    "option",
    "code",
    "collapsed_blank",
    "inter_gap_blank",
]

_OPTION = re.compile(r"^\t[A-D]\.\t")
_COMBO = re.compile(r"^\t+\(\d+\)\t")


def mcq_line_kind(line: str, *, collapsed: bool = False) -> McqLineKind:
    if collapsed or not line.strip():
        if collapsed:
            return "collapsed_blank"
        return "blank"
    if _OPTION.match(line):
        return "option"
    if _COMBO.match(line):
        return "combo_sub"
    from mcq_code_layout import is_code_content_line

    if is_code_content_line(line):
        return "code"
    return "stem"


def mcq_role_for_kind(kind: McqLineKind, *, code_center: bool = False) -> str:
    return {
        "stem": "mcq.stem",
        "blank": "mcq.blank_before_options",
        "combo_sub": "mcq.combo_sub",
        "option": "mcq.option",
        "code": "mcq.code_center" if code_center else "mcq.code_left",
        "collapsed_blank": "mcq.collapsed_padding",
        "inter_gap_blank": "mcq.inter_question_gap",
    }[kind]


WrittenLineKind = Literal[
    "scenario",
    "stem",
    "subpart",
    "subpart_nested",
    "code",
    "sql",
    "answer_blank",
    "answer_blank_long",
    "diagram_blank",
    "blank",
    "plain",
]

_SUBPART = re.compile(r"^\t+\([a-z]{1,2}\)\t", re.I)
_SUBPART_NESTED = re.compile(r"^\t\t\([ivx]+\)\t", re.I)
_ANSWER_BLANK = "\t\t\t\t\t"
_ANSWER_BLANK_LONG = "\t\t\t\t\t\t\t"
_DIAGRAM_BLANK = "\t\t"


def written_line_kind(line: str) -> WrittenLineKind:
    if line == _ANSWER_BLANK_LONG:
        return "answer_blank_long"
    if line == _ANSWER_BLANK:
        return "answer_blank"
    if line == _DIAGRAM_BLANK:
        return "diagram_blank"
    if not line.strip():
        return "blank"
    if _SUBPART_NESTED.match(line):
        return "subpart_nested"
    if _SUBPART.match(line):
        return "subpart"
    from mcq_code_layout import is_code_content_line

    if is_code_content_line(line):
        return "code"
    if re.match(
        r"^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE|FROM|WHERE)\b",
        line.strip(),
        re.I,
    ):
        return "sql"
    if line.startswith("\t") and (line.endswith("？") or line.endswith("?")):
        return "stem"
    if not line.startswith("\t"):
        return "scenario"
    return "plain"


def written_role_for_kind(kind: WrittenLineKind) -> str:
    return {
        "scenario": "written.scenario",
        "stem": "written.stem",
        "subpart": "written.subpart",
        "subpart_nested": "written.subpart_nested",
        "code": "written.code",
        "sql": "written.sql",
        "answer_blank": "written.answer_blank",
        "answer_blank_long": "written.answer_blank_long",
        "diagram_blank": "written.diagram_blank",
        "blank": "written.blank",
        "plain": "written.plain",
    }[kind]

# Representative paragraph indices in 24_25 template used to seed each role profile.
F5_ICT_ROLE_SOURCE_PARAS: dict[str, int] = {
    "mcq.stem": 44,
    "mcq.blank_before_options": 45,
    "mcq.option": 46,
    "mcq.combo_sub": 227,
    "mcq.code_left": 227,
    "mcq.code_center": 59,
    "mcq.collapsed_padding": 50,
    "mcq.inter_question_gap": 55,
    "written.scenario": 313,
    "written.stem": 316,
    "written.subpart": 317,
    "written.subpart_nested": 358,
    "written.code": 360,
    "written.sql": 399,
    "written.answer_blank": 318,
    "written.answer_blank_long": 355,
    "written.diagram_blank": 429,
    "written.blank": 314,
    "written.plain": 315,
    "section.mcq_header": 1,
    "section.written_b_header": 311,
    "section.written_c_header": 423,
}
