"""
specify_cli.runtime.lint
===============================

Runtime layer for Code quality checks (ruff, black, mypy).

This module handles all subprocess execution, file I/O, and external tool integration.
No business logic - all operations delegated from the ops layer with telemetry.

All functions:
- Use subprocess.run() with shell=False (safe subprocess calls)
- Validate paths before operations
- Handle errors with proper context
- Record OpenTelemetry spans and metrics
- Support structured logging and JSON output

Install dependencies via:
    uv sync --group lint
"""

from __future__ import annotations

__all__ = []
