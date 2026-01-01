"""CLI command for validating code against RDF specifications.

Implements constitutional equation validation: verifies that code = μ(spec.ttl)
"""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console
from rich.table import Table
from typer import Typer

from specify_cli.core.spec_validator import validate_runtime_modules

app = Typer(help="Validate implementations against RDF specifications")
console = Console()


@app.command()
def specs(
    json_output: bool = False,
    verbose: bool = False,
) -> int:
    """Validate that code implementations match RDF specifications.

    Checks the constitutional equation: implementation = μ(specification.ttl)

    This ensures the system can observe itself and detect when code diverges
    from its specification.

    Args:
        json_output: Output results as JSON
        verbose: Show detailed validation results

    Returns:
        0 if all validations pass, 1 if any fail
    """
    console.print("[bold cyan]Validating specifications...[/bold cyan]\n")

    report = validate_runtime_modules()

    if json_output:
        console.print(json.dumps(report, indent=2))
        return 0 if report["invalid_modules"] == 0 else 1

    # Display summary
    summary_table = Table(title="Validation Summary")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="green")

    summary_table.add_row(
        "Total Modules",
        str(report["total_modules"]),
    )
    summary_table.add_row(
        "Valid Modules",
        f"[green]{report['valid_modules']}[/green]",
    )
    summary_table.add_row(
        "Invalid Modules",
        f"[red]{report['invalid_modules']}[/red]"
        if report["invalid_modules"] > 0
        else f"[green]{report['invalid_modules']}[/green]",
    )

    console.print(summary_table)
    console.print()

    # Display module results
    if verbose:
        for module_result in report["modules"]:
            console.print(
                f"\n[bold]{module_result['module']}[/bold]"
            )
            console.print(
                f"  Specification: {module_result['specification']}"
            )
            console.print(
                f"  Implementation: {module_result['implementation']}"
            )

            summary = module_result["summary"]
            status = "[green]✓ VALID[/green]" if module_result["valid"] else "[red]✗ INVALID[/red]"
            console.print(
                f"  Status: {status}"
            )
            console.print(
                f"  Checks: {summary['passed']}/{summary['total']} passed "
                f"({summary['success_rate']:.1f}%)"
            )

            # Show failed checks
            failed_checks = [
                r for r in module_result["results"]
                if r["status"] != "valid"
            ]

            if failed_checks:
                console.print("  [yellow]Failed Checks:[/yellow]")
                for check in failed_checks:
                    console.print(
                        f"    - {check['component']}: {check['message']}"
                    )

    return 0 if report["invalid_modules"] == 0 else 1
