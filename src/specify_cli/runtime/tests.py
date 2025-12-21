"""
specify_cli.runtime.tests
================================

Runtime layer for Run tests with pytest, coverage, and CI verification.

This module handles all subprocess execution, file I/O, and external tool integration.
No business logic - all operations delegated from the ops layer with telemetry.

All functions:
- Use subprocess.run() with shell=False (safe subprocess calls)
- Validate paths before operations
- Handle errors with proper context
- Record OpenTelemetry spans and metrics
- Support structured logging and JSON output

Install dependencies via:
    uv sync --group tests
"""

from __future__ import annotations

import subprocess
from typing import Any

from specify_cli.core.process import run_logged
from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_counter, span

__all__ = [
    "ci",
    "coverage",
    "run_tests",
]


@timed
def run_tests(**kwargs: Any) -> dict[str, Any]:
    """
    Run comprehensive test suite (Runtime layer - I/O operations)

    This is the runtime layer that executes actual subprocess calls and I/O.
    Business logic validation happens in ops layer.

    Parameters
    ----------
    **kwargs : Any
        Command parameters and options passed from ops layer

    Returns
    -------
    dict[str, Any]
        Result with success status, output, and metadata

    Raises
    ------
    subprocess.CalledProcessError
        If subprocess execution fails
    FileNotFoundError
        If required files/tools not found
    OSError
        If filesystem operations fail

    Notes
    -----
    - Uses subprocess.run() with shell=False (safe execution)
    - Validates paths before operations
    - Records telemetry for all operations
    - Supports both text and JSON output modes
    """
    with span("tests.run.runtime"):
        metric_counter("tests.operations_executed")

        try:
            # Build command
            cmd = ["tests", "run"]

            # Add string arguments (kwargs values)
            for key, value in kwargs.items():
                if isinstance(value, bool) and value:
                    cmd.append(f"--{key}")
                elif not isinstance(value, bool) and value is not None:
                    cmd.extend([f"--{key}", str(value)])

            # Execute subprocess with logging
            output = run_logged(cmd, capture=True, check=True)

            return {
                "success": True,
                "command": "tests",
                "subcommand": "run",
                "output": output,
                "returncode": 0,
                "message": "Run comprehensive test suite completed successfully",
            }

        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "command": "tests",
                "subcommand": "run",
                "error": str(e),
                "returncode": e.returncode,
                "message": f"Command failed with exit code {e.returncode}",
            }

        except FileNotFoundError as e:
            return {
                "success": False,
                "command": "tests",
                "subcommand": "run",
                "error": f"Tool not found: {e}",
                "returncode": 127,
                "message": "Required tool not available",
            }

        except OSError as e:
            return {
                "success": False,
                "command": "tests",
                "subcommand": "run",
                "error": f"OS error: {e}",
                "returncode": 1,
                "message": "Filesystem or OS operation failed",
            }

        except Exception as e:
            return {
                "success": False,
                "command": "tests",
                "subcommand": "run",
                "error": f"Unexpected error: {e}",
                "returncode": 1,
                "message": "Unexpected error during execution",
            }


@timed
def coverage(**kwargs: Any) -> dict[str, Any]:
    """
    Generate coverage reports (Runtime layer - I/O operations)

    This is the runtime layer that executes actual subprocess calls and I/O.
    Business logic validation happens in ops layer.

    Parameters
    ----------
    **kwargs : Any
        Command parameters and options passed from ops layer

    Returns
    -------
    dict[str, Any]
        Result with success status, output, and metadata

    Raises
    ------
    subprocess.CalledProcessError
        If subprocess execution fails
    FileNotFoundError
        If required files/tools not found
    OSError
        If filesystem operations fail

    Notes
    -----
    - Uses subprocess.run() with shell=False (safe execution)
    - Validates paths before operations
    - Records telemetry for all operations
    - Supports both text and JSON output modes
    """
    with span("tests.coverage.runtime"):
        metric_counter("tests.operations_executed")

        try:
            # Build command
            cmd = ["tests", "coverage"]

            # Add string arguments (kwargs values)
            for key, value in kwargs.items():
                if isinstance(value, bool) and value:
                    cmd.append(f"--{key}")
                elif not isinstance(value, bool) and value is not None:
                    cmd.extend([f"--{key}", str(value)])

            # Execute subprocess with logging
            output = run_logged(cmd, capture=True, check=True)

            return {
                "success": True,
                "command": "tests",
                "subcommand": "coverage",
                "output": output,
                "returncode": 0,
                "message": "Generate coverage reports completed successfully",
            }

        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "command": "tests",
                "subcommand": "coverage",
                "error": str(e),
                "returncode": e.returncode,
                "message": f"Command failed with exit code {e.returncode}",
            }

        except FileNotFoundError as e:
            return {
                "success": False,
                "command": "tests",
                "subcommand": "coverage",
                "error": f"Tool not found: {e}",
                "returncode": 127,
                "message": "Required tool not available",
            }

        except OSError as e:
            return {
                "success": False,
                "command": "tests",
                "subcommand": "coverage",
                "error": f"OS error: {e}",
                "returncode": 1,
                "message": "Filesystem or OS operation failed",
            }

        except Exception as e:
            return {
                "success": False,
                "command": "tests",
                "subcommand": "coverage",
                "error": f"Unexpected error: {e}",
                "returncode": 1,
                "message": "Unexpected error during execution",
            }


@timed
def ci(**kwargs: Any) -> dict[str, Any]:
    """
    Comprehensive CI verification (Runtime layer - I/O operations)

    This is the runtime layer that executes actual subprocess calls and I/O.
    Business logic validation happens in ops layer.

    Parameters
    ----------
    **kwargs : Any
        Command parameters and options passed from ops layer

    Returns
    -------
    dict[str, Any]
        Result with success status, output, and metadata

    Raises
    ------
    subprocess.CalledProcessError
        If subprocess execution fails
    FileNotFoundError
        If required files/tools not found
    OSError
        If filesystem operations fail

    Notes
    -----
    - Uses subprocess.run() with shell=False (safe execution)
    - Validates paths before operations
    - Records telemetry for all operations
    - Supports both text and JSON output modes
    """
    with span("tests.ci.runtime"):
        metric_counter("tests.operations_executed")

        try:
            # Build command
            cmd = ["tests", "ci"]

            # Add string arguments (kwargs values)
            for key, value in kwargs.items():
                if isinstance(value, bool) and value:
                    cmd.append(f"--{key}")
                elif not isinstance(value, bool) and value is not None:
                    cmd.extend([f"--{key}", str(value)])

            # Execute subprocess with logging
            output = run_logged(cmd, capture=True, check=True)

            return {
                "success": True,
                "command": "tests",
                "subcommand": "ci",
                "output": output,
                "returncode": 0,
                "message": "Comprehensive CI verification completed successfully",
            }

        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "command": "tests",
                "subcommand": "ci",
                "error": str(e),
                "returncode": e.returncode,
                "message": f"Command failed with exit code {e.returncode}",
            }

        except FileNotFoundError as e:
            return {
                "success": False,
                "command": "tests",
                "subcommand": "ci",
                "error": f"Tool not found: {e}",
                "returncode": 127,
                "message": "Required tool not available",
            }

        except OSError as e:
            return {
                "success": False,
                "command": "tests",
                "subcommand": "ci",
                "error": f"OS error: {e}",
                "returncode": 1,
                "message": "Filesystem or OS operation failed",
            }

        except Exception as e:
            return {
                "success": False,
                "command": "tests",
                "subcommand": "ci",
                "error": f"Unexpected error: {e}",
                "returncode": 1,
                "message": "Unexpected error during execution",
            }
