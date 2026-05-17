"""MCQ answer-key balance check (A/B/C/D distribution)."""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional

from answer_pattern_check import check_letter_sequence, _pattern_config
from exam_spec import ExamItem, load_spec, spec_items
from quality_lib import extract_lines

DEFAULT_LETTERS = ("A", "B", "C", "D")
_ANSWER_FIELD_NAMES = ("answer", "correct", "key", "correct_answer")
_MCQ_KEY_LINE_RE = re.compile(r"^[ABCD](?:\s*[ABCD])+\s*$", re.IGNORECASE)


@dataclass(frozen=True)
class McqAnswerEntry:
    index: int
    letter: str
    item_id: str = ""


@dataclass
class McqBalanceIssue:
    kind: str  # imbalanced | missing_answers | count_mismatch
    message: str
    counts: dict[str, int] = field(default_factory=dict)
    expected_range: tuple[int, int] = (0, 0)


@dataclass
class McqCheckResult:
    source: str
    total_mcq: int
    answers_found: int
    counts: dict[str, int] = field(default_factory=dict)
    expected_per_letter: tuple[int, int] = (0, 0)  # lo, hi
    spread: int = 0  # max - min
    ok: bool = True
    balance_ok: bool = True
    pattern_ok: bool = True
    issues: list[McqBalanceIssue] = field(default_factory=list)
    pattern_issues: list[dict[str, Any]] = field(default_factory=list)
    answers: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "balance_ok": self.balance_ok,
            "pattern_ok": self.pattern_ok,
            "source": self.source,
            "total_mcq": self.total_mcq,
            "answers_found": self.answers_found,
            "counts": self.counts,
            "expected_per_letter": list(self.expected_per_letter),
            "spread": self.spread,
            "answers": self.answers,
            "issues": [asdict(i) for i in self.issues],
            "pattern_issues": self.pattern_issues,
        }


def _normalize_letter(ch: str, letters: tuple[str, ...]) -> Optional[str]:
    u = ch.strip().upper()
    if u in letters:
        return u
    return None


def parse_answer_letters(raw: str, *, letters: tuple[str, ...] = DEFAULT_LETTERS) -> list[str]:
    """Extract A–D letters from a key string (spaces / grouping ignored)."""
    out: list[str] = []
    for ch in raw.upper():
        if ch in letters:
            out.append(ch)
    return out


def _mcq_items(spec: dict) -> list[ExamItem]:
    return [i for i in spec_items(spec) if i.section.lower() in ("mcq", "section_a", "甲部")]


def _answer_from_item(item: ExamItem, letters: tuple[str, ...]) -> Optional[str]:
    for name in _ANSWER_FIELD_NAMES:
        raw = item.meta.get(name)
        if raw is None:
            continue
        letter = _normalize_letter(str(raw), letters)
        if letter:
            return letter
    return None


def mcq_answers_from_spec(
    spec: dict,
    *,
    letters: tuple[str, ...] = DEFAULT_LETTERS,
) -> tuple[list[McqAnswerEntry], str]:
    """
    Read MCQ answers from spec items (answer field) or meta.mcq_answers / mcq_answer_key.
    Returns (entries, source_label).
    """
    items = _mcq_items(spec)
    if not items:
        return [], "none"

    per_item: list[McqAnswerEntry] = []
    for idx, item in enumerate(items, start=1):
        letter = _answer_from_item(item, letters)
        if letter:
            per_item.append(McqAnswerEntry(index=idx, letter=letter, item_id=item.id))

    if len(per_item) == len(items):
        return per_item, "items.answer"

    meta = spec.get("meta", {})
    for key in ("mcq_answers", "mcq_answer_key", "answer_key"):
        raw = meta.get(key)
        if not raw:
            continue
        parsed = parse_answer_letters(str(raw), letters=letters)
        if parsed:
            entries = [
                McqAnswerEntry(
                    index=i + 1,
                    letter=ch,
                    item_id=items[i].id if i < len(items) else "",
                )
                for i, ch in enumerate(parsed)
            ]
            return entries, f"meta.{key}"

    if per_item:
        return per_item, "items.answer(partial)"

    return [], "none"


def mcq_answers_from_docx(
    docx_path: Path,
    *,
    letters: tuple[str, ...] = DEFAULT_LETTERS,
    expected_count: Optional[int] = None,
) -> tuple[list[str], str]:
    """Find MCQ answer-key line in DOCX (e.g. 'DBBCB CBCBB BBACB AACBA')."""
    lines = extract_lines(docx_path.expanduser().resolve())
    candidates: list[tuple[int, str]] = []

    for i, line in enumerate(lines):
        compact = re.sub(r"\s+", "", line)
        if len(compact) < 8:
            continue
        if not all(c.upper() in letters for c in compact):
            continue
        if _MCQ_KEY_LINE_RE.match(line.strip()) or len(compact) >= 10:
            candidates.append((len(compact), line))

    if not candidates:
        return [], "none"

    # Prefer longest valid key line (main MCQ block, not stray fragments)
    candidates.sort(key=lambda x: -x[0])
    best_line = candidates[0][1]
    parsed = parse_answer_letters(best_line, letters=letters)

    if expected_count and len(parsed) > expected_count:
        parsed = parsed[:expected_count]

    return parsed, "docx.answer_key_line"


def _expected_range(n: int, num_letters: int = 4) -> tuple[int, int]:
    if n <= 0:
        return 0, 0
    lo = n // num_letters
    hi = (n + num_letters - 1) // num_letters
    return lo, hi


def _balance_config(meta: dict) -> dict[str, Any]:
    raw = meta.get("mcq_balance") or {}
    if not isinstance(raw, dict):
        raw = {}
    return raw


def check_mcq_balance(
    answers: list[str],
    *,
    total_mcq: int,
    source: str,
    letters: tuple[str, ...] = DEFAULT_LETTERS,
    max_spread: Optional[int] = None,
    strict_range: bool = True,
) -> McqCheckResult:
    n = len(answers)
    lo, hi = _expected_range(n or total_mcq, len(letters))
    if max_spread is None:
        # e.g. n=20 → spread≤2 is loose; range [5,5] is tighter
        max_spread = max(2, hi - lo + 1)

    counts = {L: 0 for L in letters}
    for ch in answers:
        u = ch.upper()
        if u in counts:
            counts[u] += 1

    spread = max(counts.values()) - min(counts.values()) if n else 0
    result = McqCheckResult(
        source=source,
        total_mcq=total_mcq,
        answers_found=n,
        counts=counts,
        expected_per_letter=(lo, hi),
        spread=spread,
        answers=list(answers),
    )

    result.balance_ok = result.ok

    if n == 0:
        result.ok = False
        result.balance_ok = False
        result.issues.append(
            McqBalanceIssue(
                kind="missing_answers",
                message="No MCQ answers found (set items[].answer or meta.mcq_answers)",
            )
        )
        return result

    if total_mcq and n != total_mcq:
        result.ok = False
        result.balance_ok = False
        result.issues.append(
            McqBalanceIssue(
                kind="count_mismatch",
                message=f"Answer count {n} ≠ MCQ item count {total_mcq}",
                counts=counts,
            )
        )

    out_of_range = [L for L in letters if not (lo <= counts[L] <= hi)]
    if strict_range and out_of_range:
        result.ok = False
        result.balance_ok = False
        result.issues.append(
            McqBalanceIssue(
                kind="imbalanced",
                message=(
                    f"Letter counts outside [{lo}, {hi}] per option: "
                    + ", ".join(f"{L}={counts[L]}" for L in out_of_range)
                ),
                counts=counts,
                expected_range=(lo, hi),
            )
        )
    elif spread > max_spread:
        result.ok = False
        result.balance_ok = False
        result.issues.append(
            McqBalanceIssue(
                kind="imbalanced",
                message=f"Spread {spread} > max {max_spread} (counts: {counts})",
                counts=counts,
                expected_range=(lo, hi),
            )
        )

    return result


def check_mcq_patterns(
    answers: list[str],
    *,
    meta: Optional[dict] = None,
    letters: tuple[str, ...] = DEFAULT_LETTERS,
) -> tuple[bool, list[dict[str, Any]]]:
    meta = meta or {}
    cfg = _pattern_config(meta, "mcq")
    pat = check_letter_sequence(
        [a.upper() for a in answers],
        section="mcq",
        alphabet="".join(letters),
        config=cfg,
    )
    return pat.ok, [i.to_dict() for i in pat.issues]


def apply_pattern_check(
    result: McqCheckResult,
    *,
    meta: Optional[dict] = None,
    letters: tuple[str, ...] = DEFAULT_LETTERS,
) -> McqCheckResult:
    if not result.answers:
        return result
    ok, issues = check_mcq_patterns(result.answers, meta=meta, letters=letters)
    result.pattern_ok = ok
    result.pattern_issues = issues
    if not ok:
        result.ok = False
    return result


def check_mcq_from_spec(
    spec: dict,
    *,
    source_label: str = "",
) -> McqCheckResult:
    meta = spec.get("meta", {})
    cfg = _balance_config(meta)
    letters = tuple(cfg.get("letters") or DEFAULT_LETTERS)
    letters = tuple(str(x).upper() for x in letters)

    items = _mcq_items(spec)
    entries, src = mcq_answers_from_spec(spec, letters=letters)
    answers = [e.letter for e in entries]

    result = check_mcq_balance(
        answers,
        total_mcq=len(items),
        source=source_label or src,
        letters=letters,
        max_spread=cfg.get("max_spread"),
        strict_range=cfg.get("strict_range", True),
    )
    return apply_pattern_check(result, meta=meta, letters=letters)


def check_mcq_from_docx(
    docx_path: Path,
    *,
    spec: Optional[dict] = None,
) -> McqCheckResult:
    docx_path = docx_path.expanduser().resolve()
    meta = (spec or {}).get("meta", {})
    cfg = _balance_config(meta)
    letters = tuple(str(x).upper() for x in (cfg.get("letters") or DEFAULT_LETTERS))

    total = len(_mcq_items(spec)) if spec else 0
    answers, src = mcq_answers_from_docx(docx_path, letters=letters, expected_count=total or None)

    if spec and not answers:
        return check_mcq_from_spec(spec, source_label=src)

    result = check_mcq_balance(
        answers,
        total_mcq=total or len(answers),
        source=src,
        letters=letters,
        max_spread=cfg.get("max_spread"),
        strict_range=cfg.get("strict_range", True),
    )
    return apply_pattern_check(result, meta=meta, letters=letters)


def check_mcq(
    *,
    spec: Optional[dict] = None,
    spec_path: Optional[Path] = None,
    docx_path: Optional[Path] = None,
) -> Optional[McqCheckResult]:
    """Run MCQ balance check; prefer spec answers, fall back to DOCX key line."""
    if spec_path and spec is None:
        spec = load_spec(spec_path)

    items = _mcq_items(spec) if spec else []
    if not items and not docx_path:
        return None

    entries, src = ([], "none")
    if spec:
        entries, src = mcq_answers_from_spec(spec)
    if entries and spec:
        letters = tuple(
            str(x).upper()
            for x in (_balance_config(spec.get("meta", {})).get("letters") or DEFAULT_LETTERS)
        )
        result = check_mcq_balance(
            [e.letter for e in entries],
            total_mcq=len(items),
            source=src,
            letters=letters,
            max_spread=_balance_config(spec.get("meta", {})).get("max_spread"),
            strict_range=_balance_config(spec.get("meta", {})).get("strict_range", True),
        )
        return apply_pattern_check(result, meta=spec.get("meta", {}), letters=letters)

    if docx_path:
        return check_mcq_from_docx(docx_path, spec=spec)

    if spec:
        return check_mcq_from_spec(spec)

    return None


def format_mcq_report(result: McqCheckResult) -> str:
    lo, hi = result.expected_per_letter
    lines = [
        f"MCQ answers: {'OK' if result.ok else 'ISSUES'}",
        f"Source: {result.source}",
        f"MCQ items: {result.total_mcq}, answers: {result.answers_found}",
        f"Balance: {'OK' if result.balance_ok else 'FAIL'} — "
        + "  ".join(f"{L}={result.counts.get(L, 0)}" for L in sorted(result.counts))
        + f"  (target [{lo},{hi}], spread={result.spread})",
        f"Pattern: {'OK' if result.pattern_ok else 'FAIL'} (no ABCD cycles / block rotation / long runs)",
    ]
    if result.answers and len(result.answers) <= 40:
        grouped = " ".join("".join(result.answers[i : i + 5]) for i in range(0, len(result.answers), 5))
        lines.append(f"Key: {grouped}")
    for issue in result.issues:
        lines.append(f"\n  [balance:{issue.kind}] {issue.message}")
    for p in result.pattern_issues:
        lines.append(f"\n  [pattern:{p.get('kind')}] {p.get('message')}")
    if result.ok and result.answers_found:
        lines.append("\nMCQ key is balanced and sufficiently random.")
    return "\n".join(lines)
