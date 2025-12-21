"""
specify_cli.runtime.mermaid
==================================

Runtime layer for Mermaid diagram generation from code/specs.

This module handles all subprocess execution, file I/O, and external tool integration.
No business logic - all operations delegated from the ops layer with telemetry.

All functions:
- Use subprocess.run() with shell=False (safe subprocess calls)
- Validate paths before operations
- Handle errors with proper context
- Record OpenTelemetry spans and metrics
- Support structured logging and JSON output

Install dependencies via:
    uv sync --group mermaid
"""

from __future__ import annotations

__all__ = []
