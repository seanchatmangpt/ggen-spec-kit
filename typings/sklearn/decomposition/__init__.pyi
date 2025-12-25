"""Type stubs for sklearn.decomposition."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

class PCA:
    """Principal Component Analysis stub."""

    n_components: int | float | None
    components_: NDArray[np.float64]
    explained_variance_: NDArray[np.float64]
    explained_variance_ratio_: NDArray[np.float64]

    def __init__(
        self,
        n_components: int | float | None = None,
        *,
        copy: bool = True,
        whiten: bool = False,
        svd_solver: str = "auto",
        tol: float = 0.0,
        iterated_power: int | str = "auto",
        random_state: int | None = None,
    ) -> None: ...
    def fit(self, X: NDArray[np.float64], y: None = None) -> PCA: ...
    def transform(self, X: NDArray[np.float64]) -> NDArray[np.float64]: ...
    def fit_transform(self, X: NDArray[np.float64], y: None = None) -> NDArray[np.float64]: ...
    def inverse_transform(self, X: NDArray[np.float64]) -> NDArray[np.float64]: ...
