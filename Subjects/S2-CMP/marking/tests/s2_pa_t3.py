"""
中二級下學期實習試 - 第三部分 (20 marks)
Students submit Task3.docx with Teachable Machine screenshots and share link.
Some students submit image files directly instead of a DOCX.
"""

RUBRIC = [
    {"key": "mark1", "name": "四類別樣本 (a)", "max_marks": 5},
    {"key": "mark2", "name": "模型訓練完成 (b)", "max_marks": 5},
    {"key": "mark3", "name": "分享連結 (c-d)", "max_marks": 5},
    {"key": "mark4", "name": "截圖證據 (d)", "max_marks": 5},
]

import glob
import os
import re
from pathlib import Path

import aia_util as aia_utils
from docx_util import extract_docx_images, normalize_text, read_docx_text
from vision_util import call_gemini_vision_json

EXPECTED_CLASSES = ["水瓶", "玩具車", "水槍", "鍵盤"]

_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

TEXT_CLASS_PATTERNS = [
    (r"水瓶|bottle|waterbottle", "水瓶"),
    (r"玩具車|toy\s*car|toycar", "玩具車"),
    (r"水槍|water\s*gun|watergun", "水槍"),
    (r"鍵盤|keyboard", "鍵盤"),
]

_CATEGORY_ALIASES = {
    "水瓶": "水瓶",
    "bottle": "水瓶",
    "water bottle": "水瓶",
    "waterbottle": "水瓶",
    "玩具車": "玩具車",
    "toy car": "玩具車",
    "toycar": "玩具車",
    "car": "玩具車",
    "水槍": "水槍",
    "water gun": "水槍",
    "watergun": "水槍",
    "鍵盤": "鍵盤",
    "keyboard": "鍵盤",
}

_VISION_PROMPT = (
    "These screenshots are from a student's Teachable Machine "
    "(teachablemachine.withgoogle.com) image classifier. "
    "The student should have 4 classes. Each class is one of:\n"
    "  水瓶 (water bottle / waterbottle)\n"
    "  玩具車 (toy car / toycar / car)\n"
    "  水槍 (water gun / watergun)\n"
    "  鍵盤 (keyboard)\n\n"
    "Look at the class labels visible in the screenshots. "
    "For each class you recognise (whether in Chinese or English), "
    "include its CHINESE name in the categories array.\n\n"
    "Reply ONLY with valid JSON — no markdown, no extra text:\n"
    '{"categories": ["水瓶", "玩具車", "水槍", "鍵盤"], '
    '"training_complete": true_or_false}\n\n'
    "training_complete is true if you see a 'Model Trained' badge, "
    "accuracy/loss graph, or any clear indication training finished."
)


def _collect_sibling_images(filepath):
    """
    When a student submits images directly, gather ALL image files they submitted
    (Teams stores multiple uploads as _0.jpg, _1.jpg, etc. with the same base name).
    Returns list of (filename, bytes).
    """
    path = Path(filepath)
    # Strip the trailing _N version index to get the shared base
    base = re.sub(r"_\d+$", "", path.stem)
    images = []
    for candidate in sorted(path.parent.glob(f"{glob.escape(base)}_*")):
        if candidate.suffix.lower() in _IMAGE_EXTS:
            images.append((candidate.name, candidate.read_bytes()))
    # If glob found nothing (edge case), fall back to just the one file
    if not images and path.suffix.lower() in _IMAGE_EXTS:
        images = [(path.name, path.read_bytes())]
    return images


def _normalize_categories(raw_categories):
    found = []
    for item in raw_categories:
        key = str(item).strip().lower().replace("_", " ").replace("-", " ")
        for alias, zh in _CATEGORY_ALIASES.items():
            alias_key = alias.lower().replace("_", " ").replace("-", " ")
            if key == alias_key or key == zh:
                if zh not in found:
                    found.append(zh)
                break
    return found


def _analyze_screenshots(images):
    """Returns (categories_found: list[str], training_complete: bool)."""
    if not images:
        return [], False
    result = call_gemini_vision_json(images, _VISION_PROMPT, max_images=6, max_tokens=1024)
    categories = _normalize_categories(result.get("categories", []))
    return categories, bool(result.get("training_complete", False))


def _score_marks(images, image_count, text_classes, train_text_hits):
    """
    Core vision + count scoring. Returns (comments_body, mark1, mark2, mark4).
    mark3 (share link) is handled by callers since it depends on text availability.
    """
    comments = ""
    mark1 = mark2 = mark4 = 0

    vision_categories, vision_trained = _analyze_screenshots(images)
    classes_found = list(
        dict.fromkeys(vision_categories + [c for c in text_classes if c not in vision_categories])
    )

    n = len(classes_found)
    if n >= 3:
        mark1 = 5
        if n >= 4:
            comments += f"[O] 四個類別齊全: {', '.join(classes_found)}\n"
        else:
            comments += f"[O] 見 {n} 個類別（螢幕截圖上限，視作完成）: {', '.join(classes_found)}\n"
    elif n == 2:
        mark1 = 2
        comments += f"[-] 僅見 {n} 個類別: {', '.join(classes_found)}\n"
    elif n == 1:
        mark1 = 1
        comments += f"[-] 僅見 {n} 個類別: {', '.join(classes_found)}\n"
    else:
        comments += "[X] 未能確認四類別命名 (水瓶/玩具車/水槍/鍵盤)\n"
    comments += aia_utils.get_comments("四類別樣本 (a)", mark1, 5)

    if vision_trained:
        mark2 = 5
        comments += "[O] 截圖顯示模型訓練完成\n"
    elif train_text_hits >= 2:
        mark2 = 5
        comments += "[O] 文字顯示模型訓練完成\n"
    elif train_text_hits >= 1:
        mark2 = 3
        comments += "[-] 部分訓練完成證據\n"
    else:
        comments += "[X] 未能確認模型訓練完成\n"
    comments += aia_utils.get_comments("模型訓練完成 (b)", mark2, 5)

    if image_count >= 2:
        mark4 = 5
        comments += f"[O] 含 {image_count} 張截圖\n"
    elif image_count == 1:
        mark4 = 3
        comments += "[-] 只有 1 張截圖（應有 2 張）\n"
    else:
        comments += "[X] 缺少截圖\n"
    comments += aia_utils.get_comments("截圖證據 (d)", mark4, 5)

    return comments, mark1, mark2, mark4


def evaluate_docx(filepath):
    text = normalize_text(read_docx_text(filepath))
    images = extract_docx_images(filepath)
    image_count = len(images)

    text_classes = [lbl for pat, lbl in TEXT_CLASS_PATTERNS if re.search(pat, text, re.I)]
    train_text_hits = sum(
        1
        for p in [
            r"model trained|模型訓練|訓練完成|train model",
            r"preview|預覽",
            r"teachable\s*machine|image project",
        ]
        if re.search(p, text, re.I)
    )

    body, mark1, mark2, mark4 = _score_marks(images, image_count, text_classes, train_text_hits)

    # mark3: share link from text
    mark3 = 0
    if re.search(r"teachablemachine\.withgoogle\.com", text, re.I):
        mark3 = 5
        body += "[O] 含 Teachable Machine 分享連結\n"
    elif re.search(r"https?://\S+", text, re.I) and re.search(
        r"share\s*link|分享連結|可分享", text, re.I
    ):
        mark3 = 4
        body += "[O] 含分享連結文字\n"
    elif re.search(r"https?://\S+", text, re.I):
        mark3 = 2
        body += "[-] 有 URL 但可能非 TM 連結\n"
    else:
        body += "[X] 缺少模型分享連結\n"
    body += aia_utils.get_comments("分享連結 (c-d)", mark3, 5)

    comments = "[O]: Correct\n[-]: Minor error\n[X]: Major error\n\n" + body
    return mark1 + mark2 + mark3 + mark4, comments, mark1, mark2, mark3, mark4


def evaluate_images(filepath):
    """Score a submission made of direct image files (JPG/PNG/etc.) instead of DOCX."""
    images = _collect_sibling_images(filepath)
    image_count = len(images)
    body, mark1, mark2, mark4 = _score_marks(images, image_count, [], 0)

    # mark3 is 0 — no text to extract a share link from
    mark3 = 0
    body += "[X] 缺少模型分享連結（以圖片提交，無法擷取連結）\n"
    body += aia_utils.get_comments("分享連結 (c-d)", mark3, 5)

    comments = (
        "[O]: Correct\n[-]: Minor error\n[X]: Major error\n\n"
        "[-] 以圖片方式提交（非 DOCX），分享連結不計分\n"
        + body
    )
    return mark1 + mark2 + mark3 + mark4, comments, mark1, mark2, mark3, mark4


def test(submissions):
    for idx, row in submissions.iterrows():
        submissions.loc[idx, "marks"] = 0
        submissions.loc[idx, "comments"] = ""
        for key in ("mark1", "mark2", "mark3", "mark4"):
            submissions.loc[idx, key] = 0

        filepath = str(row.get("filepath") or "")
        if not filepath or not os.path.exists(filepath):
            submissions.loc[idx, "comments"] = (
                "[O]: Correct\n[-]: Minor error\n[X]: Major error\n\n"
                "[X] Task3.docx not submitted\n"
            )
            continue

        ext = Path(filepath).suffix.lower()

        if ext == ".docx":
            try:
                total, comments, m1, m2, m3, m4 = evaluate_docx(filepath)
            except Exception as exc:
                submissions.loc[idx, "comments"] = (
                    "[O]: Correct\n[-]: Minor error\n[X]: Major error\n\n"
                    f"[X] Cannot read docx: {exc}\n"
                )
                continue

        elif ext in _IMAGE_EXTS:
            try:
                total, comments, m1, m2, m3, m4 = evaluate_images(filepath)
            except Exception as exc:
                submissions.loc[idx, "comments"] = (
                    "[O]: Correct\n[-]: Minor error\n[X]: Major error\n\n"
                    f"[X] Cannot process image: {exc}\n"
                )
                continue

        else:
            # PDF, ZIP, or other non-markable format
            submissions.loc[idx, "marks"] = 1
            submissions.loc[idx, "comments"] = (
                "[O]: Correct\n[-]: Minor error\n[X]: Major error\n\n"
                "[X] Expected Task3.docx submission\n"
                "[-] 有提交檔案但格式不正確（只可得 1 分）\n"
            )
            continue

        submissions.loc[idx, "marks"] = total
        submissions.loc[idx, "comments"] = comments
        submissions.loc[idx, "mark1"] = m1
        submissions.loc[idx, "mark2"] = m2
        submissions.loc[idx, "mark3"] = m3
        submissions.loc[idx, "mark4"] = m4
    return submissions
