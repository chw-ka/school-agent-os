"""F5 ICT exam pipeline flags (Phase 7).

Pick-time bank similarity gates caused long silent retries; similarity is enforced
at question_review instead. Set PICK_TIME_BANK_SIM_GATE=1 to restore legacy pick behavior.
"""
from __future__ import annotations

import os

# Default off: bank pick may exceed 60% until question_review / partial regen.
PICK_TIME_BANK_SIM_GATE: bool = os.environ.get("PICK_TIME_BANK_SIM_GATE", "").strip() in (
    "1",
    "true",
    "yes",
)
