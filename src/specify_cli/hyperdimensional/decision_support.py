"""
specify_cli.hyperdimensional.decision_support - Decision Support System
======================================================================

Decision support system with recommendation engine, priority visualization, and risk assessment.

This module provides decision support capabilities for:
* **Recommendation Engine**: Feature recommendations, trade-off analysis, cost-benefit
* **Priority Visualization**: Priority matrices, impact-effort charts, critical paths
* **Risk Assessment**: Risk heatmaps, failure modes, mitigation strategies

Examples
--------
    >>> from specify_cli.hyperdimensional.decision_support import DecisionSupportSystem
    >>>
    >>> dss = DecisionSupportSystem()
    >>> recommendations = dss.show_recommended_features(objectives)
    >>> trade_offs = dss.show_trade_offs(options)
    >>> risks = dss.risk_heatmap(designs, risks)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np

from specify_cli.core.telemetry import span
from specify_cli.hyperdimensional.dashboards import VisualizationData

if TYPE_CHECKING:
    from numpy.typing import NDArray

__all__ = [
    "DecisionSupportSystem",
    "Recommendation",
    "RiskAssessment",
    "TradeOffAnalysis",
]


@dataclass
class Recommendation:
    """Recommendation data structure."""

    feature_name: str
    score: float  # 0.0 to 1.0
    reasoning: str
    confidence: float  # 0.0 to 1.0
    alternatives: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TradeOffAnalysis:
    """Trade-off analysis data structure."""

    option_name: str
    dimensions: dict[str, float]  # dimension -> score
    overall_score: float
    strengths: list[str]
    weaknesses: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RiskAssessment:
    """Risk assessment data structure."""

    risk_name: str
    probability: float  # 0.0 to 1.0
    impact: float  # 0.0 to 1.0
    severity: str  # "low", "medium", "high", "critical"
    mitigation_strategies: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)


class DecisionSupportSystem:
    """
    Comprehensive decision support system for architectural decisions.

    This class provides recommendation engine, priority visualization, and
    risk assessment capabilities for informed decision-making.

    Attributes
    ----------
    min_confidence : float
        Minimum confidence threshold for recommendations (0.0 to 1.0).
    enable_explanations : bool
        Enable detailed explanations for recommendations.
    """

    def __init__(
        self,
        min_confidence: float = 0.7,
        enable_explanations: bool = True,
    ) -> None:
        """
        Initialize decision support system.

        Parameters
        ----------
        min_confidence : float, optional
            Minimum confidence threshold. Default is 0.7.
        enable_explanations : bool, optional
            Enable explanations. Default is True.
        """
        self.min_confidence = min_confidence
        self.enable_explanations = enable_explanations

    # =========================================================================
    # Recommendation Engine Dashboard
    # =========================================================================

    def show_recommended_features(
        self,
        objectives: dict[str, float],
        available_features: list[dict[str, Any]],
        feature_embeddings: NDArray[np.float64] | None = None,
        top_k: int = 5,
    ) -> list[Recommendation]:
        """
        Show recommended features based on objectives.

        Ranks and recommends features that best align with stated objectives.

        Parameters
        ----------
        objectives : dict[str, float]
            Objectives with importance weights.
        available_features : list[dict[str, Any]]
            Available features to recommend from.
        feature_embeddings : NDArray[np.float64], optional
            Semantic embeddings for features.
        top_k : int, optional
            Number of recommendations to return. Default is 5.

        Returns
        -------
        list[Recommendation]
            Top-k feature recommendations.
        """
        with span("decision_support.show_recommended_features", top_k=top_k):
            recommendations = []

            # Score each feature based on objectives
            for idx, feature in enumerate(available_features):
                score = 0.0
                matched_objectives = []

                # Calculate alignment with objectives
                for obj_name, obj_weight in objectives.items():
                    if obj_name in feature.get("addresses_objectives", []):
                        score += obj_weight
                        matched_objectives.append(obj_name)

                # Normalize score
                total_weight = sum(objectives.values())
                normalized_score = score / total_weight if total_weight > 0 else 0.0

                # Calculate confidence based on coverage
                coverage = len(matched_objectives) / len(objectives) if objectives else 0.0
                confidence = (normalized_score + coverage) / 2.0

                # Generate reasoning
                reasoning = self._generate_recommendation_reasoning(
                    feature, matched_objectives, normalized_score
                )

                recommendations.append(
                    Recommendation(
                        feature_name=feature.get("name", f"feature_{idx}"),
                        score=normalized_score,
                        reasoning=reasoning,
                        confidence=confidence,
                        alternatives=[],
                        metadata={
                            "matched_objectives": matched_objectives,
                            "coverage": coverage,
                        },
                    )
                )

            # Sort by score and filter by confidence
            recommendations = [r for r in recommendations if r.confidence >= self.min_confidence]
            recommendations.sort(key=lambda r: r.score, reverse=True)

            # Get top-k
            return recommendations[:top_k]

    def _generate_recommendation_reasoning(
        self,
        feature: dict[str, Any],
        matched_objectives: list[str],
        score: float,
    ) -> str:
        """Generate human-readable reasoning for recommendation."""
        if not self.enable_explanations:
            return ""

        reasoning_parts = [
            f"This feature scores {score:.2f} based on alignment with your objectives.",
        ]

        if matched_objectives:
            obj_str = ", ".join(matched_objectives)
            reasoning_parts.append(f"It addresses: {obj_str}.")

        if "benefits" in feature:
            benefits = feature["benefits"]
            if isinstance(benefits, list):
                reasoning_parts.append(f"Key benefits: {', '.join(benefits)}.")

        return " ".join(reasoning_parts)

    def explain_recommendation(
        self,
        recommendation: Recommendation,
    ) -> str:
        """
        Explain a recommendation in detail.

        Provides detailed explanation of why a feature was recommended.

        Parameters
        ----------
        recommendation : Recommendation
            Recommendation to explain.

        Returns
        -------
        str
            Detailed explanation.
        """
        with span("decision_support.explain_recommendation"):
            explanation = [
                f"Recommendation: {recommendation.feature_name}",
                f"Score: {recommendation.score:.2f}/1.00",
                f"Confidence: {recommendation.confidence:.2f}/1.00",
                "",
                "Reasoning:",
                recommendation.reasoning,
            ]

            if recommendation.metadata.get("matched_objectives"):
                matched = recommendation.metadata["matched_objectives"]
                explanation.extend(
                    [
                        "",
                        "Matched Objectives:",
                        *[f"  - {obj}" for obj in matched],
                    ]
                )

            if recommendation.alternatives:
                explanation.extend(
                    [
                        "",
                        "Alternative Options:",
                        *[f"  - {alt}" for alt in recommendation.alternatives],
                    ]
                )

            return "\n".join(explanation)

    def show_trade_offs(
        self,
        options: list[dict[str, Any]],
        dimensions: list[str],
    ) -> list[TradeOffAnalysis]:
        """
        Show trade-offs between different options.

        Analyzes trade-offs across multiple dimensions for different options.

        Parameters
        ----------
        options : list[dict[str, Any]]
            Options to analyze.
        dimensions : list[str]
            Dimensions to evaluate (e.g., "speed", "reliability", "simplicity").

        Returns
        -------
        list[TradeOffAnalysis]
            Trade-off analysis for each option.
        """
        with span("decision_support.show_trade_offs", n_options=len(options)):
            analyses = []

            for option in options:
                dim_scores = {}
                strengths = []
                weaknesses = []

                # Evaluate each dimension
                for dim in dimensions:
                    score = option.get(dim, 0.5)  # Default to middle score
                    dim_scores[dim] = score

                    if score >= 0.7:
                        strengths.append(f"High {dim}")
                    elif score <= 0.3:
                        weaknesses.append(f"Low {dim}")

                # Calculate overall score (weighted average)
                overall = sum(dim_scores.values()) / len(dim_scores) if dim_scores else 0.0

                analyses.append(
                    TradeOffAnalysis(
                        option_name=option.get("name", "unknown"),
                        dimensions=dim_scores,
                        overall_score=overall,
                        strengths=strengths,
                        weaknesses=weaknesses,
                        metadata={"raw_option": option},
                    )
                )

            # Sort by overall score
            analyses.sort(key=lambda a: a.overall_score, reverse=True)

            return analyses

    def cost_benefit_analysis(
        self,
        option: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Perform detailed cost-benefit analysis for an option.

        Analyzes costs vs. benefits with detailed breakdown.

        Parameters
        ----------
        option : dict[str, Any]
            Option to analyze with cost and benefit data.

        Returns
        -------
        dict[str, Any]
            Detailed cost-benefit analysis.
        """
        with span("decision_support.cost_benefit_analysis"):
            costs = option.get("costs", {})
            benefits = option.get("benefits", {})

            # Calculate totals
            total_cost = sum(costs.values()) if isinstance(costs, dict) else costs
            total_benefit = sum(benefits.values()) if isinstance(benefits, dict) else benefits

            # Calculate metrics
            roi = ((total_benefit - total_cost) / total_cost * 100) if total_cost > 0 else 0.0
            payback_period = (
                total_cost / (total_benefit / 12) if total_benefit > 0 else float("inf")
            )
            net_benefit = total_benefit - total_cost

            return {
                "option_name": option.get("name", "unknown"),
                "total_cost": total_cost,
                "total_benefit": total_benefit,
                "net_benefit": net_benefit,
                "roi_percentage": roi,
                "payback_months": payback_period if payback_period != float("inf") else None,
                "cost_breakdown": costs,
                "benefit_breakdown": benefits,
                "recommendation": "approve" if net_benefit > 0 else "reject",
            }

    # =========================================================================
    # Priority Visualization
    # =========================================================================

    def priority_matrix(
        self,
        tasks: list[dict[str, Any]],
        dimensions: tuple[str, str] = ("urgency", "importance"),
    ) -> VisualizationData:
        """
        Create 2x2 priority matrix visualization.

        Creates Eisenhower matrix or similar priority visualization.

        Parameters
        ----------
        tasks : list[dict[str, Any]]
            Tasks to prioritize.
        dimensions : tuple[str, str], optional
            Two dimensions for the matrix. Default is ("urgency", "importance").

        Returns
        -------
        VisualizationData
            Priority matrix visualization data.
        """
        with span("decision_support.priority_matrix", n_tasks=len(tasks)):
            dim_x, dim_y = dimensions

            # Extract coordinates
            x_values = []
            y_values = []
            labels = []
            quadrants = []

            for task in tasks:
                x = task.get(dim_x, 0.5)
                y = task.get(dim_y, 0.5)
                x_values.append(x)
                y_values.append(y)
                labels.append(task.get("name", "unknown"))

                # Determine quadrant
                if x >= 0.5 and y >= 0.5:
                    quadrant = "high_urgency_high_importance"
                elif x >= 0.5 and y < 0.5:
                    quadrant = "high_urgency_low_importance"
                elif x < 0.5 and y >= 0.5:
                    quadrant = "low_urgency_high_importance"
                else:
                    quadrant = "low_urgency_low_importance"
                quadrants.append(quadrant)

            data = {
                "x": x_values,
                "y": y_values,
                "labels": labels,
                "quadrants": quadrants,
                "x_dimension": dim_x,
                "y_dimension": dim_y,
            }

            metadata = {
                "n_tasks": len(tasks),
                "quadrant_counts": {q: quadrants.count(q) for q in set(quadrants)},
            }

            return VisualizationData(
                title=f"Priority Matrix ({dim_x} vs {dim_y})",
                chart_type="scatter",
                data=data,
                metadata=metadata,
            )

    def impact_effort_chart(
        self,
        tasks: list[dict[str, Any]],
    ) -> VisualizationData:
        """
        Create impact vs. effort chart.

        Visualizes tasks by their impact and effort required to identify
        quick wins and long-term investments.

        Parameters
        ----------
        tasks : list[dict[str, Any]]
            Tasks with impact and effort scores.

        Returns
        -------
        VisualizationData
            Impact-effort chart visualization.
        """
        with span("decision_support.impact_effort_chart", n_tasks=len(tasks)):
            efforts = []
            impacts = []
            labels = []
            categories = []

            for task in tasks:
                effort = task.get("effort", 0.5)
                impact = task.get("impact", 0.5)

                efforts.append(effort)
                impacts.append(impact)
                labels.append(task.get("name", "unknown"))

                # Categorize
                if impact >= 0.7 and effort <= 0.3:
                    category = "quick_wins"
                elif impact >= 0.7 and effort >= 0.7:
                    category = "major_projects"
                elif impact <= 0.3 and effort <= 0.3:
                    category = "fill_ins"
                else:
                    category = "thankless_tasks"
                categories.append(category)

            data = {
                "effort": efforts,
                "impact": impacts,
                "labels": labels,
                "categories": categories,
            }

            metadata = {
                "n_tasks": len(tasks),
                "quick_wins": categories.count("quick_wins"),
                "major_projects": categories.count("major_projects"),
            }

            return VisualizationData(
                title="Impact vs. Effort Analysis",
                chart_type="scatter",
                data=data,
                metadata=metadata,
            )

    def critical_path_visualization(
        self,
        tasks: list[dict[str, Any]],
        dependencies: list[tuple[str, str]],
    ) -> VisualizationData:
        """
        Visualize critical path through tasks.

        Identifies bottlenecks and critical path using dependency analysis.

        Parameters
        ----------
        tasks : list[dict[str, Any]]
            Tasks with durations.
        dependencies : list[tuple[str, str]]
            Task dependencies as (from_task, to_task) pairs.

        Returns
        -------
        VisualizationData
            Critical path visualization.
        """
        with span("decision_support.critical_path", n_tasks=len(tasks)):
            # Build task lookup
            task_map = {t.get("name", f"task_{i}"): t for i, t in enumerate(tasks)}

            # Calculate earliest start times
            earliest_start = dict.fromkeys(task_map, 0)
            for from_task, to_task in dependencies:
                if from_task in task_map and to_task in task_map:
                    from_duration = task_map[from_task].get("duration", 1)
                    earliest_start[to_task] = max(
                        earliest_start[to_task], earliest_start[from_task] + from_duration
                    )

            # Calculate latest start times (backward pass)
            latest_start = {name: earliest_start[name] for name in task_map}
            max_time = max(earliest_start.values())

            # Identify critical path (tasks with zero slack)
            critical_tasks = []
            for name in task_map:
                slack = latest_start[name] - earliest_start[name]
                if slack == 0:
                    critical_tasks.append(name)

            data = {
                "tasks": list(task_map.keys()),
                "earliest_start": [earliest_start[name] for name in task_map],
                "durations": [task_map[name].get("duration", 1) for name in task_map],
                "critical_tasks": critical_tasks,
                "dependencies": dependencies,
            }

            metadata = {
                "n_tasks": len(tasks),
                "n_dependencies": len(dependencies),
                "n_critical": len(critical_tasks),
                "total_duration": max_time,
            }

            return VisualizationData(
                title="Critical Path Analysis",
                chart_type="gantt",
                data=data,
                metadata=metadata,
            )

    # =========================================================================
    # Risk Assessment
    # =========================================================================

    def risk_heatmap(
        self,
        designs: list[dict[str, Any]],
        risks: list[dict[str, Any]],
    ) -> VisualizationData:
        """
        Create risk heatmap for designs.

        Visualizes risk distribution across different designs.

        Parameters
        ----------
        designs : list[dict[str, Any]]
            Design options.
        risks : list[dict[str, Any]]
            Risk factors with probability and impact.

        Returns
        -------
        VisualizationData
            Risk heatmap visualization.
        """
        with span("decision_support.risk_heatmap", n_designs=len(designs), n_risks=len(risks)):
            # Create risk matrix
            risk_matrix = []
            design_names = []
            risk_names = []

            for design in designs:
                design_name = design.get("name", "unknown")
                design_names.append(design_name)

                design_risks = []
                for risk in risks:
                    # Calculate risk score for this design-risk combination
                    probability = risk.get("probability", 0.5)
                    impact = risk.get("impact", 0.5)

                    # Check if design is vulnerable to this risk
                    vulnerability = 1.0
                    if "vulnerabilities" in design:
                        if risk.get("id") not in design["vulnerabilities"]:
                            vulnerability = 0.3

                    risk_score = probability * impact * vulnerability
                    design_risks.append(risk_score)

            risk_matrix.append(design_risks)

            risk_names = [r.get("name", f"risk_{i}") for i, r in enumerate(risks)]

            data = {
                "designs": design_names,
                "risks": risk_names,
                "matrix": risk_matrix,
            }

            metadata = {
                "n_designs": len(designs),
                "n_risks": len(risks),
                "max_risk": float(np.max(risk_matrix)) if risk_matrix else 0.0,
            }

            return VisualizationData(
                title="Design Risk Heatmap",
                chart_type="heatmap",
                data=data,
                metadata=metadata,
            )

    def failure_mode_visualization(
        self,
        system: dict[str, Any],
    ) -> list[RiskAssessment]:
        """
        Visualize potential failure modes.

        Identifies and assesses potential failure points in a system.

        Parameters
        ----------
        system : dict[str, Any]
            System specification with components.

        Returns
        -------
        list[RiskAssessment]
            Failure mode risk assessments.
        """
        with span("decision_support.failure_mode_visualization"):
            assessments = []

            components = system.get("components", [])

            for component in components:
                # Identify potential failure modes
                failure_modes = component.get("failure_modes", [])

                for mode in failure_modes:
                    probability = mode.get("probability", 0.5)
                    impact = mode.get("impact", 0.5)

                    # Calculate severity
                    risk_score = probability * impact
                    if risk_score >= 0.7:
                        severity = "critical"
                    elif risk_score >= 0.5:
                        severity = "high"
                    elif risk_score >= 0.3:
                        severity = "medium"
                    else:
                        severity = "low"

                    assessments.append(
                        RiskAssessment(
                            risk_name=f"{component.get('name', 'unknown')}: {mode.get('name', 'failure')}",
                            probability=probability,
                            impact=impact,
                            severity=severity,
                            mitigation_strategies=mode.get("mitigations", []),
                            metadata={
                                "component": component.get("name"),
                                "failure_mode": mode.get("name"),
                            },
                        )
                    )

            # Sort by severity
            severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
            assessments.sort(key=lambda a: severity_order.get(a.severity, 4))

            return assessments

    def mitigation_strategy_recommender(
        self,
        risk: RiskAssessment,
    ) -> list[dict[str, Any]]:
        """
        Recommend mitigation strategies for a risk.

        Provides detailed mitigation strategies for identified risks.

        Parameters
        ----------
        risk : RiskAssessment
            Risk to mitigate.

        Returns
        -------
        list[dict[str, Any]]
            Recommended mitigation strategies with details.
        """
        with span("decision_support.mitigation_strategy_recommender"):
            strategies = []

            # Generate strategies based on risk characteristics
            if risk.probability >= 0.7:
                strategies.append(
                    {
                        "type": "prevention",
                        "description": "Implement controls to reduce probability of occurrence",
                        "effectiveness": 0.8,
                        "cost": "medium",
                    }
                )

            if risk.impact >= 0.7:
                strategies.append(
                    {
                        "type": "impact_reduction",
                        "description": "Add redundancy and failover mechanisms",
                        "effectiveness": 0.7,
                        "cost": "high",
                    }
                )

            # Add existing mitigation strategies from risk
            for mitigation in risk.mitigation_strategies:
                strategies.append(
                    {
                        "type": "existing",
                        "description": mitigation,
                        "effectiveness": 0.6,
                        "cost": "low",
                    }
                )

            # Always add monitoring
            strategies.append(
                {
                    "type": "monitoring",
                    "description": "Implement monitoring and alerting for early detection",
                    "effectiveness": 0.5,
                    "cost": "low",
                }
            )

            return strategies
