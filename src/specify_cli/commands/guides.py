"""
uvmgr.commands.guides
=========================

Development guides and documentation

Generated from RDF specification: ontology/cli-commands-uvmgr-full.ttl
"""

from __future__ import annotations

import typer
from rich.console import Console

app = typer.Typer(help="Development guides and documentation")
console = Console()


@app.command("run")
def run_command() -> None:
    """Execute guides command."""
    console.print("[bold green]✓[/] guides command executed")


if __name__ == "__main__":
    app()
