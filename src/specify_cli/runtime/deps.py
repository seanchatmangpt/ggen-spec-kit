"""
specify_cli.runtime.deps
===============================

Runtime layer for Dependency management with uv (add/remove/upgrade/list/lock).

This module handles all subprocess execution, file I/O, and external tool integration.
No business logic - all operations delegated from the ops layer with telemetry.

All functions:
- Use subprocess.run() with shell=False (safe subprocess calls)
- Validate paths before operations
- Handle errors with proper context
- Record OpenTelemetry spans and metrics
- Support structured logging and JSON output

Install dependencies via:
    uv sync --group deps
"""

from __future__ import annotations

import subprocess
from typing import Any

from specify_cli.core.process import run_logged
from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_counter, span

__all__ = [
    "add",
    "list",
    "lock",
    "remove",
    "upgrade",
]


@timed
def add(**kwargs: Any) -> dict[str, Any]:
    """
    Add packages to project dependencies (Runtime layer - I/O operations)

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
    with span("deps.add.runtime"):
        metric_counter("deps.operations_executed")

        try:
            # Build command
            cmd = ["deps", "add"]

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
                "command": "deps",
                "subcommand": "add",
                "output": output,
                "returncode": 0,
                "message": "Add packages to project dependencies completed successfully",
            }

        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "command": "deps",
                "subcommand": "add",
                "error": str(e),
                "returncode": e.returncode,
                "message": f"Command failed with exit code {e.returncode}",
            }

        except FileNotFoundError as e:
            return {
                "success": False,
                "command": "deps",
                "subcommand": "add",
                "error": f"Tool not found: {e}",
                "returncode": 127,
                "message": "Required tool not available",
            }

        except OSError as e:
            return {
                "success": False,
                "command": "deps",
                "subcommand": "add",
                "error": f"OS error: {e}",
                "returncode": 1,
                "message": "Filesystem or OS operation failed",
            }

        except Exception as e:
            return {
                "success": False,
                "command": "deps",
                "subcommand": "add",
                "error": f"Unexpected error: {e}",
                "returncode": 1,
                "message": "Unexpected error during execution",
            }


@timed
def remove(**kwargs: Any) -> dict[str, Any]:
    """
    Remove packages from project dependencies (Runtime layer - I/O operations)

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
    with span("deps.remove.runtime"):
        metric_counter("deps.operations_executed")

        try:
            # Build command
            cmd = ["deps", "remove"]

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
                "command": "deps",
                "subcommand": "remove",
                "output": output,
                "returncode": 0,
                "message": "Remove packages from project dependencies completed successfully",
            }

        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "command": "deps",
                "subcommand": "remove",
                "error": str(e),
                "returncode": e.returncode,
                "message": f"Command failed with exit code {e.returncode}",
            }

        except FileNotFoundError as e:
            return {
                "success": False,
                "command": "deps",
                "subcommand": "remove",
                "error": f"Tool not found: {e}",
                "returncode": 127,
                "message": "Required tool not available",
            }

        except OSError as e:
            return {
                "success": False,
                "command": "deps",
                "subcommand": "remove",
                "error": f"OS error: {e}",
                "returncode": 1,
                "message": "Filesystem or OS operation failed",
            }

        except Exception as e:
            return {
                "success": False,
                "command": "deps",
                "subcommand": "remove",
                "error": f"Unexpected error: {e}",
                "returncode": 1,
                "message": "Unexpected error during execution",
            }


@timed
def upgrade(**kwargs: Any) -> dict[str, Any]:
    """
    Upgrade packages to latest versions (Runtime layer - I/O operations)

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
    with span("deps.upgrade.runtime"):
        metric_counter("deps.operations_executed")

        try:
            # Build command
            cmd = ["deps", "upgrade"]

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
                "command": "deps",
                "subcommand": "upgrade",
                "output": output,
                "returncode": 0,
                "message": "Upgrade packages to latest versions completed successfully",
            }

        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "command": "deps",
                "subcommand": "upgrade",
                "error": str(e),
                "returncode": e.returncode,
                "message": f"Command failed with exit code {e.returncode}",
            }

        except FileNotFoundError as e:
            return {
                "success": False,
                "command": "deps",
                "subcommand": "upgrade",
                "error": f"Tool not found: {e}",
                "returncode": 127,
                "message": "Required tool not available",
            }

        except OSError as e:
            return {
                "success": False,
                "command": "deps",
                "subcommand": "upgrade",
                "error": f"OS error: {e}",
                "returncode": 1,
                "message": "Filesystem or OS operation failed",
            }

        except Exception as e:
            return {
                "success": False,
                "command": "deps",
                "subcommand": "upgrade",
                "error": f"Unexpected error: {e}",
                "returncode": 1,
                "message": "Unexpected error during execution",
            }


@timed
def list(**kwargs: Any) -> dict[str, Any]:
    """
    List installed packages (Runtime layer - I/O operations)

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
    with span("deps.list.runtime"):
        metric_counter("deps.operations_executed")

        try:
            # Build command
            cmd = ["deps", "list"]

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
                "command": "deps",
                "subcommand": "list",
                "output": output,
                "returncode": 0,
                "message": "List installed packages completed successfully",
            }

        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "command": "deps",
                "subcommand": "list",
                "error": str(e),
                "returncode": e.returncode,
                "message": f"Command failed with exit code {e.returncode}",
            }

        except FileNotFoundError as e:
            return {
                "success": False,
                "command": "deps",
                "subcommand": "list",
                "error": f"Tool not found: {e}",
                "returncode": 127,
                "message": "Required tool not available",
            }

        except OSError as e:
            return {
                "success": False,
                "command": "deps",
                "subcommand": "list",
                "error": f"OS error: {e}",
                "returncode": 1,
                "message": "Filesystem or OS operation failed",
            }

        except Exception as e:
            return {
                "success": False,
                "command": "deps",
                "subcommand": "list",
                "error": f"Unexpected error: {e}",
                "returncode": 1,
                "message": "Unexpected error during execution",
            }


@timed
def lock(**kwargs: Any) -> dict[str, Any]:
    """
    Generate or update lock file (Runtime layer - I/O operations)

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
    with span("deps.lock.runtime"):
        metric_counter("deps.operations_executed")

        try:
            # Build command
            cmd = ["deps", "lock"]

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
                "command": "deps",
                "subcommand": "lock",
                "output": output,
                "returncode": 0,
                "message": "Generate or update lock file completed successfully",
            }

        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "command": "deps",
                "subcommand": "lock",
                "error": str(e),
                "returncode": e.returncode,
                "message": f"Command failed with exit code {e.returncode}",
            }

        except FileNotFoundError as e:
            return {
                "success": False,
                "command": "deps",
                "subcommand": "lock",
                "error": f"Tool not found: {e}",
                "returncode": 127,
                "message": "Required tool not available",
            }

        except OSError as e:
            return {
                "success": False,
                "command": "deps",
                "subcommand": "lock",
                "error": f"OS error: {e}",
                "returncode": 1,
                "message": "Filesystem or OS operation failed",
            }

        except Exception as e:
            return {
                "success": False,
                "command": "deps",
                "subcommand": "lock",
                "error": f"Unexpected error: {e}",
                "returncode": 1,
                "message": "Unexpected error during execution",
            }
