"""
specify_cli.hyperdimensional.analytics - Analytics & Insights Engine
===================================================================

Analytics and insights module with predictive analytics, anomaly detection, and trend analysis.

This module provides analytics capabilities for:
* **System Metrics**: Quality trends, feature adoption, outcome delivery
* **Predictive Analytics**: Success prediction, effort estimation, achievement forecasting
* **Anomaly Detection**: Specification anomalies, code generation issues, architectural violations

Examples
--------
    >>> from specify_cli.hyperdimensional.analytics import AnalyticsEngine
    >>>
    >>> analytics = AnalyticsEngine()
    >>> trends = analytics.specification_quality_trends(time_period="30d")
    >>> prediction = analytics.predict_feature_success(feature)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

import numpy as np

from specify_cli.core.telemetry import span
from specify_cli.hyperdimensional.dashboards import VisualizationData

__all__ = [
    "AnalyticsEngine",
    "Anomaly",
    "Prediction",
    "TrendAnalysis",
]


@dataclass
class TrendAnalysis:
    """Trend analysis data structure."""

    metric_name: str
    trend: str  # "improving", "declining", "stable"
    slope: float
    confidence: float
    data_points: list[tuple[str, float]]  # (timestamp, value) pairs
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Prediction:
    """Prediction data structure."""

    target_name: str
    predicted_value: float
    confidence: float
    confidence_interval: tuple[float, float]  # (lower, upper)
    features_used: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Anomaly:
    """Anomaly data structure."""

    anomaly_type: str
    severity: str  # "low", "medium", "high"
    description: str
    detected_at: str
    anomaly_score: float
    expected_range: tuple[float, float]
    actual_value: float
    metadata: dict[str, Any] = field(default_factory=dict)


class AnalyticsEngine:
    """
    Analytics and insights engine for hyperdimensional systems.

    This class provides trend analysis, predictive analytics, and
    anomaly detection for specifications, code, and system metrics.

    Attributes
    ----------
    history_window : int
        Number of historical data points to consider for trends.
    anomaly_threshold : float
        Threshold for anomaly detection (standard deviations).
    """

    def __init__(
        self,
        history_window: int = 30,
        anomaly_threshold: float = 2.5,
    ) -> None:
        """
        Initialize analytics engine.

        Parameters
        ----------
        history_window : int, optional
            Historical window size. Default is 30.
        anomaly_threshold : float, optional
            Anomaly detection threshold. Default is 2.5.
        """
        self.history_window = history_window
        self.anomaly_threshold = anomaly_threshold

    # =========================================================================
    # System Metrics
    # =========================================================================

    def specification_quality_trends(
        self,
        spec_history: list[dict[str, Any]],
        time_period: str = "30d",
    ) -> TrendAnalysis:
        """
        Analyze specification quality trends over time.

        Tracks how specification quality evolves and identifies trends.

        Parameters
        ----------
        spec_history : list[dict[str, Any]]
            Historical specification data with timestamps.
        time_period : str, optional
            Time period to analyze (e.g., "30d", "90d"). Default is "30d".

        Returns
        -------
        TrendAnalysis
            Quality trend analysis.
        """
        with span("analytics.specification_quality_trends", period=time_period):
            # Filter by time period
            cutoff_date = self._parse_time_period(time_period)
            filtered_history = [
                s
                for s in spec_history
                if datetime.fromisoformat(s.get("timestamp", "1970-01-01")) >= cutoff_date
            ]

            # Extract quality scores over time
            data_points = []
            for spec in filtered_history:
                timestamp = spec.get("timestamp", "unknown")
                quality = self._calculate_quality_score(spec)
                data_points.append((timestamp, quality))

            # Sort by timestamp
            data_points.sort(key=lambda x: x[0])

            # Calculate trend
            if len(data_points) < 2:
                return TrendAnalysis(
                    metric_name="specification_quality",
                    trend="stable",
                    slope=0.0,
                    confidence=0.0,
                    data_points=data_points,
                )

            # Linear regression
            x = np.arange(len(data_points))
            y = np.array([dp[1] for dp in data_points])

            slope, intercept = np.polyfit(x, y, 1)

            # Determine trend direction
            if abs(slope) < 0.01:
                trend = "stable"
            elif slope > 0:
                trend = "improving"
            else:
                trend = "declining"

            # Calculate confidence (R²)
            y_pred = slope * x + intercept
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

            return TrendAnalysis(
                metric_name="specification_quality",
                trend=trend,
                slope=float(slope),
                confidence=float(r_squared),
                data_points=data_points,
                metadata={
                    "n_data_points": len(data_points),
                    "time_period": time_period,
                },
            )

    def _parse_time_period(self, period: str) -> datetime:
        """Parse time period string to datetime."""
        now = datetime.now()

        if period.endswith("d"):
            days = int(period[:-1])
            return now - timedelta(days=days)
        if period.endswith("w"):
            weeks = int(period[:-1])
            return now - timedelta(weeks=weeks)
        if period.endswith("m"):
            months = int(period[:-1])
            return now - timedelta(days=months * 30)
        return now - timedelta(days=30)

    def _calculate_quality_score(self, spec: dict[str, Any]) -> float:
        """Calculate overall quality score for a specification."""
        completeness = self._check_completeness(spec)
        clarity = self._check_clarity(spec)
        consistency = 0.8  # Placeholder

        return (completeness + clarity + consistency) / 3.0

    def _check_completeness(self, spec: dict[str, Any]) -> float:
        """Check specification completeness."""
        required_sections = {"overview", "requirements", "constraints", "acceptance_criteria"}
        present_sections = set(spec.keys())
        return len(present_sections & required_sections) / len(required_sections)

    def _check_clarity(self, spec: dict[str, Any]) -> float:
        """Check specification clarity."""
        text = spec.get("text", "")
        if not text:
            return 0.0

        # Simple clarity metric: average sentence length
        sentences = text.split(".")
        if not sentences:
            return 0.0

        avg_sentence_length = len(text) / len(sentences)
        # Optimal sentence length: 15-25 words
        if 15 <= avg_sentence_length <= 25:
            return 1.0
        if avg_sentence_length < 15:
            return 0.7
        return max(0.0, 1.0 - (avg_sentence_length - 25) / 50)

    def feature_adoption_analytics(
        self,
        features: list[dict[str, Any]],
        time_period: str = "30d",
    ) -> VisualizationData:
        """
        Analyze feature adoption patterns over time.

        Tracks which features are being adopted and usage patterns.

        Parameters
        ----------
        features : list[dict[str, Any]]
            Features with usage data.
        time_period : str, optional
            Time period to analyze. Default is "30d".

        Returns
        -------
        VisualizationData
            Feature adoption visualization.
        """
        with span("analytics.feature_adoption", period=time_period):
            # Filter by time period
            cutoff_date = self._parse_time_period(time_period)

            adoption_data = []
            for feature in features:
                usage_history = feature.get("usage_history", [])

                # Filter by time period
                recent_usage = [
                    u
                    for u in usage_history
                    if datetime.fromisoformat(u.get("timestamp", "1970-01-01")) >= cutoff_date
                ]

                adoption_data.append(
                    {
                        "feature": feature.get("name", "unknown"),
                        "usage_count": len(recent_usage),
                        "unique_users": len({u.get("user_id") for u in recent_usage}),
                    }
                )

            # Sort by usage
            adoption_data.sort(key=lambda x: x["usage_count"], reverse=True)

            data = {
                "features": [a["feature"] for a in adoption_data],
                "usage_counts": [a["usage_count"] for a in adoption_data],
                "unique_users": [a["unique_users"] for a in adoption_data],
            }

            metadata = {
                "time_period": time_period,
                "n_features": len(features),
                "total_usage": sum(a["usage_count"] for a in adoption_data),
            }

            return VisualizationData(
                title=f"Feature Adoption ({time_period})",
                chart_type="bar",
                data=data,
                metadata=metadata,
            )

    def outcome_delivery_analytics(
        self,
        outcomes: list[dict[str, Any]],
        time_period: str = "30d",
    ) -> VisualizationData:
        """
        Analyze outcome delivery trends.

        Tracks successful outcome delivery over time.

        Parameters
        ----------
        outcomes : list[dict[str, Any]]
            Outcomes with delivery data.
        time_period : str, optional
            Time period to analyze. Default is "30d".

        Returns
        -------
        VisualizationData
            Outcome delivery trends.
        """
        with span("analytics.outcome_delivery", period=time_period):
            cutoff_date = self._parse_time_period(time_period)

            # Group outcomes by timestamp
            delivery_by_date: dict[str, list[bool]] = {}

            for outcome in outcomes:
                timestamp = outcome.get("timestamp", "")
                if not timestamp:
                    continue

                date = datetime.fromisoformat(timestamp)
                if date < cutoff_date:
                    continue

                date_key = date.strftime("%Y-%m-%d")
                if date_key not in delivery_by_date:
                    delivery_by_date[date_key] = []

                delivered = outcome.get("status") == "delivered"
                delivery_by_date[date_key].append(delivered)

            # Calculate delivery rates
            dates = sorted(delivery_by_date.keys())
            delivery_rates = [
                sum(delivery_by_date[date]) / len(delivery_by_date[date]) for date in dates
            ]

            data = {
                "dates": dates,
                "delivery_rates": delivery_rates,
            }

            metadata = {
                "time_period": time_period,
                "n_outcomes": len(outcomes),
                "avg_delivery_rate": float(np.mean(delivery_rates)) if delivery_rates else 0.0,
            }

            return VisualizationData(
                title=f"Outcome Delivery Trends ({time_period})",
                chart_type="line",
                data=data,
                metadata=metadata,
            )

    def customer_satisfaction_analytics(
        self,
        surveys: list[dict[str, Any]],
        time_period: str = "30d",
    ) -> VisualizationData:
        """
        Analyze customer satisfaction trends.

        Tracks satisfaction scores and sentiment over time.

        Parameters
        ----------
        surveys : list[dict[str, Any]]
            Customer satisfaction surveys.
        time_period : str, optional
            Time period to analyze. Default is "30d".

        Returns
        -------
        VisualizationData
            Satisfaction trends.
        """
        with span("analytics.customer_satisfaction", period=time_period):
            cutoff_date = self._parse_time_period(time_period)

            # Filter surveys by time period
            recent_surveys = [
                s
                for s in surveys
                if datetime.fromisoformat(s.get("timestamp", "1970-01-01")) >= cutoff_date
            ]

            # Group by date
            satisfaction_by_date: dict[str, list[float]] = {}

            for survey in recent_surveys:
                timestamp = survey.get("timestamp", "")
                date_key = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d")

                if date_key not in satisfaction_by_date:
                    satisfaction_by_date[date_key] = []

                rating = survey.get("rating", 0.0)
                satisfaction_by_date[date_key].append(rating)

            # Calculate averages
            dates = sorted(satisfaction_by_date.keys())
            avg_ratings = [float(np.mean(satisfaction_by_date[date])) for date in dates]

            data = {
                "dates": dates,
                "ratings": avg_ratings,
            }

            metadata = {
                "time_period": time_period,
                "n_surveys": len(recent_surveys),
                "avg_rating": float(np.mean(avg_ratings)) if avg_ratings else 0.0,
            }

            return VisualizationData(
                title=f"Customer Satisfaction Trends ({time_period})",
                chart_type="line",
                data=data,
                metadata=metadata,
            )

    # =========================================================================
    # Predictive Analytics
    # =========================================================================

    def predict_feature_success(
        self,
        feature: dict[str, Any],
        historical_features: list[dict[str, Any]] | None = None,
    ) -> Prediction:
        """
        Predict feature success probability.

        Uses historical data to predict likelihood of feature success.

        Parameters
        ----------
        feature : dict[str, Any]
            Feature to predict success for.
        historical_features : list[dict[str, Any]], optional
            Historical features for training.

        Returns
        -------
        Prediction
            Success probability prediction.
        """
        with span("analytics.predict_feature_success"):
            # Extract features for prediction
            complexity = feature.get("complexity", 0.5)
            team_experience = feature.get("team_experience", 0.5)
            requirement_clarity = feature.get("requirement_clarity", 0.5)
            stakeholder_alignment = feature.get("stakeholder_alignment", 0.5)

            # Simple heuristic model (in production, use ML model)
            success_score = (
                0.2 * (1.0 - complexity)  # Lower complexity = higher success
                + 0.3 * team_experience
                + 0.3 * requirement_clarity
                + 0.2 * stakeholder_alignment
            )

            # Calculate confidence based on data availability
            available_features = sum(
                [
                    complexity != 0.5,
                    team_experience != 0.5,
                    requirement_clarity != 0.5,
                    stakeholder_alignment != 0.5,
                ]
            )
            confidence = available_features / 4.0

            # Calculate confidence interval
            margin = 0.15 * (1.0 - confidence)
            ci_lower = max(0.0, success_score - margin)
            ci_upper = min(1.0, success_score + margin)

            return Prediction(
                target_name=feature.get("name", "unknown"),
                predicted_value=success_score,
                confidence=confidence,
                confidence_interval=(ci_lower, ci_upper),
                features_used=[
                    "complexity",
                    "team_experience",
                    "requirement_clarity",
                    "stakeholder_alignment",
                ],
                metadata={"feature_id": feature.get("id")},
            )

    def estimate_development_effort(
        self,
        feature: dict[str, Any],
        historical_features: list[dict[str, Any]] | None = None,
    ) -> Prediction:
        """
        Estimate development effort for a feature.

        Predicts time/resources required based on feature characteristics.

        Parameters
        ----------
        feature : dict[str, Any]
            Feature to estimate.
        historical_features : list[dict[str, Any]], optional
            Historical features for calibration.

        Returns
        -------
        Prediction
            Effort estimation in person-days.
        """
        with span("analytics.estimate_development_effort"):
            # Extract feature characteristics
            complexity = feature.get("complexity", 0.5)
            num_requirements = len(feature.get("requirements", []))
            num_dependencies = len(feature.get("dependencies", []))
            is_novel = feature.get("is_novel", False)

            # Simple effort model (in production, use ML model trained on historical data)
            base_effort = 5.0  # days
            effort = base_effort * (
                1.0
                + complexity * 2.0
                + num_requirements * 0.5
                + num_dependencies * 0.3
                + (1.0 if is_novel else 0.0)
            )

            # Calculate confidence
            if historical_features and len(historical_features) >= 10:
                confidence = 0.8
            elif historical_features:
                confidence = 0.6
            else:
                confidence = 0.4

            # Confidence interval
            margin = effort * 0.3 * (1.0 - confidence)
            ci_lower = max(1.0, effort - margin)
            ci_upper = effort + margin

            return Prediction(
                target_name=feature.get("name", "unknown"),
                predicted_value=effort,
                confidence=confidence,
                confidence_interval=(ci_lower, ci_upper),
                features_used=["complexity", "num_requirements", "num_dependencies", "is_novel"],
                metadata={
                    "feature_id": feature.get("id"),
                    "unit": "person-days",
                },
            )

    def forecast_outcome_achievement(
        self,
        feature: dict[str, Any],
        timeline: int = 30,
    ) -> Prediction:
        """
        Forecast outcome achievement probability.

        Predicts likelihood of achieving intended outcomes within timeline.

        Parameters
        ----------
        feature : dict[str, Any]
            Feature with target outcomes.
        timeline : int, optional
            Timeline in days. Default is 30.

        Returns
        -------
        Prediction
            Achievement probability forecast.
        """
        with span("analytics.forecast_outcome_achievement", timeline=timeline):
            # Extract factors
            feature_maturity = feature.get("maturity", 0.5)
            team_capacity = feature.get("team_capacity", 0.5)
            risk_level = feature.get("risk_level", 0.5)
            complexity = feature.get("complexity", 0.5)

            # Timeline factor (longer timeline = higher probability)
            timeline_factor = min(1.0, timeline / 60.0)

            # Achievement probability
            achievement_prob = (
                0.25 * feature_maturity
                + 0.25 * team_capacity
                + 0.25 * (1.0 - risk_level)
                + 0.15 * (1.0 - complexity)
                + 0.10 * timeline_factor
            )

            confidence = 0.7

            margin = 0.15
            ci_lower = max(0.0, achievement_prob - margin)
            ci_upper = min(1.0, achievement_prob + margin)

            return Prediction(
                target_name=f"outcome_achievement_{feature.get('name', 'unknown')}",
                predicted_value=achievement_prob,
                confidence=confidence,
                confidence_interval=(ci_lower, ci_upper),
                features_used=[
                    "feature_maturity",
                    "team_capacity",
                    "risk_level",
                    "complexity",
                    "timeline",
                ],
                metadata={
                    "feature_id": feature.get("id"),
                    "timeline_days": timeline,
                },
            )

    # =========================================================================
    # Anomaly Detection
    # =========================================================================

    def detect_specification_anomalies(
        self,
        specs: list[dict[str, Any]],
    ) -> list[Anomaly]:
        """
        Detect anomalies in specifications.

        Identifies specifications with unusual patterns or characteristics.

        Parameters
        ----------
        specs : list[dict[str, Any]]
            Specifications to analyze.

        Returns
        -------
        list[Anomaly]
            Detected anomalies.
        """
        with span("analytics.detect_specification_anomalies", n_specs=len(specs)):
            anomalies = []

            # Calculate quality metrics
            quality_scores = [self._calculate_quality_score(s) for s in specs]

            if not quality_scores:
                return anomalies

            # Calculate statistics
            mean_quality = np.mean(quality_scores)
            std_quality = np.std(quality_scores)

            # Detect outliers
            for idx, (spec, quality) in enumerate(zip(specs, quality_scores, strict=False)):
                if std_quality > 0:
                    z_score = abs(quality - mean_quality) / std_quality

                    if z_score > self.anomaly_threshold:
                        severity = "high" if z_score > 3.0 else "medium"

                        anomalies.append(
                            Anomaly(
                                anomaly_type="specification_quality",
                                severity=severity,
                                description=f"Specification quality is {z_score:.1f} std devs from mean",
                                detected_at=datetime.now().isoformat(),
                                anomaly_score=float(z_score),
                                expected_range=(
                                    mean_quality - 2 * std_quality,
                                    mean_quality + 2 * std_quality,
                                ),
                                actual_value=quality,
                                metadata={
                                    "spec_id": spec.get("id", idx),
                                    "spec_name": spec.get("name", "unknown"),
                                },
                            )
                        )

            return anomalies

    def identify_code_generation_anomalies(
        self,
        generations: list[dict[str, Any]],
    ) -> list[Anomaly]:
        """
        Identify anomalies in code generation quality.

        Detects unusual drops in code generation fidelity.

        Parameters
        ----------
        generations : list[dict[str, Any]]
            Code generations to analyze.

        Returns
        -------
        list[Anomaly]
            Detected anomalies.
        """
        with span("analytics.identify_code_generation_anomalies", n_generations=len(generations)):
            anomalies = []

            # Calculate fidelity scores
            fidelity_scores = []
            for gen in generations:
                spec = gen.get("spec", {})
                code = gen.get("code", {})

                requirements = spec.get("requirements", [])
                if isinstance(requirements, str):
                    requirements = [r.strip() for r in requirements.split("\n") if r.strip()]

                code_text = code.get("text", "")
                implemented = sum(
                    1
                    for req in requirements
                    if any(kw in code_text.lower() for kw in req.lower().split())
                )

                fidelity = implemented / len(requirements) if requirements else 0.0
                fidelity_scores.append(fidelity)

            if not fidelity_scores:
                return anomalies

            # Detect anomalies
            mean_fidelity = np.mean(fidelity_scores)
            std_fidelity = np.std(fidelity_scores)

            for idx, (gen, fidelity) in enumerate(zip(generations, fidelity_scores, strict=False)):
                if std_fidelity > 0:
                    z_score = abs(fidelity - mean_fidelity) / std_fidelity

                    if z_score > self.anomaly_threshold and fidelity < mean_fidelity:
                        severity = "high" if fidelity < 0.5 else "medium"

                        anomalies.append(
                            Anomaly(
                                anomaly_type="code_generation_fidelity",
                                severity=severity,
                                description=f"Code fidelity significantly below expected ({fidelity:.2f})",
                                detected_at=datetime.now().isoformat(),
                                anomaly_score=float(z_score),
                                expected_range=(
                                    mean_fidelity - 2 * std_fidelity,
                                    mean_fidelity + 2 * std_fidelity,
                                ),
                                actual_value=fidelity,
                                metadata={
                                    "generation_id": gen.get("id", idx),
                                },
                            )
                        )

            return anomalies

    def flag_architectural_anomalies(
        self,
        codebase: dict[str, Any],
    ) -> list[Anomaly]:
        """
        Flag architectural constraint violations.

        Identifies violations of architectural patterns and constraints.

        Parameters
        ----------
        codebase : dict[str, Any]
            Codebase structure and metrics.

        Returns
        -------
        list[Anomaly]
            Architectural anomalies.
        """
        with span("analytics.flag_architectural_anomalies"):
            anomalies = []

            # Check layer violations
            layer_violations = codebase.get("layer_violations", 0)
            if layer_violations > 0:
                anomalies.append(
                    Anomaly(
                        anomaly_type="layer_separation",
                        severity="high" if layer_violations > 5 else "medium",
                        description=f"Detected {layer_violations} layer separation violations",
                        detected_at=datetime.now().isoformat(),
                        anomaly_score=float(layer_violations),
                        expected_range=(0, 0),
                        actual_value=float(layer_violations),
                        metadata={"violation_count": layer_violations},
                    )
                )

            # Check module size
            oversized_modules = codebase.get("oversized_modules", [])
            if oversized_modules:
                anomalies.append(
                    Anomaly(
                        anomaly_type="module_size",
                        severity="medium",
                        description=f"{len(oversized_modules)} modules exceed size limits",
                        detected_at=datetime.now().isoformat(),
                        anomaly_score=float(len(oversized_modules)),
                        expected_range=(0, 0),
                        actual_value=float(len(oversized_modules)),
                        metadata={"oversized_modules": oversized_modules},
                    )
                )

            return anomalies
