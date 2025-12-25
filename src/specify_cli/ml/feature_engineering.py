"""
specify_cli.ml.feature_engineering - Feature Extraction and Transformation
===========================================================================

Comprehensive feature engineering pipeline for command telemetry data.

This module provides tools for:
- Extracting features from command metadata and telemetry
- Feature normalization and scaling
- Feature selection using statistical methods
- Dimensionality reduction with PCA
- Feature transformation pipelines

Classes
-------
FeatureExtractor
    Extract features from command metadata and telemetry
FeatureNormalizer
    Normalize and scale features for ML models
FeatureSelector
    Select most important features using SelectKBest
FeatureTransformer
    Complete feature transformation pipeline

Example
-------
    >>> from specify_cli.ml import FeatureExtractor, FeatureTransformer
    >>>
    >>> # Extract features
    >>> extractor = FeatureExtractor()
    >>> features = extractor.extract_command_features({
    ...     'command': 'pytest tests/',
    ...     'duration': 5.2,
    ...     'exit_code': 0
    ... })
    >>>
    >>> # Transform for ML
    >>> transformer = FeatureTransformer()
    >>> transformer.fit(training_features)
    >>> transformed = transformer.transform(features)

See Also
--------
- :mod:`specify_cli.ml.optimizer` : ML optimization models
- :mod:`specify_cli.ml.models` : Model training and validation
"""

from __future__ import annotations

import hashlib
import logging
from typing import TYPE_CHECKING, Any

import numpy as np
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.preprocessing import RobustScaler, StandardScaler

from specify_cli.core.telemetry import metric_counter, span

if TYPE_CHECKING:
    from numpy.typing import NDArray

__all__ = [
    "FeatureExtractor",
    "FeatureNormalizer",
    "FeatureSelector",
    "FeatureTransformer",
]

_log = logging.getLogger("specify_cli.ml.features")


class FeatureExtractor:
    """Extract ML features from command metadata and telemetry.

    This class converts raw command execution data into structured features
    suitable for machine learning models.

    Attributes
    ----------
    feature_names : list[str]
        Names of extracted features
    categorical_features : dict[str, dict[str, int]]
        Mappings for categorical feature encoding

    Example
    -------
    >>> extractor = FeatureExtractor()
    >>> metadata = {
    ...     'command': 'pytest tests/',
    ...     'duration': 5.2,
    ...     'exit_code': 0,
    ...     'working_directory': '/home/user/project'
    ... }
    >>> features = extractor.extract_command_features(metadata)
    >>> print(features)
    array([5.2, 0, 1, ...])
    """

    def __init__(self) -> None:
        """Initialize the feature extractor."""
        self.feature_names: list[str] = []
        self.categorical_features: dict[str, dict[str, int]] = {}

    def extract_command_features(
        self, metadata: dict[str, Any]
    ) -> NDArray[np.float64]:
        """Extract features from command metadata.

        Parameters
        ----------
        metadata : dict[str, Any]
            Command execution metadata containing:
            - command : str - Command string
            - duration : float - Execution time in seconds
            - exit_code : int - Process exit code
            - working_directory : str - Working directory path
            - capture : bool - Whether output was captured
            - quiet : bool - Whether quiet mode was enabled
            - timestamp : float - Unix timestamp

        Returns
        -------
        NDArray[np.float64]
            Feature vector of shape (n_features,)
        """
        with span("ml.features.extract"):
            features = []
            self.feature_names = []

            # Numeric features
            features.append(metadata.get("duration", 0.0))
            self.feature_names.append("duration")

            features.append(float(metadata.get("exit_code", 0)))
            self.feature_names.append("exit_code")

            # Command-based features
            command = metadata.get("command", "")
            features.extend(self._extract_command_features(command))

            # Path-based features
            working_dir = metadata.get("working_directory", "")
            features.extend(self._extract_path_features(working_dir))

            # Boolean features
            features.append(float(metadata.get("capture", False)))
            self.feature_names.append("capture")

            features.append(float(metadata.get("quiet", False)))
            self.feature_names.append("quiet")

            # Temporal features
            timestamp = metadata.get("timestamp", 0.0)
            features.extend(self._extract_temporal_features(timestamp))

            # Record metrics
            metric_counter("ml.features.extracted")(1)

            return np.array(features, dtype=np.float64)

    def _extract_command_features(self, command: str) -> list[float]:
        """Extract features from command string.

        Parameters
        ----------
        command : str
            Command string

        Returns
        -------
        list[float]
            Command-based features
        """
        features = []

        # Command length
        features.append(float(len(command)))
        self.feature_names.append("command_length")

        # Number of arguments
        args = command.split()
        features.append(float(len(args)))
        self.feature_names.append("n_args")

        # Command complexity (average argument length)
        avg_arg_length = np.mean([len(arg) for arg in args]) if args else 0.0
        features.append(avg_arg_length)  # type: ignore[Any]
        self.feature_names.append("avg_arg_length")

        # Command hash (for categorical encoding)
        command_base = args[0] if args else ""
        command_hash = self._hash_categorical(command_base, "command_type")
        features.append(float(command_hash))
        self.feature_names.append("command_type_hash")

        # Detect common patterns
        features.append(float("test" in command.lower()))
        self.feature_names.append("is_test_command")

        features.append(float("build" in command.lower()))
        self.feature_names.append("is_build_command")

        features.append(float("git" in command.lower()))
        self.feature_names.append("is_git_command")

        features.append(float("docker" in command.lower()))
        self.feature_names.append("is_docker_command")

        features.append(float("npm" in command.lower() or "yarn" in command.lower()))
        self.feature_names.append("is_npm_command")

        features.append(float("python" in command.lower() or "pytest" in command.lower()))
        self.feature_names.append("is_python_command")

        return features

    def _extract_path_features(self, path: str) -> list[float]:
        """Extract features from file path.

        Parameters
        ----------
        path : str
            File or directory path

        Returns
        -------
        list[float]
            Path-based features
        """
        features = []

        # Path depth
        depth = len(path.split("/")) if path else 0
        features.append(float(depth))
        self.feature_names.append("path_depth")

        # Path length
        features.append(float(len(path)))
        self.feature_names.append("path_length")

        # Path hash (for categorical encoding)
        path_hash = self._hash_categorical(path, "working_dir")
        features.append(float(path_hash))
        self.feature_names.append("working_dir_hash")

        return features

    def _extract_temporal_features(self, timestamp: float) -> list[float]:
        """Extract temporal features from timestamp.

        Parameters
        ----------
        timestamp : float
            Unix timestamp

        Returns
        -------
        list[float]
            Temporal features
        """
        import datetime

        features = []

        if timestamp > 0:
            dt = datetime.datetime.fromtimestamp(timestamp, tz=datetime.UTC)

            # Hour of day (cyclical encoding)
            hour = dt.hour
            hour_sin = np.sin(2 * np.pi * hour / 24)
            hour_cos = np.cos(2 * np.pi * hour / 24)
            features.append(hour_sin)
            features.append(hour_cos)
            self.feature_names.extend(["hour_sin", "hour_cos"])

            # Day of week (cyclical encoding)
            day = dt.weekday()
            day_sin = np.sin(2 * np.pi * day / 7)
            day_cos = np.cos(2 * np.pi * day / 7)
            features.append(day_sin)
            features.append(day_cos)
            self.feature_names.extend(["day_sin", "day_cos"])

            # Weekend indicator
            features.append(float(day >= 5))
            self.feature_names.append("is_weekend")
        else:
            # Missing timestamp - use zeros
            features.extend([0.0] * 5)
            self.feature_names.extend(
                ["hour_sin", "hour_cos", "day_sin", "day_cos", "is_weekend"]
            )

        return features

    def _hash_categorical(self, value: str, category: str) -> int:
        """Hash categorical value to integer.

        Parameters
        ----------
        value : str
            Categorical value
        category : str
            Category name

        Returns
        -------
        int
            Hash code
        """
        if category not in self.categorical_features:
            self.categorical_features[category] = {}

        if value not in self.categorical_features[category]:
            # Create stable hash
            hash_obj = hashlib.md5(value.encode(), usedforsecurity=False)
            hash_value = int(hash_obj.hexdigest()[:8], 16)
            self.categorical_features[category][value] = hash_value

        return self.categorical_features[category][value]

    def get_feature_names(self) -> list[str]:
        """Get names of extracted features.

        Returns
        -------
        list[str]
            Feature names
        """
        return self.feature_names.copy()


class FeatureNormalizer:
    """Normalize and scale features for ML models.

    This class provides robust scaling that handles outliers well and
    standardization for features that follow normal distributions.

    Parameters
    ----------
    method : {'standard', 'robust'}, optional
        Normalization method, by default 'robust'
        - 'standard': StandardScaler (mean=0, std=1)
        - 'robust': RobustScaler (median=0, IQR=1)

    Attributes
    ----------
    scaler : StandardScaler | RobustScaler
        Fitted scaler instance
    is_fitted : bool
        Whether scaler has been fitted

    Example
    -------
    >>> normalizer = FeatureNormalizer(method='robust')
    >>> normalizer.fit(X_train)
    >>> X_scaled = normalizer.transform(X_test)
    """

    def __init__(self, method: str = "robust") -> None:
        """Initialize the feature normalizer."""
        if method == "standard":
            self.scaler = StandardScaler()
        elif method == "robust":
            self.scaler = RobustScaler()  # type: ignore[assignment]
        else:
            msg = f"Unknown normalization method: {method}"
            raise ValueError(msg)

        self.method = method
        self.is_fitted = False

    def fit(self, X: NDArray[np.float64]) -> FeatureNormalizer:
        """Fit the normalizer to training data.

        Parameters
        ----------
        X : NDArray[np.float64]
            Training features of shape (n_samples, n_features)

        Returns
        -------
        FeatureNormalizer
            Self for method chaining
        """
        with span("ml.features.normalize.fit", method=self.method):
            _log.info(f"Fitting {self.method} scaler on {len(X)} samples")

            self.scaler.fit(X)
            self.is_fitted = True

            metric_counter("ml.features.normalizer.fitted")(1)

            return self

    def transform(self, X: NDArray[np.float64]) -> NDArray[np.float64]:
        """Transform features using fitted scaler.

        Parameters
        ----------
        X : NDArray[np.float64]
            Features to transform

        Returns
        -------
        NDArray[np.float64]
            Normalized features

        Raises
        ------
        RuntimeError
            If normalizer has not been fitted
        """
        if not self.is_fitted:
            msg = "Normalizer must be fitted before transform"
            raise RuntimeError(msg)

        with span("ml.features.normalize.transform"):
            return self.scaler.transform(X)

    def fit_transform(self, X: NDArray[np.float64]) -> NDArray[np.float64]:
        """Fit normalizer and transform features in one step.

        Parameters
        ----------
        X : NDArray[np.float64]
            Training features

        Returns
        -------
        NDArray[np.float64]
            Normalized features
        """
        return self.fit(X).transform(X)

    def inverse_transform(self, X: NDArray[np.float64]) -> NDArray[np.float64]:
        """Inverse transform normalized features back to original scale.

        Parameters
        ----------
        X : NDArray[np.float64]
            Normalized features

        Returns
        -------
        NDArray[np.float64]
            Original scale features
        """
        if not self.is_fitted:
            msg = "Normalizer must be fitted before inverse_transform"
            raise RuntimeError(msg)

        return self.scaler.inverse_transform(X)


class FeatureSelector:
    """Select most important features using statistical tests.

    This class uses univariate feature selection to identify the k best
    features based on F-statistic from regression analysis.

    Parameters
    ----------
    k : int | str, optional
        Number of top features to select, by default 10
        Can also be 'all' to select all features
    score_func : Callable[..., Any][..., Any][..., Any], optional
        Score function for feature ranking, by default f_regression

    Attributes
    ----------
    selector : SelectKBest
        Fitted feature selector
    is_fitted : bool
        Whether selector has been fitted
    selected_indices : NDArray[np.int64] | None
        Indices of selected features
    feature_scores : NDArray[np.float64] | None
        Scores for each feature

    Example
    -------
    >>> selector = FeatureSelector(k=5)
    >>> selector.fit(X_train, y_train)
    >>> X_selected = selector.transform(X_test)
    >>> print(f"Selected {X_selected.shape[1]} features")
    """

    def __init__(self, k: int | str = 10, score_func: Any = f_regression) -> None:
        """Initialize the feature selector."""
        self.selector = SelectKBest(score_func=score_func, k=k)
        self.is_fitted = False
        self.selected_indices: NDArray[np.int_] | None = None
        self.feature_scores: NDArray[np.float64] | None = None

    def fit(
        self, X: NDArray[np.float64], y: NDArray[np.float64]
    ) -> FeatureSelector:
        """Fit the feature selector.

        Parameters
        ----------
        X : NDArray[np.float64]
            Training features of shape (n_samples, n_features)
        y : NDArray[np.float64]
            Target values of shape (n_samples,)

        Returns
        -------
        FeatureSelector
            Self for method chaining
        """
        with span("ml.features.select.fit", n_features=X.shape[1]):
            _log.info(f"Selecting top {self.selector.k} features from {X.shape[1]}")

            self.selector.fit(X, y)
            self.is_fitted = True

            # Store selected feature info
            self.selected_indices = self.selector.get_support(indices=True)  # type: ignore[assignment]
            self.feature_scores = self.selector.scores_

            metric_counter("ml.features.selector.fitted")(1)

            _log.info(f"Selected {len(self.selected_indices)} features")  # type: ignore[arg-type]

            return self

    def transform(self, X: NDArray[np.float64]) -> NDArray[np.float64]:
        """Transform features by selecting subset.

        Parameters
        ----------
        X : NDArray[np.float64]
            Features to transform

        Returns
        -------
        NDArray[np.float64]
            Selected features

        Raises
        ------
        RuntimeError
            If selector has not been fitted
        """
        if not self.is_fitted:
            msg = "Selector must be fitted before transform"
            raise RuntimeError(msg)

        with span("ml.features.select.transform"):
            return self.selector.transform(X)

    def fit_transform(
        self, X: NDArray[np.float64], y: NDArray[np.float64]
    ) -> NDArray[np.float64]:
        """Fit selector and transform features in one step.

        Parameters
        ----------
        X : NDArray[np.float64]
            Training features
        y : NDArray[np.float64]
            Target values

        Returns
        -------
        NDArray[np.float64]
            Selected features
        """
        return self.fit(X, y).transform(X)

    def get_feature_ranking(
        self, feature_names: list[str] | None = None
    ) -> dict[str, float]:
        """Get feature importance ranking.

        Parameters
        ----------
        feature_names : list[str], optional
            Names of features

        Returns
        -------
        dict[str, float]
            Feature names (or indices) mapped to scores

        Raises
        ------
        RuntimeError
            If selector has not been fitted
        """
        if not self.is_fitted or self.feature_scores is None:
            msg = "Selector must be fitted to get ranking"
            raise RuntimeError(msg)

        if feature_names:
            return dict(zip(feature_names, self.feature_scores, strict=False))

        return {f"feature_{i}": score for i, score in enumerate(self.feature_scores)}


class FeatureTransformer:
    """Complete feature transformation pipeline.

    This class combines feature extraction, normalization, selection,
    and optional dimensionality reduction into a single pipeline.

    Parameters
    ----------
    normalize : bool, optional
        Whether to normalize features, by default True
    normalization_method : str, optional
        Normalization method ('standard' or 'robust'), by default 'robust'
    select_features : bool, optional
        Whether to select top features, by default True
    n_features : int | str, optional
        Number of features to select, by default 10
    reduce_dimensions : bool, optional
        Whether to apply PCA, by default False
    n_components : int | float, optional
        Number of PCA components or variance to retain, by default 0.95

    Attributes
    ----------
    extractor : FeatureExtractor
        Feature extraction component
    normalizer : FeatureNormalizer | None
        Normalization component
    selector : FeatureSelector | None
        Feature selection component
    pca : PCA | None
        Dimensionality reduction component
    is_fitted : bool
        Whether pipeline has been fitted

    Example
    -------
    >>> transformer = FeatureTransformer(
    ...     normalize=True,
    ...     select_features=True,
    ...     n_features=10
    ... )
    >>> transformer.fit(X_train, y_train)
    >>> X_transformed = transformer.transform(X_test)
    """

    def __init__(
        self,
        normalize: bool = True,
        normalization_method: str = "robust",
        select_features: bool = True,
        n_features: int | str = 10,
        reduce_dimensions: bool = False,
        n_components: int | float = 0.95,
    ) -> None:
        """Initialize the feature transformer."""
        self.extractor = FeatureExtractor()
        self.normalizer = (
            FeatureNormalizer(method=normalization_method) if normalize else None
        )
        self.selector = FeatureSelector(k=n_features) if select_features else None
        self.pca = PCA(n_components=n_components) if reduce_dimensions else None

        self.normalize = normalize
        self.select_features = select_features
        self.reduce_dimensions = reduce_dimensions

    @property
    def is_fitted(self) -> bool:
        """Check if transformer is fitted."""
        if self.normalizer and not self.normalizer.is_fitted:
            return False
        if self.selector and not self.selector.is_fitted:
            return False
        if self.pca and not hasattr(self.pca, "components_"):
            return False
        return True

    def fit(
        self,
        X: NDArray[np.float64],
        y: NDArray[np.float64] | None = None,
    ) -> FeatureTransformer:
        """Fit the transformation pipeline.

        Parameters
        ----------
        X : NDArray[np.float64]
            Training features of shape (n_samples, n_features)
        y : NDArray[np.float64], optional
            Target values for supervised feature selection

        Returns
        -------
        FeatureTransformer
            Self for method chaining
        """
        with span("ml.features.transform.fit"):
            _log.info("Fitting feature transformation pipeline")

            X_current = X

            # Normalize
            if self.normalizer:
                X_current = self.normalizer.fit_transform(X_current)

            # Select features (requires y)
            if self.selector and y is not None:
                X_current = self.selector.fit_transform(X_current, y)

            # Reduce dimensions
            if self.pca:
                self.pca.fit(X_current)

            _log.info("Feature transformation pipeline fitted")

            return self

    def transform(self, X: NDArray[np.float64]) -> NDArray[np.float64]:
        """Transform features using fitted pipeline.

        Parameters
        ----------
        X : NDArray[np.float64]
            Features to transform

        Returns
        -------
        NDArray[np.float64]
            Transformed features
        """
        with span("ml.features.transform.apply"):
            X_current = X

            # Normalize
            if self.normalizer:
                X_current = self.normalizer.transform(X_current)

            # Select features
            if self.selector:
                X_current = self.selector.transform(X_current)

            # Reduce dimensions
            if self.pca:
                X_current = self.pca.transform(X_current)

            return X_current

    def fit_transform(
        self,
        X: NDArray[np.float64],
        y: NDArray[np.float64] | None = None,
    ) -> NDArray[np.float64]:
        """Fit and transform features in one step.

        Parameters
        ----------
        X : NDArray[np.float64]
            Training features
        y : NDArray[np.float64], optional
            Target values

        Returns
        -------
        NDArray[np.float64]
            Transformed features
        """
        return self.fit(X, y).transform(X)
