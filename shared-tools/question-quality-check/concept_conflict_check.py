"""Detect the same syllabus topic tested again across 甲–戊 (concept repetition conflicts)."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable

from exam_spec import ExamItem, spec_items

# Fine-grained syllabus topics — coarse spec.concepts (e.g. 生成式AI) are too broad.
DEFAULT_TOPIC_PATTERNS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("hallucination", "幻覺", ("幻覺", "Hallucination", "hallucination")),
    ("cross_verification", "交叉查證", ("交叉查證", "核對 AI", "多模型比對", "可靠來源")),
    ("statistical_prediction", "統計規律／超級鸚鵡", ("統計規律", "超級鸚鵡", "預測下一個字")),
    ("fluency_vs_accuracy", "流暢性", ("流暢性",)),
    ("semantic_transform", "語意轉換", ("語意轉換", "改寫成正式", "改寫成不同語氣")),
    ("summarization", "摘要", ("摘要", "濃縮成精簡", "濃縮成三個")),
    ("creative_writing", "創意寫作", ("創意寫作", "撰寫開頭")),
    ("qa_game", "問答遊戲", ("問答遊戲", "互動練習題")),
    ("text_to_image", "文生圖", ("文生圖", "文字描述生成全新影像")),
    ("image_to_image", "圖生圖／影像編輯", ("圖生圖", "影像編輯", "二次創作")),
    ("ricco_constraint", "RICCO－限制", ("Constraint", "限制（", "限制 (", "限制）")),
    ("ricco_output", "RICCO－輸出格式", ("Output", "輸出格式")),
    ("ricco_role", "RICCO－角色", ("Role", "角色（", "角色）", "扮演")),
    ("ricco_context", "RICCO－背景", ("Context", "背景（", "背景）", "分析依據")),
    ("ricco_instruction", "RICCO－指令", ("Instruction", "指令（", "指令）")),
    ("tm_training", "TM 訓練流程", ("Train Model", "訓練模型", "訓練流程", "訓練樣本", "收集樣本")),
    ("tm_labels", "TM 分類標籤", ("分類標籤", "建立標籤", "建立兩個類別")),
    ("tm_share_link", "TM 分享連結", ("分享連結", "可分享的連結", "記下可分享")),
    ("tm_testing", "TM 充分測試", ("充分測試", "測試模型準確", "反覆測試")),
    ("tm_gesture", "TM 手勢控制", ("手勢控制", "向左移動", "向右移動", "手勢影像")),
    ("tm_overview", "Teachable Machine", ("Teachable Machine", "teachablemachine")),
    ("image_recognition", "圖像識別", ("圖像識別", "圖像辨識", "影像辨識", "影像分類")),
    ("data_extraction", "數據提取", ("數據提取",)),
    ("logic_excerpt", "邏輯節錄", ("邏輯節錄",)),
    ("flashcards", "閃卡", ("閃卡", "Flashcard", "flashcard")),
    ("privacy", "私隱", ("私隱", "敏感資料")),
    ("academic_integrity", "學術誠信", ("學術誠信", "引用來源", "完全不註明", "交功課")),
    ("app_inventor", "App Inventor／積木", ("App Inventor", "TMIC", "積木式", "拖拉積木")),
    ("vibe_coding", "Vibe Coding", ("Vibe Coding", "總監", "迭代（", "迭代）")),
)

MCQ_SECTIONS = frozenset({"mcq"})
REPEAT_RISK_SECTIONS = frozenset({"section_b", "section_c", "section_d", "section_e"})


@dataclass(frozen=True)
class ConceptConflict:
    topic_id: str
    topic_label: str
    item_a_id: str
    item_a_section: str
    item_b_id: str
    item_b_section: str
    snippet_a: str
    snippet_b: str


@dataclass
class ConceptConflictResult:
    ok: bool
    conflicts: list[ConceptConflict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "conflicts": [
                {
                    "topic_id": c.topic_id,
                    "topic_label": c.topic_label,
                    "item_a_id": c.item_a_id,
                    "item_a_section": c.item_a_section,
                    "item_b_id": c.item_b_id,
                    "item_b_section": c.item_b_section,
                    "snippet_a": c.snippet_a,
                    "snippet_b": c.snippet_b,
                }
                for c in self.conflicts
            ],
        }


def _compile_patterns(
    topic_patterns: Iterable[tuple[str, str, tuple[str, ...]]],
) -> list[tuple[str, str, tuple[re.Pattern[str], ...]]]:
    compiled: list[tuple[str, str, tuple[re.Pattern[str], ...]]] = []
    for topic_id, label, patterns in topic_patterns:
        compiled.append(
            (
                topic_id,
                label,
                tuple(re.compile(re.escape(p), re.IGNORECASE) for p in patterns),
            )
        )
    return compiled


def detect_topics(
    text: str,
    *,
    topic_patterns: Iterable[tuple[str, str, tuple[str, ...]]] = DEFAULT_TOPIC_PATTERNS,
) -> set[str]:
    found: set[str] = set()
    for topic_id, _, patterns in _compile_patterns(topic_patterns):
        if any(p.search(text) for p in patterns):
            found.add(topic_id)
    return found


def _item_search_text(item: ExamItem) -> str:
    parts = [item.text or ""]
    ans = item.meta.get("answer")
    if isinstance(ans, str):
        parts.append(ans)
    elif isinstance(ans, list):
        parts.extend(str(x) for x in ans)
    return "\n".join(parts)


def _skip_item(item: ExamItem) -> bool:
    text = (item.text or "").strip()
    if len(text) < 10:
        return True
    if re.match(r"^[甲乙丙丁戊]部[：:–\-]", text) and len(text) < 48:
        return True
    if text.startswith("乙部：") or text.startswith("乙部 –"):
        return True
    return False


def check_concept_conflicts(
    spec: dict,
    *,
    topic_patterns: Iterable[tuple[str, str, tuple[str, ...]]] = DEFAULT_TOPIC_PATTERNS,
) -> ConceptConflictResult:
    """
    Flag when 甲部 MCQ and 乙–戊 reuse the same fine-grained syllabus topic.

    Same topic twice within 甲部 only is allowed; cross-section repetition is not.
    """
    compiled = _compile_patterns(topic_patterns)
    labelled: list[tuple[ExamItem, set[str]]] = []
    for item in spec_items(spec):
        if _skip_item(item):
            continue
        topics = detect_topics(_item_search_text(item), topic_patterns=topic_patterns)
        if topics:
            labelled.append((item, topics))

    id_to_label = {tid: label for tid, label, _ in compiled}
    conflicts: list[ConceptConflict] = []
    seen: set[tuple[str, str, str]] = set()

    for i, (a, topics_a) in enumerate(labelled):
        if a.section not in MCQ_SECTIONS and a.section not in REPEAT_RISK_SECTIONS:
            continue
        for b, topics_b in labelled[i + 1 :]:
            if a.section == b.section:
                continue
            cross_mcq = (a.section in MCQ_SECTIONS) ^ (b.section in MCQ_SECTIONS)
            if not cross_mcq:
                continue
            if a.section not in MCQ_SECTIONS and b.section not in MCQ_SECTIONS:
                continue
            shared = topics_a & topics_b
            for topic_id in sorted(shared):
                key = (topic_id, a.id, b.id)
                if key in seen:
                    continue
                seen.add(key)
                conflicts.append(
                    ConceptConflict(
                        topic_id=topic_id,
                        topic_label=id_to_label.get(topic_id, topic_id),
                        item_a_id=a.id,
                        item_a_section=a.section,
                        item_b_id=b.id,
                        item_b_section=b.section,
                        snippet_a=a.text[:120],
                        snippet_b=b.text[:120],
                    )
                )

    return ConceptConflictResult(ok=not conflicts, conflicts=conflicts)


def format_concept_conflict_report(result: ConceptConflictResult) -> str:
    lines = [f"Concept conflicts: {'OK' if result.ok else 'ISSUES'}"]
    if result.ok:
        lines.append("No cross-section syllabus topic repetition (甲 vs 乙–戊).")
        return "\n".join(lines)

    lines.append(
        "Same fine-grained topic appears in 甲部 MCQ and later sections — "
        "students may copy answers:"
    )
    for c in result.conflicts:
        lines.append(
            f"  - [{c.topic_label}] {c.item_a_id} ({c.item_a_section}) "
            f"↔ {c.item_b_id} ({c.item_b_section})"
        )
        lines.append(f"      甲/前: {c.snippet_a}")
        lines.append(f"      後段: {c.snippet_b}")
    return "\n".join(lines)
