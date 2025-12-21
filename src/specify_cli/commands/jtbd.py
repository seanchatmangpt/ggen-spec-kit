"""
specify_cli.commands.jtbd - JTBD CLI Commands
==============================================

CLI command handlers for Jobs-to-be-Done (JTBD) metrics tracking and reporting.

This module provides Typer command interfaces for tracking job completions,
outcome achievements, and generating JTBD insights reports.

Commands
--------
* ``specify jtbd track`` - Track a job completion event
* ``specify jtbd outcome`` - Record an outcome achievement
* ``specify jtbd report`` - Generate JTBD metrics report
* ``specify jtbd analyze`` - Analyze job-to-feature mapping
* ``specify jtbd dashboard`` - Display real-time metrics dashboard

Examples
--------
    $ specify jtbd track deps-add --persona python-developer --feature "specify deps add"
    $ specify jtbd outcome faster-deps --metric time_saved --expected 30 --actual 8.5
    $ specify jtbd report --persona python-developer --json
    $ specify jtbd analyze --persona python-developer

See Also
--------
- :mod:`specify_cli.ops.jtbd` : Business logic
- :mod:`specify_cli.core.jtbd_metrics` : Data classes
- :mod:`specify_cli.runtime.jtbd` : Data persistence
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

import typer
from rich.console import Console
from rich.table import Table

from specify_cli.core.instrumentation import instrument_command
from specify_cli.core.shell import colour, dump_json
from specify_cli.ops import jtbd as jtbd_ops
from specify_cli.runtime import jtbd as jtbd_runtime

console = Console()

app = typer.Typer(
    name="jtbd",
    help="Jobs-to-be-Done (JTBD) metrics tracking and reporting.",
)


@app.command()
@instrument_command("jtbd.track", track_args=True)
def track(
    job_id: str = typer.Argument(..., help="Unique job identifier (e.g., 'deps-add')"),
    persona: str = typer.Option(..., "--persona", "-p", help="User persona completing the job"),
    feature: str = typer.Option(..., "--feature", "-f", help="Feature/command used"),
    status: str = typer.Option(
        "completed", "--status", "-s", help="Job status (started/completed/failed)"
    ),
    context: str = typer.Option(None, "--context", "-c", help="JSON context data"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Track a job completion event.

    Jobs represent high-level tasks users want to accomplish, such as:
    - "Add a dependency to my project"
    - "Generate API documentation"
    - "Validate RDF specifications"

    This command records when users complete jobs and which features
    they used, enabling job-to-feature mapping analysis.

    Examples
    --------
        # Track successful dependency addition
        $ specify jtbd track deps-add \\
            --persona python-developer \\
            --feature "specify deps add" \\
            --status completed

        # Track with context data
        $ specify jtbd track docs-generate \\
            --persona python-developer \\
            --feature "specify docs" \\
            --context '{"format": "markdown", "pages": 42}'
    """
    try:
        # Parse context if provided
        context_dict = {}
        if context:
            try:
                context_dict = json.loads(context)
            except json.JSONDecodeError as e:
                colour(f"[red]Error:[/red] Invalid JSON context: {e}", "red")
                raise typer.Exit(1)

        # First validate the input
        validation = jtbd_ops.validate_job_completion(
            job_id=job_id,
            persona=persona,
            feature=feature,
            context=context_dict,
        )

        if not validation.valid:
            if json_output:
                dump_json({"success": False, "errors": validation.errors})
                raise typer.Exit(1)
            console.print()
            colour("[red]Validation failed:[/red]", "red")
            for error in validation.errors:
                console.print(f"  • {error}")
            raise typer.Exit(1)

        # Show warnings if any
        if validation.warnings and not json_output:
            console.print()
            colour("[yellow]Warnings:[/yellow]", "yellow")
            for warning in validation.warnings:
                console.print(f"  • {warning}")
            console.print()

        # Create and track the job completion
        result = jtbd_ops.create_job_completion(
            job_id=job_id,
            persona=persona,
            feature_used=feature,
            status=status,
            context=context_dict,
        )

        if json_output:
            output = {
                "success": result.success,
                "job_id": result.job_id,
                "message": result.message,
                "data": result.job_data,
            }
            dump_json(output)
            return

        # Pretty output
        console.print()
        if result.success:
            colour(f"[green]✓[/green] {result.message}", "green")
            console.print()
            console.print(f"  Job ID: [cyan]{job_id}[/cyan]")
            console.print(f"  Persona: [cyan]{persona}[/cyan]")
            console.print(f"  Feature: [cyan]{feature}[/cyan]")
            console.print(f"  Status: [cyan]{status}[/cyan]")

            if result.job_data.get("duration_seconds"):
                console.print(
                    f"  Duration: [cyan]{result.job_data['duration_seconds']:.2f}s[/cyan]"
                )
        else:
            colour(f"[red]✗[/red] {result.message}", "red")
            raise typer.Exit(1)

    except typer.Exit:
        raise
    except KeyboardInterrupt:
        console.print()
        colour("Operation cancelled.", "yellow")
        raise typer.Exit(130)
    except Exception as e:
        console.print()
        colour(f"[red]Error:[/red] {e}", "red")
        raise typer.Exit(1)


@app.command()
@instrument_command("jtbd.outcome", track_args=True)
def outcome(
    outcome_id: str = typer.Argument(..., help="Unique outcome identifier (e.g., 'faster-deps')"),
    metric: str = typer.Option(..., "--metric", "-m", help="Metric being measured"),
    expected: float = typer.Option(..., "--expected", "-e", help="Expected/target value"),
    actual: float = typer.Option(..., "--actual", "-a", help="Actual value achieved"),
    feature: str = typer.Option(..., "--feature", "-f", help="Feature that delivered outcome"),
    persona: str = typer.Option(None, "--persona", "-p", help="User persona"),
    context: str = typer.Option(None, "--context", "-c", help="JSON context data"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Record an outcome achievement.

    Outcomes are measurable results users want to achieve, such as:
    - "Reduce dependency management time by 30 seconds"
    - "Improve code quality score by 20%"
    - "Achieve 90% test coverage"

    This command tracks whether features deliver expected outcomes
    and calculates achievement rates.

    Examples
    --------
        # Track time savings from dependency management
        $ specify jtbd outcome faster-deps \\
            --metric time_saved_seconds \\
            --expected 30 \\
            --actual 8.5 \\
            --feature "specify deps add" \\
            --persona python-developer

        # Track quality improvement
        $ specify jtbd outcome better-code-quality \\
            --metric quality_score_increase \\
            --expected 20.0 \\
            --actual 25.5 \\
            --feature "specify lint"
    """
    try:
        # Parse context if provided
        context_dict = {}
        if context:
            try:
                context_dict = json.loads(context)
            except json.JSONDecodeError as e:
                colour(f"[red]Error:[/red] Invalid JSON context: {e}", "red")
                raise typer.Exit(1)

        # Create and track the outcome achievement
        result = jtbd_ops.create_outcome_achievement(
            outcome_id=outcome_id,
            metric=metric,
            expected_value=expected,
            actual_value=actual,
            feature=feature,
            persona=persona,
            context=context_dict,
        )

        if json_output:
            output = {
                "success": result.success,
                "outcome_id": result.outcome_id,
                "message": result.message,
                "achievement_rate": result.achievement_rate,
                "data": result.outcome_data,
            }
            dump_json(output)
            return

        # Pretty output
        console.print()
        if result.success:
            colour(f"[green]✓[/green] {result.message}", "green")
            console.print()
            console.print(f"  Outcome: [cyan]{outcome_id}[/cyan]")
            console.print(f"  Metric: [cyan]{metric}[/cyan]")
            console.print(f"  Expected: [cyan]{expected}[/cyan]")
            console.print(f"  Actual: [cyan]{actual}[/cyan]")
            console.print(f"  Achievement: [cyan]{result.achievement_rate:.1f}%[/cyan]")

            # Color-code achievement rate
            if result.achievement_rate >= 100:
                console.print("  Status: [green]✓ Achieved[/green]")
            elif result.achievement_rate >= 75:
                console.print("  Status: [yellow]⚡ Partially Achieved[/yellow]")
            else:
                console.print("  Status: [red]✗ Not Achieved[/red]")

            if persona:
                console.print(f"  Persona: [cyan]{persona}[/cyan]")
        else:
            colour(f"[red]✗[/red] {result.message}", "red")
            raise typer.Exit(1)

    except typer.Exit:
        raise
    except KeyboardInterrupt:
        console.print()
        colour("Operation cancelled.", "yellow")
        raise typer.Exit(130)
    except Exception as e:
        console.print()
        colour(f"[red]Error:[/red] {e}", "red")
        raise typer.Exit(1)


@app.command()
@instrument_command("jtbd.report", track_args=True)
def report(
    persona: str = typer.Option(None, "--persona", "-p", help="Filter by persona"),
    days: int = typer.Option(30, "--days", "-d", help="Number of days to include in report"),
    include_jobs: bool = typer.Option(True, "--jobs/--no-jobs", help="Include job completion data"),
    include_outcomes: bool = typer.Option(
        True, "--outcomes/--no-outcomes", help="Include outcome data"
    ),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Generate a comprehensive JTBD metrics report.

    Analyzes job completions, outcome achievements, and generates
    insights about feature usage and effectiveness.

    The report includes:
    - Job completion statistics
    - Outcome achievement rates
    - Top features by usage
    - Average job durations
    - Success rates

    Examples
    --------
        # Generate full report
        $ specify jtbd report

        # Filter by persona
        $ specify jtbd report --persona python-developer

        # Report for last 7 days
        $ specify jtbd report --days 7

        # JSON output for programmatic use
        $ specify jtbd report --json
    """
    try:
        # Load data from runtime
        jobs_data = [] if not include_jobs else jtbd_runtime.load_job_completions()
        outcomes_data = [] if not include_outcomes else jtbd_runtime.load_outcome_achievements()

        # Convert outcomes from dict to OutcomeAchieved objects
        from datetime import datetime

        from specify_cli.core.jtbd_metrics import OutcomeAchieved

        outcomes_list = []
        for o in outcomes_data:
            # Reconstruct OutcomeAchieved from dict
            outcome = OutcomeAchieved(
                outcome_id=o.get("outcome_id", ""),
                metric=o.get("metric", ""),
                expected_value=o.get("expected_value", 0.0),
                actual_value=o.get("actual_value", 0.0),
                feature=o.get("feature", ""),
                persona=o.get("persona"),
                context=o.get("context", {}),
            )
            outcomes_list.append(outcome)

        # Calculate date range
        end_date = datetime.now(datetime.now().astimezone().tzinfo or UTC)
        start_date = end_date - timedelta(days=days)

        # Generate the report
        result = jtbd_ops.generate_jtbd_report(
            start_date=start_date,
            end_date=end_date,
            persona=persona,
            jobs=jobs_data if include_jobs else None,
            outcomes=outcomes_list if include_outcomes else None,
        )

        if json_output:
            from dataclasses import asdict

            output = asdict(result)
            dump_json(output)
            return

        # Pretty output
        console.print()
        console.print("[bold]JTBD Metrics Report[/bold]")
        console.print()

        # Summary section
        console.print("[bold cyan]Summary[/bold cyan]")
        console.print()

        if include_jobs:
            console.print(f"  Total Jobs: [cyan]{result.total_jobs}[/cyan]")
            console.print(f"  Completed: [green]{result.completed_jobs}[/green]")
            console.print(f"  Completion Rate: [cyan]{result.completion_rate:.1f}%[/cyan]")

        if include_outcomes and result.outcome_metrics:
            console.print(f"  Total Outcomes: [cyan]{result.outcome_metrics.total_outcomes}[/cyan]")
            console.print(f"  Achieved: [green]{result.outcome_metrics.achieved_count}[/green]")
            console.print(
                f"  Avg Achievement: [cyan]{result.outcome_metrics.avg_achievement_rate:.1f}%[/cyan]"
            )

        console.print()

        # Top features table
        if result.top_performing_features:
            console.print("[bold cyan]Top Performing Features[/bold cyan]")
            console.print()

            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("Rank", style="dim")
            table.add_column("Feature", style="bold")
            table.add_column("Achievement Rate", justify="right")

            for idx, (feature, rate) in enumerate(result.top_performing_features, 1):
                table.add_row(
                    str(idx),
                    feature,
                    f"{rate:.1f}%",
                )

            console.print(table)
            console.print()

        # Footer
        if persona:
            console.print(f"[dim]Filtered by persona: {persona}[/dim]")

    except typer.Exit:
        raise
    except KeyboardInterrupt:
        console.print()
        colour("Operation cancelled.", "yellow")
        raise typer.Exit(130)
    except Exception as e:
        console.print()
        colour(f"[red]Error:[/red] {e}", "red")
        raise typer.Exit(1)


@app.command()
@instrument_command("jtbd.analyze", track_args=True)
def analyze(
    persona: str = typer.Option(None, "--persona", "-p", help="Filter by persona"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Analyze job-to-feature mappings.

    Identifies which features are used to complete which jobs,
    providing insights into feature effectiveness and usage patterns.

    The analysis shows:
    - Which features solve which jobs
    - Completion counts per job
    - Success rates
    - Average durations
    - Persona usage patterns

    Examples
    --------
        # Analyze all job-feature mappings
        $ specify jtbd analyze

        # Filter by persona
        $ specify jtbd analyze --persona python-developer

        # JSON output
        $ specify jtbd analyze --json
    """
    try:
        # Load jobs from runtime
        jobs_data = jtbd_runtime.load_job_completions()

        # Filter by persona if specified
        if persona:
            jobs_data = [j for j in jobs_data if j.get("persona") == persona]

        # Run the analysis
        result = jtbd_ops.analyze_job_feature_mapping(jobs=jobs_data)

        if json_output:
            mappings_data = [
                {
                    "job_id": m.job_id,
                    "features": m.features_used,
                    "completion_count": m.usage_count,
                    "avg_duration": m.avg_duration_seconds,
                    "success_rate": m.success_rate,
                }
                for m in result
            ]
            output = {
                "success": True,
                "mappings": mappings_data,
                "total_jobs": len(jobs_data),
            }
            dump_json(output)
            return

        # Pretty output
        console.print()
        console.print("[bold]Job-Feature Mapping Analysis[/bold]")
        console.print()

        if not result:
            console.print("[yellow]No job completions found to analyze.[/yellow]")
            console.print()
            console.print("Track some jobs first using:")
            console.print(
                "  [cyan]specify jtbd track <job-id> --persona <persona> --feature <feature>[/cyan]"
            )
            return

        # Get unique personas
        personas = list({j.get("persona", "") for j in jobs_data if j.get("persona")})

        # Summary
        console.print("[bold cyan]Summary[/bold cyan]")
        console.print()
        console.print(f"  Total Jobs Analyzed: [cyan]{len(jobs_data)}[/cyan]")
        console.print(f"  Unique Job Types: [cyan]{len(result)}[/cyan]")
        console.print(f"  Personas: [cyan]{', '.join(personas)}[/cyan]")
        console.print()

        # Mappings table
        console.print("[bold cyan]Job-Feature Mappings[/bold cyan]")
        console.print()

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Job ID", style="bold")
        table.add_column("Features Used", style="dim")
        table.add_column("Completions", justify="right")
        table.add_column("Success Rate", justify="right")
        table.add_column("Avg Duration", justify="right")

        for mapping in result[:20]:  # Show top 20
            features_str = ", ".join(mapping.features_used[:3])  # Show first 3 features
            if len(mapping.features_used) > 3:
                features_str += f" +{len(mapping.features_used) - 3} more"

            duration_str = (
                f"{mapping.avg_duration_seconds:.2f}s" if mapping.avg_duration_seconds else "N/A"
            )

            table.add_row(
                mapping.job_id,
                features_str,
                str(mapping.usage_count),
                f"{mapping.success_rate:.1f}%",
                duration_str,
            )

        console.print(table)
        console.print()

        # Footer
        if persona:
            console.print(f"[dim]Filtered by persona: {persona}[/dim]")

    except typer.Exit:
        raise
    except KeyboardInterrupt:
        console.print()
        colour("Operation cancelled.", "yellow")
        raise typer.Exit(130)
    except Exception as e:
        console.print()
        colour(f"[red]Error:[/red] {e}", "red")
        raise typer.Exit(1)


@app.command()
@instrument_command("jtbd.dashboard", track_args=True)
def dashboard(
    persona: str = typer.Option(None, "--persona", "-p", help="Filter by persona"),
    days: int = typer.Option(30, "--days", "-d", help="Number of days to include"),
    refresh_seconds: int = typer.Option(
        0, "--refresh", "-r", help="Auto-refresh interval in seconds (0 to disable)"
    ),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Display real-time JTBD metrics dashboard.

    Shows a comprehensive overview of JTBD metrics including:
    - Job completion rate and statistics
    - Outcome achievement metrics
    - Top performing features
    - Satisfaction scores
    - Painpoint resolution patterns

    The dashboard aggregates data from JSONL files and presents
    it using Rich tables and panels for easy visualization.

    Examples
    --------
        # Show dashboard for all personas
        $ specify jtbd dashboard

        # Filter by persona
        $ specify jtbd dashboard --persona python-developer

        # Show last 7 days
        $ specify jtbd dashboard --days 7

        # Auto-refresh every 5 seconds
        $ specify jtbd dashboard --refresh 5

        # JSON output for scripting
        $ specify jtbd dashboard --json
    """
    try:
        from rich.layout import Layout
        from rich.live import Live
        from rich.panel import Panel

        # Load data from runtime
        jobs_data = jtbd_runtime.load_job_completions()
        outcomes_data = jtbd_runtime.load_outcome_achievements()
        satisfaction_data = jtbd_runtime.load_satisfaction_records()
        painpoints_data = jtbd_runtime.load_painpoint_resolutions()

        # Convert outcomes from dict to OutcomeAchieved objects
        from specify_cli.core.jtbd_metrics import OutcomeAchieved

        outcomes_list = []
        for o in outcomes_data:
            outcome = OutcomeAchieved(
                outcome_id=o.get("outcome_id", ""),
                metric=o.get("metric", ""),
                expected_value=o.get("expected_value", 0.0),
                actual_value=o.get("actual_value", 0.0),
                feature=o.get("feature", ""),
                persona=o.get("persona"),
                context=o.get("context", {}),
            )
            outcomes_list.append(outcome)

        # Convert satisfaction from dict to UserSatisfaction objects
        from specify_cli.core.jtbd_metrics import SatisfactionLevel, UserSatisfaction

        satisfaction_list = []
        for s in satisfaction_data:
            satisfaction = UserSatisfaction(
                outcome_id=s.get("outcome_id", ""),
                feature=s.get("feature", ""),
                persona=s.get("persona"),
                satisfaction_level=SatisfactionLevel(s.get("satisfaction_level", "neutral")),
                met_expectations=s.get("met_expectations", False),
                would_recommend=s.get("would_recommend", False),
                effort_score=s.get("effort_score"),
                feedback_text=s.get("feedback_text"),
            )
            satisfaction_list.append(satisfaction)

        # Convert painpoints from dict to PainpointResolved objects
        from specify_cli.core.jtbd_metrics import PainpointCategory, PainpointResolved

        painpoints_list = []
        for p in painpoints_data:
            painpoint = PainpointResolved(
                painpoint_id=p.get("painpoint_id", ""),
                category=PainpointCategory(p.get("category", "manual_effort")),
                description=p.get("description", ""),
                feature=p.get("feature", ""),
                persona=p.get("persona", ""),
                severity_before=p.get("severity_before", 0),
                severity_after=p.get("severity_after", 0),
            )
            painpoints_list.append(painpoint)

        # Calculate date range
        end_date = datetime.now(datetime.now().astimezone().tzinfo or UTC)
        start_date = end_date - timedelta(days=days)

        # Generate dashboard data
        dashboard_data = jtbd_ops.generate_dashboard_metrics(
            start_date=start_date,
            end_date=end_date,
            persona=persona,
            jobs=jobs_data,
            outcomes=outcomes_list,
            satisfaction_data=satisfaction_list,
            painpoints=painpoints_list,
        )

        if json_output:
            from dataclasses import asdict

            output = asdict(dashboard_data)
            dump_json(output)
            return

        # Render the dashboard
        def make_dashboard() -> Layout:
            """Generate dashboard layout."""
            layout = Layout()
            layout.split_column(
                Layout(name="header", size=3),
                Layout(name="body"),
                Layout(name="footer", size=3),
            )

            # Header
            header_text = "[bold cyan]JTBD Metrics Dashboard[/bold cyan]"
            if persona:
                header_text += f" - [yellow]{persona}[/yellow]"
            header_text += f"\n[dim]Last {days} days • Updated: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}[/dim]"
            layout["header"].update(Panel(header_text, style="bold"))

            # Body - split into columns
            layout["body"].split_row(
                Layout(name="left"),
                Layout(name="right"),
            )

            # Left column - metrics
            layout["left"].split_column(
                Layout(name="jobs_panel", size=8),
                Layout(name="outcomes_panel", size=8),
                Layout(name="satisfaction_panel", size=8),
            )

            # Jobs panel
            jobs_table = Table(show_header=False, box=None)
            jobs_table.add_column("Metric", style="dim")
            jobs_table.add_column("Value", style="bold")
            jobs_table.add_row("Total Jobs", f"[cyan]{dashboard_data.total_jobs}[/cyan]")
            jobs_table.add_row("Completed", f"[green]{dashboard_data.completed_jobs}[/green]")
            jobs_table.add_row("Failed", f"[red]{dashboard_data.failed_jobs}[/red]")
            jobs_table.add_row(
                "Completion Rate", f"[cyan]{dashboard_data.completion_rate:.1f}%[/cyan]"
            )
            layout["jobs_panel"].update(Panel(jobs_table, title="Job Completions", style="cyan"))

            # Outcomes panel
            if dashboard_data.outcomes_summary:
                outcomes_table = Table(show_header=False, box=None)
                outcomes_table.add_column("Metric", style="dim")
                outcomes_table.add_column("Value", style="bold")
                outcomes_table.add_row(
                    "Total Outcomes", f"[cyan]{dashboard_data.outcomes_summary['total']}[/cyan]"
                )
                outcomes_table.add_row(
                    "Achieved", f"[green]{dashboard_data.outcomes_summary['achieved']}[/green]"
                )
                outcomes_table.add_row(
                    "Avg Achievement",
                    f"[cyan]{dashboard_data.outcomes_summary['avg_achievement']:.1f}%[/cyan]",
                )
                layout["outcomes_panel"].update(
                    Panel(outcomes_table, title="Outcome Achievement", style="green")
                )
            else:
                layout["outcomes_panel"].update(
                    Panel("[dim]No outcome data available[/dim]", title="Outcome Achievement")
                )

            # Satisfaction panel
            if dashboard_data.satisfaction_summary:
                sat_table = Table(show_header=False, box=None)
                sat_table.add_column("Metric", style="dim")
                sat_table.add_column("Value", style="bold")
                sat_table.add_row(
                    "Responses",
                    f"[cyan]{dashboard_data.satisfaction_summary['responses']}[/cyan]",
                )
                if dashboard_data.satisfaction_summary["nps_score"] is not None:
                    sat_table.add_row(
                        "NPS Score",
                        f"[cyan]{dashboard_data.satisfaction_summary['nps_score']:.1f}[/cyan]",
                    )
                sat_table.add_row(
                    "Met Expectations",
                    f"[cyan]{dashboard_data.satisfaction_summary['met_expectations']:.1f}%[/cyan]",
                )
                layout["satisfaction_panel"].update(
                    Panel(sat_table, title="User Satisfaction", style="yellow")
                )
            else:
                layout["satisfaction_panel"].update(
                    Panel("[dim]No satisfaction data available[/dim]", title="User Satisfaction")
                )

            # Right column - tables
            layout["right"].split_column(
                Layout(name="top_features", size=12),
                Layout(name="painpoints", size=12),
            )

            # Top features table
            if dashboard_data.top_features:
                features_table = Table(show_header=True, header_style="bold cyan")
                features_table.add_column("Rank", style="dim", width=4)
                features_table.add_column("Feature", style="bold")
                features_table.add_column("Score", justify="right", width=8)

                for idx, (feature, score) in enumerate(dashboard_data.top_features[:5], 1):
                    features_table.add_row(
                        str(idx),
                        feature[:40] + "..." if len(feature) > 40 else feature,
                        f"{score:.1f}%",
                    )

                layout["top_features"].update(
                    Panel(features_table, title="Top Performing Features", style="cyan")
                )
            else:
                layout["top_features"].update(
                    Panel("[dim]No feature data available[/dim]", title="Top Performing Features")
                )

            # Painpoints table
            if dashboard_data.painpoint_summary:
                painpoint_table = Table(show_header=True, header_style="bold cyan")
                painpoint_table.add_column("Category", style="bold")
                painpoint_table.add_column("Count", justify="right", width=8)
                painpoint_table.add_column("Effectiveness", justify="right", width=12)

                for category_data in dashboard_data.painpoint_summary[:5]:
                    painpoint_table.add_row(
                        category_data["category"],
                        str(category_data["count"]),
                        f"{category_data['effectiveness']:.1f}%",
                    )

                layout["painpoints"].update(
                    Panel(painpoint_table, title="Painpoint Resolution", style="magenta")
                )
            else:
                layout["painpoints"].update(
                    Panel("[dim]No painpoint data available[/dim]", title="Painpoint Resolution")
                )

            # Footer
            footer_text = "[dim]Press Ctrl+C to exit"
            if refresh_seconds > 0:
                footer_text += f" • Refreshing every {refresh_seconds}s"
            footer_text += "[/dim]"
            layout["footer"].update(Panel(footer_text))

            return layout

        # Display dashboard
        if refresh_seconds > 0:
            # Live updating dashboard
            import time as time_module

            with Live(make_dashboard(), console=console, refresh_per_second=1) as live:
                try:
                    while True:
                        time_module.sleep(refresh_seconds)
                        # Reload data
                        jobs_data = jtbd_runtime.load_job_completions()
                        outcomes_data = jtbd_runtime.load_outcome_achievements()
                        satisfaction_data = jtbd_runtime.load_satisfaction_records()
                        painpoints_data = jtbd_runtime.load_painpoint_resolutions()
                        # Regenerate dashboard
                        dashboard_data = jtbd_ops.generate_dashboard_metrics(
                            start_date=start_date,
                            end_date=end_date,
                            persona=persona,
                            jobs=jobs_data,
                            outcomes=outcomes_list,
                            satisfaction_data=satisfaction_list,
                            painpoints=painpoints_list,
                        )
                        live.update(make_dashboard())
                except KeyboardInterrupt:
                    pass
        else:
            # Static dashboard
            console.print(make_dashboard())

    except typer.Exit:
        raise
    except KeyboardInterrupt:
        console.print()
        colour("Operation cancelled.", "yellow")
        raise typer.Exit(130)
    except Exception as e:
        console.print()
        colour(f"[red]Error:[/red] {e}", "red")
        raise typer.Exit(1)
