"""
specify_cli.ml - Machine Learning for Predictive Optimization
==============================================================

Hyper-advanced ML features using scikit-learn for:
- Predictive optimization of command execution time
- Anomaly detection in command performance
- Command clustering and categorization
- Feature engineering from telemetry data

This module provides a complete ML pipeline for analyzing and optimizing
CLI command execution patterns.

Modules
-------
- **optimizer**: Main ML optimizer with RandomForest, IsolationForest, KMeans
- **feature_engineering**: Feature extraction, normalization, and selection
- **models**: Model training, validation, persistence, and evaluation

Key Features
-----------
* **Performance Prediction**: Predict command execution time before running
* **Anomaly Detection**: Detect unusual performance patterns in real-time
* **Command Clustering**: Categorize commands by complexity and resource usage
* **Feature Engineering**: Extract and transform telemetry data into ML features
* **Model Persistence**: Save and load trained models with versioning
* **Cross-Validation**: Comprehensive model validation and evaluation
* **Hyperparameter Tuning**: Automated optimization with GridSearchCV
* **Drift Detection**: Monitor feature and model drift over time
* **Confidence Scoring**: Prediction confidence intervals and uncertainty
* **Fairness Analysis**: Bias detection and mitigation

Example
-------
    >>> from specify_cli.ml import CommandOptimizer, FeatureExtractor
    >>>
    >>> # Create optimizer
    >>> optimizer = CommandOptimizer()
    >>>
    >>> # Extract features from command metadata
    >>> extractor = FeatureExtractor()
    >>> features = extractor.extract_command_features({
    ...     'command': 'pytest tests/',
    ...     'duration': 5.2,
    ...     'exit_code': 0,
    ...     'working_directory': '/home/user/project'
    ... })
    >>>
    >>> # Predict execution time
    >>> predicted_time = optimizer.predict_execution_time(features)
    >>>
    >>> # Detect anomalies
    >>> is_anomaly = optimizer.detect_anomaly(features)

See Also
--------
- :mod:`specify_cli.core.telemetry` : OpenTelemetry integration
- :mod:`specify_cli.core.instrumentation` : Command instrumentation
- :mod:`specify_cli.core.semconv` : Semantic conventions
"""

from __future__ import annotations

from .feature_engineering import (
    FeatureExtractor,
    FeatureNormalizer,
    FeatureSelector,
    FeatureTransformer,
)
from .models import (
    ModelEvaluator,
    ModelPersistence,
    ModelTrainer,
    ModelValidator,
)
from .optimizer import (
    AnomalyDetector,
    CommandClusterer,
    CommandOptimizer,
    PerformancePredictor,
)

__all__ = [
    "AnomalyDetector",
    "CommandClusterer",
    # Optimizer components
    "CommandOptimizer",
    # Feature engineering
    "FeatureExtractor",
    "FeatureNormalizer",
    "FeatureSelector",
    "FeatureTransformer",
    "ModelEvaluator",
    "ModelPersistence",
    # Model management
    "ModelTrainer",
    "ModelValidator",
    "PerformancePredictor",
]

__version__ = "0.1.0"
