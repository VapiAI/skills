#!/usr/bin/env python3
"""Build deterministic ZIP archives for multi-file Agent Skills."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import zipfile
from pathlib import Path


DEFAULT_SKILLS = (
    "create-assistant",
    "create-tool",
    "setup-webhook",
    "vapi-prompt-builder",
)
IGNORED_NAMES = {".DS_Store", "__pycache__"}
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def validate_skill(skill_dir: Path) -> None:
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        raise ValueError(f"{skill_dir.name}: SKILL.md is missing")

    text = skill_file.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        raise ValueError(f"{skill_dir.name}: SKILL.md has no YAML frontmatter")

    frontmatter = match.group(1)
    name_match = re.search(r"^name:\s*([^\n]+)$", frontmatter, flags=re.MULTILINE)
    if not name_match or name_match.group(1).strip(' "\'') != skill_dir.name:
        raise ValueError(f"{skill_dir.name}: frontmatter name must match the folder")
    if not re.search(r"^description:\s*\S", frontmatter, flags=re.MULTILINE):
        raise ValueError(f"{skill_dir.name}: frontmatter description is missing")


def package_files(skill_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in skill_dir.rglob("*"):
        if any(part in IGNORED_NAMES for part in path.relative_to(skill_dir).parts):
            continue
        if path.is_symlink():
            raise ValueError(f"{skill_dir.name}: symlinks are not allowed ({path})")
        if path.is_file():
            files.append(path)
    return sorted(files, key=lambda path: path.relative_to(skill_dir).as_posix())


def build_archive(skill_dir: Path, output_dir: Path) -> dict[str, object]:
    validate_skill(skill_dir)
    files = package_files(skill_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    archive_path = output_dir / f"{skill_dir.name}.zip"

    with zipfile.ZipFile(
        archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for path in files:
            relative_path = path.relative_to(skill_dir).as_posix()
            info = zipfile.ZipInfo(relative_path, date_time=ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(info, path.read_bytes(), compresslevel=9)

    archive_bytes = archive_path.read_bytes()
    return {
        "name": skill_dir.name,
        "archive": str(archive_path),
        "mediaType": "application/zip",
        "sha256": hashlib.sha256(archive_bytes).hexdigest(),
        "bytes": len(archive_bytes),
        "files": [path.relative_to(skill_dir).as_posix() for path in files],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skills", nargs="*", default=list(DEFAULT_SKILLS))
    parser.add_argument("--output", default="dist/agent-skills")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    output_dir = repo_root / args.output
    results = []
    for skill_name in args.skills:
        skill_dir = repo_root / skill_name
        if not skill_dir.is_dir():
            raise SystemExit(f"Unknown skill directory: {skill_name}")
        results.append(build_archive(skill_dir, output_dir))

    print(json.dumps({"archives": results}, indent=2))


if __name__ == "__main__":
    main()
