#!/usr/bin/env python3
"""Import the official Conductor plugin into an Antigravity workspace.

The script downloads an archive of the official
``gemini-cli-extensions/conductor`` GitHub repository, validates its plugin
manifest, skills, and rules, and installs the complete plugin folder at
``<base-folder>/.agents/plugins/conductor``.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import stat
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile


REPOSITORY = "gemini-cli-extensions/conductor"
PLUGIN_NAME = "conductor"
DEFAULT_REF = "main"
MAX_ARCHIVE_BYTES = 100 * 1024 * 1024
SKILL_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class PluginImportError(Exception):
    """Raised when the plugin cannot be downloaded, validated, or installed."""


def download_archive(ref: str, temporary_directory: Path) -> Path:
    """Download the requested GitHub repository archive."""

    encoded_ref = urllib.parse.quote(ref, safe="")
    url = f"https://codeload.github.com/{REPOSITORY}/zip/{encoded_ref}"
    archive_path = temporary_directory / "conductor.zip"
    headers = {
        "Accept": "application/zip",
        "User-Agent": "conductor-workspace-plugin-importer",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            declared_size = response.headers.get("Content-Length")
            if declared_size and int(declared_size) > MAX_ARCHIVE_BYTES:
                raise PluginImportError(
                    f"Archive is larger than the {MAX_ARCHIVE_BYTES}-byte limit."
                )

            downloaded_size = 0
            with archive_path.open("wb") as archive_file:
                while chunk := response.read(1024 * 1024):
                    downloaded_size += len(chunk)
                    if downloaded_size > MAX_ARCHIVE_BYTES:
                        raise PluginImportError(
                            f"Archive exceeded the {MAX_ARCHIVE_BYTES}-byte limit."
                        )
                    archive_file.write(chunk)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as error:
        raise PluginImportError(f"Unable to download {url}: {error}") from error
    except ValueError as error:
        raise PluginImportError("GitHub returned an invalid archive size.") from error

    return archive_path


def _is_zip_symlink(member: zipfile.ZipInfo) -> bool:
    """Return whether a ZIP member represents a symbolic link."""

    unix_mode = member.external_attr >> 16
    return stat.S_ISLNK(unix_mode)


def extract_archive(archive_path: Path, extraction_directory: Path) -> Path:
    """Safely extract an archive and return its single repository root."""

    extraction_root = extraction_directory.resolve()
    try:
        with zipfile.ZipFile(archive_path) as archive:
            top_level_directories: set[str] = set()
            for member in archive.infolist():
                if not member.filename:
                    continue
                if "\\" in member.filename:
                    raise PluginImportError(
                        "Downloaded archive contains an unsafe path separator."
                    )
                if _is_zip_symlink(member):
                    raise PluginImportError(
                        "Downloaded archive contains a symbolic link."
                    )

                member_path = (extraction_directory / member.filename).resolve()
                if (
                    member_path != extraction_root
                    and extraction_root not in member_path.parents
                ):
                    raise PluginImportError(
                        "Downloaded archive contains a path outside its root."
                    )

                top_level = Path(member.filename).parts[0]
                if top_level:
                    top_level_directories.add(top_level)

            if len(top_level_directories) != 1:
                raise PluginImportError("Downloaded archive has an unexpected layout.")

            archive.extractall(extraction_directory)
    except zipfile.BadZipFile as error:
        raise PluginImportError("GitHub returned an invalid ZIP archive.") from error

    repository_root = extraction_directory / next(iter(top_level_directories))
    if not repository_root.is_dir():
        raise PluginImportError("Downloaded repository root was not found.")
    return repository_root


def _read_nonempty_text(path: Path, description: str) -> str:
    """Read a required UTF-8 text file and ensure it is not empty."""

    try:
        contents = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise PluginImportError(f"Unable to read {description}: {path}") from error
    if not contents.strip():
        raise PluginImportError(f"Empty {description}: {path}")
    return contents


def validate_plugin(repository_root: Path) -> tuple[list[Path], list[Path]]:
    """Validate the Conductor manifest, skill folders, and rule files."""

    manifest_path = repository_root / "plugin.json"
    if not manifest_path.is_file():
        raise PluginImportError("The repository does not contain plugin.json.")

    manifest_text = _read_nonempty_text(manifest_path, "plugin manifest")
    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError as error:
        raise PluginImportError("plugin.json is not valid JSON.") from error
    if not isinstance(manifest, dict):
        raise PluginImportError("plugin.json must contain a JSON object.")
    if manifest.get("name") != PLUGIN_NAME:
        raise PluginImportError(
            f"plugin.json must declare the name {PLUGIN_NAME!r}."
        )
    description = manifest.get("description")
    if not isinstance(description, str) or not description.strip():
        raise PluginImportError(
            "plugin.json must contain a non-empty string description."
        )

    skills_root = repository_root / "skills"
    if not skills_root.is_dir():
        raise PluginImportError("The repository does not contain a skills directory.")

    skills: list[Path] = []
    for candidate in sorted(skills_root.iterdir(), key=lambda path: path.name):
        if not candidate.is_dir():
            continue
        if not SKILL_NAME_PATTERN.fullmatch(candidate.name):
            raise PluginImportError(f"Invalid upstream skill name: {candidate.name}")
        instructions_path = candidate / "SKILL.md"
        if not instructions_path.is_file():
            raise PluginImportError(
                f"Upstream skill does not contain SKILL.md: {candidate.name}"
            )
        _read_nonempty_text(
            instructions_path, f"SKILL.md for upstream skill {candidate.name}"
        )
        skills.append(candidate)

    if not skills:
        raise PluginImportError("No valid skills were found in the plugin archive.")

    rules_root = repository_root / "rules"
    if not rules_root.is_dir():
        raise PluginImportError("The repository does not contain a rules directory.")

    rules = sorted(
        (path for path in rules_root.rglob("*.md") if path.is_file()),
        key=lambda path: path.relative_to(rules_root).as_posix(),
    )
    if not rules:
        raise PluginImportError("No Markdown rules were found in the plugin archive.")
    for rule in rules:
        _read_nonempty_text(rule, "plugin rule")

    return skills, rules


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


def install_plugin(plugin: Path, destination: Path, force: bool) -> None:
    """Install the plugin, restoring the previous version on failure."""

    if path_exists(destination) and not force:
        raise PluginImportError(
            f"Destination already exists: {destination}. "
            "Re-run with --force to replace it."
        )

    transaction_root: Path | None = None
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        transaction_root = Path(
            tempfile.mkdtemp(prefix=".conductor-plugin-", dir=destination.parent)
        )
        staged_plugin = transaction_root / "staging" / PLUGIN_NAME
        backup_plugin = transaction_root / "backup" / PLUGIN_NAME
        staged_plugin.parent.mkdir()
        backup_plugin.parent.mkdir()
        shutil.copytree(plugin, staged_plugin)
    except OSError as error:
        if transaction_root is not None:
            shutil.rmtree(transaction_root, ignore_errors=True)
        raise PluginImportError(
            f"Unable to stage the plugin for {destination}: {error}"
        ) from error

    previous_version_moved = False
    new_version_installed = False
    try:
        if path_exists(destination):
            os.replace(destination, backup_plugin)
            previous_version_moved = True
        os.replace(staged_plugin, destination)
        new_version_installed = True
    except Exception as error:
        if new_version_installed:
            remove_path(destination)
        if previous_version_moved and path_exists(backup_plugin):
            remove_path(destination)
            os.replace(backup_plugin, destination)
        raise PluginImportError(
            f"Installation failed and was rolled back: {error}"
        ) from error
    finally:
        shutil.rmtree(transaction_root, ignore_errors=True)


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description=(
            "Import the Conductor plugin from gemini-cli-extensions/conductor "
            "into <base-folder>/.agents/plugins/conductor."
        )
    )
    parser.add_argument(
        "base_folder",
        type=Path,
        help="Workspace or project folder that will contain .agents/plugins.",
    )
    parser.add_argument(
        "--ref",
        default=DEFAULT_REF,
        help="Git branch, tag, or commit to import (default: main).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing Conductor plugin after staging the new version.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Download and validate the plugin, but do not modify the destination.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    """Run the plugin importer."""

    args = parse_args(argv)
    if not args.ref.strip():
        print("Error: --ref cannot be empty.", file=sys.stderr)
        return 2

    base_folder = args.base_folder.expanduser().resolve()
    if not base_folder.is_dir():
        print(f"Error: base folder is not a directory: {base_folder}", file=sys.stderr)
        return 2

    destination = base_folder / ".agents" / "plugins" / PLUGIN_NAME
    try:
        with tempfile.TemporaryDirectory(prefix="conductor-plugin-import-") as temp:
            temporary_directory = Path(temp)
            archive_path = download_archive(args.ref, temporary_directory)
            extraction_directory = temporary_directory / "repository"
            extraction_directory.mkdir()
            repository_root = extract_archive(archive_path, extraction_directory)
            skills, rules = validate_plugin(repository_root)

            action = "replace" if path_exists(destination) else "install"
            prefix = "Would" if args.dry_run else "Will"
            print(f"Source: https://github.com/{REPOSITORY}/tree/{args.ref}")
            print(f"Destination: {destination}")
            print(
                f"Validated plugin.json, {len(skills)} skills, "
                f"and {len(rules)} rules."
            )
            if path_exists(destination) and not args.force:
                print(f"{prefix} conflict with existing: {PLUGIN_NAME}")
            else:
                print(f"{prefix} {action}: {PLUGIN_NAME}")

            if args.dry_run:
                print("Dry run complete: no workspace files were changed.")
                return 0

            install_plugin(repository_root, destination, args.force)
            print(f"Imported {PLUGIN_NAME} into {destination}")
            return 0
    except PluginImportError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"Error: filesystem operation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
