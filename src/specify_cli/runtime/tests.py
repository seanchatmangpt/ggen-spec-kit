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


def _build_pytest_command(kwargs: dict[str, Any]) -> list[str]:
    """Build pytest command with optional arguments."""
    cmd = ["pytest", "tests/", "-v"]

    # Add optional arguments from kwargs
    if kwargs.get("verbose"):
        cmd.append("-vv")
    if kwargs.get("quiet"):
        cmd.remove("-v")
        cmd.append("-q")
    if kwargs.get("failed_first"):
        cmd.append("--lf")
    if kwargs.get("parallel"):
        cmd.extend(["-n", "auto"])
    if kwargs.get("markers"):
        cmd.extend(["-m", str(kwargs["markers"])])

    # Add any additional pytest options
    known_options = {"verbose", "quiet", "failed_first", "parallel", "markers"}
    for key, value in kwargs.items():
        if key not in known_options:
            if isinstance(value, bool) and value:
                cmd.append(f"--{key}")
            elif not isinstance(value, bool) and value is not None:
                cmd.extend([f"--{key}", str(value)])

    return cmd


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
            # Build pytest command
            cmd = _build_pytest_command(kwargs)

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
            # Build pytest coverage command
            cmd = ["pytest", "--cov=src/specify_cli", "--cov-report=term-missing"]

            # Add optional coverage arguments
            if kwargs.get("html"):
                cmd.append("--cov-report=html:reports/coverage")
            if kwargs.get("xml"):
                cmd.append("--cov-report=xml")
            if kwargs.get("json"):
                cmd.append("--cov-report=json")
            if kwargs.get("fail_under"):
                cmd.extend(["--cov-fail-under", str(kwargs["fail_under"])])

            # Add test directory (default to tests/)
            test_dir = kwargs.get("test_dir", "tests/")
            cmd.append(test_dir)

            # Add any additional pytest options
            for key, value in kwargs.items():
                if key not in ("html", "xml", "json", "fail_under", "test_dir"):
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
            # Build comprehensive CI test command
            # Runs all tests with coverage, strict mode, and CI-friendly output
            cmd = [
                "pytest",
                "tests/",
                "-v",
                "--cov=src/specify_cli",
                "--cov-report=term-missing",
                "--cov-report=xml",
                "--tb=short",
                "--strict-markers",
            ]

            # Add fail-under threshold for CI (default 80%)
            fail_under = kwargs.get("fail_under", 80)
            cmd.extend(["--cov-fail-under", str(fail_under)])

            # Add parallel execution for faster CI
            if kwargs.get("parallel", True):
                cmd.extend(["-n", "auto"])

            # Add random order for test independence
            if kwargs.get("random_order", True):
                cmd.append("--random-order")

            # Add any additional pytest options
            for key, value in kwargs.items():
                if key not in ("fail_under", "parallel", "random_order"):
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
