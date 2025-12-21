"""
specify_cli.commands.docs
==========================

API documentation generation

Generated from RDF specification: ontology/cli-commands-uvmgr-full.ttl
"""

from __future__ import annotations

import typer
from rich.console import Console

from specify_cli.core.instrumentation import add_span_event, instrument_command
from specify_cli.core.shell import colour
from specify_cli.ops import docs as docs_ops

app = typer.Typer(help="API documentation generation")
console = Console()


@app.command("build")
@instrument_command("docs.build", track_args=True)
def build_command(
    serve: bool = typer.Option(False, "--serve", help="Serve docs after building"),
) -> None:
    """Build documentation."""
    try:
        add_span_event("docs.build.started", {"serve": serve})

        result = docs_ops.build_docs(serve=serve)

        if result.get("success"):
            console.print("[bold green]✓[/] Documentation built successfully")
            if serve:
                console.print(
                    f"[cyan]Serving at:[/cyan] {result.get('url', 'http://localhost:8000')}"
                )
        else:
            colour("[red]✗ Documentation build failed[/red]", "red")
            raise typer.Exit(1) from None

    except Exception as e:
        colour(f"[red]Error:[/red] {e}", "red")
        raise typer.Exit(1) from e


if __name__ == "__main__":
    app()
