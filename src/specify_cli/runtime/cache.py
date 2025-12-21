"""
specify_cli.runtime.cache
================================

Runtime layer for Cache management and operations.

This module handles all subprocess execution, file I/O, and external tool integration.
No business logic - all operations delegated from the ops layer with telemetry.

All functions:
- Use subprocess.run() with shell=False (safe subprocess calls)
- Validate paths before operations
- Handle errors with proper context
- Record OpenTelemetry spans and metrics
- Support structured logging and JSON output

Install dependencies via:
    uv sync --group cache
"""

from __future__ import annotations

__all__ = []
