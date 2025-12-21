"""
specify_cli.commands.deps
==========================

Dependency management with uv (add/remove/upgrade/list/lock)

Generated from RDF specification: ontology/cli-commands-uvmgr-full.ttl
"""

from __future__ import annotations

import typer
from rich.console import Console

from specify_cli.core.instrumentation import add_span_event, instrument_command
from specify_cli.core.shell import colour
from specify_cli.ops import deps as deps_ops

app = typer.Typer(help="Dependency management with uv (add/remove/upgrade/list/lock)")
console = Console()


@app.command("add")
@instrument_command("deps.add", track_args=True)
def add_command(
    packages: list[str] = typer.Argument(..., help="Packages to add"),
    dev: bool = typer.Option(False, "--dev", help="Add as dev dependency"),
) -> None:
    """Add packages to dependencies."""
    try:
        add_span_event("deps.add.started", {"packages": len(packages), "dev": dev})

        result = deps_ops.add(packages=packages, dev=dev)

        if result.get("success"):
            console.print(f"[bold green]✓[/] Added {len(packages)} package(s)")
        else:
            colour("[red]✗ Failed to add packages[/red]", "red")
            raise typer.Exit(1) from None

    except Exception as e:
        colour(f"[red]Error:[/red] {e}", "red")
        raise typer.Exit(1) from e


@app.command("remove")
@instrument_command("deps.remove", track_args=True)
def remove_command(
    packages: list[str] = typer.Argument(..., help="Packages to remove"),
) -> None:
    """Remove packages from dependencies."""
    try:
        add_span_event("deps.remove.started", {"packages": len(packages)})

        result = deps_ops.remove(packages=packages)

        if result.get("success"):
            console.print(f"[bold green]✓[/] Removed {len(packages)} package(s)")
        else:
            colour("[red]✗ Failed to remove packages[/red]", "red")
            raise typer.Exit(1) from None

    except Exception as e:
        colour(f"[red]Error:[/red] {e}", "red")
        raise typer.Exit(1) from e


if __name__ == "__main__":
    app()
