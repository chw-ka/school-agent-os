"""Verify MCQ keys against DSE bank; written items have reference answers."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from exam_spec import spec_items
from mcq_check import mcq_answers_from_spec

_REPO = Path(__file__).resolve().parents[2]
_BANK = _REPO / "Subjects/DSE-ICT/question-bank"

_MCQ_SLUGS = ("Paper1_MultipleChoice", "Paper1A_MultipleChoice")
_WRITTEN_SLUGS = (
    "Paper1B_CompulsoryStructured",
    "Paper2A_Database",
    "Paper2_Elective",
    "Paper2D_SoftwareDevelopment",
)
_YEARS = ("2021", "2022", "2023", "2024", "2025")


@dataclass
class AnswerVerifyIssue:
    item_id: str
    kind: str
    message: str
    expected: str = ""
    actual: str = ""

    def to_dict(self) -> dict:
        return {
            "item_id": self.item_id,
            "kind": self.kind,
            "message": self.message,
            "expected": self.expected,
            "actual": self.actual,
        }


@dataclass
class AnswerVerifyResult:
    ok: bool
    issues: list[AnswerVerifyIssue] = field(default_factory=list)
    mcq_checked: int = 0
    written_checked: int = 0

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "mcq_checked": self.mcq_checked,
            "written_checked": self.written_checked,
            "issues": [i.to_dict() for i in self.issues],
        }


def _load_bank_item(item_id: str) -> dict | None:
    for year in _YEARS:
        for slug in _MCQ_SLUGS + _WRITTEN_SLUGS:
            path = _BANK / year / slug / "questions.json"
            if not path.exists():
                continue
            data = json.loads(path.read_text(encoding="utf-8"))
            for it in data.get("items", []):
                if it.get("id") == item_id:
                    return it
    return None


def _bank_mcq_letter(item: dict) -> str | None:
    for key in ("answer", "correct", "correct_answer", "key"):
        raw = item.get(key)
        if raw and str(raw).strip():
            return str(raw).strip()[0].upper()
    text = item.get("text") or ""
    m = re.search(r"答案[：:]\s*([A-D])", text, re.I)
    if m:
        return m.group(1).upper()
    opts = item.get("options") or {}
    if isinstance(opts, dict):
        for L in "ABCD":
            if opts.get(L) and re.search(rf"^\*?\s*{L}", str(opts[L])):
                return L
    return None


def _written_has_answer(item: dict) -> bool:
    if item.get("answer_details"):
        return True
    for key in ("answer", "model_answer", "marking_notes"):
        if item.get(key):
            return True
    text = str(item.get("text") or "")
    return bool(re.search(r"答案[：:]|參考答案|評分", text))


def verify_spec_answers(
    spec: dict,
    *,
    bank_root: Path | None = None,
) -> AnswerVerifyResult:
    global _BANK
    if bank_root is not None:
        _BANK = bank_root
    issues: list[AnswerVerifyIssue] = []
    meta = spec.get("meta") or {}
    prov: list[str] = list(meta.get("mcq_provenance") or [])
    entries, _ = mcq_answers_from_spec(spec)
    answer_by_idx = {e.index: e.letter for e in entries}

    for item in spec_items(spec):
        if item.section in ("mcq", "section_a"):
            idx_m = re.search(r"(\d+)$", item.id)
            if not idx_m:
                continue
            idx = int(idx_m.group(1))
            letter = answer_by_idx.get(idx) or str(item.meta.get("answer") or "")[:1].upper()
            if not letter or letter not in "ABCD":
                issues.append(
                    AnswerVerifyIssue(
                        item.id,
                        "mcq_missing_answer",
                        "MCQ 缺少答案",
                        actual=letter,
                    )
                )
                continue
            bank_id = item.meta.get("dse_source") or (
                prov[idx - 1] if idx - 1 < len(prov) else ""
            )
            if not bank_id or str(bank_id).startswith(("fallback", "generated://")):
                continue
            bank = _load_bank_item(str(bank_id))
            if not bank:
                issues.append(
                    AnswerVerifyIssue(
                        item.id,
                        "mcq_bank_missing",
                        f"找不到 bank 題目 {bank_id}",
                    )
                )
                continue
            expected = _bank_mcq_letter(bank)
            if not expected:
                continue
            if expected != letter:
                issues.append(
                    AnswerVerifyIssue(
                        item.id,
                        "mcq_bank_diff",
                        f"答案與 DSE 原題不同（可能經改寫；請人工確認）bank={bank_id}",
                        expected=expected,
                        actual=letter,
                    )
                )

        elif item.section in ("section_b", "section_c"):
            sources = list(item.meta.get("dse_sources") or [])
            if item.meta.get("dse_source"):
                sources.insert(0, item.meta["dse_source"])
            seen: set[str] = set()
            has_any = False
            for sid in sources:
                if not sid or sid in seen or str(sid).startswith("generated://"):
                    continue
                seen.add(sid)
                bank = _load_bank_item(str(sid))
                if not bank:
                    continue
                if _written_has_answer(bank):
                    has_any = True
            bank_sources = [s for s in sources if s and not str(s).startswith("generated://")]
            if bank_sources and not has_any:
                issues.append(
                    AnswerVerifyIssue(
                        item.id,
                        "written_no_model_answer",
                        "乙／丙部來源題在 bank 無參考答案（需教師核對 marking scheme）",
                    )
                )

    hard_kinds = frozenset({"mcq_missing_answer", "mcq_bank_missing"})
    mcq_checked = len([i for i in spec_items(spec) if i.section in ("mcq", "section_a")])
    written_checked = len([i for i in spec_items(spec) if i.section in ("section_b", "section_c")])
    return AnswerVerifyResult(
        ok=not any(i.kind in hard_kinds for i in issues),
        issues=issues,
        mcq_checked=mcq_checked,
        written_checked=written_checked,
    )


def format_answer_verify_report(result: AnswerVerifyResult) -> str:
    lines = [
        f"Answer verification: {'OK' if result.ok else 'ISSUES'}",
        f"  MCQ items: {result.mcq_checked}, written: {result.written_checked}",
    ]
    if not result.issues:
        lines.append("  MCQ keys match bank where provenance is set; written sources have model answers.")
        return "\n".join(lines)
    for i in result.issues:
        extra = ""
        if i.expected or i.actual:
            extra = f" (expected={i.expected}, actual={i.actual})"
        lines.append(f"  [{i.kind}] {i.item_id}: {i.message}{extra}")
    return "\n".join(lines)
