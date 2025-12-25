"""
specify_cli.commands.observability - Observability Command
==========================================================

CLI command handler for observability dashboards and metrics.

This module provides the Typer command interface for generating
observability dashboards, viewing performance metrics, and detecting anomalies.

Examples
--------
    $ specify observability dashboards
    $ specify observability stats
    $ specify observability anomalies
    $ specify observability export metrics.json

See Also
--------
- :mod:`specify_cli.ops.observability` : Business logic
- :mod:`specify_cli.core.advanced_observability` : Metrics collection
- :mod:`specify_cli.core.observability_dashboards` : Dashboard generation
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from specify_cli.core.instrumentation import instrument_command
from specify_cli.core.shell import colour, dump_json
from specify_cli.ops import observability as obs_ops

console = Console()

app = typer.Typer(
    name="observability",
    help="Observability dashboards and performance metrics.",
)


@app.command("dashboards")
@instrument_command("observability_dashboards", track_args=True)
def dashboards(
    output_dir: Path = typer.Option(
        Path("./reports/observability"),
        "--output-dir",
        "-o",
        help="Output directory for dashboards.",
    ),
) -> None:
    """Generate observability dashboards.

    Creates HTML dashboards for:
    - CLI performance metrics
    - ggen transformation performance
    - Test suite health
    - Resource usage

    Example:
        $ specify observability dashboards
        $ specify observability dashboards -o ./my-reports
    """
    try:
        result = obs_ops.generate_dashboards(output_dir)

        console.print()
        console.print("[bold]Observability Dashboards Generated[/bold]")
        console.print()

        for name, path in result.items():
            console.print(f"  [cyan]✓[/cyan] {name}: {path}")

        console.print()
        colour(
            f"[green]✓ {len(result)} dashboards generated in {output_dir}[/green]",
            "green",
        )
        console.print()
        console.print(f"Open [cyan]{output_dir / 'index.html'}[/cyan] to view")

    except Exception as e:
        console.print()
        colour(f"[red]Error generating dashboards:[/red] {e}", "red")
        raise typer.Exit(1) from None


@app.command("stats")
@instrument_command("observability_stats", track_args=True)
def stats(
    operation: str | None = typer.Argument(
        None,
        help="Operation to show stats for (shows all if not specified).",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output as JSON.",
    ),
) -> None:
    """Show performance statistics.

    Display detailed performance metrics including:
    - Mean, P50, P95, P99 durations
    - Success rates
    - Sample counts
    - Error distributions

    Example:
        $ specify observability stats
        $ specify observability stats ops.check.all_tools
        $ specify observability stats --json
    """
    try:
        if operation:
            stats_data = obs_ops.get_stats(operation)
        else:
            stats_data = obs_ops.get_all_stats()

        if json_output:
            dump_json(stats_data)
            return

        console.print()
        console.print("[bold]Performance Statistics[/bold]")
        console.print()

        if operation:
            # Single operation stats
            if "error" in stats_data:
                colour(f"[yellow]No data available for {operation}[/yellow]", "yellow")
                return

            console.print(f"[bold]Operation:[/bold] {operation}")
            console.print(f"  Samples: {stats_data['sample_count']}")
            console.print(f"  Mean: {stats_data['mean']:.3f}s")
            console.print(f"  P50: {stats_data['p50']:.3f}s")
            console.print(f"  P95: {stats_data['p95']:.3f}s")
            console.print(f"  P99: {stats_data['p99']:.3f}s")
            console.print(f"  Min: {stats_data['min']:.3f}s")
            console.print(f"  Max: {stats_data['max']:.3f}s")
            console.print(f"  Success Rate: {stats_data['success_rate']*100:.1f}%")

            if stats_data.get("error_distribution"):
                console.print("\n[bold]Error Distribution:[/bold]")
                for error_type, count in stats_data["error_distribution"].items():
                    console.print(f"  {error_type}: {count}")

        else:
            # All operations table
            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("Operation", style="bold")
            table.add_column("Samples", justify="right")
            table.add_column("Mean", justify="right")
            table.add_column("P95", justify="right")
            table.add_column("Success Rate", justify="right")

            for op, stats_item in sorted(stats_data.items()):
                if "error" in stats_item:
                    continue

                success_rate = stats_item.get("success_rate", 1.0) * 100
                success_color = (
                    "green" if success_rate >= 95 else "yellow" if success_rate >= 80 else "red"
                )

                table.add_row(
                    op,
                    str(stats_item["sample_count"]),
                    f"{stats_item['mean']:.3f}s",
                    f"{stats_item['p95']:.3f}s",
                    f"[{success_color}]{success_rate:.1f}%[/{success_color}]",
                )

            console.print(table)

        console.print()

    except Exception as e:
        console.print()
        colour(f"[red]Error getting statistics:[/red] {e}", "red")
        raise typer.Exit(1) from None


@app.command("anomalies")
@instrument_command("observability_anomalies", track_args=True)
def anomalies(
    operation: str | None = typer.Argument(
        None,
        help="Operation to check (checks all if not specified).",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output as JSON.",
    ),
) -> None:
    """Detect performance anomalies.

    Analyze recent metrics to detect performance regressions
    using statistical anomaly detection (z-score analysis).

    Example:
        $ specify observability anomalies
        $ specify observability anomalies ops.check.all_tools
        $ specify observability anomalies --json
    """
    try:
        anomalies_data = obs_ops.detect_anomalies(operation)

        if json_output:
            dump_json([a.to_dict() for a in anomalies_data])
            return

        console.print()
        console.print("[bold]Performance Anomalies[/bold]")
        console.print()

        if not anomalies_data:
            colour("[green]✓ No anomalies detected[/green]", "green")
            console.print()
            return

        # Anomalies table
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Operation", style="bold")
        table.add_column("Current", justify="right")
        table.add_column("Baseline", justify="right")
        table.add_column("Deviation", justify="right")
        table.add_column("Z-Score", justify="right")

        for anomaly in anomalies_data:
            deviation_color = "yellow" if abs(anomaly.deviation_pct) < 50 else "red"

            table.add_row(
                anomaly.operation,
                f"{anomaly.current_duration:.3f}s",
                f"{anomaly.baseline_mean:.3f}s",
                f"[{deviation_color}]{anomaly.deviation_pct:+.1f}%[/{deviation_color}]",
                f"{anomaly.z_score:.2f}",
            )

        console.print(table)
        console.print()
        colour(
            f"[yellow]⚠ {len(anomalies_data)} anomalies detected[/yellow]",
            "yellow",
        )
        console.print()

    except Exception as e:
        console.print()
        colour(f"[red]Error detecting anomalies:[/red] {e}", "red")
        raise typer.Exit(1) from None


@app.command("export")
@instrument_command("observability_export", track_args=True)
def export(
    output_path: Path = typer.Argument(
        ...,
        help="Output path for JSON export.",
    ),
) -> None:
    """Export metrics as JSON.

    Export all collected metrics and statistics to a JSON file
    for custom analysis or integration with other tools.

    Example:
        $ specify observability export metrics.json
        $ specify observability export ./data/metrics-$(date +%Y%m%d).json
    """
    try:
        obs_ops.export_metrics(output_path)

        console.print()
        colour(f"[green]✓ Metrics exported to {output_path}[/green]", "green")
        console.print()

    except Exception as e:
        console.print()
        colour(f"[red]Error exporting metrics:[/red] {e}", "red")
        raise typer.Exit(1) from None


@app.command("baselines")
@instrument_command("observability_baselines", track_args=True)
def baselines(
    action: str = typer.Argument(
        ...,
        help="Action: save, load, or update.",
    ),
    path: Path | None = typer.Option(
        None,
        "--path",
        "-p",
        help="Path to baseline file (default: .specify/baselines).",
    ),
) -> None:
    """Manage performance baselines.

    Save, load, or update performance baselines used for
    anomaly detection and regression analysis.

    Actions:
        save   - Save current baselines to disk
        load   - Load baselines from disk
        update - Update baselines from recent metrics

    Example:
        $ specify observability baselines save
        $ specify observability baselines load
        $ specify observability baselines update
        $ specify observability baselines save --path custom-baselines.json
    """
    try:
        if action == "save":
            obs_ops.save_baselines(path)
            console.print()
            colour(
                f"[green]✓ Baselines saved to {path or '.specify/baselines'}[/green]",
                "green",
            )
        elif action == "load":
            obs_ops.load_baselines(path)
            console.print()
            colour(
                f"[green]✓ Baselines loaded from {path or '.specify/baselines'}[/green]",
                "green",
            )
        elif action == "update":
            result = obs_ops.update_baselines()
            console.print()
            console.print(f"[green]✓ Updated {len(result)} baselines[/green]")
            for op in result:
                console.print(f"  - {op}")
        else:
            colour(f"[red]Unknown action: {action}[/red]", "red")
            console.print("Valid actions: save, load, update")
            raise typer.Exit(1)

        console.print()

    except Exception as e:
        console.print()
        colour(f"[red]Error managing baselines:[/red] {e}", "red")
        raise typer.Exit(1) from None
