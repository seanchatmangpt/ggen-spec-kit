"""
specify_cli.ml.optimizer - ML-Powered Command Optimization
==========================================================

Hyper-advanced machine learning optimizer using scikit-learn for:
- Performance prediction using RandomForestRegressor
- Anomaly detection using IsolationForest
- Command clustering using KMeans
- Resource allocation optimization

This module provides the main ML optimization pipeline that integrates
predictive models, anomaly detection, and clustering for intelligent
command execution optimization.

Classes
-------
PerformancePredictor
    Predict command execution time using Random Forest regression
AnomalyDetector
    Detect anomalous command performance using Isolation Forest
CommandClusterer
    Cluster commands by complexity and resource usage with KMeans
CommandOptimizer
    Integrated optimizer combining all ML models

Example
-------
    >>> from specify_cli.ml import CommandOptimizer
    >>>
    >>> # Create and train optimizer
    >>> optimizer = CommandOptimizer()
    >>> optimizer.fit(training_data)
    >>>
    >>> # Predict performance
    >>> predicted_time = optimizer.predict_execution_time(command_features)
    >>>
    >>> # Detect anomalies
    >>> is_anomaly, anomaly_score = optimizer.detect_anomaly(command_features)
    >>>
    >>> # Get command cluster
    >>> cluster_id, cluster_name = optimizer.get_cluster(command_features)

See Also
--------
- :mod:`specify_cli.ml.feature_engineering` : Feature extraction and transformation
- :mod:`specify_cli.ml.models` : Model training and validation
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    silhouette_score,
)

from specify_cli.core.telemetry import metric_counter, metric_histogram, span

if TYPE_CHECKING:
    from numpy.typing import NDArray

__all__ = [
    "AnomalyDetector",
    "AnomalyResult",
    "ClusterResult",
    "CommandClusterer",
    "CommandOptimizer",
    "PerformancePredictor",
    "PredictionResult",
]

_log = logging.getLogger("specify_cli.ml.optimizer")


@dataclass
class PredictionResult:
    """Result from performance prediction.

    Attributes
    ----------
    predicted_time : float
        Predicted execution time in seconds
    confidence_interval : tuple[float, float]
        95% confidence interval (lower, upper)
    feature_importance : dict[str, float]
        Feature importance scores
    model_version : str
        Version of the model used
    timestamp : float
        Unix timestamp of prediction
    """

    predicted_time: float
    confidence_interval: tuple[float, float]
    feature_importance: dict[str, float]
    model_version: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class AnomalyResult:
    """Result from anomaly detection.

    Attributes
    ----------
    is_anomaly : bool
        Whether the instance is anomalous
    anomaly_score : float
        Anomaly score (lower is more normal)
    threshold : float
        Decision threshold used
    confidence : float
        Confidence in the prediction (0-1)
    timestamp : float
        Unix timestamp of detection
    """

    is_anomaly: bool
    anomaly_score: float
    threshold: float
    confidence: float
    timestamp: float = field(default_factory=time.time)


@dataclass
class ClusterResult:
    """Result from command clustering.

    Attributes
    ----------
    cluster_id : int
        Cluster identifier (0-based)
    cluster_name : str
        Human-readable cluster name
    distance_to_center : float
        Euclidean distance to cluster center
    inertia : float
        Sum of squared distances to nearest cluster center
    silhouette : float
        Silhouette coefficient (-1 to 1)
    timestamp : float
        Unix timestamp of clustering
    """

    cluster_id: int
    cluster_name: str
    distance_to_center: float
    inertia: float
    silhouette: float
    timestamp: float = field(default_factory=time.time)


class PerformancePredictor:
    """Predict command execution time using Random Forest Regression.

    This predictor uses ensemble learning to estimate command execution time
    based on historical performance data and command features.

    Parameters
    ----------
    n_estimators : int, optional
        Number of trees in the forest, by default 100
    max_depth : int, optional
        Maximum depth of trees, by default 20
    min_samples_split : int, optional
        Minimum samples required to split node, by default 5
    min_samples_leaf : int, optional
        Minimum samples required at leaf node, by default 2
    random_state : int, optional
        Random state for reproducibility, by default 42
    n_jobs : int, optional
        Number of parallel jobs, by default -1 (all CPUs)

    Attributes
    ----------
    model : RandomForestRegressor
        Trained Random Forest model
    is_fitted : bool
        Whether model has been fitted to data
    feature_names : list[str] | None
        Names of features used for training
    training_score : float | None
        R² score on training data
    model_version : str
        Version identifier for the model

    Example
    -------
    >>> predictor = PerformancePredictor(n_estimators=200)
    >>> predictor.fit(X_train, y_train, feature_names=['duration', 'exit_code'])
    >>> result = predictor.predict(X_test[0])
    >>> print(f"Predicted time: {result.predicted_time:.2f}s")
    """

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: int = 20,
        min_samples_split: int = 5,
        min_samples_leaf: int = 2,
        random_state: int = 42,
        n_jobs: int = -1,
    ) -> None:
        """Initialize the performance predictor."""
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            random_state=random_state,
            n_jobs=n_jobs,
            bootstrap=True,
            oob_score=True,
        )
        self.is_fitted = False
        self.feature_names: list[str] | None = None
        self.training_score: float | None = None
        self.model_version = "1.0.0"

    def fit(
        self,
        X: NDArray[np.float64],
        y: NDArray[np.float64],
        feature_names: list[str] | None = None,
    ) -> PerformancePredictor:
        """Train the performance prediction model.

        Parameters
        ----------
        X : NDArray[np.float64]
            Training features of shape (n_samples, n_features)
        y : NDArray[np.float64]
            Target values (execution times) of shape (n_samples,)
        feature_names : list[str], optional
            Names of features for interpretability

        Returns
        -------
        PerformancePredictor
            Self for method chaining

        Raises
        ------
        ValueError
            If X and y have incompatible shapes
        """
        with span(
            "ml.predictor.fit",
            n_samples=len(X),
            n_features=X.shape[1],
            n_estimators=self.model.n_estimators,
        ):
            start_time = time.time()

            # Validate input shapes
            if X.shape[0] != y.shape[0]:
                msg = f"X and y must have same number of samples: {X.shape[0]} != {y.shape[0]}"
                raise ValueError(msg) from None

            # Train the model
            _log.info(
                f"Training RandomForest with {len(X)} samples, "
                f"{X.shape[1]} features, {self.model.n_estimators} estimators"
            )

            self.model.fit(X, y)
            self.is_fitted = True
            self.feature_names = feature_names

            # Calculate training metrics
            y_pred = self.model.predict(X)
            self.training_score = r2_score(y, y_pred)
            mae = mean_absolute_error(y, y_pred)
            rmse = np.sqrt(mean_squared_error(y, y_pred))

            training_time = time.time() - start_time

            # Record metrics
            metric_histogram("ml.predictor.training.duration")(training_time)
            metric_counter("ml.predictor.training.completed")(1)

            _log.info(
                f"Training completed in {training_time:.2f}s - "
                f"R²={self.training_score:.4f}, MAE={mae:.4f}, RMSE={rmse:.4f}, "
                f"OOB Score={self.model.oob_score_:.4f}"
            )

            return self

    def predict(
        self,
        X: NDArray[np.float64],
        confidence_level: float = 0.95,
    ) -> PredictionResult | list[PredictionResult]:
        """Predict execution time with confidence intervals.

        Parameters
        ----------
        X : NDArray[np.float64]
            Features to predict on, shape (n_features,) or (n_samples, n_features)
        confidence_level : float, optional
            Confidence level for interval, by default 0.95

        Returns
        -------
        PredictionResult | list[PredictionResult]
            Prediction result(s) with confidence intervals

        Raises
        ------
        RuntimeError
            If model has not been fitted
        """
        if not self.is_fitted:
            msg = "Model must be fitted before prediction"
            raise RuntimeError(msg) from None

        with span("ml.predictor.predict", confidence_level=confidence_level):
            # Handle single sample
            single_sample = X.ndim == 1
            if single_sample:
                X = X.reshape(1, -1)

            # Get predictions from all trees
            predictions = np.array([tree.predict(X) for tree in self.model.estimators_])

            # Calculate mean and confidence interval
            mean_pred = np.mean(predictions, axis=0)
            std_pred = np.std(predictions, axis=0)

            # Calculate confidence interval using normal distribution
            z_score = 1.96 if confidence_level == 0.95 else 2.576  # 99% CI
            margin = z_score * std_pred
            lower_bound = mean_pred - margin
            upper_bound = mean_pred + margin

            # Get feature importance
            importance_dict = {}
            if self.feature_names:
                importance_dict = dict(
                    zip(self.feature_names, self.model.feature_importances_, strict=False)
                )

            # Record metrics
            metric_counter("ml.predictor.predictions")(len(X))

            # Create results
            results = []
            for i in range(len(X)):
                result = PredictionResult(
                    predicted_time=float(mean_pred[i]),
                    confidence_interval=(float(lower_bound[i]), float(upper_bound[i])),
                    feature_importance=importance_dict,
                    model_version=self.model_version,
                )
                results.append(result)

            return results[0] if single_sample else results

    def get_feature_importance(self) -> dict[str, float]:
        """Get feature importance scores.

        Returns
        -------
        dict[str, float]
            Feature names mapped to importance scores

        Raises
        ------
        RuntimeError
            If model has not been fitted
        """
        if not self.is_fitted:
            msg = "Model must be fitted to get feature importance"
            raise RuntimeError(msg) from None

        if not self.feature_names:
            return {
                f"feature_{i}": importance
                for i, importance in enumerate(self.model.feature_importances_)
            }

        return dict(zip(self.feature_names, self.model.feature_importances_, strict=False))


class AnomalyDetector:
    """Detect anomalous command performance using Isolation Forest.

    This detector identifies unusual command execution patterns that deviate
    from normal behavior, useful for detecting performance regressions.

    Parameters
    ----------
    contamination : float, optional
        Expected proportion of outliers, by default 0.1
    n_estimators : int, optional
        Number of isolation trees, by default 100
    max_samples : int | str, optional
        Number of samples to draw, by default 'auto'
    random_state : int, optional
        Random state for reproducibility, by default 42

    Attributes
    ----------
    model : IsolationForest
        Trained Isolation Forest model
    is_fitted : bool
        Whether model has been fitted
    threshold : float | None
        Decision threshold for anomaly detection

    Example
    -------
    >>> detector = AnomalyDetector(contamination=0.05)
    >>> detector.fit(X_train)
    >>> result = detector.detect(X_test[0])
    >>> if result.is_anomaly:
    ...     print(f"Anomaly detected! Score: {result.anomaly_score}")
    """

    def __init__(
        self,
        contamination: float = 0.1,
        n_estimators: int = 100,
        max_samples: int | str = "auto",
        random_state: int = 42,
    ) -> None:
        """Initialize the anomaly detector."""
        self.model = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            max_samples=max_samples,
            random_state=random_state,
            bootstrap=False,
            n_jobs=-1,
        )
        self.is_fitted = False
        self.threshold: float | None = None

    def fit(self, X: NDArray[np.float64]) -> AnomalyDetector:
        """Train the anomaly detection model.

        Parameters
        ----------
        X : NDArray[np.float64]
            Training features of shape (n_samples, n_features)

        Returns
        -------
        AnomalyDetector
            Self for method chaining
        """
        with span("ml.anomaly.fit", n_samples=len(X), n_features=X.shape[1]):
            start_time = time.time()

            _log.info(f"Training IsolationForest with {len(X)} samples")

            self.model.fit(X)
            self.is_fitted = True

            # Calculate threshold as the score of the worst normal instance
            scores = self.model.score_samples(X)
            self.threshold = float(np.percentile(scores, 10))

            training_time = time.time() - start_time

            metric_histogram("ml.anomaly.training.duration")(training_time)
            metric_counter("ml.anomaly.training.completed")(1)

            _log.info(
                f"Anomaly detection training completed in {training_time:.2f}s - "
                f"Threshold={self.threshold:.4f}"
            )

            return self

    def detect(self, X: NDArray[np.float64]) -> AnomalyResult | list[AnomalyResult]:
        """Detect anomalies in command execution data.

        Parameters
        ----------
        X : NDArray[np.float64]
            Features to analyze, shape (n_features,) or (n_samples, n_features)

        Returns
        -------
        AnomalyResult | list[AnomalyResult]
            Anomaly detection result(s)

        Raises
        ------
        RuntimeError
            If model has not been fitted
        """
        if not self.is_fitted:
            msg = "Model must be fitted before anomaly detection"
            raise RuntimeError(msg) from None

        with span("ml.anomaly.detect"):
            # Handle single sample
            single_sample = X.ndim == 1
            if single_sample:
                X = X.reshape(1, -1)

            # Get anomaly predictions and scores
            predictions = self.model.predict(X)  # -1 for anomaly, 1 for normal
            scores = self.model.score_samples(X)  # Lower is more anomalous

            # Calculate confidence (distance from threshold)
            if self.threshold is not None:
                confidence = np.abs(scores - self.threshold) / abs(self.threshold)
                confidence = np.clip(confidence, 0, 1)
            else:
                confidence = np.ones(len(X)) * 0.5

            # Record metrics
            n_anomalies = int(np.sum(predictions == -1))
            metric_counter("ml.anomaly.detections")(len(X))
            metric_counter("ml.anomaly.found")(n_anomalies)

            # Create results
            results = []
            for i in range(len(X)):
                result = AnomalyResult(
                    is_anomaly=bool(predictions[i] == -1),
                    anomaly_score=float(scores[i]),
                    threshold=self.threshold or 0.0,
                    confidence=float(confidence[i]),
                )
                results.append(result)

            return results[0] if single_sample else results


class CommandClusterer:
    """Cluster commands by complexity and resource usage with KMeans.

    This clusterer groups similar commands together for better resource
    allocation and performance optimization.

    Parameters
    ----------
    n_clusters : int, optional
        Number of clusters, by default 5
    random_state : int, optional
        Random state for reproducibility, by default 42
    max_iter : int, optional
        Maximum iterations for convergence, by default 300

    Attributes
    ----------
    model : KMeans
        Trained KMeans clustering model
    is_fitted : bool
        Whether model has been fitted
    cluster_names : list[str]
        Human-readable names for clusters

    Example
    -------
    >>> clusterer = CommandClusterer(n_clusters=3)
    >>> clusterer.fit(X_train)
    >>> result = clusterer.get_cluster(X_test[0])
    >>> print(f"Command belongs to cluster: {result.cluster_name}")
    """

    CLUSTER_NAMES = [
        "lightweight",
        "fast",
        "moderate",
        "intensive",
        "heavy",
    ]

    def __init__(
        self,
        n_clusters: int = 5,
        random_state: int = 42,
        max_iter: int = 300,
    ) -> None:
        """Initialize the command clusterer."""
        self.model = KMeans(
            n_clusters=n_clusters,
            random_state=random_state,
            max_iter=max_iter,
            n_init=10,
            algorithm="lloyd",
        )
        self.is_fitted = False
        self.cluster_names = self.CLUSTER_NAMES[:n_clusters]

    def fit(self, X: NDArray[np.float64]) -> CommandClusterer:
        """Train the clustering model.

        Parameters
        ----------
        X : NDArray[np.float64]
            Training features of shape (n_samples, n_features)

        Returns
        -------
        CommandClusterer
            Self for method chaining
        """
        with span("ml.cluster.fit", n_samples=len(X), n_clusters=self.model.n_clusters):
            start_time = time.time()

            _log.info(f"Training KMeans with {len(X)} samples, {self.model.n_clusters} clusters")

            self.model.fit(X)
            self.is_fitted = True

            # Calculate clustering quality metrics
            labels = self.model.labels_
            silhouette = silhouette_score(X, labels)
            inertia = self.model.inertia_

            training_time = time.time() - start_time

            metric_histogram("ml.cluster.training.duration")(training_time)
            metric_counter("ml.cluster.training.completed")(1)

            _log.info(
                f"Clustering completed in {training_time:.2f}s - "
                f"Inertia={inertia:.2f}, Silhouette={silhouette:.4f}"
            )

            return self

    def get_cluster(
        self, X: NDArray[np.float64]
    ) -> ClusterResult | list[ClusterResult]:
        """Get cluster assignment for command(s).

        Parameters
        ----------
        X : NDArray[np.float64]
            Features to cluster, shape (n_features,) or (n_samples, n_features)

        Returns
        -------
        ClusterResult | list[ClusterResult]
            Cluster assignment result(s)

        Raises
        ------
        RuntimeError
            If model has not been fitted
        """
        if not self.is_fitted:
            msg = "Model must be fitted before clustering"
            raise RuntimeError(msg) from None

        with span("ml.cluster.predict"):
            # Handle single sample
            single_sample = X.ndim == 1
            if single_sample:
                X = X.reshape(1, -1)

            # Get cluster assignments
            cluster_ids = self.model.predict(X)

            # Calculate distances to cluster centers
            distances = self.model.transform(X)
            min_distances = np.min(distances, axis=1)

            silhouette = silhouette_score(X, cluster_ids) if len(X) > 1 else 0.0

            # Record metrics
            metric_counter("ml.cluster.predictions")(len(X))

            # Create results
            results = []
            for i in range(len(X)):
                cluster_id = int(cluster_ids[i])
                result = ClusterResult(
                    cluster_id=cluster_id,
                    cluster_name=self.cluster_names[cluster_id],
                    distance_to_center=float(min_distances[i]),
                    inertia=float(self.model.inertia_),
                    silhouette=float(silhouette),
                )
                results.append(result)

            return results[0] if single_sample else results


class CommandOptimizer:
    """Integrated ML optimizer for command execution.

    This class combines performance prediction, anomaly detection, and
    clustering into a unified interface for comprehensive command optimization.

    Parameters
    ----------
    predictor_params : dict[str, Any], optional
        Parameters for PerformancePredictor
    detector_params : dict[str, Any], optional
        Parameters for AnomalyDetector
    clusterer_params : dict[str, Any], optional
        Parameters for CommandClusterer

    Attributes
    ----------
    predictor : PerformancePredictor
        Performance prediction model
    detector : AnomalyDetector
        Anomaly detection model
    clusterer : CommandClusterer
        Command clustering model
    is_fitted : bool
        Whether all models have been fitted

    Example
    -------
    >>> optimizer = CommandOptimizer()
    >>> optimizer.fit(X_train, y_train)
    >>>
    >>> # Comprehensive analysis
    >>> prediction = optimizer.predict_execution_time(features)
    >>> anomaly = optimizer.detect_anomaly(features)
    >>> cluster = optimizer.get_cluster(features)
    >>>
    >>> print(f"Predicted time: {prediction.predicted_time:.2f}s")
    >>> print(f"Anomaly: {anomaly.is_anomaly}")
    >>> print(f"Cluster: {cluster.cluster_name}")
    """

    def __init__(
        self,
        predictor_params: dict[str, Any] | None = None,
        detector_params: dict[str, Any] | None = None,
        clusterer_params: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the command optimizer."""
        self.predictor = PerformancePredictor(**(predictor_params or {}))
        self.detector = AnomalyDetector(**(detector_params or {}))
        self.clusterer = CommandClusterer(**(clusterer_params or {}))

    @property
    def is_fitted(self) -> bool:
        """Check if all models are fitted."""
        return (
            self.predictor.is_fitted
            and self.detector.is_fitted
            and self.clusterer.is_fitted
        )

    def fit(
        self,
        X: NDArray[np.float64],
        y: NDArray[np.float64],
        feature_names: list[str] | None = None,
    ) -> CommandOptimizer:
        """Train all ML models.

        Parameters
        ----------
        X : NDArray[np.float64]
            Training features of shape (n_samples, n_features)
        y : NDArray[np.float64]
            Target values (execution times) of shape (n_samples,)
        feature_names : list[str], optional
            Names of features for interpretability

        Returns
        -------
        CommandOptimizer
            Self for method chaining
        """
        with span("ml.optimizer.fit", n_samples=len(X)):
            _log.info("Training integrated CommandOptimizer")

            # Train all models
            self.predictor.fit(X, y, feature_names=feature_names)
            self.detector.fit(X)
            self.clusterer.fit(X)

            _log.info("CommandOptimizer training complete")

            return self

    def predict_execution_time(
        self, X: NDArray[np.float64]
    ) -> PredictionResult | list[PredictionResult]:
        """Predict command execution time.

        Parameters
        ----------
        X : NDArray[np.float64]
            Features to predict on

        Returns
        -------
        PredictionResult | list[PredictionResult]
            Prediction result(s)
        """
        return self.predictor.predict(X)

    def detect_anomaly(
        self, X: NDArray[np.float64]
    ) -> AnomalyResult | list[AnomalyResult]:
        """Detect performance anomalies.

        Parameters
        ----------
        X : NDArray[np.float64]
            Features to analyze

        Returns
        -------
        AnomalyResult | list[AnomalyResult]
            Anomaly detection result(s)
        """
        return self.detector.detect(X)

    def get_cluster(
        self, X: NDArray[np.float64]
    ) -> ClusterResult | list[ClusterResult]:
        """Get command cluster assignment.

        Parameters
        ----------
        X : NDArray[np.float64]
            Features to cluster

        Returns
        -------
        ClusterResult | list[ClusterResult]
            Cluster assignment result(s)
        """
        return self.clusterer.get_cluster(X)

    def optimize(
        self, X: NDArray[np.float64]
    ) -> dict[str, PredictionResult | AnomalyResult | ClusterResult]:
        """Perform comprehensive optimization analysis.

        Parameters
        ----------
        X : NDArray[np.float64]
            Features for single command

        Returns
        -------
        dict[str, ...]
            Dictionary containing prediction, anomaly, and cluster results
        """
        with span("ml.optimizer.optimize"):
            return {
                "prediction": self.predict_execution_time(X),  # type: ignore[PredictionResult]
                "anomaly": self.detect_anomaly(X),  # type: ignore[AnomalyResult]
                "cluster": self.get_cluster(X),  # type: ignore[ClusterResult]
            }
