"""
uvmgr.commands.docs
=======================

API documentation generation

Generated from RDF specification: ontology/cli-commands-uvmgr-full.ttl
"""

from __future__ import annotations

import typer
from rich.console import Console

app = typer.Typer(help="API documentation generation")
console = Console()


@app.command("run")
def run_command() -> None:
    """Execute docs command."""
    console.print(f"[bold green]✓[/] docs command executed")


if __name__ == "__main__":
    app()
