"""Load API keys and config from the repo-root `.env` file."""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
_ENV_LOADED = False


def load_repo_env() -> Path | None:
    """Load ``REPO_ROOT/.env`` into ``os.environ`` (once per process).

    Existing environment variables are not overwritten.
    Returns the path loaded, or None if missing / python-dotenv not installed.
    """
    global _ENV_LOADED
    if _ENV_LOADED:
        return REPO_ROOT / ".env" if (REPO_ROOT / ".env").is_file() else None

    env_path = REPO_ROOT / ".env"
    _ENV_LOADED = True
    if not env_path.is_file():
        return None

    try:
        from dotenv import load_dotenv
    except ImportError:
        return None

    load_dotenv(env_path, override=False)
    return env_path
