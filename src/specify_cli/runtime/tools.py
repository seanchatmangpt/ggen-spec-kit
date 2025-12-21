"""
specify_cli.runtime.tools - Tool Detection
===========================================

Runtime layer for detecting and validating installed tools.

This module provides utilities to check if required external tools
are installed and available in the system PATH.

Key Features
-----------
* **Tool Detection**: Check if tools are installed
* **Path Resolution**: Find executable paths
* **Special Handling**: Claude CLI after migrate-installer
* **Telemetry**: Full OTEL instrumentation

Security
--------
* Path validation
* No command execution for detection
* Uses shutil.which for safe resolution

Examples
--------
    >>> from specify_cli.runtime.tools import check_tool, which_tool
    >>>
    >>> if check_tool("git"):
    ...     path = which_tool("git")

See Also
--------
- :mod:`specify_cli.core.process` : Process execution utilities
- :mod:`specify_cli.core.telemetry` : Telemetry utilities
"""

from __future__ import annotations

import shutil
from pathlib import Path

from specify_cli.core.instrumentation import add_span_attributes
from specify_cli.core.telemetry import metric_counter, span

__all__ = [
    "CLAUDE_LOCAL_PATH",
    "OPTIONAL_TOOLS",
    "REQUIRED_TOOLS",
    "check_required_tools",
    "check_tool",
    "get_ggen_version",
    "get_tool_versions",
    "which_tool",
]

# Claude CLI path after migrate-installer
# See: https://github.com/github/spec-kit/issues/123
CLAUDE_LOCAL_PATH = Path.home() / ".claude" / "local" / "claude"

# Required tools for basic functionality
REQUIRED_TOOLS = ["git"]

# Optional tools for enhanced functionality
OPTIONAL_TOOLS = ["claude", "cursor", "ggen", "uv"]


def which_tool(tool: str) -> Path | None:
    """Find the full path to an executable.

    Handles special cases like Claude CLI after migrate-installer.

    Parameters
    ----------
    tool : str
        Name of the tool to find.

    Returns
    -------
    Path | None
        Full path to the executable, or None if not found.
    """
    with span("tools.which", tool=tool):
        # Special handling for Claude CLI
        if tool == "claude":
            if CLAUDE_LOCAL_PATH.exists() and CLAUDE_LOCAL_PATH.is_file():
                add_span_attributes(
                    tool_path=str(CLAUDE_LOCAL_PATH),
                    tool_found=True,
                    special_path=True,
                )
                metric_counter("tools.which.claude_local")(1)
                return CLAUDE_LOCAL_PATH

        # Standard PATH lookup
        result = shutil.which(tool)
        if result:
            path = Path(result)
            add_span_attributes(
                tool_path=str(path),
                tool_found=True,
                special_path=False,
            )
            metric_counter(f"tools.which.found.{tool}")(1)
            return path

        add_span_attributes(tool_found=False)
        metric_counter(f"tools.which.not_found.{tool}")(1)
        return None


def check_tool(tool: str) -> bool:
    """Check if a tool is installed and available.

    Parameters
    ----------
    tool : str
        Name of the tool to check.

    Returns
    -------
    bool
        True if tool is available, False otherwise.
    """
    with span("tools.check", tool=tool):
        found = which_tool(tool) is not None
        add_span_attributes(tool_available=found)

        if found:
            metric_counter("tools.check.available")(1)
        else:
            metric_counter("tools.check.missing")(1)

        return found


def check_required_tools() -> tuple[list[str], list[str]]:
    """Check all required and optional tools.

    Returns
    -------
    tuple[list[str], list[str]]
        Tuple of (available_tools, missing_tools) for required tools.
    """
    with span("tools.check_required"):
        available = []
        missing = []

        for tool in REQUIRED_TOOLS:
            if check_tool(tool):
                available.append(tool)
            else:
                missing.append(tool)

        add_span_attributes(
            required_available=len(available),
            required_missing=len(missing),
        )

        return available, missing


def get_ggen_version() -> str | None:
    """Get installed ggen version.

    Returns
    -------
    str | None
        Version string (e.g., "5.0.2") or None if not found.
    """
    with span("tools.get_ggen_version"):
        try:
            from specify_cli.core.process import run

            if not check_tool("ggen"):
                add_span_attributes(ggen_available=False)
                return None

            output = run(["ggen", "--version"], capture=True, check=False)
            if output:
                # Parse "ggen 5.0.2" → "5.0.2"
                parts = output.strip().split()
                version = parts[-1] if parts else None
                add_span_attributes(ggen_version=version, ggen_available=True)
                metric_counter("tools.ggen_version.detected")(1)
                return version
        except Exception as e:
            add_span_attributes(ggen_error=str(e))
            metric_counter("tools.ggen_version.error")(1)
            return None

        return None


def get_tool_versions() -> dict[str, str | None]:
    """Get versions of common tools.

    Returns
    -------
    dict[str, str | None]
        Tool name to version mapping (None if not installed).
    """
    from specify_cli.core.process import run

    versions: dict[str, str | None] = {}

    version_commands = {
        "git": ["git", "--version"],
        "uv": ["uv", "--version"],
        "python": ["python", "--version"],
        "ggen": ["ggen", "--version"],
    }

    for tool, cmd in version_commands.items():
        if check_tool(tool):
            try:
                output = run(cmd, capture=True, check=False)
                if output:
                    # Extract version string
                    versions[tool] = output.strip().split()[-1] if output else None
                else:
                    versions[tool] = "installed"
            except Exception:
                versions[tool] = "installed (version unknown)"
        else:
            versions[tool] = None

    return versions
