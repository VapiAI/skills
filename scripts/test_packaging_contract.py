#!/usr/bin/env python3
"""Regression tests for the public Agent Skills packaging contract."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path
from types import ModuleType


REPO_ROOT = Path(__file__).resolve().parent.parent
PACKAGING_SCRIPT = REPO_ROOT / "scripts" / "package-agent-skills.py"
EXPECTED_ARCHIVE_SKILLS = (
    "create-assistant",
    "create-phone-number",
    "create-squad",
    "create-tool",
    "setup-webhook",
    "vapi-prompt-builder",
)
EXPECTED_RELEASE_VERSION = "1.1.0"


def load_packaging_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("package_agent_skills", PACKAGING_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load packaging script: {PACKAGING_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PackagingContractTests(unittest.TestCase):
    def test_default_archive_allowlist_is_exact(self) -> None:
        packaging = load_packaging_module()

        self.assertEqual(packaging.DEFAULT_SKILLS, EXPECTED_ARCHIVE_SKILLS)
        for skill_name in EXPECTED_ARCHIVE_SKILLS:
            skill_dir = REPO_ROOT / skill_name
            self.assertTrue((skill_dir / "SKILL.md").is_file())
            self.assertTrue(
                any(path.is_file() for path in skill_dir.rglob("*") if path.name != "SKILL.md"),
                f"{skill_name} must remain an archive because it has supporting files",
            )

    def test_marketplace_versions_match_release(self) -> None:
        marketplace_path = REPO_ROOT / ".claude-plugin" / "marketplace.json"
        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))

        self.assertEqual(
            marketplace["metadata"]["version"], EXPECTED_RELEASE_VERSION
        )
        self.assertEqual(
            marketplace["plugins"][0]["version"], EXPECTED_RELEASE_VERSION
        )


if __name__ == "__main__":
    unittest.main()
