"""
specify_cli.runtime.build
================================

Runtime layer for Build wheels, sdists, and executables using PyInstaller.

This module handles all subprocess execution, file I/O, and external tool integration.
No business logic - all operations delegated from the ops layer with telemetry.

All functions:
- Use subprocess.run() with shell=False (safe subprocess calls)
- Validate paths before operations
- Handle errors with proper context
- Record OpenTelemetry spans and metrics
- Support structured logging and JSON output

Install dependencies via:
    uv sync --group build
"""

from __future__ import annotations

import subprocess
from typing import Any

from specify_cli.core.process import run_logged
from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_counter, span

__all__ = [
    "dist",
    "dogfood",
    "exe",
    "spec",
]


@timed
def dist(**kwargs: Any) -> dict[str, Any]:
    """
    Build Python wheel and source distribution (Runtime layer - I/O operations)

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
    with span("build.dist.runtime"):
        metric_counter("build.operations_executed")

        try:
            # Build command
            cmd = ["build", "dist"]

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
                "command": "build",
                "subcommand": "dist",
                "output": output,
                "returncode": 0,
                "message": "Build Python wheel and source distribution completed successfully",
            }

        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "command": "build",
                "subcommand": "dist",
                "error": str(e),
                "returncode": e.returncode,
                "message": f"Command failed with exit code {e.returncode}",
            }

        except FileNotFoundError as e:
            return {
                "success": False,
                "command": "build",
                "subcommand": "dist",
                "error": f"Tool not found: {e}",
                "returncode": 127,
                "message": "Required tool not available",
            }

        except OSError as e:
            return {
                "success": False,
                "command": "build",
                "subcommand": "dist",
                "error": f"OS error: {e}",
                "returncode": 1,
                "message": "Filesystem or OS operation failed",
            }

        except Exception as e:
            return {
                "success": False,
                "command": "build",
                "subcommand": "dist",
                "error": f"Unexpected error: {e}",
                "returncode": 1,
                "message": "Unexpected error during execution",
            }


@timed
def exe(**kwargs: Any) -> dict[str, Any]:
    """
    Build standalone executable with PyInstaller (Runtime layer - I/O operations)

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
    with span("build.exe.runtime"):
        metric_counter("build.operations_executed")

        try:
            # Build command
            cmd = ["build", "exe"]

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
                "command": "build",
                "subcommand": "exe",
                "output": output,
                "returncode": 0,
                "message": "Build standalone executable with PyInstaller completed successfully",
            }

        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "command": "build",
                "subcommand": "exe",
                "error": str(e),
                "returncode": e.returncode,
                "message": f"Command failed with exit code {e.returncode}",
            }

        except FileNotFoundError as e:
            return {
                "success": False,
                "command": "build",
                "subcommand": "exe",
                "error": f"Tool not found: {e}",
                "returncode": 127,
                "message": "Required tool not available",
            }

        except OSError as e:
            return {
                "success": False,
                "command": "build",
                "subcommand": "exe",
                "error": f"OS error: {e}",
                "returncode": 1,
                "message": "Filesystem or OS operation failed",
            }

        except Exception as e:
            return {
                "success": False,
                "command": "build",
                "subcommand": "exe",
                "error": f"Unexpected error: {e}",
                "returncode": 1,
                "message": "Unexpected error during execution",
            }


@timed
def spec(**kwargs: Any) -> dict[str, Any]:
    """
    Generate PyInstaller spec file (Runtime layer - I/O operations)

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
    with span("build.spec.runtime"):
        metric_counter("build.operations_executed")

        try:
            # Build command
            cmd = ["build", "spec"]

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
                "command": "build",
                "subcommand": "spec",
                "output": output,
                "returncode": 0,
                "message": "Generate PyInstaller spec file completed successfully",
            }

        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "command": "build",
                "subcommand": "spec",
                "error": str(e),
                "returncode": e.returncode,
                "message": f"Command failed with exit code {e.returncode}",
            }

        except FileNotFoundError as e:
            return {
                "success": False,
                "command": "build",
                "subcommand": "spec",
                "error": f"Tool not found: {e}",
                "returncode": 127,
                "message": "Required tool not available",
            }

        except OSError as e:
            return {
                "success": False,
                "command": "build",
                "subcommand": "spec",
                "error": f"OS error: {e}",
                "returncode": 1,
                "message": "Filesystem or OS operation failed",
            }

        except Exception as e:
            return {
                "success": False,
                "command": "build",
                "subcommand": "spec",
                "error": f"Unexpected error: {e}",
                "returncode": 1,
                "message": "Unexpected error during execution",
            }


@timed
def dogfood(**kwargs: Any) -> dict[str, Any]:
    """
    Build uvmgr executable (eat own dog food) (Runtime layer - I/O operations)

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
    with span("build.dogfood.runtime"):
        metric_counter("build.operations_executed")

        try:
            # Build command
            cmd = ["build", "dogfood"]

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
                "command": "build",
                "subcommand": "dogfood",
                "output": output,
                "returncode": 0,
                "message": "Build uvmgr executable (eat own dog food) completed successfully",
            }

        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "command": "build",
                "subcommand": "dogfood",
                "error": str(e),
                "returncode": e.returncode,
                "message": f"Command failed with exit code {e.returncode}",
            }

        except FileNotFoundError as e:
            return {
                "success": False,
                "command": "build",
                "subcommand": "dogfood",
                "error": f"Tool not found: {e}",
                "returncode": 127,
                "message": "Required tool not available",
            }

        except OSError as e:
            return {
                "success": False,
                "command": "build",
                "subcommand": "dogfood",
                "error": f"OS error: {e}",
                "returncode": 1,
                "message": "Filesystem or OS operation failed",
            }

        except Exception as e:
            return {
                "success": False,
                "command": "build",
                "subcommand": "dogfood",
                "error": f"Unexpected error: {e}",
                "returncode": 1,
                "message": "Unexpected error during execution",
            }
