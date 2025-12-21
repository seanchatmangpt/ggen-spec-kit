"""
DSPy Spec Optimization Implementation

This module contains the optimize_spec function and related utilities.
Separated for clarity and testing.
"""

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from specify_cli.core.telemetry import metric_counter, metric_histogram, span

try:
    import dspy
    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False
    dspy = None  # type: ignore[assignment]


@dataclass
class OptimizeResult:
    """Result of spec optimization operation."""

    success: bool
    original_spec: str
    optimized_spec: str
    iterations: int
    metrics: dict[str, float] = field(default_factory=dict)
    improvement: float = 0.0
    errors: list[str] = field(default_factory=list)


def optimize_spec(  # noqa: PLR0911, PLR0912, PLR0915
    spec_file: Path,
    metric: str = "coverage",
    iterations: int = 3,
    model: str = "claude",  # noqa: ARG001
    temperature: float = 0.7,
) -> OptimizeResult:
    """
    Optimize a specification using DSPy with LLM-powered iterative refinement.

    This function implements a complete DSPy-based optimization loop that:
    1. Loads spec file (TTL or JSON format)
    2. Creates DSPy program for optimization
    3. Defines optimization metric/goal
    4. Runs optimization loop (N iterations)
    5. Measures improvement at each iteration
    6. Returns optimized spec + metrics

    Parameters
    ----------
    spec_file : Path
        Path to specification file (TTL or JSON format).
    metric : str, optional
        Optimization metric: 'coverage', 'clarity', 'brevity', 'performance'.
        Default is 'coverage'.
    iterations : int, optional
        Number of optimization iterations. Default is 3.
    model : str, optional
        LLM model identifier. Default is 'claude'.
    temperature : float, optional
        LLM temperature (0.0-1.0). Default is 0.7.

    Returns
    -------
    OptimizeResult
        Result containing success status, original spec, optimized spec,
        iterations, metrics, improvement percentage, and any errors.

    Raises
    ------
    ImportError
        If DSPy is not available.
    FileNotFoundError
        If spec_file does not exist.
    ValueError
        If metric is invalid or iterations/temperature out of range.

    Examples
    --------
    >>> result = optimize_spec(
    ...     spec_file=Path("ontology/spec-kit-schema.ttl"),
    ...     metric="coverage",
    ...     iterations=3
    ... )
    >>> print(f"Improvement: {result.improvement:.1f}%")
    >>> print(f"Coverage score: {result.metrics['coverage']:.2f}")

    Notes
    -----
    Requires DSPy to be installed and configured with a valid LLM provider.
    The function uses ChainOfThought for structured optimization.
    """
    if not DSPY_AVAILABLE:
        return OptimizeResult(
            success=False,
            original_spec="",
            optimized_spec="",
            iterations=0,
            errors=["DSPy is not installed. Install with: pip install dspy"],
        )

    # Validate inputs
    if not spec_file.exists():
        return OptimizeResult(
            success=False,
            original_spec="",
            optimized_spec="",
            iterations=0,
            errors=[f"Spec file not found: {spec_file}"],
        )

    if metric not in ["coverage", "clarity", "brevity", "performance"]:
        return OptimizeResult(
            success=False,
            original_spec="",
            optimized_spec="",
            iterations=0,
            errors=[f"Invalid metric: {metric}. Choose: coverage, clarity, brevity, performance"],
        )

    if iterations < 1 or iterations > 10:
        return OptimizeResult(
            success=False,
            original_spec="",
            optimized_spec="",
            iterations=0,
            errors=["Iterations must be between 1 and 10"],
        )

    if temperature < 0.0 or temperature > 1.0:
        return OptimizeResult(
            success=False,
            original_spec="",
            optimized_spec="",
            iterations=0,
            errors=["Temperature must be between 0.0 and 1.0"],
        )

    # Load spec file
    try:
        original_spec = spec_file.read_text()
        spec_format = "ttl" if spec_file.suffix.lower() in [".ttl", ".turtle", ".rdf"] else "json"
    except Exception as e:
        return OptimizeResult(
            success=False,
            original_spec="",
            optimized_spec="",
            iterations=0,
            errors=[f"Error reading spec file: {e}"],
        )

    # Define DSPy signature for spec optimization
    class SpecOptimizer(dspy.Signature):
        """Optimize a specification based on a given metric."""

        spec: str = dspy.InputField(desc="The specification to optimize")
        metric: str = dspy.InputField(desc="The optimization metric: coverage, clarity, brevity, or performance")
        format_type: str = dspy.InputField(desc="The spec format: ttl or json")
        iteration: int = dspy.InputField(desc="Current iteration number")

        optimized_spec: str = dspy.OutputField(desc="The optimized specification")
        reasoning: str = dspy.OutputField(desc="Explanation of optimizations made")
        score: float = dspy.OutputField(desc="Quality score (0.0-1.0) for this optimization")

    # Create the optimizer module
    class SpecOptimizerModule(dspy.Module):
        """DSPy module for iterative spec optimization."""

        def __init__(self) -> None:
            super().__init__()
            self.optimize = dspy.ChainOfThought(SpecOptimizer)

        def forward(self, spec: str, metric: str, format_type: str, iteration: int) -> dspy.Prediction:
            """Run one optimization iteration."""
            return self.optimize(
                spec=spec,
                metric=metric,
                format_type=format_type,
                iteration=iteration,
            )

    # Run optimization loop with telemetry
    errors: list[str] = []
    current_spec = original_spec
    iteration_scores: list[float] = []
    iteration_metrics: list[dict[str, Any]] = []

    try:
        with span("dspy.optimize_spec", metric=metric, iterations=iterations):
            optimizer = SpecOptimizerModule()

            for i in range(iterations):
                with span(f"dspy.optimize_spec.iteration_{i+1}", iteration=i+1):
                    iteration_start = time.perf_counter()

                    try:
                        # Run optimization
                        result = optimizer.forward(
                            spec=current_spec,
                            metric=metric,
                            format_type=spec_format,
                            iteration=i + 1,
                        )

                        # Extract results
                        optimized = getattr(result, "optimized_spec", current_spec)
                        reasoning = getattr(result, "reasoning", "No reasoning provided")
                        score = getattr(result, "score", 0.0)

                        # Validate score
                        if isinstance(score, str):
                            try:
                                score = float(score)
                            except (ValueError, TypeError):
                                score = 0.0
                        score = max(0.0, min(1.0, float(score)))

                        iteration_scores.append(score)
                        current_spec = optimized

                        # Record metrics
                        iteration_duration = time.perf_counter() - iteration_start
                        metric_histogram("dspy.optimize_spec.iteration.duration")(iteration_duration)
                        metric_counter("dspy.optimize_spec.iteration.completed")(1)

                        # Calculate iteration metrics
                        iteration_metrics.append({
                            "iteration": i + 1,
                            "score": score,
                            "reasoning": reasoning,
                            "duration": iteration_duration,
                        })

                    except Exception as e:
                        error_msg = f"Iteration {i+1} failed: {e}"
                        errors.append(error_msg)
                        metric_counter("dspy.optimize_spec.iteration.failed")(1)
                        # Continue with current spec
                        iteration_scores.append(0.0)

            # Calculate final metrics
            final_metrics = _calculate_optimization_metrics(
                original_spec=original_spec,
                optimized_spec=current_spec,
                metric=metric,
                iteration_scores=iteration_scores,
            )

            # Calculate improvement
            if iteration_scores:
                initial_score = iteration_scores[0] if len(iteration_scores) > 0 else 0.0
                final_score = iteration_scores[-1] if len(iteration_scores) > 0 else 0.0
                if initial_score > 0:
                    improvement = ((final_score - initial_score) / initial_score) * 100
                else:
                    improvement = final_score * 100
            else:
                improvement = 0.0

            metric_counter("dspy.optimize_spec.completed")(1)

            return OptimizeResult(
                success=True,
                original_spec=original_spec,
                optimized_spec=current_spec,
                iterations=iterations,
                metrics=final_metrics,
                improvement=improvement,
                errors=errors,
            )

    except Exception as e:
        metric_counter("dspy.optimize_spec.failed")(1)
        return OptimizeResult(
            success=False,
            original_spec=original_spec,
            optimized_spec=current_spec,
            iterations=0,
            errors=[f"Optimization failed: {e}", *errors],
        )


def _calculate_optimization_metrics(
    original_spec: str,
    optimized_spec: str,
    metric: str,
    iteration_scores: list[float],
) -> dict[str, float]:
    """
    Calculate optimization metrics based on spec changes.

    Parameters
    ----------
    original_spec : str
        Original specification text.
    optimized_spec : str
        Optimized specification text.
    metric : str
        The optimization metric used.
    iteration_scores : list[float]
        Scores from each iteration.

    Returns
    -------
    dict[str, float]
        Dictionary of metric names to values.
    """
    metrics: dict[str, float] = {}

    # Basic metrics
    metrics["original_length"] = float(len(original_spec))
    metrics["optimized_length"] = float(len(optimized_spec))
    metrics["length_ratio"] = len(optimized_spec) / len(original_spec) if original_spec else 1.0

    # Line counts
    original_lines = original_spec.count("\n") + 1
    optimized_lines = optimized_spec.count("\n") + 1
    metrics["original_lines"] = float(original_lines)
    metrics["optimized_lines"] = float(optimized_lines)

    # Coverage metric (estimated by content density)
    if metric == "coverage":
        # Count key spec elements (classes, properties, requirements, etc.)
        coverage_keywords = ["a owl:Class", "a rdfs:Property", "spec:", "FR-", "US-", "SC-"]
        original_coverage = sum(original_spec.count(kw) for kw in coverage_keywords)
        optimized_coverage = sum(optimized_spec.count(kw) for kw in coverage_keywords)
        metrics["coverage"] = optimized_coverage / max(original_coverage, 1)
    else:
        metrics["coverage"] = sum(iteration_scores) / len(iteration_scores) if iteration_scores else 0.0

    # Clarity metric (estimated by comment density and structure)
    if metric == "clarity":
        original_comments = original_spec.count("#")
        optimized_comments = optimized_spec.count("#")
        metrics["clarity"] = min(1.0, optimized_comments / max(original_comments, 1))
    else:
        metrics["clarity"] = sum(iteration_scores) / len(iteration_scores) if iteration_scores else 0.0

    # Brevity metric (measured by compression)
    if metric == "brevity":
        metrics["brevity"] = 1.0 - (metrics["length_ratio"] - 1.0) if metrics["length_ratio"] < 1.0 else 0.0
    else:
        metrics["brevity"] = sum(iteration_scores) / len(iteration_scores) if iteration_scores else 0.0

    # Performance metric (estimated by parse complexity)
    if metric == "performance":
        # Simple heuristic: fewer nested structures = better performance
        original_nesting = original_spec.count("  ") + original_spec.count("\t")
        optimized_nesting = optimized_spec.count("  ") + optimized_spec.count("\t")
        metrics["performance"] = 1.0 - (optimized_nesting / max(original_nesting, 1))
    else:
        metrics["performance"] = sum(iteration_scores) / len(iteration_scores) if iteration_scores else 0.0

    # Average score across iterations
    if iteration_scores:
        metrics["average_score"] = sum(iteration_scores) / len(iteration_scores)
        metrics["final_score"] = iteration_scores[-1]
    else:
        metrics["average_score"] = 0.0
        metrics["final_score"] = 0.0

    return metrics
