#!/usr/bin/env python3
"""Regression tests for the repository's Agent Skill validator."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from skill_validation import validate_skill


class SkillValidationTests(unittest.TestCase):
    def write_skill(
        self,
        root: Path,
        *,
        name: str = "example-skill",
        extra_frontmatter: str = "",
        body: str = "# Example\n",
    ) -> Path:
        skill_dir = root / name
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\n"
            f"name: {name}\n"
            "description: Validate a representative Agent Skill.\n"
            "license: MIT\n"
            "compatibility: Requires internet access.\n"
            "metadata:\n"
            "  author: vapi\n"
            "  version: \"1.0\"\n"
            f"{extra_frontmatter}"
            "---\n\n"
            f"{body}",
            encoding="utf-8",
        )
        return skill_dir

    def test_accepts_repository_frontmatter_and_linked_reference(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            skill_dir = self.write_skill(
                root,
                body="# Example\n\nRead `references/details.md`.\n",
            )
            references = skill_dir / "references"
            references.mkdir()
            (references / "details.md").write_text("# Details\n", encoding="utf-8")

            self.assertEqual(validate_skill(skill_dir), [])

    def test_rejects_unknown_frontmatter_key(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            skill_dir = self.write_skill(
                Path(temporary_directory), extra_frontmatter="unknown: value\n"
            )

            with self.assertRaisesRegex(ValueError, "unexpected frontmatter key"):
                validate_skill(skill_dir)

    def test_rejects_broken_local_link(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            skill_dir = self.write_skill(
                Path(temporary_directory),
                body="# Example\n\nRead [Details](references/missing.md).\n",
            )

            with self.assertRaisesRegex(ValueError, "broken link"):
                validate_skill(skill_dir)

    def test_rejects_unlinked_reference(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            skill_dir = self.write_skill(Path(temporary_directory))
            references = skill_dir / "references"
            references.mkdir()
            (references / "orphan.md").write_text("# Orphan\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "not linked directly"):
                validate_skill(skill_dir)

    def test_rejects_skill_over_500_lines(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            skill_dir = self.write_skill(
                Path(temporary_directory), body="\n".join(["instruction"] * 501)
            )

            with self.assertRaisesRegex(ValueError, "maximum is 500"):
                validate_skill(skill_dir)


if __name__ == "__main__":
    unittest.main()
