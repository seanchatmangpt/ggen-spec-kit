#!/usr/bin/env python3
"""
DSPy LaTeX Processor - Example Usage
=====================================

This example demonstrates the comprehensive DSPy-based LaTeX processor.

Features Demonstrated:
1. Document parsing and structure extraction
2. Metadata extraction (title, author, date)
3. Package detection and analysis
4. Equation extraction and validation
5. Cross-reference tracking
6. DSPy-powered validation with intelligent error detection
7. DSPy-powered optimization suggestions
8. Performance metrics and statistics

Requirements:
- dspy installed (pip install dspy)
- DSPy configured with an LLM provider
"""

from pathlib import Path
from textwrap import dedent

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from specify_cli.dspy_latex import (
    DSPY_AVAILABLE,
    LaTeXProcessor,
    process_latex_file,
)

console = Console()


# Sample LaTeX document for demonstration
SAMPLE_LATEX = dedent(
    r"""
    \documentclass[12pt,a4paper]{article}

    % Packages
    \usepackage[utf8]{inputenc}
    \usepackage{amsmath}
    \usepackage{amssymb}
    \usepackage{graphicx}
    \usepackage{hyperref}

    % Metadata
    \title{DSPy LaTeX Processor: A Comprehensive Example}
    \author{Claude Code}
    \date{\today}

    \begin{document}

    \maketitle

    \begin{abstract}
    This document demonstrates the capabilities of the DSPy-based LaTeX
    processor for intelligent document analysis, validation, and optimization.
    \end{abstract}

    \section{Introduction}
    \label{sec:intro}

    This is the introduction section. We'll reference the results in
    Section~\ref{sec:results}.

    \section{Mathematical Foundations}
    \label{sec:math}

    Consider the fundamental equation:

    \begin{equation}
    \label{eq:fundamental}
    E = mc^2
    \end{equation}

    The quadratic formula is given by:

    \begin{equation}
    \label{eq:quadratic}
    x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
    \end{equation}

    As shown in Equation~\ref{eq:fundamental}, energy and mass are related.

    \subsection{Matrix Operations}

    Matrix multiplication can be expressed as:

    \begin{align}
    \mathbf{A}\mathbf{B} &= \mathbf{C} \label{eq:matrix1} \\
    c_{ij} &= \sum_{k} a_{ik} b_{kj} \label{eq:matrix2}
    \end{align}

    \section{Results}
    \label{sec:results}

    The results are presented in this section. See Equation~\ref{eq:quadratic}
    for the derivation.

    \subsection{Data Analysis}

    We analyze the data using statistical methods.

    \section{Conclusion}

    In conclusion, we have demonstrated the LaTeX processor capabilities.

    \end{document}
    """
)


def demonstrate_basic_parsing() -> None:
    """Demonstrate basic document parsing."""
    console.print("\n[bold cyan]1. Basic Document Parsing[/bold cyan]\n")

    processor = LaTeXProcessor()
    doc = processor.parse(SAMPLE_LATEX)

    # Display statistics
    table = Table(title="Document Statistics", show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")

    stats = doc.stats()
    for key, value in stats.items():
        table.add_row(key.replace("_", " ").title(), str(value))

    console.print(table)


def demonstrate_metadata_extraction() -> None:
    """Demonstrate metadata extraction."""
    console.print("\n[bold cyan]2. Metadata Extraction[/bold cyan]\n")

    processor = LaTeXProcessor()
    doc = processor.parse(SAMPLE_LATEX)

    metadata_dict = doc.metadata.to_dict()

    table = Table(title="Document Metadata", show_header=True)
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")

    for key, value in metadata_dict.items():
        if value:  # Only show non-empty values
            display_value = str(value) if not isinstance(value, list) else ", ".join(value)
            table.add_row(key.replace("_", " ").title(), display_value)

    console.print(table)


def demonstrate_structure_extraction() -> None:
    """Demonstrate structure extraction."""
    console.print("\n[bold cyan]3. Document Structure[/bold cyan]\n")

    processor = LaTeXProcessor()
    doc = processor.parse(SAMPLE_LATEX)

    console.print("[bold]Sections and Subsections:[/bold]\n")
    for structure in doc.structures:
        indent = "  " * structure.level
        label = f" [dim]({structure.label})[/dim]" if structure.label else ""
        console.print(f"{indent}• {structure.title}{label}")


def demonstrate_equation_extraction() -> None:
    """Demonstrate equation extraction."""
    console.print("\n[bold cyan]4. Mathematical Equations[/bold cyan]\n")

    processor = LaTeXProcessor()
    doc = processor.parse(SAMPLE_LATEX)

    for i, eq in enumerate(doc.equations, 1):
        label_str = f" [dim](label: {eq.label})[/dim]" if eq.label else ""
        numbered = "✓" if eq.numbered else "✗"
        console.print(f"\n[bold]Equation {i}[/bold] [Numbered: {numbered}]{label_str}")
        console.print(f"[dim]Line {eq.line}, Environment: {eq.environment}[/dim]")

        # Display equation content
        syntax = Syntax(eq.content, "latex", theme="monokai")
        console.print(Panel(syntax, border_style="blue"))


def demonstrate_package_analysis() -> None:
    """Demonstrate package analysis."""
    console.print("\n[bold cyan]5. Package Analysis[/bold cyan]\n")

    processor = LaTeXProcessor()
    doc = processor.parse(SAMPLE_LATEX)

    table = Table(title="LaTeX Packages", show_header=True)
    table.add_column("Package", style="cyan")
    table.add_column("Options", style="yellow")
    table.add_column("Purpose", style="white")
    table.add_column("Line", style="dim")

    for pkg in doc.packages:
        options = ", ".join(pkg.options) if pkg.options else "-"
        purpose = pkg.purpose if pkg.purpose else "Unknown"
        table.add_row(pkg.name, options, purpose, str(pkg.line))

    console.print(table)


def demonstrate_cross_references() -> None:
    """Demonstrate cross-reference tracking."""
    console.print("\n[bold cyan]6. Cross-References[/bold cyan]\n")

    processor = LaTeXProcessor()
    doc = processor.parse(SAMPLE_LATEX)

    # Labels
    console.print("[bold]Labels Defined:[/bold]")
    for label, line in sorted(doc.labels.items(), key=lambda x: x[1]):
        console.print(f"  • {label} [dim](line {line})[/dim]")

    # References
    console.print("\n[bold]References Used:[/bold]")
    ref_types = {}
    for ref in doc.cross_references:
        if ref.type not in ref_types:
            ref_types[ref.type] = []
        ref_types[ref.type].append(ref)

    for ref_type, refs in sorted(ref_types.items()):
        console.print(f"\n  [cyan]{ref_type}:[/cyan]")
        for ref in refs:
            resolved = "✓" if ref.target in doc.labels else "✗"
            console.print(f"    • {ref.target} [dim](line {ref.line}, resolved: {resolved})[/dim]")


def demonstrate_validation() -> None:
    """Demonstrate validation (works without DSPy)."""
    console.print("\n[bold cyan]7. Document Validation[/bold cyan]\n")

    processor = LaTeXProcessor()
    doc = processor.parse(SAMPLE_LATEX)

    # Run validation
    validation = processor.validate(doc, use_dspy=DSPY_AVAILABLE)

    # Display results
    if validation.is_valid:
        console.print(Panel(
            "[green]✓ Document is valid![/green]\n\n"
            f"Warnings: {validation.warning_count}\n"
            f"Processing time: {validation.processing_time:.3f}s",
            title="Validation Result",
            border_style="green",
        ))
    else:
        console.print(Panel(
            f"[red]✗ Document has errors[/red]\n\n"
            f"Errors: {validation.error_count}\n"
            f"Warnings: {validation.warning_count}\n"
            f"Processing time: {validation.processing_time:.3f}s",
            title="Validation Result",
            border_style="red",
        ))

    # Show errors
    if validation.errors:
        console.print("\n[bold red]Errors:[/bold red]")
        for error in validation.errors:
            console.print(f"  • {error}")
            if error.suggestion:
                console.print(f"    [dim]→ {error.suggestion}[/dim]")

    # Show warnings
    if validation.warnings:
        console.print("\n[bold yellow]Warnings:[/bold yellow]")
        for warning in validation.warnings:
            console.print(f"  • {warning}")
            if warning.suggestion:
                console.print(f"    [dim]→ {warning.suggestion}[/dim]")


def demonstrate_optimization() -> None:
    """Demonstrate optimization (requires DSPy)."""
    console.print("\n[bold cyan]8. Document Optimization[/bold cyan]\n")

    if not DSPY_AVAILABLE:
        console.print("[yellow]DSPy not available. Optimization requires DSPy.[/yellow]")
        console.print("[dim]Install with: pip install dspy[/dim]")
        return

    processor = LaTeXProcessor()
    doc = processor.parse(SAMPLE_LATEX)

    console.print("[dim]Running optimization (this may take a moment)...[/dim]\n")

    # Run optimization
    optimization = processor.optimize(doc, focus="performance")

    if optimization.suggestions:
        console.print("[bold]Optimization Suggestions:[/bold]")
        for i, suggestion in enumerate(optimization.suggestions, 1):
            console.print(f"{i}. {suggestion}")

    if optimization.reasoning:
        console.print(f"\n[bold]Reasoning:[/bold]\n{optimization.reasoning}")

    if optimization.performance_impact:
        console.print(f"\n[bold]Performance Impact:[/bold]\n{optimization.performance_impact}")


def demonstrate_equation_analysis() -> None:
    """Demonstrate equation analysis (requires DSPy)."""
    console.print("\n[bold cyan]9. Equation Analysis[/bold cyan]\n")

    if not DSPY_AVAILABLE:
        console.print("[yellow]DSPy not available. Equation analysis requires DSPy.[/yellow]")
        return

    processor = LaTeXProcessor()
    doc = processor.parse(SAMPLE_LATEX)

    console.print("[dim]Analyzing equations (this may take a moment)...[/dim]\n")

    # Analyze equations
    analysis = processor.analyze_equations(doc)

    console.print(f"[bold]Total Equations:[/bold] {analysis.get('total', 0)}")
    console.print(f"[bold]Numbered:[/bold] {analysis.get('numbered', 0)}\n")

    if "issues" in analysis and analysis["issues"]:
        console.print("[bold yellow]Issues Found:[/bold yellow]")
        for issue in analysis["issues"]:
            console.print(f"  • {issue}")

    if "suggestions" in analysis and analysis["suggestions"]:
        console.print("\n[bold]Suggestions:[/bold]")
        for suggestion in analysis["suggestions"]:
            console.print(f"  • {suggestion}")

    if "best_practices" in analysis and analysis["best_practices"]:
        console.print("\n[bold cyan]Best Practices:[/bold cyan]")
        for practice in analysis["best_practices"]:
            console.print(f"  • {practice}")


def demonstrate_convenience_function() -> None:
    """Demonstrate the convenience function."""
    console.print("\n[bold cyan]10. Convenience Function Usage[/bold cyan]\n")

    # Create a temporary LaTeX file
    temp_file = Path("/tmp/example.tex")
    temp_file.write_text(SAMPLE_LATEX)

    console.print(f"[dim]Processing file: {temp_file}[/dim]\n")

    # Process using convenience function
    doc, validation, optimization = process_latex_file(
        temp_file,
        validate=True,
        optimize=DSPY_AVAILABLE,
    )

    console.print(f"[bold]Document:[/bold] {doc.metadata.title}")
    console.print(f"[bold]Chapters:[/bold] {len(doc.chapters)}")
    console.print(f"[bold]Sections:[/bold] {len(doc.sections)}")
    console.print(f"[bold]Equations:[/bold] {len(doc.equations)}")

    if validation:
        console.print(f"[bold]Validation:[/bold] {validation}")

    if optimization:
        console.print(f"[bold]Optimization Suggestions:[/bold] {len(optimization.suggestions)}")

    # Cleanup
    temp_file.unlink()


def main() -> None:
    """Run all demonstrations."""
    console.print(Panel(
        "[bold cyan]DSPy LaTeX Processor - Comprehensive Example[/bold cyan]\n\n"
        "This example demonstrates all capabilities of the DSPy-based LaTeX processor.\n"
        f"DSPy Available: {'✓ Yes' if DSPY_AVAILABLE else '✗ No (some features limited)'}",
        border_style="cyan",
    ))

    try:
        demonstrate_basic_parsing()
        demonstrate_metadata_extraction()
        demonstrate_structure_extraction()
        demonstrate_equation_extraction()
        demonstrate_package_analysis()
        demonstrate_cross_references()
        demonstrate_validation()

        if DSPY_AVAILABLE:
            demonstrate_optimization()
            demonstrate_equation_analysis()
        else:
            console.print("\n[yellow]Note: Install DSPy for optimization and advanced analysis features[/yellow]")
            console.print("[dim]pip install dspy[/dim]\n")

        demonstrate_convenience_function()

        console.print("\n[green]✓ All demonstrations completed successfully![/green]\n")

    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback

        console.print(f"[dim]{traceback.format_exc()}[/dim]")


if __name__ == "__main__":
    main()
