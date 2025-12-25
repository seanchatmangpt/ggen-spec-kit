"""Type stubs for sklearn.feature_selection."""

from __future__ import annotations

from typing import Any, Callable

import numpy as np
from numpy.typing import NDArray

class SelectKBest:
    """Select K Best features stub."""

    k: int | str
    scores_: NDArray[np.float64]

    def __init__(
        self, score_func: Callable[..., tuple[NDArray[np.float64], NDArray[np.float64]]] = ..., *, k: int | str = 10
    ) -> None: ...
    def fit(
        self, X: NDArray[np.float64], y: NDArray[np.float64]
    ) -> SelectKBest: ...
    def transform(self, X: NDArray[np.float64]) -> NDArray[np.float64]: ...
    def fit_transform(
        self, X: NDArray[np.float64], y: NDArray[np.float64]
    ) -> NDArray[np.float64]: ...
    def get_support(self, indices: bool = False) -> NDArray[np.bool_] | NDArray[np.int_]: ...

def f_regression(
    X: NDArray[np.float64], y: NDArray[np.float64]
) -> tuple[NDArray[np.float64], NDArray[np.float64]]: ...
