"""Build MCQ answer keys by shuffling option order (not swapping correct letters)."""
from __future__ import annotations

import random
import re
import sys
from pathlib import Path
from typing import Optional  # noqa: F401 — used in _inline_stem_line return

_QC = Path(__file__).resolve().parents[1] / "question-quality-check"
if str(_QC) not in sys.path:
    sys.path.insert(0, str(_QC))

from answer_pattern_check import has_pattern_issues

_OPTION_RE = re.compile(r"^(\t*)([ABCD])\.\t(.*)$", re.MULTILINE)
_LETTERS = "ABCD"

# 組合選項題：不可 random shuffle；按規則排序 A→D
# 單項 (1)→(2)→(3)… → 多項組合按數字序 → 「皆是／全部」放最後
_SUBITEM_STEM_RE = re.compile(r"^\s*\(\d+\)\s", re.MULTILINE)
_COMBO_OPTION_RE = re.compile(
    r"\(\d+\).*(?:只有|和|皆是|及|與)|(?:只有|和).*\(\d+\)",
    re.IGNORECASE,
)
_NUM_IN_OPTION_RE = re.compile(r"\((\d+)\)")

# Correct option index (0=A … 3=D) per MCQ 1–20 — from stems in s3_cmp_term2_exam_easy_from_s2_template._mcq_blocks
MCQ_CORRECT_INDEX: tuple[int, ...] = (
    3,  # 1  (1)(2)(3) 皆是 → D（組合題排序後）
    1,  # 2  pip
    2,  # 3  Hallucination
    3,  # 4  對照官方
    0,  # 5  try…except
    0,  # 6  init→selectROI→update
    2,  # 7  提高 minNeighbors
    3,  # 8  刪除同學檔案
    0,  # 9  預設鏡頭
    1,  # 10 總監
    2,  # 11 測試後迭代
    3,  # 12 減少運算量
    0,  # 13 KCF 較快
    1,  # 14 password.json
    2,  # 15 os.remove
    3,  # 16 quiz_data 分開
    0,  # 17 tkinter
    1,  # 18 CSRT
    2,  # 19 學術誠信
    3,  # 20 VideoCapture
)


def _expand_inline_options(lines: list[str]) -> list[str]:
    """Split 'stem\\nA.\\tx\\nB.\\ty…' into separate lines."""
    out: list[str] = []
    for line in lines:
        if re.search(r"[ABCD]\.\t", line) and line.count("\n"):
            parts = re.split(r"(?=\t?[ABCD]\.\t)", line)
            for part in parts:
                part = part.strip("\n")
                if part:
                    out.append(part)
        else:
            out.append(line)
    return out


def _parse_options(block_lines: list[str]) -> tuple[list[str], list[str], list[str]]:
    """Return (prefix_lines, option_texts[4], suffix_lines)."""
    lines = _expand_inline_options(block_lines)
    prefix: list[str] = []
    options: list[str] = []
    suffix: list[str] = []
    phase = "prefix"
    for line in lines:
        m = _OPTION_RE.match(line) or re.match(r"^([ABCD])\.\t(.*)$", line.strip())
        if m:
            phase = "options"
            text = m.group(3) if m.lastindex and m.lastindex >= 3 else m.group(2)
            options.append(text.strip())
            continue
        if phase == "options" and options:
            phase = "suffix"
        if phase == "prefix":
            prefix.append(line)
        else:
            suffix.append(line)
    if len(options) != 4:
        raise ValueError(f"MCQ block must have 4 options, got {len(options)}: {block_lines!r}")
    return prefix, options, suffix


def _stem_subitem_numbers(block_lines: list[str]) -> frozenset[int]:
    nums = [int(x) for x in re.findall(r"^\s*\((\d+)\)\s", "\n".join(block_lines), re.MULTILINE)]
    return frozenset(nums)


def _option_number_tuple(text: str) -> tuple[int, ...]:
    return tuple(sorted({int(x) for x in _NUM_IN_OPTION_RE.findall(text)}))


def _is_all_combination_option(text: str, stem_nums: frozenset[int]) -> bool:
    if re.search(r"皆是|全部都|全部皆", text):
        return True
    nums = _option_number_tuple(text)
    return len(nums) >= 2 and frozenset(nums) == stem_nums


def _combo_option_sort_key(text: str, stem_nums: frozenset[int]) -> tuple:
    """(tier, nums): tier 0 = 單項/部分組合按 (1)<(1,2)<(2,3)；tier 1 = 皆是（最後）。"""
    nums = _option_number_tuple(text)
    if _is_all_combination_option(text, stem_nums):
        return (1, nums)
    return (0, nums)


def sort_combination_options(
    options: list[str],
    stem_nums: frozenset[int],
    correct_index: int,
) -> tuple[list[str], int]:
    """Reorder combination options; return new list and new correct index."""
    correct_text = options[correct_index]
    sorted_opts = sorted(options, key=lambda t: _combo_option_sort_key(t, stem_nums))
    new_index = sorted_opts.index(correct_text)
    return sorted_opts, new_index


def is_ordered_combination_mcq(block_lines: list[str]) -> bool:
    """
    Detect 「組合選項」MCQ: stem lists (1)(2)(3)… and options combine them
    (e.g.「只有 (1)」「(1) 和 (2)」「(1)、(2) 和 (3) 皆是」).
    These must keep A→D in logical order — do not shuffle.
    """
    text = "\n".join(block_lines)
    if len(_SUBITEM_STEM_RE.findall(text)) < 2:
        return False
    try:
        _, options, _ = _parse_options(block_lines)
    except ValueError:
        return False
    combo_opts = sum(1 for o in options if _COMBO_OPTION_RE.search(o))
    return combo_opts >= 2


def _is_micro_mcq_slot(block_lines: list[str]) -> bool:
    """Two-paragraph slot: stem and options merged in the first paragraph."""
    if is_ordered_combination_mcq(block_lines):
        return False
    return len(block_lines) <= 2


def _is_compact_mcq_slot(block_lines: list[str]) -> bool:
    """Three-paragraph slot: stem | options block | blank."""
    if is_ordered_combination_mcq(block_lines):
        return False
    return len(block_lines) == 3


def _compact_options_paragraph(options: list[str]) -> str:
    return "\n".join(f"\t{_LETTERS[i]}.\t{options[i]}" for i in range(4))


def _options_only_paragraph(options: list[str]) -> str:
    return "\n" + _compact_options_paragraph(options)


def _stem_line_from_prefix(prefix: list[str], block_lines: list[str]) -> str:
    if prefix:
        return prefix[0].split("\n", 1)[0]
    return block_lines[0].split("\n", 1)[0]


def _rebuild_micro_block(
    block_lines: list[str],
    prefix: list[str],
    options: list[str],
) -> list[str]:
    stem = _stem_line_from_prefix(prefix, block_lines)
    merged = f"{stem}\n{_compact_options_paragraph(options)}"
    return [merged, ""][: len(block_lines)]


def _rebuild_compact_block(
    block_lines: list[str],
    prefix: list[str],
    options: list[str],
) -> list[str]:
    stem = _stem_line_from_prefix(prefix, block_lines)
    merged = f"{stem}\n{_compact_options_paragraph(options)}"
    return [merged, "", ""][: len(block_lines)]


def _rebuild_block_preserve_layout(
    block_lines: list[str],
    prefix: list[str],
    options: list[str],
    suffix: list[str],
) -> list[str]:
    """Write options back without shuffling; match original inline vs multiline layout."""
    if _is_micro_mcq_slot(block_lines):
        return _rebuild_micro_block(block_lines, prefix, options)
    if _is_compact_mcq_slot(block_lines):
        return _rebuild_compact_block(block_lines, prefix, options)

    stem_inline = _inline_stem_line(block_lines)
    if stem_inline is not None:
        opts = _compact_options_paragraph(options)
        merged = f"{stem_inline}\n{opts}"
        new_lines = [merged]
        while len(new_lines) < len(block_lines):
            new_lines.append(block_lines[len(new_lines)] if block_lines[len(new_lines)] == "" else "")
        return new_lines[: len(block_lines)]

    stem = _stem_line_from_prefix(prefix, block_lines)
    new_lines = [stem, _options_only_paragraph(options)]
    new_lines.extend(suffix)
    while len(new_lines) < len(block_lines):
        new_lines.append("")
    return new_lines[: len(block_lines)]


def _inline_stem_line(block_lines: list[str]) -> Optional[str]:
    for line in block_lines:
        if re.search(r"[ABCD]\.\t", line) and "\n" in line:
            stem = line.split("\n", 1)[0]
            if re.match(r"\d+\.", stem.strip()):
                return stem
    return None


def _rebuild_combo_block(
    block_lines: list[str],
    prefix: list[str],
    options: list[str],
    suffix: list[str],
) -> list[str]:
    """Keep (1)(2)(3) sub-items; replace only A–D option lines."""
    new_lines: list[str] = []
    opt_i = 0
    for line in block_lines:
        if re.match(r"^\t?[ABCD]\.\t", line.strip()) or re.match(r"^[ABCD]\.\t", line):
            if opt_i < 4:
                lead = "\t" if line.startswith("\t") else ""
                new_lines.append(f"{lead}{_LETTERS[opt_i]}.\t{options[opt_i]}")
                opt_i += 1
            continue
        new_lines.append(line)
    while len(new_lines) < len(block_lines):
        new_lines.append(block_lines[len(new_lines)] if block_lines[len(new_lines)] == "" else "")
    return new_lines[: len(block_lines)]


def permute_mcq_block(
    block_lines: list[str],
    correct_index: int,
    rng: random.Random,
    *,
    allow_shuffle: bool = True,
) -> tuple[list[str], str]:
    """Shuffle A–D option order; return new block lines and new correct letter."""
    prefix, options, suffix = _parse_options(block_lines)
    if is_ordered_combination_mcq(block_lines):
        stem_nums = _stem_subitem_numbers(block_lines)
        options, correct_index = sort_combination_options(options, stem_nums, correct_index)
        letter = _LETTERS[correct_index]
        return _rebuild_combo_block(block_lines, prefix, options, suffix), letter

    if not allow_shuffle:
        return block_lines, _LETTERS[correct_index]

    order = [0, 1, 2, 3]
    rng.shuffle(order)
    shuffled = [options[i] for i in order]
    new_letter = _LETTERS[order.index(correct_index)]

    if _is_micro_mcq_slot(block_lines):
        return _rebuild_micro_block(block_lines, prefix, shuffled), new_letter
    if _is_compact_mcq_slot(block_lines):
        return _rebuild_compact_block(block_lines, prefix, shuffled), new_letter

    stem_inline = _inline_stem_line(block_lines)
    if stem_inline is not None:
        opts = _compact_options_paragraph(shuffled)
        merged = f"{stem_inline}\n{opts}"
        new_lines = [merged]
        while len(new_lines) < len(block_lines):
            new_lines.append("" if block_lines[len(new_lines)] == "" else block_lines[len(new_lines)])
        return new_lines[: len(block_lines)], new_letter

    new_lines = list(prefix)
    for i, text in enumerate(shuffled):
        new_lines.append(f"\t{_LETTERS[i]}.\t{text}")
    new_lines.extend(suffix)
    while len(new_lines) < len(block_lines):
        new_lines.append("")
    return new_lines[: len(block_lines)], new_letter


def build_random_mcq_key(
    blocks: dict[int, list[str]],
    *,
    correct_indices: tuple[int, ...] = MCQ_CORRECT_INDEX,
    rng: Optional[random.Random] = None,
    max_attempts: int = 8000,
) -> tuple[dict[int, list[str]], str]:
    """
    Permute each question's options until the 20-letter key is balanced and pattern-free.
    """
    if len(correct_indices) != len(blocks):
        raise ValueError("correct_indices length must match MCQ block count")
    rng = rng or random.Random()

    for _ in range(max_attempts):
        new_blocks: dict[int, list[str]] = {}
        letters: list[str] = []
        for q in sorted(blocks):
            nb, letter = permute_mcq_block(
                blocks[q],
                correct_indices[q - 1],
                rng,
                allow_shuffle=not is_ordered_combination_mcq(blocks[q]),
            )
            new_blocks[q] = nb
            letters.append(letter)
        key = "".join(letters)
        counts = {ch: letters.count(ch) for ch in _LETTERS}
        if max(counts.values()) - min(counts.values()) > 1:
            continue
        if has_pattern_issues(letters, alphabet=_LETTERS):
            continue
        return new_blocks, key
    raise RuntimeError("Could not build random MCQ key after permuting options")
