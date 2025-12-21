"""
specify_cli.commands.version - Version Command
===============================================

CLI command handler for version information.

This module provides the Typer command interface for displaying
the current version and checking for updates.

Examples
--------
    $ specify version
    $ specify version --check-updates
    $ specify version --json

See Also
--------
- :mod:`specify_cli.ops.version` : Business logic
"""

from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel

from specify_cli.core.instrumentation import instrument_command
from specify_cli.core.shell import colour, dump_json
from specify_cli.ops import version as version_ops

console = Console()

app = typer.Typer(
    name="version",
    help="Show version information.",
)


@app.callback(invoke_without_command=True)
@instrument_command("version", track_args=True)
def version(
    check_updates: bool = typer.Option(
        False,
        "--check-updates",
        "-u",
        help="Check for available updates.",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results as JSON.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed build information.",
    ),
) -> None:
    """Show version information.

    Displays the current version of specify-cli and optionally
    checks for available updates.
    """
    try:
        current = version_ops.get_current_version()

        if check_updates:
            # Get full version info with update check
            info = version_ops.get_version_info(check_updates=True)

            if json_output:
                output = {
                    "current_version": info.current_version,
                    "latest_version": info.latest_version,
                    "update_available": info.update_available,
                    "release_url": info.release_url,
                    "error": info.error,
                }
                dump_json(output)
                return

            console.print()
            console.print(f"[bold]specify-cli[/bold] version {current}")
            console.print()

            if info.error:
                console.print(f"[yellow]Could not check for updates:[/yellow] {info.error}")
            elif info.update_available:
                console.print(
                    Panel(
                        f"[green]Update available![/green]\n\n"
                        f"Current version: {info.current_version}\n"
                        f"Latest version:  {info.latest_version}\n\n"
                        f"[cyan]Update with:[/cyan] pip install --upgrade specify-cli",
                        title="Update Available",
                        border_style="green",
                    )
                )
            else:
                colour("[green]✓ You are running the latest version[/green]", "green")

        else:
            if json_output:
                output = {"version": current}
                if verbose:
                    output["build_info"] = version_ops.get_build_info()
                dump_json(output)
                return

            console.print(f"specify-cli {current}")

            if verbose:
                console.print()
                build_info = version_ops.get_build_info()
                console.print("[bold]Build Information:[/bold]")
                console.print(f"  Python: {build_info['python_version']}")
                console.print(f"  Platform: {build_info['platform']}")
                console.print(
                    f"  OTEL: {'enabled' if build_info['otel_available'] else 'disabled'}"
                )

                if build_info.get("dependencies"):
                    console.print()
                    console.print("[bold]Dependencies:[/bold]")
                    for dep, ver in build_info["dependencies"].items():
                        console.print(f"  {dep}: {ver}")

    except KeyboardInterrupt:
        console.print()
        colour("Operation cancelled.", "yellow")
        raise typer.Exit(130)

    except Exception as e:
        console.print()
        colour(f"[red]Error getting version:[/red] {e}", "red")
        raise typer.Exit(1)


# Standalone version callback for main app
def version_callback(value: bool) -> None:
    """Callback for --version flag on main app."""
    if value:
        console.print(f"specify-cli {version_ops.get_current_version()}")
        raise typer.Exit
