"""
specify_cli.commands.init - Init Command
=========================================

CLI command handler for project initialization.

This module provides the Typer command interface for initializing
new specify projects. It handles argument parsing, user interaction,
and output formatting, delegating business logic to the ops layer.

Examples
--------
    $ specify init my-project
    $ specify init my-project --ai claude
    $ specify init --here

See Also
--------
- :mod:`specify_cli.ops.init` : Business logic
- :mod:`specify_cli.runtime` : Runtime execution
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from specify_cli.core.instrumentation import instrument_command
from specify_cli.core.shell import colour
from specify_cli.ops import init as init_ops

console = Console()

app = typer.Typer(
    name="init",
    help="Initialize a new Specify project from the latest template.",
)


def _select_ai_assistant_interactive() -> str:
    """Interactively select AI assistant."""
    from specify_cli.utils.progress import select_with_arrows

    options = {
        "claude": "Claude (Anthropic)",
        "cursor": "Cursor",
        "copilot": "GitHub Copilot",
    }

    selected = select_with_arrows(options, prompt_text="Select AI Assistant")
    return selected


@app.callback(invoke_without_command=True)
@instrument_command("init", track_args=True)
def init(
    ctx: typer.Context,
    project_name: Optional[str] = typer.Argument(
        None,
        help="Name of the project to create. Omit if using --here.",
    ),
    ai_assistant: Optional[str] = typer.Option(
        None,
        "--ai",
        "-a",
        help="AI assistant type (claude, cursor, copilot).",
    ),
    script_type: str = typer.Option(
        "sh",
        "--script",
        "-s",
        help="Script type for helper scripts (sh or ps1).",
    ),
    here: bool = typer.Option(
        False,
        "--here",
        "-H",
        help="Initialize in current directory instead of creating new.",
    ),
    no_git: bool = typer.Option(
        False,
        "--no-git",
        help="Skip git repository initialization.",
    ),
    github_token: Optional[str] = typer.Option(
        None,
        "--github-token",
        envvar="GH_TOKEN",
        help="GitHub token for authenticated requests.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output.",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug output.",
    ),
) -> None:
    """Initialize a new Specify project from the latest template.

    Creates a new project directory with the Specify spec-driven development
    template, configured for your preferred AI assistant.

    Examples:
        specify init my-project
        specify init my-project --ai claude
        specify init --here --ai cursor
    """
    # Validate arguments
    if not project_name and not here:
        console.print("[red]Error:[/red] Either provide a project name or use --here flag.")
        console.print("\nUsage:")
        console.print("  specify init [PROJECT_NAME]")
        console.print("  specify init --here")
        raise typer.Exit(1)

    if project_name and here:
        console.print("[red]Error:[/red] Cannot specify both project name and --here flag.")
        raise typer.Exit(1)

    # Interactive AI assistant selection if not specified
    if not ai_assistant:
        try:
            ai_assistant = _select_ai_assistant_interactive()
        except (ImportError, KeyboardInterrupt):
            ai_assistant = "claude"
            if verbose:
                console.print(f"[dim]Using default AI assistant: {ai_assistant}[/dim]")

    # Show what we're doing
    if here:
        console.print(f"\n[cyan]Initializing Specify project in current directory...[/cyan]")
    else:
        console.print(f"\n[cyan]Creating Specify project:[/cyan] {project_name}")

    console.print(f"[cyan]AI Assistant:[/cyan] {ai_assistant}")
    console.print(f"[cyan]Script Type:[/cyan] {script_type}")
    console.print()

    try:
        # Call ops layer
        result = init_ops.initialize_project(
            name=project_name,
            ai_assistant=ai_assistant,
            script_type=script_type,
            here=here,
            no_git=no_git,
            github_token=github_token,
        )

        if result.success:
            # Success output
            console.print()
            colour(f"[green]✓[/green] Project initialized successfully!", "green")
            console.print()

            console.print(f"[bold]Project Path:[/bold] {result.project_path}")
            console.print(f"[bold]AI Assistant:[/bold] {result.ai_assistant}")
            console.print(f"[bold]Template Version:[/bold] {result.release_tag}")

            if result.git_initialized:
                console.print(f"[bold]Git:[/bold] Initialized with initial commit")
            else:
                console.print(f"[bold]Git:[/bold] Skipped")

            if result.warnings:
                console.print()
                console.print("[yellow]Warnings:[/yellow]")
                for warning in result.warnings:
                    console.print(f"  • {warning}")

            console.print()
            console.print("[cyan]Next steps:[/cyan]")
            if not here:
                console.print(f"  1. cd {result.project_path.name}")
            console.print(f"  2. Review the README.md for getting started")
            console.print(f"  3. Run 'specify check' to verify your setup")

        else:
            # Failure output
            console.print()
            colour("[red]✗ Project initialization failed[/red]", "red")
            for error in result.errors:
                console.print(f"  • {error}")
            raise typer.Exit(1)

    except init_ops.InitError as e:
        console.print()
        console.print(Panel(
            str(e),
            title="Initialization Error",
            border_style="red",
        ))
        if e.suggestions:
            console.print()
            console.print("[yellow]Suggestions:[/yellow]")
            for suggestion in e.suggestions:
                console.print(f"  • {suggestion}")
        raise typer.Exit(1)

    except KeyboardInterrupt:
        console.print()
        colour("Operation cancelled.", "yellow")
        raise typer.Exit(130)

    except Exception as e:
        console.print()
        console.print(Panel(
            str(e),
            title="Unexpected Error",
            border_style="red",
        ))
        if debug:
            import traceback
            console.print()
            console.print("[dim]Stack trace:[/dim]")
            console.print(traceback.format_exc())
        raise typer.Exit(1)
