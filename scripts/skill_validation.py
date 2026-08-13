"""Dependency-free validation for Agent Skills in this repository."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote


ALLOWED_FRONTMATTER_KEYS = {
    "name",
    "description",
    "license",
    "compatibility",
    "allowed-tools",
    "metadata",
}
MAX_DESCRIPTION_LENGTH = 1024
MAX_SKILL_LINES = 500
MAX_SKILL_NAME_LENGTH = 64
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER_PATTERN = re.compile(r"\A---\n(.*?)\n---(?:\n|\Z)", re.DOTALL)
TOP_LEVEL_KEY_PATTERN = re.compile(r"^([A-Za-z][A-Za-z0-9-]*):(?:[ \t]*(.*))?$")
MARKDOWN_LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
BACKTICK_RESOURCE_PATTERN = re.compile(
    r"`((?:references|scripts|assets)/[^`]+)`"
)


def _scalar_value(value: str, continuation: list[str]) -> str:
    value = value.strip()
    if value in {"|", ">", "|-", ">-", "|+", ">+"}:
        parts = [line.strip() for line in continuation]
        return ("\n" if value.startswith("|") else " ").join(parts).strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def _parse_frontmatter(text: str) -> tuple[dict[str, str], list[str]]:
    match = FRONTMATTER_PATTERN.match(text)
    if not match:
        return {}, ["SKILL.md must start with YAML frontmatter delimited by ---"]

    lines = match.group(1).splitlines()
    entries: dict[str, tuple[str, list[str]]] = {}
    errors: list[str] = []
    current_key: str | None = None

    for line_number, line in enumerate(lines, start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[0].isspace():
            if current_key is None:
                errors.append(
                    f"frontmatter line {line_number} is indented without a parent key"
                )
            else:
                parent_value = entries[current_key][0].strip()
                nested_value = line.strip()
                is_block_scalar = parent_value in {
                    "|",
                    ">",
                    "|-",
                    ">-",
                    "|+",
                    ">+",
                }
                is_metadata_entry = current_key == "metadata" and bool(
                    TOP_LEVEL_KEY_PATTERN.match(nested_value)
                )
                is_allowed_tool = current_key == "allowed-tools" and nested_value.startswith(
                    "- "
                )
                if not (is_block_scalar or is_metadata_entry or is_allowed_tool):
                    errors.append(
                        f"frontmatter line {line_number} has unsupported nested content "
                        f"under '{current_key}'"
                    )
                entries[current_key][1].append(line)
            continue

        key_match = TOP_LEVEL_KEY_PATTERN.match(line)
        if not key_match:
            errors.append(f"frontmatter line {line_number} is not a valid key/value")
            current_key = None
            continue

        key, value = key_match.groups()
        if key in entries:
            errors.append(f"frontmatter contains duplicate key: {key}")
            current_key = key
            continue
        entries[key] = (value or "", [])
        current_key = key

    parsed = {
        key: _scalar_value(value, continuation)
        for key, (value, continuation) in entries.items()
    }
    return parsed, errors


def _local_link_target(raw_target: str) -> str | None:
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")]
    else:
        target = target.split(maxsplit=1)[0]
    target = unquote(target.split("#", maxsplit=1)[0])
    if not target or target.startswith("#"):
        return None
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target):
        return None
    return target


def _referenced_local_targets(text: str) -> set[str]:
    targets = {
        target
        for raw_target in MARKDOWN_LINK_PATTERN.findall(text)
        if (target := _local_link_target(raw_target)) is not None
    }
    targets.update(BACKTICK_RESOURCE_PATTERN.findall(text))
    return targets


def _validate_links(skill_dir: Path, markdown_files: list[Path]) -> list[str]:
    errors: list[str] = []
    resolved_skill_dir = skill_dir.resolve()

    for markdown_file in markdown_files:
        text = markdown_file.read_text(encoding="utf-8")
        for target in _referenced_local_targets(text):
            resolved = (markdown_file.parent / target).resolve()
            try:
                resolved.relative_to(resolved_skill_dir)
            except ValueError:
                errors.append(
                    f"{markdown_file.relative_to(skill_dir)} links outside the skill: {target}"
                )
                continue
            if not resolved.exists():
                errors.append(
                    f"{markdown_file.relative_to(skill_dir)} has a broken link: {target}"
                )

    return errors


def validate_skill(skill_dir: Path) -> list[str]:
    """Validate one skill and return non-blocking warnings.

    Raise ValueError with all blocking validation errors.
    """

    skill_dir = skill_dir.resolve()
    skill_file = skill_dir / "SKILL.md"
    errors: list[str] = []
    warnings: list[str] = []

    if not skill_file.is_file():
        raise ValueError(f"{skill_dir.name}: SKILL.md is missing")

    text = skill_file.read_text(encoding="utf-8")
    frontmatter, frontmatter_errors = _parse_frontmatter(text)
    errors.extend(frontmatter_errors)

    unexpected = sorted(set(frontmatter) - ALLOWED_FRONTMATTER_KEYS)
    if unexpected:
        errors.append(f"unexpected frontmatter key(s): {', '.join(unexpected)}")

    for required in ("name", "description"):
        if not frontmatter.get(required, "").strip():
            errors.append(f"frontmatter field '{required}' is required")

    name = frontmatter.get("name", "").strip()
    if name:
        if len(name) > MAX_SKILL_NAME_LENGTH:
            errors.append(
                f"name is {len(name)} characters; maximum is {MAX_SKILL_NAME_LENGTH}"
            )
        if not NAME_PATTERN.fullmatch(name):
            errors.append("name must use lowercase letters, digits, and single hyphens")
        if name != skill_dir.name:
            errors.append(
                f"frontmatter name '{name}' must match folder '{skill_dir.name}'"
            )

    description = frontmatter.get("description", "").strip()
    if len(description) > MAX_DESCRIPTION_LENGTH:
        errors.append(
            f"description is {len(description)} characters; maximum is "
            f"{MAX_DESCRIPTION_LENGTH}"
        )
    if "<" in description or ">" in description:
        errors.append("description cannot contain angle brackets")

    line_count = len(text.splitlines())
    if line_count > MAX_SKILL_LINES:
        errors.append(
            f"SKILL.md has {line_count} lines; maximum is {MAX_SKILL_LINES}"
        )

    body_match = FRONTMATTER_PATTERN.match(text)
    if body_match and not text[body_match.end() :].strip():
        errors.append("SKILL.md body is empty")

    markdown_files = sorted(skill_dir.rglob("*.md"))
    errors.extend(_validate_links(skill_dir, markdown_files))

    references_dir = skill_dir / "references"
    if references_dir.is_dir():
        skill_text = skill_file.read_text(encoding="utf-8")
        linked_targets = _referenced_local_targets(skill_text)
        for reference in sorted(references_dir.rglob("*")):
            if not reference.is_file():
                continue
            relative = reference.relative_to(skill_dir).as_posix()
            if len(reference.relative_to(references_dir).parts) > 1:
                errors.append(f"reference must be one level deep: {relative}")
            if relative not in linked_targets:
                errors.append(f"reference is not linked directly from SKILL.md: {relative}")
            if reference.suffix.lower() == ".md":
                reference_text = reference.read_text(encoding="utf-8")
                if len(reference_text.splitlines()) > 100 and not re.search(
                    r"^## Contents\s*$", reference_text, re.MULTILINE
                ):
                    warnings.append(f"{relative} exceeds 100 lines without a Contents section")

    for path in skill_dir.rglob("*"):
        if path.is_symlink():
            errors.append(f"symlinks are not allowed: {path.relative_to(skill_dir)}")

    if errors:
        formatted = "\n  - ".join(errors)
        raise ValueError(f"{skill_dir.name}: validation failed\n  - {formatted}")

    return warnings


def discover_skills(repo_root: Path) -> list[Path]:
    """Return top-level skill directories in stable order."""

    return sorted(
        path.parent
        for path in repo_root.glob("*/SKILL.md")
        if path.parent.is_dir()
    )
