"""
specify_cli.commands.cloud - Cloud Operations Command
====================================================

CLI command handler for multi-cloud operations.

This module provides the Typer command interface for cloud operations including:

* Provider initialization and configuration
* Artifact upload and download
* Multi-cloud deployment
* Cost analysis and comparison
* Metrics export

Examples
--------
    $ specify cloud init aws gcp azure
    $ specify cloud upload myapp.tar.gz --provider aws
    $ specify cloud deploy app.tar.gz --providers aws,gcp --regions us-east-1,us-central1
    $ specify cloud costs --compare --days 30
    $ specify cloud export-metrics --provider aws

See Also
--------
- :mod:`specify_cli.ops.cloud` : Business logic
- :mod:`specify_cli.cloud` : Cloud provider implementations
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from specify_cli.core.instrumentation import instrument_command
from specify_cli.core.shell import colour, dump_json
from specify_cli.ops import cloud as cloud_ops

console = Console()

app = typer.Typer(
    name="cloud",
    help="Multi-cloud operations (AWS, GCP, Azure).",
)


@app.command("init")
@instrument_command("cloud.init", track_args=True)
def init_providers(
    providers: list[str] = typer.Argument(..., help="Cloud providers to initialize (aws, gcp, azure)"),
    region: str = typer.Option(None, "--region", "-r", help="Default region for providers"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Initialize cloud providers.

    Examples:
        specify cloud init aws
        specify cloud init aws gcp azure
        specify cloud init aws --region us-west-2
    """
    try:
        console.print()
        console.print("[bold]Initializing Cloud Providers[/bold]")
        console.print()

        # Initialize providers
        statuses = cloud_ops.initialize_providers(providers, region=region)

        if json_output:
            output = {
                name: {
                    "available": status.available,
                    "error": status.error,
                    "config": status.config,
                }
                for name, status in statuses.items()
            }
            dump_json(output)
            return

        # Table output
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Provider", style="bold")
        table.add_column("Status")
        table.add_column("Configuration")

        for name, status in statuses.items():
            if status.available:
                status_text = "[green]✓ Available[/green]"
                config_text = ", ".join(f"{k}={v}" for k, v in status.config.items())
            else:
                status_text = f"[red]✗ Failed[/red]"
                config_text = f"Error: {status.error}"

            table.add_row(name.upper(), status_text, config_text)

        console.print(table)
        console.print()

        # Summary
        available = sum(1 for s in statuses.values() if s.available)
        total = len(statuses)

        if available == total:
            colour(f"[green]✓ All {total} provider(s) initialized successfully[/green]", "green")
        elif available > 0:
            colour(
                f"[yellow]⚠ {available}/{total} provider(s) initialized[/yellow]",
                "yellow",
            )
        else:
            colour("[red]✗ All providers failed to initialize[/red]", "red")
            raise typer.Exit(1) from None

    except KeyboardInterrupt:
        console.print()
        colour("Operation cancelled.", "yellow")
        raise typer.Exit(130)

    except Exception as e:
        console.print()
        colour(f"[red]Error initializing providers:[/red] {e}", "red")
        raise typer.Exit(1) from None


@app.command("upload")
@instrument_command("cloud.upload", track_args=True)
def upload_artifact(
    local_path: Path = typer.Argument(..., help="Local file to upload"),
    remote_key: str = typer.Option(None, "--key", "-k", help="Remote storage key"),
    provider: str = typer.Option("aws", "--provider", "-p", help="Cloud provider"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Upload artifact to cloud storage.

    Examples:
        specify cloud upload app.tar.gz --provider aws
        specify cloud upload build.zip --key releases/v1.0.0/build.zip --provider gcp
    """
    try:
        # Default remote key
        if not remote_key:
            remote_key = f"artifacts/{local_path.name}"

        console.print()
        console.print(f"[bold]Uploading to {provider.upper()}[/bold]")
        console.print()

        result = cloud_ops.upload_artifact(provider, local_path, remote_key)

        if json_output:
            output = {
                "success": result.success,
                "provider": result.provider,
                "operation": result.operation,
                "message": result.message,
                "data": result.data,
                "error": result.error,
            }
            dump_json(output)
            return

        if result.success:
            colour(f"[green]✓ {result.message}[/green]", "green")
            console.print()
            console.print(f"[bold]URL:[/bold] {result.data.get('url', 'N/A')}")
            console.print(f"[bold]Key:[/bold] {result.data.get('key', 'N/A')}")
        else:
            colour(f"[red]✗ {result.message}[/red]", "red")
            raise typer.Exit(1) from None

    except KeyboardInterrupt:
        console.print()
        colour("Operation cancelled.", "yellow")
        raise typer.Exit(130)

    except Exception as e:
        console.print()
        colour(f"[red]Upload failed:[/red] {e}", "red")
        raise typer.Exit(1) from None


@app.command("deploy")
@instrument_command("cloud.deploy", track_args=True)
def deploy_multicloud(
    artifact: Path = typer.Argument(..., help="Artifact to deploy"),
    providers: str = typer.Option("aws", "--providers", "-p", help="Comma-separated provider list"),
    regions: str = typer.Option(None, "--regions", "-r", help="Comma-separated region list"),
    instance_type: str = typer.Option(None, "--instance-type", "-t", help="Instance type"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Deploy to multiple cloud providers.

    Examples:
        specify cloud deploy app.tar.gz --providers aws
        specify cloud deploy app.tar.gz --providers aws,gcp,azure --regions us-east-1,us-central1,eastus
    """
    try:
        # Parse providers and regions
        provider_list = [p.strip() for p in providers.split(",")]
        region_list = [r.strip() for r in regions.split(",")] if regions else None

        console.print()
        console.print("[bold]Multi-Cloud Deployment[/bold]")
        console.print()
        console.print(f"Artifact: {artifact}")
        console.print(f"Providers: {', '.join(provider_list)}")
        if region_list:
            console.print(f"Regions: {', '.join(region_list)}")
        console.print()

        result = cloud_ops.deploy_multicloud(
            artifact,
            providers=provider_list,
            regions=region_list,
            instance_type=instance_type,
        )

        if json_output:
            output = {
                "success": result.success,
                "success_rate": result.success_rate,
                "deployments": [
                    {
                        "provider": d.provider,
                        "success": d.success,
                        "message": d.message,
                        "data": d.data,
                        "error": d.error,
                    }
                    for d in result.deployments
                ],
                "failed_providers": result.failed_providers,
            }
            dump_json(output)
            return

        # Table output
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Provider", style="bold")
        table.add_column("Status")
        table.add_column("Region")
        table.add_column("Endpoint")

        for deployment in result.deployments:
            if deployment.success:
                status_text = "[green]✓ Deployed[/green]"
                region = deployment.data.get("region", "N/A")
                endpoint = deployment.data.get("endpoint", "N/A")
            else:
                status_text = "[red]✗ Failed[/red]"
                region = "N/A"
                endpoint = deployment.error or "N/A"

            table.add_row(deployment.provider.upper(), status_text, region, endpoint)

        console.print(table)
        console.print()

        # Summary
        success_rate = result.success_rate * 100
        console.print(f"[bold]Success Rate:[/bold] {success_rate:.1f}%")

        if result.success:
            colour("[green]✓ All deployments successful[/green]", "green")
        elif success_rate > 0:
            colour(
                f"[yellow]⚠ {len(result.failed_providers)} deployment(s) failed[/yellow]",
                "yellow",
            )
        else:
            colour("[red]✗ All deployments failed[/red]", "red")
            raise typer.Exit(1) from None

    except KeyboardInterrupt:
        console.print()
        colour("Operation cancelled.", "yellow")
        raise typer.Exit(130)

    except Exception as e:
        console.print()
        colour(f"[red]Deployment failed:[/red] {e}", "red")
        raise typer.Exit(1) from None


@app.command("costs")
@instrument_command("cloud.costs", track_args=True)
def compare_costs(
    providers: str = typer.Option(None, "--providers", "-p", help="Comma-separated provider list"),
    days: int = typer.Option(30, "--days", "-d", help="Number of days to analyze"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Compare costs across cloud providers.

    Examples:
        specify cloud costs
        specify cloud costs --providers aws,gcp --days 7
    """
    try:
        from datetime import UTC, datetime, timedelta

        # Parse providers
        provider_list = [p.strip() for p in providers.split(",")] if providers else None

        # Calculate date range
        end_date = datetime.now(UTC)
        start_date = end_date - timedelta(days=days)

        console.print()
        console.print("[bold]Cloud Cost Analysis[/bold]")
        console.print()
        console.print(f"Period: {start_date.date()} to {end_date.date()} ({days} days)")
        console.print()

        cost_data = cloud_ops.compare_costs(
            providers=provider_list,
            start_date=start_date,
            end_date=end_date,
        )

        if json_output:
            dump_json(cost_data)
            return

        if not cost_data:
            colour("[yellow]No cost data available[/yellow]", "yellow")
            return

        # Table output
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Provider", style="bold")
        table.add_column("Total Cost", justify="right")
        table.add_column("Currency")
        table.add_column("Top Service")

        for provider_name, data in cost_data.items():
            if provider_name.startswith("_"):
                continue

            total = data.get("total_cost", 0.0)
            currency = data.get("currency", "USD")
            breakdown = data.get("breakdown", {})

            # Find top service by cost
            top_service = "N/A"
            if breakdown:
                top_service = max(breakdown.items(), key=lambda x: x[1])[0]

            table.add_row(provider_name.upper(), f"${total:.2f}", currency, top_service)

        console.print(table)
        console.print()

        # Analysis
        analysis = cost_data.get("_analysis", {})
        if analysis:
            cheapest = analysis.get("cheapest")
            if cheapest:
                console.print(f"[bold]Cheapest Provider:[/bold] {cheapest.upper()}")
                console.print()

            recommendations = analysis.get("recommendations", [])
            if recommendations:
                console.print("[bold]Recommendations:[/bold]")
                for rec in recommendations:
                    console.print(f"  • {rec}")

    except KeyboardInterrupt:
        console.print()
        colour("Operation cancelled.", "yellow")
        raise typer.Exit(130)

    except Exception as e:
        console.print()
        colour(f"[red]Cost analysis failed:[/red] {e}", "red")
        raise typer.Exit(1) from None


@app.command("export-metrics")
@instrument_command("cloud.export_metrics", track_args=True)
def export_metrics(
    provider: str = typer.Option("aws", "--provider", "-p", help="Cloud provider"),
    namespace: str = typer.Option("SpecifyCLI", "--namespace", "-n", help="Metrics namespace"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Export OpenTelemetry metrics to cloud monitoring.

    Examples:
        specify cloud export-metrics --provider aws
        specify cloud export-metrics --provider gcp --namespace MyApp
    """
    try:
        console.print()
        console.print(f"[bold]Exporting Metrics to {provider.upper()}[/bold]")
        console.print()

        # Example metrics (in real usage, these would come from OTEL)
        metrics = {
            "operations.count": 42.0,
            "operations.duration": 1.5,
            "operations.errors": 0.0,
        }

        result = cloud_ops.export_metrics_to_cloud(
            provider,
            metrics=metrics,
            namespace=namespace,
        )

        if json_output:
            output = {
                "success": result.success,
                "provider": result.provider,
                "message": result.message,
                "data": result.data,
                "error": result.error,
            }
            dump_json(output)
            return

        if result.success:
            colour(f"[green]✓ {result.message}[/green]", "green")
            exported = result.data.get("exported", 0)
            total = result.data.get("total", 0)
            console.print()
            console.print(f"Exported: {exported}/{total} metrics")
        else:
            colour(f"[red]✗ {result.message}[/red]", "red")
            raise typer.Exit(1) from None

    except KeyboardInterrupt:
        console.print()
        colour("Operation cancelled.", "yellow")
        raise typer.Exit(130)

    except Exception as e:
        console.print()
        colour(f"[red]Metrics export failed:[/red] {e}", "red")
        raise typer.Exit(1) from None
