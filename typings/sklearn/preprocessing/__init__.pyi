"""Type stubs for sklearn.preprocessing."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

class StandardScaler:
    """Standard Scaler stub."""

    mean_: NDArray[np.float64]
    scale_: NDArray[np.float64]
    var_: NDArray[np.float64]

    def __init__(
        self, *, copy: bool = True, with_mean: bool = True, with_std: bool = True
    ) -> None: ...
    def fit(
        self, X: NDArray[np.float64], y: None = None, sample_weight: NDArray[np.float64] | None = None
    ) -> StandardScaler: ...
    def transform(self, X: NDArray[np.float64]) -> NDArray[np.float64]: ...
    def fit_transform(
        self, X: NDArray[np.float64], y: None = None
    ) -> NDArray[np.float64]: ...
    def inverse_transform(self, X: NDArray[np.float64]) -> NDArray[np.float64]: ...

class RobustScaler:
    """Robust Scaler stub."""

    center_: NDArray[np.float64]
    scale_: NDArray[np.float64]

    def __init__(
        self,
        *,
        with_centering: bool = True,
        with_scaling: bool = True,
        quantile_range: tuple[float, float] = (25.0, 75.0),
        copy: bool = True,
        unit_variance: bool = False,
    ) -> None: ...
    def fit(
        self, X: NDArray[np.float64], y: None = None
    ) -> RobustScaler: ...
    def transform(self, X: NDArray[np.float64]) -> NDArray[np.float64]: ...
    def fit_transform(
        self, X: NDArray[np.float64], y: None = None
    ) -> NDArray[np.float64]: ...
    def inverse_transform(self, X: NDArray[np.float64]) -> NDArray[np.float64]: ...
