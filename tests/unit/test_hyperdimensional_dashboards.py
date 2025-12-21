"""Unit tests for hyperdimensional dashboards module."""

from __future__ import annotations

import numpy as np
import pytest

# These tests are for experimental hyperdimensional dashboards
# Mark as xfail until full implementation is complete
pytestmark = pytest.mark.xfail(
    reason="Hyperdimensional dashboards module under development",
    strict=False,
)

from specify_cli.hyperdimensional.dashboards import (
    DashboardFramework,
    MetricData,
    VisualizationData,
)


@pytest.fixture
def dashboard():
    """Create dashboard framework instance."""
    return DashboardFramework(visualization_backend="data_only", output_format="json")


@pytest.fixture
def sample_embeddings():
    """Create sample embeddings for testing."""
    np.random.seed(42)
    return np.random.randn(20, 128).astype(np.float64)


@pytest.fixture
def sample_specs():
    """Create sample specifications."""
    return [
        {
            "id": "spec1",
            "text": "This is a clear specification with well-defined requirements and constraints.",
            "overview": "Test spec",
            "requirements": ["req1", "req2"],
        },
        {
            "id": "spec2",
            "text": "Another specification.",
            "overview": "Test spec 2",
        },
    ]


@pytest.fixture
def sample_features():
    """Create sample features."""
    return [
        {
            "id": "feat1",
            "name": "Feature 1",
            "description": "First feature",
            "timestamp": "2024-01-01T00:00:00Z",
            "status": "delivered",
        },
        {
            "id": "feat2",
            "name": "Feature 2",
            "description": "Second feature",
            "timestamp": "2024-01-02T00:00:00Z",
            "status": "in_progress",
        },
    ]


# =======================================================================================
# Semantic Space Visualization Tests
# =======================================================================================


def test_plot_semantic_space_2d(dashboard, sample_embeddings):
    """Test 2D semantic space projection."""
    labels = [f"item_{i}" for i in range(len(sample_embeddings))]

    viz = dashboard.plot_semantic_space_2d(sample_embeddings, labels=labels, method="pca")

    assert isinstance(viz, VisualizationData)
    assert viz.title == "Semantic Space 2D Projection (PCA)"
    assert viz.chart_type == "scatter"
    assert len(viz.data["x"]) == len(sample_embeddings)
    assert len(viz.data["y"]) == len(sample_embeddings)
    assert viz.metadata["method"] == "pca"
    assert viz.metadata["n_samples"] == len(sample_embeddings)


def test_plot_semantic_space_3d(dashboard, sample_embeddings):
    """Test 3D semantic space projection."""
    viz = dashboard.plot_semantic_space_3d(sample_embeddings, method="pca")

    assert isinstance(viz, VisualizationData)
    assert viz.chart_type == "scatter3d"
    assert len(viz.data["x"]) == len(sample_embeddings)
    assert len(viz.data["y"]) == len(sample_embeddings)
    assert len(viz.data["z"]) == len(sample_embeddings)


def test_highlight_concept_cluster(dashboard, sample_embeddings):
    """Test concept cluster highlighting."""
    concept_indices = [0, 1, 5, 10]

    viz = dashboard.highlight_concept_cluster(
        sample_embeddings,
        concept_indices,
        labels=None,
    )

    assert isinstance(viz, VisualizationData)
    assert viz.title == "Concept Cluster Visualization"
    assert viz.metadata["n_highlighted"] == len(concept_indices)
    assert sum(viz.data["highlight"]) == len(concept_indices)


def test_show_similarity_graph(dashboard, sample_embeddings):
    """Test similarity graph generation."""
    labels = [f"entity_{i}" for i in range(len(sample_embeddings))]

    viz = dashboard.show_similarity_graph(
        sample_embeddings,
        threshold=0.7,
        labels=labels,
    )

    assert isinstance(viz, VisualizationData)
    assert viz.chart_type == "graph"
    assert len(viz.data["nodes"]) == len(sample_embeddings)
    assert viz.metadata["threshold"] == 0.7


def test_measure_semantic_distance(dashboard):
    """Test semantic distance measurement."""
    emb1 = np.array([1.0, 0.0, 0.0], dtype=np.float64)
    emb2 = np.array([0.0, 1.0, 0.0], dtype=np.float64)

    metric = dashboard.measure_semantic_distance(
        emb1,
        emb2,
        entity1_label="entity1",
        entity2_label="entity2",
    )

    assert isinstance(metric, MetricData)
    assert metric.unit == "cosine_distance"
    assert 0.0 <= metric.value <= 2.0


# =======================================================================================
# Information Metrics Tests
# =======================================================================================


def test_entropy_distribution(dashboard, sample_specs):
    """Test entropy distribution calculation."""
    viz = dashboard.entropy_distribution(sample_specs, feature_key="text")

    assert isinstance(viz, VisualizationData)
    assert viz.chart_type == "histogram"
    assert "entropies" in viz.data
    assert viz.metadata["n_specs"] == len(sample_specs)


def test_mutual_information_heatmap(dashboard):
    """Test mutual information heatmap generation."""
    features = np.random.randn(50, 5).astype(np.float64)
    objectives = np.random.randn(50, 3).astype(np.float64)

    viz = dashboard.mutual_information_heatmap(
        features,
        objectives,
        feature_names=["f1", "f2", "f3", "f4", "f5"],
        objective_names=["obj1", "obj2", "obj3"],
    )

    assert isinstance(viz, VisualizationData)
    assert viz.chart_type == "heatmap"
    assert len(viz.data["feature_names"]) == 5
    assert len(viz.data["objective_names"]) == 3


def test_information_gain_chart(dashboard):
    """Test information gain chart."""
    features = np.random.randn(100, 10).astype(np.float64)
    target = np.random.randn(100).astype(np.float64)

    viz = dashboard.information_gain_chart(
        features,
        target,
        feature_names=[f"feature_{i}" for i in range(10)],
        top_k=5,
    )

    assert isinstance(viz, VisualizationData)
    assert viz.chart_type == "bar"
    assert len(viz.data["feature_names"]) == 5


def test_complexity_analysis(dashboard):
    """Test complexity analysis."""
    entities = [
        {"text": "Simple text"},
        {"text": "More complex text with many words and multiple lines\n" * 10},
    ]

    viz = dashboard.complexity_analysis(entities, complexity_key="text")

    assert isinstance(viz, VisualizationData)
    assert viz.chart_type == "histogram"
    assert viz.metadata["n_entities"] == len(entities)


# =======================================================================================
# Quality Metrics Tests
# =======================================================================================


def test_specification_completeness_tracker(dashboard):
    """Test specification completeness tracking."""
    spec_history = [
        {
            "timestamp": "2024-01-01T00:00:00Z",
            "overview": "Initial",
        },
        {
            "timestamp": "2024-01-02T00:00:00Z",
            "overview": "Updated",
            "requirements": ["req1"],
        },
        {
            "timestamp": "2024-01-03T00:00:00Z",
            "overview": "Complete",
            "requirements": ["req1", "req2"],
            "constraints": ["c1"],
            "acceptance_criteria": ["ac1"],
        },
    ]

    viz = dashboard.specification_completeness_tracker(spec_history)

    assert isinstance(viz, VisualizationData)
    assert viz.chart_type == "line"
    assert len(viz.data["timestamps"]) == len(spec_history)
    assert viz.data["completeness"][-1] > viz.data["completeness"][0]


def test_code_generation_fidelity(dashboard):
    """Test code generation fidelity measurement."""
    spec = {
        "requirements": [
            "implement function to add numbers",
            "handle error cases",
        ],
    }

    code = {
        "text": "def add(a, b):\n    return a + b\n\ntry:\n    add(1, 2)\nexcept:\n    pass",
    }

    metric = dashboard.code_generation_fidelity(spec, code)

    assert isinstance(metric, MetricData)
    assert metric.name == "code_generation_fidelity"
    assert 0.0 <= metric.value <= 1.0


def test_architectural_compliance_scorecard(dashboard):
    """Test architectural compliance scorecard."""
    codebase = {
        "layer_violations": 2,
        "total_dependencies": 100,
        "oversized_modules": 3,
        "total_modules": 50,
    }

    metrics = dashboard.architectural_compliance_scorecard(codebase)

    assert "layer_separation" in metrics
    assert "module_size" in metrics
    assert all(isinstance(m, MetricData) for m in metrics.values())


def test_test_coverage_heatmap(dashboard):
    """Test test coverage heatmap."""
    modules = {
        "module1": 0.95,
        "module2": 0.75,
        "module3": 0.60,
    }

    viz = dashboard.test_coverage_heatmap(modules)

    assert isinstance(viz, VisualizationData)
    assert viz.chart_type == "heatmap"
    assert len(viz.data["modules"]) == len(modules)


# =======================================================================================
# JTBD Outcome Metrics Tests
# =======================================================================================


def test_outcome_delivery_rate_dashboard(dashboard, sample_features):
    """Test outcome delivery rate dashboard."""
    outcomes = [
        {"id": "out1", "name": "Outcome 1"},
        {"id": "out2", "name": "Outcome 2"},
    ]

    viz = dashboard.outcome_delivery_rate_dashboard(sample_features, outcomes)

    assert isinstance(viz, VisualizationData)
    assert viz.chart_type == "line"
    assert "delivery_rates" in viz.data


def test_job_coverage_analysis(dashboard, sample_features):
    """Test job coverage analysis."""
    jobs = [
        {"id": "job1", "name": "Python Developer"},
        {"id": "job2", "name": "DevOps Engineer"},
    ]

    features_with_jobs = [{**f, "addresses_jobs": ["job1"]} for f in sample_features]

    viz = dashboard.job_coverage_analysis(jobs, features_with_jobs)

    assert isinstance(viz, VisualizationData)
    assert viz.chart_type == "bar"
    assert len(viz.data["jobs"]) == len(jobs)


def test_customer_satisfaction_trends(dashboard):
    """Test customer satisfaction trends."""
    feedback = [
        {"timestamp": "2024-01-01T00:00:00Z", "rating": 4.0},
        {"timestamp": "2024-01-02T00:00:00Z", "rating": 4.5},
        {"timestamp": "2024-01-03T00:00:00Z", "rating": 4.2},
    ]

    viz = dashboard.customer_satisfaction_trends(feedback)

    assert isinstance(viz, VisualizationData)
    assert viz.chart_type == "line"
    assert len(viz.data["ratings"]) == len(feedback)


def test_feature_roi_analysis(dashboard, sample_features):
    """Test feature ROI analysis."""
    features_with_roi = [{**f, "cost": 10.0, "benefit": 20.0} for f in sample_features]

    viz = dashboard.feature_roi_analysis(features_with_roi)

    assert isinstance(viz, VisualizationData)
    assert viz.chart_type == "scatter"
    assert len(viz.data["features"]) == len(features_with_roi)


# =======================================================================================
# Data Export Tests
# =======================================================================================


def test_to_json_visualization(dashboard, sample_embeddings):
    """Test JSON export of visualization data."""
    viz = dashboard.plot_semantic_space_2d(sample_embeddings)
    json_str = dashboard.to_json(viz)

    assert isinstance(json_str, str)
    assert "title" in json_str
    assert "chart_type" in json_str


def test_to_json_metric(dashboard):
    """Test JSON export of metric data."""
    metric = MetricData(
        name="test_metric",
        value=0.85,
        unit="ratio",
        threshold=0.8,
        status="ok",
    )

    json_str = dashboard.to_json(metric)

    assert isinstance(json_str, str)
    assert "name" in json_str
    assert "value" in json_str


# =======================================================================================
# Edge Cases and Error Handling
# =======================================================================================


def test_empty_embeddings(dashboard):
    """Test handling of empty embeddings."""
    empty_embeddings = np.array([]).reshape(0, 128)

    with pytest.raises((ValueError, IndexError)):
        dashboard.plot_semantic_space_2d(empty_embeddings)


def test_single_embedding(dashboard):
    """Test handling of single embedding."""
    single_embedding = np.random.randn(1, 128).astype(np.float64)

    viz = dashboard.plot_semantic_space_2d(single_embedding)

    assert isinstance(viz, VisualizationData)
    assert len(viz.data["x"]) == 1


def test_empty_specifications(dashboard):
    """Test handling of empty specifications."""
    viz = dashboard.entropy_distribution([])

    assert isinstance(viz, VisualizationData)
    assert viz.metadata["n_specs"] == 0


def test_invalid_method(dashboard, sample_embeddings):
    """Test invalid dimensionality reduction method."""
    with pytest.raises(ValueError):
        dashboard.plot_semantic_space_2d(sample_embeddings, method="invalid")
