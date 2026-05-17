#!/usr/bin/env python3
"""Deprecated: moved to shared-tools/paper-generator/f5_ict_blueprint_db_web.py"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

_TARGET = Path(__file__).resolve().parents[1] / "paper-generator" / "f5_ict_blueprint_db_web.py"

if __name__ == "__main__":
    sys.argv[0] = str(_TARGET)
    runpy.run_path(str(_TARGET), run_name="__main__")
