"""
specify_cli.ops.ggen_timeout_config - Timeout Configuration Support
===================================================================

Configuration support for SPARQL query timeouts (Phase 2 flexibility).

Allows per-transformation timeout configuration via ggen.toml,
replacing fixed 60-second default with customizable timeouts.

Key Features:
- Per-transformation timeout configuration
- Global default timeout setting
- Validation of timeout values
- Clear error messages for timeout violations

Examples:
    >>> from specify_cli.ops.ggen_timeout_config import parse_timeout
    >>> timeout = parse_timeout(\"30s\")  # 30 seconds
    >>> timeout = parse_timeout(\"5m\")   # 5 minutes
    >>> timeout = parse_timeout(120)     # 120 seconds

See Also:
    - specify_cli.ops.ggen_timeout : Timeout execution
    - docs/GGEN_SYNC_OPERATIONAL_RUNBOOKS.md : Configuration guide

Notes:
    Supports: 30s, 5m, 300 (seconds).
    Default: 60 seconds if not specified.
"""

from __future__ import annotations

import re
from typing import Any

__all__ = [
    "DEFAULT_TIMEOUT",
    "get_transformation_timeout",
    "parse_timeout",
]

# Default timeout in seconds
DEFAULT_TIMEOUT: int = 60


def parse_timeout(timeout_spec: str | int | None) -> int:
    """Parse timeout specification to seconds.

    Parameters
    ----------
    timeout_spec : str | int | None
        Timeout specification. Can be:
        - int: seconds directly (e.g., 120)
        - str: with unit suffix (e.g., "30s", "5m")
        - None: uses DEFAULT_TIMEOUT

    Returns
    -------
    int
        Timeout in seconds.

    Raises
    ------
    ValueError
        If timeout format invalid or value negative.
    """
    if timeout_spec is None:
        return DEFAULT_TIMEOUT

    # Handle integer directly
    if isinstance(timeout_spec, int):
        if timeout_spec <= 0:
            raise ValueError(f"Timeout must be positive: {timeout_spec}")
        return timeout_spec

    # Handle string with units
    if isinstance(timeout_spec, str):
        timeout_spec = timeout_spec.strip()

        # Check for negative values
        if timeout_spec.startswith("-"):
            raise ValueError(f"Timeout must be positive: {timeout_spec}")

        # Try seconds suffix
        match = re.match(r"^(\d+)\s*s$", timeout_spec, re.IGNORECASE)
        if match:
            seconds = int(match.group(1))
            if seconds <= 0:
                raise ValueError(f"Timeout must be positive: {timeout_spec}")
            return seconds

        # Try minutes suffix
        match = re.match(r"^(\d+)\s*m$", timeout_spec, re.IGNORECASE)
        if match:
            minutes = int(match.group(1))
            if minutes <= 0:
                raise ValueError(f"Timeout must be positive: {timeout_spec}")
            return minutes * 60

        # Try plain number
        try:
            seconds = int(timeout_spec)
        except ValueError as e:
            raise ValueError(
                f"Invalid timeout format: {timeout_spec}. Use '30s', '5m', or plain seconds."
            ) from e

        if seconds <= 0:
            raise ValueError(f"Timeout must be positive: {timeout_spec}")
        return seconds

    raise ValueError(f"Timeout must be int, str, or None, got {type(timeout_spec).__name__}")


def get_transformation_timeout(
    transformation: dict[str, Any],
    global_default: int | None = None,
) -> int:
    """Get timeout for a transformation.

    Checks transformation-specific timeout first, then global default,
    then uses DEFAULT_TIMEOUT.

    Parameters
    ----------
    transformation : dict[str, Any]
        Transformation configuration from ggen.toml.
    global_default : int | None
        Global default timeout in seconds.

    Returns
    -------
    int
        Timeout in seconds.

    Raises
    ------
    ValueError
        If timeout value invalid.
    """
    # Check transformation-specific timeout
    if "timeout" in transformation:
        return parse_timeout(transformation["timeout"])

    # Check global default
    if global_default is not None:
        return parse_timeout(global_default)

    # Use built-in default
    return DEFAULT_TIMEOUT
