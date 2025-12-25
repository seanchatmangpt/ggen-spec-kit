"""Type stubs for sklearn.metrics."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

def mean_squared_error(
    y_true: NDArray[np.float64],
    y_pred: NDArray[np.float64],
    *,
    sample_weight: NDArray[np.float64] | None = None,
    multioutput: str = "uniform_average",
    squared: bool = True,
) -> float: ...

def mean_absolute_error(
    y_true: NDArray[np.float64],
    y_pred: NDArray[np.float64],
    *,
    sample_weight: NDArray[np.float64] | None = None,
    multioutput: str = "uniform_average",
) -> float: ...

def r2_score(
    y_true: NDArray[np.float64],
    y_pred: NDArray[np.float64],
    *,
    sample_weight: NDArray[np.float64] | None = None,
    multioutput: str = "uniform_average",
) -> float: ...

def silhouette_score(
    X: NDArray[np.float64],
    labels: NDArray[np.int_],
    *,
    metric: str = "euclidean",
    sample_size: int | None = None,
    random_state: int | None = None,
) -> float: ...
