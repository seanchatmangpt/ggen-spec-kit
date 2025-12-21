"""
specify_cli.runtime.template - Template Operations
===================================================

Runtime layer for template extraction and file operations.

This module handles all template-related I/O operations including
ZIP extraction, file copying, merging, and permission management.

Key Features
-----------
* **ZIP Extraction**: Extract templates with nested directory handling
* **File Merging**: Intelligent JSON file merging (e.g., VSCode settings)
* **Permission Management**: Ensure script executability on POSIX
* **Cleanup**: Temporary file management

Security
--------
* Path validation before extraction
* Secure temporary directories
* No path traversal vulnerabilities

Examples
--------
    >>> from specify_cli.runtime.template import extract_template
    >>>
    >>> extract_template(zip_path, project_path)

See Also
--------
- :mod:`specify_cli.runtime.github` : GitHub download operations
- :mod:`specify_cli.core.telemetry` : Telemetry utilities
"""

from __future__ import annotations

import json
import os
import shutil
import stat
import tempfile
import time
import zipfile
from pathlib import Path
from typing import Any

from specify_cli.core.instrumentation import add_span_attributes, add_span_event
from specify_cli.core.semconv import TemplateAttributes, TemplateOperations
from specify_cli.core.telemetry import metric_counter, metric_histogram, span

__all__ = [
    "TemplateError",
    "ensure_executable_scripts",
    "extract_template",
    "handle_vscode_settings",
    "merge_json_files",
]


class TemplateError(Exception):
    """Template operation error."""


def merge_json_files(existing_path: Path, new_content: dict[str, Any]) -> dict[str, Any]:
    """Merge new JSON content into existing JSON file.

    Performs a deep merge where:
    - New keys are added
    - Existing keys are preserved unless overwritten by new content
    - Nested dictionaries are merged recursively
    - Lists and other values are replaced (not merged)

    Parameters
    ----------
    existing_path : Path
        Path to existing JSON file.
    new_content : dict[str, Any]
        New JSON content to merge in.

    Returns
    -------
    dict[str, Any]
        Merged JSON content.
    """
    with span("template.merge_json", path=str(existing_path)):
        try:
            with open(existing_path, encoding="utf-8") as f:
                existing_content = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # If file doesn't exist or is invalid, just use new content
            return new_content

        def deep_merge(base: dict[str, Any], update: dict[str, Any]) -> dict[str, Any]:
            """Recursively merge update dict into base dict."""
            result = base.copy()
            for key, value in update.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result

        merged = deep_merge(existing_content, new_content)
        metric_counter("template.json_merged")(1)
        return merged


def handle_vscode_settings(source_path: Path, dest_path: Path) -> None:
    """Handle merging or copying of .vscode/settings.json files.

    Parameters
    ----------
    source_path : Path
        Source settings.json file.
    dest_path : Path
        Destination settings.json file.
    """
    with span("template.vscode_settings", source=str(source_path), dest=str(dest_path)):
        try:
            with open(source_path, encoding="utf-8") as f:
                new_settings = json.load(f)

            if dest_path.exists():
                merged = merge_json_files(dest_path, new_settings)
                with open(dest_path, "w", encoding="utf-8") as f:
                    json.dump(merged, f, indent=4)
                    f.write("\n")
                add_span_event("vscode.settings.merged", {})
            else:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, dest_path)
                add_span_event("vscode.settings.copied", {})

            metric_counter("template.vscode_settings.handled")(1)

        except Exception as e:
            # Fallback to simple copy
            shutil.copy2(source_path, dest_path)
            add_span_event("vscode.settings.fallback", {"error": str(e)})


def extract_template(
    zip_path: Path,
    project_path: Path,
    *,
    is_current_dir: bool = False,
    merge_existing: bool = True,
) -> Path:
    """Extract template from ZIP file to project directory.

    Parameters
    ----------
    zip_path : Path
        Path to the ZIP file.
    project_path : Path
        Destination directory for extraction.
    is_current_dir : bool, optional
        If True, merge into current directory. Default is False.
    merge_existing : bool, optional
        If True, merge with existing files. Default is True.

    Returns
    -------
    Path
        Path to the extracted project directory.

    Raises
    ------
    TemplateError
        If extraction fails.
    """
    start_time = time.time()

    with span(
        TemplateOperations.EXTRACT,
        **{
            TemplateAttributes.SOURCE: str(zip_path),
            TemplateAttributes.DESTINATION: str(project_path),
        },
    ):
        add_span_event("template.extract.starting", {"zip": str(zip_path)})

        try:
            if not is_current_dir:
                project_path.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_contents = zip_ref.namelist()
                add_span_attributes(**{TemplateAttributes.FILES_EXTRACTED: len(zip_contents)})

                if is_current_dir:
                    # Extract to temp directory first, then merge
                    _extract_and_merge(zip_ref, project_path)
                else:
                    # Extract directly
                    zip_ref.extractall(project_path)

                    # Handle nested directory structure
                    extracted_items = list(project_path.iterdir())
                    if len(extracted_items) == 1 and extracted_items[0].is_dir():
                        _flatten_nested_directory(project_path, extracted_items[0])

            duration = time.time() - start_time

            # Record metrics
            metric_counter("template.extract.success")(1)
            metric_histogram("template.extract.duration")(duration)
            metric_histogram("template.extract.files")(float(len(zip_contents)))

            add_span_event(
                "template.extract.completed",
                {
                    "files": len(zip_contents),
                    "duration": duration,
                },
            )

            return project_path

        except Exception as e:
            duration = time.time() - start_time
            metric_counter("template.extract.error")(1)

            add_span_event(
                "template.extract.failed",
                {
                    "error": str(e),
                    "duration": duration,
                },
            )

            # Clean up on failure
            if not is_current_dir and project_path.exists():
                shutil.rmtree(project_path)

            raise TemplateError(f"Failed to extract template: {e}") from e


def _extract_and_merge(zip_ref: zipfile.ZipFile, project_path: Path) -> None:
    """Extract ZIP to temp directory and merge into project path."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        zip_ref.extractall(temp_path)

        extracted_items = list(temp_path.iterdir())

        # Handle nested directory
        source_dir = temp_path
        if len(extracted_items) == 1 and extracted_items[0].is_dir():
            source_dir = extracted_items[0]

        # Merge each item
        for item in source_dir.iterdir():
            dest_path = project_path / item.name

            if item.is_dir():
                if dest_path.exists():
                    # Merge directory contents
                    _merge_directory(item, dest_path)
                else:
                    shutil.copytree(item, dest_path)
            else:
                shutil.copy2(item, dest_path)


def _merge_directory(source_dir: Path, dest_dir: Path) -> None:
    """Recursively merge source directory into destination."""
    for sub_item in source_dir.rglob("*"):
        if sub_item.is_file():
            rel_path = sub_item.relative_to(source_dir)
            dest_file = dest_dir / rel_path
            dest_file.parent.mkdir(parents=True, exist_ok=True)

            # Special handling for .vscode/settings.json
            if dest_file.name == "settings.json" and dest_file.parent.name == ".vscode":
                handle_vscode_settings(sub_item, dest_file)
            else:
                shutil.copy2(sub_item, dest_file)


def _flatten_nested_directory(project_path: Path, nested_dir: Path) -> None:
    """Flatten a single nested directory to project root."""
    temp_move_dir = project_path.parent / f"{project_path.name}_temp"

    shutil.move(str(nested_dir), str(temp_move_dir))
    project_path.rmdir()
    shutil.move(str(temp_move_dir), str(project_path))

    add_span_event("template.flatten.completed", {})


def ensure_executable_scripts(project_path: Path) -> tuple[int, list[str]]:
    """Ensure POSIX .sh scripts have execute permissions.

    No-op on Windows.

    Parameters
    ----------
    project_path : Path
        Project root directory.

    Returns
    -------
    tuple[int, list[str]]
        Number of scripts updated and list of any failures.
    """
    if os.name == "nt":
        return 0, []

    scripts_root = project_path / ".specify" / "scripts"
    if not scripts_root.is_dir():
        return 0, []

    with span("template.chmod_scripts", path=str(scripts_root)):
        failures: list[str] = []
        updated = 0

        for script in scripts_root.rglob("*.sh"):
            try:
                if script.is_symlink() or not script.is_file():
                    continue

                # Check for shebang
                try:
                    with script.open("rb") as f:
                        if f.read(2) != b"#!":
                            continue
                except Exception:
                    continue

                st = script.stat()
                mode = st.st_mode

                # Skip if already executable
                if mode & 0o111:
                    continue

                # Add execute bits based on read permissions
                new_mode = mode
                if mode & stat.S_IRUSR:
                    new_mode |= stat.S_IXUSR
                if mode & stat.S_IRGRP:
                    new_mode |= stat.S_IXGRP
                if mode & stat.S_IROTH:
                    new_mode |= stat.S_IXOTH
                if not (new_mode & stat.S_IXUSR):
                    new_mode |= stat.S_IXUSR

                os.chmod(script, new_mode)
                updated += 1

            except Exception as e:
                failures.append(f"{script.relative_to(scripts_root)}: {e}")

        # Record metrics
        metric_counter("template.chmod.updated")(updated)
        if failures:
            metric_counter("template.chmod.failures")(len(failures))

        add_span_attributes(
            scripts_updated=updated,
            scripts_failed=len(failures),
        )

        return updated, failures
