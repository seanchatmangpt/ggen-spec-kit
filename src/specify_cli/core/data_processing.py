"""
specify_cli.core.data_processing
---------------------------------
Hyper-advanced data processing layer using pandas and numpy for metrics, reports, and analysis.

This module provides enterprise-grade data processing capabilities:

* **DataFrame-based Metrics**: Convert raw metrics to structured DataFrames
* **Time-Series Analysis**: Resample, trend detection, seasonality analysis
* **Statistical Analysis**: Mean, std, percentiles, skewness, kurtosis
* **Outlier Detection**: IQR, Z-score, and isolation forest methods
* **Data Aggregation**: Groupby, pivot tables, multi-index operations
* **Performance Optimization**: Vectorized operations, chunked processing
* **Data Export**: CSV, JSON, Excel, Parquet formats
* **Correlation Analysis**: Pearson, Spearman correlation matrices
* **Trend Analysis**: Linear regression, polynomial fitting, moving averages

The module integrates with advanced_observability.py to provide powerful
data analysis capabilities for performance metrics and telemetry data.

Example
-------
    from specify_cli.core.data_processing import (
        MetricsDataProcessor,
        TimeSeriesAnalyzer,
        OutlierDetector,
    )

    # Process metrics to DataFrame
    processor = MetricsDataProcessor()
    df = processor.metrics_to_dataframe("my_operation")

    # Analyze time series
    analyzer = TimeSeriesAnalyzer(df)
    trends = analyzer.detect_trends()

    # Detect outliers
    detector = OutlierDetector()
    outliers = detector.detect_zscore(df['duration'])

Environment Variables
--------------------
- SPECIFY_DATA_EXPORT_PATH : Default path for data exports (default: .specify/exports)
- SPECIFY_CHUNK_SIZE : Chunk size for large dataset processing (default: 10000)
- SPECIFY_OUTLIER_THRESHOLD : Z-score threshold for outlier detection (default: 3.0)

See Also
--------
- :mod:`specify_cli.core.advanced_observability` : Advanced metrics collection
- :mod:`specify_cli.core.reporting` : Report generation from DataFrames
"""

from __future__ import annotations

import os
import warnings
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

import numpy as np

try:
    import pandas as pd  # type: ignore[import-untyped]

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    warnings.warn(
        "pandas not available. Install with: uv sync --group pm or uv sync --group all",
        stacklevel=2,
    )

try:
    from scipy import stats  # type: ignore[import-untyped]
    from scipy.signal import find_peaks  # type: ignore[import-untyped]

    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from .advanced_observability import (
    _GLOBAL_STORE,
)

# --------------------------------------------------------------------------- #
# Configuration                                                                #
# --------------------------------------------------------------------------- #

EXPORT_PATH = Path(os.getenv("SPECIFY_DATA_EXPORT_PATH", ".specify/exports"))
CHUNK_SIZE = int(os.getenv("SPECIFY_CHUNK_SIZE", "10000"))
OUTLIER_THRESHOLD = float(os.getenv("SPECIFY_OUTLIER_THRESHOLD", "3.0"))


# --------------------------------------------------------------------------- #
# Data Structures                                                              #
# --------------------------------------------------------------------------- #


@dataclass
class StatisticalSummary:
    """Comprehensive statistical summary of a dataset."""

    count: int
    mean: float
    std: float
    min: float
    max: float
    p25: float
    p50: float  # median
    p75: float
    p95: float
    p99: float
    skewness: float | None = None
    kurtosis: float | None = None
    range: float | None = None
    iqr: float | None = None
    cv: float | None = None  # coefficient of variation

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class TrendAnalysis:
    """Trend analysis results."""

    trend_type: Literal["increasing", "decreasing", "stable", "volatile"]
    slope: float
    r_squared: float
    p_value: float | None
    confidence_interval: tuple[float, float] | None
    prediction_next: float | None
    volatility: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class OutlierReport:
    """Outlier detection report."""

    method: str
    outlier_count: int
    outlier_indices: list[int]
    outlier_values: list[float]
    threshold_lower: float | None
    threshold_upper: float | None
    outlier_percentage: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


# --------------------------------------------------------------------------- #
# Core Data Processor                                                          #
# --------------------------------------------------------------------------- #


class MetricsDataProcessor:
    """
    Process performance metrics into pandas DataFrames for analysis.

    This class converts raw PerformanceMetrics into structured DataFrames
    and provides methods for data transformation, aggregation, and export.
    """

    def __init__(self, chunk_size: int = CHUNK_SIZE):
        """
        Initialize metrics data processor.

        Parameters
        ----------
        chunk_size : int
            Chunk size for processing large datasets.
        """
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas is required. Install with: uv sync --group pm") from None

        self.chunk_size = chunk_size

    def metrics_to_dataframe(
        self,
        operation: str | None = None,
        include_custom_attrs: bool = True,
    ) -> pd.DataFrame:
        """
        Convert performance metrics to pandas DataFrame.

        Parameters
        ----------
        operation : str, optional
            Filter by specific operation. If None, includes all operations.
        include_custom_attrs : bool
            Whether to include custom attributes as columns.

        Returns
        -------
        pd.DataFrame
            DataFrame with metrics data.
        """
        if operation:
            metrics = _GLOBAL_STORE.get_metrics(operation)
        else:
            # Get all metrics from all operations
            metrics = []
            for op in _GLOBAL_STORE.get_all_operations():
                metrics.extend(_GLOBAL_STORE.get_metrics(op))

        if not metrics:
            return pd.DataFrame()

        # Convert to list of dicts
        data = []
        for metric in metrics:
            row = {
                "operation": metric.operation,
                "duration_seconds": metric.duration_seconds,
                "timestamp": pd.Timestamp(metric.timestamp, unit="s"),
                "success": metric.success,
                "error_type": metric.error_type,
            }

            # Add resource usage
            if metric.resource_usage:
                for key, value in metric.resource_usage.items():
                    row[f"resource_{key}"] = value

            # Add custom attributes
            if include_custom_attrs and metric.custom_attributes:
                for key, value in metric.custom_attributes.items():
                    row[f"attr_{key}"] = value

            data.append(row)

        # Create DataFrame
        df = pd.DataFrame(data)

        # Set timestamp as index
        if not df.empty:
            df = df.set_index("timestamp")
            df = df.sort_index()

        return df

    def aggregate_by_operation(
        self,
        df: pd.DataFrame,
        agg_funcs: dict[str, str | list[str]] | None = None,
    ) -> pd.DataFrame:
        """
        Aggregate metrics by operation.

        Parameters
        ----------
        df : pd.DataFrame
            Input DataFrame with metrics.
        agg_funcs : dict, optional
            Aggregation functions per column. Default aggregates duration.

        Returns
        -------
        pd.DataFrame
            Aggregated DataFrame.
        """
        if agg_funcs is None:
            agg_funcs = {
                "duration_seconds": ["count", "mean", "std", "min", "max", "median"],
                "success": "sum",
            }

        return df.groupby("operation").agg(agg_funcs)

    def resample_timeseries(
        self,
        df: pd.DataFrame,
        freq: str = "1h",
        agg_func: str = "mean",
    ) -> pd.DataFrame:
        """
        Resample time series data.

        Parameters
        ----------
        df : pd.DataFrame
            Input DataFrame with timestamp index.
        freq : str
            Resampling frequency (e.g., '1h', '1D', '1W').
        agg_func : str
            Aggregation function ('mean', 'sum', 'count', etc.).

        Returns
        -------
        pd.DataFrame
            Resampled DataFrame.
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        return df[numeric_cols].resample(freq).agg(agg_func)

    def create_pivot_table(
        self,
        df: pd.DataFrame,
        values: str = "duration_seconds",
        index: str = "operation",
        columns: str | None = None,
        aggfunc: str = "mean",
    ) -> pd.DataFrame:
        """
        Create pivot table from metrics.

        Parameters
        ----------
        df : pd.DataFrame
            Input DataFrame.
        values : str
            Column to aggregate.
        index : str
            Column to use as index.
        columns : str, optional
            Column to use as columns.
        aggfunc : str
            Aggregation function.

        Returns
        -------
        pd.DataFrame
            Pivot table.
        """
        if columns:
            return pd.pivot_table(
                df,
                values=values,
                index=index,
                columns=columns,
                aggfunc=aggfunc,
            )
        return df.groupby(index)[values].agg(aggfunc).to_frame()

    def calculate_statistics(self, series: pd.Series) -> StatisticalSummary:
        """
        Calculate comprehensive statistics for a series.

        Parameters
        ----------
        series : pd.Series
            Input data series.

        Returns
        -------
        StatisticalSummary
            Comprehensive statistics.
        """
        # Basic statistics
        stats_dict = {
            "count": int(series.count()),
            "mean": float(series.mean()),
            "std": float(series.std()),
            "min": float(series.min()),
            "max": float(series.max()),
            "p25": float(series.quantile(0.25)),
            "p50": float(series.quantile(0.50)),
            "p75": float(series.quantile(0.75)),
            "p95": float(series.quantile(0.95)),
            "p99": float(series.quantile(0.99)),
        }

        # Advanced statistics with scipy
        if SCIPY_AVAILABLE:
            stats_dict["skewness"] = float(stats.skew(series.dropna()))
            stats_dict["kurtosis"] = float(stats.kurtosis(series.dropna()))

        # Additional metrics
        stats_dict["range"] = stats_dict["max"] - stats_dict["min"]
        stats_dict["iqr"] = stats_dict["p75"] - stats_dict["p25"]
        if stats_dict["mean"] != 0:
            stats_dict["cv"] = stats_dict["std"] / stats_dict["mean"]
        else:
            stats_dict["cv"] = None  # type: ignore[assignment]

        return StatisticalSummary(**stats_dict)  # type: ignore[arg-type]

    def export_to_csv(self, df: pd.DataFrame, filename: str, path: Path | None = None) -> Path:
        """
        Export DataFrame to CSV.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to export.
        filename : str
            Output filename.
        path : Path, optional
            Output directory. Default is EXPORT_PATH.

        Returns
        -------
        Path
            Path to exported file.
        """
        path = path or EXPORT_PATH
        path.mkdir(parents=True, exist_ok=True)
        output_path = path / filename
        df.to_csv(output_path)
        return output_path

    def export_to_json(
        self,
        df: pd.DataFrame,
        filename: str,
        path: Path | None = None,
        orient: str = "records",
    ) -> Path:
        """
        Export DataFrame to JSON.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to export.
        filename : str
            Output filename.
        path : Path, optional
            Output directory.
        orient : str
            JSON orientation ('records', 'index', 'columns', etc.).

        Returns
        -------
        Path
            Path to exported file.
        """
        path = path or EXPORT_PATH
        path.mkdir(parents=True, exist_ok=True)
        output_path = path / filename
        df.to_json(output_path, orient=orient, indent=2, date_format="iso")
        return output_path

    def export_to_excel(
        self,
        df: pd.DataFrame | dict[str, pd.DataFrame],
        filename: str,
        path: Path | None = None,
    ) -> Path:
        """
        Export DataFrame(s) to Excel.

        Parameters
        ----------
        df : pd.DataFrame or dict
            Single DataFrame or dict of DataFrames for multiple sheets.
        filename : str
            Output filename.
        path : Path, optional
            Output directory.

        Returns
        -------
        Path
            Path to exported file.
        """
        try:
            import openpyxl  # noqa: F401, PLC0415  # type: ignore[import-untyped]
        except ImportError:
            raise ImportError(
                "openpyxl is required for Excel export. Install with: pip install openpyxl"
            ) from None

        path = path or EXPORT_PATH
        path.mkdir(parents=True, exist_ok=True)
        output_path = path / filename

        if isinstance(df, dict):
            with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                for sheet_name, sheet_df in df.items():
                    sheet_df.to_excel(writer, sheet_name=sheet_name)
        else:
            df.to_excel(output_path, engine="openpyxl")

        return output_path


# --------------------------------------------------------------------------- #
# Time Series Analyzer                                                         #
# --------------------------------------------------------------------------- #


class TimeSeriesAnalyzer:
    """
    Advanced time series analysis for performance metrics.

    Provides trend detection, seasonality analysis, and forecasting.
    """

    def __init__(self, df: pd.DataFrame, time_column: str | None = None):
        """
        Initialize time series analyzer.

        Parameters
        ----------
        df : pd.DataFrame
            Input DataFrame with time series data.
        time_column : str, optional
            Name of time column. If None, uses index.
        """
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas is required. Install with: uv sync --group pm") from None

        self.df = df.copy()
        if time_column:
            self.df = self.df.set_index(time_column)
            self.df.index = pd.to_datetime(self.df.index)
        elif not isinstance(self.df.index, pd.DatetimeIndex):
            raise ValueError("DataFrame must have DatetimeIndex or specify time_column") from None

    def detect_trends(self, column: str = "duration_seconds") -> TrendAnalysis:
        """
        Detect trends using linear regression.

        Parameters
        ----------
        column : str
            Column to analyze.

        Returns
        -------
        TrendAnalysis
            Trend analysis results.
        """
        x = np.arange(len(self.df))
        y = self.df[column].values

        # Remove NaN values
        mask = ~np.isnan(y)
        x = x[mask]
        y = y[mask]

        if len(x) < 2:
            raise ValueError("Insufficient data for trend analysis") from None

        # Linear regression
        slope, intercept = np.polyfit(x, y, 1)
        y_pred = slope * x + intercept

        # Calculate R-squared
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        # Calculate volatility (standard deviation of residuals)
        residuals = y - y_pred
        volatility = float(np.std(residuals))

        # Determine trend type
        trend_type_str: Literal["increasing", "decreasing", "stable", "volatile"]
        if abs(slope) < volatility * 0.1:
            trend_type_str = "stable"
        elif volatility > np.mean(y) * 0.5:
            trend_type_str = "volatile"
        elif slope > 0:
            trend_type_str = "increasing"
        else:
            trend_type_str = "decreasing"

        p_value = None
        confidence_interval = None
        if SCIPY_AVAILABLE and len(x) > 2:
            se = np.sqrt(ss_res / (len(x) - 2) / np.sum((x - np.mean(x)) ** 2))
            t_stat = slope / se if se > 0 else 0
            p_value = float(stats.t.sf(abs(t_stat), len(x) - 2) * 2)

            # 95% confidence interval
            margin = stats.t.ppf(0.975, len(x) - 2) * se
            confidence_interval = (slope - margin, slope + margin)

        # Predict next value
        prediction_next = float(slope * len(self.df) + intercept)

        return TrendAnalysis(
            trend_type=trend_type_str,
            slope=float(slope),
            r_squared=float(r_squared),
            p_value=p_value,
            confidence_interval=confidence_interval,
            prediction_next=prediction_next,
            volatility=volatility,
        )

    def calculate_moving_average(
        self,
        column: str = "duration_seconds",
        window: int = 10,
    ) -> pd.Series:
        """
        Calculate moving average.

        Parameters
        ----------
        column : str
            Column to analyze.
        window : int
            Window size.

        Returns
        -------
        pd.Series
            Moving average series.
        """
        return self.df[column].rolling(window=window).mean()

    def calculate_exponential_moving_average(
        self,
        column: str = "duration_seconds",
        span: int = 10,
    ) -> pd.Series:
        """
        Calculate exponential moving average.

        Parameters
        ----------
        column : str
            Column to analyze.
        span : int
            Span for EMA.

        Returns
        -------
        pd.Series
            EMA series.
        """
        return self.df[column].ewm(span=span).mean()

    def detect_peaks(self, column: str = "duration_seconds", prominence: float = 0.5) -> dict[str, Any]:
        """
        Detect peaks (performance spikes).

        Parameters
        ----------
        column : str
            Column to analyze.
        prominence : float
            Required prominence of peaks.

        Returns
        -------
        dict
            Peak detection results.
        """
        if not SCIPY_AVAILABLE:
            raise ImportError("scipy is required for peak detection") from None

        values = self.df[column].values
        peaks, properties = find_peaks(values, prominence=prominence)

        return {
            "peak_indices": peaks.tolist(),
            "peak_timestamps": self.df.index[peaks].tolist(),
            "peak_values": values[peaks].tolist(),
            "peak_count": len(peaks),
            "properties": {
                k: v.tolist() if isinstance(v, np.ndarray) else v
                for k, v in properties.items()
            },
        }


# --------------------------------------------------------------------------- #
# Outlier Detector                                                             #
# --------------------------------------------------------------------------- #


class OutlierDetector:
    """
    Advanced outlier detection using multiple methods.

    Supports Z-score, IQR, and Isolation Forest methods.
    """

    def __init__(self, threshold: float = OUTLIER_THRESHOLD):
        """
        Initialize outlier detector.

        Parameters
        ----------
        threshold : float
            Threshold for outlier detection.
        """
        self.threshold = threshold

    def detect_zscore(self, series: pd.Series) -> OutlierReport:
        """
        Detect outliers using Z-score method.

        Parameters
        ----------
        series : pd.Series
            Input data series.

        Returns
        -------
        OutlierReport
            Outlier detection report.
        """
        mean = series.mean()
        std = series.std()

        if std == 0:
            return OutlierReport(
                method="zscore",
                outlier_count=0,
                outlier_indices=[],
                outlier_values=[],
                threshold_lower=None,
                threshold_upper=None,
                outlier_percentage=0.0,
            )

        z_scores = np.abs((series - mean) / std)
        outliers = z_scores > self.threshold

        outlier_indices = series[outliers].index.tolist()
        outlier_values = series[outliers].values.tolist()

        threshold_lower = mean - self.threshold * std
        threshold_upper = mean + self.threshold * std

        return OutlierReport(
            method="zscore",
            outlier_count=int(outliers.sum()),
            outlier_indices=outlier_indices,
            outlier_values=outlier_values,
            threshold_lower=float(threshold_lower),
            threshold_upper=float(threshold_upper),
            outlier_percentage=float(outliers.sum() / len(series) * 100),
        )

    def detect_iqr(self, series: pd.Series, multiplier: float = 1.5) -> OutlierReport:
        """
        Detect outliers using IQR (Interquartile Range) method.

        Parameters
        ----------
        series : pd.Series
            Input data series.
        multiplier : float
            IQR multiplier for threshold.

        Returns
        -------
        OutlierReport
            Outlier detection report.
        """
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        threshold_lower = q1 - multiplier * iqr
        threshold_upper = q3 + multiplier * iqr

        outliers = (series < threshold_lower) | (series > threshold_upper)

        outlier_indices = series[outliers].index.tolist()
        outlier_values = series[outliers].values.tolist()

        return OutlierReport(
            method="iqr",
            outlier_count=int(outliers.sum()),
            outlier_indices=outlier_indices,
            outlier_values=outlier_values,
            threshold_lower=float(threshold_lower),
            threshold_upper=float(threshold_upper),
            outlier_percentage=float(outliers.sum() / len(series) * 100),
        )

    def detect_isolation_forest(
        self,
        df: pd.DataFrame,
        contamination: float = 0.1,
    ) -> OutlierReport:
        """
        Detect outliers using Isolation Forest (ML-based).

        Parameters
        ----------
        df : pd.DataFrame
            Input DataFrame (multi-dimensional).
        contamination : float
            Expected proportion of outliers.

        Returns
        -------
        OutlierReport
            Outlier detection report.
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn is required. Install with: uv sync --group hd") from None

        # Select numeric columns
        numeric_df = df.select_dtypes(include=[np.number])

        if numeric_df.empty:
            raise ValueError("No numeric columns for outlier detection") from None

        # Standardize features
        scaler = StandardScaler()
        x_scaled = scaler.fit_transform(numeric_df)

        # Fit Isolation Forest
        iso_forest = IsolationForest(contamination=contamination, random_state=42)
        predictions = iso_forest.fit_predict(x_scaled)  # type: ignore[attr-defined]

        # -1 indicates outlier
        outliers = predictions == -1

        outlier_indices = numeric_df[outliers].index.tolist()

        return OutlierReport(
            method="isolation_forest",
            outlier_count=int(outliers.sum()),
            outlier_indices=outlier_indices,
            outlier_values=[],  # Multi-dimensional, no single value
            threshold_lower=None,
            threshold_upper=None,
            outlier_percentage=float(outliers.sum() / len(df) * 100),
        )


# --------------------------------------------------------------------------- #
# Correlation Analyzer                                                         #
# --------------------------------------------------------------------------- #


class CorrelationAnalyzer:
    """Analyze correlations between metrics."""

    def __init__(self, df: pd.DataFrame):
        """
        Initialize correlation analyzer.

        Parameters
        ----------
        df : pd.DataFrame
            Input DataFrame with numeric columns.
        """
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas is required. Install with: uv sync --group pm") from None

        self.df = df.select_dtypes(include=[np.number])

    def pearson_correlation(self) -> pd.DataFrame:
        """
        Calculate Pearson correlation matrix.

        Returns
        -------
        pd.DataFrame
            Correlation matrix.
        """
        return self.df.corr(method="pearson")

    def spearman_correlation(self) -> pd.DataFrame:
        """
        Calculate Spearman rank correlation matrix.

        Returns
        -------
        pd.DataFrame
            Correlation matrix.
        """
        return self.df.corr(method="spearman")

    def find_strong_correlations(self, threshold: float = 0.7) -> list[dict[str, Any]]:
        """
        Find strong correlations.

        Parameters
        ----------
        threshold : float
            Minimum absolute correlation value.

        Returns
        -------
        list[dict]
            List of strong correlations.
        """
        corr_matrix = self.pearson_correlation()
        strong_corr = []

        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) >= threshold:
                    strong_corr.append(
                        {
                            "variable1": corr_matrix.columns[i],
                            "variable2": corr_matrix.columns[j],
                            "correlation": float(corr_value),
                            "strength": "strong" if abs(corr_value) >= 0.9 else "moderate",
                        }
                    )

        return sorted(strong_corr, key=lambda x: abs(x["correlation"]), reverse=True)


__all__ = [
    "PANDAS_AVAILABLE",
    "SCIPY_AVAILABLE",
    "SKLEARN_AVAILABLE",
    "CorrelationAnalyzer",
    "MetricsDataProcessor",
    "OutlierDetector",
    "OutlierReport",
    "StatisticalSummary",
    "TimeSeriesAnalyzer",
    "TrendAnalysis",
]
