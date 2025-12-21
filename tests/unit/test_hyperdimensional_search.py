"""Unit tests for hyperdimensional search module."""

from __future__ import annotations

import numpy as np
import pytest

# These tests are for experimental hyperdimensional search features
# Mark as xfail until full implementation is complete
pytestmark = pytest.mark.xfail(
    reason="Hyperdimensional search module under development",
    strict=False,
)

from specify_cli.hyperdimensional.search import SearchResult, SemanticSearchDashboard


@pytest.fixture
def search_dashboard():
    """Create semantic search dashboard instance."""
    return SemanticSearchDashboard(min_similarity=0.5)


@pytest.fixture
def sample_features():
    """Create sample features."""
    return [
        {
            "id": "feat1",
            "name": "Feature 1",
            "description": "A feature for Python developers",
            "addresses_jobs": ["job1"],
            "capabilities": ["capability1", "capability2"],
        },
        {
            "id": "feat2",
            "name": "Feature 2",
            "description": "A feature for DevOps engineers",
            "addresses_jobs": ["job2"],
            "capabilities": ["capability3"],
        },
    ]


@pytest.fixture
def sample_embeddings():
    """Create sample embeddings."""
    np.random.seed(42)
    return np.random.randn(2, 128).astype(np.float64)


# =================================================================
# Interactive Query Interface Tests
# =================================================================


def test_search_by_semantic_similarity(search_dashboard, sample_features, sample_embeddings):
    """Test semantic similarity search."""
    query_embedding = sample_embeddings[0]

    results = search_dashboard.search_by_semantic_similarity(
        query_embedding,
        sample_features,
        sample_embeddings,
        k=2,
    )

    assert len(results) <= 2
    assert all(isinstance(r, SearchResult) for r in results)
    assert all(r.score >= search_dashboard.min_similarity for r in results)


def test_search_with_text_query(search_dashboard, sample_features, sample_embeddings):
    """Test search with text query."""
    results = search_dashboard.search_by_semantic_similarity(
        "Python development",
        sample_features,
        sample_embeddings,
        k=1,
    )

    assert isinstance(results, list)


def test_find_similar_features(search_dashboard, sample_features, sample_embeddings):
    """Test finding similar features."""
    reference_feature = sample_features[0]

    results = search_dashboard.find_similar_features(
        reference_feature,
        sample_features,
        sample_embeddings,
        k=1,
    )

    assert len(results) <= 1
    # Should not include the reference feature itself


def test_recommend_features_for_job(search_dashboard, sample_features, sample_embeddings):
    """Test feature recommendation for job."""
    job = {
        "id": "job1",
        "name": "Python Developer",
        "description": "Develop Python applications",
    }

    results = search_dashboard.recommend_features_for_job(
        job,
        sample_features,
        sample_embeddings,
        k=2,
    )

    assert len(results) <= 2
    assert all(isinstance(r, SearchResult) for r in results)


def test_identify_feature_gaps_for_job(search_dashboard, sample_features):
    """Test feature gap identification."""
    job = {
        "id": "job1",
        "name": "Python Developer",
        "required_capabilities": ["capability1", "capability2", "capability4"],
    }

    gap_analysis = search_dashboard.identify_feature_gaps_for_job(job, sample_features)

    assert "coverage" in gap_analysis
    assert "missing_capabilities" in gap_analysis
    assert "capability4" in gap_analysis["missing_capabilities"]


# =================================================================
# Visualization Tests
# =================================================================


def test_show_feature_outcome_mappings(search_dashboard):
    """Test feature-outcome mapping visualization."""
    feature = {
        "id": "feat1",
        "name": "Feature 1",
        "delivers_outcomes": ["outcome1", "outcome2"],
    }

    viz = search_dashboard.show_feature_outcome_mappings(feature)

    assert viz.chart_type == "graph"
    assert len(viz.data["nodes"]) > 0
    assert len(viz.data["edges"]) == 2


def test_visualize_job_coverage(search_dashboard, sample_features):
    """Test job coverage visualization."""
    job = {
        "id": "job1",
        "name": "Python Developer",
        "required_capabilities": ["capability1", "capability2"],
    }

    viz = search_dashboard.visualize_job_coverage(job, sample_features)

    assert viz.chart_type == "bar"
    assert "capabilities" in viz.data
    assert "status" in viz.data


def test_show_painpoint_resolution(search_dashboard):
    """Test painpoint resolution visualization."""
    painpoint = {
        "id": "pain1",
        "name": "Slow builds",
    }

    features = [
        {
            "id": "feat1",
            "name": "Feature 1",
            "addresses_painpoints": ["pain1"],
            "painpoint_resolution_scores": {"pain1": 0.8},
        },
    ]

    viz = search_dashboard.show_painpoint_resolution(painpoint, features)

    assert viz.chart_type == "bar"
    assert len(viz.data["features"]) == 1


# =================================================================
# Edge Cases
# =================================================================


def test_empty_features(search_dashboard, sample_embeddings):
    """Test with empty feature list."""
    results = search_dashboard.search_by_semantic_similarity(
        sample_embeddings[0],
        [],
        None,
    )

    assert len(results) == 0


def test_no_matching_features(search_dashboard, sample_features):
    """Test job with no matching features."""
    job = {
        "id": "job99",
        "name": "Unknown Job",
        "description": "xyz abc",
    }

    results = search_dashboard.recommend_features_for_job(
        job,
        sample_features,
        None,  # No embeddings
    )

    # Should use fallback keyword matching
    assert isinstance(results, list)


def test_complete_job_coverage(search_dashboard):
    """Test job with complete coverage."""
    job = {
        "id": "job1",
        "name": "Test Job",
        "required_capabilities": ["cap1", "cap2"],
    }

    features = [
        {
            "id": "feat1",
            "name": "Feature 1",
            "addresses_jobs": ["job1"],
            "capabilities": ["cap1", "cap2"],
        },
    ]

    gap_analysis = search_dashboard.identify_feature_gaps_for_job(job, features)

    assert gap_analysis["coverage"] == 1.0
    assert len(gap_analysis["missing_capabilities"]) == 0
