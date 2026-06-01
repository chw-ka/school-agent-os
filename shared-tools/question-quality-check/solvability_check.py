"""Check whether each exam item is answerable from its stem (data + prompts complete)."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from exam_spec import spec_items

_PLACEHOLDER = re.compile(r"\{[A-Z_][A-Z0-9_]*\}")
_SUBPART = re.compile(r"\(([a-z]{1,2}|[ivx]{1,4})\)", re.I)

_VAGUE_SQL = re.compile(
    r"寫出(一條)?\s*(CREATE\s+TABLE|SELECT)\s*[^。?？\n]{0,20}[。.]\s*$",
    re.I | re.M,
)
_SEE_TABLE = re.compile(r"見表|下表|如上表|上表所列")
_TABLE_HINT = re.compile(r"欄位如下|部分記錄見表|資料表（見表）|（見表）")
_SHEET_CTX = re.compile(r"試算表|欄\s*[A-Z]=|F2|COUNTIF|SUMIF|RANK|XLOOKUP|\$H\$")
_BMP_CTX = re.compile(r"BMP|像素|bit\s*真彩色|相片")
_UPLOAD_CTX = re.compile(r"MP3|上載速度|Mbps|下載")
_ERD_ASK = re.compile(r"ERD|實體關係圖|繪製.*關係")
_INTEGRITY_ONLY = re.compile(r"完整性問題|參照完整性|域完整性|實體完整性")
_HW_TABLE = re.compile(r"下表所列部件|完成下表|候選規格")
_ALGO_CODE = re.compile(
    r"found\s*←|WHILE|PUSH|POP|Enqueue|二分搜尋|線性搜尋|算法",
    re.I,
)
_TRACE_ASK = re.compile(r"追蹤|完成追蹤表|列出每次")
# Some items render tables into DOCX at execution time; allow "見下表" in their stems.
_RENDER_TABLE_SLOTS = frozenset({"b-01", "b-02", "b-05", "b-06", "c-05", "mcq-06", "mcq-13", "mcq-15"})


@dataclass
class SolvabilityIssue:
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
class SolvabilityCheckResult:
    candidate: str
    ok: bool
    issues: list[SolvabilityIssue] = field(default_factory=list)
    items_checked: int = 0

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "candidate": self.candidate,
            "items_checked": self.items_checked,
            "issues": [i.to_dict() for i in self.issues],
        }


def _add(issues: list[SolvabilityIssue], item_id: str, kind: str, msg: str, text: str) -> None:
    issues.append(SolvabilityIssue(item_id, kind, msg, snippet=(text or "")[:140]))


def check_item_solvability(item_id: str, text: str, *, section: str = "") -> list[SolvabilityIssue]:
    issues: list[SolvabilityIssue] = []
    t = (text or "").strip()
    if not t:
        _add(issues, item_id, "empty", "題幹為空，無法作答", t)
        return issues

    for m in _PLACEHOLDER.finditer(t):
        _add(issues, item_id, "placeholder", f"含有未替換佔位符：{m.group(0)}", t)

    if _SEE_TABLE.search(t) and not _TABLE_HINT.search(t):
        if item_id not in _RENDER_TABLE_SLOTS:
            _add(issues, item_id, "missing_table", "提及「見表／下表」但題幹無表內資料", t)

    if _VAGUE_SQL.search(t):
        _add(issues, item_id, "vague_sql", "SQL 題過於籠統（如「寫出 SELECT。」）", t)

    if item_id == "b-01":
        if not _SHEET_CTX.search(t):
            _add(issues, item_id, "scenario_mismatch", "試算表題缺欄位／儲存格說明", t)
        if _UPLOAD_CTX.search(t) or "新電腦" in t and "操作系統" in t and "F2" not in t:
            _add(issues, item_id, "scenario_mismatch", "情境與試算表公式題不符", t)

    if item_id == "b-02":
        if _HW_TABLE.search(t) and "CPU" not in t and "部件" not in t and item_id not in _RENDER_TABLE_SLOTS:
            _add(issues, item_id, "missing_table", "要求填表但無部件列表", t)

    if item_id == "b-03":
        if _BMP_CTX.search(t) and _UPLOAD_CTX.search(t):
            _add(issues, item_id, "scenario_mismatch", "BMP 估算題混用 MP3／上載速度", t)

    if item_id == "b-04":
        if _TRACE_ASK.search(t) and not _ALGO_CODE.search(t):
            _add(issues, item_id, "missing_algorithm", "要求追蹤但題幹無偽代碼", t)

    if item_id == "b-05":
        if "見表" in t and "TRANSACTION" not in t.upper():
            _add(issues, item_id, "missing_table", "乙部 SQL 題缺樣本資料表", t)

    if item_id == "c-01":
        if _INTEGRITY_ONLY.search(t) and not _ERD_ASK.search(t):
            _add(issues, item_id, "wrong_task", "應畫 ERD，題幹卻只問完整性插入", t)
        if not _ERD_ASK.search(t):
            _add(issues, item_id, "wrong_task", "丙部 c-01 應為 ERD 繪圖題", t)

    if item_id == "c-02":
        if "CREATE TABLE" not in t.upper() and "LOAN" not in t.upper():
            _add(issues, item_id, "missing_sql_skeleton", "欄位限制題缺 CREATE TABLE 骨架", t)

    if item_id == "c-05" and "MEMBER" not in t.upper():
        _add(issues, item_id, "missing_schema", "SQL 綜合題缺資料表名稱／欄位", t)

    if item_id in ("c-06", "c-07", "c-08") and _INTEGRITY_ONLY.search(t):
        _add(issues, item_id, "wrong_task", "程式開發題混入數據庫完整性", t)

    if section == "mcq":
        if not re.search(r"[A-D]\.\s", t):
            _add(issues, item_id, "mcq_options", "MCQ 缺少 A.–D. 選項", t)

    return issues


def check_spec_solvability(spec: dict, *, candidate_label: str = "") -> SolvabilityCheckResult:
    issues: list[SolvabilityIssue] = []
    n = 0
    for item in spec_items(spec):
        sec = item.section
        if sec in ("mcq", "section_a", "section_b", "section_c"):
            n += 1
            section = "mcq" if sec in ("mcq", "section_a") else sec
            issues.extend(check_item_solvability(item.id, item.text, section=section))
    hard = frozenset(
        {
            "empty",
            "placeholder",
            "scenario_mismatch",
            "missing_table",
            "missing_algorithm",
            "wrong_task",
            "missing_sql_skeleton",
            "mcq_options",
        }
    )
    ok = not any(i.kind in hard for i in issues)
    return SolvabilityCheckResult(
        candidate=candidate_label or str(spec.get("meta", {}).get("title", "")),
        ok=ok,
        issues=issues,
        items_checked=n,
    )


def format_solvability_report(result: SolvabilityCheckResult) -> str:
    lines = [
        f"Solvability (可作答): {'OK' if result.ok else 'ISSUES'}",
        f"  Items checked: {result.items_checked}",
    ]
    if not result.issues:
        lines.append("  All items have complete stems for students to answer.")
        return "\n".join(lines)
    by_id: dict[str, list[SolvabilityIssue]] = {}
    for i in result.issues:
        by_id.setdefault(i.item_id, []).append(i)
    for iid in sorted(by_id):
        lines.append(f"  {iid}:")
        for g in by_id[iid]:
            lines.append(f"    [{g.kind}] {g.message}")
    return "\n".join(lines)
