"""
specify_cli.runtime.lint - Code Quality Runtime Operations
===========================================================

Runtime layer for code quality checks (ruff, mypy).

This module handles all subprocess execution for linting and type checking tools.
No business logic - all operations delegated from the ops layer with telemetry.

All functions:
- Use subprocess.run() with shell=False (safe subprocess calls)
- Validate paths before operations
- Handle errors with proper context
- Record OpenTelemetry spans and metrics
- Support structured logging and JSON output

Install dependencies via:
    uv sync --group dev
"""

from __future__ import annotations

import json
import subprocess
import time
from typing import TYPE_CHECKING, Any

from specify_cli.core.instrumentation import add_span_attributes, add_span_event
from specify_cli.core.process import run, which
from specify_cli.core.telemetry import metric_counter, metric_histogram, span

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

__all__ = [
    "LintError",
    "is_mypy_available",
    "is_ruff_available",
    "run_mypy",
    "run_ruff_check",
    "run_ruff_format",
]


class LintError(Exception):
    """Lint operation error."""

    def __init__(self, message: str, command: list[str] | None = None) -> None:
        """Initialize lint error.

        Parameters
        ----------
        message : str
            Error message
        command : list[str] | None
            Command that failed
        """
        super().__init__(message)
        self.command = command


def is_ruff_available() -> bool:
    """Check if ruff is available.

    Returns
    -------
    bool
        True if ruff is installed and available.
    """
    with span("lint.check_ruff"):
        result = which("ruff") is not None
        add_span_event("lint.ruff_available", {"available": result})
        return result


def is_mypy_available() -> bool:
    """Check if mypy is available.

    Returns
    -------
    bool
        True if mypy is installed and available.
    """
    with span("lint.check_mypy"):
        result = which("mypy") is not None
        add_span_event("lint.mypy_available", {"available": result})
        return result


def run_ruff_check(  # noqa: PLR0912, PLR0915
    paths: Sequence[Path] | None = None,
    *,
    fix: bool = False,
    show_fixes: bool = False,
    output_format: str = "text",
) -> dict[str, Any]:
    """Run ruff check on specified paths.

    Parameters
    ----------
    paths : Sequence[Path] | None
        Paths to check. If None, checks current directory.
    fix : bool, optional
        Automatically fix violations. Default is False.
    show_fixes : bool, optional
        Show fixes that would be applied. Default is False.
    output_format : str, optional
        Output format: text, json, junit, github. Default is "text".

    Returns
    -------
    dict[str, Any]
        Result dictionary with keys:
        - success: bool - Whether check passed
        - violations: list - List of violations (if format=json)
        - output: str - Raw output
        - duration: float - Execution time in seconds

    Raises
    ------
    LintError
        If ruff is not available or execution fails unexpectedly.
    """
    if not is_ruff_available():
        raise LintError("ruff is not installed. Install with: uv sync --group dev")

    start_time = time.time()

    # Build command
    cmd = ["ruff", "check"]

    if fix:
        cmd.append("--fix")

    if show_fixes:
        cmd.append("--show-fixes")

    if output_format != "text":
        cmd.extend(["--output-format", output_format])

    # Add paths
    if paths:
        # Validate paths exist
        path_strs = []
        for path in paths:
            if not path.exists():
                raise LintError(f"Path does not exist: {path}")
            path_strs.append(str(path))
        cmd.extend(path_strs)
    else:
        cmd.append(".")

    with span(
        "lint.ruff_check",
        **{
            "lint.tool": "ruff",
            "lint.operation": "check",
            "lint.paths": str(paths) if paths else ".",
            "lint.fix": fix,
            "lint.format": output_format,
        },
    ):
        add_span_event(
            "lint.ruff_check.starting",
            {
                "command": " ".join(cmd),
                "paths": str(paths) if paths else ".",
                "fix": fix,
            },
        )

        try:
            # Run ruff check - capture output for parsing
            output = run(cmd, capture=True, check=False)

            duration = time.time() - start_time

            # Parse output based on format
            violations = []
            if output_format == "json" and output:
                try:
                    violations = json.loads(output)
                except json.JSONDecodeError:
                    violations = []

            # Success if no violations found
            success = len(violations) == 0 if output_format == "json" else not output

            # Record metrics
            if success:
                metric_counter("lint.ruff_check.success")(1)
            else:
                metric_counter("lint.ruff_check.violations")(1)

            metric_histogram("lint.ruff_check.duration")(duration)

            add_span_attributes(
                **{
                    "lint.success": success,
                    "lint.violation_count": len(violations),
                    "lint.duration": duration,
                }
            )

            add_span_event(
                "lint.ruff_check.completed",
                {
                    "success": success,
                    "violations": len(violations),
                    "duration": duration,
                },
            )

            return {  # noqa: TRY300
                "success": success,
                "violations": violations,
                "output": output or "",
                "duration": duration,
            }

        except subprocess.CalledProcessError as e:
            duration = time.time() - start_time

            metric_counter("lint.ruff_check.error")(1)
            metric_histogram("lint.ruff_check.duration")(duration)

            add_span_event(
                "lint.ruff_check.failed",
                {
                    "error": str(e),
                    "exit_code": e.returncode,
                    "duration": duration,
                },
            )

            # Ruff returns exit code 1 for violations, which is expected
            # Only raise error for unexpected failures
            if e.returncode not in [0, 1]:
                raise LintError(f"ruff check failed: {e}", cmd) from e

            # Return violations found
            return {
                "success": False,
                "violations": [],
                "output": e.stdout or "",
                "duration": duration,
            }

        except Exception as e:
            duration = time.time() - start_time
            metric_counter("lint.ruff_check.exception")(1)

            add_span_event(
                "lint.ruff_check.exception",
                {
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )

            raise LintError(f"ruff check failed: {e}", cmd) from e


def run_ruff_format(  # noqa: PLR0912
    paths: Sequence[Path] | None = None,
    *,
    check: bool = False,
    diff: bool = False,
) -> dict[str, Any]:
    """Run ruff format on specified paths.

    Parameters
    ----------
    paths : Sequence[Path] | None
        Paths to format. If None, formats current directory.
    check : bool, optional
        Check if files are formatted without modifying. Default is False.
    diff : bool, optional
        Show diff of formatting changes. Default is False.

    Returns
    -------
    dict[str, Any]
        Result dictionary with keys:
        - success: bool - Whether formatting passed/succeeded
        - modified_files: list - List of files that were/would be modified
        - output: str - Raw output
        - duration: float - Execution time in seconds

    Raises
    ------
    LintError
        If ruff is not available or execution fails unexpectedly.
    """
    if not is_ruff_available():
        raise LintError("ruff is not installed. Install with: uv sync --group dev")

    start_time = time.time()

    # Build command
    cmd = ["ruff", "format"]

    if check:
        cmd.append("--check")

    if diff:
        cmd.append("--diff")

    # Add paths
    if paths:
        # Validate paths exist
        path_strs = []
        for path in paths:
            if not path.exists():
                raise LintError(f"Path does not exist: {path}")
            path_strs.append(str(path))
        cmd.extend(path_strs)
    else:
        cmd.append(".")

    with span(
        "lint.ruff_format",
        **{
            "lint.tool": "ruff",
            "lint.operation": "format",
            "lint.paths": str(paths) if paths else ".",
            "lint.check": check,
            "lint.diff": diff,
        },
    ):
        add_span_event(
            "lint.ruff_format.starting",
            {
                "command": " ".join(cmd),
                "paths": str(paths) if paths else ".",
                "check": check,
            },
        )

        try:
            # Run ruff format - capture output for parsing
            output = run(cmd, capture=True, check=False)

            duration = time.time() - start_time

            # Parse output to find modified files
            modified_files = []
            if output:
                # Ruff format outputs "Would reformat: <file>" in check mode
                # or formats silently
                for line in output.splitlines():
                    if "Would reformat:" in line or "Reformatted" in line:
                        # Extract filename from output
                        parts = line.split(":", 1)
                        if len(parts) > 1:
                            modified_files.append(parts[1].strip())

            success = len(modified_files) == 0 if check else True

            # Record metrics
            if success:
                metric_counter("lint.ruff_format.success")(1)
            else:
                metric_counter("lint.ruff_format.changes_needed")(1)

            metric_histogram("lint.ruff_format.duration")(duration)

            add_span_attributes(
                **{
                    "lint.success": success,
                    "lint.modified_count": len(modified_files),
                    "lint.duration": duration,
                }
            )

            add_span_event(
                "lint.ruff_format.completed",
                {
                    "success": success,
                    "modified_files": len(modified_files),
                    "duration": duration,
                },
            )

            return {  # noqa: TRY300
                "success": success,
                "modified_files": modified_files,
                "output": output or "",
                "duration": duration,
            }

        except subprocess.CalledProcessError as e:
            duration = time.time() - start_time

            metric_counter("lint.ruff_format.error")(1)
            metric_histogram("lint.ruff_format.duration")(duration)

            add_span_event(
                "lint.ruff_format.failed",
                {
                    "error": str(e),
                    "exit_code": e.returncode,
                    "duration": duration,
                },
            )

            # Ruff returns exit code 1 when files need formatting in check mode
            if check and e.returncode == 1:
                return {
                    "success": False,
                    "modified_files": [],
                    "output": e.stdout or "",
                    "duration": duration,
                }

            raise LintError(f"ruff format failed: {e}", cmd) from e

        except Exception as e:
            duration = time.time() - start_time
            metric_counter("lint.ruff_format.exception")(1)

            add_span_event(
                "lint.ruff_format.exception",
                {
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )

            raise LintError(f"ruff format failed: {e}", cmd) from e


def run_mypy(  # noqa: PLR0912, PLR0915
    paths: Sequence[Path] | None = None,
    *,
    strict: bool = False,
    show_error_codes: bool = True,
    output_format: str = "text",
) -> dict[str, Any]:
    """Run mypy type checking on specified paths.

    Parameters
    ----------
    paths : Sequence[Path] | None
        Paths to type check. If None, checks current directory.
    strict : bool, optional
        Enable strict type checking mode. Default is False.
    show_error_codes : bool, optional
        Show error codes in output. Default is True.
    output_format : str, optional
        Output format: text, json. Default is "text".

    Returns
    -------
    dict[str, Any]
        Result dictionary with keys:
        - success: bool - Whether type checking passed
        - errors: list - List of type errors (if format=json)
        - output: str - Raw output
        - duration: float - Execution time in seconds

    Raises
    ------
    LintError
        If mypy is not available or execution fails unexpectedly.
    """
    if not is_mypy_available():
        raise LintError("mypy is not installed. Install with: uv sync --group dev")

    start_time = time.time()

    # Build command
    cmd = ["mypy"]

    if strict:
        cmd.append("--strict")

    if show_error_codes:
        cmd.append("--show-error-codes")

    if output_format == "json":
        cmd.append("--no-error-summary")
        # Note: mypy doesn't have native JSON output, we'll parse text output

    # Add paths
    if paths:
        # Validate paths exist
        path_strs = []
        for path in paths:
            if not path.exists():
                raise LintError(f"Path does not exist: {path}")
            path_strs.append(str(path))
        cmd.extend(path_strs)
    else:
        cmd.append(".")

    with span(
        "lint.mypy",
        **{
            "lint.tool": "mypy",
            "lint.operation": "type_check",
            "lint.paths": str(paths) if paths else ".",
            "lint.strict": strict,
            "lint.format": output_format,
        },
    ):
        add_span_event(
            "lint.mypy.starting",
            {
                "command": " ".join(cmd),
                "paths": str(paths) if paths else ".",
                "strict": strict,
            },
        )

        try:
            # Run mypy - capture output for parsing
            output = run(cmd, capture=True, check=False)

            duration = time.time() - start_time

            # Parse output to extract errors
            errors = []
            if output:
                # Parse mypy output format: file:line: error: message [error-code]
                for line in output.splitlines():
                    if ": error:" in line:
                        errors.append(line.strip())

            # Success if no errors found
            success = len(errors) == 0

            # Record metrics
            if success:
                metric_counter("lint.mypy.success")(1)
            else:
                metric_counter("lint.mypy.errors")(1)

            metric_histogram("lint.mypy.duration")(duration)

            add_span_attributes(
                **{
                    "lint.success": success,
                    "lint.error_count": len(errors),
                    "lint.duration": duration,
                }
            )

            add_span_event(
                "lint.mypy.completed",
                {
                    "success": success,
                    "errors": len(errors),
                    "duration": duration,
                },
            )

            return {  # noqa: TRY300
                "success": success,
                "errors": errors,
                "output": output or "",
                "duration": duration,
            }

        except subprocess.CalledProcessError as e:
            duration = time.time() - start_time

            metric_counter("lint.mypy.error")(1)
            metric_histogram("lint.mypy.duration")(duration)

            add_span_event(
                "lint.mypy.failed",
                {
                    "error": str(e),
                    "exit_code": e.returncode,
                    "duration": duration,
                },
            )

            # mypy returns exit code 1 for type errors, which is expected
            if e.returncode == 1:
                # Parse errors from output
                errors = []
                if e.stdout:
                    for line in e.stdout.splitlines():
                        if ": error:" in line:
                            errors.append(line.strip())

                return {
                    "success": False,
                    "errors": errors,
                    "output": e.stdout or "",
                    "duration": duration,
                }

            raise LintError(f"mypy failed: {e}", cmd) from e

        except Exception as e:
            duration = time.time() - start_time
            metric_counter("lint.mypy.exception")(1)

            add_span_event(
                "lint.mypy.exception",
                {
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )

            raise LintError(f"mypy failed: {e}", cmd) from e
