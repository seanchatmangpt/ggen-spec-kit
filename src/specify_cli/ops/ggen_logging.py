"""
specify_cli.ops.ggen_logging - Structured JSON Logging for ggen sync
====================================================================

Structured JSON logging for ggen operations (Phase 2 observability).

Implements comprehensive JSON logging for audit trails, debugging,
and operational monitoring.

Key Features:
- Structured JSON output with context
- Log levels (debug, info, warning, error, critical)
- Operation tracing with IDs
- Performance metrics (duration, rate)
- Searchable log format

Examples:
    >>> from specify_cli.ops.ggen_logging import GgenLogger
    >>> logger = GgenLogger("output/")
    >>> logger.info(\"Starting sync\", operation=\"sync\", file_count=10)
    >>> logger.record_duration(\"transformation\", 1.23)

See Also:
    - specify_cli.core.telemetry : OpenTelemetry spans
    - docs/GGEN_SYNC_OPERATIONAL_RUNBOOKS.md : Logging guidelines

Notes:
    JSON format enables machine parsing for metrics/monitoring.
    Logs written to .ggen-logs/ directory.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

__all__ = [
    "GgenLogger",
    "LogEntry",
]


@dataclass
class LogEntry:
    """Structured log entry.

    Attributes
    ----------
    timestamp : str
        ISO format timestamp.
    level : str
        Log level (debug, info, warning, error, critical).
    message : str
        Log message.
    context : dict[str, Any]
        Additional context fields.
    """

    timestamp: str
    level: str
    message: str
    context: dict[str, Any]


class GgenLogger:
    """Structured JSON logger for ggen operations.

    Writes JSON-formatted logs for operational monitoring and debugging.

    Parameters
    ----------
    output_dir : str | Path
        Output directory for sync.
    """

    def __init__(self, output_dir: str | Path) -> None:
        """Initialize logger.

        Parameters
        ----------
        output_dir : str | Path
            Target output directory.
        """
        self.output_dir = Path(output_dir)
        self.logs_dir = self.output_dir / ".ggen-logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Current session log file
        timestamp = datetime.now(tz=UTC).strftime("%Y%m%d_%H%M%S")
        self.log_file = self.logs_dir / f"sync_{timestamp}.jsonl"

    def debug(self, message: str, **context: Any) -> None:
        """Log debug message.

        Parameters
        ----------
        message : str
            Log message.
        **context : Any
            Context fields to include.
        """
        self._write_log("debug", message, context)

    def info(self, message: str, **context: Any) -> None:
        """Log info message.

        Parameters
        ----------
        message : str
            Log message.
        **context : Any
            Context fields to include.
        """
        self._write_log("info", message, context)

    def warning(self, message: str, **context: Any) -> None:
        """Log warning message.

        Parameters
        ----------
        message : str
            Log message.
        **context : Any
            Context fields to include.
        """
        self._write_log("warning", message, context)

    def error(self, message: str, **context: Any) -> None:
        """Log error message.

        Parameters
        ----------
        message : str
            Log message.
        **context : Any
            Context fields to include.
        """
        self._write_log("error", message, context)

    def critical(self, message: str, **context: Any) -> None:
        """Log critical message.

        Parameters
        ----------
        message : str
            Log message.
        **context : Any
            Context fields to include.
        """
        self._write_log("critical", message, context)

    def record_duration(self, operation: str, duration: float, **context: Any) -> None:
        """Record operation duration.

        Parameters
        ----------
        operation : str
            Operation name.
        duration : float
            Duration in seconds.
        **context : Any
            Additional context.
        """
        ctx = {"operation": operation, "duration_seconds": duration, **context}
        self.info(f"Operation completed: {operation}", **ctx)

    def record_file_processed(
        self, file_path: str, size: int, duration: float, **context: Any
    ) -> None:
        """Record file processing.

        Parameters
        ----------
        file_path : str
            Output file path.
        size : int
            File size in bytes.
        duration : float
            Processing duration in seconds.
        **context : Any
            Additional context.
        """
        ctx = {
            "file": file_path,
            "size_bytes": size,
            "duration_seconds": duration,
            **context,
        }
        self.info(f"File processed: {file_path}", **ctx)

    def _write_log(self, level: str, message: str, context: dict[str, Any]) -> None:
        """Write log entry to file.

        Parameters
        ----------
        level : str
            Log level.
        message : str
            Log message.
        context : dict[str, Any]
            Context fields.
        """
        entry = LogEntry(
            timestamp=datetime.now(tz=UTC).isoformat(),
            level=level,
            message=message,
            context=context,
        )

        try:
            line = json.dumps(asdict(entry))
            self.log_file.write_text(
                self.log_file.read_text() + line + "\n",
                encoding="utf-8",
            )
        except Exception:
            # Graceful degradation - don't fail sync on logging error
            pass
