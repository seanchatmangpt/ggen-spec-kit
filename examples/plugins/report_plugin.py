"""
Example Plugin: Report Generator
=================================

A report generator plugin that creates various reports from project data.

This demonstrates:
- Reporter plugin implementation
- Data transformation
- File generation
- Multiple output formats (Markdown, JSON, HTML)
- Template rendering

Installation:
    Copy this file to ~/.specify/plugins/user/report_plugin.py

Usage:
    $ specify report generate --type metrics --output report.md
    $ specify report generate --type coverage --output coverage.html --format html
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import typer
from rich.console import Console

from specify_cli.plugins.api import (
    BasePlugin,
    CommandPlugin,
    PluginConfig,
    PluginMetadata,
    PluginPermissions,
    PluginType,
    ReporterPlugin,
)

console = Console()


class ReportGeneratorPlugin(BasePlugin, CommandPlugin, ReporterPlugin):
    """Report generator plugin.

    Generates various reports from project data including metrics,
    coverage, and dependency reports.
    """

    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="report-plugin",
            version="1.0.0",
            description="Generate reports from project data (metrics, coverage, dependencies)",
            author="Specify Team",
            author_email="info@chatmangpt.com",
            plugin_type=PluginType.REPORTER,
            permissions=[
                PluginPermissions.READ_FILES,
                PluginPermissions.WRITE_FILES,
            ],
            tags=["report", "metrics", "coverage", "documentation"],
            min_cli_version="0.0.1",
        )

    def _initialize_impl(self) -> None:
        """Initialize the plugin."""
        console.print("[green]✓[/green] Report generator plugin initialized")

    def generate_report(
        self, data: Any, output_path: Path, options: dict[str, Any] | None = None
    ) -> Path:
        """Generate report.

        Args:
            data: Data to report on
            output_path: Output file path
            options: Report generation options

        Returns:
            Path to generated report
        """
        options = options or {}
        report_format = options.get("format", "markdown")

        if report_format == "markdown":
            return self._generate_markdown(data, output_path, options)
        elif report_format == "json":
            return self._generate_json(data, output_path, options)
        elif report_format == "html":
            return self._generate_html(data, output_path, options)
        else:
            raise ValueError(f"Unsupported format: {report_format}")

    def _generate_markdown(
        self, data: dict[str, Any], output_path: Path, options: dict[str, Any]
    ) -> Path:
        """Generate Markdown report."""
        report_type = options.get("type", "metrics")

        # Generate report content
        content = f"# {report_type.title()} Report\n\n"
        content += f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"

        if report_type == "metrics":
            content += self._format_metrics_markdown(data)
        elif report_type == "coverage":
            content += self._format_coverage_markdown(data)
        elif report_type == "dependencies":
            content += self._format_dependencies_markdown(data)

        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content)

        return output_path

    def _generate_json(
        self, data: dict[str, Any], output_path: Path, options: dict[str, Any]
    ) -> Path:
        """Generate JSON report."""
        report_data = {
            "generated_at": datetime.now().isoformat(),
            "report_type": options.get("type", "metrics"),
            "data": data,
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report_data, indent=2))

        return output_path

    def _generate_html(
        self, data: dict[str, Any], output_path: Path, options: dict[str, Any]
    ) -> Path:
        """Generate HTML report."""
        report_type = options.get("type", "metrics")

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{report_type.title()} Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
    </style>
</head>
<body>
    <h1>{report_type.title()} Report</h1>
    <p><em>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
    <pre>{json.dumps(data, indent=2)}</pre>
</body>
</html>
"""

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html)

        return output_path

    def _format_metrics_markdown(self, data: dict[str, Any]) -> str:
        """Format metrics data as Markdown."""
        content = "## Code Metrics\n\n"
        content += "| Metric | Value |\n"
        content += "|--------|-------|\n"

        for key, value in data.items():
            content += f"| {key} | {value} |\n"

        return content

    def _format_coverage_markdown(self, data: dict[str, Any]) -> str:
        """Format coverage data as Markdown."""
        content = "## Test Coverage\n\n"

        total_coverage = data.get("total_coverage", 0)
        content += f"**Total Coverage:** {total_coverage}%\n\n"

        content += "### Coverage by File\n\n"
        content += "| File | Coverage |\n"
        content += "|------|----------|\n"

        for file_data in data.get("files", []):
            content += f"| {file_data['name']} | {file_data['coverage']}% |\n"

        return content

    def _format_dependencies_markdown(self, data: dict[str, Any]) -> str:
        """Format dependencies as Markdown."""
        content = "## Dependencies\n\n"

        for category, deps in data.items():
            content += f"### {category.title()}\n\n"
            for dep in deps:
                content += f"- {dep['name']} ({dep['version']})\n"
            content += "\n"

        return content

    def get_commands(self) -> dict[str, typer.Typer]:
        """Get plugin commands."""
        app = typer.Typer(
            name="report",
            help="Report generation commands",
            add_completion=False,
        )

        @app.command("generate")
        def generate(
            report_type: str = typer.Option(
                "metrics",
                "--type",
                "-t",
                help="Report type (metrics, coverage, dependencies)",
            ),
            output: Path = typer.Option(
                Path("report.md"),
                "--output",
                "-o",
                help="Output file path",
            ),
            report_format: str = typer.Option(
                "markdown",
                "--format",
                "-f",
                help="Report format (markdown, json, html)",
            ),
        ) -> None:
            """Generate a report.

            Examples:
                $ specify report generate --type metrics --output metrics.md
                $ specify report generate --type coverage --format html
            """
            # Gather sample data (in real plugin, this would come from actual sources)
            if report_type == "metrics":
                data = {
                    "Total Lines": 5420,
                    "Functions": 234,
                    "Classes": 56,
                    "Test Coverage": "85%",
                    "Complexity": 12.5,
                }
            elif report_type == "coverage":
                data = {
                    "total_coverage": 85.2,
                    "files": [
                        {"name": "src/main.py", "coverage": 92.5},
                        {"name": "src/utils.py", "coverage": 78.3},
                        {"name": "src/api.py", "coverage": 88.1},
                    ],
                }
            elif report_type == "dependencies":
                data = {
                    "production": [
                        {"name": "typer", "version": "0.15.1"},
                        {"name": "rich", "version": "13.0.0"},
                    ],
                    "development": [
                        {"name": "pytest", "version": "8.0.0"},
                        {"name": "ruff", "version": "0.8.0"},
                    ],
                }
            else:
                console.print(f"[red]Error:[/red] Unknown report type: {report_type}")
                raise typer.Exit(1)

            try:
                # Generate report
                result_path = self.generate_report(
                    data,
                    output,
                    {"type": report_type, "format": report_format},
                )

                console.print(f"[green]✓[/green] Report generated: {result_path}")

            except Exception as e:
                console.print(f"[red]Error:[/red] Failed to generate report: {e}")
                raise typer.Exit(1) from e

        @app.command("list-types")
        def list_types() -> None:
            """List available report types."""
            console.print("[bold]Available Report Types:[/bold]")
            console.print("  • metrics      - Code metrics and statistics")
            console.print("  • coverage     - Test coverage report")
            console.print("  • dependencies - Dependency list")

        return {"report": app}

    def _shutdown_impl(self) -> None:
        """Shutdown the plugin."""
        console.print("[yellow]Report generator plugin shutting down[/yellow]")


# Plugin instance for auto-discovery
plugin = ReportGeneratorPlugin()
