"""
specify_cli.ops.check - Tool Checking Operations
=================================================

Business logic for checking installed tools and dependencies.

This module contains pure business logic for validating that required
and optional tools are available in the system.

Key Features
-----------
* **Tool Validation**: Check required and optional tools
* **Version Detection**: Get installed tool versions
* **Health Checks**: Validate tool functionality

Design Principles
----------------
* Pure functions (same input → same output)
* No direct I/O (delegates to runtime layer)
* Fully testable with mocked runtime
* Returns structured results for commands to format

Examples
--------
    >>> from specify_cli.ops.check import check_all_tools
    >>>
    >>> result = check_all_tools()
    >>> for tool in result.available:
    ...     print(f"{tool}: available")

See Also
--------
- :mod:`specify_cli.runtime.tools` : Tool detection runtime
- :mod:`specify_cli.commands.check` : CLI command handler
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from specify_cli.core.instrumentation import add_span_attributes, add_span_event
from specify_cli.core.telemetry import metric_counter, metric_histogram, span
from specify_cli.runtime import tools

__all__ = [
    "check_all_tools",
    "check_tool",
    "get_tool_status",
    "CheckResult",
    "ToolStatus",
]


@dataclass
class ToolStatus:
    """Status of a single tool."""

    name: str
    available: bool
    required: bool
    path: str | None = None
    version: str | None = None
    error: str | None = None


@dataclass
class CheckResult:
    """Result of tool checking operation."""

    success: bool  # True if all required tools are available
    available: list[ToolStatus] = field(default_factory=list)
    missing: list[ToolStatus] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    duration: float = 0.0

    @property
    def all_required_available(self) -> bool:
        """Check if all required tools are available."""
        return not any(t.required for t in self.missing)

    @property
    def tool_count(self) -> dict[str, int]:
        """Get counts of available and missing tools."""
        return {
            "available": len(self.available),
            "missing": len(self.missing),
            "required_missing": sum(1 for t in self.missing if t.required),
        }


def check_tool(name: str, *, required: bool = False) -> ToolStatus:
    """Check if a specific tool is available.

    Parameters
    ----------
    name : str
        Name of the tool to check.
    required : bool, optional
        Whether this tool is required.

    Returns
    -------
    ToolStatus
        Status of the tool.
    """
    with span("ops.check.tool", tool=name, required=required):
        status = ToolStatus(name=name, available=False, required=required)

        try:
            path = tools.which_tool(name)
            if path:
                status.available = True
                status.path = str(path)
                add_span_attributes(tool_path=str(path), tool_available=True)
            else:
                add_span_attributes(tool_available=False)
        except Exception as e:
            status.error = str(e)
            add_span_attributes(tool_error=str(e))

        return status


def get_tool_status(name: str) -> ToolStatus:
    """Get detailed status of a tool including version.

    Parameters
    ----------
    name : str
        Name of the tool.

    Returns
    -------
    ToolStatus
        Detailed tool status.
    """
    with span("ops.check.tool_status", tool=name):
        # First check availability
        is_required = name in tools.REQUIRED_TOOLS
        status = check_tool(name, required=is_required)

        # If available, try to get version
        if status.available:
            versions = tools.get_tool_versions()
            status.version = versions.get(name)

        return status


def check_all_tools(
    *,
    include_optional: bool = True,
    additional_tools: list[str] | None = None,
) -> CheckResult:
    """Check all required and optional tools.

    Parameters
    ----------
    include_optional : bool, optional
        Include optional tools in check. Default is True.
    additional_tools : list[str], optional
        Additional tools to check.

    Returns
    -------
    CheckResult
        Result with all tool statuses.
    """
    start_time = time.time()

    with span("ops.check.all_tools", include_optional=include_optional):
        result = CheckResult(success=False)

        # Collect tools to check
        tools_to_check: list[tuple[str, bool]] = []

        # Required tools
        for tool in tools.REQUIRED_TOOLS:
            tools_to_check.append((tool, True))

        # Optional tools
        if include_optional:
            for tool in tools.OPTIONAL_TOOLS:
                tools_to_check.append((tool, False))

        # Additional tools
        if additional_tools:
            for tool in additional_tools:
                if tool not in [t[0] for t in tools_to_check]:
                    tools_to_check.append((tool, False))

        add_span_event("check.starting", {"tools_count": len(tools_to_check)})

        # Check each tool
        for name, required in tools_to_check:
            status = check_tool(name, required=required)

            if status.available:
                result.available.append(status)
            else:
                result.missing.append(status)

        # Determine success (all required tools available)
        result.success = result.all_required_available
        result.duration = time.time() - start_time

        # Record metrics
        metric_counter("ops.check.completed")(1)
        metric_histogram("ops.check.duration")(result.duration)

        counts = result.tool_count
        add_span_attributes(
            tools_available=counts["available"],
            tools_missing=counts["missing"],
            required_missing=counts["required_missing"],
            check_success=result.success,
        )

        add_span_event(
            "check.completed",
            {
                "success": result.success,
                "available": counts["available"],
                "missing": counts["missing"],
            },
        )

        return result


def get_environment_info() -> dict[str, Any]:
    """Get environment information for diagnostics.

    Returns
    -------
    dict[str, Any]
        Environment information.
    """
    import os
    import platform
    import sys

    from specify_cli.core.config import get_config

    config = get_config()

    return {
        "python": {
            "version": sys.version,
            "executable": sys.executable,
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "specify": {
            "cache_dir": str(config.cache_dir),
            "config_dir": str(config.config_dir),
            "otel_enabled": config.otel_enabled,
        },
        "environment": {
            "PATH": os.getenv("PATH", "")[:200] + "...",  # Truncate long PATH
            "VIRTUAL_ENV": os.getenv("VIRTUAL_ENV", ""),
        },
    }
