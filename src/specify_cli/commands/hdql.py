"""HDQL query command for spec-kit CLI.

This module provides the command-line interface for executing hyperdimensional queries.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import typer
from rich.console import Console
from rich.table import Table

from specify_cli.core.telemetry import span

if TYPE_CHECKING:
    from pathlib import Path

app = typer.Typer(help="Execute hyperdimensional queries (HDQL)")
console = Console()


@app.command("query")
def query_command(
    query_string: str = typer.Argument(..., help="HDQL query to execute"),
    format_type: str = typer.Option(
        "table", "--format", "-f", help="Output format: table, json, yaml"
    ),
    output: Path | None = typer.Option(None, "--output", "-o", help="Save results to file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show reasoning trace"),
    top_k: int = typer.Option(10, "--top-k", "-k", help="Maximum results to return"),
) -> None:
    """Execute hyperdimensional query."""
    from specify_cli.hyperdimensional import execute_query

    with span("hdql.query", query=query_string):
        try:
            # Execute query
            result = execute_query(
                query_string=query_string,
                top_k=top_k,
                verbose=verbose,
            )

            # Format output
            if format_type == "table":
                _display_table(result)
            elif format_type == "json":
                output_json = json.dumps(result.to_dict(), indent=2)
                if output:
                    output.write_text(output_json)
                    console.print(f"[green]Results saved to {output}[/green]")
                else:
                    console.print(output_json)
            elif format_type == "yaml":
                import yaml

                output_yaml = yaml.dump(result.to_dict(), default_flow_style=False)
                if output:
                    output.write_text(output_yaml)
                    console.print(f"[green]Results saved to {output}[/green]")
                else:
                    console.print(output_yaml)

            # Show reasoning if verbose
            if verbose:
                console.print("\n[bold]Reasoning:[/bold]")
                console.print(result.reasoning_trace.explain())

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1) from e


@app.command("parse")
def parse_command(
    query_string: str = typer.Argument(..., help="HDQL query to parse"),
) -> None:
    """Parse query and show AST (for debugging)."""
    from specify_cli.hyperdimensional.parser import parse_query

    try:
        ast = parse_query(query_string)
        console.print("[bold]Abstract Syntax Tree:[/bold]")
        console.print(ast)
    except Exception as e:
        console.print(f"[red]Parse Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command("explain")
def explain_command(
    query_string: str = typer.Argument(..., help="HDQL query to explain"),
) -> None:
    """Explain query execution plan."""
    from specify_cli.hyperdimensional import QueryEngine
    from specify_cli.hyperdimensional.embeddings import load_default_database

    try:
        db = load_default_database()
        engine = QueryEngine(db)
        explanation = engine.explain(query_string)

        console.print("[bold]Query Execution Plan:[/bold]")
        console.print(explanation)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command("repl")
def repl_command() -> None:
    """Start interactive HDQL REPL."""
    from specify_cli.hyperdimensional.repl import run_repl

    run_repl()


def _display_table(result: any) -> None:
    """Display results as Rich table."""
    from specify_cli.hyperdimensional.results import VectorQueryResult

    if isinstance(result, VectorQueryResult):
        table = Table(title="Query Results")
        table.add_column("Entity", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Score", justify="right", style="green")
        table.add_column("Explanation", style="yellow")

        for match in result.top_k(10):
            table.add_row(
                match.entity.name,
                match.entity.entity_type,
                f"{match.score:.3f}",
                match.explanation[:60] + "..."
                if len(match.explanation) > 60
                else match.explanation,
            )

        console.print(table)
        console.print(f"\n[dim]Execution time: {result.execution_time_ms:.2f}ms[/dim]")
    else:
        # Recommendation or Analysis result
        console.print(result.explain() if hasattr(result, "explain") else str(result))


if __name__ == "__main__":
    app()
