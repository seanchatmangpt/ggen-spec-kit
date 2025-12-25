"""Type stubs for sklearn.cluster."""

from __future__ import annotations

from typing import Literal

import numpy as np
from numpy.typing import NDArray

class KMeans:
    """K-Means clustering stub."""

    n_clusters: int
    random_state: int | None
    max_iter: int
    n_init: int
    algorithm: Literal["lloyd", "elkan", "auto", "full"]
    inertia_: float
    labels_: NDArray[np.int_]
    cluster_centers_: NDArray[np.float64]

    def __init__(
        self,
        n_clusters: int = 8,
        *,
        init: Literal["k-means++", "random"] | NDArray[np.float64] = "k-means++",
        n_init: int = 10,
        max_iter: int = 300,
        tol: float = 1e-4,
        verbose: int = 0,
        random_state: int | None = None,
        copy_x: bool = True,
        algorithm: Literal["lloyd", "elkan", "auto", "full"] = "lloyd",
    ) -> None: ...
    def fit(self, X: NDArray[np.float64], y: None = None, sample_weight: NDArray[np.float64] | None = None) -> KMeans: ...
    def predict(self, X: NDArray[np.float64]) -> NDArray[np.int_]: ...
    def transform(self, X: NDArray[np.float64]) -> NDArray[np.float64]: ...
    def fit_predict(self, X: NDArray[np.float64], y: None = None, sample_weight: NDArray[np.float64] | None = None) -> NDArray[np.int_]: ...
    def score(self, X: NDArray[np.float64], y: None = None, sample_weight: NDArray[np.float64] | None = None) -> float: ...
