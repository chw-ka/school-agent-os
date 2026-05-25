"""LLM client for solve review / repair (Gemini, DeepSeek, or OpenAI-compatible)."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_SHARED = Path(__file__).resolve().parents[1]
_PDF = _SHARED / "pdf-engine"
if str(_PDF) not in sys.path:
    sys.path.insert(0, str(_PDF))

from dse_ict_llm_refine import (  # noqa: E402
    LlmConfig,
    _chat_completion,
    _extract_json_object,
)
from repo_env import REPO_ROOT, load_repo_env  # noqa: E402

PROVIDER_CHOICES = ("gemini", "deepseek", "openai")


def check_api_key(*, provider: str | None = None) -> dict[str, str]:
    """Return status for setup instructions (--check-key)."""
    load_repo_env()
    import os

    gemini = (os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY") or "").strip()
    deepseek = (os.environ.get("DEEPSEEK_API_KEY") or "").strip()
    openai = (os.environ.get("OPENAI_API_KEY") or "").strip()
    env_provider = (os.environ.get("DSE_ICT_LLM_PROVIDER") or "").strip().lower()
    env_file = REPO_ROOT / ".env"

    if provider:
        recommended = provider
    elif env_provider in PROVIDER_CHOICES:
        recommended = env_provider
    elif deepseek:
        recommended = "deepseek"
    elif gemini:
        recommended = "gemini"
    elif openai:
        recommended = "openai"
    else:
        recommended = "deepseek"

    return {
        "env_file": str(env_file),
        "env_exists": str(env_file.is_file()),
        "GOOGLE_API_KEY_set": str(bool(gemini)),
        "DEEPSEEK_API_KEY_set": str(bool(deepseek)),
        "OPENAI_API_KEY_set": str(bool(openai)),
        "DSE_ICT_LLM_PROVIDER": env_provider or "(not set)",
        "recommended": recommended,
        "provider_hint": provider or "",
    }


def llm_config_from_env(*, provider: str | None = None, model: str | None = None) -> LlmConfig:
    cfg = LlmConfig.from_env(mode="text", provider=provider)
    if model:
        cfg.model = model
    return cfg


def llm_json_completion(
    *,
    cfg: LlmConfig,
    system: str,
    user: str,
    temperature: float = 0.15,
) -> dict[str, Any]:
    raw = _chat_completion(
        cfg=cfg,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
    )
    return _extract_json_object(raw)


def llm_json_with_image(
    *,
    cfg: LlmConfig,
    system: str,
    user_text: str,
    image_b64: str,
    mime: str = "image/png",
    temperature: float = 0.15,
) -> dict[str, Any]:
    if cfg.provider == "deepseek":
        raise RuntimeError("DeepSeek solve_review does not support vision; use text + item.tables only.")
    cfg_v = LlmConfig(
        api_key=cfg.api_key,
        provider=cfg.provider,
        base_url=cfg.base_url,
        model=cfg.model,
        mode="vision",
    )
    raw = _chat_completion(
        cfg=cfg_v,
        messages=[
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_text},
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{image_b64}"}},
                ],
            },
        ],
        temperature=temperature,
    )
    return _extract_json_object(raw)
