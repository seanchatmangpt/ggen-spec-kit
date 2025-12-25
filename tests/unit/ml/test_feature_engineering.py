"""Unit tests for ML feature engineering module."""

from __future__ import annotations

import numpy as np
import pytest

from specify_cli.ml.feature_engineering import (
    FeatureExtractor,
    FeatureNormalizer,
    FeatureSelector,
    FeatureTransformer,
)


class TestFeatureExtractor:
    """Test FeatureExtractor class."""

    def test_extract_command_features(self) -> None:
        """Test feature extraction from command metadata."""
        extractor = FeatureExtractor()

        metadata = {
            "command": "pytest tests/ -v --cov",
            "duration": 5.2,
            "exit_code": 0,
            "working_directory": "/home/user/project",
            "capture": True,
            "quiet": False,
            "timestamp": 1703001234.5,
        }

        features = extractor.extract_command_features(metadata)

        assert isinstance(features, np.ndarray)
        assert len(features) > 0
        assert features[0] == 5.2  # duration
        assert features[1] == 0.0  # exit_code

    def test_feature_names(self) -> None:
        """Test feature name extraction."""
        extractor = FeatureExtractor()

        metadata = {
            "command": "test",
            "duration": 1.0,
            "exit_code": 0,
            "working_directory": "/",
            "timestamp": 0.0,
        }

        extractor.extract_command_features(metadata)
        names = extractor.get_feature_names()

        assert "duration" in names
        assert "exit_code" in names
        assert "command_length" in names

    def test_command_features(self) -> None:
        """Test command-specific feature extraction."""
        extractor = FeatureExtractor()

        # Test command - check that is_test_command flag is set
        features_test = extractor._extract_command_features("pytest tests/")
        # is_test_command is 6th from end (including python flag)
        assert features_test[4] == 1.0  # is_test_command flag

        # Git command - check that is_git_command flag is set
        features_git = extractor._extract_command_features("git commit -m msg")
        assert features_git[6] == 1.0  # is_git_command flag

    def test_temporal_features(self) -> None:
        """Test temporal feature extraction."""
        import time

        extractor = FeatureExtractor()
        ts = time.time()

        temporal = extractor._extract_temporal_features(ts)

        assert len(temporal) == 5
        # Check cyclical encoding
        assert -1 <= temporal[0] <= 1  # hour_sin
        assert -1 <= temporal[1] <= 1  # hour_cos


class TestFeatureNormalizer:
    """Test FeatureNormalizer class."""

    @pytest.fixture
    def sample_data(self) -> np.ndarray:
        """Generate sample data for normalization."""
        np.random.seed(42)
        return np.random.randn(100, 5) * 10 + 50

    def test_standard_scaler(self, sample_data: np.ndarray) -> None:
        """Test standard normalization."""
        normalizer = FeatureNormalizer(method="standard")
        X_scaled = normalizer.fit_transform(sample_data)

        # Check mean and std
        assert np.abs(np.mean(X_scaled)) < 0.1
        assert np.abs(np.std(X_scaled) - 1.0) < 0.1
        assert normalizer.is_fitted

    def test_robust_scaler(self, sample_data: np.ndarray) -> None:
        """Test robust normalization."""
        normalizer = FeatureNormalizer(method="robust")
        X_scaled = normalizer.fit_transform(sample_data)

        assert normalizer.is_fitted
        assert X_scaled.shape == sample_data.shape

    def test_inverse_transform(self, sample_data: np.ndarray) -> None:
        """Test inverse transformation."""
        normalizer = FeatureNormalizer(method="standard")
        X_scaled = normalizer.fit_transform(sample_data)
        X_restored = normalizer.inverse_transform(X_scaled)

        # Should be close to original
        np.testing.assert_array_almost_equal(X_restored, sample_data, decimal=5)

    def test_unfitted_transform_raises(self) -> None:
        """Test that transforming before fitting raises error."""
        normalizer = FeatureNormalizer()
        X = np.random.randn(10, 5)

        with pytest.raises(RuntimeError, match="Normalizer must be fitted"):
            normalizer.transform(X)


class TestFeatureSelector:
    """Test FeatureSelector class."""

    @pytest.fixture
    def sample_data(self) -> tuple[np.ndarray, np.ndarray]:
        """Generate sample data with known important features."""
        np.random.seed(42)
        X = np.random.randn(100, 20)
        # Only first 3 features are important
        y = 5 * X[:, 0] + 3 * X[:, 1] + 2 * X[:, 2] + np.random.normal(0, 0.1, 100)
        return X, y

    def test_fit(self, sample_data: tuple[np.ndarray, np.ndarray]) -> None:
        """Test feature selector training."""
        X, y = sample_data
        selector = FeatureSelector(k=5)

        selector.fit(X, y)

        assert selector.is_fitted
        assert len(selector.selected_indices) == 5
        assert selector.feature_scores is not None

    def test_transform(self, sample_data: tuple[np.ndarray, np.ndarray]) -> None:
        """Test feature selection."""
        X, y = sample_data
        selector = FeatureSelector(k=5)
        selector.fit(X, y)

        X_selected = selector.transform(X)

        assert X_selected.shape[0] == X.shape[0]
        assert X_selected.shape[1] == 5

    def test_feature_ranking(self, sample_data: tuple[np.ndarray, np.ndarray]) -> None:
        """Test feature importance ranking."""
        X, y = sample_data
        selector = FeatureSelector(k=10)
        selector.fit(X, y)

        ranking = selector.get_feature_ranking()

        assert len(ranking) == X.shape[1]
        # First features should have highest scores
        scores = list(ranking.values())
        assert scores[0] > scores[-1]


class TestFeatureTransformer:
    """Test integrated FeatureTransformer pipeline."""

    @pytest.fixture
    def sample_data(self) -> tuple[np.ndarray, np.ndarray]:
        """Generate sample data."""
        np.random.seed(42)
        X = np.random.randn(100, 20) * 10
        y = 3 * X[:, 0] + 2 * X[:, 1] + np.random.normal(0, 0.5, 100)
        return X, y

    def test_initialization(self) -> None:
        """Test transformer initialization."""
        transformer = FeatureTransformer(
            normalize=True,
            select_features=True,
            reduce_dimensions=True,
        )

        assert transformer.normalizer is not None
        assert transformer.selector is not None
        assert transformer.pca is not None

    def test_fit_transform(
        self, sample_data: tuple[np.ndarray, np.ndarray]
    ) -> None:
        """Test complete transformation pipeline."""
        X, y = sample_data
        transformer = FeatureTransformer(
            normalize=True,
            select_features=True,
            n_features=10,
            reduce_dimensions=False,
        )

        X_transformed = transformer.fit_transform(X, y)

        assert X_transformed.shape[0] == X.shape[0]
        assert X_transformed.shape[1] == 10
        assert transformer.is_fitted

    def test_with_pca(self, sample_data: tuple[np.ndarray, np.ndarray]) -> None:
        """Test transformation with PCA."""
        X, y = sample_data
        transformer = FeatureTransformer(
            normalize=True,
            select_features=True,
            n_features=15,
            reduce_dimensions=True,
            n_components=5,
        )

        X_transformed = transformer.fit_transform(X, y)

        assert X_transformed.shape[1] == 5  # PCA reduced to 5 components
