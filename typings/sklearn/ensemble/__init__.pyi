"""Type stubs for sklearn.ensemble."""

from __future__ import annotations

from typing import Any, Literal

import numpy as np
from numpy.typing import NDArray

class RandomForestRegressor:
    """Random Forest Regressor stub."""

    n_estimators: int
    max_depth: int | None
    min_samples_split: int
    min_samples_leaf: int
    random_state: int | None
    n_jobs: int | None
    bootstrap: bool
    oob_score: bool
    oob_score_: float
    feature_importances_: NDArray[np.float64]
    estimators_: list[Any]

    def __init__(
        self,
        n_estimators: int = 100,
        *,
        criterion: Literal["squared_error", "absolute_error", "friedman_mse", "poisson"] = "squared_error",
        max_depth: int | None = None,
        min_samples_split: int = 2,
        min_samples_leaf: int = 1,
        min_weight_fraction_leaf: float = 0.0,
        max_features: int | float | Literal["sqrt", "log2"] | None = 1.0,
        max_leaf_nodes: int | None = None,
        min_impurity_decrease: float = 0.0,
        bootstrap: bool = True,
        oob_score: bool = False,
        n_jobs: int | None = None,
        random_state: int | None = None,
        verbose: int = 0,
        warm_start: bool = False,
        ccp_alpha: float = 0.0,
        max_samples: int | float | None = None,
    ) -> None: ...
    def fit(
        self,
        X: NDArray[np.float64],
        y: NDArray[np.float64],
        sample_weight: NDArray[np.float64] | None = None,
    ) -> RandomForestRegressor: ...
    def predict(self, X: NDArray[np.float64]) -> NDArray[np.float64]: ...
    def score(self, X: NDArray[np.float64], y: NDArray[np.float64]) -> float: ...

class IsolationForest:
    """Isolation Forest for anomaly detection stub."""

    contamination: float
    n_estimators: int
    max_samples: int | str
    random_state: int | None
    n_jobs: int | None
    bootstrap: bool

    def __init__(
        self,
        *,
        n_estimators: int = 100,
        max_samples: int | str = "auto",
        contamination: float = 0.1,
        max_features: int | float = 1.0,
        bootstrap: bool = False,
        n_jobs: int | None = None,
        random_state: int | None = None,
        verbose: int = 0,
        warm_start: bool = False,
    ) -> None: ...
    def fit(
        self, X: NDArray[np.float64], y: Any = None, sample_weight: NDArray[np.float64] | None = None
    ) -> IsolationForest: ...
    def predict(self, X: NDArray[np.float64]) -> NDArray[np.int_]: ...
    def score_samples(self, X: NDArray[np.float64]) -> NDArray[np.float64]: ...
    def decision_function(self, X: NDArray[np.float64]) -> NDArray[np.float64]: ...
