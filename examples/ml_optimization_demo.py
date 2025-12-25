"""
ML Optimization Demo - Predictive Command Performance Optimization
===================================================================

This example demonstrates the complete ML optimization pipeline for
command execution prediction, anomaly detection, and clustering.

Features Demonstrated
--------------------
1. Feature extraction from command metadata
2. Model training with hyperparameter tuning
3. Performance prediction with confidence intervals
4. Anomaly detection in command execution
5. Command clustering by complexity
6. Model persistence and reloading
7. Comprehensive evaluation and reporting

Run this example:
    python examples/ml_optimization_demo.py
"""

from __future__ import annotations

import numpy as np
from pathlib import Path

from specify_cli.ml import (
    CommandOptimizer,
    FeatureExtractor,
    FeatureTransformer,
    ModelEvaluator,
    ModelPersistence,
    ModelTrainer,
)


def generate_synthetic_data(n_samples: int = 1000) -> tuple[np.ndarray, np.ndarray]:
    """Generate synthetic command execution data.

    Parameters
    ----------
    n_samples : int
        Number of samples to generate

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Features (X) and execution times (y)
    """
    np.random.seed(42)

    # Generate features
    X = np.random.randn(n_samples, 20)

    # Generate execution times with some pattern
    # Duration increases with command complexity
    y = (
        3 * X[:, 0]
        + 2 * X[:, 1]
        + 1.5 * X[:, 2]
        + np.random.normal(0, 0.5, n_samples)
    )

    # Ensure positive execution times
    y = np.abs(y) + 0.1

    return X, y


def main() -> None:
    """Run ML optimization demonstration."""
    print("=" * 80)
    print("ML OPTIMIZATION DEMO - Command Performance Prediction")
    print("=" * 80)
    print()

    # Step 1: Generate training data
    print("Step 1: Generating synthetic command execution data...")
    X_train, y_train = generate_synthetic_data(n_samples=800)
    X_test, y_test = generate_synthetic_data(n_samples=200)
    print(f"  Training samples: {len(X_train)}")
    print(f"  Test samples: {len(X_test)}")
    print()

    # Step 2: Feature engineering
    print("Step 2: Feature engineering and transformation...")
    transformer = FeatureTransformer(
        normalize=True,
        normalization_method="robust",
        select_features=True,
        n_features=10,
    )

    X_train_transformed = transformer.fit_transform(X_train, y_train)
    X_test_transformed = transformer.transform(X_test)
    print(f"  Original features: {X_train.shape[1]}")
    print(f"  Selected features: {X_train_transformed.shape[1]}")
    print()

    # Step 3: Train model with hyperparameter tuning
    print("Step 3: Training RandomForest with hyperparameter tuning...")
    trainer = ModelTrainer(model_type="random_forest")

    param_grid = {
        "n_estimators": [50, 100],
        "max_depth": [10, 20],
        "min_samples_split": [2, 5],
    }

    best_model = trainer.train_with_tuning(
        X_train_transformed,
        y_train,
        param_grid=param_grid,
        cv=5,
    )
    print(f"  Best parameters: {trainer.best_params}")
    print(f"  Training time: {trainer.training_time:.2f}s")
    print()

    # Step 4: Evaluate model performance
    print("Step 4: Evaluating model performance...")
    evaluator = ModelEvaluator()
    evaluation = evaluator.evaluate(
        best_model,
        X_test_transformed,
        y_test,
        feature_names=[f"feature_{i}" for i in range(X_test_transformed.shape[1])],
    )

    print(f"  R² Score: {evaluation['metrics']['r2']:.4f}")
    print(f"  RMSE: {evaluation['metrics']['rmse']:.4f}")
    print(f"  MAE: {evaluation['metrics']['mae']:.4f}")
    print()

    # Step 5: Generate evaluation report
    print("Step 5: Generating evaluation report...")
    report = evaluator.generate_report(evaluation)
    print(report)

    # Step 6: Integrated optimizer (all models)
    print("Step 6: Training integrated CommandOptimizer...")
    optimizer = CommandOptimizer(
        predictor_params={"n_estimators": 100},
        detector_params={"contamination": 0.1},
        clusterer_params={"n_clusters": 5},
    )

    optimizer.fit(X_train, y_train)
    print("  All models trained successfully")
    print()

    # Step 7: Make predictions
    print("Step 7: Making predictions on test data...")
    sample = X_test[0]

    # Performance prediction
    prediction = optimizer.predict_execution_time(sample)
    print(f"  Predicted execution time: {prediction.predicted_time:.2f}s")
    print(f"  Confidence interval: ({prediction.confidence_interval[0]:.2f}s, "
          f"{prediction.confidence_interval[1]:.2f}s)")

    # Anomaly detection
    anomaly = optimizer.detect_anomaly(sample)
    print(f"  Is anomaly: {anomaly.is_anomaly}")
    print(f"  Anomaly score: {anomaly.anomaly_score:.4f}")
    print(f"  Confidence: {anomaly.confidence:.2%}")

    # Clustering
    cluster = optimizer.get_cluster(sample)
    print(f"  Cluster: {cluster.cluster_name} (ID: {cluster.cluster_id})")
    print(f"  Distance to center: {cluster.distance_to_center:.4f}")
    print()

    # Step 8: Model persistence
    print("Step 8: Saving models to disk...")
    persistence = ModelPersistence(model_dir=Path("ml_models"))

    metadata = {
        "model_type": "RandomForestRegressor",
        "n_features": X_train_transformed.shape[1],
        "training_samples": len(X_train),
        "r2_score": evaluation["metrics"]["r2"],
        "best_params": trainer.best_params,
    }

    model_path = persistence.save_model(
        best_model,
        name="command_performance_predictor",
        metadata=metadata,
    )
    print(f"  Model saved to: {model_path}")
    print()

    # Step 9: Load and verify
    print("Step 9: Loading model from disk...")
    loaded_model, loaded_metadata = persistence.load_model(
        "command_performance_predictor"
    )
    print(f"  Model version: {loaded_metadata.get('version')}")
    print(f"  Original R² score: {loaded_metadata.get('r2_score'):.4f}")
    print()

    # Step 10: Feature extraction example
    print("Step 10: Feature extraction from command metadata...")
    extractor = FeatureExtractor()

    command_metadata = {
        "command": "pytest tests/ -v --cov",
        "duration": 5.2,
        "exit_code": 0,
        "working_directory": "/home/user/project",
        "capture": True,
        "quiet": False,
        "timestamp": 1703001234.5,
    }

    features = extractor.extract_command_features(command_metadata)
    print(f"  Extracted {len(features)} features")
    print(f"  Feature names: {', '.join(extractor.get_feature_names()[:5])}...")
    print()

    print("=" * 80)
    print("DEMO COMPLETE!")
    print("=" * 80)
    print()
    print("Summary:")
    print(f"  - Trained model with R² score: {evaluation['metrics']['r2']:.4f}")
    print(f"  - Can predict execution time with confidence intervals")
    print(f"  - Can detect anomalous command performance")
    print(f"  - Can cluster commands by complexity")
    print(f"  - Models saved to: {persistence.model_dir}")
    print()


if __name__ == "__main__":
    main()
