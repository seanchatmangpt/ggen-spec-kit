"""
specify_cli.hyperdimensional.dashboards - Dashboard Framework
=============================================================

Comprehensive dashboard framework with semantic space visualization, information metrics,
quality metrics, and JTBD outcome tracking.

This module provides visualization and dashboard capabilities for:
* **Semantic Space Visualization**: PCA/t-SNE projections, similarity graphs
* **Information Metrics**: Entropy distribution, mutual information, information gain
* **Quality Metrics**: Specification completeness, code fidelity, architecture compliance
* **JTBD Outcome Metrics**: Outcome delivery, job coverage, customer satisfaction

Examples
--------
    >>> from specify_cli.hyperdimensional.dashboards import DashboardFramework
    >>>
    >>> dashboard = DashboardFramework()
    >>> dashboard.plot_semantic_space_2d(embeddings, labels=["feature1", "feature2"])
    >>> dashboard.entropy_distribution(specifications)
    >>> dashboard.specification_completeness_tracker(spec_history)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np

from specify_cli.core.telemetry import span

if TYPE_CHECKING:
    from numpy.typing import NDArray

__all__ = [
    "DashboardFramework",
    "JTBDMetrics",
    "MetricData",
    "QualityMetrics",
    "VisualizationData",
]


@dataclass
class VisualizationData:
    """Data structure for visualization outputs."""

    title: str
    chart_type: str  # "scatter", "heatmap", "line", "bar", "histogram"
    data: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricData:
    """Data structure for metric values."""

    name: str
    value: float
    unit: str = ""
    threshold: float | None = None
    status: str = "ok"  # "ok", "warning", "critical"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityMetrics:
    """Quality metrics data structure."""

    completeness: float  # 0.0 to 1.0
    fidelity: float  # 0.0 to 1.0
    compliance: float  # 0.0 to 1.0
    test_coverage: float  # 0.0 to 1.0
    timestamp: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class JTBDMetrics:
    """Jobs-to-be-Done metrics data structure."""

    outcome_delivery_rate: float  # 0.0 to 1.0
    job_coverage: float  # 0.0 to 1.0
    customer_satisfaction: float  # 0.0 to 5.0
    feature_roi: float  # Ratio of benefits to costs
    timestamp: str
    metadata: dict[str, Any] = field(default_factory=dict)


class DashboardFramework:
    """
    Comprehensive dashboard framework for hyperdimensional observability.

    This class provides visualization and dashboard capabilities for semantic spaces,
    information metrics, quality tracking, and JTBD outcome analysis.

    Attributes
    ----------
    visualization_backend : str
        Visualization backend to use ("matplotlib", "plotly", "data_only").
    enable_interactive : bool
        Enable interactive visualizations (requires plotly).
    output_format : str
        Output format for visualizations ("png", "svg", "html", "json").
    """

    def __init__(
        self,
        visualization_backend: str = "data_only",
        enable_interactive: bool = False,
        output_format: str = "json",
    ) -> None:
        """
        Initialize dashboard framework.

        Parameters
        ----------
        visualization_backend : str, optional
            Visualization backend to use. Default is "data_only".
        enable_interactive : bool, optional
            Enable interactive visualizations. Default is False.
        output_format : str, optional
            Output format for visualizations. Default is "json".
        """
        self.visualization_backend = visualization_backend
        self.enable_interactive = enable_interactive
        self.output_format = output_format

    # =========================================================================
    # Semantic Space Visualization
    # =========================================================================

    def plot_semantic_space_2d(
        self,
        embeddings: NDArray[np.float64],
        labels: list[str] | None = None,
        method: str = "pca",
    ) -> VisualizationData:
        """
        Create 2D projection visualization of semantic space.

        Uses PCA or t-SNE to project high-dimensional embeddings to 2D space
        for visualization.

        Parameters
        ----------
        embeddings : NDArray[np.float64]
            High-dimensional embeddings matrix (n_samples, n_dimensions).
        labels : list[str], optional
            Labels for each embedding point.
        method : str, optional
            Dimensionality reduction method ("pca" or "tsne"). Default is "pca".

        Returns
        -------
        VisualizationData
            2D projection visualization data.
        """
        with span("dashboard.plot_semantic_space_2d", method=method):
            # Import dimensionality reduction
            from sklearn.decomposition import PCA

            # Perform dimensionality reduction
            if method == "pca":
                reducer = PCA(n_components=2, random_state=42)
                coords = reducer.fit_transform(embeddings)
                variance = reducer.explained_variance_ratio_
            elif method == "tsne":
                from sklearn.manifold import TSNE

                reducer = TSNE(
                    n_components=2, random_state=42, perplexity=min(30, len(embeddings) - 1)
                )
                coords = reducer.fit_transform(embeddings)
                variance = [0.0, 0.0]  # t-SNE doesn't provide variance
            else:
                raise ValueError(f"Unknown method: {method}")

            # Create visualization data
            data = {
                "x": coords[:, 0].tolist(),
                "y": coords[:, 1].tolist(),
                "labels": labels if labels else [f"point_{i}" for i in range(len(embeddings))],
            }

            metadata = {
                "method": method,
                "n_samples": len(embeddings),
                "n_dimensions": embeddings.shape[1],
                "explained_variance": variance.tolist()
                if isinstance(variance, np.ndarray)
                else variance,
            }

            return VisualizationData(
                title=f"Semantic Space 2D Projection ({method.upper()})",
                chart_type="scatter",
                data=data,
                metadata=metadata,
            )

    def plot_semantic_space_3d(
        self,
        embeddings: NDArray[np.float64],
        labels: list[str] | None = None,
        method: str = "pca",
    ) -> VisualizationData:
        """
        Create 3D projection visualization of semantic space.

        Uses PCA or t-SNE to project high-dimensional embeddings to 3D space
        for interactive visualization.

        Parameters
        ----------
        embeddings : NDArray[np.float64]
            High-dimensional embeddings matrix (n_samples, n_dimensions).
        labels : list[str], optional
            Labels for each embedding point.
        method : str, optional
            Dimensionality reduction method ("pca" or "tsne"). Default is "pca".

        Returns
        -------
        VisualizationData
            3D projection visualization data.
        """
        with span("dashboard.plot_semantic_space_3d", method=method):
            from sklearn.decomposition import PCA

            if method == "pca":
                reducer = PCA(n_components=3, random_state=42)
                coords = reducer.fit_transform(embeddings)
                variance = reducer.explained_variance_ratio_
            elif method == "tsne":
                from sklearn.manifold import TSNE

                reducer = TSNE(
                    n_components=3, random_state=42, perplexity=min(30, len(embeddings) - 1)
                )
                coords = reducer.fit_transform(embeddings)
                variance = [0.0, 0.0, 0.0]
            else:
                raise ValueError(f"Unknown method: {method}")

            data = {
                "x": coords[:, 0].tolist(),
                "y": coords[:, 1].tolist(),
                "z": coords[:, 2].tolist(),
                "labels": labels if labels else [f"point_{i}" for i in range(len(embeddings))],
            }

            metadata = {
                "method": method,
                "n_samples": len(embeddings),
                "n_dimensions": embeddings.shape[1],
                "explained_variance": variance.tolist()
                if isinstance(variance, np.ndarray)
                else variance,
            }

            return VisualizationData(
                title=f"Semantic Space 3D Projection ({method.upper()})",
                chart_type="scatter3d",
                data=data,
                metadata=metadata,
            )

    def highlight_concept_cluster(
        self,
        embeddings: NDArray[np.float64],
        concept_indices: list[int],
        labels: list[str] | None = None,
    ) -> VisualizationData:
        """
        Highlight a concept cluster in semantic space.

        Creates a 2D visualization with specific concepts highlighted to show
        related concepts and their clustering.

        Parameters
        ----------
        embeddings : NDArray[np.float64]
            High-dimensional embeddings matrix.
        concept_indices : list[int]
            Indices of concepts to highlight.
        labels : list[str], optional
            Labels for each embedding point.

        Returns
        -------
        VisualizationData
            Concept cluster visualization data.
        """
        with span("dashboard.highlight_concept_cluster", n_concepts=len(concept_indices)):
            from sklearn.decomposition import PCA

            reducer = PCA(n_components=2, random_state=42)
            coords = reducer.fit_transform(embeddings)

            # Create highlight markers
            highlight = [i in concept_indices for i in range(len(embeddings))]

            data = {
                "x": coords[:, 0].tolist(),
                "y": coords[:, 1].tolist(),
                "labels": labels if labels else [f"point_{i}" for i in range(len(embeddings))],
                "highlight": highlight,
            }

            metadata = {
                "n_highlighted": len(concept_indices),
                "highlighted_indices": concept_indices,
            }

            return VisualizationData(
                title="Concept Cluster Visualization",
                chart_type="scatter",
                data=data,
                metadata=metadata,
            )

    def show_similarity_graph(
        self,
        embeddings: NDArray[np.float64],
        threshold: float = 0.7,
        labels: list[str] | None = None,
    ) -> VisualizationData:
        """
        Show entity relationships as a similarity graph.

        Creates a graph visualization where nodes are entities and edges represent
        similarity above a threshold.

        Parameters
        ----------
        embeddings : NDArray[np.float64]
            High-dimensional embeddings matrix.
        threshold : float, optional
            Similarity threshold for creating edges (0.0 to 1.0). Default is 0.7.
        labels : list[str], optional
            Labels for each entity.

        Returns
        -------
        VisualizationData
            Similarity graph visualization data.
        """
        with span("dashboard.show_similarity_graph", threshold=threshold):
            from sklearn.metrics.pairwise import cosine_similarity

            # Compute similarity matrix
            similarity_matrix = cosine_similarity(embeddings)

            # Create edges above threshold (excluding self-similarity)
            edges = []
            for i in range(len(embeddings)):
                for j in range(i + 1, len(embeddings)):
                    if similarity_matrix[i, j] >= threshold:
                        edges.append(
                            {
                                "source": i,
                                "target": j,
                                "weight": float(similarity_matrix[i, j]),
                            }
                        )

            data = {
                "nodes": labels if labels else [f"entity_{i}" for i in range(len(embeddings))],
                "edges": edges,
            }

            metadata = {
                "threshold": threshold,
                "n_nodes": len(embeddings),
                "n_edges": len(edges),
                "avg_similarity": float(
                    np.mean(similarity_matrix[np.triu_indices_from(similarity_matrix, k=1)])
                ),
            }

            return VisualizationData(
                title="Entity Similarity Graph",
                chart_type="graph",
                data=data,
                metadata=metadata,
            )

    def measure_semantic_distance(
        self,
        entity1_embedding: NDArray[np.float64],
        entity2_embedding: NDArray[np.float64],
        entity1_label: str = "entity1",
        entity2_label: str = "entity2",
    ) -> MetricData:
        """
        Measure semantic distance between two entities.

        Computes cosine distance (1 - cosine_similarity) and Euclidean distance.

        Parameters
        ----------
        entity1_embedding : NDArray[np.float64]
            First entity embedding.
        entity2_embedding : NDArray[np.float64]
            Second entity embedding.
        entity1_label : str, optional
            Label for first entity.
        entity2_label : str, optional
            Label for second entity.

        Returns
        -------
        MetricData
            Semantic distance metrics.
        """
        with span("dashboard.measure_semantic_distance"):
            from sklearn.metrics.pairwise import cosine_similarity

            # Ensure 2D arrays for sklearn
            emb1 = entity1_embedding.reshape(1, -1)
            emb2 = entity2_embedding.reshape(1, -1)

            # Compute distances
            cosine_sim = float(cosine_similarity(emb1, emb2)[0, 0])
            cosine_dist = 1.0 - cosine_sim
            euclidean_dist = float(np.linalg.norm(entity1_embedding - entity2_embedding))

            return MetricData(
                name=f"semantic_distance_{entity1_label}_to_{entity2_label}",
                value=cosine_dist,
                unit="cosine_distance",
                metadata={
                    "entity1": entity1_label,
                    "entity2": entity2_label,
                    "cosine_similarity": cosine_sim,
                    "cosine_distance": cosine_dist,
                    "euclidean_distance": euclidean_dist,
                },
            )

    # =========================================================================
    # Information Metrics Dashboard
    # =========================================================================

    def entropy_distribution(
        self,
        specs: list[dict[str, Any]],
        feature_key: str = "text",
    ) -> VisualizationData:
        """
        Compute and visualize entropy distribution of specifications.

        Measures the information entropy of specification text to identify
        overly complex or ambiguous specifications.

        Parameters
        ----------
        specs : list[dict[str, Any]]
            List of specification dictionaries.
        feature_key : str, optional
            Key to extract text from specifications. Default is "text".

        Returns
        -------
        VisualizationData
            Entropy distribution histogram.
        """
        with span("dashboard.entropy_distribution", n_specs=len(specs)):
            import re
            from collections import Counter

            entropies = []
            for spec in specs:
                text = spec.get(feature_key, "")
                if not text:
                    continue

                # Tokenize and compute entropy
                tokens = re.findall(r"\w+", text.lower())
                if not tokens:
                    entropies.append(0.0)
                    continue

                # Compute probability distribution
                total = len(tokens)
                counts = Counter(tokens)
                probs = [count / total for count in counts.values()]

                # Compute Shannon entropy
                entropy = -sum(p * np.log2(p) for p in probs if p > 0)
                entropies.append(entropy)

            # Create histogram data
            hist, bin_edges = np.histogram(entropies, bins=20)

            data = {
                "bins": bin_edges.tolist(),
                "counts": hist.tolist(),
                "entropies": entropies,
            }

            metadata = {
                "n_specs": len(specs),
                "mean_entropy": float(np.mean(entropies)) if entropies else 0.0,
                "std_entropy": float(np.std(entropies)) if entropies else 0.0,
                "min_entropy": float(np.min(entropies)) if entropies else 0.0,
                "max_entropy": float(np.max(entropies)) if entropies else 0.0,
            }

            return VisualizationData(
                title="Specification Entropy Distribution",
                chart_type="histogram",
                data=data,
                metadata=metadata,
            )

    def mutual_information_heatmap(
        self,
        features: NDArray[np.float64],
        objectives: NDArray[np.float64],
        feature_names: list[str] | None = None,
        objective_names: list[str] | None = None,
    ) -> VisualizationData:
        """
        Compute mutual information between features and objectives.

        Creates a heatmap showing which features are most informative for
        each objective.

        Parameters
        ----------
        features : NDArray[np.float64]
            Feature matrix (n_samples, n_features).
        objectives : NDArray[np.float64]
            Objective matrix (n_samples, n_objectives).
        feature_names : list[str], optional
            Names of features.
        objective_names : list[str], optional
            Names of objectives.

        Returns
        -------
        VisualizationData
            Mutual information heatmap data.
        """
        with span("dashboard.mutual_information_heatmap"):
            from sklearn.feature_selection import mutual_info_regression

            n_features = features.shape[1]
            n_objectives = objectives.shape[1] if objectives.ndim > 1 else 1

            # Ensure 2D objectives
            if objectives.ndim == 1:
                objectives = objectives.reshape(-1, 1)

            # Compute mutual information for each objective
            mi_matrix = np.zeros((n_features, n_objectives))
            for j in range(n_objectives):
                mi_matrix[:, j] = mutual_info_regression(
                    features, objectives[:, j], random_state=42
                )

            data = {
                "matrix": mi_matrix.tolist(),
                "feature_names": feature_names
                if feature_names
                else [f"feature_{i}" for i in range(n_features)],
                "objective_names": objective_names
                if objective_names
                else [f"objective_{i}" for i in range(n_objectives)],
            }

            metadata = {
                "n_features": n_features,
                "n_objectives": n_objectives,
                "mean_mi": float(np.mean(mi_matrix)),
                "max_mi": float(np.max(mi_matrix)),
            }

            return VisualizationData(
                title="Feature-Objective Mutual Information",
                chart_type="heatmap",
                data=data,
                metadata=metadata,
            )

    def information_gain_chart(
        self,
        features: NDArray[np.float64],
        target: NDArray[np.float64],
        feature_names: list[str] | None = None,
        top_k: int = 10,
    ) -> VisualizationData:
        """
        Compute and visualize information gain for features.

        Ranks features by their information gain with respect to the target
        variable.

        Parameters
        ----------
        features : NDArray[np.float64]
            Feature matrix (n_samples, n_features).
        target : NDArray[np.float64]
            Target variable (n_samples,).
        feature_names : list[str], optional
            Names of features.
        top_k : int, optional
            Number of top features to show. Default is 10.

        Returns
        -------
        VisualizationData
            Information gain bar chart data.
        """
        with span("dashboard.information_gain_chart", top_k=top_k):
            from sklearn.feature_selection import mutual_info_regression

            # Compute information gain (mutual information)
            info_gains = mutual_info_regression(features, target, random_state=42)

            # Get top-k features
            top_indices = np.argsort(info_gains)[-top_k:][::-1]
            top_gains = info_gains[top_indices]

            names = (
                feature_names if feature_names else [f"feature_{i}" for i in range(len(info_gains))]
            )
            top_names = [names[i] for i in top_indices]

            data = {
                "feature_names": top_names,
                "information_gains": top_gains.tolist(),
            }

            metadata = {
                "n_features": len(info_gains),
                "top_k": top_k,
                "max_gain": float(np.max(info_gains)),
                "mean_gain": float(np.mean(info_gains)),
            }

            return VisualizationData(
                title=f"Top {top_k} Features by Information Gain",
                chart_type="bar",
                data=data,
                metadata=metadata,
            )

    def complexity_analysis(
        self,
        entities: list[dict[str, Any]],
        complexity_key: str = "text",
    ) -> VisualizationData:
        """
        Analyze and visualize complexity distribution of entities.

        Measures cyclomatic complexity (for code) or text complexity metrics
        (for specifications).

        Parameters
        ----------
        entities : list[dict[str, Any]]
            List of entity dictionaries.
        complexity_key : str, optional
            Key to extract content for complexity analysis. Default is "text".

        Returns
        -------
        VisualizationData
            Complexity distribution visualization.
        """
        with span("dashboard.complexity_analysis", n_entities=len(entities)):
            complexities = []

            for entity in entities:
                content = entity.get(complexity_key, "")
                if not content:
                    complexities.append(0.0)
                    continue

                # Simple complexity metrics based on text structure
                lines = content.split("\n")
                words = len(content.split())
                len(content)
                unique_words = len(set(content.lower().split()))

                # Complexity score: combination of metrics
                complexity = (
                    len(lines) * 0.3  # Number of lines
                    + words * 0.5  # Number of words
                    + (words / max(unique_words, 1)) * 0.2  # Repetition factor
                )
                complexities.append(complexity)

            # Create histogram
            hist, bin_edges = np.histogram(complexities, bins=15)

            data = {
                "bins": bin_edges.tolist(),
                "counts": hist.tolist(),
                "complexities": complexities,
            }

            metadata = {
                "n_entities": len(entities),
                "mean_complexity": float(np.mean(complexities)) if complexities else 0.0,
                "std_complexity": float(np.std(complexities)) if complexities else 0.0,
                "max_complexity": float(np.max(complexities)) if complexities else 0.0,
            }

            return VisualizationData(
                title="Entity Complexity Distribution",
                chart_type="histogram",
                data=data,
                metadata=metadata,
            )

    # =========================================================================
    # Quality Metrics
    # =========================================================================

    def specification_completeness_tracker(
        self,
        spec_history: list[dict[str, Any]],
    ) -> VisualizationData:
        """
        Track specification completeness over time.

        Analyzes how specifications evolve and become more complete over time.

        Parameters
        ----------
        spec_history : list[dict[str, Any]]
            History of specification versions with timestamps.

        Returns
        -------
        VisualizationData
            Completeness trend line chart.
        """
        with span("dashboard.specification_completeness_tracker", n_versions=len(spec_history)):
            timestamps = []
            completeness_scores = []

            required_sections = {
                "overview",
                "requirements",
                "constraints",
                "acceptance_criteria",
                "dependencies",
            }

            for spec in spec_history:
                timestamps.append(spec.get("timestamp", "unknown"))

                # Calculate completeness based on present sections
                present_sections = set(spec.keys())
                completeness = len(present_sections & required_sections) / len(required_sections)
                completeness_scores.append(completeness)

            data = {
                "timestamps": timestamps,
                "completeness": completeness_scores,
            }

            metadata = {
                "n_versions": len(spec_history),
                "final_completeness": completeness_scores[-1] if completeness_scores else 0.0,
                "required_sections": list(required_sections),
            }

            return VisualizationData(
                title="Specification Completeness Over Time",
                chart_type="line",
                data=data,
                metadata=metadata,
            )

    def code_generation_fidelity(
        self,
        spec: dict[str, Any],
        code: dict[str, Any],
    ) -> MetricData:
        """
        Measure code generation fidelity to specification.

        Computes how well generated code adheres to the specification requirements.

        Parameters
        ----------
        spec : dict[str, Any]
            Specification dictionary.
        code : dict[str, Any]
            Generated code dictionary.

        Returns
        -------
        MetricData
            Code generation fidelity metric.
        """
        with span("dashboard.code_generation_fidelity"):
            # Extract requirements from spec
            requirements = spec.get("requirements", [])
            if isinstance(requirements, str):
                requirements = [req.strip() for req in requirements.split("\n") if req.strip()]

            # Check implemented requirements in code
            code_text = code.get("text", "")
            implemented = 0

            for req in requirements:
                # Simple keyword matching (in production, use more sophisticated analysis)
                keywords = req.lower().split()
                if any(keyword in code_text.lower() for keyword in keywords):
                    implemented += 1

            fidelity = implemented / len(requirements) if requirements else 0.0

            return MetricData(
                name="code_generation_fidelity",
                value=fidelity,
                unit="ratio",
                threshold=0.8,
                status="ok" if fidelity >= 0.8 else "warning" if fidelity >= 0.6 else "critical",
                metadata={
                    "total_requirements": len(requirements),
                    "implemented_requirements": implemented,
                    "fidelity_score": fidelity,
                },
            )

    def architectural_compliance_scorecard(
        self,
        codebase: dict[str, Any],
    ) -> dict[str, MetricData]:
        """
        Generate architectural compliance scorecard.

        Measures compliance with architectural constraints and patterns.

        Parameters
        ----------
        codebase : dict[str, Any]
            Codebase structure and metrics.

        Returns
        -------
        dict[str, MetricData]
            Compliance metrics for different architectural aspects.
        """
        with span("dashboard.architectural_compliance_scorecard"):
            metrics = {}

            # Layer separation compliance
            layer_violations = codebase.get("layer_violations", 0)
            total_dependencies = codebase.get("total_dependencies", 1)
            layer_compliance = 1.0 - (layer_violations / total_dependencies)

            metrics["layer_separation"] = MetricData(
                name="layer_separation_compliance",
                value=layer_compliance,
                unit="ratio",
                threshold=0.95,
                status="ok" if layer_compliance >= 0.95 else "warning",
                metadata={"violations": layer_violations, "total": total_dependencies},
            )

            # Module size compliance
            oversized_modules = codebase.get("oversized_modules", 0)
            total_modules = codebase.get("total_modules", 1)
            size_compliance = 1.0 - (oversized_modules / total_modules)

            metrics["module_size"] = MetricData(
                name="module_size_compliance",
                value=size_compliance,
                unit="ratio",
                threshold=0.9,
                status="ok" if size_compliance >= 0.9 else "warning",
                metadata={"oversized": oversized_modules, "total": total_modules},
            )

            return metrics

    def test_coverage_heatmap(
        self,
        modules: dict[str, float],
    ) -> VisualizationData:
        """
        Create test coverage heatmap for modules.

        Visualizes test coverage across different modules to identify gaps.

        Parameters
        ----------
        modules : dict[str, float]
            Module names mapped to coverage percentages (0.0 to 1.0).

        Returns
        -------
        VisualizationData
            Test coverage heatmap data.
        """
        with span("dashboard.test_coverage_heatmap", n_modules=len(modules)):
            # Sort modules by coverage
            sorted_modules = sorted(modules.items(), key=lambda x: x[1])

            module_names = [name for name, _ in sorted_modules]
            coverage_values = [cov for _, cov in sorted_modules]

            data = {
                "modules": module_names,
                "coverage": coverage_values,
            }

            metadata = {
                "n_modules": len(modules),
                "mean_coverage": float(np.mean(coverage_values)),
                "min_coverage": float(np.min(coverage_values)),
                "max_coverage": float(np.max(coverage_values)),
                "below_threshold": sum(1 for cov in coverage_values if cov < 0.8),
            }

            return VisualizationData(
                title="Test Coverage by Module",
                chart_type="heatmap",
                data=data,
                metadata=metadata,
            )

    # =========================================================================
    # JTBD Outcome Metrics
    # =========================================================================

    def outcome_delivery_rate_dashboard(
        self,
        features: list[dict[str, Any]],
        outcomes: list[dict[str, Any]],
    ) -> VisualizationData:
        """
        Track outcome delivery rate over time.

        Measures how effectively features deliver on intended outcomes.

        Parameters
        ----------
        features : list[dict[str, Any]]
            List of features with delivery status.
        outcomes : list[dict[str, Any]]
            List of intended outcomes.

        Returns
        -------
        VisualizationData
            Outcome delivery rate trend visualization.
        """
        with span("dashboard.outcome_delivery_rate", n_features=len(features)):
            # Track delivery over time
            timestamps = []
            delivery_rates = []

            # Group features by timestamp
            from collections import defaultdict

            features_by_time = defaultdict(list)
            for feature in features:
                ts = feature.get("timestamp", "unknown")
                features_by_time[ts].append(feature)

            for ts in sorted(features_by_time.keys()):
                delivered = sum(1 for f in features_by_time[ts] if f.get("status") == "delivered")
                total = len(features_by_time[ts])
                rate = delivered / total if total > 0 else 0.0

                timestamps.append(ts)
                delivery_rates.append(rate)

            data = {
                "timestamps": timestamps,
                "delivery_rates": delivery_rates,
            }

            metadata = {
                "total_features": len(features),
                "total_outcomes": len(outcomes),
                "current_rate": delivery_rates[-1] if delivery_rates else 0.0,
            }

            return VisualizationData(
                title="Outcome Delivery Rate Over Time",
                chart_type="line",
                data=data,
                metadata=metadata,
            )

    def job_coverage_analysis(
        self,
        jobs: list[dict[str, Any]],
        features: list[dict[str, Any]],
    ) -> VisualizationData:
        """
        Analyze feature coverage for each job.

        Shows which jobs are well-supported by features and which have gaps.

        Parameters
        ----------
        jobs : list[dict[str, Any]]
            List of customer jobs.
        features : list[dict[str, Any]]
            List of features with job mappings.

        Returns
        -------
        VisualizationData
            Job coverage bar chart.
        """
        with span("dashboard.job_coverage_analysis", n_jobs=len(jobs)):
            job_coverage = {}

            for job in jobs:
                job_id = job.get("id", "unknown")
                # Count features addressing this job
                addressing_features = sum(
                    1 for f in features if job_id in f.get("addresses_jobs", [])
                )
                job_coverage[job.get("name", job_id)] = addressing_features

            job_names = list(job_coverage.keys())
            coverage_counts = list(job_coverage.values())

            data = {
                "jobs": job_names,
                "feature_counts": coverage_counts,
            }

            metadata = {
                "n_jobs": len(jobs),
                "total_features": len(features),
                "uncovered_jobs": sum(1 for count in coverage_counts if count == 0),
            }

            return VisualizationData(
                title="Feature Coverage per Job",
                chart_type="bar",
                data=data,
                metadata=metadata,
            )

    def customer_satisfaction_trends(
        self,
        feedback: list[dict[str, Any]],
    ) -> VisualizationData:
        """
        Visualize customer satisfaction trends over time.

        Tracks satisfaction scores from customer feedback.

        Parameters
        ----------
        feedback : list[dict[str, Any]]
            List of customer feedback with timestamps and ratings.

        Returns
        -------
        VisualizationData
            Customer satisfaction trend line chart.
        """
        with span("dashboard.customer_satisfaction_trends", n_feedback=len(feedback)):
            # Sort by timestamp
            sorted_feedback = sorted(feedback, key=lambda x: x.get("timestamp", ""))

            timestamps = [f.get("timestamp", "unknown") for f in sorted_feedback]
            ratings = [f.get("rating", 0.0) for f in sorted_feedback]

            # Calculate rolling average
            window = 5
            rolling_avg = []
            for i in range(len(ratings)):
                start = max(0, i - window + 1)
                avg = sum(ratings[start : i + 1]) / (i - start + 1)
                rolling_avg.append(avg)

            data = {
                "timestamps": timestamps,
                "ratings": ratings,
                "rolling_average": rolling_avg,
            }

            metadata = {
                "n_feedback": len(feedback),
                "mean_rating": float(np.mean(ratings)) if ratings else 0.0,
                "latest_rating": ratings[-1] if ratings else 0.0,
                "trend": "improving" if ratings[-1] > np.mean(ratings) else "declining",
            }

            return VisualizationData(
                title="Customer Satisfaction Trends",
                chart_type="line",
                data=data,
                metadata=metadata,
            )

    def feature_roi_analysis(
        self,
        features: list[dict[str, Any]],
    ) -> VisualizationData:
        """
        Analyze return on investment for features.

        Compares development costs to delivered benefits for each feature.

        Parameters
        ----------
        features : list[dict[str, Any]]
            List of features with cost and benefit data.

        Returns
        -------
        VisualizationData
            Feature ROI scatter plot.
        """
        with span("dashboard.feature_roi_analysis", n_features=len(features)):
            feature_names = []
            costs = []
            benefits = []
            roi_scores = []

            for feature in features:
                cost = feature.get("cost", 1.0)
                benefit = feature.get("benefit", 0.0)
                roi = (benefit - cost) / cost if cost > 0 else 0.0

                feature_names.append(feature.get("name", "unknown"))
                costs.append(cost)
                benefits.append(benefit)
                roi_scores.append(roi)

            data = {
                "features": feature_names,
                "costs": costs,
                "benefits": benefits,
                "roi": roi_scores,
            }

            metadata = {
                "n_features": len(features),
                "mean_roi": float(np.mean(roi_scores)) if roi_scores else 0.0,
                "positive_roi_count": sum(1 for roi in roi_scores if roi > 0),
            }

            return VisualizationData(
                title="Feature ROI Analysis",
                chart_type="scatter",
                data=data,
                metadata=metadata,
            )

    def to_json(self, data: VisualizationData | MetricData) -> str:
        """
        Convert visualization or metric data to JSON.

        Parameters
        ----------
        data : VisualizationData | MetricData
            Data to convert.

        Returns
        -------
        str
            JSON string representation.
        """
        if isinstance(data, VisualizationData):
            return json.dumps(
                {
                    "title": data.title,
                    "chart_type": data.chart_type,
                    "data": data.data,
                    "metadata": data.metadata,
                },
                indent=2,
            )
        if isinstance(data, MetricData):
            return json.dumps(
                {
                    "name": data.name,
                    "value": data.value,
                    "unit": data.unit,
                    "threshold": data.threshold,
                    "status": data.status,
                    "metadata": data.metadata,
                },
                indent=2,
            )
        return json.dumps(data, indent=2)
