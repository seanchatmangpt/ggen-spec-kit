"""
Tests for data_processing module.

Run with:
    uv sync --group pm --group hd --group dev
    uv run pytest tests/unit/test_data_processing.py -v
"""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pytest

# Import components to test
from specify_cli.core.advanced_observability import PerformanceTracker, _GLOBAL_STORE
from specify_cli.core.data_processing import (
    PANDAS_AVAILABLE,
    SCIPY_AVAILABLE,
    SKLEARN_AVAILABLE,
    CorrelationAnalyzer,
    MetricsDataProcessor,
    OutlierDetector,
    TimeSeriesAnalyzer,
)

# Skip all tests if pandas not available
pytestmark = pytest.mark.skipif(not PANDAS_AVAILABLE, reason="pandas not installed")

if PANDAS_AVAILABLE:
    import pandas as pd


@pytest.fixture
def sample_metrics():
    """Create sample metrics for testing."""
    # Clear existing metrics
    _GLOBAL_STORE._metrics.clear()

    # Generate sample metrics
    for i in range(100):
        with PerformanceTracker("test_operation"):
            time.sleep(0.001)  # 1ms

    for i in range(50):
        with PerformanceTracker("slow_operation"):
            time.sleep(0.002)  # 2ms

    yield

    # Cleanup
    _GLOBAL_STORE._metrics.clear()


@pytest.fixture
def sample_dataframe():
    """Create sample DataFrame for testing."""
    dates = pd.date_range("2024-01-01", periods=100, freq="1h")
    return pd.DataFrame(
        {
            "duration_seconds": np.random.normal(0.05, 0.01, 100),
            "success": [True] * 95 + [False] * 5,
            "operation": ["test_op"] * 100,
        },
        index=dates,
    )


class TestMetricsDataProcessor:
    """Test MetricsDataProcessor class."""

    def test_initialization(self):
        """Test processor initialization."""
        processor = MetricsDataProcessor(chunk_size=5000)
        assert processor.chunk_size == 5000

    def test_metrics_to_dataframe(self, sample_metrics):
        """Test converting metrics to DataFrame."""
        processor = MetricsDataProcessor()
        df = processor.metrics_to_dataframe(operation="test_operation")

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 100
        assert "duration_seconds" in df.columns
        assert "operation" in df.columns
        assert "success" in df.columns
        assert isinstance(df.index, pd.DatetimeIndex)

    def test_metrics_to_dataframe_all_operations(self, sample_metrics):
        """Test converting all operations to DataFrame."""
        processor = MetricsDataProcessor()
        df = processor.metrics_to_dataframe()

        assert len(df) == 150  # 100 + 50
        assert "test_operation" in df["operation"].values
        assert "slow_operation" in df["operation"].values

    def test_aggregate_by_operation(self, sample_metrics):
        """Test aggregation by operation."""
        processor = MetricsDataProcessor()
        df = processor.metrics_to_dataframe()
        agg_df = processor.aggregate_by_operation(df)

        assert len(agg_df) == 2  # Two operations
        assert ("duration_seconds", "mean") in agg_df.columns
        assert ("duration_seconds", "count") in agg_df.columns

    def test_resample_timeseries(self, sample_dataframe):
        """Test time series resampling."""
        processor = MetricsDataProcessor()
        resampled = processor.resample_timeseries(sample_dataframe, freq="1D", agg_func="mean")

        assert isinstance(resampled, pd.DataFrame)
        assert len(resampled) <= len(sample_dataframe)

    def test_calculate_statistics(self, sample_dataframe):
        """Test statistics calculation."""
        processor = MetricsDataProcessor()
        stats = processor.calculate_statistics(sample_dataframe["duration_seconds"])

        assert stats.count == 100
        assert stats.mean > 0
        assert stats.std > 0
        assert stats.min <= stats.p50 <= stats.max
        assert stats.p50 <= stats.p95 <= stats.p99
        assert stats.iqr == stats.p75 - stats.p25

    def test_export_to_csv(self, sample_dataframe, tmp_path):
        """Test CSV export."""
        processor = MetricsDataProcessor()
        output_path = processor.export_to_csv(sample_dataframe, "test.csv", path=tmp_path)

        assert output_path.exists()
        assert output_path.suffix == ".csv"

        # Verify can be read back
        df_read = pd.read_csv(output_path)
        assert len(df_read) == len(sample_dataframe)

    def test_export_to_json(self, sample_dataframe, tmp_path):
        """Test JSON export."""
        processor = MetricsDataProcessor()
        output_path = processor.export_to_json(sample_dataframe, "test.json", path=tmp_path)

        assert output_path.exists()
        assert output_path.suffix == ".json"

        # Verify can be read back
        df_read = pd.read_json(output_path)
        assert len(df_read) == len(sample_dataframe)


class TestTimeSeriesAnalyzer:
    """Test TimeSeriesAnalyzer class."""

    def test_initialization(self, sample_dataframe):
        """Test analyzer initialization."""
        analyzer = TimeSeriesAnalyzer(sample_dataframe)
        assert isinstance(analyzer.df, pd.DataFrame)
        assert isinstance(analyzer.df.index, pd.DatetimeIndex)

    def test_detect_trends(self, sample_dataframe):
        """Test trend detection."""
        analyzer = TimeSeriesAnalyzer(sample_dataframe)
        trend = analyzer.detect_trends()

        assert trend.trend_type in ["increasing", "decreasing", "stable", "volatile"]
        assert isinstance(trend.slope, float)
        assert 0 <= trend.r_squared <= 1
        assert trend.volatility >= 0

    def test_detect_trends_increasing(self):
        """Test trend detection with increasing data."""
        dates = pd.date_range("2024-01-01", periods=50, freq="1h")
        df = pd.DataFrame(
            {"duration_seconds": np.linspace(0.01, 0.1, 50)},
            index=dates,
        )

        analyzer = TimeSeriesAnalyzer(df)
        trend = analyzer.detect_trends()

        assert trend.trend_type in ["increasing", "stable"]
        assert trend.slope > 0

    def test_calculate_moving_average(self, sample_dataframe):
        """Test moving average calculation."""
        analyzer = TimeSeriesAnalyzer(sample_dataframe)
        ma = analyzer.calculate_moving_average(window=10)

        assert isinstance(ma, pd.Series)
        assert len(ma) == len(sample_dataframe)
        # First 9 values should be NaN
        assert ma[:9].isna().all()

    def test_calculate_exponential_moving_average(self, sample_dataframe):
        """Test EMA calculation."""
        analyzer = TimeSeriesAnalyzer(sample_dataframe)
        ema = analyzer.calculate_exponential_moving_average(span=10)

        assert isinstance(ema, pd.Series)
        assert len(ema) == len(sample_dataframe)

    @pytest.mark.skipif(not SCIPY_AVAILABLE, reason="scipy not installed")
    def test_detect_peaks(self):
        """Test peak detection."""
        # Create data with known peaks
        dates = pd.date_range("2024-01-01", periods=100, freq="1h")
        values = np.sin(np.linspace(0, 4 * np.pi, 100)) + 1
        df = pd.DataFrame({"duration_seconds": values}, index=dates)

        analyzer = TimeSeriesAnalyzer(df)
        peaks = analyzer.detect_peaks(prominence=0.5)

        assert "peak_count" in peaks
        assert "peak_indices" in peaks
        assert "peak_values" in peaks
        assert peaks["peak_count"] > 0


class TestOutlierDetector:
    """Test OutlierDetector class."""

    def test_initialization(self):
        """Test detector initialization."""
        detector = OutlierDetector(threshold=2.5)
        assert detector.threshold == 2.5

    def test_detect_zscore(self):
        """Test Z-score outlier detection."""
        # Create data with known outliers
        data = pd.Series([1.0] * 95 + [10.0] * 5)
        detector = OutlierDetector(threshold=3.0)
        report = detector.detect_zscore(data)

        assert report.method == "zscore"
        assert report.outlier_count > 0
        assert report.outlier_percentage > 0
        assert report.threshold_lower is not None
        assert report.threshold_upper is not None

    def test_detect_zscore_no_outliers(self):
        """Test Z-score with no outliers."""
        data = pd.Series([1.0] * 100)
        detector = OutlierDetector(threshold=3.0)
        report = detector.detect_zscore(data)

        assert report.outlier_count == 0

    def test_detect_iqr(self):
        """Test IQR outlier detection."""
        # Create data with known outliers
        data = pd.Series([1.0] * 95 + [100.0] * 5)
        detector = OutlierDetector()
        report = detector.detect_iqr(data, multiplier=1.5)

        assert report.method == "iqr"
        assert report.outlier_count > 0
        assert report.threshold_lower is not None
        assert report.threshold_upper is not None

    @pytest.mark.skipif(not SKLEARN_AVAILABLE, reason="scikit-learn not installed")
    def test_detect_isolation_forest(self):
        """Test Isolation Forest outlier detection."""
        # Create data with outliers
        df = pd.DataFrame(
            {
                "duration_seconds": [0.05] * 90 + [1.0] * 10,
                "memory_mb": [100] * 90 + [1000] * 10,
            }
        )

        detector = OutlierDetector()
        report = detector.detect_isolation_forest(df, contamination=0.1)

        assert report.method == "isolation_forest"
        assert report.outlier_count > 0


class TestCorrelationAnalyzer:
    """Test CorrelationAnalyzer class."""

    def test_initialization(self):
        """Test analyzer initialization."""
        df = pd.DataFrame(
            {
                "duration": [1.0, 2.0, 3.0],
                "memory": [100, 200, 300],
            }
        )
        analyzer = CorrelationAnalyzer(df)
        assert isinstance(analyzer.df, pd.DataFrame)

    def test_pearson_correlation(self):
        """Test Pearson correlation."""
        df = pd.DataFrame(
            {
                "duration": [1.0, 2.0, 3.0, 4.0, 5.0],
                "memory": [100, 200, 300, 400, 500],
            }
        )
        analyzer = CorrelationAnalyzer(df)
        corr = analyzer.pearson_correlation()

        assert isinstance(corr, pd.DataFrame)
        assert corr.shape == (2, 2)
        # Perfect correlation with self
        assert corr.loc["duration", "duration"] == 1.0
        # Strong positive correlation
        assert corr.loc["duration", "memory"] > 0.9

    def test_spearman_correlation(self):
        """Test Spearman correlation."""
        df = pd.DataFrame(
            {
                "duration": [1.0, 2.0, 3.0, 4.0, 5.0],
                "memory": [100, 200, 300, 400, 500],
            }
        )
        analyzer = CorrelationAnalyzer(df)
        corr = analyzer.spearman_correlation()

        assert isinstance(corr, pd.DataFrame)
        assert corr.shape == (2, 2)

    def test_find_strong_correlations(self):
        """Test finding strong correlations."""
        df = pd.DataFrame(
            {
                "duration": [1.0, 2.0, 3.0, 4.0, 5.0],
                "memory": [100, 200, 300, 400, 500],
                "cpu": [10, 20, 30, 40, 50],
            }
        )
        analyzer = CorrelationAnalyzer(df)
        strong = analyzer.find_strong_correlations(threshold=0.9)

        assert isinstance(strong, list)
        assert len(strong) > 0
        for corr in strong:
            assert "variable1" in corr
            assert "variable2" in corr
            assert "correlation" in corr
            assert abs(corr["correlation"]) >= 0.9


class TestIntegration:
    """Integration tests combining multiple components."""

    def test_end_to_end_workflow(self, sample_metrics, tmp_path):
        """Test complete workflow from metrics to export."""
        # Process metrics
        processor = MetricsDataProcessor()
        df = processor.metrics_to_dataframe()

        # Calculate statistics
        stats = processor.calculate_statistics(df["duration_seconds"])
        assert stats.count > 0

        # Analyze time series
        analyzer = TimeSeriesAnalyzer(df[df["operation"] == "test_operation"])
        trend = analyzer.detect_trends()
        assert trend.trend_type in ["increasing", "decreasing", "stable", "volatile"]

        # Detect outliers
        detector = OutlierDetector()
        outliers = detector.detect_zscore(df["duration_seconds"])
        assert outliers.outlier_count >= 0

        # Export
        csv_path = processor.export_to_csv(df, "integration_test.csv", path=tmp_path)
        assert csv_path.exists()

    def test_performance_comparison(self):
        """Test performance: pandas vs raw numpy."""
        # Generate large dataset
        data = np.random.normal(0.05, 0.01, 10000)

        # Raw numpy
        start = time.time()
        numpy_mean = np.mean(data)
        numpy_std = np.std(data)
        numpy_p95 = np.percentile(data, 95)
        numpy_time = time.time() - start

        # Pandas
        series = pd.Series(data)
        start = time.time()
        pandas_mean = series.mean()
        pandas_std = series.std()
        pandas_p95 = series.quantile(0.95)
        pandas_time = time.time() - start

        # Verify results are similar
        assert abs(numpy_mean - pandas_mean) < 0.0001
        assert abs(numpy_std - pandas_std) < 0.0001
        assert abs(numpy_p95 - pandas_p95) < 0.0001

        # Performance should be comparable (pandas may be slightly slower but acceptable)
        assert pandas_time < numpy_time * 10  # Allow 10x overhead
