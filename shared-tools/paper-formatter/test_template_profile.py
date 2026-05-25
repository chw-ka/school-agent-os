#!/usr/bin/env python3
"""Smoke test: template profile extract + role resolution."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

_FMT = Path(__file__).resolve().parent
if str(_FMT) not in sys.path:
    sys.path.insert(0, str(_FMT))

from paper_format.f5_ict_roles import mcq_line_kind, mcq_role_for_kind, written_line_kind
from template_profile import DEFAULT_F5_ICT_PROFILE, load_f5_ict_profile


class TestTemplateProfile(unittest.TestCase):
    def test_profile_exists(self) -> None:
        self.assertTrue(DEFAULT_F5_ICT_PROFILE.is_file())

    def test_load_roles(self) -> None:
        prof = load_f5_ict_profile()
        roles = prof.get("roles") or {}
        self.assertIn("mcq.stem", roles)
        self.assertIn("mcq.option", roles)
        self.assertIn("written.answer_blank", roles)
        ts = roles["mcq.stem"].get("tab_stops") or []
        self.assertGreater(len(ts), 0)

    def test_mcq_line_kinds(self) -> None:
        self.assertEqual(mcq_line_kind("\t1.\t題目"), "stem")
        self.assertEqual(mcq_line_kind("\tA.\t選項"), "option")
        self.assertEqual(mcq_line_kind("\t\t(1)\t陳述"), "combo_sub")
        self.assertEqual(mcq_role_for_kind("option"), "mcq.option")

    def test_answer_blank_kind(self) -> None:
        from paper_format.f5_ict_roles import written_line_kind

        self.assertEqual(written_line_kind(ANSWER_BLANK), "answer_blank")
        self.assertEqual(written_line_kind(ANSWER_BLANK_LONG), "answer_blank_long")

    def test_written_answer_blank(self) -> None:
        from written_layout import ANSWER_BLANK

        self.assertEqual(written_line_kind(ANSWER_BLANK), "answer_blank")


if __name__ == "__main__":
    unittest.main()
