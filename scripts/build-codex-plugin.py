#!/usr/bin/env python3
"""Assemble the repository's submission-shaped, skills-only Codex plugin."""

from __future__ import annotations

import argparse
import json
import os
import stat
import sys
import zipfile
from pathlib import Path
from typing import Dict, Iterable, Tuple


PLUGIN_NAME = "vapi-voice-ai"
PLUGIN_VERSION = "1.2.0"
PLUGIN_ASSET_FILES = (
    "full-logo-square-5.svg",
    "va-square-5.svg",
)
INCLUDED_SKILLS = (
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
EXCLUDED_SKILLS = ("vapi-bootstrap-framework",)
IGNORED_NAMES = {".DS_Store", "__pycache__"}
SKILL_INTERFACES = {
    "setup-api-key": {
        "display_name": "Set Up Vapi API Key",
        "short_description": "Configure a private Vapi API key safely.",
        "default_prompt": (
            "Use $setup-api-key to help me configure a Vapi API key safely."
        ),
    },
    "create-assistant": {
        "display_name": "Create Vapi Assistant",
        "short_description": "Design Vapi voice assistant configurations.",
        "default_prompt": (
            "Use $create-assistant to create a Vapi voice assistant configuration."
        ),
    },
    "create-structured-output": {
        "display_name": "Create Structured Output",
        "short_description": "Design reusable Vapi post-call extraction.",
        "default_prompt": (
            "Use $create-structured-output to design a Vapi post-call extraction."
        ),
    },
    "vapi-prompt-builder": {
        "display_name": "Vapi Prompt Builder",
        "short_description": "Write and audit production voice-agent prompts.",
        "default_prompt": (
            "Use $vapi-prompt-builder to build a production-ready voice-agent prompt."
        ),
    },
    "create-tool": {
        "display_name": "Create Vapi Tool",
        "short_description": "Design tools for Vapi voice assistants.",
        "default_prompt": "Use $create-tool to design a tool for a Vapi assistant.",
    },
    "create-call": {
        "display_name": "Create Vapi Call",
        "short_description": "Prepare one-off Vapi phone or web calls.",
        "default_prompt": (
            "Use $create-call to prepare a one-off Vapi call without executing it."
        ),
    },
    "create-campaign": {
        "display_name": "Create Vapi Campaign",
        "short_description": "Plan and manage persistent outbound campaigns.",
        "default_prompt": (
            "Use $create-campaign to plan a Vapi outbound campaign without launching it."
        ),
    },
    "create-squad": {
        "display_name": "Create Vapi Squad",
        "short_description": "Design multi-assistant Vapi handoff workflows.",
        "default_prompt": (
            "Use $create-squad to design a multi-assistant Vapi handoff workflow."
        ),
    },
    "create-phone-number": {
        "display_name": "Create Vapi Phone Number",
        "short_description": "Configure Vapi numbers and provider imports.",
        "default_prompt": (
            "Use $create-phone-number to configure a Vapi phone number."
        ),
    },
    "setup-webhook": {
        "display_name": "Set Up Vapi Webhook",
        "short_description": "Configure Vapi server URLs and call events.",
        "default_prompt": (
            "Use $setup-webhook to configure a Vapi webhook and event subscriptions."
        ),
    },
    "simulations": {
        "display_name": "Vapi Simulations",
        "short_description": "Design Vapi assistant simulation suites.",
        "default_prompt": (
            "Use $simulations to design a Vapi assistant simulation suite."
        ),
    },
}
CLAUDE_MCP_BLOCKS = (
    b"\n**Manual setup:** If your agent doesn't auto-detect the config, run:\n"
    b"```bash\n"
    b"claude mcp add vapi-docs -- npx -y mcp-remote https://docs.vapi.ai/_mcp/server\n"
    b"```\n",
    b"\nTo add the Vapi documentation MCP server manually in Claude Code, run:\n"
    b"```bash\n"
    b"claude mcp add vapi-docs -- npx -y mcp-remote https://docs.vapi.ai/_mcp/server\n"
    b"```\n",
)


PLUGIN_MANIFEST = {
    "name": PLUGIN_NAME,
    "version": PLUGIN_VERSION,
    "description": (
        "Skills for building and testing voice AI agents with Vapi, including "
        "assistants, tools, calls, campaigns, squads, phone numbers, webhooks, "
        "structured outputs, prompts, and simulations."
    ),
    "author": {
        "name": "Vapi",
        "email": "support@vapi.ai",
        "url": "https://vapi.ai",
    },
    "homepage": "https://vapi.ai",
    "repository": "https://github.com/VapiAI/skills",
    "license": "MIT",
    "keywords": ["vapi", "voice-ai", "agents", "telephony"],
    "skills": "./skills/",
    "interface": {
        "displayName": "Vapi Voice AI",
        "shortDescription": "Build voice agents with Vapi.",
        "longDescription": (
            "Plan, configure, and validate Vapi voice AI workflows with skills for "
            "assistants, prompts, tools, calls, campaigns, squads, phone numbers, "
            "webhooks, structured outputs, and simulations."
        ),
        "developerName": "Vapi",
        "category": "Developer Tools",
        "capabilities": ["Interactive", "Write"],
        "websiteURL": "https://vapi.ai",
        "privacyPolicyURL": "https://vapi.ai/privacy",
        "termsOfServiceURL": "https://vapi.ai/terms-of-service",
        "defaultPrompt": [
            "Plan a Vapi outbound campaign without launching it.",
            "Create a Vapi voice assistant configuration.",
            "Design a Vapi simulation suite.",
        ],
        "brandColor": "#000714",
        "composerIcon": "./assets/va-square-5.svg",
        "logo": "./assets/full-logo-square-5.svg",
    },
}

MARKETPLACE_MANIFEST = {
    "name": "vapi-skills",
    "interface": {"displayName": "Vapi Skills"},
    "plugins": [
        {
            "name": PLUGIN_NAME,
            "source": {"source": "local", "path": f"./plugins/{PLUGIN_NAME}"},
            "policy": {
                "installation": "AVAILABLE",
                "authentication": "ON_INSTALL",
            },
            "category": "Developer Tools",
        }
    ],
}


def json_bytes(payload: object) -> bytes:
    return (json.dumps(payload, indent=2) + "\n").encode("utf-8")


def openai_yaml_bytes(interface: dict[str, str]) -> bytes:
    """Render deterministic YAML without adding a runtime YAML dependency."""
    lines = ["interface:"]
    for key in ("display_name", "short_description", "default_prompt"):
        lines.append(f"  {key}: {json.dumps(interface[key])}")
    return ("\n".join(lines) + "\n").encode("utf-8")


def normalize_openai_skill_frontmatter(contents: bytes, source: Path) -> bytes:
    """Remove unsupported frontmatter fields from the OpenAI package copy only."""
    lines = contents.splitlines(keepends=True)
    if not lines or lines[0].strip() != b"---":
        raise ValueError(f"skill is missing YAML frontmatter: {source}")

    closing_index = next(
        (index for index, line in enumerate(lines[1:], start=1) if line.strip() == b"---"),
        None,
    )
    if closing_index is None:
        raise ValueError(f"skill has unterminated YAML frontmatter: {source}")

    for field in (b"compatibility", b"metadata"):
        field_indexes = [
            index
            for index, line in enumerate(lines[1:closing_index], start=1)
            if line.startswith(field + b":")
        ]
        if len(field_indexes) != 1:
            raise ValueError(
                f"skill must have exactly one {field.decode()} field: {source}"
            )

        start = field_indexes[0]
        end = start + 1
        while end < closing_index and lines[end].startswith((b" ", b"\t")):
            end += 1
        del lines[start:end]
        closing_index -= end - start

    return b"".join(lines)


def source_files(skill_dir: Path) -> Iterable[Path]:
    for path in sorted(skill_dir.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(skill_dir)
        if any(part in IGNORED_NAMES for part in relative.parts):
            continue
        if path.is_symlink():
            raise ValueError(f"{skill_dir.name}: symlinks are not allowed ({relative})")
        if path.is_file():
            yield path


def plugin_source_bytes(source: Path) -> bytes:
    """Return provider-neutral bytes for the Codex package without changing sources."""
    contents = source.read_bytes()
    if source.name != "SKILL.md":
        return contents
    contents = normalize_openai_skill_frontmatter(contents, source)
    for block in CLAUDE_MCP_BLOCKS:
        contents = contents.replace(block, b"\n")
    if b"claude mcp add" in contents:
        raise ValueError(f"Claude-specific MCP setup remains in generated skill: {source}")
    return contents


def expected_plugin_files(repo_root: Path) -> Dict[Path, Tuple[bytes, int]]:
    if tuple(SKILL_INTERFACES) != INCLUDED_SKILLS:
        raise ValueError("skill interface definitions must match the included skill allowlist")
    expected: Dict[Path, Tuple[bytes, int]] = {
        Path(".codex-plugin/plugin.json"): (json_bytes(PLUGIN_MANIFEST), 0o644),
    }
    asset_root = repo_root / "codex-plugin" / "assets"
    for asset_name in PLUGIN_ASSET_FILES:
        source = asset_root / asset_name
        if not source.is_file():
            raise ValueError(f"plugin asset is missing: {source}")
        expected[Path("assets") / asset_name] = (source.read_bytes(), 0o644)
    for skill_name in INCLUDED_SKILLS:
        skill_dir = repo_root / skill_name
        if not (skill_dir / "SKILL.md").is_file():
            raise ValueError(f"included skill is missing SKILL.md: {skill_name}")
        for source in source_files(skill_dir):
            relative = Path("skills") / skill_name / source.relative_to(skill_dir)
            mode = 0o755 if source.stat().st_mode & stat.S_IXUSR else 0o644
            expected[relative] = (plugin_source_bytes(source), mode)
        interface_path = Path("skills") / skill_name / "agents" / "openai.yaml"
        if interface_path in expected:
            raise ValueError(
                f"canonical skill already supplies generated interface path: {skill_name}"
            )
        expected[interface_path] = (
            openai_yaml_bytes(SKILL_INTERFACES[skill_name]),
            0o644,
        )
    return expected


def existing_plugin_files(plugin_root: Path) -> Dict[Path, Tuple[bytes, int]]:
    if not plugin_root.exists():
        return {}
    existing: Dict[Path, Tuple[bytes, int]] = {}
    for path in sorted(plugin_root.rglob("*"), key=lambda item: item.as_posix()):
        if path.is_symlink():
            relative = path.relative_to(plugin_root)
            raise ValueError(f"generated plugin contains a symlink: {relative}")
        if path.is_file():
            relative = path.relative_to(plugin_root)
            existing[relative] = (path.read_bytes(), stat.S_IMODE(path.stat().st_mode))
    return existing


def compare_plugin(repo_root: Path, plugin_root: Path, marketplace_path: Path) -> list[str]:
    expected = expected_plugin_files(repo_root)
    existing = existing_plugin_files(plugin_root)
    errors = []
    for path in sorted(set(expected) - set(existing), key=lambda item: item.as_posix()):
        errors.append(f"missing generated file: {plugin_root / path}")
    for path in sorted(set(existing) - set(expected), key=lambda item: item.as_posix()):
        errors.append(f"stale generated file: {plugin_root / path}")
    for path in sorted(set(expected) & set(existing), key=lambda item: item.as_posix()):
        if existing[path] != expected[path]:
            errors.append(f"out-of-date generated file: {plugin_root / path}")

    expected_marketplace = json_bytes(MARKETPLACE_MANIFEST)
    if not marketplace_path.is_file():
        errors.append(f"missing generated file: {marketplace_path}")
    elif marketplace_path.read_bytes() != expected_marketplace:
        errors.append(f"out-of-date generated file: {marketplace_path}")
    return errors


def write_plugin(repo_root: Path, plugin_root: Path, marketplace_path: Path) -> None:
    expected = expected_plugin_files(repo_root)
    plugin_root.mkdir(parents=True, exist_ok=True)

    existing = existing_plugin_files(plugin_root)
    for relative in sorted(set(existing) - set(expected), key=lambda item: item.as_posix()):
        (plugin_root / relative).unlink()

    for relative, (contents, mode) in expected.items():
        destination = plugin_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(contents)
        os.chmod(destination, mode)

    for directory in sorted(
        (path for path in plugin_root.rglob("*") if path.is_dir()),
        key=lambda item: len(item.parts),
        reverse=True,
    ):
        if not any(directory.iterdir()):
            directory.rmdir()

    marketplace_path.parent.mkdir(parents=True, exist_ok=True)
    marketplace_path.write_bytes(json_bytes(MARKETPLACE_MANIFEST))


def write_archive(repo_root: Path, archive_path: Path) -> None:
    """Write a byte-for-byte deterministic upload archive."""
    expected = expected_plugin_files(repo_root)
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        archive_path,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for relative, (contents, mode) in sorted(
            expected.items(), key=lambda item: item[0].as_posix()
        ):
            info = zipfile.ZipInfo(relative.as_posix(), date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | mode) << 16
            archive.writestr(info, contents, compresslevel=9)


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if generated files are stale")
    parser.add_argument(
        "--output",
        type=Path,
        default=repo_root / "plugins" / PLUGIN_NAME,
        help="Plugin output directory",
    )
    parser.add_argument(
        "--marketplace",
        type=Path,
        default=repo_root / ".agents" / "plugins" / "marketplace.json",
        help="Marketplace manifest output path",
    )
    parser.add_argument(
        "--archive",
        type=Path,
        help="Optional deterministic ZIP archive output path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    plugin_root = args.output.expanduser().resolve()
    marketplace_path = args.marketplace.expanduser().resolve()

    if args.check:
        errors = compare_plugin(repo_root, plugin_root, marketplace_path)
        if errors:
            print("Codex plugin assembly check failed:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            raise SystemExit(1)
        print(f"Codex plugin assembly is current: {plugin_root}")
        return

    write_plugin(repo_root, plugin_root, marketplace_path)
    print(f"Built Codex plugin: {plugin_root}")
    print(f"Built marketplace manifest: {marketplace_path}")
    if args.archive is not None:
        archive_path = args.archive.expanduser().resolve()
        write_archive(repo_root, archive_path)
        print(f"Built Codex plugin archive: {archive_path}")


if __name__ == "__main__":
    main()
