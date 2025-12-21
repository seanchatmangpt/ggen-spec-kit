"""Query result types for HDQL.

This module defines result types returned by query execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Entity:
    """Entity in the knowledge graph."""

    entity_type: str  # command, job, feature, outcome, constraint
    name: str
    description: str
    attributes: dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        """String representation."""
        return f"{self.entity_type}({self.name!r})"


@dataclass(frozen=True)
class EntityMatch:
    """Single matching entity from query."""

    entity: Entity
    distance: float
    similarity: float
    explanation: str

    @property
    def score(self) -> float:
        """Normalized score (higher is better)."""
        return self.similarity

    def __repr__(self) -> str:
        """String representation."""
        return f"EntityMatch({self.entity.name}, score={self.score:.3f})"


@dataclass(frozen=True)
class ReasoningTrace:
    """Trace of reasoning steps in query execution."""

    steps: tuple[str, ...]
    intermediate_results: dict[str, Any]
    execution_plan: str

    def explain(self) -> str:
        """Generate human-readable explanation."""
        lines = ["Query Execution Trace:", ""]
        for i, step in enumerate(self.steps, 1):
            lines.append(f"{i}. {step}")

        if self.intermediate_results:
            lines.append("")
            lines.append("Intermediate Results:")
            for key, value in self.intermediate_results.items():
                lines.append(f"  {key}: {value}")

        return "\n".join(lines)


@dataclass(frozen=True)
class VectorQueryResult:
    """Result of vector-based query."""

    matching_entities: tuple[EntityMatch, ...]
    confidence_scores: tuple[float, ...]
    reasoning_trace: ReasoningTrace
    execution_time_ms: float

    def top_k(self, k: int) -> list[EntityMatch]:
        """Return top K results by score."""
        return sorted(self.matching_entities, key=lambda m: m.score, reverse=True)[:k]

    def filter_by_confidence(self, threshold: float) -> VectorQueryResult:
        """Filter results by confidence threshold."""
        filtered = [
            m
            for m, c in zip(self.matching_entities, self.confidence_scores, strict=False)
            if c >= threshold
        ]
        filtered_confidence = [c for c in self.confidence_scores if c >= threshold]

        return VectorQueryResult(
            matching_entities=tuple(filtered),
            confidence_scores=tuple(filtered_confidence),
            reasoning_trace=self.reasoning_trace,
            execution_time_ms=self.execution_time_ms,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "matches": [
                {
                    "entity": {
                        "type": m.entity.entity_type,
                        "name": m.entity.name,
                        "description": m.entity.description,
                        "attributes": m.entity.attributes,
                    },
                    "score": m.score,
                    "distance": m.distance,
                    "explanation": m.explanation,
                }
                for m in self.matching_entities
            ],
            "confidence_scores": list(self.confidence_scores),
            "execution_time_ms": self.execution_time_ms,
            "reasoning": {
                "steps": list(self.reasoning_trace.steps),
                "execution_plan": self.reasoning_trace.execution_plan,
            },
        }


@dataclass(frozen=True)
class Recommendation:
    """Single recommendation from optimization query."""

    entity: Entity
    score: float
    rationale: str
    metrics: dict[str, float]

    def __repr__(self) -> str:
        """String representation."""
        return f"Recommendation({self.entity.name}, score={self.score:.3f})"


@dataclass(frozen=True)
class Alternative:
    """Alternative option in recommendation."""

    entity: Entity
    score: float
    trade_offs: str

    def __repr__(self) -> str:
        """String representation."""
        return f"Alternative({self.entity.name}, score={self.score:.3f})"


@dataclass(frozen=True)
class TradeOffAnalysis:
    """Analysis of trade-offs in recommendations."""

    summary: str
    pareto_frontier: tuple[Entity, ...]
    dominated_options: tuple[Entity, ...]

    def __repr__(self) -> str:
        """String representation."""
        return f"TradeOffAnalysis({len(self.pareto_frontier)} Pareto optimal)"


@dataclass(frozen=True)
class RecommendationResult:
    """Result of optimization/recommendation query."""

    top_k_recommendations: tuple[Recommendation, ...]
    trade_offs: TradeOffAnalysis
    alternative_options: tuple[Alternative, ...]
    objective_value: float

    def explain(self) -> str:
        """Generate human-readable explanation."""
        if not self.top_k_recommendations:
            return "No recommendations found."

        top = self.top_k_recommendations[0]

        lines = [
            f"Top Recommendation: {top.entity.name}",
            f"Score: {top.score:.3f}",
            "",
            "Why this recommendation:",
            top.rationale,
            "",
            "Trade-offs:",
            self.trade_offs.summary,
            "",
            "Alternatives considered:",
        ]

        for alt in self.alternative_options[:5]:
            lines.append(f"  - {alt.entity.name} (score={alt.score:.3f})")

        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "recommendations": [
                {
                    "entity": {
                        "type": r.entity.entity_type,
                        "name": r.entity.name,
                        "description": r.entity.description,
                    },
                    "score": r.score,
                    "rationale": r.rationale,
                    "metrics": r.metrics,
                }
                for r in self.top_k_recommendations
            ],
            "trade_offs": {
                "summary": self.trade_offs.summary,
                "pareto_frontier": [e.name for e in self.trade_offs.pareto_frontier],
                "dominated": [e.name for e in self.trade_offs.dominated_options],
            },
            "alternatives": [
                {
                    "entity": a.entity.name,
                    "score": a.score,
                    "trade_offs": a.trade_offs,
                }
                for a in self.alternative_options
            ],
            "objective_value": self.objective_value,
        }


@dataclass(frozen=True)
class Gap:
    """Identified gap in coverage or capability."""

    gap_type: str  # coverage, capability, performance
    description: str
    severity: str  # critical, high, medium, low
    affected_entities: tuple[Entity, ...]
    suggested_actions: tuple[str, ...]

    def __repr__(self) -> str:
        """String representation."""
        return f"Gap({self.gap_type}, severity={self.severity}, entities={len(self.affected_entities)})"


@dataclass(frozen=True)
class Opportunity:
    """Identified improvement opportunity."""

    opportunity_type: str
    description: str
    potential_value: float
    implementation_effort: float

    @property
    def roi_score(self) -> float:
        """Calculate ROI score."""
        if self.implementation_effort == 0:
            return float("inf")
        return self.potential_value / self.implementation_effort

    def __repr__(self) -> str:
        """String representation."""
        return f"Opportunity({self.opportunity_type}, ROI={self.roi_score:.2f})"


@dataclass(frozen=True)
class AnalysisResult:
    """Result of analytical query."""

    metrics: dict[str, float]
    gaps_identified: tuple[Gap, ...]
    opportunities: tuple[Opportunity, ...]
    insights: tuple[str, ...]

    def summary_report(self) -> str:
        """Generate summary report."""
        lines = [
            "ANALYSIS SUMMARY",
            "=" * 80,
            "",
            "Key Metrics:",
        ]

        for metric, value in self.metrics.items():
            lines.append(f"  {metric}: {value:.3f}")

        lines.extend(["", f"Gaps Identified ({len(self.gaps_identified)}):"])
        for gap in self.gaps_identified:
            lines.append(f"  [{gap.severity.upper()}] {gap.description}")

        lines.extend(["", f"Opportunities ({len(self.opportunities)}):"])
        for opp in sorted(self.opportunities, key=lambda o: o.roi_score, reverse=True):
            lines.append(
                f"  {opp.description} (ROI={opp.roi_score:.2f}, "
                f"value={opp.potential_value:.1f}, effort={opp.implementation_effort:.1f})"
            )

        lines.extend(["", "Key Insights:"])
        for insight in self.insights:
            lines.append(f"  - {insight}")

        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "metrics": self.metrics,
            "gaps": [
                {
                    "type": g.gap_type,
                    "description": g.description,
                    "severity": g.severity,
                    "affected_entities": [e.name for e in g.affected_entities],
                    "suggested_actions": list(g.suggested_actions),
                }
                for g in self.gaps_identified
            ],
            "opportunities": [
                {
                    "type": o.opportunity_type,
                    "description": o.description,
                    "potential_value": o.potential_value,
                    "implementation_effort": o.implementation_effort,
                    "roi_score": o.roi_score,
                }
                for o in self.opportunities
            ],
            "insights": list(self.insights),
        }
