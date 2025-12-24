"""
DSPy LaTeX Optimization Module

Cognitive optimization layer for LaTeX documents using DSPy and machine learning.

This module implements a three-stage cognitive architecture:
- Ψ₁ Perception: Document complexity analysis
- Ψ₂ Reasoning: Optimization strategy selection
- Ψ₃ Generation: Adaptive transformation application

Exhibits autonomic computing properties:
- Self-configuration: Adapts to document type
- Self-optimization: Learns best strategies
- Self-healing: Proposes fixes for common errors
- Self-protection: Validates before applying changes

Examples
--------
    >>> from specify_cli.dspy_latex import LaTeXOptimizer
    >>>
    >>> optimizer = LaTeXOptimizer()
    >>> optimized, metrics = optimizer.optimize(latex_content)
    >>> print(f"Applied {metrics.successful_optimizations} optimizations")

See Also
--------
- optimizer.py : Main optimization engine
- README.md : User guide
- API.md : Complete API reference
"""

from __future__ import annotations

from specify_cli.dspy_latex.optimizer import (
    CompilationRecord,
    CompilationStatus,
    DocumentComplexity,
    DocumentType,
    LaTeXOptimizer,
    OptimizationLevel,
    OptimizationMetrics,
    OptimizationResult,
    OptimizationStrategy,
    PerformancePredictor,
    StrategyLearner,
    StrategyPerformance,
    # Concrete strategies
    BibliographyOptimizationStrategy,
    CrossReferenceValidationStrategy,
    EquationSimplificationStrategy,
    FloatPlacementStrategy,
    GraphicsPathStrategy,
    MacroExpansionStrategy,
    PackageConsolidationStrategy,
)

__all__ = [
    # Main optimizer
    "LaTeXOptimizer",
    # Data classes
    "DocumentComplexity",
    "CompilationRecord",
    "OptimizationResult",
    "StrategyPerformance",
    "OptimizationMetrics",
    # Enums
    "DocumentType",
    "OptimizationLevel",
    "CompilationStatus",
    # ML components
    "PerformancePredictor",
    "StrategyLearner",
    # Base class
    "OptimizationStrategy",
    # Concrete strategies
    "EquationSimplificationStrategy",
    "PackageConsolidationStrategy",
    "MacroExpansionStrategy",
    "BibliographyOptimizationStrategy",
    "FloatPlacementStrategy",
    "GraphicsPathStrategy",
    "CrossReferenceValidationStrategy",
]
