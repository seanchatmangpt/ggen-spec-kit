# Type stubs for sklearn.feature_selection
from typing import Any
from numpy.typing import NDArray

def mutual_info_regression(
    X: NDArray[Any],
    y: NDArray[Any],
    **kwargs: Any
) -> NDArray[Any]: ...
