#!/usr/bin/env python3
"""Regression tests for the generated Codex plugin submission package."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from types import ModuleType


REPO_ROOT = Path(__file__).resolve().parent.parent
BUILD_SCRIPT = REPO_ROOT / "scripts" / "build-codex-plugin.py"
EXPECTED_SKILLS = (
    "setup-api-key",
    "create-assistant",
    "create-structured-output",
    "vapi-prompt-builder",
    "create-tool",
    "create-call",
    "create-campaign",
    "create-squad",
    "create-phone-number",
    "setup-webhook",
    "simulations",
)


def load_build_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("build_codex_plugin", BUILD_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load build script: {BUILD_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def tree_digest(root: Path) -> dict[str, tuple[str, int]]:
    return {
        path.relative_to(root).as_posix(): (
            hashlib.sha256(path.read_bytes()).hexdigest(),
            path.stat().st_mode & 0o777,
        )
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


class CodexPluginTests(unittest.TestCase):
    def test_exact_skill_allowlist_and_experimental_exclusion(self) -> None:
        build = load_build_module()
        self.assertEqual(build.INCLUDED_SKILLS, EXPECTED_SKILLS)
        self.assertEqual(build.EXCLUDED_SKILLS, ("vapi-bootstrap-framework",))
        bootstrap_skill = REPO_ROOT / "vapi-bootstrap-framework" / "SKILL.md"
        self.assertTrue(bootstrap_skill.is_file())
        self.assertIn(
            "experimental reference workflow",
            bootstrap_skill.read_text(encoding="utf-8").lower(),
        )

        claude_marketplace = json.loads(
            (REPO_ROOT / ".claude-plugin" / "marketplace.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            tuple(
                path.removeprefix("./")
                for path in claude_marketplace["plugins"][0]["skills"]
            ),
            EXPECTED_SKILLS,
        )

        generated_skills = REPO_ROOT / "plugins" / build.PLUGIN_NAME / "skills"
        self.assertEqual(
            sorted(path.name for path in generated_skills.iterdir() if path.is_dir()),
            sorted(EXPECTED_SKILLS),
        )
        self.assertFalse((generated_skills / "vapi-bootstrap-framework").exists())

    def test_all_nested_skill_files_are_included(self) -> None:
        build = load_build_module()
        expected = build.expected_plugin_files(REPO_ROOT)
        for skill_name in EXPECTED_SKILLS:
            source_root = REPO_ROOT / skill_name
            source_files = list(build.source_files(source_root))
            self.assertTrue(source_files)
            for source in source_files:
                generated = (
                    Path("skills") / skill_name / source.relative_to(source_root)
                )
                self.assertIn(generated, expected)
                self.assertEqual(
                    expected[generated][0],
                    build.plugin_source_bytes(source),
                )

    def test_generated_skills_remove_claude_only_setup(self) -> None:
        build = load_build_module()
        expected = build.expected_plugin_files(REPO_ROOT)
        for path, (contents, _mode) in expected.items():
            if path.parts[:1] == ("skills",) and path.name == "SKILL.md":
                self.assertNotIn(b"claude mcp add", contents)

    def test_official_brand_assets_are_included(self) -> None:
        build = load_build_module()
        expected = build.expected_plugin_files(REPO_ROOT)
        source_hashes = {
            "full-logo-square-5.svg": (
                "dbcb01cb16b744cb94c37d9384d92ec38b9961213e407c0a311e1240adaf5841"
            ),
            "va-square-5.svg": (
                "73d251f2fa2d57f24aac166afd9202167d47951fdd8343ead5bc03c823c88a05"
            ),
        }
        for asset_name in build.PLUGIN_ASSET_FILES:
            source = REPO_ROOT / "codex-plugin" / "assets" / asset_name
            generated = Path("assets") / asset_name
            self.assertIn(generated, expected)
            self.assertEqual(expected[generated][0], source.read_bytes())
            self.assertEqual(
                hashlib.sha256(source.read_bytes().rstrip(b"\n")).hexdigest(),
                source_hashes[asset_name],
            )

    def test_manifest_and_marketplace_paths_are_valid(self) -> None:
        build = load_build_module()
        plugin_root = REPO_ROOT / "plugins" / build.PLUGIN_NAME
        manifest = json.loads(
            (plugin_root / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        marketplace_path = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"
        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))

        self.assertEqual(manifest["name"], "vapi-voice-ai")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertNotIn("mcpServers", manifest)
        self.assertNotIn("apps", manifest)
        self.assertEqual(manifest["author"]["email"], "support@vapi.ai")
        interface = manifest["interface"]
        self.assertEqual(interface["privacyPolicyURL"], "https://vapi.ai/privacy")
        self.assertEqual(
            interface["termsOfServiceURL"],
            "https://vapi.ai/terms-of-service",
        )
        self.assertEqual(interface["brandColor"], "#0BD8B6")
        for field in ("composerIcon", "logo"):
            asset_path = interface[field]
            self.assertTrue(asset_path.startswith("./assets/"))
            self.assertTrue((plugin_root / asset_path).is_file())
        self.assertEqual(marketplace["name"], "vapi-skills")
        self.assertEqual(len(marketplace["plugins"]), 1)
        entry = marketplace["plugins"][0]
        self.assertEqual(entry["name"], manifest["name"])
        self.assertEqual(entry["source"], {
            "source": "local",
            "path": "./plugins/vapi-voice-ai",
        })
        self.assertTrue((REPO_ROOT / entry["source"]["path"]).is_dir())
        self.assertEqual(entry["policy"]["installation"], "AVAILABLE")
        self.assertEqual(entry["policy"]["authentication"], "ON_INSTALL")

    def test_submission_materials_are_reviewer_ready(self) -> None:
        materials = json.loads(
            (REPO_ROOT / "codex-plugin" / "submission-materials.json").read_text(
                encoding="utf-8"
            )
        )
        listing = materials["listing"]
        self.assertEqual(listing["pluginIdentifier"], "vapi-voice-ai")
        self.assertEqual(listing["websiteURL"], "https://vapi.ai")
        self.assertEqual(listing["supportURL"], "https://docs.vapi.ai/support")
        self.assertEqual(listing["privacyPolicyURL"], "https://vapi.ai/privacy")
        self.assertEqual(
            listing["termsOfServiceURL"],
            "https://vapi.ai/terms-of-service",
        )
        self.assertEqual(len(materials["starterPrompts"]), 3)
        self.assertEqual(len(materials["positiveTestCases"]), 5)
        self.assertEqual(len(materials["negativeTestCases"]), 3)
        self.assertEqual(
            materials["availability"]["status"],
            "owner-selection-required",
        )
        self.assertEqual(
            materials["credentialArchitecture"]["submissionMode"],
            "Skills only",
        )
        self.assertEqual(len(materials["ownerActions"]), 6)
        self.assertTrue(materials["releaseNotes"].strip())

    def test_build_is_deterministic(self) -> None:
        build = load_build_module()
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            first = temporary_root / "first" / build.PLUGIN_NAME
            second = temporary_root / "second" / build.PLUGIN_NAME
            first_marketplace = temporary_root / "first-marketplace.json"
            second_marketplace = temporary_root / "second-marketplace.json"
            build.write_plugin(REPO_ROOT, first, first_marketplace)
            build.write_plugin(REPO_ROOT, second, second_marketplace)

            self.assertEqual(tree_digest(first), tree_digest(second))
            self.assertEqual(first_marketplace.read_bytes(), second_marketplace.read_bytes())

            first_archive = temporary_root / "first.zip"
            second_archive = temporary_root / "second.zip"
            build.write_archive(REPO_ROOT, first_archive)
            build.write_archive(REPO_ROOT, second_archive)
            self.assertEqual(first_archive.read_bytes(), second_archive.read_bytes())
            with zipfile.ZipFile(first_archive) as archive:
                self.assertEqual(
                    sorted(archive.namelist()),
                    sorted(tree_digest(first)),
                )

    def test_checked_in_generated_files_are_current(self) -> None:
        build = load_build_module()
        errors = build.compare_plugin(
            REPO_ROOT,
            REPO_ROOT / "plugins" / build.PLUGIN_NAME,
            REPO_ROOT / ".agents" / "plugins" / "marketplace.json",
        )
        self.assertEqual(errors, [])

    def test_stale_generated_file_is_rejected(self) -> None:
        build = load_build_module()
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            plugin_root = temporary_root / build.PLUGIN_NAME
            marketplace_path = temporary_root / "marketplace.json"
            build.write_plugin(REPO_ROOT, plugin_root, marketplace_path)
            stale_file = plugin_root / "skills" / "stale.txt"
            stale_file.write_text("stale\n", encoding="utf-8")

            errors = build.compare_plugin(REPO_ROOT, plugin_root, marketplace_path)
            self.assertTrue(any("stale generated file" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
