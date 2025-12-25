# Type stubs for sklearn.metrics.pairwise
from typing import Any
from numpy.typing import NDArray

def cosine_similarity(
    X: NDArray[Any],
    Y: NDArray[Any] | None = None,
    dense_output: bool = True
) -> NDArray[Any]: ...

def euclidean_distances(
    X: NDArray[Any],
    Y: NDArray[Any] | None = None,
    **kwargs: Any
) -> NDArray[Any]: ...
