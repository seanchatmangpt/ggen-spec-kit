"""
specify_cli.commands.dod
=========================

Definition of Done automation and checklists

Generated from RDF specification: ontology/cli-commands-uvmgr-full.ttl
"""

from __future__ import annotations

import typer
from rich.console import Console

from specify_cli.core.instrumentation import add_span_event, instrument_command
from specify_cli.core.shell import colour
from specify_cli.ops import dod as dod_ops

app = typer.Typer(help="Definition of Done automation and checklists")
console = Console()


@app.command("check")
@instrument_command("dod.check", track_args=True)
def check_command(
    strict: bool = typer.Option(
        False, "--strict", help="Strict mode - fail on any incomplete items"
    ),
) -> None:
    """Check Definition of Done compliance."""
    try:
        add_span_event("dod.check.started", {"strict": strict})

        result = dod_ops.check_dod(strict=strict)

        if result.get("success"):
            console.print(
                f"[bold green]✓[/] DoD check passed ({result.get('completed', 0)}/{result.get('total', 0)} items)"
            )
        else:
            colour("[red]✗ DoD check failed[/red]", "red")
            raise typer.Exit(1) from None

    except Exception as e:
        colour(f"[red]Error:[/red] {e}", "red")
        raise typer.Exit(1) from e


if __name__ == "__main__":
    app()
