"""Use an OpenAI-compatible LLM to refine OCR/noisy question extractions."""
from __future__ import annotations

import base64
import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import fitz

RefineMode = Literal["text", "vision"]
LlmProvider = Literal["gemini", "openai"]

DEFAULT_MODEL_TEXT = "gpt-4o-mini"
DEFAULT_MODEL_VISION = "gpt-4o"
DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"
DEFAULT_BASE_URL = "https://api.openai.com/v1"
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"


@dataclass
class LlmConfig:
    api_key: str
    provider: LlmProvider = "openai"
    base_url: str = DEFAULT_BASE_URL
    model: str | None = None
    mode: RefineMode = "text"

    @classmethod
    def from_env(cls, *, mode: RefineMode = "text", provider: str | None = None) -> "LlmConfig":
        chosen = (provider or os.environ.get("DSE_ICT_LLM_PROVIDER", "")).strip().lower()
        gemini_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY") or ""
        gemini_key = gemini_key.strip()
        openai_key = os.environ.get("OPENAI_API_KEY", "").strip()

        if chosen == "gemini" or (not chosen and gemini_key):
            if not gemini_key:
                raise RuntimeError(
                    "Gemini provider selected but GOOGLE_API_KEY / GEMINI_API_KEY is not set.\n"
                    "Get a free key at https://aistudio.google.com/apikey (no credit card for free tier)."
                )
            model = os.environ.get("DSE_ICT_LLM_MODEL") or DEFAULT_GEMINI_MODEL
            return cls(api_key=gemini_key, provider="gemini", model=model, mode=mode)

        if not openai_key:
            raise RuntimeError(
                "No LLM API key found.\n"
                "  Hong Kong / free: set GOOGLE_API_KEY from https://aistudio.google.com/apikey\n"
                "    and run with --provider gemini (or set DSE_ICT_LLM_PROVIDER=gemini)\n"
                "  OpenAI-compatible: set OPENAI_API_KEY (+ optional OPENAI_BASE_URL)"
            )
        base_url = os.environ.get("OPENAI_BASE_URL", DEFAULT_BASE_URL).strip()
        model = os.environ.get("DSE_ICT_LLM_MODEL")
        if not model:
            model = DEFAULT_MODEL_VISION if mode == "vision" else DEFAULT_MODEL_TEXT
        return cls(api_key=openai_key, provider="openai", base_url=base_url, model=model, mode=mode)


def _http_post_json(url: str, payload: dict[str, Any], *, headers: dict[str, str]) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={**headers, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"LLM API error {e.code}: {detail}") from e


def _openai_chat_completion(*, cfg: LlmConfig, messages: list[dict[str, Any]], temperature: float = 0.1) -> str:
    url = f"{cfg.base_url.rstrip('/')}/chat/completions"
    data = _http_post_json(
        url,
        {
            "model": cfg.model,
            "messages": messages,
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        },
        headers={"Authorization": f"Bearer {cfg.api_key}"},
    )
    return data["choices"][0]["message"]["content"]


def _messages_to_gemini_parts(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    parts: list[dict[str, Any]] = []
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content")
        if role == "system" and isinstance(content, str):
            parts.append({"text": f"[System]\n{content}\n"})
            continue
        if isinstance(content, str):
            parts.append({"text": content})
            continue
        if isinstance(content, list):
            for block in content:
                if block.get("type") == "text":
                    parts.append({"text": block["text"]})
                elif block.get("type") == "image_url":
                    url = block["image_url"]["url"]
                    if url.startswith("data:"):
                        header, b64 = url.split(",", 1)
                        mime = header.split(";")[0].split(":", 1)[1]
                        parts.append({"inline_data": {"mime_type": mime, "data": b64}})
    return parts


def _gemini_generate_content(*, cfg: LlmConfig, messages: list[dict[str, Any]], temperature: float = 0.1) -> str:
    model = cfg.model or DEFAULT_GEMINI_MODEL
    url = f"{GEMINI_API_BASE}/models/{model}:generateContent?key={cfg.api_key}"
    data = _http_post_json(
        url,
        {
            "contents": [{"role": "user", "parts": _messages_to_gemini_parts(messages)}],
            "generationConfig": {
                "temperature": temperature,
                "responseMimeType": "application/json",
            },
        },
        headers={},
    )
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Unexpected Gemini response: {json.dumps(data)[:500]}") from e


def _chat_completion(*, cfg: LlmConfig, messages: list[dict[str, Any]], temperature: float = 0.1) -> str:
    if cfg.provider == "gemini":
        return _gemini_generate_content(cfg=cfg, messages=messages, temperature=temperature)
    return _openai_chat_completion(cfg=cfg, messages=messages, temperature=temperature)


def _extract_json_object(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("{"):
        return json.loads(text)
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        raise ValueError("LLM response did not contain JSON object")
    return json.loads(m.group(0))


def _page_png_b64(pdf_path: Path, page_no: int, *, scale: float = 2.0) -> str:
    doc = fitz.open(pdf_path)
    pix = doc[page_no].get_pixmap(matrix=fitz.Matrix(scale, scale))
    return base64.standard_b64encode(pix.tobytes("png")).decode("ascii")


def _chunk_text(text: str, *, max_chars: int = 6000) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    chunks: list[str] = []
    buf: list[str] = []
    size = 0
    for para in re.split(r"\n{2,}", text):
        if size + len(para) + 2 > max_chars and buf:
            chunks.append("\n\n".join(buf))
            buf = [para]
            size = len(para)
        else:
            buf.append(para)
            size += len(para) + 2
    if buf:
        chunks.append("\n\n".join(buf))
    return chunks


def _refine_prompt(
    *,
    paper_label: str,
    slug: str,
    ocr_text: str,
    draft_questions: list[dict[str, Any]] | None,
    mcq_answers: dict[int, str] | None,
    page_hint: str | None = None,
) -> str:
    draft_blob = json.dumps(draft_questions or [], ensure_ascii=False, indent=2)[:4000]
    answers_blob = json.dumps(mcq_answers or {}, ensure_ascii=False)
    page_line = f"Page scope: {page_hint}\n" if page_hint else ""
    return f"""You clean up HKDSE ICT exam questions extracted from scanned papers.

Paper: {paper_label} ({slug})
{page_line}
Rules:
- Use Traditional Chinese (香港用字) for Chinese text.
- Do NOT invent missing options or marks; if unsure, set needs_review=true and explain in notes.
- Fix obvious OCR errors only when context makes the intended word clear (e.g. 尺有→只有, sOL→SQL).
- For MCQ: output stem + options A–D when present. For written questions: output full prompt text.
- Ignore watermark/footer noise (dse.life, Provided by, 請在此貼上電腦條碼, page headers).
- Merge split lines that belong to one question. Do not duplicate the same question number.
- If a table/image is garbled, keep readable parts and note the gap in notes.

Marking scheme MCQ keys (if any, for cross-check only): {answers_blob}

Draft parser output (noisy, use as hints not ground truth):
{draft_blob}

OCR text:
{ocr_text}

Return JSON:
{{
  "questions": [
    {{
      "number": 1,
      "type": "mcq|short_answer|structured|long_answer|matching|true_false|fill_in",
      "section": "甲部|乙部|丙部|…",
      "stem": "question stem",
      "options": {{"A": "…", "B": "…", "C": "…", "D": "…"}},
      "text": "full plain text for search/compare",
      "marks": 1,
      "confidence": 0.0,
      "needs_review": false,
      "notes": ""
    }}
  ],
  "chunk_notes": "optional overall comment"
}}"""


def refine_from_text(
    *,
    cfg: LlmConfig,
    paper_label: str,
    slug: str,
    ocr_text: str,
    draft_questions: list[dict[str, Any]] | None = None,
    mcq_answers: dict[int, str] | None = None,
) -> list[dict[str, Any]]:
    merged: dict[int, dict[str, Any]] = {}
    chunks = _chunk_text(ocr_text)
    for i, chunk in enumerate(chunks, start=1):
        hint = f"chunk {i}/{len(chunks)}" if len(chunks) > 1 else None
        prompt = _refine_prompt(
            paper_label=paper_label,
            slug=slug,
            ocr_text=chunk,
            draft_questions=draft_questions,
            mcq_answers=mcq_answers,
            page_hint=hint,
        )
        raw = _chat_completion(
            cfg=cfg,
            messages=[
                {"role": "system", "content": "You structure HKDSE ICT exam content. Reply with JSON only."},
                {"role": "user", "content": prompt},
            ],
        )
        data = _extract_json_object(raw)
        for q in data.get("questions") or []:
            num = int(q["number"])
            prev = merged.get(num)
            if prev is None or float(q.get("confidence") or 0) >= float(prev.get("confidence") or 0):
                merged[num] = q
    return [merged[k] for k in sorted(merged)]


def refine_from_vision_pages(
    *,
    cfg: LlmConfig,
    paper_label: str,
    slug: str,
    pdf_path: Path,
    page_numbers: list[int],
    ocr_text_by_page: dict[int, str] | None = None,
    mcq_answers: dict[int, str] | None = None,
) -> list[dict[str, Any]]:
    merged: dict[int, dict[str, Any]] = {}
    for page_no in page_numbers:
        ocr_hint = (ocr_text_by_page or {}).get(page_no, "")
        prompt = _refine_prompt(
            paper_label=paper_label,
            slug=slug,
            ocr_text=ocr_hint or "(no OCR for this page — read from image)",
            draft_questions=None,
            mcq_answers=mcq_answers,
            page_hint=f"PDF page {page_no + 1} (1-based)",
        )
        img_b64 = _page_png_b64(pdf_path, page_no)
        raw = _chat_completion(
            cfg=cfg,
            messages=[
                {"role": "system", "content": "You structure HKDSE ICT exam content from exam scans. Reply with JSON only."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
                    ],
                },
            ],
        )
        data = _extract_json_object(raw)
        for q in data.get("questions") or []:
            num = int(q["number"])
            prev = merged.get(num)
            if prev is None or float(q.get("confidence") or 0) >= float(prev.get("confidence") or 0):
                merged[num] = q
    return [merged[k] for k in sorted(merged)]


def default_content_pages(slug: str, pdf_path: Path) -> list[int]:
    """0-based page indices to send to vision model."""
    doc = fitz.open(pdf_path)
    skip_first, skip_last, max_pages = _skip_pages(slug)
    start = min(skip_first, doc.page_count)
    end = doc.page_count - skip_last if skip_last else doc.page_count
    if max_pages is not None:
        end = min(end, start + max_pages)
    return list(range(start, end))


def _skip_pages(slug: str) -> tuple[int, int, int | None]:
    if slug == "Paper1_MultipleChoice":
        return 2, 0, 14
    if slug.startswith("Paper2"):
        return 2, 0, 10
    if slug == "MarkingScheme":
        return 0, 0, None
    return 1, 0, None


def validate_refined_questions(
    questions: list[dict[str, Any]],
    *,
    slug: str,
    mcq_answers: dict[int, str] | None,
) -> dict[str, Any]:
    flags: list[str] = []
    numbers = [int(q["number"]) for q in questions if q.get("number") is not None]
    if slug == "Paper1_MultipleChoice" and numbers and max(numbers) < 35:
        flags.append(f"expected ~40 MCQs, got {len(numbers)} (max #{max(numbers)})")
    missing_opts = [
        int(q["number"])
        for q in questions
        if q.get("type") == "mcq" and len([k for k in (q.get("options") or {}) if (q["options"] or {}).get(k)]) < 3
    ]
    if missing_opts:
        flags.append(f"MCQs with incomplete options: {missing_opts[:10]}")
    review = [int(q["number"]) for q in questions if q.get("needs_review")]
    low_conf = [int(q["number"]) for q in questions if float(q.get("confidence") or 1) < 0.6]
    return {
        "question_count": len(questions),
        "needs_review_numbers": review,
        "low_confidence_numbers": low_conf,
        "warnings": flags,
        "mcq_answer_key_size": len(mcq_answers or {}),
    }


def build_refined_spec(
    *,
    year_label: str,
    slug: str,
    paper_label: str,
    source_pdf: Path,
    questions: list[dict[str, Any]],
    validation: dict[str, Any],
    mode: RefineMode,
    model: str,
    provider: LlmProvider = "openai",
) -> dict[str, Any]:
    paper_id = f"{year_label}-{slug}"
    items: list[dict[str, Any]] = []
    for q in questions:
        qtype = q.get("type") or "short_answer"
        num = q.get("number")
        item_id = f"{paper_id}-Q{int(num):02d}" if qtype == "mcq" else f"{paper_id}-LLM{int(num):02d}"
        text = q.get("text") or q.get("stem") or ""
        row: dict[str, Any] = {
            "id": item_id,
            "section": "mcq" if qtype == "mcq" else qtype,
            "text": text,
            "marks": q.get("marks"),
            "number": num,
            "confidence": q.get("confidence"),
            "needs_review": bool(q.get("needs_review")),
            "notes": q.get("notes") or "",
        }
        if qtype == "mcq":
            row["stem"] = q.get("stem") or text
            row["options"] = q.get("options") or {}
        else:
            row["section_label"] = q.get("section")
        items.append(row)

    return {
        "version": 1,
        "meta": {
            "source": "dse-ict-question-bank-llm",
            "refined_at": datetime.now(timezone.utc).isoformat(),
            "refine_mode": mode,
            "llm_provider": provider,
            "llm_model": model,
            "year_label": year_label,
            "paper_slug": slug,
            "paper_label": paper_label,
            "source_pdf": str(source_pdf).replace("\\", "/"),
            "question_count": len(items),
            "validation": validation,
        },
        "items": items,
        "paper": {"id": paper_id, "questions": questions},
    }
