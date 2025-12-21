#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "typer",
#     "rich",
#     "platformdirs",
#     "readchar",
#     "httpx",
# ]
# ///
"""
Specify CLI - Setup tool for Specify projects
"""

import importlib.metadata
import os
import platform
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx
import typer
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text

# Import from refactored modules
from .cli import BannerGroup, show_banner
from .core import (
    _format_rate_limit_error,
    _github_auth_headers,
    init_git_repo,
    is_git_repo,
)
from .core.github import ssl_context
from .utils import (
    AGENT_CONFIG,
    BANNER,
    CLAUDE_LOCAL_PATH,
    SCRIPT_TYPE_CHOICES,
    TAGLINE,
    StepTracker,
    check_tool,
    download_and_extract_template,
    ensure_executable_scripts,
    get_key,
    run_command,
    select_with_arrows,
)

console = Console()

# Create global httpx client
client = httpx.Client(verify=ssl_context)

# Create the main Typer app
app = typer.Typer(
    name="specify",
    help="Setup tool for Specify spec-driven development projects",
    add_completion=False,
    invoke_without_command=True,
    cls=BannerGroup,
)


@app.callback()
def callback(ctx: typer.Context):
    """Show banner when no subcommand is provided."""
    if ctx.invoked_subcommand is None and "--help" not in sys.argv and "-h" not in sys.argv:
        show_banner()
        from rich.align import Align

        console.print(Align.center("[dim]Run 'specify --help' for usage information[/dim]"))
        console.print()


@app.command()
def init(
    project_name: str = typer.Argument(
        None,
        help="Name for your new project directory (optional if using --here, or use '.' for current directory)",
    ),
    ai_assistant: str = typer.Option(
        None,
        "--ai",
        help="AI assistant to use: claude, gemini, copilot, cursor-agent, qwen, opencode, codex, windsurf, kilocode, auggie, codebuddy, amp, shai, q, bob, or qoder ",
    ),
    script_type: str = typer.Option(None, "--script", help="Script type to use: sh or ps"),
    ignore_agent_tools: bool = typer.Option(
        False, "--ignore-agent-tools", help="Skip checks for AI agent tools like Claude Code"
    ),
    no_git: bool = typer.Option(False, "--no-git", help="Skip git repository initialization"),
    here: bool = typer.Option(
        False,
        "--here",
        help="Initialize project in the current directory instead of creating a new one",
    ),
    force: bool = typer.Option(
        False, "--force", help="Force merge/overwrite when using --here (skip confirmation)"
    ),
    skip_tls: bool = typer.Option(
        False, "--skip-tls", help="Skip SSL/TLS verification (not recommended)"
    ),
    debug: bool = typer.Option(
        False, "--debug", help="Show verbose diagnostic output for network and extraction failures"
    ),
    github_token: str = typer.Option(
        None,
        "--github-token",
        help="GitHub token to use for API requests (or set GH_TOKEN or GITHUB_TOKEN environment variable)",
    ),
):
    """
    Initialize a new Specify project from the latest template.

    This command will:
    1. Check that required tools are installed (git is optional)
    2. Let you choose your AI assistant
    3. Download the appropriate template from GitHub
    4. Extract the template to a new project directory or current directory
    5. Initialize a fresh git repository (if not --no-git and no existing repo)
    6. Optionally set up AI assistant commands

    Examples:
        specify init my-project
        specify init my-project --ai claude
        specify init my-project --ai copilot --no-git
        specify init --ignore-agent-tools my-project
        specify init . --ai claude         # Initialize in current directory
        specify init .                     # Initialize in current directory (interactive AI selection)
        specify init --here --ai claude    # Alternative syntax for current directory
        specify init --here --ai codex
        specify init --here --ai codebuddy
        specify init --here
        specify init --here --force  # Skip confirmation when current directory not empty
    """

    show_banner()

    if project_name == ".":
        here = True
        project_name = None  # Clear project_name to use existing validation logic

    if here and project_name:
        console.print("[red]Error:[/red] Cannot specify both project name and --here flag")
        raise typer.Exit(1)

    if not here and not project_name:
        console.print(
            "[red]Error:[/red] Must specify either a project name, use '.' for current directory, or use --here flag"
        )
        raise typer.Exit(1)

    if here:
        project_name = Path.cwd().name
        project_path = Path.cwd()

        existing_items = list(project_path.iterdir())
        if existing_items:
            console.print(
                f"[yellow]Warning:[/yellow] Current directory is not empty ({len(existing_items)} items)"
            )
            console.print(
                "[yellow]Template files will be merged with existing content and may overwrite existing files[/yellow]"
            )
            if force:
                console.print(
                    "[cyan]--force supplied: skipping confirmation and proceeding with merge[/cyan]"
                )
            else:
                response = typer.confirm("Do you want to continue?")
                if not response:
                    console.print("[yellow]Operation cancelled[/yellow]")
                    raise typer.Exit(0)
    else:
        project_path = Path(project_name).resolve()
        if project_path.exists():
            error_panel = Panel(
                f"Directory '[cyan]{project_name}[/cyan]' already exists\n"
                "Please choose a different project name or remove the existing directory.",
                title="[red]Directory Conflict[/red]",
                border_style="red",
                padding=(1, 2),
            )
            console.print()
            console.print(error_panel)
            raise typer.Exit(1)

    current_dir = Path.cwd()

    setup_lines = [
        "[cyan]Specify Project Setup[/cyan]",
        "",
        f"{'Project':<15} [green]{project_path.name}[/green]",
        f"{'Working Path':<15} [dim]{current_dir}[/dim]",
    ]

    if not here:
        setup_lines.append(f"{'Target Path':<15} [dim]{project_path}[/dim]")

    console.print(Panel("\n".join(setup_lines), border_style="cyan", padding=(1, 2)))

    should_init_git = False
    if not no_git:
        should_init_git = check_tool("git")
        if not should_init_git:
            console.print("[yellow]Git not found - will skip repository initialization[/yellow]")

    if ai_assistant:
        if ai_assistant not in AGENT_CONFIG:
            console.print(
                f"[red]Error:[/red] Invalid AI assistant '{ai_assistant}'. Choose from: {', '.join(AGENT_CONFIG.keys())}"
            )
            raise typer.Exit(1)
        selected_ai = ai_assistant
    else:
        # Create options dict for selection (agent_key: display_name)
        ai_choices = {key: config["name"] for key, config in AGENT_CONFIG.items()}
        selected_ai = select_with_arrows(ai_choices, "Choose your AI assistant:", "copilot")

    if not ignore_agent_tools:
        agent_config = AGENT_CONFIG.get(selected_ai)
        if agent_config and agent_config["requires_cli"]:
            install_url = agent_config["install_url"]
            if not check_tool(selected_ai):
                error_panel = Panel(
                    f"[cyan]{selected_ai}[/cyan] not found\n"
                    f"Install from: [cyan]{install_url}[/cyan]\n"
                    f"{agent_config['name']} is required to continue with this project type.\n\n"
                    "Tip: Use [cyan]--ignore-agent-tools[/cyan] to skip this check",
                    title="[red]Agent Detection Error[/red]",
                    border_style="red",
                    padding=(1, 2),
                )
                console.print()
                console.print(error_panel)
                raise typer.Exit(1)

    if script_type:
        if script_type not in SCRIPT_TYPE_CHOICES:
            console.print(
                f"[red]Error:[/red] Invalid script type '{script_type}'. Choose from: {', '.join(SCRIPT_TYPE_CHOICES.keys())}"
            )
            raise typer.Exit(1)
        selected_script = script_type
    else:
        default_script = "ps" if os.name == "nt" else "sh"

        if sys.stdin.isatty():
            selected_script = select_with_arrows(
                SCRIPT_TYPE_CHOICES, "Choose script type (or press Enter)", default_script
            )
        else:
            selected_script = default_script

    console.print(f"[cyan]Selected AI assistant:[/cyan] {selected_ai}")
    console.print(f"[cyan]Selected script type:[/cyan] {selected_script}")

    tracker = StepTracker("Initialize Specify Project")

    sys._specify_tracker_active = True

    tracker.add("precheck", "Check required tools")
    tracker.complete("precheck", "ok")
    tracker.add("ai-select", "Select AI assistant")
    tracker.complete("ai-select", f"{selected_ai}")
    tracker.add("script-select", "Select script type")
    tracker.complete("script-select", selected_script)
    for key, label in [
        ("fetch", "Fetch latest release"),
        ("download", "Download template"),
        ("extract", "Extract template"),
        ("zip-list", "Archive contents"),
        ("extracted-summary", "Extraction summary"),
        ("chmod", "Ensure scripts executable"),
        ("cleanup", "Cleanup"),
        ("git", "Initialize git repository"),
        ("final", "Finalize"),
    ]:
        tracker.add(key, label)

    # Track git error message outside Live context so it persists
    git_error_message = None

    with Live(tracker.render(), console=console, refresh_per_second=8, transient=True) as live:
        tracker.attach_refresh(lambda: live.update(tracker.render()))
        try:
            verify = not skip_tls
            local_ssl_context = ssl_context if verify else False
            local_client = httpx.Client(verify=local_ssl_context)

            download_and_extract_template(
                project_path,
                selected_ai,
                selected_script,
                here,
                verbose=False,
                tracker=tracker,
                client=local_client,
                debug=debug,
                github_token=github_token,
            )

            ensure_executable_scripts(project_path, tracker=tracker)

            if not no_git:
                tracker.start("git")
                if is_git_repo(project_path):
                    tracker.complete("git", "existing repo detected")
                elif should_init_git:
                    success, error_msg = init_git_repo(project_path, quiet=True)
                    if success:
                        tracker.complete("git", "initialized")
                    else:
                        tracker.error("git", "init failed")
                        git_error_message = error_msg
                else:
                    tracker.skip("git", "git not available")
            else:
                tracker.skip("git", "--no-git flag")

            tracker.complete("final", "project ready")
        except Exception as e:
            tracker.error("final", str(e))
            console.print(Panel(f"Initialization failed: {e}", title="Failure", border_style="red"))
            if debug:
                _env_pairs = [
                    ("Python", sys.version.split()[0]),
                    ("Platform", sys.platform),
                    ("CWD", str(Path.cwd())),
                ]
                _label_width = max(len(k) for k, _ in _env_pairs)
                env_lines = [
                    f"{k.ljust(_label_width)} → [bright_black]{v}[/bright_black]"
                    for k, v in _env_pairs
                ]
                console.print(
                    Panel("\n".join(env_lines), title="Debug Environment", border_style="magenta")
                )
            if not here and project_path.exists():
                shutil.rmtree(project_path)
            raise typer.Exit(1)
        finally:
            pass

    console.print(tracker.render())
    console.print("\n[bold green]Project ready.[/bold green]")

    # Show git error details if initialization failed
    if git_error_message:
        console.print()
        git_error_panel = Panel(
            f"[yellow]Warning:[/yellow] Git repository initialization failed\n\n"
            f"{git_error_message}\n\n"
            f"[dim]You can initialize git manually later with:[/dim]\n"
            f"[cyan]cd {project_path if not here else '.'}[/cyan]\n"
            f"[cyan]git init[/cyan]\n"
            f"[cyan]git add .[/cyan]\n"
            f'[cyan]git commit -m "Initial commit"[/cyan]',
            title="[red]Git Initialization Failed[/red]",
            border_style="red",
            padding=(1, 2),
        )
        console.print(git_error_panel)

    # Agent folder security notice
    agent_config = AGENT_CONFIG.get(selected_ai)
    if agent_config:
        agent_folder = agent_config["folder"]
        security_notice = Panel(
            f"Some agents may store credentials, auth tokens, or other identifying and private artifacts in the agent folder within your project.\n"
            f"Consider adding [cyan]{agent_folder}[/cyan] (or parts of it) to [cyan].gitignore[/cyan] to prevent accidental credential leakage.",
            title="[yellow]Agent Folder Security[/yellow]",
            border_style="yellow",
            padding=(1, 2),
        )
        console.print()
        console.print(security_notice)

    import shlex

    steps_lines = []
    if not here:
        steps_lines.append(f"1. Go to the project folder: [cyan]cd {project_name}[/cyan]")
        step_num = 2
    else:
        steps_lines.append("1. You're already in the project directory!")
        step_num = 2

    # Add Codex-specific setup step if needed
    if selected_ai == "codex":
        codex_path = project_path / ".codex"
        quoted_path = shlex.quote(str(codex_path))
        if os.name == "nt":  # Windows
            cmd = f"setx CODEX_HOME {quoted_path}"
        else:  # Unix-like systems
            cmd = f"export CODEX_HOME={quoted_path}"

        steps_lines.append(
            f"{step_num}. Set [cyan]CODEX_HOME[/cyan] environment variable before running Codex: [cyan]{cmd}[/cyan]"
        )
        step_num += 1

    steps_lines.append(f"{step_num}. Start using slash commands with your AI agent:")

    steps_lines.append("   2.1 [cyan]/speckit.constitution[/] - Establish project principles")
    steps_lines.append("   2.2 [cyan]/speckit.specify[/] - Create baseline specification")
    steps_lines.append("   2.3 [cyan]/speckit.plan[/] - Create implementation plan")
    steps_lines.append("   2.4 [cyan]/speckit.tasks[/] - Generate actionable tasks")
    steps_lines.append("   2.5 [cyan]/speckit.implement[/] - Execute implementation")

    steps_panel = Panel(
        "\n".join(steps_lines), title="Next Steps", border_style="cyan", padding=(1, 2)
    )
    console.print()
    console.print(steps_panel)

    enhancement_lines = [
        "Optional commands that you can use for your specs [bright_black](improve quality & confidence)[/bright_black]",
        "",
        "○ [cyan]/speckit.clarify[/] [bright_black](optional)[/bright_black] - Ask structured questions to de-risk ambiguous areas before planning (run before [cyan]/speckit.plan[/] if used)",
        "○ [cyan]/speckit.analyze[/] [bright_black](optional)[/bright_black] - Cross-artifact consistency & alignment report (after [cyan]/speckit.tasks[/], before [cyan]/speckit.implement[/])",
        "○ [cyan]/speckit.checklist[/] [bright_black](optional)[/bright_black] - Generate quality checklists to validate requirements completeness, clarity, and consistency (after [cyan]/speckit.plan[/])",
    ]
    enhancements_panel = Panel(
        "\n".join(enhancement_lines),
        title="Enhancement Commands",
        border_style="cyan",
        padding=(1, 2),
    )
    console.print()
    console.print(enhancements_panel)


# NOTE: Old check command removed - now using refactored version from commands/check.py
# The refactored check command provides:
# - --verbose/-v flag for detailed output
# - --json flag for JSON output
# - Better separation of concerns (commands/ops/runtime layers)


# =============================================================================
# Process Mining Commands
# =============================================================================

pm_app = typer.Typer(
    name="pm",
    help="Process mining commands using pm4py",
    add_completion=False,
)
app.add_typer(pm_app, name="pm")

# Add SpiffWorkflow self-automation commands (optional)
try:
    from specify_cli.spiff_automation import create_self_automating_cli

    automate_app = create_self_automating_cli()
    app.add_typer(automate_app, name="automate")
except ImportError:
    pass  # SpiffWorkflow not installed


def _load_event_log(
    file_path: Path,
    case_id: str = "case:concept:name",
    activity: str = "concept:name",
    timestamp: str = "time:timestamp",
):
    """Load event log from CSV/XES file."""
    try:
        import pm4py

        if file_path.suffix.lower() == ".xes":
            return pm4py.read_xes(str(file_path))
        if file_path.suffix.lower() == ".csv":
            df = pm4py.read_csv(str(file_path))
            return pm4py.convert_to_event_log(
                df, case_id=case_id, activity_key=activity, timestamp_key=timestamp
            )
        raise ValueError(f"Unsupported file format: {file_path.suffix}")
    except ImportError:
        raise RuntimeError("pm4py is not installed. Install it with: pip install pm4py")


def _save_model(model, output_path: Path, model_type: str = "petri"):
    """Save a model to file."""
    try:
        import pm4py

        if model_type == "petri" and hasattr(model, "__iter__") and len(model) == 3:
            net, im, fm = model
            pm4py.write_petri_net(net, str(output_path), im, fm)
        elif model_type == "process_tree":
            pm4py.write_process_tree(model, str(output_path))
        elif hasattr(model, "to_file"):
            model.to_file(str(output_path))
        else:
            raise ValueError(f"Cannot save model of type {type(model)}")
    except ImportError:
        raise RuntimeError("pm4py is not installed. Install it with: pip install pm4py")


@pm_app.command("discover")
def pm_discover(
    input_file: Path = typer.Argument(..., help="Input event log file (CSV or XES)"),
    output_file: Path = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file for discovered model (default: input_name_model.pnml)",
    ),
    model_type: str = typer.Option("petri", "--type", "-t", help="Model type: petri or tree"),
    case_id: str = typer.Option("case:concept:name", "--case-id", help="Column name for case ID"),
    activity: str = typer.Option("concept:name", "--activity", help="Column name for activity"),
    timestamp: str = typer.Option(
        "time:timestamp", "--timestamp", help="Column name for timestamp"
    ),
):
    """Discover a process model from an event log using the Inductive Miner."""
    try:
        import pm4py

        if not input_file.exists():
            console.print(f"[red]Error:[/red] Input file not found: {input_file}")
            raise typer.Exit(1)

        console.print(f"[cyan]Loading event log from:[/cyan] {input_file}")
        event_log = _load_event_log(
            input_file, case_id=case_id, activity=activity, timestamp=timestamp
        )

        console.print(
            f"[cyan]Event log loaded:[/cyan] {len(event_log)} cases, {len(event_log.get_events())} events"
        )

        tracker = StepTracker("Process Discovery")
        tracker.add("discover", "Discover model using Inductive Miner")

        with Live(tracker.render(), console=console, refresh_per_second=2, transient=True) as live:
            tracker.attach_refresh(lambda: live.update(tracker.render()))
            tracker.start("discover")

            if model_type == "tree":
                model = pm4py.discover_process_tree_inductive(event_log)
            else:
                model = pm4py.discover_petri_net_inductive(event_log)

            tracker.complete("discover", f"{model_type} net discovered")

            if output_file is None:
                output_file = input_file.parent / f"{input_file.stem}_model.pnml"

            tracker.add("save", "Save model to file")
            tracker.start("save")

            _save_model(model, output_file, model_type)
            tracker.complete("save", str(output_file))

        console.print(tracker.render())
        console.print(
            f"\n[bold green]Model discovered and saved to:[/bold green] [cyan]{output_file}[/cyan]"
        )

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@pm_app.command("conform")
def pm_conform(
    input_file: Path = typer.Argument(..., help="Input event log file (CSV or XES)"),
    model_file: Path = typer.Argument(..., help="Process model file (PNML)"),
    case_id: str = typer.Option("case:concept:name", "--case-id", help="Column name for case ID"),
    activity: str = typer.Option("concept:name", "--activity", help="Column name for activity"),
    timestamp: str = typer.Option(
        "time:timestamp", "--timestamp", help="Column name for timestamp"
    ),
):
    """Check log conformance against a process model."""
    try:
        import pm4py

        if not input_file.exists():
            console.print(f"[red]Error:[/red] Input file not found: {input_file}")
            raise typer.Exit(1)

        if not model_file.exists():
            console.print(f"[red]Error:[/red] Model file not found: {model_file}")
            raise typer.Exit(1)

        console.print(f"[cyan]Loading event log:[/cyan] {input_file}")
        event_log = _load_event_log(
            input_file, case_id=case_id, activity=activity, timestamp=timestamp
        )

        console.print(f"[cyan]Loading model:[/cyan] {model_file}")
        net, im, fm = pm4py.read_petri_net(str(model_file))

        tracker = StepTracker("Conformance Checking")
        tracker.add("conformance", "Check conformance")

        with Live(tracker.render(), console=console, refresh_per_second=2, transient=True) as live:
            tracker.attach_refresh(lambda: live.update(tracker.render()))
            tracker.start("conformance")

            fitness = pm4py.fitness_petri_net_token_based_replay(event_log, net, im, fm)
            precision = pm4py.precision_petri_net(event_log, net, im, fm)

            tracker.complete("conformance", f"fitness={fitness:.2%}, precision={precision:.2%}")

        console.print(tracker.render())
        console.print()

        # Show results
        result_table = Table(
            title="Conformance Results", show_header=True, header_style="bold cyan"
        )
        result_table.add_column("Metric", style="cyan")
        result_table.add_column("Value", style="white")

        result_table.add_row("Fitness", f"{fitness:.2%}")
        result_table.add_row("Precision", f"{precision:.2%}")

        console.print(result_table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@pm_app.command("stats")
def pm_stats(
    input_file: Path = typer.Argument(..., help="Input event log file (CSV or XES)"),
    case_id: str = typer.Option("case:concept:name", "--case-id", help="Column name for case ID"),
    activity: str = typer.Option("concept:name", "--activity", help="Column name for activity"),
    timestamp: str = typer.Option(
        "time:timestamp", "--timestamp", help="Column name for timestamp"
    ),
):
    """Analyze event log statistics."""
    try:
        import statistics

        import pm4py

        if not input_file.exists():
            console.print(f"[red]Error:[/red] Input file not found: {input_file}")
            raise typer.Exit(1)

        console.print(f"[cyan]Loading event log:[/cyan] {input_file}")
        event_log = _load_event_log(
            input_file, case_id=case_id, activity=activity, timestamp=timestamp
        )

        tracker = StepTracker("Event Log Analysis")
        tracker.add("stats", "Calculate statistics")

        with Live(tracker.render(), console=console, refresh_per_second=2, transient=True) as live:
            tracker.attach_refresh(lambda: live.update(tracker.render()))
            tracker.start("stats")

            # Compute stats
            cases_count = len(event_log)
            events_count = sum(len(case) for case in event_log)

            trace_lengths = [len(case) for case in event_log]
            min_trace = min(trace_lengths)
            max_trace = max(trace_lengths)
            avg_trace = statistics.mean(trace_lengths)

            activities = set()
            for case in event_log:
                for event in case:
                    if activity in event:
                        activities.add(event[activity])

            tracker.complete("stats", f"{cases_count} cases, {events_count} events")

        console.print(tracker.render())
        console.print()

        # Show results
        stats_table = Table(
            title="Event Log Statistics", show_header=True, header_style="bold cyan"
        )
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="white")

        stats_table.add_row("Total Cases", str(cases_count))
        stats_table.add_row("Total Events", str(events_count))
        stats_table.add_row("Unique Activities", str(len(activities)))
        stats_table.add_row("Min Trace Length", str(min_trace))
        stats_table.add_row("Max Trace Length", str(max_trace))
        stats_table.add_row("Avg Trace Length", f"{avg_trace:.2f}")

        console.print(stats_table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@pm_app.command("convert")
def pm_convert(
    input_file: Path = typer.Argument(..., help="Input file (CSV, XES, or PNML)"),
    output_file: Path = typer.Argument(..., help="Output file (CSV, XES, or PNML)"),
    case_id: str = typer.Option("case:concept:name", "--case-id", help="Column name for case ID"),
    activity: str = typer.Option("concept:name", "--activity", help="Column name for activity"),
    timestamp: str = typer.Option(
        "time:timestamp", "--timestamp", help="Column name for timestamp"
    ),
):
    """Convert between event log and model formats."""
    try:
        import pm4py

        if not input_file.exists():
            console.print(f"[red]Error:[/red] Input file not found: {input_file}")
            raise typer.Exit(1)

        console.print(f"[cyan]Loading:[/cyan] {input_file}")

        tracker = StepTracker("Format Conversion")
        tracker.add("load", "Load file")
        tracker.add("convert", "Convert format")
        tracker.add("save", "Save file")

        with Live(tracker.render(), console=console, refresh_per_second=2, transient=True) as live:
            tracker.attach_refresh(lambda: live.update(tracker.render()))

            tracker.start("load")
            if input_file.suffix.lower() == ".pnml":
                net, im, fm = pm4py.read_petri_net(str(input_file))
                tracker.complete("load", "Petri net")
            else:
                event_log = _load_event_log(
                    input_file, case_id=case_id, activity=activity, timestamp=timestamp
                )
                tracker.complete("load", f"Event log ({input_file.suffix})")

            tracker.start("convert")
            out_suffix = output_file.suffix.lower()

            if out_suffix == ".pnml":
                if input_file.suffix.lower() != ".pnml":
                    net, im, fm = pm4py.discover_petri_net_inductive(event_log)
                    tracker.complete("convert", "Petri net model")
            elif out_suffix in [".csv", ".xes"]:
                if input_file.suffix.lower() == ".pnml":
                    tracker.error("convert", "cannot convert model to log")
                    raise RuntimeError("Cannot convert Petri net model to event log")
                tracker.complete("convert", out_suffix)
            else:
                tracker.error("convert", f"unsupported format: {out_suffix}")
                raise typer.Exit(1)

            tracker.start("save")
            if out_suffix == ".csv" and "event_log" in locals():
                pm4py.write_csv(event_log, str(output_file))
            elif out_suffix == ".xes" and "event_log" in locals():
                pm4py.write_xes(event_log, str(output_file))
            elif out_suffix == ".pnml" and "net" in locals():
                pm4py.write_petri_net(net, str(output_file), im, fm)
            else:
                tracker.error("save", f"unsupported format: {out_suffix}")
                raise typer.Exit(1)
            tracker.complete("save", output_file.name)

        console.print(tracker.render())
        console.print("\n[bold green]Conversion complete.[/bold green]")
        console.print(f"Output: [cyan]{output_file}[/cyan]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@pm_app.command("visualize")
def pm_visualize(
    input_file: Path = typer.Argument(..., help="Input file (event log CSV/XES or model PNML)"),
    output_file: Path = typer.Option(
        None, "--output", "-o", help="Output image file (PNG, SVG, etc.)"
    ),
    case_id: str = typer.Option("case:concept:name", "--case-id", help="Column name for case ID"),
    activity: str = typer.Option("concept:name", "--activity", help="Column name for activity"),
    timestamp: str = typer.Option(
        "time:timestamp", "--timestamp", help="Column name for timestamp"
    ),
):
    """Visualize a process model or event log."""
    try:
        import pm4py

        if not input_file.exists():
            console.print(f"[red]Error:[/red] Input file not found: {input_file}")
            raise typer.Exit(1)

        console.print(f"[cyan]Loading:[/cyan] {input_file}")

        tracker = StepTracker("Visualization")
        tracker.add("load", "Load file")
        tracker.add("visualize", "Generate visualization")

        with Live(tracker.render(), console=console, refresh_per_second=2, transient=True) as live:
            tracker.attach_refresh(lambda: live.update(tracker.render()))

            tracker.start("load")
            if input_file.suffix.lower() == ".pnml":
                net, im, fm = pm4py.read_petri_net(str(input_file))
                tracker.complete("load", "Petri net")

                tracker.start("visualize")
                gviz = pm4py.vis_petri_net(net, im, fm)
                tracker.complete("visualize", "Petri net diagram")
            else:
                event_log = _load_event_log(
                    input_file, case_id=case_id, activity=activity, timestamp=timestamp
                )
                tracker.complete("load", f"Event log ({input_file.suffix})")

                tracker.start("visualize")
                process_tree = pm4py.discover_process_tree_inductive(event_log)
                gviz = pm4py.vis_process_tree(process_tree)
                tracker.complete("visualize", "Process tree diagram")

            if output_file is None:
                output_file = input_file.parent / f"{input_file.stem}_viz"

            gviz.render(str(output_file), format="png", cleanup=True)

        console.print(tracker.render())
        console.print(
            f"\n[bold green]Visualization saved:[/bold green] [cyan]{output_file}.png[/cyan]"
        )

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@pm_app.command("filter")
def pm_filter(
    input_file: Path = typer.Argument(..., help="Input event log file (CSV or XES)"),
    output_file: Path = typer.Option(
        None, "--output", "-o", help="Output file (default: input_name_filtered.csv)"
    ),
    min_support: float = typer.Option(
        0.1, "--min-support", "-s", help="Minimum support threshold (0.0-1.0)"
    ),
    max_duration: int = typer.Option(
        None, "--max-duration", "-d", help="Maximum trace duration in seconds"
    ),
    case_id: str = typer.Option("case:concept:name", "--case-id", help="Column name for case ID"),
    activity: str = typer.Option("concept:name", "--activity", help="Column name for activity"),
    timestamp: str = typer.Option(
        "time:timestamp", "--timestamp", help="Column name for timestamp"
    ),
):
    """Filter an event log by support and other criteria."""
    try:
        import pm4py

        if not input_file.exists():
            console.print(f"[red]Error:[/red] Input file not found: {input_file}")
            raise typer.Exit(1)

        console.print(f"[cyan]Loading event log:[/cyan] {input_file}")
        event_log = _load_event_log(
            input_file, case_id=case_id, activity=activity, timestamp=timestamp
        )

        tracker = StepTracker("Event Log Filtering")
        tracker.add("filter", "Filter event log")

        with Live(tracker.render(), console=console, refresh_per_second=2, transient=True) as live:
            tracker.attach_refresh(lambda: live.update(tracker.render()))

            tracker.start("filter")

            # Apply filtering
            if min_support > 0:
                filtered_log = pm4py.filter_log_events_percentage(event_log, min_support)
            else:
                filtered_log = event_log

            original_size = len(event_log)
            filtered_size = len(filtered_log)

            tracker.complete("filter", f"reduced to {filtered_size}/{original_size} cases")

            if output_file is None:
                output_file = input_file.parent / f"{input_file.stem}_filtered.csv"

            tracker.add("save", "Save filtered log")
            tracker.start("save")

            pm4py.write_csv(filtered_log, str(output_file))
            tracker.complete("save", output_file.name)

        console.print(tracker.render())
        console.print("\n[bold green]Filtering complete.[/bold green]")
        console.print(f"Original cases: {original_size}, Filtered cases: {filtered_size}")
        console.print(f"Output: [cyan]{output_file}[/cyan]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@pm_app.command("sample")
def pm_sample(
    output_file: Path = typer.Argument(..., help="Output event log file (CSV or XES)"),
    cases: int = typer.Option(100, "--cases", "-c", help="Number of cases to generate"),
    activities: int = typer.Option(5, "--activities", "-a", help="Number of activities"),
    min_trace_length: int = typer.Option(3, "--min-trace", help="Minimum events per trace"),
    max_trace_length: int = typer.Option(10, "--max-trace", help="Maximum events per trace"),
    seed: int = typer.Option(None, "--seed", help="Random seed for reproducibility"),
):
    """Generate a sample event log for testing."""
    try:
        import random
        from datetime import datetime, timedelta

        import pm4py

        if output_file.exists():
            console.print(
                f"[yellow]Warning:[/yellow] Output file exists, will overwrite: {output_file}"
            )

        tracker = StepTracker("Sample Log Generation")
        tracker.add("generate", "Generate sample log")
        tracker.add("save", "Save to file")

        with Live(tracker.render(), console=console, refresh_per_second=2, transient=True) as live:
            tracker.attach_refresh(lambda: live.update(tracker.render()))

            tracker.start("generate")

            if seed is not None:
                random.seed(seed)

            event_log = []
            activity_names = [f"Activity_{i + 1}" for i in range(activities)]
            start_date = datetime(2024, 1, 1)

            total_events = 0
            for case_id in range(cases):
                trace_length = random.randint(min_trace_length, max_trace_length)
                current_time = start_date + timedelta(days=case_id)

                for _event_idx in range(trace_length):
                    event = {
                        "case:concept:name": f"Case_{case_id + 1:05d}",
                        "concept:name": random.choice(activity_names),
                        "time:timestamp": current_time.isoformat(),
                    }
                    event_log.append(event)
                    current_time += timedelta(hours=random.randint(1, 8))
                    total_events += 1

            tracker.complete("generate", f"generated {total_events} events")

            tracker.add("save", "Save to file")
            tracker.start("save")

            out_suffix = output_file.suffix.lower()
            if out_suffix == ".csv":
                import csv

                with open(output_file, "w", newline="") as f:
                    writer = csv.DictWriter(
                        f, fieldnames=["case:concept:name", "concept:name", "time:timestamp"]
                    )
                    writer.writeheader()
                    writer.writerows(event_log)
            elif out_suffix == ".xes":
                # For XES, we need to create a proper log object
                import pandas as pd

                df = pd.DataFrame(event_log)
                xes_log = pm4py.convert_to_event_log(df)
                pm4py.write_xes(xes_log, str(output_file))
            else:
                tracker.error("save", f"unsupported format: {out_suffix}")
                raise typer.Exit(1)
            tracker.complete("save", output_file.name)

        console.print(tracker.render())
        console.print("\n[bold green]Sample log generated.[/bold green]")
        console.print(f"Output: [cyan]{output_file}[/cyan]")

        # Show summary
        summary_table = Table(
            title="Generated Log Summary", show_header=True, header_style="bold cyan"
        )
        summary_table.add_column("Parameter", style="cyan")
        summary_table.add_column("Value", style="white")

        summary_table.add_row("Cases", str(cases))
        summary_table.add_row("Events", str(total_events))
        summary_table.add_row("Activities", str(activities))
        summary_table.add_row("Trace Length", f"{min_trace_length}-{max_trace_length}")
        if seed is not None:
            summary_table.add_row("Seed", str(seed))

        console.print()
        console.print(summary_table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


# =============================================================================
# End Process Mining Commands
# =============================================================================

# =============================================================================
# Workflow Automation Commands (SpiffWorkflow)
# =============================================================================

wf_app = typer.Typer(
    name="wf",
    help="Workflow automation commands using SpiffWorkflow",
    add_completion=False,
)

app.add_typer(wf_app, name="wf")


def _load_workflow(file_path: Path) -> tuple:
    """Load a BPMN workflow file and return the parser and spec."""
    from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser
    from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

    if not file_path.exists():
        raise FileNotFoundError(f"Workflow file not found: {file_path}")

    if file_path.suffix.lower() != ".bpmn":
        raise ValueError(f"Expected .bpmn file, got: {file_path.suffix}")

    parser = BpmnParser()
    with open(file_path) as f:
        parser.parse_file(f)

    workflow_spec = parser.get_spec(next(iter(parser.processes.keys())))
    return parser, workflow_spec


def _save_workflow(workflow_spec, output_path: Path) -> None:
    """Save workflow spec to BPMN file.

    Note: SpiffWorkflow doesn't support BPMN serialization/export.
    Use the source BPMN file directly or external BPMN editors.

    Raises:
        ValueError: BPMN export not supported by SpiffWorkflow.

    TODO v1.1: Consider adding BPMN export via lxml reconstruction
    """
    if output_path.suffix.lower() != ".bpmn":
        raise ValueError(f"Expected .bpmn output file, got: {output_path.suffix}")

    # SpiffWorkflow parser is read-only, does not support serialization
    raise ValueError(
        "BPMN export not supported by SpiffWorkflow. "
        "Use source BPMN file or external BPMN editor (e.g., Camunda Modeler) instead."
    )


def _validate_bpmn(file_path: Path) -> dict:
    """Validate a BPMN file for correctness."""
    import xml.etree.ElementTree as ET

    try:
        tree = ET.parse(str(file_path))
        root = tree.getroot()

        # Basic validation checks
        validation = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "root_tag": root.tag,
            "namespaces": list[Any](root.attrib.keys()) if hasattr(root, "attrib") else [],
        }

        # Check for required elements
        processes = root.findall(".//{http://www.omg.org/spec/BPMN/20100524/MODEL}process")
        if not processes:
            validation["warnings"].append("No BPMN processes found")

        # Try to load with SpiffWorkflow parser for deeper validation
        try:
            from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser

            parser = BpmnParser()
            with open(file_path) as f:
                parser.parse_file(f)
            validation["processes_found"] = len(parser.processes)
        except Exception as e:
            validation["valid"] = False
            validation["errors"].append(f"SpiffWorkflow parsing failed: {e!s}")

        return validation

    except ET.ParseError as e:
        return {
            "valid": False,
            "errors": [f"XML parsing error: {e!s}"],
            "warnings": [],
        }
    except Exception as e:
        return {
            "valid": False,
            "errors": [f"Validation failed: {e!s}"],
            "warnings": [],
        }


def _parse_workflow_structure(file_path: Path) -> dict:
    """Parse and extract workflow structure information."""
    import xml.etree.ElementTree as ET

    tree = ET.parse(str(file_path))
    root = tree.getroot()

    # Define BPMN namespace
    ns = {"bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL"}

    structure = {
        "processes": [],
        "tasks": [],
        "gateways": [],
        "events": [],
        "flows": [],
    }

    # Extract processes
    for process in root.findall(".//bpmn:process", ns):
        process_id = process.get("id", "unknown")
        process_name = process.get("name", process_id)
        structure["processes"].append(
            {
                "id": process_id,
                "name": process_name,
                "is_executable": process.get("isExecutable", "false") == "true",
            }
        )

    # Extract tasks
    for task in root.findall(".//bpmn:task", ns):
        task_id = task.get("id", "unknown")
        task_name = task.get("name", task_id)
        structure["tasks"].append(
            {
                "id": task_id,
                "name": task_name,
                "type": "Task",
            }
        )

    # Extract service tasks
    for task in root.findall(".//bpmn:serviceTask", ns):
        task_id = task.get("id", "unknown")
        task_name = task.get("name", task_id)
        structure["tasks"].append(
            {
                "id": task_id,
                "name": task_name,
                "type": "ServiceTask",
            }
        )

    # Extract user tasks
    for task in root.findall(".//bpmn:userTask", ns):
        task_id = task.get("id", "unknown")
        task_name = task.get("name", task_id)
        structure["tasks"].append(
            {
                "id": task_id,
                "name": task_name,
                "type": "UserTask",
            }
        )

    # Extract gateways
    for gateway in root.findall(".//bpmn:exclusiveGateway", ns):
        gateway_id = gateway.get("id", "unknown")
        gateway_name = gateway.get("name", gateway_id)
        structure["gateways"].append(
            {
                "id": gateway_id,
                "name": gateway_name,
                "type": "ExclusiveGateway",
            }
        )

    # Extract events
    for event in root.findall(".//bpmn:startEvent", ns):
        event_id = event.get("id", "unknown")
        event_name = event.get("name", event_id)
        structure["events"].append(
            {
                "id": event_id,
                "name": event_name,
                "type": "StartEvent",
            }
        )

    for event in root.findall(".//bpmn:endEvent", ns):
        event_id = event.get("id", "unknown")
        event_name = event.get("name", event_id)
        structure["events"].append(
            {
                "id": event_id,
                "name": event_name,
                "type": "EndEvent",
            }
        )

    # Extract flows
    for flow in root.findall(".//bpmn:sequenceFlow", ns):
        flow_id = flow.get("id", "unknown")
        source = flow.get("sourceRef", "unknown")
        target = flow.get("targetRef", "unknown")
        structure["flows"].append(
            {
                "id": flow_id,
                "source": source,
                "target": target,
            }
        )

    return structure


@wf_app.command("execute")
def wf_execute(
    workflow_file: Path = typer.Argument(..., help="BPMN workflow file (.bpmn)"),
    variables: str | None = typer.Option(
        None, "--variables", "-v", help="JSON string with workflow variables"
    ),
    trace: bool = typer.Option(False, "--trace", "-t", help="Show execution trace"),
    output: Path | None = typer.Option(
        None, "--output", "-o", help="Save execution output to file"
    ),
):
    """
    Execute a BPMN workflow with optional variables.

    Examples:
        specify wf execute workflow.bpmn
        specify wf execute workflow.bpmn --variables '{"name": "John", "amount": 1000}'
        specify wf execute workflow.bpmn --trace -o result.json
    """
    from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser
    from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

    if not workflow_file.exists():
        console.print(f"[red]Error:[/red] Workflow file not found: {workflow_file}")
        raise typer.Exit(1)

    tracker = StepTracker("Workflow Execution")
    tracker.add("load", "Load workflow")
    tracker.add("parse", "Parse workflow spec")
    tracker.add("execute", "Execute workflow")
    tracker.add("save", "Save results")

    with Live(tracker.render(), console=console, refresh_per_second=8, transient=True) as live:
        tracker.attach_refresh(lambda: live.update(tracker.render()))

        try:
            tracker.start("load")
            parser = BpmnParser()
            with open(workflow_file) as f:
                parser.parse_file(f)
            tracker.complete("load", workflow_file.name)

            tracker.start("parse")
            workflow_spec = parser.get_spec(next(iter(parser.processes.keys())))
            workflow = BpmnWorkflow(workflow_spec)
            tracker.complete("parse", f"{len(parser.processes)} process(es)")

            tracker.start("execute")

            # Parse and set variables if provided
            wf_variables = {}
            if variables:
                try:
                    wf_variables = json.loads(variables)
                except json.JSONDecodeError as e:
                    tracker.error("execute", f"Invalid JSON variables: {e}")
                    raise typer.Exit(1)

            # Execute workflow
            workflow.do_engine_steps()
            for task in workflow.get_ready_user_tasks():
                # Set task variables
                for key, value in wf_variables.items():
                    task.data[key] = value
                task.complete()
                workflow.complete_task_from_id(task.id)
                workflow.do_engine_steps()

            # Collect execution data
            execution_data = {
                "workflow_file": str(workflow_file),
                "status": "completed",
                "variables_input": wf_variables,
                "variables_output": workflow.data,
                "tasks_completed": len(workflow.completed_tasks),
                "trace": [],
            }

            if trace:
                # Build execution trace
                for task in workflow.completed_tasks:
                    execution_data["trace"].append(
                        {
                            "task_id": task.task_spec.name,
                            "status": "completed",
                        }
                    )

            tracker.complete("execute", f"{execution_data['tasks_completed']} task(s) completed")

            if output:
                tracker.start("save")
                with open(output, "w") as f:
                    json.dump(execution_data, f, indent=2)
                tracker.complete("save", str(output))
            else:
                tracker.skip("save", "no output specified")

        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    console.print(tracker.render())
    console.print("\n[bold green]Workflow executed successfully.[/bold green]")


@wf_app.command("validate")
def wf_validate(
    workflow_file: Path = typer.Argument(..., help="BPMN workflow file (.bpmn)"),
):
    """
    Validate a BPMN workflow file for correctness.

    Examples:
        specify wf validate workflow.bpmn
    """
    if not workflow_file.exists():
        console.print(f"[red]Error:[/red] Workflow file not found: {workflow_file}")
        raise typer.Exit(1)

    tracker = StepTracker("Workflow Validation")
    tracker.add("validate", "Validate BPMN file")

    with Live(tracker.render(), console=console, refresh_per_second=8, transient=True) as live:
        tracker.attach_refresh(lambda: live.update(tracker.render()))

        tracker.start("validate")
        validation = _validate_bpmn(workflow_file)

        if validation["valid"]:
            tracker.complete("validate", "all checks passed")
        else:
            tracker.error("validate", f"{len(validation['errors'])} error(s)")

    console.print(tracker.render())
    console.print()

    # Display validation results
    result_table = Table(title="Validation Results", show_header=True, header_style="bold cyan")
    result_table.add_column("Status", style="cyan")
    result_table.add_column("Value", style="white")

    result_table.add_row("Valid", "[green]✓[/green]" if validation["valid"] else "[red]✗[/red]")
    if validation.get("processes_found"):
        result_table.add_row("Processes", str(validation["processes_found"]))

    if validation["errors"]:
        result_table.add_row("Errors", "[red]" + ", ".join(validation["errors"]) + "[/red]")

    if validation["warnings"]:
        result_table.add_row(
            "Warnings", "[yellow]" + ", ".join(validation["warnings"]) + "[/yellow]"
        )

    console.print(result_table)

    if not validation["valid"]:
        raise typer.Exit(1)


@wf_app.command("parse")
def wf_parse(
    workflow_file: Path = typer.Argument(..., help="BPMN workflow file (.bpmn)"),
    format_output: str = typer.Option("table", "--format", "-f", help="Output format: table, json"),
):
    """
    Parse and inspect workflow structure.

    Examples:
        specify wf parse workflow.bpmn
        specify wf parse workflow.bpmn --format json
    """
    if not workflow_file.exists():
        console.print(f"[red]Error:[/red] Workflow file not found: {workflow_file}")
        raise typer.Exit(1)

    tracker = StepTracker("Workflow Parsing")
    tracker.add("parse", "Parse workflow structure")

    with Live(tracker.render(), console=console, refresh_per_second=8, transient=True) as live:
        tracker.attach_refresh(lambda: live.update(tracker.render()))

        tracker.start("parse")
        structure = _parse_workflow_structure(workflow_file)
        tracker.complete(
            "parse", f"{len(structure['tasks'])} task(s), {len(structure['gateways'])} gateway(s)"
        )

    console.print(tracker.render())
    console.print()

    if format_output == "json":
        console.print(json.dumps(structure, indent=2))
    else:
        # Table format
        tasks_table = Table(title="Tasks", show_header=True, header_style="bold cyan")
        tasks_table.add_column("Task ID", style="cyan")
        tasks_table.add_column("Name", style="white")
        tasks_table.add_column("Type", style="yellow")

        for task in structure["tasks"]:
            tasks_table.add_row(task["id"], task["name"], task["type"])

        if structure["tasks"]:
            console.print(tasks_table)
            console.print()

        gateways_table = Table(title="Gateways", show_header=True, header_style="bold cyan")
        gateways_table.add_column("Gateway ID", style="cyan")
        gateways_table.add_column("Name", style="white")
        gateways_table.add_column("Type", style="yellow")

        for gateway in structure["gateways"]:
            gateways_table.add_row(gateway["id"], gateway["name"], gateway["type"])

        if structure["gateways"]:
            console.print(gateways_table)
            console.print()

        if structure["events"]:
            events_table = Table(title="Events", show_header=True, header_style="bold cyan")
            events_table.add_column("Event ID", style="cyan")
            events_table.add_column("Name", style="white")
            events_table.add_column("Type", style="yellow")

            for event in structure["events"]:
                events_table.add_row(event["id"], event["name"], event["type"])

            console.print(events_table)
            console.print()

        if structure["flows"]:
            flows_table = Table(title="Sequence Flows", show_header=True, header_style="bold cyan")
            flows_table.add_column("Source", style="cyan")
            flows_table.add_column("Target", style="green")

            for flow in structure["flows"]:
                flows_table.add_row(flow["source"], flow["target"])

            console.print(flows_table)


@wf_app.command("convert")
def wf_convert(
    input_file: Path = typer.Argument(..., help="Input workflow file (.bpmn, .pnml, .png, .svg)"),
    output_file: Path = typer.Option(
        ..., "--output", "-o", help="Output file (.bpmn, .pnml, .png, .svg)"
    ),
):
    """
    Convert workflow between formats.

    Supported conversions:
    - BPMN to visualization (PNG, SVG)
    - BPMN to Petri net (PNML)
    - Petri net (PNML) to visualization

    Examples:
        specify wf convert workflow.bpmn -o workflow.png
        specify wf convert model.pnml -o model.svg
        specify wf convert process.bpmn -o process.pnml
    """
    import pm4py

    if not input_file.exists():
        console.print(f"[red]Error:[/red] Input file not found: {input_file}")
        raise typer.Exit(1)

    in_suffix = input_file.suffix.lower()
    out_suffix = output_file.suffix.lower()

    # Validate file extensions
    valid_in = {".bpmn", ".pnml", ".png", ".svg"}
    valid_out = {".bpmn", ".pnml", ".png", ".svg"}

    if in_suffix not in valid_in or out_suffix not in valid_out:
        console.print(f"[red]Error:[/red] Unsupported format. Valid: {valid_in}")
        raise typer.Exit(1)

    tracker = StepTracker("Workflow Conversion")
    tracker.add("load", "Load workflow")
    tracker.add("convert", "Convert format")
    tracker.add("save", "Save output")

    with Live(tracker.render(), console=console, refresh_per_second=8, transient=True) as live:
        tracker.attach_refresh(lambda: live.update(tracker.render()))

        try:
            tracker.start("load")

            # Load input based on format
            model = None
            model_type = None

            if in_suffix == ".bpmn":
                from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser

                parser = BpmnParser()
                with open(input_file) as f:
                    parser.parse_file(f)
                model = parser.get_spec(next(iter(parser.processes.keys())))
                model_type = "bpmn"
                tracker.complete("load", "BPMN file")
            elif in_suffix == ".pnml":
                net, im, fm = pm4py.read_pnml(str(input_file))
                model = (net, im, fm)
                model_type = "petri"
                tracker.complete("load", "PNML file")

            if not model:
                tracker.error("load", "unsupported input format")
                raise typer.Exit(1)

            tracker.start("convert")

            # Convert to output format
            if out_suffix == ".bpmn" and model_type == "petri":
                # Convert Petri net to BPMN
                net, im, fm = model
                model = pm4py.convert_to_bpmn(net, im, fm)
                tracker.complete("convert", "Petri net → BPMN")
            elif out_suffix == ".pnml" and model_type == "bpmn":
                # BPMN to Petri net conversion not supported
                # Alternative: use 'specify pm discover' to discover Petri nets from event logs
                tracker.error("convert", "BPMN → Petri net conversion not supported")
                console.print(
                    "\n[yellow]BPMN to Petri net conversion not supported.[/yellow]\n"
                    "[dim]Alternative approaches:[/dim]\n"
                    "  • Use [cyan]specify pm discover[/cyan] to discover Petri nets from event logs\n"
                    "  • Export BPMN to XES event log, then discover Petri net\n"
                    "  • Use external BPMN-to-Petri conversion tools\n"
                )
                raise typer.Exit(1)
            elif out_suffix in {".png", ".svg"}:
                if model_type == "bpmn":
                    pm4py.save_vis_bpmn(model, str(output_file))
                    tracker.complete("convert", f"BPMN → {out_suffix.upper()}")
                else:
                    net, im, fm = model
                    pm4py.save_vis_petri_net(net, im, fm, str(output_file))
                    tracker.complete("convert", f"Petri net → {out_suffix.upper()}")
            else:
                tracker.complete("convert", f"{in_suffix} → {out_suffix}")

            tracker.start("save")
            # File is already saved during visualization step
            tracker.complete("save", str(output_file))

        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    console.print(tracker.render())
    console.print("\n[bold green]Workflow converted successfully.[/bold green]")
    console.print(f"Output: [cyan]{output_file}[/cyan]")


@pm_app.command("execute")
def pm_execute(
    bpmn_file: Path = typer.Argument(..., help="BPMN file to execute (.bpmn)"),
    data_file: Path = typer.Option(None, "--data", "-d", help="JSON file with workflow data"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed execution trace"),
):
    """
    Execute a BPMN workflow using SpiffWorkflow.

    This command loads a BPMN file and executes it using the SpiffWorkflow engine,
    showing the execution flow and task completions.

    Examples:
        specify pm execute process.bpmn
        specify pm execute process.bpmn --verbose
        specify pm execute process.bpmn --data workflow_data.json
    """
    import json

    from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser
    from SpiffWorkflow.bpmn.serializer.workflow import BpmnWorkflowSerializer
    from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
    from SpiffWorkflow.task import TaskState

    if not bpmn_file.exists():
        console.print(f"[red]Error:[/red] BPMN file not found: {bpmn_file}")
        raise typer.Exit(1)

    # Load optional data
    workflow_data = {}
    if data_file:
        if not data_file.exists():
            console.print(f"[red]Error:[/red] Data file not found: {data_file}")
            raise typer.Exit(1)
        with open(data_file) as f:
            workflow_data = json.load(f)

    tracker = StepTracker("Execute BPMN Workflow")
    tracker.add("load", "Load BPMN")
    tracker.add("execute", "Execute workflow")
    tracker.add("results", "Collect results")

    with Live(tracker.render(), console=console, refresh_per_second=8, transient=True) as live:
        tracker.attach_refresh(lambda: live.update(tracker.render()))

        try:
            tracker.start("load")

            # Parse BPMN file
            parser = BpmnParser()
            parser.add_bpmn_file(str(bpmn_file))

            # Get the first process spec
            process_ids = list(parser.process_parsers.keys())
            if not process_ids:
                raise ValueError("No process found in BPMN file")

            spec = parser.get_spec(process_ids[0])

            tracker.complete("load", bpmn_file.name)

            tracker.start("execute")

            # Create and execute workflow
            workflow = BpmnWorkflow(spec, workflow_data)

            completed_tasks = []
            execution_steps = []
            step_count = 0

            # Execute all tasks in the workflow
            task_types_to_show = ["Task", "UserTask", "ManualTask", "ScriptTask", "ServiceTask"]

            while not workflow.is_completed():
                # Get the next task to run
                ready_tasks = list(workflow.get_tasks(state=TaskState.READY))

                if not ready_tasks:
                    break

                for task in ready_tasks:
                    task_name = (
                        task.task_spec.name
                        if hasattr(task.task_spec, "name")
                        else str(task.task_spec)
                    )
                    task_type = task.task_spec.__class__.__name__

                    if verbose:
                        console.print(f"[dim]Executing:[/dim] {task_name} ({task_type})")

                    # Execute the task
                    task.run()

                    # Track completed work tasks
                    if task.state == TaskState.COMPLETED and any(
                        t in task_type for t in task_types_to_show
                    ):
                        step_count += 1
                        execution_steps.append(f"Step {step_count}: {task_name}")
                        completed_tasks.append(task_name)

                # Run engine steps to move workflow forward
                workflow.do_engine_steps()

            tracker.complete("execute", f"{step_count} steps")

            tracker.start("results")

            # Get workflow status
            is_complete = workflow.is_completed()

            tracker.complete("results")

        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            import traceback

            if verbose:
                console.print(traceback.format_exc())
            raise typer.Exit(1)

    console.print(tracker.render())
    console.print("\n[bold green]Workflow execution complete.[/bold green]")

    # Show execution summary
    summary_table = Table(title="Execution Summary", show_header=True, header_style="bold cyan")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="white")

    summary_table.add_row("BPMN File", str(bpmn_file))
    summary_table.add_row("Total Steps", str(step_count))
    summary_table.add_row("Completed Tasks", str(len(completed_tasks)))
    summary_table.add_row("Workflow Status", "✓ Completed" if is_complete else "⚠ Incomplete")

    console.print()
    console.print(summary_table)

    if verbose and execution_steps:
        console.print()
        exec_table = Table(title="Execution Steps", show_header=True, header_style="bold cyan")
        exec_table.add_column("Step", style="cyan")

        for step in execution_steps:
            exec_table.add_row(step)

        console.print(exec_table)

    if completed_tasks:
        console.print()
        tasks_table = Table(title="Completed Tasks", show_header=True, header_style="bold cyan")
        tasks_table.add_column("Task Name", style="green")

        for task in completed_tasks:
            tasks_table.add_row(task)

        console.print(tasks_table)

    # =============================================================================
    # End Workflow Automation Commands
    # =============================================================================

    if not cargo_ok:
        console.print("[yellow]⚠ Cargo is required for ontology compilation[/yellow]")
        console.print(
            "[dim]  Install Rust: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh[/dim]"
        )
        console.print("[dim]  Visit: https://rustup.rs/[/dim]")

    if not ggen_ok and cargo_ok:
        console.print("[yellow]⚠ ggen is required for compiling ontologies[/yellow]")
        console.print("[dim]  Install: brew install seanchatmangpt/ggen/ggen[/dim]")
        console.print("[dim]  Or: cargo install ggen-cli-lib[/dim]")
        console.print("[dim]  Visit: https://github.com/seanchatmangpt/ggen[/dim]")

    if not ggen_ok and not cargo_ok:
        console.print("[yellow]⚠ Spec-driven development requires ontology compilation[/yellow]")
        console.print("[dim]  Install Rust and ggen to continue[/dim]")


@app.command()
def version():
    """Display version and system information."""
    show_banner()

    # Get CLI version from package metadata
    cli_version = "unknown"
    try:
        cli_version = importlib.metadata.version("specify-cli")
    except Exception:
        # Fallback: try reading from pyproject.toml if running from source
        try:
            import tomllib

            pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
            if pyproject_path.exists():
                with open(pyproject_path, "rb") as f:
                    data = tomllib.load(f)
                    cli_version = data.get("project", {}).get("version", "unknown")
        except Exception:
            pass

    # Fetch latest template release version
    repo_owner = "github"
    repo_name = "spec-kit"
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"

    template_version = "unknown"
    release_date = "unknown"

    try:
        response = client.get(
            api_url,
            timeout=10,
            follow_redirects=True,
            headers=_github_auth_headers(),
        )
        if response.status_code == 200:
            release_data = response.json()
            template_version = release_data.get("tag_name", "unknown")
            # Remove 'v' prefix if present
            if template_version.startswith("v"):
                template_version = template_version[1:]
            release_date = release_data.get("published_at", "unknown")
            if release_date != "unknown":
                # Format the date nicely
                try:
                    dt = datetime.fromisoformat(release_date.replace("Z", "+00:00"))
                    release_date = dt.strftime("%Y-%m-%d")
                except Exception:
                    pass
    except Exception:
        pass

    info_table = Table(show_header=False, box=None, padding=(0, 2))
    info_table.add_column("Key", style="cyan", justify="right")
    info_table.add_column("Value", style="white")

    info_table.add_row("CLI Version", cli_version)
    info_table.add_row("Template Version", template_version)
    info_table.add_row("Released", release_date)
    info_table.add_row("", "")
    info_table.add_row("Python", platform.python_version())
    info_table.add_row("Platform", platform.system())
    info_table.add_row("Architecture", platform.machine())
    info_table.add_row("OS Version", platform.version())

    panel = Panel(
        info_table,
        title="[bold cyan]Specify CLI Information[/bold cyan]",
        border_style="cyan",
        padding=(1, 2),
    )

    console.print(panel)
    console.print()


def main():
    """Entry point for the CLI - delegates to refactored app.py."""
    from specify_cli.app import main as app_main

    app_main()


if __name__ == "__main__":
    main()
