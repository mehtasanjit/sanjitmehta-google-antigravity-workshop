#!/usr/bin/env python3
"""Import Google Agents CLI skills into a workspace folder.

The script downloads an archive of the official ``google/agents-cli`` GitHub
repository, discovers every skill under its top-level ``skills`` directory,
and installs each complete skill folder into ``<base-folder>/.agents/skills``.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile


REPOSITORY = "google/agents-cli"
DEFAULT_REF = "main"
MAX_ARCHIVE_BYTES = 100 * 1024 * 1024
SKILL_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class SkillImportError(Exception):
    """Raised when skills cannot be downloaded, validated, or installed."""


def download_archive(ref: str, temporary_directory: Path) -> Path:
    """Download the requested GitHub repository archive."""

    encoded_ref = urllib.parse.quote(ref, safe="")
    url = f"https://codeload.github.com/{REPOSITORY}/zip/{encoded_ref}"
    archive_path = temporary_directory / "agents-cli.zip"
    headers = {
        "Accept": "application/zip",
        "User-Agent": "google-agents-cli-workspace-skill-importer",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            declared_size = response.headers.get("Content-Length")
            if declared_size and int(declared_size) > MAX_ARCHIVE_BYTES:
                raise SkillImportError(
                    f"Archive is larger than the {MAX_ARCHIVE_BYTES}-byte limit."
                )

            downloaded_size = 0
            with archive_path.open("wb") as archive_file:
                while chunk := response.read(1024 * 1024):
                    downloaded_size += len(chunk)
                    if downloaded_size > MAX_ARCHIVE_BYTES:
                        raise SkillImportError(
                            f"Archive exceeded the {MAX_ARCHIVE_BYTES}-byte limit."
                        )
                    archive_file.write(chunk)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as error:
        raise SkillImportError(f"Unable to download {url}: {error}") from error
    except ValueError as error:
        raise SkillImportError("GitHub returned an invalid archive size.") from error

    return archive_path


def extract_archive(archive_path: Path, extraction_directory: Path) -> Path:
    """Safely extract an archive and return its single repository root."""

    extraction_root = extraction_directory.resolve()
    try:
        with zipfile.ZipFile(archive_path) as archive:
            top_level_directories: set[str] = set()
            for member in archive.infolist():
                if not member.filename:
                    continue
                member_path = (extraction_directory / member.filename).resolve()
                if (
                    member_path != extraction_root
                    and extraction_root not in member_path.parents
                ):
                    raise SkillImportError(
                        "Downloaded archive contains a path outside its root."
                    )
                top_level = Path(member.filename).parts[0]
                if top_level:
                    top_level_directories.add(top_level)

            if len(top_level_directories) != 1:
                raise SkillImportError("Downloaded archive has an unexpected layout.")

            archive.extractall(extraction_directory)
    except zipfile.BadZipFile as error:
        raise SkillImportError("GitHub returned an invalid ZIP archive.") from error

    repository_root = extraction_directory / next(iter(top_level_directories))
    if not repository_root.is_dir():
        raise SkillImportError("Downloaded repository root was not found.")
    return repository_root


def discover_skills(repository_root: Path) -> list[Path]:
    """Discover and validate all top-level skill directories."""

    skills_root = repository_root / "skills"
    if not skills_root.is_dir():
        raise SkillImportError("The repository does not contain a skills directory.")

    skills: list[Path] = []
    for candidate in sorted(skills_root.iterdir(), key=lambda path: path.name):
        if not candidate.is_dir() or not (candidate / "SKILL.md").is_file():
            continue
        if not SKILL_NAME_PATTERN.fullmatch(candidate.name):
            raise SkillImportError(f"Invalid upstream skill name: {candidate.name}")
        try:
            skill_instructions = (candidate / "SKILL.md").read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            raise SkillImportError(
                f"Unable to read SKILL.md in upstream skill: {candidate.name}"
            ) from error
        if not skill_instructions.strip():
            raise SkillImportError(f"Empty SKILL.md in upstream skill: {candidate.name}")
        skills.append(candidate)

    if not skills:
        raise SkillImportError("No valid skills were found in the repository archive.")
    return skills


def path_exists(path: Path) -> bool:
    """Return whether a path exists, including a broken symbolic link."""

    return path.exists() or path.is_symlink()


def remove_path(path: Path) -> None:
    """Remove a file, link, or directory used during transactional rollback."""

    if not path_exists(path):
        return
    if path.is_symlink() or path.is_file():
        path.unlink()
    else:
        shutil.rmtree(path)


def install_skills(skills: list[Path], destination: Path, force: bool) -> None:
    """Install all skills, restoring prior contents if an operation fails."""

    if path_exists(destination) and not destination.is_dir():
        raise SkillImportError(f"Destination is not a directory: {destination}")

    conflicts = [skill.name for skill in skills if path_exists(destination / skill.name)]
    if conflicts and not force:
        formatted_conflicts = ", ".join(conflicts)
        raise SkillImportError(
            "Destination skill directories already exist: "
            f"{formatted_conflicts}. Re-run with --force to replace them."
        )

    transaction_root: Path | None = None
    try:
        destination.mkdir(parents=True, exist_ok=True)
        transaction_root = Path(
            tempfile.mkdtemp(prefix=".agents-cli-skills-", dir=destination.parent)
        )
        staging_root = transaction_root / "staging"
        backup_root = transaction_root / "backup"
        staging_root.mkdir()
        backup_root.mkdir()
    except OSError as error:
        if transaction_root is not None:
            shutil.rmtree(transaction_root, ignore_errors=True)
        raise SkillImportError(
            f"Unable to prepare destination directory {destination}: {error}"
        ) from error

    installed: list[str] = []

    try:
        for skill in skills:
            shutil.copytree(skill, staging_root / skill.name)

        for skill in skills:
            name = skill.name
            target = destination / name
            backup = backup_root / name
            if path_exists(target):
                os.replace(target, backup)
            os.replace(staging_root / name, target)
            installed.append(name)
    except Exception as error:
        for name in reversed([skill.name for skill in skills]):
            target = destination / name
            backup = backup_root / name
            if name in installed:
                remove_path(target)
            if path_exists(backup):
                remove_path(target)
                os.replace(backup, target)
        raise SkillImportError(f"Installation failed and was rolled back: {error}") from error
    finally:
        shutil.rmtree(transaction_root, ignore_errors=True)


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description=(
            "Import every skill from google/agents-cli into "
            "<base-folder>/.agents/skills."
        )
    )
    parser.add_argument(
        "base_folder",
        type=Path,
        help="Workspace or project folder that will contain .agents/skills.",
    )
    parser.add_argument(
        "--ref",
        default=DEFAULT_REF,
        help="Git branch, tag, or commit to import (default: main).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace existing skill directories after staging the new versions.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Download and validate skills, but do not modify the destination.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    """Run the skill importer."""

    args = parse_args(argv)
    if not args.ref.strip():
        print("Error: --ref cannot be empty.", file=sys.stderr)
        return 2

    base_folder = args.base_folder.expanduser().resolve()
    if not base_folder.is_dir():
        print(f"Error: base folder is not a directory: {base_folder}", file=sys.stderr)
        return 2

    destination = base_folder / ".agents" / "skills"
    try:
        with tempfile.TemporaryDirectory(prefix="google-agents-cli-skills-") as temp:
            temporary_directory = Path(temp)
            archive_path = download_archive(args.ref, temporary_directory)
            extraction_directory = temporary_directory / "repository"
            extraction_directory.mkdir()
            repository_root = extract_archive(archive_path, extraction_directory)
            skills = discover_skills(repository_root)

            print(f"Source: https://github.com/{REPOSITORY}/tree/{args.ref}/skills")
            print(f"Destination: {destination}")
            for skill in skills:
                already_exists = path_exists(destination / skill.name)
                if already_exists and not args.force:
                    action = "conflict with existing"
                elif already_exists:
                    action = "replace"
                else:
                    action = "install"
                prefix = "Would" if args.dry_run else "Will"
                print(f"{prefix} {action}: {skill.name}")

            if args.dry_run:
                print(f"Dry run complete: found {len(skills)} skills.")
                return 0

            install_skills(skills, destination, args.force)
            print(f"Imported {len(skills)} skills into {destination}")
            return 0
    except SkillImportError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"Error: filesystem operation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
