"""
specify_cli.commands.build
===========================

Build wheels, sdists, and executables using PyInstaller

Generated from RDF specification: ontology/cli-commands-uvmgr-full.ttl
"""

from __future__ import annotations

import typer
from rich.console import Console

from specify_cli.core.instrumentation import add_span_event, instrument_command
from specify_cli.core.shell import colour
from specify_cli.ops import build as build_ops

app = typer.Typer(help="Build wheels, sdists, and executables using PyInstaller")
console = Console()


@app.command("run")
@instrument_command("build.run", track_args=True)
def run_command(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Execute build command."""
    try:
        add_span_event("build.started", {"operation": "build"})

        result = build_ops.run_build(verbose=verbose)

        if result.get("success"):
            console.print("[bold green]✓[/] Build completed successfully")
        else:
            colour("[red]✗ Build failed[/red]", "red")
            raise typer.Exit(1) from None

    except Exception as e:
        colour(f"[red]Error:[/red] {e}", "red")
        raise typer.Exit(1) from e


if __name__ == "__main__":
    app()
