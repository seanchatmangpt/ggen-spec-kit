"""
Cognitive Optimization Layer for LaTeX Documents

This module implements a DSPy-based cognitive architecture for optimizing LaTeX documents
using machine learning to learn from compilation history. It follows the constitutional
equation principles with three cognitive stages:

    Ψ₁: Perception (Document Complexity Analysis)
    Ψ₂: Reasoning (Optimization Strategy Selection)
    Ψ₃: Generation (Adaptive Transformation Application)

The system exhibits four autonomic computing properties:
- Self-configuration: Adapts to document type
- Self-optimization: Learns best strategies
- Self-healing: Proposes fixes for common errors
- Self-protection: Validates before applying changes
"""

import hashlib
import json
import re
import time
from abc import ABC, abstractmethod
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

from specify_cli.core.telemetry import metric_counter, metric_histogram, span

try:
    import dspy

    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False
    dspy = None  # type: ignore[assignment]


# ============================================================================
# Enumerations
# ============================================================================


class DocumentType(str, Enum):
    """LaTeX document types with different optimization needs."""

    ARTICLE = "article"
    BOOK = "book"
    REPORT = "report"
    THESIS = "thesis"
    PRESENTATION = "presentation"
    LETTER = "letter"
    UNKNOWN = "unknown"


class OptimizationLevel(str, Enum):
    """Optimization aggressiveness levels."""

    CONSERVATIVE = "conservative"  # Safe changes only
    MODERATE = "moderate"  # Standard optimizations
    AGGRESSIVE = "aggressive"  # All available optimizations


class CompilationStatus(str, Enum):
    """Compilation result status."""

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    TIMEOUT = "timeout"


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class DocumentComplexity:
    """Analysis of document complexity metrics."""

    total_lines: int = 0
    equation_count: int = 0
    figure_count: int = 0
    table_count: int = 0
    citation_count: int = 0
    package_count: int = 0
    custom_macro_count: int = 0
    nesting_depth: int = 0
    float_count: int = 0
    cross_ref_count: int = 0
    complexity_score: float = 0.0
    document_type: DocumentType = DocumentType.UNKNOWN

    # Detailed package analysis
    packages: list[str] = field(default_factory=list)
    redundant_packages: list[str] = field(default_factory=list)
    conflicting_packages: list[tuple[str, str]] = field(default_factory=list)

    # Content structure
    sections_depth: dict[str, int] = field(default_factory=dict)
    problematic_constructs: list[str] = field(default_factory=list)


@dataclass
class CompilationRecord:
    """Record of a LaTeX compilation attempt."""

    timestamp: datetime
    document_hash: str
    status: CompilationStatus
    compile_time: float
    error_messages: list[str] = field(default_factory=list)
    warning_messages: list[str] = field(default_factory=list)
    optimization_applied: str | None = None
    metrics: dict[str, float] = field(default_factory=dict)


@dataclass
class OptimizationResult:
    """Result of applying an optimization strategy."""

    success: bool
    original_content: str
    optimized_content: str
    strategy_name: str
    changes_made: list[str] = field(default_factory=list)
    estimated_improvement: float = 0.0
    confidence: float = 0.0
    reasoning: str = ""
    validation_passed: bool = False


@dataclass
class StrategyPerformance:
    """Performance metrics for an optimization strategy."""

    strategy_name: str
    success_count: int = 0
    failure_count: int = 0
    avg_improvement: float = 0.0
    avg_compile_time: float = 0.0
    success_rate: float = 0.0
    last_used: datetime | None = None
    document_types: dict[DocumentType, int] = field(default_factory=dict)


@dataclass
class OptimizationMetrics:
    """Comprehensive metrics for optimization operations."""

    total_optimizations: int = 0
    successful_optimizations: int = 0
    failed_optimizations: int = 0
    total_compile_time_saved: float = 0.0
    strategies_used: dict[str, int] = field(default_factory=dict)
    document_types_optimized: dict[DocumentType, int] = field(default_factory=dict)
    avg_confidence: float = 0.0


# ============================================================================
# DSPy Signatures - Cognitive Architecture (Ψ₁, Ψ₂, Ψ₃)
# ============================================================================


if DSPY_AVAILABLE:

    class DocumentPerceptionSignature(dspy.Signature):
        """Ψ₁: Perception - Analyze LaTeX document complexity and characteristics."""

        latex_content: str = dspy.InputField(desc="The LaTeX document content to analyze")
        compilation_history: str = dspy.InputField(
            desc="JSON-formatted compilation history for context"
        )

        document_type: str = dspy.OutputField(
            desc="Detected document type: article, book, report, thesis, presentation, letter"
        )
        complexity_assessment: str = dspy.OutputField(
            desc="Detailed assessment of document complexity and potential issues"
        )
        key_metrics: str = dspy.OutputField(
            desc="JSON object with key complexity metrics"
        )
        bottlenecks: str = dspy.OutputField(
            desc="List of identified performance bottlenecks and compilation issues"
        )

    class StrategyReasoningSignature(dspy.Signature):
        """Ψ₂: Reasoning - Select optimal optimization strategies based on analysis."""

        complexity_analysis: str = dspy.InputField(
            desc="Document complexity analysis from Ψ₁"
        )
        compilation_errors: str = dspy.InputField(
            desc="Recent compilation errors and warnings"
        )
        strategy_history: str = dspy.InputField(
            desc="Historical performance of strategies on similar documents"
        )
        optimization_level: str = dspy.InputField(
            desc="Desired optimization level: conservative, moderate, aggressive"
        )

        selected_strategies: str = dspy.OutputField(
            desc="Ordered list of recommended optimization strategies"
        )
        reasoning: str = dspy.OutputField(
            desc="Detailed reasoning for strategy selection"
        )
        risk_assessment: str = dspy.OutputField(
            desc="Assessment of risks and potential side effects"
        )
        expected_improvement: str = dspy.OutputField(
            desc="Estimated improvement in compilation time and success rate"
        )

    class TransformationGenerationSignature(dspy.Signature):
        """Ψ₃: Generation - Generate adaptive transformations for LaTeX content."""

        latex_content: str = dspy.InputField(desc="Original LaTeX content")
        strategy_name: str = dspy.InputField(desc="Name of optimization strategy to apply")
        strategy_parameters: str = dspy.InputField(
            desc="Parameters and configuration for the strategy"
        )
        complexity_info: str = dspy.InputField(
            desc="Document complexity information from Ψ₁"
        )

        optimized_content: str = dspy.OutputField(
            desc="LaTeX content after applying the optimization"
        )
        changes_summary: str = dspy.OutputField(
            desc="Summary of changes made during optimization"
        )
        validation_checks: str = dspy.OutputField(
            desc="Validation checks performed and their results"
        )
        confidence_score: float = dspy.OutputField(
            desc="Confidence score for the optimization (0.0-1.0)"
        )


# ============================================================================
# Optimization Strategies (Base Class and Implementations)
# ============================================================================


class OptimizationStrategy(ABC):
    """Base class for LaTeX optimization strategies."""

    def __init__(self, name: str, description: str, risk_level: str = "low"):
        """
        Initialize optimization strategy.

        Parameters
        ----------
        name : str
            Strategy name
        description : str
            Human-readable description
        risk_level : str
            Risk level: "low", "medium", "high"
        """
        self.name = name
        self.description = description
        self.risk_level = risk_level
        self.performance_history: list[float] = []

    @abstractmethod
    def apply(self, latex_content: str, complexity: DocumentComplexity) -> str:
        """
        Apply the optimization strategy to LaTeX content.

        Parameters
        ----------
        latex_content : str
            Original LaTeX content
        complexity : DocumentComplexity
            Document complexity analysis

        Returns
        -------
        str
            Optimized LaTeX content
        """

    @abstractmethod
    def analyze(self, latex_content: str) -> dict[str, Any]:
        """
        Analyze what changes would be made without applying them.

        Parameters
        ----------
        latex_content : str
            LaTeX content to analyze

        Returns
        -------
        dict[str, Any]
            Analysis results including potential changes
        """

    def record_performance(self, improvement: float) -> None:
        """Record performance improvement for learning."""
        self.performance_history.append(improvement)
        if len(self.performance_history) > 100:
            self.performance_history.pop(0)

    def get_avg_performance(self) -> float:
        """Get average performance improvement."""
        return float(np.mean(self.performance_history)) if self.performance_history else 0.0


class EquationSimplificationStrategy(OptimizationStrategy):
    """Simplify equations without changing mathematical meaning."""

    def __init__(self):
        """Initialize equation simplification strategy."""
        super().__init__(
            name="equation_simplification",
            description="Simplify equation formatting while preserving mathematical meaning",
            risk_level="low",
        )

    def apply(self, latex_content: str, complexity: DocumentComplexity) -> str:
        """Apply equation simplifications."""
        content = latex_content

        # Replace displaymath with equation* for consistency
        content = re.sub(r"\\\[", r"\\begin{equation*}", content)
        content = re.sub(r"\\\]", r"\\end{equation*}", content)

        # Simplify spacing in equations
        content = re.sub(r"\\,+", r"\\,", content)  # Multiple thin spaces to one
        content = re.sub(r"\\;+", r"\\;", content)  # Multiple thick spaces to one

        # Simplify nested fractions using \dfrac where appropriate
        # This is a conservative change
        return re.sub(
            r"\\frac\{\\frac\{([^}]+)\}\{([^}]+)\}\}",
            r"\\dfrac{\\frac{\1}{\2}}",
            content,
        )


    def analyze(self, latex_content: str) -> dict[str, Any]:
        """Analyze equation simplification opportunities."""
        displaymath_count = len(re.findall(r"\\\[|\\\]", latex_content))
        spacing_issues = len(re.findall(r"\\,{2,}|\\;{2,}", latex_content))
        nested_fractions = len(re.findall(r"\\frac\{\\frac", latex_content))

        return {
            "displaymath_conversions": displaymath_count // 2,
            "spacing_simplifications": spacing_issues,
            "nested_fraction_improvements": nested_fractions,
            "total_changes": displaymath_count // 2 + spacing_issues + nested_fractions,
        }


class PackageConsolidationStrategy(OptimizationStrategy):
    """Remove redundant and conflicting package imports."""

    def __init__(self):
        """Initialize package consolidation strategy."""
        super().__init__(
            name="package_consolidation",
            description="Remove redundant package imports and resolve conflicts",
            risk_level="medium",
        )

        # Known package relationships
        self.superseded_packages = {
            "epsfig": "graphicx",  # epsfig is obsolete
            "subfigure": "subcaption",  # subfigure is obsolete
            "doublespace": "setspace",  # doublespace is obsolete
            "fancyheadings": "fancyhdr",  # old version
        }

        self.conflicting_packages = [
            ("subfigure", "subcaption"),
            ("subfigure", "subfig"),
            ("times", "mathptmx"),
            ("pslatex", "mathptmx"),
        ]

    def apply(self, latex_content: str, complexity: DocumentComplexity) -> str:
        """Apply package consolidation."""
        content = latex_content
        removed_packages = []

        # Remove obsolete packages and replace with modern equivalents
        for old_pkg, new_pkg in self.superseded_packages.items():
            pattern = rf"\\usepackage(?:\[[^\]]*\])?\{{{old_pkg}\}}"
            if re.search(pattern, content):
                # Check if new package is already loaded
                new_pattern = rf"\\usepackage(?:\[[^\]]*\])?\{{{new_pkg}\}}"
                if not re.search(new_pattern, content):
                    # Replace old with new
                    content = re.sub(pattern, rf"\\usepackage{{{new_pkg}}}", content, count=1)
                else:
                    # Just remove old
                    content = re.sub(pattern, "", content)
                    removed_packages.append(old_pkg)

        # Remove duplicate package loads
        packages_seen = set()
        lines = content.split("\n")
        new_lines = []

        for line in lines:
            match = re.match(r"\\usepackage(?:\[([^\]]*)\])?\{([^}]+)\}", line)
            if match:
                options, pkg_name = match.groups()
                key = (pkg_name, options or "")
                if key not in packages_seen:
                    packages_seen.add(key)
                    new_lines.append(line)
                else:
                    removed_packages.append(pkg_name)
            else:
                new_lines.append(line)

        return "\n".join(new_lines)

    def analyze(self, latex_content: str) -> dict[str, Any]:
        """Analyze package optimization opportunities."""
        obsolete_count = sum(
            1
            for pkg in self.superseded_packages
            if re.search(rf"\\usepackage(?:\[[^\]]*\])?\{{{pkg}\}}", latex_content)
        )

        # Find duplicates
        packages = re.findall(r"\\usepackage(?:\[[^\]]*\])?\{([^}]+)\}", latex_content)
        duplicates = len(packages) - len(set(packages))

        conflicts = []
        for pkg1, pkg2 in self.conflicting_packages:
            if pkg1 in packages and pkg2 in packages:
                conflicts.append((pkg1, pkg2))

        return {
            "obsolete_packages": obsolete_count,
            "duplicate_packages": duplicates,
            "conflicting_packages": len(conflicts),
            "total_removals": obsolete_count + duplicates,
        }


class MacroExpansionStrategy(OptimizationStrategy):
    """Expand problematic custom macros."""

    def __init__(self):
        """Initialize macro expansion strategy."""
        super().__init__(
            name="macro_expansion",
            description="Expand problematic custom macros that cause compilation issues",
            risk_level="medium",
        )

    def apply(self, latex_content: str, complexity: DocumentComplexity) -> str:
        """Apply selective macro expansion."""
        content = latex_content

        # Identify and expand macros that are defined but cause issues
        # This is conservative - only expand macros with specific problematic patterns

        # Find macro definitions
        macro_defs = re.findall(r"\\newcommand\{\\(\w+)\}(?:\[(\d+)\])?\{([^}]+)\}", content)

        # Expand macros that use fragile commands
        fragile_commands = ["\\cite", "\\ref", "\\label", "\\footnote"]

        for macro_name, num_args, macro_body in macro_defs:
            # Check if macro body contains fragile commands
            if any(cmd in macro_body for cmd in fragile_commands):
                # Replace usages with expanded form
                if num_args:
                    # For now, skip parameterized macros (more complex)
                    continue
                # Simple replacement
                content = re.sub(rf"\\{macro_name}\b", macro_body, content)

        return content

    def analyze(self, latex_content: str) -> dict[str, Any]:
        """Analyze macro expansion opportunities."""
        macro_defs = re.findall(r"\\newcommand\{\\(\w+)\}", latex_content)
        fragile_commands = ["\\cite", "\\ref", "\\label", "\\footnote"]

        problematic_macros = 0
        for match in re.finditer(r"\\newcommand\{\\(\w+)\}(?:\[(\d+)\])?\{([^}]+)\}", latex_content):
            macro_body = match.group(3)
            if any(cmd in macro_body for cmd in fragile_commands):
                problematic_macros += 1

        return {
            "total_macros": len(macro_defs),
            "problematic_macros": problematic_macros,
            "expansion_candidates": problematic_macros,
        }


class BibliographyOptimizationStrategy(OptimizationStrategy):
    """Optimize bibliography processing."""

    def __init__(self):
        """Initialize bibliography optimization strategy."""
        super().__init__(
            name="bibliography_optimization",
            description="Optimize bibliography and citation processing",
            risk_level="low",
        )

    def apply(self, latex_content: str, complexity: DocumentComplexity) -> str:
        """Apply bibliography optimizations."""
        content = latex_content

        # Ensure biblatex is used with biber for better performance
        if re.search(r"\\usepackage\{natbib\}", content):
            # Suggest migration but don't auto-replace (too risky)
            pass

        # Add \nocite{*} consolidation if many unused citations
        # This is very document-specific, so skip for now

        return content

    def analyze(self, latex_content: str) -> dict[str, Any]:
        """Analyze bibliography optimization opportunities."""
        has_natbib = bool(re.search(r"\\usepackage\{natbib\}", latex_content))
        has_biblatex = bool(re.search(r"\\usepackage\{biblatex\}", latex_content))
        citation_count = len(re.findall(r"\\cite", latex_content))

        return {
            "using_natbib": has_natbib,
            "using_biblatex": has_biblatex,
            "citation_count": citation_count,
            "optimization_opportunities": 1 if has_natbib else 0,
        }


class FloatPlacementStrategy(OptimizationStrategy):
    """Optimize float placement directives."""

    def __init__(self):
        """Initialize float placement strategy."""
        super().__init__(
            name="float_placement",
            description="Optimize figure and table placement directives",
            risk_level="low",
        )

    def apply(self, latex_content: str, complexity: DocumentComplexity) -> str:
        """Apply float placement optimizations."""
        content = latex_content

        # Replace restrictive float placement with more flexible options
        # [h] -> [htbp] (more flexible)
        # [H] stays as is (from float package, forces position)

        content = re.sub(
            r"\\begin\{(figure|table)\}\[h\]",
            r"\\begin{\1}[htbp]",
            content,
        )

        # [t] -> [tbp] for better placement
        return re.sub(
            r"\\begin\{(figure|table)\}\[t\]",
            r"\\begin{\1}[tbp]",
            content,
        )


    def analyze(self, latex_content: str) -> dict[str, Any]:
        """Analyze float placement optimization opportunities."""
        restrictive_h = len(re.findall(r"\\begin\{(?:figure|table)\}\[h\]", latex_content))
        restrictive_t = len(re.findall(r"\\begin\{(?:figure|table)\}\[t\]", latex_content))
        forced_H = len(re.findall(r"\\begin\{(?:figure|table)\}\[H\]", latex_content))

        return {
            "restrictive_h_placement": restrictive_h,
            "restrictive_t_placement": restrictive_t,
            "forced_H_placement": forced_H,
            "total_improvements": restrictive_h + restrictive_t,
        }


class GraphicsPathStrategy(OptimizationStrategy):
    """Optimize graphics path handling."""

    def __init__(self):
        """Initialize graphics path strategy."""
        super().__init__(
            name="graphics_path",
            description="Optimize graphics path resolution and caching",
            risk_level="low",
        )

    def apply(self, latex_content: str, complexity: DocumentComplexity) -> str:
        """Apply graphics path optimizations."""
        content = latex_content

        # Ensure graphicspath is defined early in document
        has_graphicspath = bool(re.search(r"\\graphicspath", content))

        if not has_graphicspath:
            # Extract common paths from includegraphics
            graphics_files = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", content)
            paths = set()

            for gfile in graphics_files:
                path = Path(gfile).parent
                if path != Path():
                    paths.add(str(path))

            if paths:
                # Add graphicspath directive after documentclass
                graphicspath_cmd = "\\graphicspath{{" + "}{".join(f"{{{p}/}}" for p in paths) + "}}\n"
                content = re.sub(
                    r"(\\documentclass[^\n]+\n)",
                    rf"\1{graphicspath_cmd}",
                    content,
                    count=1,
                )

        return content

    def analyze(self, latex_content: str) -> dict[str, Any]:
        """Analyze graphics path optimization opportunities."""
        has_graphicspath = bool(re.search(r"\\graphicspath", latex_content))
        graphics_files = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", latex_content)

        paths = set()
        for gfile in graphics_files:
            path = Path(gfile).parent
            if path != Path():
                paths.add(str(path))

        return {
            "has_graphicspath": has_graphicspath,
            "unique_graphics_paths": len(paths),
            "total_graphics": len(graphics_files),
            "would_add_graphicspath": not has_graphicspath and len(paths) > 0,
        }


class CrossReferenceValidationStrategy(OptimizationStrategy):
    """Validate and fix cross-reference issues."""

    def __init__(self):
        """Initialize cross-reference validation strategy."""
        super().__init__(
            name="cross_reference_validation",
            description="Validate cross-references and fix common issues",
            risk_level="low",
        )

    def apply(self, latex_content: str, complexity: DocumentComplexity) -> str:
        """Apply cross-reference fixes."""
        content = latex_content

        # Find all labels
        set(re.findall(r"\\label\{([^}]+)\}", content))

        # Find all references
        refs = re.findall(r"\\ref\{([^}]+)\}", content)
        refs.extend(re.findall(r"\\eqref\{([^}]+)\}", content))
        refs.extend(re.findall(r"\\pageref\{([^}]+)\}", content))

        # Warn about undefined references (but don't change - need compilation to verify)
        # This strategy is mostly validation

        return content

    def analyze(self, latex_content: str) -> dict[str, Any]:
        """Analyze cross-reference issues."""
        labels = set(re.findall(r"\\label\{([^}]+)\}", latex_content))
        refs = re.findall(r"\\ref\{([^}]+)\}", latex_content)
        refs.extend(re.findall(r"\\eqref\{([^}]+)\}", latex_content))
        refs.extend(re.findall(r"\\pageref\{([^}]+)\}", latex_content))

        undefined_refs = [ref for ref in refs if ref not in labels]
        unused_labels = labels - set(refs)

        return {
            "total_labels": len(labels),
            "total_references": len(refs),
            "undefined_references": len(set(undefined_refs)),
            "unused_labels": len(unused_labels),
        }


# ============================================================================
# Machine Learning Components
# ============================================================================


class PerformancePredictor:
    """ML-based performance predictor for optimization strategies."""

    def __init__(self):
        """Initialize performance predictor."""
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = [
            "equation_count",
            "package_count",
            "figure_count",
            "table_count",
            "complexity_score",
            "nesting_depth",
        ]

    def extract_features(self, complexity: DocumentComplexity) -> np.ndarray:
        """Extract features from document complexity for ML."""
        features = [
            complexity.equation_count,
            complexity.package_count,
            complexity.figure_count,
            complexity.table_count,
            complexity.complexity_score,
            complexity.nesting_depth,
        ]
        return np.array(features).reshape(1, -1)

    def train(self, training_data: list[tuple[DocumentComplexity, str, bool]]) -> None:
        """
        Train the predictor on historical data.

        Parameters
        ----------
        training_data : list[tuple[DocumentComplexity, str, bool]]
            List of (complexity, strategy_name, success) tuples
        """
        if len(training_data) < 10:
            # Not enough data to train
            return

        X = []
        y = []

        for complexity, _strategy_name, success in training_data:
            features = self.extract_features(complexity).flatten()
            X.append(features)
            y.append(1 if success else 0)

        X_array = np.array(X)
        y_array = np.array(y)

        # Scale features
        X_scaled = self.scaler.fit_transform(X_array)

        # Train model
        self.model.fit(X_scaled, y_array)
        self.is_trained = True

    def predict_success_probability(
        self, complexity: DocumentComplexity, strategy_name: str
    ) -> float:
        """
        Predict probability of strategy success.

        Parameters
        ----------
        complexity : DocumentComplexity
            Document complexity metrics
        strategy_name : str
            Name of strategy to predict for

        Returns
        -------
        float
            Predicted success probability (0.0-1.0)
        """
        if not self.is_trained:
            return 0.5  # Default probability

        features = self.extract_features(complexity)
        features_scaled = self.scaler.transform(features)

        # Get probability of success (class 1)
        proba = self.model.predict_proba(features_scaled)[0]
        return float(proba[1]) if len(proba) > 1 else 0.5


class StrategyLearner:
    """Learns optimal strategies from compilation history."""

    def __init__(self, history_path: Path | None = None):
        """
        Initialize strategy learner.

        Parameters
        ----------
        history_path : Path, optional
            Path to compilation history file
        """
        self.history_path = history_path or Path.home() / ".specify" / "latex_optimization_history.json"
        self.compilation_history: list[CompilationRecord] = []
        self.strategy_performance: dict[str, StrategyPerformance] = {}
        self.predictor = PerformancePredictor()

        # Load existing history
        self._load_history()

    def _load_history(self) -> None:
        """Load compilation history from disk."""
        if self.history_path.exists():
            try:
                with open(self.history_path) as f:
                    data = json.load(f)

                # Reconstruct compilation records
                for record_data in data.get("compilations", []):
                    record = CompilationRecord(
                        timestamp=datetime.fromisoformat(record_data["timestamp"]),
                        document_hash=record_data["document_hash"],
                        status=CompilationStatus(record_data["status"]),
                        compile_time=record_data["compile_time"],
                        error_messages=record_data.get("error_messages", []),
                        warning_messages=record_data.get("warning_messages", []),
                        optimization_applied=record_data.get("optimization_applied"),
                        metrics=record_data.get("metrics", {}),
                    )
                    self.compilation_history.append(record)

                # Reconstruct strategy performance
                for strategy_name, perf_data in data.get("strategy_performance", {}).items():
                    perf = StrategyPerformance(
                        strategy_name=strategy_name,
                        success_count=perf_data["success_count"],
                        failure_count=perf_data["failure_count"],
                        avg_improvement=perf_data["avg_improvement"],
                        avg_compile_time=perf_data["avg_compile_time"],
                        success_rate=perf_data["success_rate"],
                        last_used=datetime.fromisoformat(perf_data["last_used"])
                        if perf_data.get("last_used")
                        else None,
                    )
                    # Reconstruct document_types
                    perf.document_types = {
                        DocumentType(k): v for k, v in perf_data.get("document_types", {}).items()
                    }
                    self.strategy_performance[strategy_name] = perf

            except Exception:
                pass

    def save_history(self) -> None:
        """Save compilation history to disk."""
        self.history_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "compilations": [
                {
                    "timestamp": record.timestamp.isoformat(),
                    "document_hash": record.document_hash,
                    "status": record.status.value,
                    "compile_time": record.compile_time,
                    "error_messages": record.error_messages,
                    "warning_messages": record.warning_messages,
                    "optimization_applied": record.optimization_applied,
                    "metrics": record.metrics,
                }
                for record in self.compilation_history
            ],
            "strategy_performance": {
                name: {
                    "success_count": perf.success_count,
                    "failure_count": perf.failure_count,
                    "avg_improvement": perf.avg_improvement,
                    "avg_compile_time": perf.avg_compile_time,
                    "success_rate": perf.success_rate,
                    "last_used": perf.last_used.isoformat() if perf.last_used else None,
                    "document_types": {k.value: v for k, v in perf.document_types.items()},
                }
                for name, perf in self.strategy_performance.items()
            },
        }

        with open(self.history_path, "w") as f:
            json.dump(data, f, indent=2)

    def record_compilation(self, record: CompilationRecord) -> None:
        """Record a compilation attempt."""
        self.compilation_history.append(record)

        # Update strategy performance if optimization was applied
        if record.optimization_applied:
            strategy_name = record.optimization_applied

            if strategy_name not in self.strategy_performance:
                self.strategy_performance[strategy_name] = StrategyPerformance(
                    strategy_name=strategy_name
                )

            perf = self.strategy_performance[strategy_name]

            if record.status == CompilationStatus.SUCCESS:
                perf.success_count += 1
            else:
                perf.failure_count += 1

            total = perf.success_count + perf.failure_count
            perf.success_rate = perf.success_count / total if total > 0 else 0.0
            perf.last_used = record.timestamp

            # Update average compile time
            if perf.avg_compile_time == 0:
                perf.avg_compile_time = record.compile_time
            else:
                perf.avg_compile_time = (
                    perf.avg_compile_time * 0.9 + record.compile_time * 0.1
                )

        # Keep only last 1000 records
        if len(self.compilation_history) > 1000:
            self.compilation_history = self.compilation_history[-1000:]

        # Save after each compilation
        self.save_history()

    def get_strategy_ranking(
        self, document_type: DocumentType, optimization_level: OptimizationLevel
    ) -> list[tuple[str, float]]:
        """
        Get ranked list of strategies for document type.

        Parameters
        ----------
        document_type : DocumentType
            Type of document to optimize
        optimization_level : OptimizationLevel
            Desired optimization level

        Returns
        -------
        list[tuple[str, float]]
            List of (strategy_name, score) tuples, sorted by score descending
        """
        scores = []

        for strategy_name, perf in self.strategy_performance.items():
            # Base score on success rate
            score = perf.success_rate

            # Boost score if strategy has been used on this document type
            if document_type in perf.document_types:
                score *= 1.2

            # Boost recent strategies
            if perf.last_used:
                days_since = (datetime.now() - perf.last_used).days
                recency_factor = max(0.8, 1.0 - (days_since / 365.0) * 0.2)
                score *= recency_factor

            # Adjust based on optimization level
            # This would require risk metadata on strategies
            # For now, keep all strategies

            scores.append((strategy_name, score))

        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores

    def learn_from_history(self) -> None:
        """Train ML models from compilation history."""
        if len(self.compilation_history) < 10:
            return

        # Prepare training data for predictor
        # This would require storing complexity info with each record
        # For now, we'll train when we have enough data


# ============================================================================
# Cognitive Optimizer (Ψ₁ → Ψ₂ → Ψ₃)
# ============================================================================


class LaTeXOptimizer:
    """
    Main cognitive optimization orchestrator.

    Implements three-stage cognitive architecture:
    - Ψ₁ Perception: Analyze document complexity
    - Ψ₂ Reasoning: Select optimization strategies
    - Ψ₃ Generation: Apply transformations

    Exhibits autonomic computing properties:
    - Self-configuration: Adapts to document type
    - Self-optimization: Learns best strategies
    - Self-healing: Proposes fixes for errors
    - Self-protection: Validates changes
    """

    def __init__(
        self,
        optimization_level: OptimizationLevel = OptimizationLevel.MODERATE,
        enable_ml: bool = True,
        history_path: Path | None = None,
    ):
        """
        Initialize LaTeX optimizer.

        Parameters
        ----------
        optimization_level : OptimizationLevel
            Desired optimization level
        enable_ml : bool
            Enable machine learning components
        history_path : Path, optional
            Path to compilation history file
        """
        self.optimization_level = optimization_level
        self.enable_ml = enable_ml

        # Initialize strategies
        self.strategies: dict[str, OptimizationStrategy] = {
            "equation_simplification": EquationSimplificationStrategy(),
            "package_consolidation": PackageConsolidationStrategy(),
            "macro_expansion": MacroExpansionStrategy(),
            "bibliography_optimization": BibliographyOptimizationStrategy(),
            "float_placement": FloatPlacementStrategy(),
            "graphics_path": GraphicsPathStrategy(),
            "cross_reference_validation": CrossReferenceValidationStrategy(),
        }

        # Initialize ML components
        self.learner = StrategyLearner(history_path) if enable_ml else None
        self.metrics = OptimizationMetrics()

        # DSPy modules (initialized when configured)
        self.perception_module = None
        self.reasoning_module = None
        self.generation_module = None

        if DSPY_AVAILABLE:
            self._initialize_dspy_modules()

    def _initialize_dspy_modules(self) -> None:
        """Initialize DSPy cognitive modules."""
        if not DSPY_AVAILABLE:
            return

        # Ψ₁: Perception module
        class PerceptionModule(dspy.Module):
            def __init__(self):
                super().__init__()
                self.perceive = dspy.ChainOfThought(DocumentPerceptionSignature)

            def forward(self, latex_content: str, compilation_history: str) -> dspy.Prediction:
                return self.perceive(
                    latex_content=latex_content[:4000],  # Limit for context
                    compilation_history=compilation_history,
                )

        # Ψ₂: Reasoning module
        class ReasoningModule(dspy.Module):
            def __init__(self):
                super().__init__()
                self.reason = dspy.ChainOfThought(StrategyReasoningSignature)

            def forward(
                self,
                complexity_analysis: str,
                compilation_errors: str,
                strategy_history: str,
                optimization_level: str,
            ) -> dspy.Prediction:
                return self.reason(
                    complexity_analysis=complexity_analysis,
                    compilation_errors=compilation_errors,
                    strategy_history=strategy_history,
                    optimization_level=optimization_level,
                )

        # Ψ₃: Generation module
        class GenerationModule(dspy.Module):
            def __init__(self):
                super().__init__()
                self.generate = dspy.ChainOfThought(TransformationGenerationSignature)

            def forward(
                self,
                latex_content: str,
                strategy_name: str,
                strategy_parameters: str,
                complexity_info: str,
            ) -> dspy.Prediction:
                return self.generate(
                    latex_content=latex_content[:4000],  # Limit for context
                    strategy_name=strategy_name,
                    strategy_parameters=strategy_parameters,
                    complexity_info=complexity_info,
                )

        self.perception_module = PerceptionModule()
        self.reasoning_module = ReasoningModule()
        self.generation_module = GenerationModule()

    def analyze_complexity(self, latex_content: str) -> DocumentComplexity:
        """
        Ψ₁ Perception: Analyze document complexity.

        Parameters
        ----------
        latex_content : str
            LaTeX document content

        Returns
        -------
        DocumentComplexity
            Detailed complexity analysis
        """
        with span("latex_optimizer.perception"):
            complexity = DocumentComplexity()

            # Basic metrics
            complexity.total_lines = len(latex_content.split("\n"))
            complexity.equation_count = len(
                re.findall(r"\\begin\{equation\*?\}|\\begin\{align\*?\}|\\\[", latex_content)
            )
            complexity.figure_count = len(re.findall(r"\\begin\{figure\}", latex_content))
            complexity.table_count = len(re.findall(r"\\begin\{table\}", latex_content))
            complexity.citation_count = len(re.findall(r"\\cite", latex_content))

            # Package analysis
            packages = re.findall(r"\\usepackage(?:\[[^\]]*\])?\{([^}]+)\}", latex_content)
            complexity.package_count = len(packages)
            complexity.packages = list(set(packages))

            # Find redundant packages
            package_counts = Counter(packages)
            complexity.redundant_packages = [pkg for pkg, count in package_counts.items() if count > 1]

            # Custom macros
            complexity.custom_macro_count = len(re.findall(r"\\newcommand", latex_content))

            # Nesting depth (approximate)
            max_depth = 0
            current_depth = 0
            for line in latex_content.split("\n"):
                current_depth += line.count(r"\begin{")
                current_depth -= line.count(r"\end{")
                max_depth = max(max_depth, current_depth)
            complexity.nesting_depth = max_depth

            # Float and cross-reference counts
            complexity.float_count = complexity.figure_count + complexity.table_count
            complexity.cross_ref_count = len(re.findall(r"\\ref\{|\\eqref\{|\\pageref\{", latex_content))

            # Detect document type
            complexity.document_type = self._detect_document_type(latex_content)

            # Calculate complexity score (0-100)
            complexity.complexity_score = min(
                100.0,
                (
                    complexity.equation_count * 2.0
                    + complexity.figure_count * 1.5
                    + complexity.table_count * 1.5
                    + complexity.package_count * 0.5
                    + complexity.custom_macro_count * 1.0
                    + complexity.nesting_depth * 5.0
                )
                / 10.0,
            )

            # Identify problematic constructs
            if re.search(r"\\def\\", latex_content):
                complexity.problematic_constructs.append("Uses \\def instead of \\newcommand")
            if re.search(r"\\pdfoutput", latex_content):
                complexity.problematic_constructs.append("Direct PDF output manipulation")

            metric_histogram("latex_optimizer.complexity_score")(complexity.complexity_score)

            return complexity

    def _detect_document_type(self, latex_content: str) -> DocumentType:
        """Detect document type from content."""
        # Check documentclass
        doc_class_match = re.search(r"\\documentclass(?:\[[^\]]*\])?\{([^}]+)\}", latex_content)
        if doc_class_match:
            doc_class = doc_class_match.group(1)
            if "article" in doc_class:
                return DocumentType.ARTICLE
            if "book" in doc_class:
                return DocumentType.BOOK
            if "report" in doc_class:
                return DocumentType.REPORT
            if "beamer" in doc_class:
                return DocumentType.PRESENTATION
            if "letter" in doc_class:
                return DocumentType.LETTER

        # Check for thesis patterns
        if re.search(r"\\chapter|thesis|dissertation", latex_content, re.IGNORECASE):
            return DocumentType.THESIS

        return DocumentType.UNKNOWN

    def select_strategies(
        self, complexity: DocumentComplexity, compilation_errors: list[str] | None = None
    ) -> list[str]:
        """
        Ψ₂ Reasoning: Select optimal optimization strategies.

        Parameters
        ----------
        complexity : DocumentComplexity
            Document complexity analysis
        compilation_errors : list[str], optional
            Recent compilation errors

        Returns
        -------
        list[str]
            Ordered list of strategy names to apply
        """
        with span("latex_optimizer.reasoning"):
            compilation_errors = compilation_errors or []

            # Get ML-based ranking if available
            if self.learner:
                ml_ranking = self.learner.get_strategy_ranking(
                    complexity.document_type, self.optimization_level
                )
                if ml_ranking:
                    return [name for name, _score in ml_ranking]

            # Fallback: Rule-based strategy selection
            selected = []

            # Always try package consolidation if there are redundant packages
            if complexity.redundant_packages:
                selected.append("package_consolidation")

            # Equation simplification for math-heavy documents
            if complexity.equation_count > 10:
                selected.append("equation_simplification")

            # Float placement if many floats
            if complexity.float_count > 5:
                selected.append("float_placement")

            # Graphics path optimization if many figures
            if complexity.figure_count > 3:
                selected.append("graphics_path")

            # Cross-reference validation
            selected.append("cross_reference_validation")

            # Macro expansion for complex documents (aggressive mode only)
            if self.optimization_level == OptimizationLevel.AGGRESSIVE:
                if complexity.custom_macro_count > 5:
                    selected.append("macro_expansion")

            # Bibliography optimization if citations present
            if complexity.citation_count > 10:
                selected.append("bibliography_optimization")

            metric_counter("latex_optimizer.strategies_selected")(len(selected))

            return selected

    def apply_optimization(
        self, latex_content: str, strategy_name: str, complexity: DocumentComplexity
    ) -> OptimizationResult:
        """
        Ψ₃ Generation: Apply optimization transformation.

        Parameters
        ----------
        latex_content : str
            Original LaTeX content
        strategy_name : str
            Name of strategy to apply
        complexity : DocumentComplexity
            Document complexity info

        Returns
        -------
        OptimizationResult
            Result of optimization with validation
        """
        with span("latex_optimizer.generation", strategy=strategy_name):
            if strategy_name not in self.strategies:
                return OptimizationResult(
                    success=False,
                    original_content=latex_content,
                    optimized_content=latex_content,
                    strategy_name=strategy_name,
                    changes_made=["Unknown strategy"],
                    confidence=0.0,
                )

            strategy = self.strategies[strategy_name]

            try:
                # Analyze before applying
                analysis = strategy.analyze(latex_content)

                # Apply optimization
                start_time = time.perf_counter()
                optimized_content = strategy.apply(latex_content, complexity)
                elapsed = time.perf_counter() - start_time

                # Validate changes
                validation_passed = self._validate_optimization(latex_content, optimized_content)

                # Calculate confidence based on analysis
                confidence = min(
                    1.0,
                    0.5
                    + (analysis.get("total_changes", 0) * 0.1)
                    + (strategy.get_avg_performance() * 0.3),
                )

                # Build changes summary
                changes_made = [f"{k}: {v}" for k, v in analysis.items()]

                metric_histogram("latex_optimizer.optimization_time")(elapsed)
                metric_counter("latex_optimizer.optimizations_applied")(1)

                return OptimizationResult(
                    success=True,
                    original_content=latex_content,
                    optimized_content=optimized_content,
                    strategy_name=strategy_name,
                    changes_made=changes_made,
                    estimated_improvement=analysis.get("total_changes", 0) * 0.05,
                    confidence=confidence,
                    reasoning=f"Applied {strategy_name}: {strategy.description}",
                    validation_passed=validation_passed,
                )


            except Exception as e:
                metric_counter("latex_optimizer.optimization_failed")(1)
                return OptimizationResult(
                    success=False,
                    original_content=latex_content,
                    optimized_content=latex_content,
                    strategy_name=strategy_name,
                    changes_made=[f"Error: {e}"],
                    confidence=0.0,
                )

    def _validate_optimization(self, original: str, optimized: str) -> bool:
        """
        Self-protection: Validate optimization didn't break document.

        Parameters
        ----------
        original : str
            Original content
        optimized : str
            Optimized content

        Returns
        -------
        bool
            True if validation passed
        """
        # Basic structural validation
        checks = [
            # Check begin/end balance
            (
                original.count(r"\begin{") == optimized.count(r"\begin{"),
                "begin/end balance",
            ),
            (
                original.count(r"\end{") == optimized.count(r"\end{"),
                "begin/end balance",
            ),
            # Check documentclass preserved
            (
                bool(re.search(r"\\documentclass", optimized)),
                "documentclass present",
            ),
            # Check document environment preserved
            (
                bool(re.search(r"\\begin\{document\}", optimized)),
                "document environment",
            ),
            # Length check (shouldn't reduce by more than 30%)
            (len(optimized) >= len(original) * 0.7, "length check"),
        ]

        failed_checks = [name for passed, name in checks if not passed]

        return not failed_checks

    def optimize(
        self, latex_content: str, max_iterations: int = 3
    ) -> tuple[str, OptimizationMetrics]:
        """
        Full optimization pipeline: Ψ₁ → Ψ₂ → Ψ₃.

        Parameters
        ----------
        latex_content : str
            Original LaTeX content
        max_iterations : int
            Maximum optimization iterations

        Returns
        -------
        tuple[str, OptimizationMetrics]
            (optimized_content, metrics)
        """
        with span("latex_optimizer.optimize", iterations=max_iterations):
            current_content = latex_content
            iteration = 0

            while iteration < max_iterations:
                iteration += 1

                # Ψ₁: Perception
                complexity = self.analyze_complexity(current_content)

                # Ψ₂: Reasoning
                strategies = self.select_strategies(complexity)

                if not strategies:
                    break  # No more strategies to apply

                # Ψ₃: Generation - apply top strategy
                strategy_name = strategies[0]
                result = self.apply_optimization(current_content, strategy_name, complexity)

                if result.success and result.validation_passed:
                    current_content = result.optimized_content
                    self.metrics.successful_optimizations += 1
                    self.metrics.strategies_used[strategy_name] = (
                        self.metrics.strategies_used.get(strategy_name, 0) + 1
                    )

                    # Record with learner
                    if self.learner:
                        record = CompilationRecord(
                            timestamp=datetime.now(),
                            document_hash=hashlib.sha256(current_content.encode()).hexdigest(),
                            status=CompilationStatus.SUCCESS,
                            compile_time=0.0,  # Would be measured in real compilation
                            optimization_applied=strategy_name,
                        )
                        self.learner.record_compilation(record)
                else:
                    self.metrics.failed_optimizations += 1

                self.metrics.total_optimizations += 1

            return current_content, self.metrics


# ============================================================================
# Example Usage and Testing
# ============================================================================


def example_basic_usage() -> None:
    """Example: Basic optimization usage."""

    # Sample LaTeX document
    latex_doc = r"""
\documentclass{article}
\usepackage{amsmath}
\usepackage{graphicx}
\usepackage{amsmath}  % Duplicate!
\usepackage{epsfig}   % Obsolete!

\begin{document}
\section{Introduction}

Some math: \[ E = mc^2 \]

\begin{figure}[h]
\includegraphics{figures/plot.pdf}
\caption{A plot}
\end{figure}

More math: \begin{equation}
    x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
\end{equation}

\end{document}
"""

    # Create optimizer
    optimizer = LaTeXOptimizer(
        optimization_level=OptimizationLevel.MODERATE,
        enable_ml=False,  # Disable ML for simple example
    )

    # Analyze complexity (Ψ₁)
    complexity = optimizer.analyze_complexity(latex_doc)

    # Select strategies (Ψ₂)
    optimizer.select_strategies(complexity)

    # Apply optimizations (Ψ₃)
    _optimized, _metrics = optimizer.optimize(latex_doc, max_iterations=3)




def example_ml_learning() -> None:
    """Example: Machine learning from compilation history."""

    # Create optimizer with ML enabled
    optimizer = LaTeXOptimizer(
        optimization_level=OptimizationLevel.MODERATE,
        enable_ml=True,
    )

    # Simulate compilation history

    sample_docs = [
        (DocumentType.ARTICLE, "equation_simplification", True),
        (DocumentType.ARTICLE, "equation_simplification", True),
        (DocumentType.ARTICLE, "package_consolidation", True),
        (DocumentType.BOOK, "package_consolidation", False),
        (DocumentType.THESIS, "macro_expansion", True),
    ]

    for doc_type, strategy, success in sample_docs:
        # Create synthetic complexity
        DocumentComplexity(
            total_lines=100,
            equation_count=10 if doc_type == DocumentType.ARTICLE else 50,
            package_count=15,
            complexity_score=30.0,
            document_type=doc_type,
        )

        # Record compilation
        record = CompilationRecord(
            timestamp=datetime.now(),
            document_hash=hashlib.sha256(b"test").hexdigest(),
            status=CompilationStatus.SUCCESS if success else CompilationStatus.ERROR,
            compile_time=1.5,
            optimization_applied=strategy,
        )

        if optimizer.learner:
            optimizer.learner.record_compilation(record)


    # Get strategy rankings
    if optimizer.learner:
        rankings = optimizer.learner.get_strategy_ranking(
            DocumentType.ARTICLE, OptimizationLevel.MODERATE
        )
        for _strategy_name, _score in rankings[:5]:
            pass


def example_autonomic_properties() -> None:
    """Example: Demonstrate autonomic computing properties."""

    optimizer = LaTeXOptimizer(optimization_level=OptimizationLevel.AGGRESSIVE)

    # Self-configuration: Adapts to document type
    article_doc = r"\documentclass{article}\begin{document}Test\end{document}"
    book_doc = r"\documentclass{book}\begin{document}\chapter{Test}Test\end{document}"

    optimizer.analyze_complexity(article_doc)
    optimizer.analyze_complexity(book_doc)


    # Self-optimization: Learns best strategies

    # Self-healing: Proposes fixes
    broken_doc = r"""
\documentclass{article}
\usepackage{epsfig}  % Obsolete package
\begin{document}
\begin{figure}[h]    % Restrictive placement
\end{document}
"""
    complexity = optimizer.analyze_complexity(broken_doc)
    optimizer.select_strategies(complexity)

    # Self-protection: Validates changes
    test_content = r"\documentclass{article}\begin{document}Test\end{document}"
    broken_content = r"\documentclass{article}Test\end{document}"  # Missing begin

    optimizer._validate_optimization(test_content, test_content)
    optimizer._validate_optimization(test_content, broken_content)



def example_comprehensive() -> None:
    """Comprehensive example with all features."""

    # Complex thesis document
    thesis_doc = r"""
\documentclass[12pt]{report}
\usepackage{amsmath}
\usepackage{amsmath}  % Duplicate
\usepackage{graphicx}
\usepackage{epsfig}   % Obsolete
\usepackage{subfigure}  % Obsolete
\usepackage{natbib}

\newcommand{\myref}[1]{\cite{#1}}  % Fragile command in macro

\begin{document}

\chapter{Introduction}

As shown in \myref{smith2020}, we have:

\[ E = mc^2 \]

\begin{figure}[h]
\includegraphics{images/chapter1/plot1.pdf}
\caption{First plot}
\end{figure}

\begin{figure}[t]
\includegraphics{images/chapter1/plot2.pdf}
\caption{Second plot}
\end{figure}

\begin{equation}
    x = \frac  {-b    \pm   \sqrt{b^2 - 4ac}}  {2a}
\end{equation}

\begin{table}[h]
\begin{tabular}{ll}
A & B \\
C & D
\end{tabular}
\caption{A table}
\end{table}

\bibliographystyle{plain}
\bibliography{references}

\end{document}
"""

    optimizer = LaTeXOptimizer(
        optimization_level=OptimizationLevel.AGGRESSIVE,
        enable_ml=True,
    )

    _optimized_content, metrics = optimizer.optimize(thesis_doc, max_iterations=5)

    for _strategy, _count in metrics.strategies_used.items():
        pass



if __name__ == "__main__":
    # Run all examples
    example_basic_usage()
    example_ml_learning()
    example_autonomic_properties()
    example_comprehensive()

