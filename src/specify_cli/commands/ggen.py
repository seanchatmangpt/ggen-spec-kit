"""
specify_cli.commands.ggen - ggen Command Group
================================================

CLI command handler for ggen (Graph Generator) operations.

This module provides Typer command interface for RDF-first code generation:
- sync: Transform RDF specifications to code/markdown via ggen.toml configuration

All transformations implement the constitutional equation: spec.md = μ(feature.ttl)

Where μ is the five-stage transformation pipeline:
- μ₁ Normalize: Validate SHACL shapes
- μ₂ Extract: Execute SPARQL queries
- μ₃ Emit: Render Tera templates
- μ₄ Canonicalize: Format output
- μ₅ Receipt: SHA256 hash proof

Examples
--------
    $ specify ggen sync
    $ specify ggen sync --watch
    $ specify ggen sync --verbose

See Also
--------
- :mod:`specify_cli.runtime.ggen` : Runtime layer for ggen operations
- :mod:`specify_cli.core.telemetry` : OpenTelemetry instrumentation

Notes
-----
All generation happens through ggen.toml configuration. The only supported
subcommand is 'sync', which reads configuration from ggen.toml and executes
the five-stage transformation pipeline.
"""

from __future__ import annotations

import time
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from specify_cli.core.instrumentation import instrument_command
from specify_cli.core.shell import colour, dump_json
from specify_cli.runtime.ggen import (
    GgenError,
    get_ggen_version,
    is_ggen_available,
    sync_specs,
)

console = Console()

app = typer.Typer(
    name="ggen",
    help="RDF-first code generation (ggen v5.0.2 integration)",
)


def _handle_sync_failure(json_output: bool) -> None:
    """Handle ggen sync failure output and exit.

    Parameters
    ----------
    json_output : bool
        Whether to output JSON format.

    Raises
    ------
    typer.Exit
        Always exits with code 1.
    """
    if json_output:
        dump_json({"success": False})
    else:
        console.print()
        colour("[red]✗ Transformation failed[/red]", "red")
        console.print("[dim]Transformation failed[/dim]")
    raise typer.Exit(1) from None


@app.command("sync")
@instrument_command("ggen.sync", track_args=True)
def sync(  # noqa: PLR0912, PLR0915 - CLI command with user-facing output formatting
    ctx: typer.Context,  # noqa: ARG001 - Required by Typer for context access
    watch: bool = typer.Option(
        False,
        "--watch",
        "-w",
        help="Watch for file changes and automatically re-run transformations.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output showing transformation details.",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results as JSON.",
    ),
) -> None:
    """Transform RDF specifications to code/markdown using ggen sync.

    Implements the constitutional equation: spec.md = μ(feature.ttl)

    The sync operation runs the five-stage transformation pipeline:
    1. μ₁ Normalize - Load and validate RDF against SHACL shapes
    2. μ₂ Extract - Execute SPARQL queries to extract data
    3. μ₃ Emit - Render Tera templates with query results
    4. μ₄ Canonicalize - Format output (line endings, whitespace)
    5. μ₅ Receipt - Generate SHA256 hash proof of transformation

    Configuration is read from ggen.toml in the current directory.

    Examples:
        specify ggen sync
        specify ggen sync --watch
        specify ggen sync --verbose
    """
    # Check ggen availability
    if not is_ggen_available():
        console.print()
        console.print(
            Panel(
                "[red]ggen is not installed or not in PATH[/red]\n\n"
                "Install ggen using one of these methods:\n"
                "  • brew install seanchatmangpt/ggen/ggen (recommended)\n"
                "  • cargo install ggen-cli-lib\n"
                "  • docker pull seanchatman/ggen:5.0.2",
                title="ggen Not Found",
                border_style="red",
            )
        )
        raise typer.Exit(1)

    # Show ggen version if verbose
    if verbose:
        version = get_ggen_version()
        console.print(f"[dim]ggen version: {version}[/dim]")

    # Determine project path (use current directory, as ggen reads ggen.toml from CWD)
    project_path = Path.cwd()

    # Show what we're doing
    if not json_output:
        console.print()
        console.print("[bold cyan]Running ggen sync transformation[/bold cyan]")
        console.print(f"[cyan]Project:[/cyan] {project_path}")
        console.print(f"[cyan]Watch mode:[/cyan] {'enabled' if watch else 'disabled'}")
        console.print()

        if watch:
            console.print("[yellow]Watch mode: Press Ctrl+C to stop[/yellow]")
            console.print()

    start_time = time.time()

    try:
        # Call runtime layer
        success = sync_specs(
            project_path=project_path,
            watch=watch,
            verbose=verbose,
        )

        duration = time.time() - start_time

        if not success:
            _handle_sync_failure(json_output)

        if json_output:
            # JSON output
            output = {
                "success": success,
                "project_path": str(project_path),
                "watch": watch,
                "duration": duration,
            }
            dump_json(output)
        else:
            # Pretty output
            console.print()
            colour("[green]✓ Transformation completed successfully[/green]", "green")
            console.print(f"[dim]Duration: {duration:.2f}s[/dim]")

            console.print()
            console.print("[bold]What happened:[/bold]")
            console.print("  • μ₁ Normalized RDF and validated SHACL shapes")
            console.print("  • μ₂ Extracted data using SPARQL queries")
            console.print("  • μ₃ Rendered Tera templates with query results")
            console.print("  • μ₄ Canonicalized output formatting")
            console.print("  • μ₅ Generated SHA256 receipt for verification")

            console.print()
            console.print("[cyan]Next steps:[/cyan]")
            console.print("  • Review generated files in your project")
            if not watch:
                console.print("  • Use --watch to auto-regenerate on changes")

    except GgenError as e:
        if json_output:
            dump_json({"success": False, "error": str(e)})
        else:
            console.print()
            console.print(
                Panel(
                    str(e),
                    title="ggen Sync Error",
                    border_style="red",
                )
            )
        raise typer.Exit(1) from e

    except KeyboardInterrupt:
        console.print()
        colour("Operation cancelled by user.", "yellow")
        raise typer.Exit(130) from None

    except Exception as e:
        if json_output:
            dump_json({"success": False, "error": str(e), "type": type(e).__name__})
        else:
            console.print()
            console.print(
                Panel(
                    f"[red]{e}[/red]",
                    title="Unexpected Error",
                    border_style="red",
                )
            )
        raise typer.Exit(1) from e
