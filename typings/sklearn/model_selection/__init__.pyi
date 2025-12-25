"""Type stubs for sklearn.model_selection."""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray

class GridSearchCV:
    """Grid Search CV stub."""

    best_estimator_: Any
    best_params_: dict[str, Any]
    best_score_: float
    cv_results_: dict[str, NDArray[Any]]

    def __init__(
        self,
        estimator: Any,
        param_grid: dict[str, list[Any]],
        *,
        scoring: str | None = None,
        n_jobs: int | None = None,
        refit: bool = True,
        cv: int | None = None,
        verbose: int = 0,
        pre_dispatch: str | int = "2*n_jobs",
        error_score: float | str = ...,
        return_train_score: bool = False,
    ) -> None: ...
    def fit(
        self,
        X: NDArray[np.float64],
        y: NDArray[np.float64],
        *,
        groups: NDArray[np.int_] | None = None,
    ) -> GridSearchCV: ...
    def predict(self, X: NDArray[np.float64]) -> NDArray[np.float64]: ...
    def score(self, X: NDArray[np.float64], y: NDArray[np.float64]) -> float: ...

def cross_val_score(
    estimator: Any,
    X: NDArray[np.float64],
    y: NDArray[np.float64],
    *,
    groups: NDArray[np.int_] | None = None,
    scoring: str | None = None,
    cv: int | None = None,
    n_jobs: int | None = None,
    verbose: int = 0,
    fit_params: dict[str, Any] | None = None,
    pre_dispatch: str | int = "2*n_jobs",
    error_score: float | str = ...,
) -> NDArray[np.float64]: ...
