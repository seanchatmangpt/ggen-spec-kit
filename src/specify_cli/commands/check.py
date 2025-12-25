"""
specify_cli.commands.check - Check Command
===========================================

CLI command handler for checking installed tools and dependencies.

This module provides the Typer command interface for validating
that required and optional tools are available.

Examples
--------
    $ specify check
    $ specify check --verbose
    $ specify check --json

See Also
--------
- :mod:`specify_cli.ops.check` : Business logic
- :mod:`specify_cli.runtime.tools` : Tool detection
"""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from specify_cli.core.instrumentation import instrument_command
from specify_cli.core.shell import colour, dump_json
from specify_cli.ops import check as check_ops

console = Console()

app = typer.Typer(
    name="check",
    help="Check for required and optional tools.",
)


@app.callback(invoke_without_command=True)
@instrument_command("check", track_args=True)
def check(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed information about each tool.",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results as JSON.",
    ),
    include_optional: bool = typer.Option(
        True,
        "--include-optional/--required-only",
        help="Include optional tools in the check.",
    ),
) -> None:
    """Check for required and optional tools.

    Validates that all required tools are installed and available
    in your PATH. Also checks optional tools that enhance functionality.

    Required tools:
        git - Version control

    Optional tools:
        claude - Claude CLI (Anthropic)
        cursor - Cursor editor
        ggen - Graph generator CLI
        uv - Python package manager
    """
    try:
        # Call ops layer
        result = check_ops.check_all_tools(include_optional=include_optional)

        if json_output:
            # JSON output format
            output = {
                "success": result.success,
                "available": [
                    {
                        "name": t.name,
                        "path": t.path,
                        "required": t.required,
                        "version": t.version,
                    }
                    for t in result.available
                ],
                "missing": [
                    {
                        "name": t.name,
                        "required": t.required,
                        "error": t.error,
                    }
                    for t in result.missing
                ],
                "duration": result.duration,
            }
            dump_json(output)
            return

        # Table output
        console.print()
        console.print("[bold]Tool Check Results[/bold]")
        console.print()

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Tool", style="bold")
        table.add_column("Status")
        table.add_column("Required")
        if verbose:
            table.add_column("Version")
            table.add_column("Path / Error")

        # Available tools
        for tool in result.available:
            status = "[green]✓ Available[/green]"
            required = "[yellow]Yes[/yellow]" if tool.required else "No"

            if verbose:
                table.add_row(
                    tool.name,
                    status,
                    required,
                    tool.version or "unknown",
                    tool.path or "",
                )
            else:
                table.add_row(tool.name, status, required)

        # Missing tools
        for tool in result.missing:
            status = "[red]✗ Missing[/red]"
            required = "[yellow]Yes[/yellow]" if tool.required else "No"

            if verbose:
                table.add_row(
                    tool.name,
                    status,
                    required,
                    "-",
                    tool.error or "Not found in PATH",
                )
            else:
                table.add_row(tool.name, status, required)

        console.print(table)
        console.print()

        # Summary
        counts = result.tool_count
        console.print("[bold]Summary:[/bold]")
        console.print(f"  Available: {counts['available']}")
        console.print(f"  Missing: {counts['missing']}")

        if counts["required_missing"] > 0:
            console.print()
            colour(f"[red]✗ {counts['required_missing']} required tool(s) missing[/red]", "red")
            console.print()
            console.print("[yellow]Please install missing required tools to use Specify.[/yellow]")
            raise typer.Exit(1) from None
        console.print()
        colour("[green]✓ All required tools are available[/green]", "green")

        if verbose:
            # Show ggen-specific information if available
            ggen_status = next((t for t in result.available if t.name == "ggen"), None)
            if ggen_status:
                console.print()
                console.print("[bold]ggen:[/bold] RDF-first code generation")
                console.print(f"  Version: {ggen_status.version or 'unknown'}")
                console.print(f"  Path: {ggen_status.path or 'unknown'}")
                console.print("  Purpose: Required for RDF ontology compilation (optional)")

            # Show environment info
            console.print()
            console.print("[bold]Environment:[/bold]")
            env_info = check_ops.get_environment_info()
            console.print(f"  Python: {env_info['python']['version'].split()[0]}")
            console.print(
                f"  Platform: {env_info['platform']['system']} {env_info['platform']['release']}"
            )

    except KeyboardInterrupt:
        console.print()
        colour("Operation cancelled.", "yellow")
        raise typer.Exit(130)

    except Exception as e:
        console.print()
        colour(f"[red]Error checking tools:[/red] {e}", "red")
        raise typer.Exit(1) from None
