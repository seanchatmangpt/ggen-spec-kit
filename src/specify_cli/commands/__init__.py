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

from .check import app as check_app

# Core commands
from .init import app as init_app

# Workflow commands (SpiffWorkflow)
from .spiff import app as spiff_app
from .version import app as version_app
from .version import version_callback

# ggen commands (RDF-first code generation, optional)
try:
    from .ggen import app as ggen_app

    GGEN_COMMANDS_AVAILABLE = True
except ImportError:
    GGEN_COMMANDS_AVAILABLE = False
    ggen_app = None

# Process mining commands (pm4py, optional)
try:
    from .pm import app as pm_app

    PM_COMMANDS_AVAILABLE = True
except ImportError:
    PM_COMMANDS_AVAILABLE = False
    pm_app = None

# DSPy commands (optional)
try:
    from specify_cli.dspy_commands import get_dspy_app

    DSPY_COMMANDS_AVAILABLE = True
except ImportError:
    DSPY_COMMANDS_AVAILABLE = False
    get_dspy_app = None

__all__ = [
    "DSPY_COMMANDS_AVAILABLE",
    "GGEN_COMMANDS_AVAILABLE",
    "PM_COMMANDS_AVAILABLE",
    "check_app",
    # DSPy commands
    "get_dspy_app",
    # ggen commands
    "ggen_app",
    # Core commands
    "init_app",
    # Process mining commands
    "pm_app",
    # Workflow commands
    "spiff_app",
    "version_app",
    "version_callback",
]
