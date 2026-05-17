"""Extract, apply, and verify exam paper footer banner text in DOCX."""
from __future__ import annotations

import re
import zipfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional
from xml.etree import ElementTree as ET

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W_T = f"{{{W_NS}}}t"

# Strip Word page-number fields: 第5頁 / 第 5 頁 / 第二頁
_PAGE_RE = re.compile(r"第\s*[\d一二三四五六七八九十百千]+\s*頁")


@dataclass(frozen=True)
class FooterMeta:
    academic_year: str = ""
    level: str = ""
    term_exam: str = ""
    subject: str = ""

    def banner_text(self) -> str:
        parts = [p for p in (self.academic_year, self.level, self.term_exam, self.subject) if p]
        if self.term_exam and self.subject:
            return f"{self.academic_year} {self.level}{self.term_exam}-{self.subject}".strip()
        return " ".join(parts).strip()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FooterMeta:
        return cls(
            academic_year=str(data.get("academic_year", "")),
            level=str(data.get("level", "")),
            term_exam=str(data.get("term_exam", "")),
            subject=str(data.get("subject", "")),
        )


@dataclass
class FooterIssue:
    kind: str  # mismatch | missing | unexpected_change
    expected: str
    actual: str
    footer_part: str = ""


@dataclass
class FooterCheckResult:
    candidate: str
    expected: str
    actual: str
    ok: bool
    issues: list[FooterIssue] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "expected": self.expected,
            "actual": self.actual,
            "issues": [asdict(i) for i in self.issues],
        }


def _footer_xml_paths(docx_path: Path) -> list[str]:
    with zipfile.ZipFile(docx_path, "r") as zf:
        return sorted(n for n in zf.namelist() if n.startswith("word/footer") and n.endswith(".xml"))


def extract_footer_raw(docx_path: Path) -> dict[str, str]:
    """Join all w:t text per footer part file."""
    docx_path = docx_path.expanduser().resolve()
    out: dict[str, str] = {}
    with zipfile.ZipFile(docx_path, "r") as zf:
        for name in _footer_xml_paths(docx_path):
            root = ET.fromstring(zf.read(name))
            out[name] = "".join(t.text for t in root.iter(W_T) if t.text)
    return out


def extract_footer_banner(docx_path: Path) -> str:
    """Static footer banner without page-number field text."""
    parts = extract_footer_raw(docx_path)
    combined = " ".join(parts.values())
    banner = _PAGE_RE.sub("", combined)
    return re.sub(r"\s+", " ", banner).strip()


def _normalize_banner(s: str) -> str:
    s = re.sub(r"\s+", "", s)
    s = s.replace("－", "-").replace("—", "-")
    return s


def check_footer(
    candidate: Path,
    *,
    expected_banner: Optional[str] = None,
    expected_meta: Optional[FooterMeta | dict[str, Any]] = None,
    template: Optional[Path] = None,
) -> FooterCheckResult:
    candidate = candidate.expanduser().resolve()
    actual = extract_footer_banner(candidate)

    expected = expected_banner or ""
    if not expected and expected_meta is not None:
        meta = expected_meta if isinstance(expected_meta, FooterMeta) else FooterMeta.from_dict(expected_meta)
        expected = meta.banner_text()
    if not expected and template:
        expected = extract_footer_banner(template.expanduser().resolve())

    issues: list[FooterIssue] = []
    ok = True
    if not actual and expected:
        ok = False
        issues.append(FooterIssue("missing", expected, actual))
    elif expected and _normalize_banner(actual) != _normalize_banner(expected):
        ok = False
        issues.append(FooterIssue("mismatch", expected, actual))
    elif template and not expected:
        template_banner = extract_footer_banner(template.expanduser().resolve())
        if (
            template_banner
            and actual
            and _normalize_banner(actual) != _normalize_banner(template_banner)
        ):
            ok = False
            issues.append(
                FooterIssue(
                    "unexpected_change",
                    template_banner,
                    actual,
                    footer_part="template",
                )
            )

    return FooterCheckResult(
        candidate=str(candidate),
        expected=expected,
        actual=actual,
        ok=ok,
        issues=issues,
    )


def _replace_footer_banner_in_xml(xml_bytes: bytes, new_banner: str) -> bytes:
    root = ET.fromstring(xml_bytes)
    texts = [t for t in root.iter(W_T) if t.text is not None]
    if not texts:
        return xml_bytes

    combined = "".join(t.text for t in texts)
    if not combined.strip():
        return xml_bytes

    old_banner = _PAGE_RE.sub("", combined)
    if not old_banner.strip():
        return xml_bytes

    new_combined = combined.replace(old_banner, new_banner, 1)
    # If runs are split per character, fall back: put banner in first run, clear others before page field
    if new_combined == combined and old_banner not in combined:
        # Per-character runs: rebuild prefix runs
        idx = 0
        for t in texts:
            if idx >= len(new_banner):
                t.text = ""
                continue
            # stop before page marker in original
            if "第" in (t.text or "") and "頁" in combined[combined.find(t.text or "") :]:
                break
            t.text = new_banner[idx : idx + len(t.text or "")]
            idx += len(t.text or "")
        if idx < len(new_banner) and texts:
            texts[0].text = new_banner
            for t in texts[1:]:
                if "第" not in (t.text or "") or "頁" not in (t.text or ""):
                    t.text = ""
    else:
        pos = 0
        for t in texts:
            chunk = t.text or ""
            if not chunk:
                continue
            if pos + len(chunk) <= len(new_combined):
                t.text = new_combined[pos : pos + len(chunk)]
                pos += len(chunk)
            else:
                t.text = new_combined[pos:]
                pos = len(new_combined)

    return ET.tostring(root, encoding="UTF-8", xml_declaration=True)


def _inject_footer_banner_in_xml(xml_bytes: bytes, new_banner: str) -> bytes:
    """Prepend banner when footer only has page-number runs (no existing banner text)."""
    root = ET.fromstring(xml_bytes)
    texts = [t for t in root.iter(W_T) if t.text is not None]
    if not texts:
        return xml_bytes
    combined = "".join(t.text for t in texts)
    if _PAGE_RE.sub("", combined).strip():
        return xml_bytes
    texts[0].text = new_banner + (texts[0].text or "")
    return ET.tostring(root, encoding="UTF-8", xml_declaration=True)


def apply_footer_meta(docx_path: Path, footer_meta: FooterMeta | dict[str, Any]) -> None:
    """Rewrite static footer banner in all footer parts; preserve page-number fields."""
    docx_path = docx_path.expanduser().resolve()
    meta = footer_meta if isinstance(footer_meta, FooterMeta) else FooterMeta.from_dict(footer_meta)
    banner = meta.banner_text()
    if not banner:
        return

    with zipfile.ZipFile(docx_path, "r") as zin:
        names = zin.namelist()
        payloads = {n: zin.read(n) for n in names}

    changed = False
    banner_injected = False
    for name in _footer_xml_paths(docx_path):
        raw = payloads.get(name, b"")
        if not raw:
            continue
        joined = "".join(
            t.text for t in ET.fromstring(raw).iter(W_T) if t.text
        )
        if not joined.strip():
            continue
        if _PAGE_RE.sub("", joined).strip() == "":
            if banner_injected:
                continue
            payloads[name] = _inject_footer_banner_in_xml(raw, banner)
            banner_injected = True
        else:
            payloads[name] = _replace_footer_banner_in_xml(raw, banner)
        changed = True

    if not changed:
        return

    tmp = docx_path.with_suffix(".footer.tmp.docx")
    with zipfile.ZipFile(tmp, "w") as zout:
        for name in names:
            zout.writestr(name, payloads[name])
    tmp.replace(docx_path)


def format_footer_report(result: FooterCheckResult) -> str:
    lines = [
        f"Footer banner (candidate): {result.actual or '(empty)'}",
        f"Expected: {result.expected or '(from template)'}",
        f"Status: {'OK' if result.ok else 'ISSUES FOUND'}",
    ]
    for issue in result.issues:
        lines.append(f"\n[{issue.kind}] expected: {issue.expected!r}")
        lines.append(f"  actual:   {issue.actual!r}")
    return "\n".join(lines)
