"""Shared Gemini vision helper for image analysis in marking testers."""

import hashlib
import importlib.util as _ilu
import json
import os
import threading
from pathlib import Path

_SHARED_TOOLS = Path(__file__).resolve().parent.parent  # shared-tools/
_spec = _ilu.spec_from_file_location("repo_env", _SHARED_TOOLS / "repo_env.py")
_mod = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
_mod.load_repo_env()

from google import genai
from google.genai import types

_GEMINI_MODEL = "gemini-2.5-flash"
_CACHE_PATH = Path("marksheets") / "vision_cache.json"  # CWD-relative (subject marking/ dir)
_cache: dict | None = None
_cache_lock = threading.Lock()


def _load_cache() -> dict:
    global _cache
    if _cache is not None:
        return _cache
    if _CACHE_PATH.exists():
        with open(_CACHE_PATH, encoding="utf-8") as f:
            _cache = json.load(f)
    else:
        _cache = {}
    return _cache


def _save_cache():
    _CACHE_PATH.parent.mkdir(exist_ok=True)
    with open(_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(_cache, f, ensure_ascii=False, indent=2)


def _image_hash(img_bytes: bytes) -> str:
    return hashlib.sha256(img_bytes).hexdigest()[:16]


def _cache_key(images, prompt, max_images) -> str:
    img_hashes = "-".join(_image_hash(b) for _, b in images[:max_images])
    prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:8]
    return f"{img_hashes}__{prompt_hash}"


def _client():
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")
    return genai.Client(api_key=api_key)


def _media_type(filename):
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    return {"png": "image/png", "gif": "image/gif", "webp": "image/webp"}.get(ext, "image/jpeg")


def _parse_json_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = "\n".join(
            line for line in text.splitlines()
            if not line.startswith("```")
        ).strip()
    result = json.loads(text)
    if not isinstance(result, dict):
        raise ValueError("vision response is not a JSON object")
    return result


def _fetch_gemini_vision_text(images, prompt, max_images=6, max_tokens=256) -> str:
    client = _client()
    parts = []
    for filename, img_bytes in images[:max_images]:
        parts.append(
            types.Part.from_bytes(data=img_bytes, mime_type=_media_type(filename))
        )
    parts.append(types.Part.from_text(text=prompt))

    response = client.models.generate_content(
        model=_GEMINI_MODEL,
        contents=parts,
        config=types.GenerateContentConfig(max_output_tokens=max_tokens),
    )
    return response.text.strip()


def call_gemini_vision(images, prompt, max_images=6, max_tokens=256):
    """Send images + prompt to Gemini and return the raw text response.

    Results are cached in marksheets/vision_cache.json keyed by image content hash.
    Run scripts from the subject's marking/ directory so the cache path resolves correctly.
    """
    with _cache_lock:
        cache = _load_cache()
        key = _cache_key(images, prompt, max_images)
        if key in cache:
            return cache[key]

    text = _fetch_gemini_vision_text(images, prompt, max_images, max_tokens)

    with _cache_lock:
        _cache[key] = text
        _save_cache()

    return text


def call_gemini_vision_json(images, prompt, max_images=6, max_tokens=256):
    """Like call_gemini_vision but parses the response as JSON and returns a dict.

    Caches parsed dicts; invalid/truncated responses are retried with doubled token budget.
    """
    text_key = _cache_key(images, prompt, max_images)
    json_key = f"{text_key}__json"

    with _cache_lock:
        cache = _load_cache()
        cached = cache.get(json_key)
        if isinstance(cached, dict):
            return cached

    tokens = max(max_tokens, 1024)
    for attempt in range(2):
        with _cache_lock:
            cache = _load_cache()
            if attempt == 0 and text_key in cache:
                text = cache[text_key]
            else:
                text = None

        if text is None:
            text = _fetch_gemini_vision_text(images, prompt, max_images, tokens)

        try:
            result = _parse_json_response(text)
            with _cache_lock:
                cache = _load_cache()
                cache[text_key] = text
                cache[json_key] = result
                _save_cache()
            return result
        except Exception:
            with _cache_lock:
                cache = _load_cache()
                cache.pop(text_key, None)
                cache.pop(json_key, None)
                _save_cache()
            tokens = max(tokens * 2, 2048)

    return {}
