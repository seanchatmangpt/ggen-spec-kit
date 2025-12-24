#!/usr/bin/env python
"""
DSPy LaTeX Optimization Example

Demonstrates the cognitive optimization layer for LaTeX documents with:
- Ψ₁ Perception: Document complexity analysis
- Ψ₂ Reasoning: Strategy selection with ML
- Ψ₃ Generation: Adaptive transformations
- Autonomic computing properties
- Machine learning from compilation history

Run with:
    python examples/dspy_latex_optimization_example.py
"""

from pathlib import Path

from specify_cli.dspy_latex import (
    CompilationRecord,
    CompilationStatus,
    DocumentType,
    LaTeXOptimizer,
    OptimizationLevel,
)


def example_1_basic_optimization():
    """Example 1: Basic document optimization."""
    print("=" * 80)
    print("EXAMPLE 1: Basic LaTeX Document Optimization")
    print("=" * 80)

    # Sample LaTeX document with common issues
    latex_doc = r"""
\documentclass{article}
\usepackage{amsmath}
\usepackage{amsmath}  % Duplicate package
\usepackage{graphicx}
\usepackage{epsfig}   % Obsolete package
\usepackage{subfigure}  % Obsolete package

\begin{document}

\section{Introduction}

This is a sample document with some equations:

\[ E = mc^2 \]

\begin{equation}
    x = \frac  {-b   \pm   \sqrt{b^2 - 4ac}}  {2a}
\end{equation}

\begin{figure}[h]  % Restrictive placement
    \includegraphics{figures/plot.pdf}
    \caption{A sample plot}
\end{figure}

\end{document}
"""

    print("\n1. Creating optimizer...")
    optimizer = LaTeXOptimizer(
        optimization_level=OptimizationLevel.MODERATE,
        enable_ml=False,  # Disable ML for this simple example
    )

    print("\n2. Analyzing document complexity (Ψ₁ Perception)...")
    complexity = optimizer.analyze_complexity(latex_doc)
    print(f"   Document Type: {complexity.document_type.value}")
    print(f"   Complexity Score: {complexity.complexity_score:.1f}")
    print(f"   Equations: {complexity.equation_count}")
    print(f"   Figures: {complexity.figure_count}")
    print(f"   Packages: {complexity.package_count}")
    print(f"   Redundant Packages: {complexity.redundant_packages}")

    print("\n3. Selecting strategies (Ψ₂ Reasoning)...")
    strategies = optimizer.select_strategies(complexity)
    print(f"   Selected Strategies: {', '.join(strategies)}")

    print("\n4. Running optimization pipeline (Ψ₃ Generation)...")
    optimized_content, metrics = optimizer.optimize(latex_doc, max_iterations=5)

    print(f"\n5. Results:")
    print(f"   Total Optimizations: {metrics.total_optimizations}")
    print(f"   Successful: {metrics.successful_optimizations}")
    print(f"   Failed: {metrics.failed_optimizations}")
    print(f"   Strategies Used: {dict(metrics.strategies_used)}")

    print("\n6. Optimized Document (first 500 chars):")
    print("-" * 80)
    print(optimized_content[:500])
    print("-" * 80)


def example_2_strategy_by_strategy():
    """Example 2: Apply strategies one by one to see their effects."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Strategy-by-Strategy Optimization")
    print("=" * 80)

    latex_doc = r"""
\documentclass{article}
\usepackage{amsmath}
\usepackage{amsmath}
\usepackage{epsfig}

\begin{document}
\[ E = mc^2 \]
\begin{figure}[h]
\includegraphics{plot.pdf}
\end{figure}
\end{document}
"""

    optimizer = LaTeXOptimizer(optimization_level=OptimizationLevel.MODERATE, enable_ml=False)
    complexity = optimizer.analyze_complexity(latex_doc)

    print("\n1. Package Consolidation Strategy:")
    from specify_cli.dspy_latex import PackageConsolidationStrategy

    strategy = PackageConsolidationStrategy()
    analysis = strategy.analyze(latex_doc)
    print(f"   Analysis: {analysis}")

    result = optimizer.apply_optimization(latex_doc, "package_consolidation", complexity)
    print(f"   Success: {result.success}")
    print(f"   Validation Passed: {result.validation_passed}")
    print(f"   Confidence: {result.confidence:.1%}")
    print(f"   Changes: {result.changes_made[:2]}")  # Show first 2 changes

    print("\n2. Float Placement Strategy:")
    from specify_cli.dspy_latex import FloatPlacementStrategy

    strategy = FloatPlacementStrategy()
    analysis = strategy.analyze(latex_doc)
    print(f"   Analysis: {analysis}")

    result = optimizer.apply_optimization(latex_doc, "float_placement", complexity)
    print(f"   Success: {result.success}")
    print(f"   Changes Made: {len(result.changes_made)}")


def example_3_ml_learning():
    """Example 3: Machine learning from compilation history."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Machine Learning from Compilation History")
    print("=" * 80)

    from datetime import datetime
    import hashlib

    print("\n1. Creating optimizer with ML enabled...")
    optimizer = LaTeXOptimizer(optimization_level=OptimizationLevel.MODERATE, enable_ml=True)

    print("\n2. Simulating compilation history...")
    # Simulate successful compilations with different strategies
    simulated_history = [
        (DocumentType.ARTICLE, "equation_simplification", True, 1.2),
        (DocumentType.ARTICLE, "equation_simplification", True, 1.1),
        (DocumentType.ARTICLE, "package_consolidation", True, 0.9),
        (DocumentType.ARTICLE, "package_consolidation", False, 2.5),  # Failed
        (DocumentType.BOOK, "package_consolidation", True, 2.0),
        (DocumentType.THESIS, "macro_expansion", True, 3.5),
        (DocumentType.THESIS, "bibliography_optimization", True, 2.8),
    ]

    for doc_type, strategy, success, compile_time in simulated_history:
        record = CompilationRecord(
            timestamp=datetime.now(),
            document_hash=hashlib.sha256(f"{doc_type}-{strategy}".encode()).hexdigest(),
            status=CompilationStatus.SUCCESS if success else CompilationStatus.ERROR,
            compile_time=compile_time,
            optimization_applied=strategy,
        )
        if optimizer.learner:
            optimizer.learner.record_compilation(record)

    print(f"   Recorded {len(simulated_history)} compilation attempts")

    print("\n3. Strategy rankings for different document types:")

    for doc_type in [DocumentType.ARTICLE, DocumentType.BOOK, DocumentType.THESIS]:
        if optimizer.learner:
            rankings = optimizer.learner.get_strategy_ranking(
                doc_type, OptimizationLevel.MODERATE
            )
            print(f"\n   {doc_type.value.upper()}:")
            for strategy_name, score in rankings[:3]:  # Top 3
                print(f"     - {strategy_name}: {score:.3f}")

    print("\n4. Strategy performance statistics:")
    if optimizer.learner:
        for strategy_name, perf in list(optimizer.learner.strategy_performance.items())[:5]:
            total = perf.success_count + perf.failure_count
            print(f"\n   {strategy_name}:")
            print(f"     Success Rate: {perf.success_rate:.1%} ({perf.success_count}/{total})")
            print(f"     Avg Compile Time: {perf.avg_compile_time:.2f}s")


def example_4_autonomic_properties():
    """Example 4: Demonstrate autonomic computing properties."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Autonomic Computing Properties")
    print("=" * 80)

    optimizer = LaTeXOptimizer(optimization_level=OptimizationLevel.AGGRESSIVE, enable_ml=True)

    print("\n1. SELF-CONFIGURATION (adapts to document type):")

    test_docs = {
        "article": r"\documentclass{article}\begin{document}Paper\end{document}",
        "book": r"\documentclass{book}\begin{document}\chapter{One}Book\end{document}",
        "thesis": r"\documentclass{report}\begin{document}\chapter{Intro}Thesis text\end{document}",
        "beamer": r"\documentclass{beamer}\begin{document}\frame{Slides}\end{document}",
    }

    for name, doc in test_docs.items():
        complexity = optimizer.analyze_complexity(doc)
        print(f"   {name:15} → detected as: {complexity.document_type.value}")

    print("\n2. SELF-OPTIMIZATION (learns from history):")
    print("   ✓ Tracks strategy success rates over time")
    print("   ✓ Adjusts strategy rankings based on performance")
    print("   ✓ Favors strategies that worked recently")
    print("   ✓ Predicts success probability using ML")

    print("\n3. SELF-HEALING (proposes fixes):")

    broken_doc = r"""
\documentclass{article}
\usepackage{epsfig}  % Obsolete
\usepackage{subfigure}  % Obsolete
\begin{document}
\begin{figure}[h]  % Too restrictive
\end{document}
"""

    complexity = optimizer.analyze_complexity(broken_doc)
    strategies = optimizer.select_strategies(complexity)
    print(f"   Detected issues:")
    print(f"   - Obsolete packages: {len(complexity.packages)}")
    print(f"   - Proposed fixes: {', '.join(strategies[:3])}")

    print("\n4. SELF-PROTECTION (validates changes):")

    test_doc = r"\documentclass{article}\begin{document}Test\end{document}"
    valid_doc = r"\documentclass{article}\begin{document}Test\end{document}"
    invalid_doc = r"\documentclass{article}Test\end{document}"  # Missing \begin

    result1 = optimizer._validate_optimization(test_doc, valid_doc)
    result2 = optimizer._validate_optimization(test_doc, invalid_doc)

    print(f"   Valid optimization: {result1} ✓")
    print(f"   Invalid optimization (missing \\begin): {result2} ✗")
    print("   → Changes automatically rejected if validation fails")


def example_5_document_types():
    """Example 5: Different document type handling."""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Document Type-Specific Optimization")
    print("=" * 80)

    optimizer = LaTeXOptimizer(optimization_level=OptimizationLevel.MODERATE, enable_ml=False)

    # Article - research paper
    article = r"""
\documentclass{article}
\usepackage{amsmath}
\usepackage{amsmath}
\begin{document}
\section{Introduction}
\[ E = mc^2 \]
\end{document}
"""

    # Thesis - long document
    thesis = r"""
\documentclass[12pt]{report}
\usepackage{graphicx}
\usepackage{epsfig}
\begin{document}
\chapter{Introduction}
\section{Background}
\begin{figure}[h]
\includegraphics{fig.pdf}
\end{figure}
\end{document}
"""

    # Presentation
    presentation = r"""
\documentclass{beamer}
\usepackage{graphicx}
\begin{document}
\frame{
    \frametitle{Title}
    Content
}
\end{document}
"""

    for name, doc in [("Article", article), ("Thesis", thesis), ("Presentation", presentation)]:
        print(f"\n{name}:")
        complexity = optimizer.analyze_complexity(doc)
        strategies = optimizer.select_strategies(complexity)

        print(f"  Type: {complexity.document_type.value}")
        print(f"  Complexity: {complexity.complexity_score:.1f}")
        print(f"  Top 3 strategies: {', '.join(strategies[:3])}")


def example_6_optimization_levels():
    """Example 6: Different optimization levels."""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Optimization Levels")
    print("=" * 80)

    latex_doc = r"""
\documentclass{article}
\usepackage{amsmath}
\usepackage{amsmath}
\usepackage{epsfig}
\newcommand{\myref}[1]{\cite{#1}}
\begin{document}
Test \[ E = mc^2 \]
\end{document}
"""

    levels = [
        OptimizationLevel.CONSERVATIVE,
        OptimizationLevel.MODERATE,
        OptimizationLevel.AGGRESSIVE,
    ]

    for level in levels:
        print(f"\n{level.value.upper()}:")
        optimizer = LaTeXOptimizer(optimization_level=level, enable_ml=False)

        complexity = optimizer.analyze_complexity(latex_doc)
        strategies = optimizer.select_strategies(complexity)

        print(f"  Strategies selected: {len(strategies)}")
        print(f"  Strategy names: {', '.join(strategies[:5])}")

        optimized, metrics = optimizer.optimize(latex_doc, max_iterations=3)
        print(f"  Optimizations applied: {metrics.successful_optimizations}")


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("DSPy LaTeX Cognitive Optimizer - Comprehensive Examples")
    print("=" * 80)
    print()
    print("This demonstrates a cognitive optimization layer that:")
    print("  Ψ₁ Perception:  Analyzes document complexity")
    print("  Ψ₂ Reasoning:   Selects optimal strategies")
    print("  Ψ₃ Generation:  Applies adaptive transformations")
    print()
    print("With autonomic properties:")
    print("  • Self-configuration: Adapts to document type")
    print("  • Self-optimization: Learns from compilation history")
    print("  • Self-healing: Proposes fixes for errors")
    print("  • Self-protection: Validates changes before applying")
    print()

    # Run all examples
    example_1_basic_optimization()
    example_2_strategy_by_strategy()
    example_3_ml_learning()
    example_4_autonomic_properties()
    example_5_document_types()
    example_6_optimization_levels()

    print("\n" + "=" * 80)
    print("✓ ALL EXAMPLES COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  1. Try optimizing your own LaTeX documents")
    print("  2. Enable ML learning to improve over time")
    print("  3. Create custom optimization strategies")
    print("  4. Integrate with your compilation pipeline")
    print()


if __name__ == "__main__":
    main()
