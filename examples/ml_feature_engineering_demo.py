"""
ML Feature Engineering Demo - Extract and Transform Command Features
=====================================================================

This example demonstrates the feature engineering pipeline for extracting
ML features from command execution telemetry.

Features Demonstrated
--------------------
1. Feature extraction from command metadata
2. Feature normalization and scaling
3. Feature selection using statistical tests
4. Dimensionality reduction with PCA
5. Complete transformation pipeline

Run this example:
    python examples/ml_feature_engineering_demo.py
"""

from __future__ import annotations

import numpy as np

from specify_cli.ml import (
    FeatureExtractor,
    FeatureNormalizer,
    FeatureSelector,
    FeatureTransformer,
)


def main() -> None:
    """Run feature engineering demonstration."""
    print("=" * 80)
    print("FEATURE ENGINEERING DEMO - Command Telemetry Feature Extraction")
    print("=" * 80)
    print()

    # Step 1: Feature extraction
    print("Step 1: Extracting features from command metadata...")
    extractor = FeatureExtractor()

    # Example command executions
    commands = [
        {
            "command": "pytest tests/unit/ -v",
            "duration": 2.3,
            "exit_code": 0,
            "working_directory": "/home/user/project",
            "capture": True,
            "quiet": False,
            "timestamp": 1703001234.5,
        },
        {
            "command": "docker build -t myapp:latest .",
            "duration": 45.2,
            "exit_code": 0,
            "working_directory": "/home/user/app",
            "capture": False,
            "quiet": False,
            "timestamp": 1703001300.0,
        },
        {
            "command": "git commit -m 'feat: add ML module'",
            "duration": 0.5,
            "exit_code": 0,
            "working_directory": "/home/user/project",
            "capture": True,
            "quiet": True,
            "timestamp": 1703001400.0,
        },
    ]

    # Extract features
    features_list = []
    for cmd_meta in commands:
        features = extractor.extract_command_features(cmd_meta)
        features_list.append(features)

    X = np.array(features_list)
    feature_names = extractor.get_feature_names()

    print(f"  Extracted {X.shape[1]} features from {len(commands)} commands")
    print(f"  Features: {', '.join(feature_names[:10])}...")
    print()

    # Display some features
    print("  Sample feature values:")
    for i, name in enumerate(feature_names[:5]):
        print(f"    {name:20s}: {X[0, i]:.4f}")
    print()

    # Step 2: Feature normalization
    print("Step 2: Normalizing features...")

    # Generate more data for demo
    np.random.seed(42)
    X_large = np.random.randn(100, X.shape[1]) * np.std(X, axis=0) + np.mean(X, axis=0)

    normalizer_standard = FeatureNormalizer(method="standard")
    X_standard = normalizer_standard.fit_transform(X_large)

    normalizer_robust = FeatureNormalizer(method="robust")
    X_robust = normalizer_robust.fit_transform(X_large)

    print(f"  Original - Mean: {np.mean(X_large):.4f}, Std: {np.std(X_large):.4f}")
    print(f"  StandardScaler - Mean: {np.mean(X_standard):.4f}, Std: {np.std(X_standard):.4f}")
    print(f"  RobustScaler - Median: {np.median(X_robust):.4f}, IQR: {np.percentile(X_robust, 75) - np.percentile(X_robust, 25):.4f}")
    print()

    # Step 3: Feature selection
    print("Step 3: Selecting most important features...")

    # Generate target variable
    y = 3 * X_large[:, 0] + 2 * X_large[:, 1] + np.random.normal(0, 0.5, len(X_large))

    selector = FeatureSelector(k=10)
    X_selected = selector.fit_transform(X_large, y)

    print(f"  Original features: {X_large.shape[1]}")
    print(f"  Selected features: {X_selected.shape[1]}")
    print()

    # Display feature ranking
    print("  Top 10 features by importance:")
    ranking = selector.get_feature_ranking(feature_names)
    sorted_features = sorted(ranking.items(), key=lambda x: x[1], reverse=True)[:10]
    for i, (name, score) in enumerate(sorted_features, 1):
        print(f"    {i:2d}. {name:25s}: {score:.4f}")
    print()

    # Step 4: Complete transformation pipeline
    print("Step 4: Complete feature transformation pipeline...")

    transformer = FeatureTransformer(
        normalize=True,
        normalization_method="robust",
        select_features=True,
        n_features=10,
        reduce_dimensions=True,
        n_components=0.95,
    )

    X_transformed = transformer.fit_transform(X_large, y)

    print(f"  Original shape: {X_large.shape}")
    print(f"  Transformed shape: {X_transformed.shape}")
    print(f"  Pipeline steps:")
    print(f"    1. Normalization: {'robust' if transformer.normalize else 'none'}")
    print(f"    2. Feature selection: {transformer.selector.selector.k if transformer.selector else 'none'}")
    print(f"    3. PCA: {transformer.pca.n_components if transformer.pca else 'none'} components")
    print()

    # Step 5: Categorical feature encoding
    print("Step 5: Categorical feature encoding...")

    command_types = [
        "pytest tests/",
        "docker build",
        "git commit",
        "npm install",
        "pytest tests/",  # Duplicate
    ]

    print("  Command type hashes:")
    for cmd in command_types:
        hash_val = extractor._hash_categorical(cmd, "command_type")
        print(f"    '{cmd:20s}' -> {hash_val}")
    print()

    # Step 6: Temporal features
    print("Step 6: Temporal feature extraction...")

    import time

    timestamps = [
        time.time(),  # Now
        time.time() - 3600,  # 1 hour ago
        time.time() - 86400,  # 1 day ago
    ]

    print("  Temporal features (cyclical encoding):")
    for ts in timestamps:
        import datetime
        dt = datetime.datetime.fromtimestamp(ts, tz=datetime.UTC)
        temporal = extractor._extract_temporal_features(ts)
        print(f"    {dt.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"      Hour (sin/cos): ({temporal[0]:.4f}, {temporal[1]:.4f})")
        print(f"      Day (sin/cos): ({temporal[2]:.4f}, {temporal[3]:.4f})")
        print(f"      Is weekend: {temporal[4]}")
    print()

    print("=" * 80)
    print("DEMO COMPLETE!")
    print("=" * 80)
    print()
    print("Summary:")
    print(f"  - Extracted {len(feature_names)} features from command metadata")
    print(f"  - Demonstrated normalization (Standard, Robust)")
    print(f"  - Selected top {X_selected.shape[1]} features")
    print(f"  - Reduced dimensions with PCA")
    print(f"  - Complete transformation pipeline ready for ML")
    print()


if __name__ == "__main__":
    main()
