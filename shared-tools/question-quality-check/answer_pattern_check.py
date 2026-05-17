"""
Detect predictable patterns in answer keys (MCQ A–D, matching letters, T/F, fill-in order).

Goal: keys should look random — no ABCD cycles, block rotations, long runs, bank-order fills, etc.
"""
from __future__ import annotations

import random
import re
import secrets
from dataclasses import asdict, dataclass, field
from typing import Any, Optional, Sequence


@dataclass
class PatternIssue:
    section: str  # mcq | matching | tf | fill
    kind: str
    message: str
    detail: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PatternCheckResult:
    section: str
    values: list[str]
    ok: bool = True
    issues: list[PatternIssue] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "section": self.section,
            "ok": self.ok,
            "values": self.values,
            "issues": [i.to_dict() for i in self.issues],
        }


@dataclass
class AllAnswerPatternsResult:
    ok: bool = True
    sections: list[PatternCheckResult] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "sections": [s.to_dict() for s in self.sections],
        }


def _pattern_config(meta: dict, section: str) -> dict[str, Any]:
    root = meta.get("answer_pattern") or {}
    if not isinstance(root, dict):
        root = {}
    sec = root.get(section) or {}
    if not isinstance(sec, dict):
        sec = {}
    defaults: dict[str, Any] = {
        "max_consecutive": 2,
        "forbid_periods": [2, 3, 4],
        "forbid_block_rotation": True,
        "block_size": 5,
        "min_unique_ratio": 0.2,
    }
    merged = {**defaults, **sec}
    return merged


def _max_run(seq: Sequence[str]) -> tuple[str, int]:
    if not seq:
        return "", 0
    best_ch, best_n = seq[0], 1
    cur_ch, cur_n = seq[0], 1
    for ch in seq[1:]:
        if ch == cur_ch:
            cur_n += 1
        else:
            if cur_n > best_n:
                best_ch, best_n = cur_ch, cur_n
            cur_ch, cur_n = ch, 1
    if cur_n > best_n:
        best_ch, best_n = cur_ch, cur_n
    return best_ch, best_n


def _is_periodic(seq: list[str], period: int) -> bool:
    if period < 1 or len(seq) < period * 2:
        return False
    base = seq[:period]
    return all(seq[i] == base[i % period] for i in range(len(seq)))


def _is_arithmetic_stride(seq: list[str], alphabet: str) -> bool:
    """Indices increase by +1 mod |alphabet| for whole sequence (e.g. ABCDABCD)."""
    if len(seq) < 4 or not alphabet:
        return False
    idx = [alphabet.index(c) for c in seq if c in alphabet]
    if len(idx) != len(seq):
        return False
    n = len(alphabet)
    step = (idx[1] - idx[0]) % n
    if step == 0:
        return False
    for i in range(1, len(idx)):
        if (idx[i] - idx[i - 1]) % n != step and (idx[i - 1] - idx[i]) % n != (n - step) % n:
            return False
    return True


def _is_block_rotation(seq: list[str], block_size: int) -> bool:
    """e.g. ABCDA | BCDAB | CDABC (each block is previous rotated by 1)."""
    if block_size < 2 or len(seq) < block_size * 2:
        return False
    if len(seq) % block_size != 0:
        return False
    blocks = [seq[i : i + block_size] for i in range(0, len(seq), block_size)]
    if len(blocks) < 2:
        return False
    for i in range(1, len(blocks)):
        if blocks[i] != blocks[i - 1][1:] + blocks[i - 1][:1]:
            return False
    return True


def _only_two_alternating(seq: list[str]) -> bool:
    if len(seq) < 6:
        return False
    uniq = set(seq)
    if len(uniq) != 2:
        return False
    a, b = list(uniq)
    return all(seq[i] in (a, b) and seq[i] != seq[i - 1] for i in range(1, len(seq)))


def check_letter_sequence(
    answers: list[str],
    *,
    section: str,
    alphabet: str,
    config: Optional[dict[str, Any]] = None,
) -> PatternCheckResult:
    cfg = config or {}
    letters = tuple(ch.upper() for ch in alphabet.upper())
    seq = [c.upper() for c in answers if c]
    result = PatternCheckResult(section=section, values=seq)

    if not seq:
        return result

    max_consec = int(cfg.get("max_consecutive", 2))
    ch, run = _max_run(seq)
    if run > max_consec:
        result.ok = False
        result.issues.append(
            PatternIssue(
                section=section,
                kind="long_run",
                message=f"Same letter {ch!r} appears {run} times in a row (max {max_consec})",
            )
        )

    for period in cfg.get("forbid_periods") or [2, 3, 4]:
        p = int(period)
        if _is_periodic(seq, p):
            result.ok = False
            result.issues.append(
                PatternIssue(
                    section=section,
                    kind="cyclic_repeat",
                    message=f"Repeating every {p} answers: {''.join(seq[:p])}…",
                    detail="".join(seq[: min(len(seq), p * 3)]),
                )
            )

    if _is_arithmetic_stride(seq, "".join(letters)):
        result.ok = False
        result.issues.append(
            PatternIssue(
                section=section,
                kind="arithmetic_stride",
                message="Letters follow a fixed step (e.g. ABCDABCD…)",
            )
        )

    if cfg.get("forbid_block_rotation", True):
        bs = int(cfg.get("block_size", 5))
        if _is_block_rotation(seq, bs):
            result.ok = False
            result.issues.append(
                PatternIssue(
                    section=section,
                    kind="block_rotation",
                    message=f"Each block of {bs} is a 1-letter rotation of the previous block",
                )
            )

    if _only_two_alternating(seq):
        result.ok = False
        result.issues.append(
            PatternIssue(
                section=section,
                kind="two_letter_alternate",
                message="Only two letters alternating (e.g. ABABAB…)",
            )
        )

    min_ratio = float(cfg.get("min_unique_ratio", 0.2))
    if letters and len(set(seq)) < max(2, int(len(letters) * min_ratio)):
        result.ok = False
        result.issues.append(
            PatternIssue(
                section=section,
                kind="low_variety",
                message=f"Too few distinct letters: {sorted(set(seq))}",
            )
        )

    return result


def _normalize_token(s: str) -> str:
    return re.sub(r"\s+", "", s).lower()


def _bank_order_similarity(answers: list[str], bank: list[str]) -> float:
    """1.0 = answers appear in same order as word bank (forbidden)."""
    if not answers or not bank:
        return 0.0
    a_norm = [_normalize_token(x) for x in answers]
    b_norm = [_normalize_token(x) for x in bank]
    if len(a_norm) != len(b_norm):
        return 0.0
    matches = sum(1 for x, y in zip(a_norm, b_norm) if x == y)
    return matches / len(a_norm)


def _matches_canonical_list_order(answers: list[str], canonical: list[str]) -> bool:
    if not answers or not canonical:
        return False
    a_norm = [_normalize_token(x) for x in answers]
    c_norm = [_normalize_token(x) for x in canonical]
    return a_norm == c_norm


def check_fill_sequence(
    answers: list[str],
    *,
    word_bank: list[str],
    section: str = "fill",
    config: Optional[dict[str, Any]] = None,
    canonical_order: Optional[list[str]] = None,
) -> PatternCheckResult:
    cfg = config or {}
    result = PatternCheckResult(section=section, values=answers)
    if not answers:
        return result

    if canonical_order and _matches_canonical_list_order(answers, canonical_order):
        result.ok = False
        result.issues.append(
            PatternIssue(
                section=section,
                kind="canonical_question_order",
                message="Fill answers follow fixed textbook / stem order (shuffle questions)",
            )
        )

    sim = _bank_order_similarity(answers, word_bank)
    threshold = float(cfg.get("max_bank_order_similarity", 0.6))
    if word_bank and sim >= threshold:
        result.ok = False
        result.issues.append(
            PatternIssue(
                section=section,
                kind="matches_word_bank_order",
                message=f"Fill answers follow word-bank order (similarity {sim:.0%})",
                detail=" → ".join(answers),
            )
        )

    sorted_ans = sorted(_normalize_token(a) for a in answers)
    sorted_bank = sorted(_normalize_token(b) for b in word_bank)
    if answers and sorted_ans == sorted_bank and len(set(sorted_ans)) == len(sorted_ans):
        norm_ans = [_normalize_token(a) for a in answers]
        if norm_ans == sorted(norm_ans) or norm_ans == sorted(norm_ans, reverse=True):
            result.ok = False
            result.issues.append(
                PatternIssue(
                    section=section,
                    kind="alphabetical_order",
                    message="Fill answers are in alphabetical order",
                )
            )

    return result


def check_tf_sequence(
    answers: list[str],
    *,
    section: str = "tf",
    config: Optional[dict[str, Any]] = None,
) -> PatternCheckResult:
    seq = [c.upper() for c in answers if c in ("T", "F")]
    return check_letter_sequence(seq, section=section, alphabet="TF", config=config)


def check_matching_sequence(
    answers: list[str],
    *,
    section: str = "matching",
    alphabet: str = "ABCDE",
    config: Optional[dict[str, Any]] = None,
) -> PatternCheckResult:
    seq = [c.upper() for c in answers if c in alphabet]
    result = check_letter_sequence(seq, section=section, alphabet=alphabet, config=config)

    if len(seq) >= 4:
        indices = [alphabet.index(c) for c in seq if c in alphabet]
        ascending = all(indices[i] + 1 == indices[i + 1] for i in range(len(indices) - 1))
        descending = all(indices[i] - 1 == indices[i + 1] for i in range(len(indices) - 1))
        if ascending:
            result.ok = False
            result.issues.append(
                PatternIssue(
                    section=section,
                    kind="sequential_letters",
                    message="Matching answers are in ascending A→E order",
                )
            )
        if descending:
            result.ok = False
            result.issues.append(
                PatternIssue(
                    section=section,
                    kind="sequential_letters",
                    message="Matching answers are in descending order",
                )
            )
    return result


def has_pattern_issues(answers: list[str], *, alphabet: str, config: Optional[dict] = None) -> bool:
    return not check_letter_sequence(answers, section="test", alphabet=alphabet, config=config).ok


def generate_random_balanced_letters(
    n: int,
    letters: str,
    *,
    config: Optional[dict[str, Any]] = None,
    rng: Optional[random.Random] = None,
    max_attempts: int = 5000,
) -> str:
    """Balanced counts per letter, shuffled until pattern checks pass."""
    letters = letters.upper()
    if n <= 0:
        return ""
    rng = rng or random.Random(secrets.randbits(64))
    base, rem = divmod(n, len(letters))
    pool: list[str] = []
    for ch in letters:
        pool.extend([ch] * (base + (1 if letters.index(ch) < rem else 0)))
    cfg = config or {}

    for _ in range(max_attempts):
        rng.shuffle(pool)
        if not has_pattern_issues(pool, alphabet=letters, config=cfg):
            return "".join(pool)
    raise RuntimeError(
        f"Could not generate random {letters} key of length {n} after {max_attempts} attempts"
    )


def generate_random_tf(n: int, *, config: Optional[dict] = None, rng: Optional[random.Random] = None) -> str:
    rng = rng or random.Random(secrets.randbits(64))
    cfg = {**(config or {}), "forbid_periods": [2], "max_consecutive": 3}
    for _ in range(5000):
        seq = [rng.choice("TF") for _ in range(n)]
        if not has_pattern_issues(seq, alphabet="TF", config=cfg):
            return "".join(seq)
    raise RuntimeError(f"Could not generate random T/F sequence of length {n}")


def generate_random_matching_block(
    n: int,
    letters: str = "ABCDE",
    *,
    config: Optional[dict] = None,
    rng: Optional[random.Random] = None,
) -> str:
    """n letters using each of A..E once (for standard matching row)."""
    letters = letters.upper()
    if n != len(letters):
        pool = [rng.choice(letters) if rng else random.choice(letters) for _ in range(n)]
        return "".join(pool)
    rng = rng or random.Random(secrets.randbits(64))
    pool = list(letters)
    cfg = {**(config or {}), "forbid_periods": [], "forbid_block_rotation": False}
    for _ in range(5000):
        rng.shuffle(pool)
        if not check_matching_sequence(pool, alphabet=letters, config=cfg).issues:
            return "".join(pool)
        # allow issues only from sequential - recheck
        r = check_matching_sequence(pool, alphabet=letters, config=cfg)
        if r.ok:
            return "".join(pool)
    raise RuntimeError("Could not generate random matching block")


def shuffle_fill_answers(
    bank: list[str],
    *,
    rng: Optional[random.Random] = None,
) -> list[str]:
    rng = rng or random.Random(secrets.randbits(64))
    out = list(bank)
    for _ in range(100):
        rng.shuffle(out)
        if check_fill_sequence(out, word_bank=bank).ok:
            return out
    raise RuntimeError("Could not shuffle fill answers away from bank order")


def check_all_answer_patterns(spec: dict) -> AllAnswerPatternsResult:
    meta = spec.get("meta", {})
    overall = AllAnswerPatternsResult()
    cfg_root = meta.get("answer_pattern") or {}

    # MCQ
    mcq_raw = meta.get("mcq_answers") or meta.get("mcq_answer_key") or ""
    if mcq_raw:
        from mcq_check import parse_answer_letters

        mcq_letters = parse_answer_letters(str(mcq_raw))
        mcq_cfg = _pattern_config(meta, "mcq")
        mcq_res = check_letter_sequence(mcq_letters, section="mcq", alphabet="ABCD", config=mcq_cfg)
        overall.sections.append(mcq_res)
        if not mcq_res.ok:
            overall.ok = False

    # Matching: list of strings per block
    match_raw = meta.get("matching_answers") or []
    if match_raw:
        mcfg = _pattern_config(meta, "matching")
        flat: list[str] = []
        if isinstance(match_raw, str):
            flat = list(match_raw.upper())
        else:
            for block in match_raw:
                flat.extend(list(str(block).upper()))
        m_res = check_matching_sequence(flat, config=mcfg)
        overall.sections.append(m_res)
        if not m_res.ok:
            overall.ok = False

    # T/F
    tf_raw = meta.get("tf_answers") or ""
    if tf_raw:
        tf_cfg = _pattern_config(meta, "tf")
        tf_res = check_tf_sequence(list(str(tf_raw).upper()), config=tf_cfg)
        overall.sections.append(tf_res)
        if not tf_res.ok:
            overall.ok = False

    # Fill: list of lists + banks
    fill_raw = meta.get("fill_answers") or []
    banks = meta.get("fill_word_banks") or []
    fcfg = _pattern_config(meta, "fill")
    if fill_raw:
        blocks = fill_raw if isinstance(fill_raw, list) and fill_raw and isinstance(fill_raw[0], list) else [fill_raw]
        bank_blocks = banks if banks else [[]] * len(blocks)
        for i, (ans_block, bank) in enumerate(zip(blocks, bank_blocks)):
            if not isinstance(ans_block, list):
                ans_block = list(ans_block)
            bank_list = list(bank) if bank else []
            f_res = check_fill_sequence(
                [str(a) for a in ans_block],
                word_bank=[str(b) for b in bank_list],
                section=f"fill-{i + 1}",
                config=fcfg,
            )
            overall.sections.append(f_res)
            if not f_res.ok:
                overall.ok = False

    return overall


def format_all_patterns_report(result: AllAnswerPatternsResult) -> str:
    lines = [f"Answer pattern (randomness): {'OK' if result.ok else 'PATTERNS DETECTED'}"]
    if not result.sections:
        lines.append("  (no answer keys in spec meta)")
        return "\n".join(lines)
    for sec in result.sections:
        preview = "".join(sec.values[:24])
        if len(sec.values) > 24:
            preview += "…"
        lines.append(f"\n  [{sec.section}] {'OK' if sec.ok else 'FAIL'}  {preview}")
        for issue in sec.issues:
            lines.append(f"    • {issue.kind}: {issue.message}")
    if result.ok:
        lines.append("\nNo predictable answer patterns detected.")
    return "\n".join(lines)
