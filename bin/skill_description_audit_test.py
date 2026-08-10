#!/usr/bin/env python3
"""Unit tests for skill-description-audit.py."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("skill-description-audit.py")
SPEC = importlib.util.spec_from_file_location("skill_description_audit", MODULE_PATH)
assert SPEC and SPEC.loader
AUDIT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDIT
SPEC.loader.exec_module(AUDIT)


class SkillDescriptionAuditTest(unittest.TestCase):
    def audit(self, description_yaml: str):
        with tempfile.TemporaryDirectory() as temporary_directory:
            skill_directory = Path(temporary_directory) / "example"
            skill_directory.mkdir()
            path = skill_directory / "SKILL.md"
            path.write_text(
                "---\n"
                "name: example\n"
                f"{description_yaml}\n"
                "---\n"
                "# Example\n",
                encoding="utf-8",
            )
            return AUDIT.audit_path(path)

    def test_accepts_folded_description_with_both_boundaries(self):
        result = self.audit(
            "description: >\n"
            "  Builds bounded widgets. Use when: a widget needs a deterministic build.\n"
            "  Do not use when: the request only changes widget copy; use direct editing instead."
        )
        self.assertTrue(result.ok, result.errors)

    def test_accepts_folded_description_header_with_yaml_comment(self):
        result = self.audit(
            "description: > # routing metadata\n"
            "  Builds bounded widgets. Use when: a widget needs a deterministic build.\n"
            "  Do not use when: the request only changes widget copy; use direct editing instead."
        )
        self.assertTrue(result.ok, result.errors)

    def test_accepts_inline_description(self):
        result = self.audit(
            "description: Builds widgets. Use when: a widget needs compilation. "
            "Do not use when: the request only inspects output; use the inspection workflow instead."
        )
        self.assertTrue(result.ok, result.errors)

    def test_rejects_missing_negative_boundary(self):
        result = self.audit(
            "description: Builds widgets. Use when: a widget needs compilation."
        )
        self.assertFalse(result.ok)
        self.assertIn(
            "missing exact negative marker 'Do not use when:'", result.errors
        )

    def test_rejects_generic_alternate_route(self):
        result = self.audit(
            "description: Builds widgets. Use when: a widget needs compilation. "
            "Do not use when: the request only inspects output; use another skill instead."
        )
        self.assertFalse(result.ok)
        self.assertIn("alternate route is not explicit", result.errors)

    def test_rejects_description_over_limit(self):
        padding = "x" * AUDIT.MAX_DESCRIPTION_CHARS
        result = self.audit(
            "description: >\n"
            f"  {padding} Use when: widgets need compilation.\n"
            "  Do not use when: widgets only need inspection; use direct inspection instead."
        )
        self.assertFalse(result.ok)
        self.assertTrue(
            any("maximum is 1024" in error for error in result.errors), result.errors
        )


if __name__ == "__main__":
    unittest.main()
