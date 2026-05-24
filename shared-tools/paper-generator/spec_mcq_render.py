"""Convert exam spec MCQ items to template row blocks for DOCX render."""
from __future__ import annotations

import re
from typing import Any

# Paragraph line counts per MCQ slot (24_25 template)
MCQ_SPANS: tuple[int, ...] = (
    6,
    6,
    6,
    6,
    6,
    10,
    8,
    10,
    6,
    6,
    6,
    6,
    10,
    6,
    10,
    10,
    6,
    6,
    6,
    6,
    10,
    10,
    9,
    13,
    12,
    10,
    8,
    14,
    6,
    14,
)

_OPT_RE = re.compile(r"^\t([A-D])\.\t(.+)$")
_SUB_RE = re.compile(r"^\t+\((\d+)\)\t(.+)$")


def parse_spec_mcq_text(text: str) -> tuple[str, list[str], dict[str, str]]:
    """Parse spec item text → question, (1)(2)(3) statements, A–D options."""
    question_parts: list[str] = []
    statements: list[str] = []
    opts: dict[str, str] = {}
    for raw in (text or "").splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        mo = _OPT_RE.match(line)
        ms = _SUB_RE.match(line)
        if mo:
            opts[mo.group(1)] = mo.group(2).strip()
        elif ms:
            statements.append(ms.group(2).strip())
        else:
            question_parts.append(line.strip())
    question = "\n".join(question_parts)
    return question, statements, opts


def spec_mcq_to_final_rows(spec: dict[str, Any]) -> tuple[list[list[str]], str]:
    """Build template MCQ row blocks + answer key from spec."""
    from f5_ict_from_dse import _layout_mcq_block

    mcq_items = sorted(
        (it for it in spec.get("items") or [] if it.get("section") == "mcq"),
        key=lambda x: str(x.get("id", "")),
    )
    if len(mcq_items) != len(MCQ_SPANS):
        raise ValueError(f"Expected {len(MCQ_SPANS)} MCQ items, got {len(mcq_items)}")

    rows: list[list[str]] = []
    for idx, item in enumerate(mcq_items, start=1):
        question, statements, opts = parse_spec_mcq_text(str(item.get("text") or ""))
        if len(opts) != 4:
            raise ValueError(f"{item.get('id')}: need 4 options, got {len(opts)}")
        span = MCQ_SPANS[idx - 1]
        rows.append(_layout_mcq_block(question, statements, opts, span))

    meta = spec.get("meta") or {}
    key = str(meta.get("mcq_answers") or meta.get("mcq_answer_key") or "")
    if len(key) != len(mcq_items):
        key = "".join(
            str(it.get("answer") or "A")[:1].upper()
            for it in mcq_items
        )
    return rows, key
