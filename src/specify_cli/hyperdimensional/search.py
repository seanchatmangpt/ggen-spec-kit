"""
specify_cli.hyperdimensional.search - Semantic Search Dashboard
==============================================================

Semantic search dashboard with interactive query interface and feature recommendations.

This module provides semantic search capabilities for:
* **Interactive Query Interface**: Semantic similarity search, feature finding
* **Feature Recommendations**: Job-based recommendations, feature gap identification
* **Visualization**: Feature-outcome mappings, job coverage maps

Examples
--------
    >>> from specify_cli.hyperdimensional.search import SemanticSearchDashboard
    >>>
    >>> search = SemanticSearchDashboard()
    >>> results = search.search_by_semantic_similarity(query, k=10)
    >>> similar = search.find_similar_features(feature, k=5)
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
    "SearchResult",
    "SemanticSearchDashboard",
]


@dataclass
class SearchResult:
    """Search result data structure."""

    item_id: str
    name: str
    score: float  # Similarity score 0.0 to 1.0
    rank: int
    content: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)


class SemanticSearchDashboard:
    """
    Semantic search dashboard for hyperdimensional feature discovery.

    This class provides semantic search and recommendation capabilities
    for features, specifications, and job-to-be-done analysis.

    Attributes
    ----------
    feature_index : dict[str, NDArray[np.float64]]
        Index of feature embeddings.
    min_similarity : float
        Minimum similarity threshold for results.
    """

    def __init__(
        self,
        feature_index: dict[str, NDArray[np.float64]] | None = None,
        min_similarity: float = 0.5,
    ) -> None:
        """
        Initialize semantic search dashboard.

        Parameters
        ----------
        feature_index : dict[str, NDArray[np.float64]], optional
            Pre-built feature index.
        min_similarity : float, optional
            Minimum similarity threshold. Default is 0.5.
        """
        self.feature_index = feature_index or {}
        self.min_similarity = min_similarity

    # =========================================================================
    # Interactive Query Interface
    # =========================================================================

    def search_by_semantic_similarity(
        self,
        query: str | NDArray[np.float64],
        features: list[dict[str, Any]] | None = None,
        embeddings: NDArray[np.float64] | None = None,
        k: int = 10,
    ) -> list[SearchResult]:
        """
        Search by semantic similarity.

        Finds features most similar to a query using semantic embeddings.

        Parameters
        ----------
        query : str | NDArray[np.float64]
            Query string or embedding vector.
        features : list[dict[str, Any]], optional
            Feature list to search.
        embeddings : NDArray[np.float64], optional
            Feature embeddings matrix.
        k : int, optional
            Number of results to return. Default is 10.

        Returns
        -------
        list[SearchResult]
            Top-k similar features.
        """
        with span("search.semantic_similarity", k=k):
            if features is None or embeddings is None:
                return []

            # Convert query to embedding if needed
            query_embedding = self._text_to_embedding(query) if isinstance(query, str) else query

            # Compute similarities
            from sklearn.metrics.pairwise import cosine_similarity

            query_emb_2d = query_embedding.reshape(1, -1)
            similarities = cosine_similarity(query_emb_2d, embeddings)[0]

            # Get top-k indices
            top_indices = np.argsort(similarities)[-k:][::-1]

            # Create results
            results = []
            for rank, idx in enumerate(top_indices, start=1):
                if similarities[idx] < self.min_similarity:
                    continue

                feature = features[idx]
                results.append(
                    SearchResult(
                        item_id=feature.get("id", f"feature_{idx}"),
                        name=feature.get("name", f"feature_{idx}"),
                        score=float(similarities[idx]),
                        rank=rank,
                        content=feature,
                        metadata={"embedding_idx": idx},
                    )
                )

            return results

    def _text_to_embedding(self, text: str) -> NDArray[np.float64]:
        """Convert text to embedding vector (placeholder)."""
        # In production, use actual embedding model (e.g., sentence-transformers)
        # For now, create a simple hash-based embedding
        import hashlib

        # Create deterministic vector from text hash
        text_hash = hashlib.md5(text.encode()).digest()
        embedding = np.frombuffer(text_hash, dtype=np.uint8).astype(np.float64)

        # Pad or truncate to fixed dimension
        target_dim = 128
        if len(embedding) < target_dim:
            embedding = np.pad(embedding, (0, target_dim - len(embedding)))
        else:
            embedding = embedding[:target_dim]

        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return embedding

    def find_similar_features(
        self,
        feature: dict[str, Any],
        all_features: list[dict[str, Any]],
        embeddings: NDArray[np.float64],
        k: int = 10,
    ) -> list[SearchResult]:
        """
        Find features similar to a given feature.

        Parameters
        ----------
        feature : dict[str, Any]
            Reference feature.
        all_features : list[dict[str, Any]]
            All available features.
        embeddings : NDArray[np.float64]
            Feature embeddings matrix.
        k : int, optional
            Number of similar features to return. Default is 10.

        Returns
        -------
        list[SearchResult]
            Top-k similar features.
        """
        with span("search.find_similar_features", k=k):
            # Find feature index
            feature_id = feature.get("id")
            feature_idx = next(
                (i for i, f in enumerate(all_features) if f.get("id") == feature_id), None
            )

            if feature_idx is None:
                return []

            # Use feature's embedding as query
            feature_embedding = embeddings[feature_idx]

            # Search
            return self.search_by_semantic_similarity(
                feature_embedding,
                all_features,
                embeddings,
                k=k + 1,  # +1 to exclude self
            )[1:]  # Exclude self from results

    def recommend_features_for_job(
        self,
        job: dict[str, Any],
        features: list[dict[str, Any]],
        embeddings: NDArray[np.float64] | None = None,
        k: int = 5,
    ) -> list[SearchResult]:
        """
        Recommend features for a specific job.

        Uses job description to find relevant features.

        Parameters
        ----------
        job : dict[str, Any]
            Job-to-be-done specification.
        features : list[dict[str, Any]]
            Available features.
        embeddings : NDArray[np.float64], optional
            Feature embeddings.
        k : int, optional
            Number of recommendations. Default is 5.

        Returns
        -------
        list[SearchResult]
            Top-k recommended features.
        """
        with span("search.recommend_features_for_job", k=k):
            # Extract job description
            job_desc = job.get("description", "")
            if not job_desc:
                job_desc = job.get("name", "")

            # Search by job description
            if embeddings is not None:
                return self.search_by_semantic_similarity(
                    job_desc,
                    features,
                    embeddings,
                    k=k,
                )

            # Fallback to keyword matching
            results = []
            job_keywords = set(job_desc.lower().split())

            for idx, feature in enumerate(features):
                feature_text = f"{feature.get('name', '')} {feature.get('description', '')}"
                feature_keywords = set(feature_text.lower().split())

                # Calculate keyword overlap
                overlap = len(job_keywords & feature_keywords)
                score = overlap / max(len(job_keywords), 1)

                if score >= self.min_similarity:
                    results.append(
                        SearchResult(
                            item_id=feature.get("id", f"feature_{idx}"),
                            name=feature.get("name", f"feature_{idx}"),
                            score=score,
                            rank=0,
                            content=feature,
                        )
                    )

            # Sort by score
            results.sort(key=lambda r: r.score, reverse=True)

            # Update ranks
            for rank, result in enumerate(results[:k], start=1):
                result.rank = rank

            return results[:k]

    def identify_feature_gaps_for_job(
        self,
        job: dict[str, Any],
        features: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Identify feature gaps for a job.

        Analyzes what features are missing to fully support a job.

        Parameters
        ----------
        job : dict[str, Any]
            Job-to-be-done specification.
        features : list[dict[str, Any]]
            Available features.

        Returns
        -------
        dict[str, Any]
            Gap analysis with missing capabilities.
        """
        with span("search.identify_feature_gaps"):
            job_id = job.get("id")
            job_name = job.get("name", "unknown")

            # Extract required capabilities from job
            required_capabilities = set(job.get("required_capabilities", []))

            # Extract provided capabilities from features
            provided_capabilities = set()
            addressing_features = []

            for feature in features:
                if job_id in feature.get("addresses_jobs", []):
                    addressing_features.append(feature.get("name"))
                    provided_capabilities.update(feature.get("capabilities", []))

            # Identify gaps
            missing_capabilities = required_capabilities - provided_capabilities
            coverage = (
                len(provided_capabilities) / len(required_capabilities)
                if required_capabilities
                else 1.0
            )

            return {
                "job": job_name,
                "job_id": job_id,
                "coverage": coverage,
                "required_capabilities": list(required_capabilities),
                "provided_capabilities": list(provided_capabilities),
                "missing_capabilities": list(missing_capabilities),
                "addressing_features": addressing_features,
                "gap_count": len(missing_capabilities),
            }

    # =========================================================================
    # Visualization
    # =========================================================================

    def show_feature_outcome_mappings(
        self,
        feature: dict[str, Any],
    ) -> VisualizationData:
        """
        Show feature-to-outcome value delivery chains.

        Visualizes how a feature delivers value to outcomes.

        Parameters
        ----------
        feature : dict[str, Any]
            Feature to analyze.

        Returns
        -------
        VisualizationData
            Feature-outcome mapping visualization.
        """
        with span("search.show_feature_outcome_mappings"):
            # Extract outcomes
            outcomes = feature.get("delivers_outcomes", [])

            # Build graph structure
            nodes = [feature.get("name", "feature")]
            nodes.extend(outcomes)

            edges = [
                {
                    "source": feature.get("name", "feature"),
                    "target": outcome,
                    "weight": 1.0,
                }
                for outcome in outcomes
            ]

            data = {
                "nodes": nodes,
                "edges": edges,
                "feature": feature.get("name"),
            }

            metadata = {
                "n_outcomes": len(outcomes),
                "feature_id": feature.get("id"),
            }

            return VisualizationData(
                title=f"Value Delivery Chain: {feature.get('name')}",
                chart_type="graph",
                data=data,
                metadata=metadata,
            )

    def visualize_job_coverage(
        self,
        job: dict[str, Any],
        features: list[dict[str, Any]],
    ) -> VisualizationData:
        """
        Visualize feature coverage for a job.

        Shows which capabilities are covered by features.

        Parameters
        ----------
        job : dict[str, Any]
            Job-to-be-done.
        features : list[dict[str, Any]]
            Available features.

        Returns
        -------
        VisualizationData
            Job coverage visualization.
        """
        with span("search.visualize_job_coverage"):
            gap_analysis = self.identify_feature_gaps_for_job(job, features)

            # Create coverage visualization
            capabilities = gap_analysis["required_capabilities"]
            coverage_status = []

            for cap in capabilities:
                if cap in gap_analysis["provided_capabilities"]:
                    coverage_status.append("covered")
                else:
                    coverage_status.append("missing")

            data = {
                "capabilities": capabilities,
                "status": coverage_status,
                "coverage_ratio": gap_analysis["coverage"],
            }

            metadata = {
                "job": gap_analysis["job"],
                "total_capabilities": len(capabilities),
                "covered_capabilities": len(gap_analysis["provided_capabilities"]),
                "missing_capabilities": len(gap_analysis["missing_capabilities"]),
            }

            return VisualizationData(
                title=f"Job Coverage: {gap_analysis['job']}",
                chart_type="bar",
                data=data,
                metadata=metadata,
            )

    def show_painpoint_resolution(
        self,
        painpoint: dict[str, Any],
        features: list[dict[str, Any]],
    ) -> VisualizationData:
        """
        Show which features address a specific painpoint.

        Parameters
        ----------
        painpoint : dict[str, Any]
            Customer painpoint.
        features : list[dict[str, Any]]
            Available features.

        Returns
        -------
        VisualizationData
            Painpoint resolution visualization.
        """
        with span("search.show_painpoint_resolution"):
            painpoint_id = painpoint.get("id")
            painpoint_name = painpoint.get("name", "unknown")

            # Find addressing features
            addressing_features = []
            resolution_scores = []

            for feature in features:
                if painpoint_id in feature.get("addresses_painpoints", []):
                    addressing_features.append(feature.get("name"))
                    # Get resolution score (how well it addresses the painpoint)
                    score = feature.get("painpoint_resolution_scores", {}).get(painpoint_id, 0.5)
                    resolution_scores.append(score)

            data = {
                "features": addressing_features,
                "resolution_scores": resolution_scores,
                "painpoint": painpoint_name,
            }

            metadata = {
                "painpoint_id": painpoint_id,
                "n_features": len(addressing_features),
                "avg_resolution": float(np.mean(resolution_scores)) if resolution_scores else 0.0,
            }

            return VisualizationData(
                title=f"Painpoint Resolution: {painpoint_name}",
                chart_type="bar",
                data=data,
                metadata=metadata,
            )
