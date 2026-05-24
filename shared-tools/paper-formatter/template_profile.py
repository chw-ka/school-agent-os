"""Default F5 ICT template profile location and loader."""

from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

_FMT = Path(__file__).resolve().parent
_REPO = _FMT.parents[1]

DEFAULT_F5_ICT_PROFILE = (
    _REPO / "Subjects/S5-ICT/templates/24_25_S5_ICT_Exam02.profile.json"
)


def _ensure_fmt_path() -> None:
    if str(_FMT) not in sys.path:
        sys.path.insert(0, str(_FMT))


@lru_cache(maxsize=4)
def load_f5_ict_profile(path: str | None = None) -> dict:
    _ensure_fmt_path()
    from paper_format.extractor.f5_ict_extract import load_profile

    p = Path(path) if path else DEFAULT_F5_ICT_PROFILE
    if not p.exists():
        raise FileNotFoundError(
            f"Template profile not found: {p}\n"
            "Run: python shared-tools/paper-formatter/paper_extract.py"
        )
    return load_profile(p)
