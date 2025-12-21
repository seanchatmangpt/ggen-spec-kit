"""
specify_cli.commands.cache
===========================

Cache management and operations

Generated from RDF specification: ontology/cli-commands-uvmgr-full.ttl
"""

from __future__ import annotations

import typer
from rich.console import Console

from specify_cli.core.instrumentation import add_span_event, instrument_command
from specify_cli.core.shell import colour
from specify_cli.ops import cache as cache_ops

app = typer.Typer(help="Cache management and operations")
console = Console()


@app.command("clear")
@instrument_command("cache.clear", track_args=True)
def clear_command(
    clear_all: bool = typer.Option(False, "--all", help="Clear all caches"),
) -> None:
    """Clear cache."""
    try:
        add_span_event("cache.clear.started", {"clear_all": clear_all})

        result = cache_ops.clear_cache(clear_all=clear_all)

        if result.get("success"):
            console.print(
                f"[bold green]✓[/] Cleared {result.get('entries_removed', 0)} cache entries"
            )
        else:
            colour("[red]✗ Cache clear failed[/red]", "red")
            raise typer.Exit(1) from None

    except Exception as e:
        colour(f"[red]Error:[/red] {e}", "red")
        raise typer.Exit(1) from e


@app.command("stats")
@instrument_command("cache.stats", track_args=True)
def stats_command() -> None:
    """Show cache statistics."""
    try:
        add_span_event("cache.stats.started", {})

        result = cache_ops.get_cache_stats()

        console.print("[bold]Cache Statistics:[/bold]")
        console.print(f"  Entries: {result.get('entries', 0)}")
        console.print(f"  Size: {result.get('size_mb', 0):.2f} MB")

    except Exception as e:
        colour(f"[red]Error:[/red] {e}", "red")
        raise typer.Exit(1) from e


if __name__ == "__main__":
    app()
