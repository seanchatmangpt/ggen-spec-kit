"""
specify_cli.app - Main CLI Application
=======================================

Main Typer application assembly for specify-cli.

This module assembles the three-tier architecture into a single
CLI application:
- Commands from specify_cli.commands
- Business logic from specify_cli.ops
- Runtime execution from specify_cli.runtime
- Core utilities from specify_cli.core

Architecture
-----------

    ┌────────────────────────────────────────────┐
    │  CLI App (this module)                     │
    │  • Typer application assembly              │
    │  • Banner and help formatting              │
    │  • Command group registration              │
    └──────────────────┬─────────────────────────┘
                       │
    ┌──────────────────▼─────────────────────────┐
    │  Commands Layer (specify_cli.commands/)    │
    │  • Argument parsing                        │
    │  • Output formatting                       │
    │  • @instrument_command decorators          │
    └──────────────────┬─────────────────────────┘
                       │
    ┌──────────────────▼─────────────────────────┐
    │  Operations Layer (specify_cli.ops/)       │
    │  • Pure business logic                     │
    │  • No side effects                         │
    └──────────────────┬─────────────────────────┘
                       │
    ┌──────────────────▼─────────────────────────┐
    │  Runtime Layer (specify_cli.runtime/)      │
    │  • All I/O operations                      │
    │  • Subprocess execution                    │
    └────────────────────────────────────────────┘

Usage
-----
    $ specify --help
    $ specify init my-project
    $ specify check
    $ specify version

See Also
--------
- :mod:`specify_cli.commands` : Command handlers
- :mod:`specify_cli.ops` : Business logic
- :mod:`specify_cli.runtime` : Runtime execution
"""

from __future__ import annotations

import sys

import typer
from rich.align import Align
from rich.console import Console

from specify_cli.cli import BannerGroup, show_banner
from specify_cli.commands import (
    check_app,
    ggen_app,
    init_app,
    jtbd_app,
    spiff_app,
    version_app,
    version_callback,
)
from specify_cli.core.shell import install_rich

console = Console()

# Install Rich tracebacks for better error display
install_rich()

# Create the main Typer app
app = typer.Typer(
    name="specify",
    help="Setup tool for Specify spec-driven development projects",
    add_completion=False,
    invoke_without_command=True,
    cls=BannerGroup,
)


# Register command groups
# Init command
app.add_typer(init_app, name="init", help="Initialize a new Specify project")

# Check command
app.add_typer(check_app, name="check", help="Check for required tools")

# Version command
app.add_typer(version_app, name="version", help="Show version information")

# Workflow commands (SpiffWorkflow)
app.add_typer(spiff_app, name="wf", help="Workflow automation (SpiffWorkflow)")

# ggen commands (RDF-first code generation)
app.add_typer(ggen_app, name="ggen", help="RDF-first code generation (ggen v5.0.2)")

# JTBD commands (Jobs-to-be-Done metrics)
app.add_typer(jtbd_app, name="jtbd", help="Jobs-to-be-Done (JTBD) metrics tracking")


# Try to add process mining commands if pm4py is available
try:
    from specify_cli.commands.pm import app as pm_app

    app.add_typer(pm_app, name="pm", help="Process mining operations")
except ImportError:
    pass  # pm4py not installed


# Try to add DSPy commands if dspy is available
try:
    from specify_cli.dspy_commands import get_dspy_app

    dspy_app = get_dspy_app()
    app.add_typer(dspy_app, name="dspy", help="DSPy LLM optimization")
except ImportError:
    pass  # dspy not installed


# Try to add Hyperdimensional Dashboard commands if dependencies are available
try:
    from specify_cli.commands.dashboards import app as dashboards_app

    app.add_typer(
        dashboards_app, name="dashboard", help="Hyperdimensional dashboards & observability"
    )
except ImportError:
    pass  # numpy/scikit-learn not installed

# Try to add Hyperdimensional analysis commands if dependencies are available
try:
    from specify_cli.commands.hd import app as hd_app

    app.add_typer(hd_app, name="hd", help="Hyperdimensional analysis & decision support")
except ImportError:
    pass  # numpy/scikit-learn not installed


# uvmgr commands - 13 core commands for project management
# These are optional and fail gracefully if not fully implemented
_UVMGR_COMMANDS = [
    ("deps", "Dependency management with uv"),
    ("build", "Package building (wheel/sdist/exe)"),
    ("tests", "Test execution with pytest"),
    ("cache", "Cache management operations"),
    ("lint", "Code quality (ruff, mypy)"),
    ("otel", "OpenTelemetry validation"),
    ("guides", "Development guides"),
    ("worktree", "Git worktree management"),
    ("infodesign", "Information design support"),
    ("mermaid", "Mermaid diagram generation"),
    ("dod", "Definition of Done automation"),
    ("docs", "API documentation generation"),
    ("terraform", "Infrastructure as code"),
]

for cmd_name, cmd_help in _UVMGR_COMMANDS:
    try:
        module = __import__(f"specify_cli.commands.{cmd_name}", fromlist=["app"])
        app.add_typer(module.app, name=cmd_name, help=cmd_help)
    except (ImportError, AttributeError):
        pass  # Command not available


@app.callback()
def callback(
    ctx: typer.Context,
    version: bool | None = typer.Option(
        None,
        "--version",
        "-V",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """Specify CLI - Setup tool for spec-driven development projects.

    Run 'specify init' to create a new project, or 'specify --help' for
    more information on available commands.
    """
    if ctx.invoked_subcommand is None and "--help" not in sys.argv and "-h" not in sys.argv:
        show_banner()
        console.print(Align.center("[dim]Run 'specify --help' for usage information[/dim]"))
        console.print()


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
