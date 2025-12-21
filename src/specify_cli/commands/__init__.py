"""
specify_cli.commands - CLI Commands Layer
==========================================

CLI command handlers for specify-cli.

This layer contains Typer command definitions that:
- Parse CLI arguments and options
- Validate user input
- Format output using Rich
- Delegate business logic to ops layer

Layer Architecture
-----------------
Commands are the top layer, closest to the user:

    User → Commands Layer → Ops Layer → Runtime Layer
              (Typer)      (Logic)       (I/O)

Design Principles
----------------
* **Thin Handlers**: Minimal logic, just parsing and formatting
* **Immediate Delegation**: Call ops layer for all business logic
* **Rich Output**: Beautiful terminal output with Rich
* **OTEL Instrumented**: All commands decorated with @instrument_command

Available Commands
-----------------
* **init**: Initialize a new Specify project
* **check**: Check for required tools
* **version**: Show version information
* **wf/spiff**: Workflow automation (SpiffWorkflow)
* **pm**: Process mining (pm4py, optional)

See Also
--------
- :mod:`specify_cli.ops` : Operations/business logic layer
- :mod:`specify_cli.cli` : Main CLI assembly
"""

from __future__ import annotations

# Core commands
from .init import app as init_app
from .check import app as check_app
from .version import app as version_app, version_callback

# Workflow commands (SpiffWorkflow)
from .spiff import app as spiff_app

__all__ = [
    # Core commands
    "init_app",
    "check_app",
    "version_app",
    "version_callback",
    # Workflow commands
    "spiff_app",
]
