"""
specify_cli.core.process - Process Execution and Management
============================================================

Thin subprocess wrapper with DRY/QUIET flags and comprehensive telemetry.

This module provides a streamlined interface for executing external commands
with built-in support for dry-run mode, quiet execution, and comprehensive
OpenTelemetry instrumentation for monitoring process execution.

Key Features
-----------
* **Simple Interface**: Clean API for command execution
* **Dry Run Support**: Preview commands without execution (SPECIFY_DRY=1)
* **Quiet Mode**: Suppress output for automated execution (SPECIFY_QUIET)
* **Telemetry Integration**: Full OpenTelemetry instrumentation
* **Error Handling**: Comprehensive error tracking and metrics
* **Path Resolution**: Executable location utilities
* **Security-First**: List-based commands only (no shell=True)

Available Functions
------------------
- **run()**: Execute command with optional output capture
- **run_logged()**: Execute command with logging and display
- **which()**: Find executable in PATH with telemetry

Environment Variables
--------------------
SPECIFY_DRY : str, optional
    Set to "1" to enable dry-run mode (commands are displayed but not executed)
SPECIFY_QUIET : str, optional
    Set to any value to suppress command output

Examples
--------
    >>> from specify_cli.core.process import run, run_logged, which
    >>>
    >>> # Basic command execution
    >>> run(["python", "--version"])
    >>>
    >>> # Capture output
    >>> output = run(["echo", "hello"], capture=True)
    >>>
    >>> # Logged execution with display
    >>> run_logged(["ls", "-la"])
    >>>
    >>> # Find executable
    >>> python_path = which("python")

See Also
--------
- :mod:`specify_cli.core.telemetry` : Telemetry and observability
- :mod:`specify_cli.core.semconv` : Semantic conventions
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import time
from typing import TYPE_CHECKING, Any

from .instrumentation import add_span_attributes, add_span_event
from .shell import colour
from .telemetry import metric_counter, metric_histogram, span

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

__all__ = ["run", "run_command", "run_logged", "which"]

_log = logging.getLogger("specify_cli.process")


def _to_str(cmd: str | Sequence[str]) -> str:
    """Convert command to string for display."""
    return cmd if isinstance(cmd, str) else " ".join(cmd)


def _to_list(cmd: str | Sequence[str]) -> list[str]:
    """Convert command to list for subprocess."""
    if isinstance(cmd, str):
        import shlex

        return shlex.split(cmd)
    return list(cmd)


def run(
    cmd: str | Sequence[str],
    *,
    capture: bool = False,
    cwd: Path | None = None,
    check: bool = True,
    env: dict[str, str] | None = None,
) -> str | None:
    """
    Execute a command with comprehensive OTEL instrumentation.

    Security-first: Uses list-based subprocess execution (no shell=True).

    Parameters
    ----------
    cmd : str | Sequence[str]
        Command to execute. If string, will be split using shlex.
    capture : bool, optional
        If True, capture and return stdout. Default is False.
    cwd : Path, optional
        Working directory for command execution.
    check : bool, optional
        If True, raise CalledProcessError on non-zero exit. Default is True.
    env : dict[str, str], optional
        Environment variables to set for the command.

    Returns
    -------
    str | None
        Captured stdout if capture=True, else None.

    Raises
    ------
    subprocess.CalledProcessError
        If check=True and command returns non-zero exit code.
    """
    cmd_list = _to_list(cmd)
    cmd_str = _to_str(cmd_list)
    start_time = time.time()

    # Handle dry run mode
    if os.getenv("SPECIFY_DRY") == "1":
        colour(f"[dry] {cmd_str}", "yellow")
        metric_counter("process.dry_runs")(1)
        return ""

    # Build subprocess kwargs
    kw: dict[str, Any] = {
        "cwd": str(cwd) if cwd else None,
        "text": True,
        "check": check,
    }

    if capture or os.getenv("SPECIFY_QUIET"):
        kw["stdout"] = subprocess.PIPE
        kw["stderr"] = subprocess.STDOUT

    if env:
        # Merge with current environment
        full_env = os.environ.copy()
        full_env.update(env)
        kw["env"] = full_env

    with span(
        "process.execution",
        **{
            "process.command": cmd_str,
            "process.working_directory": str(cwd) if cwd else os.getcwd(),
            "process.capture": capture,
            "process.quiet": bool(os.getenv("SPECIFY_QUIET")),
        },
    ):
        add_span_event(
            "process.starting",
            {
                "command": cmd_str,
                "working_directory": str(cwd) if cwd else os.getcwd(),
                "capture_output": capture,
            },
        )

        try:
            # SECURITY: Always use list-based execution, never shell=True
            res = subprocess.run(cmd_list, check=False, **kw)

            duration = time.time() - start_time

            # Record success metrics
            metric_counter("process.executions.success")(1)
            metric_histogram("process.execution.duration")(duration)

            add_span_attributes(
                **{
                    "process.exit_code": res.returncode,
                    "process.duration": duration,
                }
            )

            add_span_event(
                "process.completed",
                {
                    "exit_code": res.returncode,
                    "duration": duration,
                    "output_captured": bool(res.stdout),
                },
            )

            return res.stdout if capture else None

        except subprocess.CalledProcessError as e:
            duration = time.time() - start_time

            # Record failure metrics
            metric_counter("process.executions.failed")(1)
            metric_histogram("process.execution.duration")(duration)

            add_span_attributes(
                **{
                    "process.exit_code": e.returncode,
                    "process.duration": duration,
                }
            )

            add_span_event(
                "process.failed",
                {
                    "exit_code": e.returncode,
                    "duration": duration,
                    "error": str(e),
                },
            )

            # Re-raise the exception
            raise

        except Exception as e:
            duration = time.time() - start_time

            metric_counter("process.executions.error")(1)

            add_span_event(
                "process.error",
                {
                    "duration": duration,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )

            raise


def run_logged(
    cmd: str | Sequence[str],
    *,
    label: str = "",
    capture: bool = False,
    check: bool = True,
    cwd: Path | None = None,
) -> str | None:
    """
    Execute a command with logging and telemetry.

    Parameters
    ----------
    cmd : str | Sequence[str]
        Command to execute.
    label : str, optional
        Label to display before running command.
    capture : bool, optional
        If True, capture and return stdout.
    check : bool, optional
        If True, raise on non-zero exit.
    cwd : Path, optional
        Working directory.

    Returns
    -------
    str | None
        Captured output if capture=True, else None.
    """
    cmd_str = _to_str(cmd)

    with span("process.logged_execution", command=cmd_str):
        if label:
            colour(f"-> {label}", "cyan")
        else:
            colour(f"$ {cmd_str}", "cyan")

        add_span_event("process.logged.starting", {"command": cmd_str})
        metric_counter("process.logged_executions")(1)

        try:
            result = run(cmd, capture=capture, check=check, cwd=cwd)
            add_span_event("process.logged.completed", {"command": cmd_str})
            return result

        except Exception as e:
            add_span_event(
                "process.logged.failed",
                {
                    "command": cmd_str,
                    "error": str(e),
                },
            )
            raise


def which(binary: str) -> str | None:
    """
    Find executable in PATH with telemetry tracking.

    Parameters
    ----------
    binary : str
        Name of the executable to find.

    Returns
    -------
    str | None
        Full path to the executable, or None if not found.
    """
    with span("process.which", binary=binary):
        add_span_event("process.which.starting", {"binary": binary})

        result = shutil.which(binary)

        # Record metrics
        if result:
            metric_counter("process.which.found")(1)
            add_span_attributes(
                executable_path=result,
                binary_found=True,
            )
            add_span_event(
                "process.which.found",
                {
                    "binary": binary,
                    "path": result,
                },
            )
        else:
            metric_counter("process.which.not_found")(1)
            add_span_attributes(binary_found=False)
            add_span_event("process.which.not_found", {"binary": binary})

        return result


# Backward compatibility alias
def run_command(
    cmd: list[str],
    check_return: bool = True,
    capture: bool = False,
    shell: bool = False,  # DEPRECATED: Ignored for security
    cwd: Path | None = None,
) -> str | None:
    """
    Execute a command and optionally capture output.

    .. deprecated::
        The `shell` parameter is deprecated and ignored for security.
        Use `run()` instead.

    Parameters
    ----------
    cmd : list[str]
        Command as list of strings.
    check_return : bool, optional
        Raise CalledProcessError if exit code != 0. Default is True.
    capture : bool, optional
        If True, return stdout; if False, stream to console.
    shell : bool, optional
        DEPRECATED: Ignored for security reasons.
    cwd : Path, optional
        Working directory for command execution.

    Returns
    -------
    str | None
        Captured output if capture=True, else None.
    """
    if shell:
        _log.warning(
            "shell=True is deprecated and ignored for security. "
            "Command will be executed without shell."
        )

    return run(cmd, capture=capture, check=check_return, cwd=cwd)
