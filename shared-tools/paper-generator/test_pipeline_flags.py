"""Tests for Phase 7 pipeline flags."""
from f5_ict_pipeline_flags import PICK_TIME_BANK_SIM_GATE


def test_pick_gate_default_off():
    assert PICK_TIME_BANK_SIM_GATE is False


if __name__ == "__main__":
    test_pick_gate_default_off()
    print("ok")
