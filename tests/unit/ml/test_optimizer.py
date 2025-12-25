"""Unit tests for ML optimizer module."""

from __future__ import annotations

import numpy as np
import pytest

from specify_cli.ml.optimizer import (
    AnomalyDetector,
    CommandClusterer,
    CommandOptimizer,
    PerformancePredictor,
)


@pytest.fixture
def synthetic_data() -> tuple[np.ndarray, np.ndarray]:
    """Generate synthetic training data."""
    np.random.seed(42)
    X = np.random.randn(100, 10)
    y = 3 * X[:, 0] + 2 * X[:, 1] + np.random.normal(0, 0.5, 100)
    y = np.abs(y) + 0.1  # Ensure positive
    return X, y


@pytest.fixture
def test_data() -> tuple[np.ndarray, np.ndarray]:
    """Generate synthetic test data."""
    np.random.seed(43)
    X = np.random.randn(20, 10)
    y = 3 * X[:, 0] + 2 * X[:, 1] + np.random.normal(0, 0.5, 20)
    y = np.abs(y) + 0.1
    return X, y


class TestPerformancePredictor:
    """Test PerformancePredictor class."""

    def test_initialization(self) -> None:
        """Test predictor initialization."""
        predictor = PerformancePredictor(n_estimators=50, max_depth=10)
        assert predictor.model.n_estimators == 50
        assert predictor.model.max_depth == 10
        assert not predictor.is_fitted

    def test_fit(self, synthetic_data: tuple[np.ndarray, np.ndarray]) -> None:
        """Test model training."""
        X, y = synthetic_data
        predictor = PerformancePredictor()

        result = predictor.fit(X, y, feature_names=[f"f{i}" for i in range(10)])

        assert predictor.is_fitted
        assert predictor.training_score is not None
        assert predictor.training_score > 0.5  # Should have decent fit
        assert result is predictor  # Returns self

    def test_predict(self, synthetic_data: tuple[np.ndarray, np.ndarray]) -> None:
        """Test prediction with confidence intervals."""
        X, y = synthetic_data
        predictor = PerformancePredictor()
        predictor.fit(X, y)

        # Single sample prediction
        result = predictor.predict(X[0])
        assert result.predicted_time > 0
        assert len(result.confidence_interval) == 2
        assert result.confidence_interval[0] < result.predicted_time < result.confidence_interval[1]

    def test_predict_batch(self, synthetic_data: tuple[np.ndarray, np.ndarray]) -> None:
        """Test batch prediction."""
        X, y = synthetic_data
        predictor = PerformancePredictor()
        predictor.fit(X, y)

        results = predictor.predict(X[:5])
        assert isinstance(results, list)
        assert len(results) == 5

    def test_feature_importance(self, synthetic_data: tuple[np.ndarray, np.ndarray]) -> None:
        """Test feature importance extraction."""
        X, y = synthetic_data
        predictor = PerformancePredictor()
        predictor.fit(X, y, feature_names=[f"feature_{i}" for i in range(10)])

        importance = predictor.get_feature_importance()
        assert len(importance) == 10
        assert all(0 <= v <= 1 for v in importance.values())

    def test_predict_unfitted_raises(self) -> None:
        """Test that predicting before fitting raises error."""
        predictor = PerformancePredictor()
        X = np.random.randn(1, 10)

        with pytest.raises(RuntimeError, match="Model must be fitted"):
            predictor.predict(X)


class TestAnomalyDetector:
    """Test AnomalyDetector class."""

    def test_initialization(self) -> None:
        """Test detector initialization."""
        detector = AnomalyDetector(contamination=0.05, n_estimators=50)
        assert detector.model.contamination == 0.05
        assert detector.model.n_estimators == 50
        assert not detector.is_fitted

    def test_fit(self, synthetic_data: tuple[np.ndarray, np.ndarray]) -> None:
        """Test anomaly detector training."""
        X, _ = synthetic_data
        detector = AnomalyDetector()

        result = detector.fit(X)

        assert detector.is_fitted
        assert detector.threshold is not None
        assert result is detector

    def test_detect(self, synthetic_data: tuple[np.ndarray, np.ndarray]) -> None:
        """Test anomaly detection."""
        X, _ = synthetic_data
        detector = AnomalyDetector()
        detector.fit(X)

        # Single sample
        result = detector.detect(X[0])
        assert isinstance(result.is_anomaly, bool)
        assert 0 <= result.confidence <= 1

        # Create obvious anomaly
        anomaly = np.ones(10) * 100
        result_anomaly = detector.detect(anomaly)
        # Likely to be detected as anomaly
        assert isinstance(result_anomaly.is_anomaly, bool)

    def test_detect_batch(self, synthetic_data: tuple[np.ndarray, np.ndarray]) -> None:
        """Test batch anomaly detection."""
        X, _ = synthetic_data
        detector = AnomalyDetector()
        detector.fit(X)

        results = detector.detect(X[:5])
        assert isinstance(results, list)
        assert len(results) == 5


class TestCommandClusterer:
    """Test CommandClusterer class."""

    def test_initialization(self) -> None:
        """Test clusterer initialization."""
        clusterer = CommandClusterer(n_clusters=3)
        assert clusterer.model.n_clusters == 3
        assert not clusterer.is_fitted

    def test_fit(self, synthetic_data: tuple[np.ndarray, np.ndarray]) -> None:
        """Test clustering training."""
        X, _ = synthetic_data
        clusterer = CommandClusterer(n_clusters=3)

        result = clusterer.fit(X)

        assert clusterer.is_fitted
        assert result is clusterer

    def test_get_cluster(self, synthetic_data: tuple[np.ndarray, np.ndarray]) -> None:
        """Test cluster assignment."""
        X, _ = synthetic_data
        clusterer = CommandClusterer(n_clusters=5)
        clusterer.fit(X)

        # Single sample
        result = clusterer.get_cluster(X[0])
        assert 0 <= result.cluster_id < 5
        assert result.cluster_name in clusterer.cluster_names

    def test_get_cluster_batch(self, synthetic_data: tuple[np.ndarray, np.ndarray]) -> None:
        """Test batch clustering."""
        X, _ = synthetic_data
        clusterer = CommandClusterer(n_clusters=5)
        clusterer.fit(X)

        results = clusterer.get_cluster(X[:5])
        assert isinstance(results, list)
        assert len(results) == 5


class TestCommandOptimizer:
    """Test integrated CommandOptimizer class."""

    def test_initialization(self) -> None:
        """Test optimizer initialization."""
        optimizer = CommandOptimizer()
        assert optimizer.predictor is not None
        assert optimizer.detector is not None
        assert optimizer.clusterer is not None
        assert not optimizer.is_fitted

    def test_fit(self, synthetic_data: tuple[np.ndarray, np.ndarray]) -> None:
        """Test optimizer training."""
        X, y = synthetic_data
        optimizer = CommandOptimizer()

        result = optimizer.fit(X, y)

        assert optimizer.is_fitted
        assert optimizer.predictor.is_fitted
        assert optimizer.detector.is_fitted
        assert optimizer.clusterer.is_fitted
        assert result is optimizer

    def test_predict_execution_time(
        self, synthetic_data: tuple[np.ndarray, np.ndarray]
    ) -> None:
        """Test execution time prediction."""
        X, y = synthetic_data
        optimizer = CommandOptimizer()
        optimizer.fit(X, y)

        result = optimizer.predict_execution_time(X[0])
        assert result.predicted_time > 0

    def test_detect_anomaly(
        self, synthetic_data: tuple[np.ndarray, np.ndarray]
    ) -> None:
        """Test anomaly detection."""
        X, y = synthetic_data
        optimizer = CommandOptimizer()
        optimizer.fit(X, y)

        result = optimizer.detect_anomaly(X[0])
        assert isinstance(result.is_anomaly, bool)

    def test_get_cluster(
        self, synthetic_data: tuple[np.ndarray, np.ndarray]
    ) -> None:
        """Test cluster assignment."""
        X, y = synthetic_data
        optimizer = CommandOptimizer()
        optimizer.fit(X, y)

        result = optimizer.get_cluster(X[0])
        assert 0 <= result.cluster_id < 5

    def test_optimize(self, synthetic_data: tuple[np.ndarray, np.ndarray]) -> None:
        """Test comprehensive optimization."""
        X, y = synthetic_data
        optimizer = CommandOptimizer()
        optimizer.fit(X, y)

        result = optimizer.optimize(X[0])

        assert "prediction" in result
        assert "anomaly" in result
        assert "cluster" in result
