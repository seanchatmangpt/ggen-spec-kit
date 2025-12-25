"""
specify_cli.commands.dspy_latex
================================

DSPy LaTeX Integration Command Group

CLI command handlers for DSPy-powered LaTeX document processing and PDF compilation.

This module provides Typer command interface for:
- LaTeX document processing with intelligent validation
- Multi-stage PDF compilation with error recovery
- Cognitive optimization using DSPy and machine learning
- Comprehensive observability and health monitoring
- Dependency verification and system diagnostics

Commands
--------
process : Process LaTeX files with DSPy document processor
compile : Compile LaTeX to PDF with multi-stage pipeline
optimize : Optimize LaTeX documents using cognitive layer
observe : View observability metrics and health status
verify : Verify DSPy LaTeX installation and dependencies

Examples
--------
    $ specify dspy-latex process thesis.tex --validate
    $ specify dspy-latex compile paper.tex --backend xelatex
    $ specify dspy-latex optimize document.tex --level aggressive
    $ specify dspy-latex observe --format json
    $ specify dspy-latex verify

See Also
--------
- :mod:`specify_cli.dspy_latex.processor` : LaTeX document processing
- :mod:`specify_cli.dspy_latex.compiler` : PDF compilation engine
- :mod:`specify_cli.dspy_latex.optimizer` : Cognitive optimization
- :mod:`specify_cli.dspy_latex.observability` : Metrics and monitoring

Notes
-----
All commands follow the three-tier architecture:
- Commands layer: CLI interface (this module)
- Operations layer: Business logic (dspy_latex module)
- Runtime layer: I/O and subprocess execution
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from specify_cli.core.instrumentation import instrument_command

if TYPE_CHECKING:
    from pathlib import Path

# Create Typer app
app = typer.Typer(
    name="dspy-latex",
    help="DSPy-powered LaTeX processing and PDF compilation",
)

console = Console()


# ============================================================================
# Helper Functions
# ============================================================================


def _check_dspy_availability() -> bool:
    """Check if DSPy is available."""
    try:
        import dspy  # noqa: F401

        return True
    except ImportError:
        return False


def _display_error_panel(title: str, message: str) -> None:
    """Display error panel with consistent formatting."""
    console.print()
    console.print(
        Panel(
            f"[red]{message}[/red]",
            title=title,
            border_style="red",
        )
    )


def _display_success_panel(title: str, message: str) -> None:
    """Display success panel with consistent formatting."""
    console.print()
    console.print(
        Panel(
            f"[green]{message}[/green]",
            title=title,
            border_style="green",
        )
    )


# ============================================================================
# Commands
# ============================================================================


@app.command("process")
@instrument_command("dspy_latex.process", track_args=True)
def process_command(
    file_path: Path = typer.Argument(
        ...,
        help="Path to LaTeX file to process",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    validate: bool = typer.Option(
        True,
        "--validate/--no-validate",
        help="Perform DSPy-powered validation",
    ),
    analyze: bool = typer.Option(
        False,
        "--analyze",
        "-a",
        help="Analyze document structure and complexity",
    ),
    suggest_packages: bool = typer.Option(
        False,
        "--suggest-packages",
        help="Suggest missing LaTeX packages",
    ),
    output_json: bool = typer.Option(
        False,
        "--json",
        help="Output results as JSON",
    ),
) -> None:
    """
    Process LaTeX files with DSPy document processor.

    Performs intelligent parsing, validation, and analysis of LaTeX documents
    using DSPy-powered chain-of-thought reasoning for error detection and
    fix suggestions.

    Examples:
        specify dspy-latex process thesis.tex --validate
        specify dspy-latex process paper.tex --analyze --json
        specify dspy-latex process document.tex --suggest-packages
    """
    try:
        # Import processor
        from specify_cli.dspy_latex.processor import LaTeXProcessor, process_latex_file

        if not _check_dspy_availability():
            console.print("[yellow]⚠ DSPy not available - using basic processing[/yellow]")

        console.print()
        console.print(f"[bold cyan]Processing LaTeX document:[/bold cyan] {file_path}")
        console.print()

        # Process document
        processor = LaTeXProcessor()
        doc, validation_result, _optimization_result = process_latex_file(
            file_path,
            validate=validate,
            optimize=False,  # Optimize command handles this
        )

        # Display document statistics
        stats = doc.stats()
        stats_table = Table(title="Document Statistics", show_header=True)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")

        for key, value in stats.items():
            stats_table.add_row(key.replace("_", " ").title(), str(value))

        console.print(stats_table)
        console.print()

        # Display validation results
        if validation_result:
            if validation_result.is_valid:
                console.print("[green]✓ Validation passed[/green]")
                if validation_result.warnings:
                    console.print(f"[yellow]  {len(validation_result.warnings)} warnings[/yellow]")
            else:
                console.print(f"[red]✗ Validation failed: {validation_result.error_count} errors[/red]")
                console.print()

                # Show errors
                error_table = Table(title="Validation Errors", show_header=True)
                error_table.add_column("Line", style="yellow", width=8)
                error_table.add_column("Severity", style="red", width=10)
                error_table.add_column("Message", style="white")

                for error in validation_result.errors[:10]:  # Show first 10
                    error_table.add_row(
                        str(error.line),
                        error.severity.value.upper(),
                        error.message,
                    )

                console.print(error_table)
                console.print()

                if validation_result.error_count > 10:
                    console.print(f"[dim]... and {validation_result.error_count - 10} more errors[/dim]")

        # Analyze structure if requested
        if analyze:
            console.print()
            console.print("[bold]Document Structure:[/bold]")
            console.print(f"  • Chapters: {len(doc.chapters)}")
            console.print(f"  • Sections: {len(doc.sections)}")
            console.print(f"  • Equations: {len(doc.equations)}")
            console.print(f"  • Figures: {sum(1 for s in doc.structures if 'figure' in s.content.lower())}")
            console.print(f"  • Citations: {len(doc.citations)}")

        # Suggest packages if requested
        if suggest_packages:
            suggested = processor.suggest_packages(doc)
            if suggested:
                console.print()
                console.print("[bold]Suggested Packages:[/bold]")
                for pkg in suggested:
                    console.print(f"  • {pkg}")
            else:
                console.print()
                console.print("[dim]No additional packages suggested[/dim]")

        # JSON output
        if output_json:
            import json

            output = {
                "file": str(file_path),
                "stats": stats,
                "validation": {
                    "valid": validation_result.is_valid if validation_result else None,
                    "errors": validation_result.error_count if validation_result else 0,
                    "warnings": validation_result.warning_count if validation_result else 0,
                }
                if validation_result
                else None,
            }
            console.print()
            console.print(json.dumps(output, indent=2))

    except ImportError as e:
        _display_error_panel(
            "DSPy LaTeX Module Not Available",
            f"DSPy LaTeX module could not be imported: {e}\n\n"
            "Install with: pip install dspy",
        )
        raise typer.Exit(1) from e

    except Exception as e:
        _display_error_panel("Processing Error", str(e))
        raise typer.Exit(1) from e


@app.command("compile")
@instrument_command("dspy_latex.compile", track_args=True)
def compile_command(
    file_path: Path = typer.Argument(
        ...,
        help="Path to LaTeX file to compile",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    backend: str = typer.Option(
        "pdflatex",
        "--backend",
        "-b",
        help="LaTeX backend: pdflatex, xelatex, lualatex, latexmk",
    ),
    output_dir: Path | None = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Output directory for PDF and auxiliary files",
    ),
    enable_recovery: bool = typer.Option(
        True,
        "--recovery/--no-recovery",
        help="Enable autonomous error recovery",
    ),
    max_retries: int = typer.Option(
        3,
        "--max-retries",
        help="Maximum retry attempts per stage",
    ),
    compress_pdf: bool = typer.Option(
        True,
        "--compress/--no-compress",
        help="Enable PDF compression",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force recompilation (ignore cache)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed compilation output",
    ),
) -> None:
    """
    Compile LaTeX to PDF with multi-stage pipeline.

    Executes the 5-stage compilation pipeline:
    - μ₁ Normalize: Validation and package resolution
    - μ₂ Preprocess: Macro expansion and file inclusion
    - μ₃ Compile: Backend execution (pdflatex/xelatex/lualatex)
    - μ₄ Postprocess: BibTeX, makeindex, cross-reference resolution
    - μ₅ Optimize: PDF compression and receipt generation

    Examples:
        specify dspy-latex compile thesis.tex
        specify dspy-latex compile paper.tex --backend xelatex
        specify dspy-latex compile doc.tex --output-dir build --compress
        specify dspy-latex compile article.tex --force --verbose
    """
    try:
        from specify_cli.dspy_latex.compiler import (
            CompilationBackend,
            CompilationCache,
            PDFCompiler,
        )

        console.print()
        console.print(f"[bold cyan]Compiling LaTeX document:[/bold cyan] {file_path}")
        console.print(f"[cyan]Backend:[/cyan] {backend}")
        console.print(f"[cyan]Output directory:[/cyan] {output_dir or file_path.parent}")
        console.print()

        # Parse backend
        try:
            backend_enum = CompilationBackend(backend.lower())
        except ValueError:
            console.print(f"[red]Invalid backend: {backend}[/red]")
            console.print("[yellow]Valid backends: pdflatex, xelatex, lualatex, latexmk[/yellow]")
            raise typer.Exit(1) from None

        # Initialize cache
        cache = CompilationCache() if not force else None

        # Create compiler
        compiler = PDFCompiler(
            backend=backend_enum,
            enable_recovery=enable_recovery,
            max_retries=max_retries,
            cache=cache,
            compress_pdf=compress_pdf,
            output_dir=output_dir,
        )

        # Compile with progress indication
        with console.status("[bold green]Compiling...", spinner="dots"):
            result = compiler.compile(file_path, force=force)

        console.print()

        if result.success:
            _display_success_panel(
                "Compilation Successful",
                f"PDF created: {result.pdf_path}\n"
                f"Duration: {result.total_duration:.2f}s\n"
                f"Receipt: {result.receipt_path}",
            )

            # Show stage durations if verbose
            if verbose:
                console.print()
                stage_table = Table(title="Stage Performance", show_header=True)
                stage_table.add_column("Stage", style="cyan")
                stage_table.add_column("Duration", style="green")
                stage_table.add_column("Status", style="white")

                for stage_type, stage_result in result.stage_results.items():
                    status = "✓" if stage_result.success else "✗"
                    stage_table.add_row(
                        stage_type.value,
                        f"{stage_result.duration:.2f}s",
                        status,
                    )

                console.print(stage_table)

            # Show warnings if any
            if result.warnings:
                console.print()
                console.print(f"[yellow]⚠ {len(result.warnings)} warnings generated[/yellow]")
                if verbose:
                    for warning in result.warnings[:5]:
                        console.print(f"  [dim]{warning}[/dim]")

        else:
            _display_error_panel(
                "Compilation Failed",
                f"Compilation failed after {result.total_duration:.2f}s\n"
                f"Errors: {len(result.errors)}",
            )

            # Show errors
            if result.errors:
                console.print()
                console.print("[bold red]Errors:[/bold red]")
                for error in result.errors[:10]:
                    console.print(f"  [red]✗[/red] {error.message}")
                    if error.suggestion:
                        console.print(f"    [dim]→ {error.suggestion}[/dim]")

            raise typer.Exit(1)  # noqa: TRY301

    except ImportError as e:
        _display_error_panel(
            "DSPy LaTeX Module Not Available",
            f"DSPy LaTeX module could not be imported: {e}",
        )
        raise typer.Exit(1) from e

    except Exception as e:
        _display_error_panel("Compilation Error", str(e))
        if verbose:
            console.print_exception()
        raise typer.Exit(1) from e


@app.command("optimize")
@instrument_command("dspy_latex.optimize", track_args=True)
def optimize_command(
    file_path: Path = typer.Argument(
        ...,
        help="Path to LaTeX file to optimize",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    level: str = typer.Option(
        "moderate",
        "--level",
        "-l",
        help="Optimization level: conservative, moderate, aggressive",
    ),
    output_file: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file for optimized LaTeX (default: overwrites input)",
    ),
    max_iterations: int = typer.Option(
        3,
        "--max-iterations",
        help="Maximum optimization iterations",
    ),
    enable_ml: bool = typer.Option(
        True,
        "--ml/--no-ml",
        help="Enable machine learning components",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would be optimized without applying changes",
    ),
) -> None:
    """
    Optimize LaTeX documents using cognitive layer.

    Uses DSPy-powered cognitive architecture (Ψ₁ → Ψ₂ → Ψ₃):
    - Ψ₁ Perception: Analyze document complexity
    - Ψ₂ Reasoning: Select optimization strategies
    - Ψ₃ Generation: Apply adaptive transformations

    Exhibits autonomic computing properties:
    - Self-configuration: Adapts to document type
    - Self-optimization: Learns best strategies
    - Self-healing: Proposes fixes for errors
    - Self-protection: Validates changes

    Examples:
        specify dspy-latex optimize thesis.tex --level aggressive
        specify dspy-latex optimize paper.tex --output optimized.tex
        specify dspy-latex optimize doc.tex --dry-run
    """
    try:
        from specify_cli.dspy_latex.optimizer import LaTeXOptimizer, OptimizationLevel

        if not _check_dspy_availability() and enable_ml:
            console.print("[yellow]⚠ DSPy not available - ML features disabled[/yellow]")
            enable_ml = False

        console.print()
        console.print(f"[bold cyan]Optimizing LaTeX document:[/bold cyan] {file_path}")
        console.print(f"[cyan]Level:[/cyan] {level}")
        console.print(f"[cyan]Max iterations:[/cyan] {max_iterations}")
        console.print()

        # Parse optimization level
        try:
            level_enum = OptimizationLevel(level.lower())
        except ValueError:
            console.print(f"[red]Invalid optimization level: {level}[/red]")
            console.print("[yellow]Valid levels: conservative, moderate, aggressive[/yellow]")
            raise typer.Exit(1) from None

        # Read document
        content = file_path.read_text(encoding="utf-8")

        # Create optimizer
        optimizer = LaTeXOptimizer(
            optimization_level=level_enum,
            enable_ml=enable_ml,
        )

        # Analyze complexity (Ψ₁ Perception)
        console.print("[bold]Ψ₁ Perception: Analyzing document complexity...[/bold]")
        complexity = optimizer.analyze_complexity(content)

        complexity_table = Table(show_header=False)
        complexity_table.add_column("Metric", style="cyan")
        complexity_table.add_column("Value", style="green")

        complexity_table.add_row("Document Type", complexity.document_type.value)
        complexity_table.add_row("Complexity Score", f"{complexity.complexity_score:.1f}")
        complexity_table.add_row("Total Lines", str(complexity.total_lines))
        complexity_table.add_row("Equations", str(complexity.equation_count))
        complexity_table.add_row("Figures", str(complexity.figure_count))
        complexity_table.add_row("Packages", str(complexity.package_count))

        console.print(complexity_table)
        console.print()

        # Select strategies (Ψ₂ Reasoning)
        console.print("[bold]Ψ₂ Reasoning: Selecting optimization strategies...[/bold]")
        strategies = optimizer.select_strategies(complexity)
        console.print(f"[cyan]Selected strategies:[/cyan] {', '.join(strategies)}")
        console.print()

        if dry_run:
            console.print("[yellow]Dry run mode - no changes will be applied[/yellow]")
            for strategy_name in strategies:
                strategy = optimizer.strategies.get(strategy_name)
                if strategy:
                    analysis = strategy.analyze(content)
                    console.print(f"\n[bold]{strategy_name}:[/bold]")
                    for key, value in analysis.items():
                        console.print(f"  • {key}: {value}")
            return

        # Apply optimizations (Ψ₃ Generation)
        console.print("[bold]Ψ₃ Generation: Applying optimizations...[/bold]")
        with console.status("[bold green]Optimizing...", spinner="dots"):
            optimized_content, metrics = optimizer.optimize(content, max_iterations=max_iterations)

        console.print()
        _display_success_panel(
            "Optimization Complete",
            f"Applied {metrics.successful_optimizations} optimizations\n"
            f"Failed: {metrics.failed_optimizations}",
        )

        # Show metrics
        console.print()
        metrics_table = Table(title="Optimization Metrics", show_header=True)
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Value", style="green")

        metrics_table.add_row("Total Optimizations", str(metrics.total_optimizations))
        metrics_table.add_row("Successful", str(metrics.successful_optimizations))
        metrics_table.add_row("Failed", str(metrics.failed_optimizations))

        console.print(metrics_table)
        console.print()

        # Show strategies used
        if metrics.strategies_used:
            console.print("[bold]Strategies Applied:[/bold]")
            for strategy, count in metrics.strategies_used.items():
                console.print(f"  • {strategy}: {count} times")
            console.print()

        # Write output
        output_path = output_file or file_path
        output_path.write_text(optimized_content, encoding="utf-8")
        console.print(f"[green]✓ Optimized content written to:[/green] {output_path}")

    except ImportError as e:
        _display_error_panel(
            "DSPy LaTeX Module Not Available",
            f"DSPy LaTeX module could not be imported: {e}",
        )
        raise typer.Exit(1) from e

    except Exception as e:
        _display_error_panel("Optimization Error", str(e))
        raise typer.Exit(1) from e


@app.command("observe")
@instrument_command("dspy_latex.observe", track_args=True)
def observe_command(
    format: str = typer.Option(
        "table",
        "--format",
        "-f",
        help="Output format: table, json, prometheus, markdown",
    ),
    export_file: Path | None = typer.Option(
        None,
        "--export",
        "-e",
        help="Export metrics to file",
    ),
    show_health: bool = typer.Option(
        True,
        "--health/--no-health",
        help="Show health score",
    ),
    show_trends: bool = typer.Option(
        True,
        "--trends/--no-trends",
        help="Show performance trends",
    ),
    show_anomalies: bool = typer.Option(
        False,
        "--anomalies",
        help="Show detected anomalies",
    ),
) -> None:
    """
    View observability metrics and health status.

    Displays comprehensive metrics including:
    - Compilation performance (duration, success rate)
    - Quality metrics (errors, warnings)
    - Health score and trends
    - Anomaly detection
    - Resource usage

    Examples:
        specify dspy-latex observe
        specify dspy-latex observe --format json
        specify dspy-latex observe --export metrics.json
        specify dspy-latex observe --anomalies
    """
    try:
        from specify_cli.dspy_latex.observability import (
            MetricsAnalyzer,
            PerformanceDashboard,
            TelemetryCollector,
        )

        # Initialize collector (would typically load from persistent storage)
        collector = TelemetryCollector()

        if not collector.metrics_history:
            console.print()
            console.print("[yellow]⚠ No metrics data available[/yellow]")
            console.print("[dim]Compile some LaTeX documents to collect metrics[/dim]")
            return

        console.print()
        console.print("[bold cyan]DSPy LaTeX Observability Dashboard[/bold cyan]")
        console.print()

        # Get summary
        summary = collector.get_metrics_summary()

        # Show overview
        if format == "table":
            overview_table = Table(title="Overview", show_header=True)
            overview_table.add_column("Metric", style="cyan")
            overview_table.add_column("Value", style="green")

            overview_table.add_row("Total Compilations", str(summary.get("total_compilations", 0)))
            overview_table.add_row(
                "Successful", str(summary.get("successful_compilations", 0))
            )
            overview_table.add_row("Failed", str(summary.get("failed_compilations", 0)))
            overview_table.add_row(
                "Success Rate", f"{summary.get('success_rate', 0):.1%}"
            )

            console.print(overview_table)
            console.print()

            # Performance stats
            duration_stats = summary.get("duration_stats", {})
            if duration_stats:
                perf_table = Table(title="Performance", show_header=True)
                perf_table.add_column("Metric", style="cyan")
                perf_table.add_column("Duration", style="green")

                perf_table.add_row("Mean", f"{duration_stats.get('mean', 0):.2f}s")
                perf_table.add_row("Median", f"{duration_stats.get('median', 0):.2f}s")
                perf_table.add_row("P95", f"{duration_stats.get('p95', 0):.2f}s")
                perf_table.add_row("P99", f"{duration_stats.get('p99', 0):.2f}s")
                perf_table.add_row("Min", f"{duration_stats.get('min', 0):.2f}s")
                perf_table.add_row("Max", f"{duration_stats.get('max', 0):.2f}s")

                console.print(perf_table)
                console.print()

        # Health score
        if show_health:
            analyzer = MetricsAnalyzer(collector)
            health_score = analyzer.calculate_health_score()

            health_color = "green" if health_score > 0.8 else "yellow" if health_score > 0.5 else "red"
            console.print(f"[bold]Health Score:[/bold] [{health_color}]{health_score:.1%}[/{health_color}]")
            console.print()

        # Trends
        if show_trends and len(collector.metrics_history) >= 5:
            analyzer = MetricsAnalyzer(collector)
            trends = analyzer.analyze_performance_trends()

            if trends.get("status") != "insufficient_data":
                console.print("[bold]Performance Trends:[/bold]")
                console.print(f"  • Duration: {trends.get('duration_trend', 'unknown')}")
                console.print(f"  • Errors: {trends.get('error_trend', 'unknown')}")
                console.print(f"  • Memory: {trends.get('memory_trend', 'unknown')}")
                console.print()

        # Anomalies
        if show_anomalies:
            analyzer = MetricsAnalyzer(collector)
            anomalies = analyzer.detect_anomalies()

            if anomalies:
                console.print(f"[bold yellow]⚠ {len(anomalies)} Anomalies Detected:[/bold yellow]")
                for anomaly in anomalies:
                    console.print(f"  • {anomaly.metric_name}: deviation score {anomaly.deviation_score:.2f}")
                console.print()
            else:
                console.print("[green]✓ No anomalies detected[/green]")
                console.print()

        # Export if requested
        if export_file:
            dashboard = PerformanceDashboard(collector, MetricsAnalyzer(collector))

            if format == "json":
                dashboard.save_dashboard(export_file)
            elif format == "prometheus":
                dashboard.save_prometheus_metrics(export_file)
            elif format == "markdown":
                report = analyzer.generate_report()
                report.save(export_file, output_format="markdown")
            else:
                dashboard.save_dashboard(export_file)

            console.print(f"[green]✓ Metrics exported to:[/green] {export_file}")

        # JSON output
        elif format == "json":
            import json

            console.print(json.dumps(summary, indent=2))

        # Prometheus output
        elif format == "prometheus":
            prometheus_output = collector.export_prometheus()
            console.print(prometheus_output)

        # Markdown output
        elif format == "markdown":
            analyzer = MetricsAnalyzer(collector)
            report = analyzer.generate_report()
            console.print(report.to_markdown())

    except ImportError as e:
        _display_error_panel(
            "DSPy LaTeX Module Not Available",
            f"DSPy LaTeX module could not be imported: {e}",
        )
        raise typer.Exit(1) from e

    except Exception as e:
        _display_error_panel("Observability Error", str(e))
        raise typer.Exit(1) from e


@app.command("verify")
@instrument_command("dspy_latex.verify", track_args=True)
def verify_command(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed verification output",
    ),
) -> None:
    """
    Verify DSPy LaTeX installation and dependencies.

    Checks:
    - DSPy installation and version
    - LaTeX backends availability (pdflatex, xelatex, lualatex)
    - Required Python packages
    - Optional dependencies
    - System tools (bibtex, makeindex, ghostscript)

    Examples:
        specify dspy-latex verify
        specify dspy-latex verify --verbose
    """
    console.print()
    console.print("[bold cyan]DSPy LaTeX Installation Verification[/bold cyan]")
    console.print()

    all_checks_passed = True

    # Check DSPy
    console.print("[bold]Core Dependencies:[/bold]")
    try:
        import dspy

        dspy_version = getattr(dspy, "__version__", "unknown")
        console.print(f"  [green]✓[/green] DSPy installed (version: {dspy_version})")
    except ImportError:
        console.print("  [red]✗[/red] DSPy not installed")
        console.print("    [dim]Install with: pip install dspy-ai[/dim]")
        all_checks_passed = False

    # Check sklearn (for optimizer)
    try:
        import sklearn  # noqa: F401

        console.print("  [green]✓[/green] scikit-learn installed")
    except ImportError:
        console.print("  [yellow]⚠[/yellow] scikit-learn not installed (optional for ML features)")
        if verbose:
            console.print("    [dim]Install with: pip install scikit-learn[/dim]")

    # Check numpy
    try:
        import numpy  # noqa: F401

        console.print("  [green]✓[/green] numpy installed")
    except ImportError:
        console.print("  [yellow]⚠[/yellow] numpy not installed (required for optimizer)")
        console.print("    [dim]Install with: pip install numpy[/dim]")

    console.print()

    # Check LaTeX backends
    console.print("[bold]LaTeX Backends:[/bold]")

    from specify_cli.core.process import which

    backends = {
        "pdflatex": "Standard LaTeX to PDF compiler",
        "xelatex": "Unicode-capable LaTeX compiler",
        "lualatex": "Lua-based LaTeX compiler",
        "latexmk": "Automated LaTeX compilation",
    }

    for backend, description in backends.items():
        if which(backend):
            console.print(f"  [green]✓[/green] {backend} available")
            if verbose:
                console.print(f"    [dim]{description}[/dim]")
        else:
            console.print(f"  [yellow]⚠[/yellow] {backend} not found")
            if verbose:
                console.print(f"    [dim]{description}[/dim]")

    console.print()

    # Check auxiliary tools
    console.print("[bold]Auxiliary Tools:[/bold]")

    tools = {
        "bibtex": "Bibliography processing",
        "biber": "Modern bibliography processor",
        "makeindex": "Index generation",
        "gs": "Ghostscript (PDF compression)",
    }

    for tool, description in tools.items():
        if which(tool):
            console.print(f"  [green]✓[/green] {tool} available")
            if verbose:
                console.print(f"    [dim]{description}[/dim]")
        else:
            console.print(f"  [yellow]⚠[/yellow] {tool} not found (optional)")
            if verbose:
                console.print(f"    [dim]{description}[/dim]")

    console.print()

    # Check DSPy LaTeX modules
    console.print("[bold]DSPy LaTeX Modules:[/bold]")

    modules = [
        ("specify_cli.dspy_latex.processor", "LaTeX document processor"),
        ("specify_cli.dspy_latex.compiler", "PDF compilation engine"),
        ("specify_cli.dspy_latex.optimizer", "Cognitive optimization layer"),
        ("specify_cli.dspy_latex.observability", "Observability infrastructure"),
    ]

    for module_name, description in modules:
        try:
            __import__(module_name)
            console.print(f"  [green]✓[/green] {module_name}")
            if verbose:
                console.print(f"    [dim]{description}[/dim]")
        except ImportError as e:
            console.print(f"  [red]✗[/red] {module_name} failed to import")
            if verbose:
                console.print(f"    [dim]{e}[/dim]")
            all_checks_passed = False

    console.print()

    # Final status
    if all_checks_passed:
        _display_success_panel(
            "Verification Complete",
            "All core dependencies are installed and working correctly!",
        )
    else:
        _display_error_panel(
            "Verification Issues",
            "Some dependencies are missing. See above for details.",
        )
        raise typer.Exit(1) from None


if __name__ == "__main__":
    app()
