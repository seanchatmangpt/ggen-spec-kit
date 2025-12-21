"""
specify_cli.commands.pm - Process Mining Commands
==================================================

CLI command handlers for process mining operations using pm4py.

This module provides the Typer command interface for process mining
operations, delegating all business logic to the ops.process_mining layer.

Commands
--------
* **discover**: Discover a process model from an event log
* **conform**: Check conformance between event log and process model
* **stats**: Extract statistics from an event log
* **filter**: Filter event logs by criteria
* **sample**: Sample traces from event logs

Examples
--------
    $ specify pm discover log.csv -o model.pnml
    $ specify pm conform log.csv model.pnml
    $ specify pm stats log.xes --json
    $ specify pm filter log.csv --min-support 0.8
    $ specify pm sample -o test_log.csv --cases 100

See Also
--------
- :mod:`specify_cli.ops.process_mining` : Business logic
- :mod:`pm4py` : Process mining library
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from specify_cli.core.instrumentation import instrument_command
from specify_cli.core.shell import colour, dump_json
from specify_cli.ops import process_mining as pm_ops

console = Console()

app = typer.Typer(
    name="pm",
    help="Process mining operations using pm4py",
)


@app.command("discover")
@instrument_command("pm.discover", track_args=True)
def discover(
    input_file: Path = typer.Argument(
        ...,
        help="Input event log file (CSV or XES)",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    output_file: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file for discovered model (default: input_name_model.pnml)",
    ),
    algorithm: str = typer.Option(
        "inductive",
        "--algorithm",
        "-a",
        help="Discovery algorithm: alpha, alpha_plus, heuristic, inductive, ilp",
    ),
    noise_threshold: float = typer.Option(
        0.0,
        "--noise",
        "-n",
        help="Noise threshold for inductive miner (0.0-1.0)",
    ),
    case_id: str = typer.Option(
        "case:concept:name",
        "--case-id",
        help="Column name for case ID (CSV only)",
    ),
    activity: str = typer.Option(
        "concept:name",
        "--activity",
        help="Column name for activity (CSV only)",
    ),
    timestamp: str = typer.Option(
        "time:timestamp",
        "--timestamp",
        help="Column name for timestamp (CSV only)",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results as JSON",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed progress information",
    ),
) -> None:
    """Discover a process model from an event log.

    Uses the specified discovery algorithm to mine a process model
    from the provided event log. Supported algorithms:
    - alpha: Alpha Miner (basic)
    - alpha_plus: Alpha+ Miner (improved)
    - heuristic: Heuristics Miner (noise-tolerant)
    - inductive: Inductive Miner (default, robust)
    - ilp: Integer Linear Programming (precise)

    The discovered model is saved in PNML (Petri Net Markup Language) format.

    Examples:
        specify pm discover log.csv
        specify pm discover log.xes -o model.pnml --algorithm heuristic
        specify pm discover log.csv --noise 0.2 --json
    """
    try:
        # Default output file
        if output_file is None:
            output_file = input_file.parent / f"{input_file.stem}_model.pnml"

        if verbose:
            console.print(f"[cyan]Loading event log:[/cyan] {input_file}")

        # Load event log
        log = pm_ops.load_event_log(
            input_file,
            case_id=case_id,
            activity=activity,
            timestamp=timestamp,
        )

        if verbose:
            console.print(f"[cyan]Loaded:[/cyan] {len(log)} cases")

        # Discover model
        if verbose:
            console.print(f"[cyan]Discovering model using:[/cyan] {algorithm}")

        model, model_type = pm_ops.discover_process_model(
            log,
            algorithm=algorithm,
            noise_threshold=noise_threshold,
        )

        if verbose:
            console.print(f"[cyan]Model type:[/cyan] {model_type}")

        # Save model
        pm_ops.save_model(model, output_file, model_type=model_type)

        if json_output:
            output = {
                "success": True,
                "input_file": str(input_file),
                "output_file": str(output_file),
                "algorithm": algorithm,
                "model_type": model_type,
                "num_cases": len(log),
            }
            dump_json(output)
            return

        # Rich output
        console.print()
        console.print("[bold green]✓ Model discovered successfully[/bold green]")
        console.print()

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Input File", str(input_file))
        table.add_row("Output File", str(output_file))
        table.add_row("Algorithm", algorithm)
        table.add_row("Model Type", model_type)
        table.add_row("Cases", str(len(log)))

        console.print(table)
        console.print()

    except FileNotFoundError as e:
        colour(f"[red]✗ File not found:[/red] {e}", "red")
        raise typer.Exit(1)
    except ValueError as e:
        colour(f"[red]✗ Invalid input:[/red] {e}", "red")
        raise typer.Exit(1)
    except Exception as e:
        colour(f"[red]✗ Error during discovery:[/red] {e}", "red")
        if verbose:
            import traceback

            console.print(traceback.format_exc())
        raise typer.Exit(1)


@app.command("conform")
@instrument_command("pm.conform", track_args=True)
def conform(
    log_file: Path = typer.Argument(
        ...,
        help="Input event log file (CSV or XES)",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    model_file: Path = typer.Argument(
        ...,
        help="Process model file (PNML or BPMN)",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    method: str = typer.Option(
        "token",
        "--method",
        "-m",
        help="Conformance method: token or alignment",
    ),
    case_id: str = typer.Option(
        "case:concept:name",
        "--case-id",
        help="Column name for case ID (CSV only)",
    ),
    activity: str = typer.Option(
        "concept:name",
        "--activity",
        help="Column name for activity (CSV only)",
    ),
    timestamp: str = typer.Option(
        "time:timestamp",
        "--timestamp",
        help="Column name for timestamp (CSV only)",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results as JSON",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed conformance diagnostics",
    ),
) -> None:
    """Check conformance between event log and process model.

    Performs conformance checking to measure how well the event log
    fits the process model. Computes:
    - Fitness: How much of the log can be replayed on the model
    - Precision: How much behavior is allowed by the model
    - F1 Score: Harmonic mean of fitness and precision

    Methods:
    - token: Token-based replay (fast, approximate)
    - alignment: Optimal alignments (slow, precise)

    Examples:
        specify pm conform log.csv model.pnml
        specify pm conform log.xes model.bpmn --method alignment
        specify pm conform log.csv model.pnml --json
    """
    try:
        if verbose:
            console.print(f"[cyan]Loading event log:[/cyan] {log_file}")

        # Load event log
        log = pm_ops.load_event_log(
            log_file,
            case_id=case_id,
            activity=activity,
            timestamp=timestamp,
        )

        if verbose:
            console.print(f"[cyan]Loaded:[/cyan] {len(log)} cases")
            console.print(f"[cyan]Checking conformance using:[/cyan] {method}")

        # Perform conformance checking
        result = pm_ops.conform_trace(log, model_file, method=method)

        if json_output:
            output = {
                "success": True,
                "log_file": str(log_file),
                "model_file": str(model_file),
                "method": result["method"],
                "fitness": result["fitness"],
                "precision": result["precision"],
                "f1_score": result["f1_score"],
                "num_traces": result["num_traces"],
            }
            dump_json(output)
            return

        # Rich output
        console.print()
        console.print("[bold]Conformance Checking Results[/bold]")
        console.print()

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Log File", str(log_file))
        table.add_row("Model File", str(model_file))
        table.add_row("Method", result["method"])
        table.add_row("Traces", str(result["num_traces"]))
        table.add_row("", "")
        table.add_row("Fitness", f"{result['fitness']:.2%}")
        table.add_row("Precision", f"{result['precision']:.2%}")
        table.add_row("F1 Score", f"{result['f1_score']:.2%}")

        console.print(table)
        console.print()

        # Color-coded interpretation
        if result["fitness"] >= 0.9 and result["precision"] >= 0.9:
            colour("[green]✓ Excellent conformance[/green]", "green")
        elif result["fitness"] >= 0.7 and result["precision"] >= 0.7:
            colour("[yellow]⚠ Good conformance[/yellow]", "yellow")
        else:
            colour("[red]✗ Poor conformance[/red]", "red")

        console.print()

    except FileNotFoundError as e:
        colour(f"[red]✗ File not found:[/red] {e}", "red")
        raise typer.Exit(1)
    except ValueError as e:
        colour(f"[red]✗ Invalid input:[/red] {e}", "red")
        raise typer.Exit(1)
    except Exception as e:
        colour(f"[red]✗ Error during conformance checking:[/red] {e}", "red")
        if verbose:
            import traceback

            console.print(traceback.format_exc())
        raise typer.Exit(1)


@app.command("stats")
@instrument_command("pm.stats", track_args=True)
def stats(
    input_file: Path = typer.Argument(
        ...,
        help="Input event log file (CSV or XES)",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    case_id: str = typer.Option(
        "case:concept:name",
        "--case-id",
        help="Column name for case ID (CSV only)",
    ),
    activity: str = typer.Option(
        "concept:name",
        "--activity",
        help="Column name for activity (CSV only)",
    ),
    timestamp: str = typer.Option(
        "time:timestamp",
        "--timestamp",
        help="Column name for timestamp (CSV only)",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results as JSON",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed statistics including variants",
    ),
) -> None:
    """Extract statistics from an event log.

    Analyzes the event log and computes various statistics:
    - Total cases and events
    - Unique activities
    - Trace length statistics (min, max, average)
    - Start and end activities
    - Process variants (if verbose)

    Examples:
        specify pm stats log.csv
        specify pm stats log.xes --verbose
        specify pm stats log.csv --json
    """
    try:
        if verbose:
            console.print(f"[cyan]Loading event log:[/cyan] {input_file}")

        # Load event log
        log = pm_ops.load_event_log(
            input_file,
            case_id=case_id,
            activity=activity,
            timestamp=timestamp,
        )

        # Get statistics
        stats_data = pm_ops.get_log_statistics(log)

        if json_output:
            dump_json(stats_data)
            return

        # Rich output
        console.print()
        console.print("[bold]Event Log Statistics[/bold]")
        console.print()

        # Summary table
        summary_table = Table(show_header=True, header_style="bold cyan")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="white")

        summary_table.add_row("Total Cases", str(stats_data["num_cases"]))
        summary_table.add_row("Total Events", str(stats_data["num_events"]))
        summary_table.add_row("Unique Activities", str(stats_data["num_activities"]))
        summary_table.add_row("Process Variants", str(stats_data["num_variants"]))
        summary_table.add_row("Avg Trace Length", f"{stats_data['avg_trace_length']:.2f}")

        console.print(summary_table)
        console.print()

        # Start/End activities
        if verbose:
            console.print("[bold]Start Activities[/bold]")
            start_table = Table(show_header=True, header_style="bold cyan")
            start_table.add_column("Activity", style="cyan")
            start_table.add_column("Count", style="white")

            for activity_name, count in list(stats_data["start_activities"].items())[:5]:
                start_table.add_row(activity_name, str(count))

            console.print(start_table)
            console.print()

            console.print("[bold]End Activities[/bold]")
            end_table = Table(show_header=True, header_style="bold cyan")
            end_table.add_column("Activity", style="cyan")
            end_table.add_column("Count", style="white")

            for activity_name, count in list(stats_data["end_activities"].items())[:5]:
                end_table.add_row(activity_name, str(count))

            console.print(end_table)
            console.print()

    except FileNotFoundError as e:
        colour(f"[red]✗ File not found:[/red] {e}", "red")
        raise typer.Exit(1)
    except ValueError as e:
        colour(f"[red]✗ Invalid input:[/red] {e}", "red")
        raise typer.Exit(1)
    except Exception as e:
        colour(f"[red]✗ Error extracting statistics:[/red] {e}", "red")
        if verbose:
            import traceback

            console.print(traceback.format_exc())
        raise typer.Exit(1)


@app.command("filter")
@instrument_command("pm.filter", track_args=True)
def filter_log(
    input_file: Path = typer.Argument(
        ...,
        help="Input event log file (CSV or XES)",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    output_file: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file (default: input_name_filtered.csv)",
    ),
    filter_type: str = typer.Option(
        "activity",
        "--type",
        "-t",
        help="Filter type: activity, start, end, length",
    ),
    filter_value: str | None = typer.Option(
        None,
        "--value",
        "-val",
        help="Value to filter by (activity name)",
    ),
    min_length: int | None = typer.Option(
        None,
        "--min-length",
        help="Minimum trace length",
    ),
    max_length: int | None = typer.Option(
        None,
        "--max-length",
        help="Maximum trace length",
    ),
    case_id: str = typer.Option(
        "case:concept:name",
        "--case-id",
        help="Column name for case ID (CSV only)",
    ),
    activity: str = typer.Option(
        "concept:name",
        "--activity",
        help="Column name for activity (CSV only)",
    ),
    timestamp: str = typer.Option(
        "time:timestamp",
        "--timestamp",
        help="Column name for timestamp (CSV only)",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results as JSON",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed filtering information",
    ),
) -> None:
    """Filter an event log by criteria.

    Apply various filters to reduce the event log:
    - activity: Keep only traces with specified activity
    - start: Keep only traces starting with activity
    - end: Keep only traces ending with activity
    - length: Keep only traces within length range

    Examples:
        specify pm filter log.csv --type activity --value "Review"
        specify pm filter log.csv --type length --min-length 3 --max-length 10
        specify pm filter log.xes --type start --value "Start" -o filtered.xes
    """
    try:
        # Default output file
        if output_file is None:
            output_file = input_file.parent / f"{input_file.stem}_filtered.csv"

        if verbose:
            console.print(f"[cyan]Loading event log:[/cyan] {input_file}")

        # Load event log
        log = pm_ops.load_event_log(
            input_file,
            case_id=case_id,
            activity=activity,
            timestamp=timestamp,
        )

        original_count = len(log)

        if verbose:
            console.print(f"[cyan]Original cases:[/cyan] {original_count}")
            console.print(f"[cyan]Applying filter:[/cyan] {filter_type}")

        # Apply filter
        filtered_log = pm_ops.filter_log(
            log,
            filter_type=filter_type,
            filter_value=filter_value,
            min_length=min_length,
            max_length=max_length,
        )

        filtered_count = len(filtered_log)

        if verbose:
            console.print(f"[cyan]Filtered cases:[/cyan] {filtered_count}")

        # Save filtered log
        import pm4py

        if output_file.suffix.lower() == ".csv":
            pm4py.write_csv(filtered_log, str(output_file))
        elif output_file.suffix.lower() == ".xes":
            pm4py.write_xes(filtered_log, str(output_file))
        else:
            raise ValueError(f"Unsupported output format: {output_file.suffix}")

        if json_output:
            output = {
                "success": True,
                "input_file": str(input_file),
                "output_file": str(output_file),
                "filter_type": filter_type,
                "original_cases": original_count,
                "filtered_cases": filtered_count,
                "reduction": f"{(1 - filtered_count / original_count) * 100:.1f}%",
            }
            dump_json(output)
            return

        # Rich output
        console.print()
        console.print("[bold green]✓ Filtering complete[/bold green]")
        console.print()

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Input File", str(input_file))
        table.add_row("Output File", str(output_file))
        table.add_row("Filter Type", filter_type)
        table.add_row("Original Cases", str(original_count))
        table.add_row("Filtered Cases", str(filtered_count))
        table.add_row("Reduction", f"{(1 - filtered_count / original_count) * 100:.1f}%")

        console.print(table)
        console.print()

    except FileNotFoundError as e:
        colour(f"[red]✗ File not found:[/red] {e}", "red")
        raise typer.Exit(1)
    except ValueError as e:
        colour(f"[red]✗ Invalid input:[/red] {e}", "red")
        raise typer.Exit(1)
    except Exception as e:
        colour(f"[red]✗ Error during filtering:[/red] {e}", "red")
        if verbose:
            import traceback

            console.print(traceback.format_exc())
        raise typer.Exit(1)


@app.command("sample")
@instrument_command("pm.sample", track_args=True)
def sample(
    input_file: Path = typer.Argument(
        ...,
        help="Input event log file (CSV or XES)",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    output_file: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file (default: input_name_sample.csv)",
    ),
    num_traces: int | None = typer.Option(
        None,
        "--num-traces",
        "-n",
        help="Number of traces to sample",
    ),
    num_events: int | None = typer.Option(
        None,
        "--num-events",
        "-e",
        help="Number of events to sample (approximate)",
    ),
    method: str = typer.Option(
        "random",
        "--method",
        "-m",
        help="Sampling method: random",
    ),
    case_id: str = typer.Option(
        "case:concept:name",
        "--case-id",
        help="Column name for case ID (CSV only)",
    ),
    activity: str = typer.Option(
        "concept:name",
        "--activity",
        help="Column name for activity (CSV only)",
    ),
    timestamp: str = typer.Option(
        "time:timestamp",
        "--timestamp",
        help="Column name for timestamp (CSV only)",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results as JSON",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed sampling information",
    ),
) -> None:
    """Sample traces from an event log.

    Create a smaller sample of the event log for testing or analysis.
    Specify either number of traces or approximate number of events.

    Examples:
        specify pm sample log.csv --num-traces 100
        specify pm sample log.xes --num-events 500 -o sample.xes
        specify pm sample log.csv -n 50 --json
    """
    try:
        # Validate parameters
        if num_traces is None and num_events is None:
            colour("[red]✗ Must specify either --num-traces or --num-events[/red]", "red")
            raise typer.Exit(1)

        # Default output file
        if output_file is None:
            output_file = input_file.parent / f"{input_file.stem}_sample.csv"

        if verbose:
            console.print(f"[cyan]Loading event log:[/cyan] {input_file}")

        # Load event log
        log = pm_ops.load_event_log(
            input_file,
            case_id=case_id,
            activity=activity,
            timestamp=timestamp,
        )

        original_count = len(log)

        if verbose:
            console.print(f"[cyan]Original cases:[/cyan] {original_count}")
            console.print(f"[cyan]Sampling method:[/cyan] {method}")

        # Sample log
        sampled_log = pm_ops.sample_log(
            log,
            num_traces=num_traces,
            num_events=num_events,
            method=method,
        )

        sampled_count = len(sampled_log)

        if verbose:
            console.print(f"[cyan]Sampled cases:[/cyan] {sampled_count}")

        # Save sampled log
        import pm4py

        if output_file.suffix.lower() == ".csv":
            pm4py.write_csv(sampled_log, str(output_file))
        elif output_file.suffix.lower() == ".xes":
            pm4py.write_xes(sampled_log, str(output_file))
        else:
            raise ValueError(f"Unsupported output format: {output_file.suffix}")

        if json_output:
            output = {
                "success": True,
                "input_file": str(input_file),
                "output_file": str(output_file),
                "method": method,
                "original_cases": original_count,
                "sampled_cases": sampled_count,
                "sample_rate": f"{sampled_count / original_count * 100:.1f}%",
            }
            dump_json(output)
            return

        # Rich output
        console.print()
        console.print("[bold green]✓ Sampling complete[/bold green]")
        console.print()

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Input File", str(input_file))
        table.add_row("Output File", str(output_file))
        table.add_row("Sampling Method", method)
        table.add_row("Original Cases", str(original_count))
        table.add_row("Sampled Cases", str(sampled_count))
        table.add_row("Sample Rate", f"{sampled_count / original_count * 100:.1f}%")

        console.print(table)
        console.print()

    except FileNotFoundError as e:
        colour(f"[red]✗ File not found:[/red] {e}", "red")
        raise typer.Exit(1)
    except ValueError as e:
        colour(f"[red]✗ Invalid input:[/red] {e}", "red")
        raise typer.Exit(1)
    except Exception as e:
        colour(f"[red]✗ Error during sampling:[/red] {e}", "red")
        if verbose:
            import traceback

            console.print(traceback.format_exc())
        raise typer.Exit(1)
