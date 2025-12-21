"""
specify_cli.ops.version - Version Operations
=============================================

Business logic for version checking and update detection.

This module contains pure business logic for checking the current
version and detecting available updates.

Key Features
-----------
* **Version Detection**: Get current installed version
* **Update Checking**: Check for available updates
* **Release Info**: Get latest release information

Design Principles
----------------
* Pure functions (same input → same output)
* No direct I/O (delegates to runtime layer)
* Fully testable with mocked runtime
* Returns structured results for commands to format

Examples
--------
    >>> from specify_cli.ops.version import get_version_info
    >>>
    >>> info = get_version_info()
    >>> print(f"Current: {info.current_version}")
    >>> if info.update_available:
    ...     print(f"Update available: {info.latest_version}")

See Also
--------
- :mod:`specify_cli.runtime.github` : GitHub API operations
- :mod:`specify_cli.commands.version` : CLI command handler
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from specify_cli.core.instrumentation import add_span_attributes, add_span_event
from specify_cli.core.telemetry import metric_counter, span
from specify_cli.runtime import github

__all__ = [
    "get_version_info",
    "check_for_updates",
    "get_current_version",
    "VersionInfo",
]


# Version is managed in pyproject.toml and imported
try:
    from importlib.metadata import version as get_pkg_version

    CURRENT_VERSION = get_pkg_version("specify-cli")
except Exception:
    CURRENT_VERSION = "0.0.0"


@dataclass
class VersionInfo:
    """Version information result."""

    current_version: str
    latest_version: str | None = None
    update_available: bool = False
    release_url: str | None = None
    release_notes: str | None = None
    check_time: float = 0.0
    error: str | None = None


def get_current_version() -> str:
    """Get the current installed version.

    Returns
    -------
    str
        Current version string.
    """
    return CURRENT_VERSION


def _parse_version(version: str) -> tuple[int, ...]:
    """Parse version string to tuple for comparison.

    Parameters
    ----------
    version : str
        Version string (e.g., "1.2.3", "v1.2.3").

    Returns
    -------
    tuple[int, ...]
        Version components as integers.
    """
    # Remove 'v' prefix if present
    version = version.lstrip("v")

    # Split and convert to integers
    try:
        parts = version.split(".")
        return tuple(int(p.split("-")[0].split("+")[0]) for p in parts)
    except (ValueError, IndexError):
        return (0,)


def _is_newer_version(current: str, latest: str) -> bool:
    """Check if latest version is newer than current.

    Parameters
    ----------
    current : str
        Current version string.
    latest : str
        Latest version string.

    Returns
    -------
    bool
        True if latest is newer than current.
    """
    current_parts = _parse_version(current)
    latest_parts = _parse_version(latest)

    # Pad shorter tuple with zeros
    max_len = max(len(current_parts), len(latest_parts))
    current_parts = current_parts + (0,) * (max_len - len(current_parts))
    latest_parts = latest_parts + (0,) * (max_len - len(latest_parts))

    return latest_parts > current_parts


def check_for_updates(
    *,
    owner: str = "github",
    repo: str = "spec-kit",
    token: str | None = None,
) -> VersionInfo:
    """Check for available updates.

    Parameters
    ----------
    owner : str, optional
        GitHub repository owner.
    repo : str, optional
        GitHub repository name.
    token : str, optional
        GitHub token for authentication.

    Returns
    -------
    VersionInfo
        Version information with update status.
    """
    start_time = time.time()
    info = VersionInfo(current_version=CURRENT_VERSION)

    with span("ops.version.check_updates", owner=owner, repo=repo):
        add_span_event("version.checking", {"current": CURRENT_VERSION})

        try:
            # Fetch latest release
            release_data = github.fetch_latest_release(
                owner=owner,
                repo=repo,
                token=token,
            )

            info.latest_version = release_data.get("tag_name", "").lstrip("v")
            info.release_url = release_data.get("html_url")
            info.release_notes = release_data.get("body", "")

            # Compare versions
            if info.latest_version:
                info.update_available = _is_newer_version(
                    CURRENT_VERSION, info.latest_version
                )

            info.check_time = time.time() - start_time

            # Record metrics
            metric_counter("ops.version.checked")(1)
            if info.update_available:
                metric_counter("ops.version.update_available")(1)

            add_span_attributes(
                latest_version=info.latest_version or "",
                update_available=info.update_available,
            )

            add_span_event(
                "version.checked",
                {
                    "current": CURRENT_VERSION,
                    "latest": info.latest_version or "",
                    "update_available": info.update_available,
                },
            )

        except Exception as e:
            info.error = str(e)
            info.check_time = time.time() - start_time

            metric_counter("ops.version.check_error")(1)
            add_span_event("version.check_failed", {"error": str(e)})

        return info


def get_version_info(
    *,
    check_updates: bool = True,
    token: str | None = None,
) -> VersionInfo:
    """Get comprehensive version information.

    Parameters
    ----------
    check_updates : bool, optional
        Whether to check for updates. Default is True.
    token : str, optional
        GitHub token for update checking.

    Returns
    -------
    VersionInfo
        Version information.
    """
    with span("ops.version.get_info", check_updates=check_updates):
        if check_updates:
            return check_for_updates(token=token)
        else:
            return VersionInfo(current_version=CURRENT_VERSION)


def get_build_info() -> dict[str, Any]:
    """Get build information for diagnostics.

    Returns
    -------
    dict[str, Any]
        Build information including version and dependencies.
    """
    import sys

    info: dict[str, Any] = {
        "version": CURRENT_VERSION,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": sys.platform,
    }

    # Try to get key dependency versions
    try:
        from importlib.metadata import version as get_pkg_version

        info["dependencies"] = {
            "typer": get_pkg_version("typer"),
            "rich": get_pkg_version("rich"),
            "httpx": get_pkg_version("httpx"),
        }
    except Exception:
        info["dependencies"] = {}

    # Check OTEL availability
    try:
        from specify_cli.core.telemetry import OTEL_AVAILABLE

        info["otel_available"] = OTEL_AVAILABLE
    except Exception:
        info["otel_available"] = False

    return info
