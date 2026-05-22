"""Rule-based exam question fluency / coherence checks (通順)."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from exam_spec import ExamItem, spec_items

_META_MARKERS = (
    "以下各題參考上述情境",
    "部分設定取自不同 DSE",
    "已改編自 DSE 試題",
    "在下列校本情境中",
    "參考以下設定（已改編",
)

_SUBPART_RE = re.compile(r"\(([a-z]+|[ivx]+)\)", re.IGNORECASE)

_TOPIC_SQL = re.compile(
    r"SELECT\s|INSERT\s|UPDATE\s|DELETE\s|CREATE\s+TABLE|GROUP\s+BY|主關鍵|外鍵|ERD",
    re.IGNORECASE,
)
_TOPIC_MEDIA = re.compile(r"像素|BMP|視像|壓縮|多媒體|點陣|解像度", re.IGNORECASE)
_TOPIC_ANTIVIRUS = re.compile(r"病毒|防毒|掃描器|惡意", re.IGNORECASE)
_TOPIC_ALGO = re.compile(r"偽代碼|算法|堆疊|陣列\s*\[|線性搜尋", re.IGNORECASE)
_TOPIC_SHEET = re.compile(r"公式|試算表|VLOOKUP|COUNTIF|SUMIF|欄\s*[A-Z]|Sheet\d", re.IGNORECASE)
_TOPIC_VALIDATION = re.compile(r"有效性|驗證|奇偶|CHECKDIGIT|一次性密碼", re.IGNORECASE)

# slot_id → allowed topic tag sets (union); empty = any single family ok
_SLOT_TOPIC_ALLOW: dict[str, frozenset[str]] = {
    "b-06": frozenset({"sql", "sheet", "db"}),
}


@dataclass
class CoherenceIssue:
    item_id: str
    kind: str
    message: str
    snippet: str = ""

    def to_dict(self) -> dict:
        return {
            "item_id": self.item_id,
            "kind": self.kind,
            "message": self.message,
            "snippet": self.snippet,
        }


@dataclass
class CoherenceCheckResult:
    candidate: str
    ok: bool
    issues: list[CoherenceIssue] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "issue_count": len(self.issues),
            "issues": [i.to_dict() for i in self.issues],
        }


def _topic_tags(text: str) -> set[str]:
    tags: set[str] = set()
    if _TOPIC_SQL.search(text):
        tags.add("sql")
    if _TOPIC_MEDIA.search(text):
        tags.add("media")
    if _TOPIC_ANTIVIRUS.search(text):
        tags.add("antivirus")
    if _TOPIC_ALGO.search(text):
        tags.add("algo")
    if _TOPIC_SHEET.search(text):
        tags.add("sheet")
    if _TOPIC_VALIDATION.search(text):
        tags.add("validation")
    return tags


def _subpart_order_ok(text: str) -> str | None:
    """Return error message if (b) appears before (a), etc."""
    order_map = {ch: i for i, ch in enumerate("abcdefghijklmnopqrstuvwxyz")}
    seen: list[tuple[int, str]] = []
    for m in _SUBPART_RE.finditer(text):
        label = m.group(1).lower()
        if len(label) == 1 and label.isalpha():
            seen.append((m.start(), order_map.get(label, 99)))
    if len(seen) < 2:
        return None
    positions = [p for p, _ in seen]
    ranks = [r for _, r in seen]
    if ranks != sorted(ranks):
        return "子題標號順序混亂（例如 (b) 在 (a) 之前）"
    return None


def _orphan_subpart(text: str) -> str | None:
    for block in re.split(r"\n\n+", text):
        b = block.strip()
        if not b:
            continue
        if re.match(r"^\([ivx]+\)", b, re.I):
            return "子題以 (ii)/(iii) 開首但缺少 (i) 情境"
        if re.match(r"^\(a\)\s*\([ivx]+\)", b, re.I):
            return "子題以 (a)(ii) 開首但缺少完整 (i) 題幹"
    return None


def _topic_clash(text: str, item_id: str) -> str | None:
    tags = _topic_tags(text)
    if len(tags) <= 1:
        return None
    allowed = _SLOT_TOPIC_ALLOW.get(item_id)
    if allowed and tags <= allowed:
        return None
    clash_pairs = (
        ({"sql", "media"}, "SQL／數據庫與多媒體題混在同一題"),
        ({"sql", "antivirus"}, "SQL／數據庫與防毒題混在同一題"),
        ({"media", "antivirus"}, "多媒體與防毒題混在同一題"),
        ({"algo", "validation"}, "算法／堆疊與有效性檢驗硬拼"),
        ({"sheet", "media"}, "試算表與多媒體硬拼"),
        ({"sheet", "antivirus"}, "試算表與防毒硬拼"),
    )
    for pair, msg in clash_pairs:
        if pair <= tags:
            return msg
    if len(tags) >= 3:
        return f"多個不相干主題混雜：{', '.join(sorted(tags))}"
    return None


def check_text_coherence(item_id: str, text: str, *, section: str = "") -> list[CoherenceIssue]:
    issues: list[CoherenceIssue] = []
    t = (text or "").strip()
    if not t:
        issues.append(CoherenceIssue(item_id, "empty", "題幹為空"))
        return issues

    for marker in _META_MARKERS:
        if marker in t:
            issues.append(
                CoherenceIssue(
                    item_id,
                    "meta_bridge",
                    f"含有改編／橋接句（不應出現在試題）：{marker}",
                    snippet=t[:120],
                )
            )

    if "否則則" in t:
        issues.append(CoherenceIssue(item_id, "typo", "「否則則」重複用字", snippet=t[:80]))

    if re.match(r"^\([a-z]\)", t, re.I) and len(t) < 500:
        issues.append(
            CoherenceIssue(
                item_id,
                "cold_start",
                "題幹以子題標號開首，缺少完整情境",
                snippet=t[:100],
            )
        )

    err = _subpart_order_ok(t)
    if err:
        issues.append(CoherenceIssue(item_id, "subpart_order", err, snippet=t[:120]))

    err = _orphan_subpart(t)
    if err:
        issues.append(CoherenceIssue(item_id, "orphan_subpart", err, snippet=t[:120]))

    err = _topic_clash(t, item_id)
    if err:
        issues.append(CoherenceIssue(item_id, "topic_clash", err, snippet=t[:120]))

    # MCQ: need options A–D
    if section == "mcq":
        letters = sum(
            1
            for L in "ABCD"
            if re.search(rf"(?:^|\t){L}\.\s", t, re.M) or f"{L}、" in t
        )
        if letters < 4:
            issues.append(CoherenceIssue(item_id, "mcq_options", f"MCQ 選項不足（只得 {letters}/4）"))

    return issues


def check_spec_coherence(spec: dict, *, candidate_label: str = "") -> CoherenceCheckResult:
    issues: list[CoherenceIssue] = []
    for item in spec_items(spec):
        if item.section in ("section_b", "section_c", "mcq", "section_a"):
            section = "mcq" if item.section in ("mcq", "section_a") else item.section
            issues.extend(check_text_coherence(item.id, item.text, section=section))
    return CoherenceCheckResult(
        candidate=candidate_label or str(spec.get("meta", {}).get("title", "")),
        ok=not issues,
        issues=issues,
    )


def format_coherence_report(result: CoherenceCheckResult) -> str:
    lines = [f"Coherence (通順): {'OK' if result.ok else 'ISSUES'}"]
    if not result.issues:
        lines.append("  All items read as single-topic, ordered prompts.")
        return "\n".join(lines)
    by_id: dict[str, list[CoherenceIssue]] = {}
    for i in result.issues:
        by_id.setdefault(i.item_id, []).append(i)
    for iid, group in sorted(by_id.items()):
        lines.append(f"  {iid}:")
        for g in group:
            lines.append(f"    [{g.kind}] {g.message}")
    return "\n".join(lines)
