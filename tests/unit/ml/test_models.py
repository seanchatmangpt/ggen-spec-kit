"""Unit tests for ML models module."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from specify_cli.ml.models import (
    ModelEvaluator,
    ModelPersistence,
    ModelTrainer,
    ModelValidator,
)


@pytest.fixture
def synthetic_data() -> tuple[np.ndarray, np.ndarray]:
    """Generate synthetic training data."""
    np.random.seed(42)
    X = np.random.randn(100, 10)
    y = 3 * X[:, 0] + 2 * X[:, 1] + np.random.normal(0, 0.5, 100)
    return X, y


@pytest.fixture
def test_data() -> tuple[np.ndarray, np.ndarray]:
    """Generate synthetic test data."""
    np.random.seed(43)
    X = np.random.randn(20, 10)
    y = 3 * X[:, 0] + 2 * X[:, 1] + np.random.normal(0, 0.5, 20)
    return X, y


class TestModelTrainer:
    """Test ModelTrainer class."""

    def test_initialization(self) -> None:
        """Test trainer initialization."""
        trainer = ModelTrainer(model_type="random_forest")
        assert trainer.model_type == "random_forest"
        assert trainer.best_model is None
        assert trainer.best_params is None

    def test_train(self, synthetic_data: tuple[np.ndarray, np.ndarray]) -> None:
        """Test basic model training."""
        X, y = synthetic_data
        trainer = ModelTrainer()

        model = trainer.train(X, y)

        assert model is not None
        assert trainer.training_time is not None
        assert trainer.training_time > 0

    def test_train_with_tuning(
        self, synthetic_data: tuple[np.ndarray, np.ndarray]
    ) -> None:
        """Test hyperparameter tuning."""
        X, y = synthetic_data
        trainer = ModelTrainer()

        param_grid = {
            "n_estimators": [50, 100],
            "max_depth": [5, 10],
        }

        model = trainer.train_with_tuning(X, y, param_grid=param_grid, cv=3)

        assert model is not None
        assert trainer.best_model is not None
        assert trainer.best_params is not None
        assert "n_estimators" in trainer.best_params

    def test_train_with_default_grid(
        self, synthetic_data: tuple[np.ndarray, np.ndarray]
    ) -> None:
        """Test training with default parameter grid."""
        X, y = synthetic_data
        trainer = ModelTrainer()

        # Use small grid for faster testing
        param_grid = {
            "n_estimators": [50],
            "max_depth": [5],
        }

        model = trainer.train_with_tuning(X, y, param_grid=param_grid, cv=2)

        assert model is not None
        assert trainer.best_params is not None


class TestModelValidator:
    """Test ModelValidator class."""

    def test_initialization(self) -> None:
        """Test validator initialization."""
        validator = ModelValidator(cv=10)
        assert validator.cv == 10

    def test_cross_validate(
        self, synthetic_data: tuple[np.ndarray, np.ndarray]
    ) -> None:
        """Test cross-validation."""
        X, y = synthetic_data
        trainer = ModelTrainer()
        model = trainer.train(X, y)

        validator = ModelValidator(cv=3)
        scores = validator.cross_validate(model, X, y)

        assert "mse" in scores
        assert "mae" in scores
        assert "r2" in scores
        assert len(scores["mse"]) == 3  # CV folds

    def test_validate_with_splits(
        self,
        synthetic_data: tuple[np.ndarray, np.ndarray],
        test_data: tuple[np.ndarray, np.ndarray],
    ) -> None:
        """Test validation on train/test splits."""
        X_train, y_train = synthetic_data
        X_test, y_test = test_data

        trainer = ModelTrainer()
        model = trainer.train(X_train, y_train)

        validator = ModelValidator()
        results = validator.validate_with_splits(
            model, X_train, y_train, X_test, y_test
        )

        assert "train" in results
        assert "test" in results
        assert "r2" in results["train"]
        assert "r2" in results["test"]


class TestModelEvaluator:
    """Test ModelEvaluator class."""

    def test_evaluate(
        self, synthetic_data: tuple[np.ndarray, np.ndarray]
    ) -> None:
        """Test model evaluation."""
        X, y = synthetic_data
        trainer = ModelTrainer()
        model = trainer.train(X, y)

        evaluator = ModelEvaluator()
        report = evaluator.evaluate(model, X, y)

        assert "metrics" in report
        assert "residuals" in report
        assert "feature_importance" in report
        assert "n_samples" in report
        assert "timestamp" in report

        # Check metrics
        assert "r2" in report["metrics"]
        assert "rmse" in report["metrics"]
        assert "mae" in report["metrics"]

    def test_evaluate_with_feature_names(
        self, synthetic_data: tuple[np.ndarray, np.ndarray]
    ) -> None:
        """Test evaluation with feature names."""
        X, y = synthetic_data
        trainer = ModelTrainer()
        model = trainer.train(X, y)

        feature_names = [f"feature_{i}" for i in range(10)]

        evaluator = ModelEvaluator()
        report = evaluator.evaluate(model, X, y, feature_names=feature_names)

        assert report["feature_importance"] is not None
        assert "feature_0" in report["feature_importance"]

    def test_generate_report(
        self, synthetic_data: tuple[np.ndarray, np.ndarray], tmp_path: Path
    ) -> None:
        """Test report generation."""
        X, y = synthetic_data
        trainer = ModelTrainer()
        model = trainer.train(X, y)

        evaluator = ModelEvaluator()
        evaluation = evaluator.evaluate(model, X, y)

        # Generate report without saving
        report = evaluator.generate_report(evaluation)
        assert "MODEL EVALUATION REPORT" in report
        assert "R² Score" in report

        # Generate and save report
        report_path = tmp_path / "report.txt"
        report_saved = evaluator.generate_report(evaluation, output_path=report_path)

        assert report_path.exists()
        assert report_saved == report


class TestModelPersistence:
    """Test ModelPersistence class."""

    def test_initialization(self, tmp_path: Path) -> None:
        """Test persistence initialization."""
        persistence = ModelPersistence(model_dir=tmp_path / "models")
        assert persistence.model_dir.exists()

    def test_save_model(
        self, synthetic_data: tuple[np.ndarray, np.ndarray], tmp_path: Path
    ) -> None:
        """Test model saving."""
        X, y = synthetic_data
        trainer = ModelTrainer()
        model = trainer.train(X, y)

        persistence = ModelPersistence(model_dir=tmp_path / "models")

        metadata = {
            "description": "Test model",
            "n_features": X.shape[1],
        }

        model_path = persistence.save_model(
            model, name="test_model", metadata=metadata, version="1.0"
        )

        assert model_path.exists()
        assert model_path.name == "test_model_v1.0.pkl"

        # Check metadata file
        metadata_path = tmp_path / "models" / "test_model_v1.0_metadata.json"
        assert metadata_path.exists()

    def test_load_model(
        self, synthetic_data: tuple[np.ndarray, np.ndarray], tmp_path: Path
    ) -> None:
        """Test model loading."""
        X, y = synthetic_data
        trainer = ModelTrainer()
        model = trainer.train(X, y)

        persistence = ModelPersistence(model_dir=tmp_path / "models")

        # Save model
        persistence.save_model(model, name="test_model", version="1.0")

        # Load model
        loaded_model, metadata = persistence.load_model(
            "test_model", version="1.0"
        )

        assert loaded_model is not None
        assert metadata["name"] == "test_model"
        assert metadata["version"] == "1.0"

        # Verify model works
        predictions = loaded_model.predict(X[:5])
        assert len(predictions) == 5

    def test_load_latest_version(
        self, synthetic_data: tuple[np.ndarray, np.ndarray], tmp_path: Path
    ) -> None:
        """Test loading latest model version."""
        X, y = synthetic_data
        trainer = ModelTrainer()
        model = trainer.train(X, y)

        persistence = ModelPersistence(model_dir=tmp_path / "models")

        # Save multiple versions
        persistence.save_model(model, name="test_model", version="1.0")
        persistence.save_model(model, name="test_model", version="2.0")

        # Load without version (should get latest)
        loaded_model, metadata = persistence.load_model("test_model")

        assert metadata["version"] == "2.0"

    def test_list_models(
        self, synthetic_data: tuple[np.ndarray, np.ndarray], tmp_path: Path
    ) -> None:
        """Test listing saved models."""
        X, y = synthetic_data
        trainer = ModelTrainer()
        model = trainer.train(X, y)

        persistence = ModelPersistence(model_dir=tmp_path / "models")

        # Save multiple models
        persistence.save_model(model, name="model1", version="1.0")
        persistence.save_model(model, name="model2", version="1.0")

        models = persistence.list_models()

        assert len(models) == 2
        model_names = {m["name"] for m in models}
        assert "model1" in model_names
        assert "model2" in model_names

    def test_load_nonexistent_model_raises(self, tmp_path: Path) -> None:
        """Test that loading nonexistent model raises error."""
        persistence = ModelPersistence(model_dir=tmp_path / "models")

        with pytest.raises(FileNotFoundError, match="No model found"):
            persistence.load_model("nonexistent_model")
