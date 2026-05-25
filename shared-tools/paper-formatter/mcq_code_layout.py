"""MCQ pseudocode / Python layout (DSE-style Chinese keywords + indentation)."""

from __future__ import annotations

import re

# 甲部 MCQ 演算法題：參考 24_25 template para 227（外層 \t，內層 \t\t）
MCQ_CODE_BASE_DEPTH = 1

# DSE Paper 1A 常見偽代碼用語（參考 2025 等年度）
_PSEUDO_LINE = re.compile(
    r"^\s*("
    r"[iI]\s*←|←|→|當\s|重複|直至|輸出|輸入|若\s|否則|結束|程序|"
    r"FOR\s|WHILE\s|IF\s|OUTPUT|INPUT|PROCEDURE|END|REPEAT"
    r")",
    re.IGNORECASE,
)
_PYTHON_LINE = re.compile(
    r"^\s*(def |class |import |from |if |elif |else:|while |for |print\(|return )",
    re.IGNORECASE,
)
_PYTHON_INTRO = re.compile(r"Python\s*程式|下列\s*Python", re.IGNORECASE)
_PYTHON_ASSIGN = re.compile(r"^[a-zA-Z_]\w*\s*=", re.IGNORECASE)
_INTRO_PREFIX = re.compile(
    r"^(考慮以下(?:程序|偽代碼|算法|Python 程式)[^：:\n]*[：:])(.*)$",
    re.IGNORECASE,
)
_STMT_START = re.compile(
    r"^("
    r"[\w]+ ←|輸出|輸入|若|當|重複|否則|"
    r"FOR |WHILE |IF |OUTPUT|INPUT|def |print\(|while |if |for "
    r")",
    re.IGNORECASE,
)
_TRAILING_QUESTION = re.compile(r"。([^。]+[？?])$")


def _is_python_statement(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    if _PYTHON_LINE.match(s) or _PYTHON_ASSIGN.match(s):
        return True
    if re.match(r"^[a-zA-Z_]\w*\s*[\[,]", s):
        return True
    return False


def is_code_content_line(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    if s.endswith("？") or s.endswith("?"):
        return False
    if s.startswith(("考慮", "下列", "以下", "細看", "參考", "假設", "設計", "就", "在", "執行下列")):
        return False
    if _PSEUDO_LINE.match(s) or _is_python_statement(s):
        return True
    if "←" in s or "→" in s:
        return True
    return False


def is_code_layout_line(line: str) -> bool:
    """True after layout (tab-prefixed pseudocode) or raw code line."""
    if not line.strip():
        return False
    stripped = line.lstrip("\t")
    if line.startswith("\t") and (
        is_code_content_line(stripped) or "←" in stripped or "→" in stripped
    ):
        return True
    return is_code_content_line(line)


def indent_code_line(line: str, *, depth: int = MCQ_CODE_BASE_DEPTH) -> str:
    """Prefix with tabs for DOCX (Courier New applied at render)."""
    stripped = line.strip()
    if not stripped:
        return ""
    lead_spaces = len(line) - len(line.lstrip(" \t"))
    if lead_spaces and not line.startswith("\t"):
        depth = MCQ_CODE_BASE_DEPTH + max(0, lead_spaces // 2)
    return f"{'\t' * depth}{stripped}"


def split_semicolon_statements(text: str) -> list[str]:
    """Split ``；`` / ``;`` when the following segment starts a new statement."""
    text = text.strip()
    if not text or ("；" not in text and ";" not in text):
        return [text] if text else []
    parts = re.split(r"[；;]", text)
    out = [parts[0].strip()]
    for part in parts[1:]:
        part = part.strip()
        if not part:
            continue
        if _STMT_START.match(part) and not out[-1].rstrip().endswith(("則", ":", "：")):
            out.append(part)
        else:
            out[-1] = f"{out[-1]}；{part}"
    return [s for s in out if s.strip()]


def split_mixed_intro_line(line: str) -> tuple[str | None, list[str], str | None]:
    """
    ``考慮以下偽代碼：x ← 2；…`` → intro, code lines, optional trailing question.
    """
    line = line.strip()
    m = _INTRO_PREFIX.match(line)
    if not m:
        return None, [], line

    intro = m.group(1).strip()
    rest = m.group(2).strip()
    if not rest:
        return intro, [], None

    qm = _TRAILING_QUESTION.search(rest)
    trailing: str | None = None
    code_text = rest
    if qm and ("←" in rest or "若" in rest or "則" in rest):
        trailing = qm.group(1).strip()
        code_text = rest[: qm.start()].strip().rstrip("。")

    code_lines: list[str] = []
    if code_text:
        if is_code_content_line(code_text) or "←" in code_text:
            code_lines = split_semicolon_statements(code_text)
        else:
            code_lines = [code_text]

    return intro, code_lines, trailing


def expand_code_source_line(line: str) -> list[str]:
    """One spec line → one or more code source lines (semicolon split)."""
    lead = line[: len(line) - len(line.lstrip(" \t"))]
    stripped = line.strip()
    parts = split_semicolon_statements(stripped)
    if len(parts) <= 1:
        return [line.rstrip()] if stripped else []
    return [f"{lead}{p}" for p in parts]


def _en_pseudo_to_zh(line: str) -> str:
    """Map common English-style keywords to DSE Chinese 偽代碼."""
    s = line.strip()
    repl = (
        (r"^PROCEDURE\s+(\w+)", r"程序 \1"),
        (r"^ENDPROCEDURE\s*$", "結束程序"),
        (r"^OUTPUT\s+", "輸出 "),
        (r"^INPUT\s+", "輸入 "),
        (r"^ENDFOR\s*$", "結束重複"),
        (r"^ENDWHILE\s*$", "結束當"),
        (r"^ENDIF\s*$", "結束若"),
        (r"^ELSE\s*$", "否則"),
        (r"^FOR\s+(\w+)\s*←\s*(\d+)\s+TO\s+(\w+)", r"重複 \1 由 \2 至 \3"),
        (r"^WHILE\s+(.+?)\s+DO\s*$", r"當 \1"),
        (r"^IF\s+(.+?)\s+THEN\s*$", r"若 \1 則"),
    )
    for pat, sub in repl:
        s = re.sub(pat, sub, s, flags=re.IGNORECASE)
    return s


def _code_line_depth(zh: str, *, prev: str | None, open_blocks: int, source_line: str) -> tuple[int, int]:
    """Return (tab depth, updated open_blocks)."""
    stripped_src = source_line.lstrip(" \t")
    lead = len(source_line) - len(stripped_src)
    if source_line.startswith("\t"):
        tab_lead = len(source_line) - len(source_line.lstrip("\t"))
        return MCQ_CODE_BASE_DEPTH + open_blocks + max(0, tab_lead - 1), open_blocks

    if lead >= 2:
        return MCQ_CODE_BASE_DEPTH + open_blocks, open_blocks
    if lead == 1 and source_line.startswith(" "):
        return MCQ_CODE_BASE_DEPTH + open_blocks + 1, open_blocks

    depth = MCQ_CODE_BASE_DEPTH + open_blocks
    header_only = zh.startswith(("當 ", "若 ", "重複 ")) and (
        zh.rstrip().endswith(("則", "：", ":"))
        or (zh.endswith("則") and "←" not in zh.split("則", 1)[-1])
    )
    inline_block = zh.startswith(("當 ", "若 ", "重複 ")) and "：" in zh and any(
        ch in zh.split("：", 1)[1] for ch in ("←", "輸出", "輸入")
    )

    if inline_block:
        return MCQ_CODE_BASE_DEPTH, open_blocks

    if header_only:
        return depth, open_blocks + 1

    if zh.startswith(("當 ", "若 ", "重複 ")) and lead == 0 and not zh.rstrip().endswith(
        ("則", "：", ":")
    ):
        return MCQ_CODE_BASE_DEPTH + open_blocks, open_blocks + 1

    if zh.startswith(("輸出", "結束")) and lead == 0:
        return MCQ_CODE_BASE_DEPTH, max(0, open_blocks - 1)

    return depth, open_blocks


def format_code_block(text: str, *, lang: str = "pseudo_zh") -> str:
    """
    Normalise multiline code in MCQ stems: Chinese keywords, consistent indent.

    ``lang``: ``pseudo_zh`` | ``python`` (Python keeps 4-space inner indent → tabs).
    """
    out: list[str] = []
    open_blocks = 0
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        if lang == "python":
            stripped = line.lstrip()
            lead_spaces = len(line) - len(stripped)
            depth = MCQ_CODE_BASE_DEPTH + (lead_spaces // 4)
            out.append(indent_code_line(stripped, depth=depth))
            continue
        zh = _en_pseudo_to_zh(line) if is_code_content_line(line) else line.strip()
        if is_code_content_line(line):
            depth, open_blocks = _code_line_depth(
                zh, prev=out[-1] if out else None, open_blocks=open_blocks, source_line=line
            )
            out.append(indent_code_line(zh, depth=depth))
        else:
            out.append(indent_code_line(line, depth=MCQ_CODE_BASE_DEPTH))
    return "\n".join(out)


def format_mcq_stem_with_code(stem: str) -> str:
    """
    Split stem into prose + code regions; format code with indentation.

    Handles inline code after ``考慮以下偽代碼：`` and ``；``-separated statements.
    """
    parts: list[str] = []
    code_buf: list[str] = []
    lang = "pseudo_zh"
    python_mode = False

    def flush_code() -> None:
        nonlocal code_buf, lang
        if code_buf:
            block = format_code_block("\n".join(code_buf), lang=lang)
            parts.extend(block.splitlines())
            code_buf = []

    for raw in stem.splitlines():
        line = raw.rstrip()
        if not line.strip():
            flush_code()
            python_mode = False
            continue

        if _PYTHON_INTRO.search(line):
            flush_code()
            parts.append(line.strip())
            python_mode = True
            lang = "python"
            continue

        if python_mode and _is_python_statement(line):
            code_buf.append(line)
            continue

        intro, code_lines, trailing = split_mixed_intro_line(line)
        if intro is not None:
            flush_code()
            python_mode = False
            lang = "pseudo_zh"
            parts.append(intro)
            if code_lines:
                code_buf.extend(code_lines)
                flush_code()
            if trailing:
                parts.append(trailing)
            continue

        if is_code_content_line(line):
            code_buf.extend(expand_code_source_line(line))
        else:
            flush_code()
            python_mode = False
            lang = "pseudo_zh"
            parts.append(line.strip())
    flush_code()
    return "\n".join(p for p in parts if p is not None)


def insert_code_block_gaps(lines: list[str], *, max_lines: int | None = None) -> list[str]:
    """
    Insert blank lines on prose↔code transitions (DSE style).

    If ``max_lines`` is set and gaps would exceed budget, skip gaps (use paragraph spacing).
    """
    if not lines:
        return lines

    def with_gaps(src: list[str]) -> list[str]:
        out: list[str] = []
        for line in src:
            if not line.strip():
                if out and out[-1] != "":
                    out.append("")
                continue
            cur = is_code_layout_line(line)
            if out and out[-1].strip():
                prev = is_code_layout_line(out[-1])
                # Blank before code block only; after code use paragraph spacing + pre-option blank
                if not prev and cur:
                    out.append("")
            out.append(line)
        return out

    expanded = with_gaps(lines)
    if max_lines is not None and len(expanded) > max_lines:
        return lines
    return expanded


def max_prose_lines_for_span(span: int, *, combo: bool) -> int:
    """Max non-option lines before the blank line above A/B/C/D."""
    if combo:
        return span - 8
    return span - 5
