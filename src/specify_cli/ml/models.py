"""
specify_cli.ml.models - Model Training, Validation, and Persistence
====================================================================

Comprehensive model management for ML pipelines.

This module provides tools for:
- Model training with hyperparameter tuning
- Cross-validation and model evaluation
- Model persistence with versioning
- Performance metrics and reporting

Classes
-------
ModelTrainer
    Train ML models with hyperparameter optimization
ModelValidator
    Validate models using cross-validation
ModelEvaluator
    Evaluate model performance with comprehensive metrics
ModelPersistence
    Save and load models with versioning

Example
-------
    >>> from specify_cli.ml import ModelTrainer, ModelValidator
    >>>
    >>> # Train with hyperparameter tuning
    >>> trainer = ModelTrainer(model_type='random_forest')
    >>> best_model = trainer.train_with_tuning(X_train, y_train)
    >>>
    >>> # Validate
    >>> validator = ModelValidator()
    >>> scores = validator.cross_validate(best_model, X, y)

See Also
--------
- :mod:`specify_cli.ml.optimizer` : ML optimization models
- :mod:`specify_cli.ml.feature_engineering` : Feature engineering
"""

from __future__ import annotations

import json
import logging
import pickle
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import GridSearchCV, cross_val_score

from specify_cli.core.telemetry import metric_counter, metric_histogram, span

if TYPE_CHECKING:
    from numpy.typing import NDArray

__all__ = [
    "ModelEvaluator",
    "ModelPersistence",
    "ModelTrainer",
    "ModelValidator",
]

_log = logging.getLogger("specify_cli.ml.models")


class ModelTrainer:
    """Train ML models with hyperparameter optimization.

    This class provides a high-level interface for training scikit-learn
    models with automated hyperparameter tuning using GridSearchCV.

    Parameters
    ----------
    model_type : str, optional
        Type of model to train, by default 'random_forest'
        Currently supports: 'random_forest'
    random_state : int, optional
        Random state for reproducibility, by default 42
    n_jobs : int, optional
        Number of parallel jobs, by default -1

    Attributes
    ----------
    model_type : str
        Type of model being trained
    best_model : Any | None
        Best model from hyperparameter tuning
    best_params : dict[str, Any] | None
        Best hyperparameters found
    training_time : float | None
        Time taken to train in seconds

    Example
    -------
    >>> trainer = ModelTrainer(model_type='random_forest')
    >>> model = trainer.train_with_tuning(X_train, y_train)
    >>> print(f"Best params: {trainer.best_params}")
    """

    def __init__(
        self,
        model_type: str = "random_forest",
        random_state: int = 42,
        n_jobs: int = -1,
    ) -> None:
        """Initialize the model trainer."""
        self.model_type = model_type
        self.random_state = random_state
        self.n_jobs = n_jobs
        self.best_model: Any | None = None
        self.best_params: dict[str, Any] | None = None
        self.training_time: float | None = None

    def train(
        self, X: NDArray[np.float64], y: NDArray[np.float64], **kwargs: Any
    ) -> Any:
        """Train a model with default parameters.

        Parameters
        ----------
        X : NDArray[np.float64]
            Training features of shape (n_samples, n_features)
        y : NDArray[np.float64]
            Target values of shape (n_samples,)
        **kwargs : Any
            Additional parameters for model initialization

        Returns
        -------
        Any
            Trained model instance
        """
        with span(
            "ml.models.train",
            model_type=self.model_type,
            n_samples=len(X),
            n_features=X.shape[1],
        ):
            start_time = time.time()

            _log.info(f"Training {self.model_type} model with {len(X)} samples")

            # Create and train model
            model = self._create_model(**kwargs)
            model.fit(X, y)

            self.training_time = time.time() - start_time

            # Record metrics
            metric_histogram("ml.models.training.duration")(self.training_time)
            metric_counter("ml.models.trained")(1)

            _log.info(f"Training completed in {self.training_time:.2f}s")

            return model

    def train_with_tuning(
        self,
        X: NDArray[np.float64],
        y: NDArray[np.float64],
        param_grid: dict[str, list[Any]] | None = None,
        cv: int = 5,
        scoring: str = "neg_mean_squared_error",
    ) -> Any:
        """Train model with hyperparameter tuning using GridSearchCV.

        Parameters
        ----------
        X : NDArray[np.float64]
            Training features of shape (n_samples, n_features)
        y : NDArray[np.float64]
            Target values of shape (n_samples,)
        param_grid : dict[str, list[Any]], optional
            Parameter grid for GridSearchCV
            If None, uses default grid for model type
        cv : int, optional
            Number of cross-validation folds, by default 5
        scoring : str, optional
            Scoring metric for optimization, by default 'neg_mean_squared_error'

        Returns
        -------
        Any
            Best model from hyperparameter search

        Example
        -------
        >>> param_grid = {
        ...     'n_estimators': [50, 100, 200],
        ...     'max_depth': [10, 20, 30]
        ... }
        >>> model = trainer.train_with_tuning(X, y, param_grid=param_grid)
        """
        with span(
            "ml.models.tune",
            model_type=self.model_type,
            cv_folds=cv,
        ):
            start_time = time.time()

            # Use default param grid if not provided
            if param_grid is None:
                param_grid = self._get_default_param_grid()

            _log.info(
                f"Starting hyperparameter tuning for {self.model_type} "
                f"with {cv}-fold CV"
            )

            # Create base model
            base_model = self._create_model()

            # Perform grid search
            grid_search = GridSearchCV(
                estimator=base_model,
                param_grid=param_grid,
                cv=cv,
                scoring=scoring,
                n_jobs=self.n_jobs,
                verbose=1,
                return_train_score=True,
            )

            grid_search.fit(X, y)

            self.best_model = grid_search.best_estimator_
            self.best_params = grid_search.best_params_
            self.training_time = time.time() - start_time

            # Record metrics
            metric_histogram("ml.models.tuning.duration")(self.training_time)
            metric_counter("ml.models.tuned")(1)

            _log.info(
                f"Hyperparameter tuning completed in {self.training_time:.2f}s - "
                f"Best score: {grid_search.best_score_:.4f}"
            )
            _log.info(f"Best parameters: {self.best_params}")

            return self.best_model

    def _create_model(self, **kwargs: Any) -> Any:
        """Create a model instance based on model_type.

        Parameters
        ----------
        **kwargs : Any
            Model initialization parameters

        Returns
        -------
        Any
            Model instance
        """
        if self.model_type == "random_forest":
            return RandomForestRegressor(
                random_state=self.random_state,
                n_jobs=self.n_jobs,
                **kwargs,
            )

        msg = f"Unknown model type: {self.model_type}"
        raise ValueError(msg)

    def _get_default_param_grid(self) -> dict[str, list[Any]]:
        """Get default parameter grid for model type.

        Returns
        -------
        dict[str, list[Any]]
            Parameter grid for GridSearchCV
        """
        if self.model_type == "random_forest":
            return {
                "n_estimators": [50, 100, 200],
                "max_depth": [10, 20, 30, None],
                "min_samples_split": [2, 5, 10],
                "min_samples_leaf": [1, 2, 4],
                "bootstrap": [True],
            }

        return {}


class ModelValidator:
    """Validate models using cross-validation.

    This class provides comprehensive model validation using k-fold
    cross-validation with multiple scoring metrics.

    Parameters
    ----------
    cv : int, optional
        Number of cross-validation folds, by default 5
    scoring : str | list[str], optional
        Scoring metric(s) to use, by default 'neg_mean_squared_error'

    Attributes
    ----------
    cv : int
        Number of folds
    scoring : str | list[str]
        Scoring metrics

    Example
    -------
    >>> validator = ModelValidator(cv=10)
    >>> scores = validator.cross_validate(model, X, y)
    >>> print(f"Mean R² score: {scores['r2'].mean():.4f}")
    """

    def __init__(
        self,
        cv: int = 5,
        scoring: str | list[str] = "neg_mean_squared_error",
    ) -> None:
        """Initialize the model validator."""
        self.cv = cv
        self.scoring = scoring

    def cross_validate(
        self,
        model: Any,
        X: NDArray[np.float64],
        y: NDArray[np.float64],
    ) -> dict[str, NDArray[np.float64]]:
        """Perform cross-validation on model.

        Parameters
        ----------
        model : Any
            Model to validate
        X : NDArray[np.float64]
            Features of shape (n_samples, n_features)
        y : NDArray[np.float64]
            Target values of shape (n_samples,)

        Returns
        -------
        dict[str, NDArray[np.float64]]
            Dictionary containing cross-validation scores for each metric
        """
        with span("ml.models.validate", cv_folds=self.cv):
            _log.info(f"Performing {self.cv}-fold cross-validation")

            # Perform cross-validation for different metrics
            metrics = {
                "mse": "neg_mean_squared_error",
                "mae": "neg_mean_absolute_error",
                "r2": "r2",
            }

            results = {}
            for name, scoring in metrics.items():
                scores = cross_val_score(
                    model, X, y, cv=self.cv, scoring=scoring, n_jobs=-1
                )

                # Negate scores for error metrics (they're returned as negative)
                if name in ("mse", "mae"):
                    scores = -scores

                results[name] = scores

                _log.info(f"{name.upper()}: {scores.mean():.4f} (+/- {scores.std():.4f})")

            # Record metrics
            metric_counter("ml.models.validated")(1)

            return results

    def validate_with_splits(
        self,
        model: Any,
        X_train: NDArray[np.float64],
        y_train: NDArray[np.float64],
        X_test: NDArray[np.float64],
        y_test: NDArray[np.float64],
    ) -> dict[str, Any]:
        """Validate model on train/test splits.

        Parameters
        ----------
        model : Any
            Model to validate
        X_train : NDArray[np.float64]
            Training features
        y_train : NDArray[np.float64]
            Training targets
        X_test : NDArray[np.float64]
            Test features
        y_test : NDArray[np.float64]
            Test targets

        Returns
        -------
        dict[str, Any]
            Validation metrics for train and test sets
        """
        with span("ml.models.validate.splits"):
            # Train predictions
            y_train_pred = model.predict(X_train)
            train_metrics = {
                "mse": mean_squared_error(y_train, y_train_pred),
                "mae": mean_absolute_error(y_train, y_train_pred),
                "r2": r2_score(y_train, y_train_pred),
            }

            # Test predictions
            y_test_pred = model.predict(X_test)
            test_metrics = {
                "mse": mean_squared_error(y_test, y_test_pred),
                "mae": mean_absolute_error(y_test, y_test_pred),
                "r2": r2_score(y_test, y_test_pred),
            }

            _log.info(f"Train R²: {train_metrics['r2']:.4f}, Test R²: {test_metrics['r2']:.4f}")

            return {
                "train": train_metrics,
                "test": test_metrics,
            }


class ModelEvaluator:
    """Evaluate model performance with comprehensive metrics.

    This class provides detailed performance analysis including:
    - Standard regression metrics (MSE, MAE, R²)
    - Residual analysis
    - Feature importance
    - Performance report generation

    Example
    -------
    >>> evaluator = ModelEvaluator()
    >>> report = evaluator.evaluate(model, X_test, y_test)
    >>> print(report['metrics']['r2'])
    """

    def evaluate(
        self,
        model: Any,
        X: NDArray[np.float64],
        y: NDArray[np.float64],
        feature_names: list[str] | None = None,
    ) -> dict[str, Any]:
        """Evaluate model performance comprehensively.

        Parameters
        ----------
        model : Any
            Trained model to evaluate
        X : NDArray[np.float64]
            Test features
        y : NDArray[np.float64]
            True target values
        feature_names : list[str], optional
            Names of features for importance analysis

        Returns
        -------
        dict[str, Any]
            Comprehensive evaluation report containing:
            - metrics: Standard regression metrics
            - residuals: Residual analysis
            - feature_importance: Feature importance scores (if available)
            - predictions: Sample predictions
        """
        with span("ml.models.evaluate", n_samples=len(X)):
            _log.info(f"Evaluating model on {len(X)} samples")

            # Get predictions
            y_pred = model.predict(X)

            # Calculate metrics
            metrics = {
                "mse": float(mean_squared_error(y, y_pred)),
                "rmse": float(np.sqrt(mean_squared_error(y, y_pred))),
                "mae": float(mean_absolute_error(y, y_pred)),
                "r2": float(r2_score(y, y_pred)),
            }

            # Residual analysis
            residuals = y - y_pred
            residuals_metrics = {
                "mean": float(np.mean(residuals)),
                "std": float(np.std(residuals)),
                "min": float(np.min(residuals)),
                "max": float(np.max(residuals)),
                "percentiles": {
                    "25": float(np.percentile(residuals, 25)),
                    "50": float(np.percentile(residuals, 50)),
                    "75": float(np.percentile(residuals, 75)),
                },
            }

            # Feature importance (if available)
            feature_importance = None
            if hasattr(model, "feature_importances_"):
                if feature_names:
                    feature_importance = dict(
                        zip(feature_names, model.feature_importances_.tolist(), strict=False)
                    )
                else:
                    feature_importance = {
                        f"feature_{i}": float(imp)
                        for i, imp in enumerate(model.feature_importances_)
                    }

            # Record metrics
            metric_counter("ml.models.evaluated")(1)

            report = {
                "metrics": metrics,
                "residuals": residuals_metrics,
                "feature_importance": feature_importance,
                "n_samples": len(X),
                "timestamp": datetime.now(tz=UTC).isoformat(),
            }

            _log.info(
                f"Evaluation complete - R²={metrics['r2']:.4f}, "
                f"RMSE={metrics['rmse']:.4f}, MAE={metrics['mae']:.4f}"
            )

            return report

    def generate_report(
        self,
        evaluation: dict[str, Any],
        output_path: Path | None = None,
    ) -> str:
        """Generate human-readable evaluation report.

        Parameters
        ----------
        evaluation : dict[str, Any]
            Evaluation results from evaluate()
        output_path : Path, optional
            Path to save report, by default None (return only)

        Returns
        -------
        str
            Formatted evaluation report
        """
        lines = [
            "=" * 80,
            "MODEL EVALUATION REPORT",
            "=" * 80,
            "",
            f"Timestamp: {evaluation['timestamp']}",
            f"Samples: {evaluation['n_samples']}",
            "",
            "PERFORMANCE METRICS",
            "-" * 80,
            f"R² Score:     {evaluation['metrics']['r2']:.6f}",
            f"RMSE:         {evaluation['metrics']['rmse']:.6f}",
            f"MAE:          {evaluation['metrics']['mae']:.6f}",
            f"MSE:          {evaluation['metrics']['mse']:.6f}",
            "",
            "RESIDUAL ANALYSIS",
            "-" * 80,
            f"Mean:         {evaluation['residuals']['mean']:.6f}",
            f"Std Dev:      {evaluation['residuals']['std']:.6f}",
            f"Min:          {evaluation['residuals']['min']:.6f}",
            f"Max:          {evaluation['residuals']['max']:.6f}",
            f"25th %ile:    {evaluation['residuals']['percentiles']['25']:.6f}",
            f"Median:       {evaluation['residuals']['percentiles']['50']:.6f}",
            f"75th %ile:    {evaluation['residuals']['percentiles']['75']:.6f}",
            "",
        ]

        # Add feature importance if available
        if evaluation.get("feature_importance"):
            lines.extend([
                "FEATURE IMPORTANCE",
                "-" * 80,
            ])
            # Sort by importance
            sorted_features = sorted(
                evaluation["feature_importance"].items(),
                key=lambda x: x[1],
                reverse=True,
            )
            for name, importance in sorted_features[:10]:  # Top 10
                lines.append(f"{name:30s}  {importance:.6f}")
            lines.append("")

        lines.append("=" * 80)

        report = "\n".join(lines)

        # Save if path provided
        if output_path:
            output_path.write_text(report)
            _log.info(f"Report saved to {output_path}")

        return report


class ModelPersistence:
    """Save and load models with versioning.

    This class handles model serialization with metadata including:
    - Model version and timestamp
    - Training parameters and metrics
    - Feature names and configuration

    Parameters
    ----------
    model_dir : Path, optional
        Directory to store models, by default Path("models")

    Attributes
    ----------
    model_dir : Path
        Directory for model storage

    Example
    -------
    >>> persistence = ModelPersistence(model_dir=Path("ml_models"))
    >>> persistence.save_model(model, "performance_predictor", metadata)
    >>> loaded_model, metadata = persistence.load_model("performance_predictor")
    """

    def __init__(self, model_dir: Path = Path("models")) -> None:
        """Initialize model persistence handler."""
        self.model_dir = model_dir
        self.model_dir.mkdir(parents=True, exist_ok=True)

    def save_model(
        self,
        model: Any,
        name: str,
        metadata: dict[str, Any] | None = None,
        version: str | None = None,
    ) -> Path:
        """Save model with metadata.

        Parameters
        ----------
        model : Any
            Model to save
        name : str
            Model name
        metadata : dict[str, Any], optional
            Additional metadata to store
        version : str, optional
            Model version, by default uses timestamp

        Returns
        -------
        Path
            Path to saved model file
        """
        with span("ml.models.save", model_name=name):
            # Generate version if not provided
            if version is None:
                version = datetime.now(tz=UTC).strftime("%Y%m%d_%H%M%S")

            # Create filenames
            model_file = self.model_dir / f"{name}_v{version}.pkl"
            metadata_file = self.model_dir / f"{name}_v{version}_metadata.json"

            _log.info(f"Saving model to {model_file}")

            # Save model
            with model_file.open("wb") as f:
                pickle.dump(model, f)

            # Prepare metadata
            full_metadata = {
                "name": name,
                "version": version,
                "timestamp": datetime.now(tz=UTC).isoformat(),
                "model_type": type(model).__name__,
                **(metadata or {}),
            }

            # Save metadata
            with metadata_file.open("w") as f:
                json.dump(full_metadata, f, indent=2)

            # Record metrics
            metric_counter("ml.models.saved")(1)

            _log.info(f"Model and metadata saved successfully (version: {version})")

            return model_file

    def load_model(
        self, name: str, version: str | None = None
    ) -> tuple[Any, dict[str, Any]]:
        """Load model with metadata.

        Parameters
        ----------
        name : str
            Model name
        version : str, optional
            Model version, by default loads latest

        Returns
        -------
        tuple[Any, dict[str, Any]]
            Loaded model and its metadata

        Raises
        ------
        FileNotFoundError
            If model file not found
        """
        with span("ml.models.load", model_name=name):
            # Find model file
            if version:
                model_file = self.model_dir / f"{name}_v{version}.pkl"
                metadata_file = self.model_dir / f"{name}_v{version}_metadata.json"
            else:
                # Find latest version
                pattern = f"{name}_v*.pkl"
                model_files = sorted(self.model_dir.glob(pattern))
                if not model_files:
                    msg = f"No model found with name: {name}"
                    raise FileNotFoundError(msg)
                model_file = model_files[-1]
                metadata_file = model_file.with_name(
                    model_file.stem + "_metadata.json"
                )

            _log.info(f"Loading model from {model_file}")

            # Load model
            with model_file.open("rb") as f:
                model = pickle.load(f)

            # Load metadata
            metadata = {}
            if metadata_file.exists():
                with metadata_file.open() as f:
                    metadata = json.load(f)

            # Record metrics
            metric_counter("ml.models.loaded")(1)

            _log.info(f"Model loaded successfully (version: {metadata.get('version', 'unknown')})")

            return model, metadata

    def list_models(self) -> list[dict[str, Any]]:
        """List all saved models with metadata.

        Returns
        -------
        list[dict[str, Any]]
            List of model metadata dictionaries
        """
        models = []

        for metadata_file in sorted(self.model_dir.glob("*_metadata.json")):
            with metadata_file.open() as f:
                metadata = json.load(f)
                models.append(metadata)

        return models
