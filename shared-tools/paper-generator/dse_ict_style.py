"""HKDSE ICT style guide — terminology and phrasing for school paper generation."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

STYLE_GUIDE_PATH = Path(__file__).with_name("dse_ict_style_guide.json")

# Standard combo MCQ option sets (DSE 2019–2023)
COMBO_OPTS_1_ONLY = ("只有 (1)", "只有 (2)", "只有 (3)", "只有 (1) 和 (2)")
COMBO_OPTS_3_ONLY = ("只有 (1)", "只有 (2)", "只有 (3)", "只有 (2) 和 (3)")
COMBO_OPTS_1_AND_2 = ("只有 (1)", "只有 (2)", "只有 (3)", "只有 (1) 和 (2)")
COMBO_OPTS_1_AND_3 = ("只有 (1)", "只有 (2)", "只有 (1) 和 (3)", "只有 (2) 和 (3)")
COMBO_OPTS_ALL = ("只有 (1)", "只有 (1) 和 (2)", "(1)、(2) 和 (3)", "只有 (3)")
COMBO_OPTS_1_2_OK = ("只有 (1)", "只有 (1) 和 (2)", "只有 (3)", "(1) 和 (2) 均正確")


def load_style_guide() -> dict[str, Any]:
    return json.loads(STYLE_GUIDE_PATH.read_text(encoding="utf-8"))


def style_meta() -> dict[str, Any]:
    """Snippet for exam spec meta."""
    g = load_style_guide()
    return {
        "style_guide": str(STYLE_GUIDE_PATH.relative_to(STYLE_GUIDE_PATH.parents[2])),
        "dse_sources": g["meta"]["sources"],
        "mcq_curriculum_units": ["Core-A", "Core-B", "Core-D"],
        "phrasing": "HKDSE ICT 2019–2023 (OCR-curated)",
    }
