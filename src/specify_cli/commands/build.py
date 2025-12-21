"""
uvmgr.commands.build
========================

Build wheels, sdists, and executables using PyInstaller

Generated from RDF specification: ontology/cli-commands-uvmgr-full.ttl
"""

from __future__ import annotations

import typer
from rich.console import Console

app = typer.Typer(help="Build wheels, sdists, and executables using PyInstaller")
console = Console()


@app.command("run")
def run_command() -> None:
    """Execute build command."""
    console.print(f"[bold green]✓[/] build command executed")


if __name__ == "__main__":
    app()
