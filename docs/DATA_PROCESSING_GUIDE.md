# Hyper-Advanced Data Processing Guide

This guide covers the hyper-advanced data processing capabilities in specify-cli using pandas and numpy for metrics, reports, and analysis.

## Overview

The data processing layer provides enterprise-grade capabilities for:

- **DataFrame-based Metrics**: Convert raw performance metrics to structured DataFrames
- **Time-Series Analysis**: Trend detection, moving averages, seasonality analysis
- **Statistical Analysis**: Comprehensive statistics with mean, std, percentiles, skewness, kurtosis
- **Outlier Detection**: Multiple methods (Z-score, IQR, Isolation Forest)
- **Data Aggregation**: Groupby operations, pivot tables, multi-index support
- **Correlation Analysis**: Pearson and Spearman correlation matrices
- **Chart Generation**: Matplotlib/Seaborn integration for visualization
- **Report Generation**: Automated HTML reports with charts and tables
- **Multi-Format Export**: CSV, JSON, Excel, Parquet support

## Installation

```bash
# Install core dependencies
uv sync

# Install optional data processing dependencies
uv sync --group pm --group hd

# Or install everything
uv sync --group all
```

Required dependencies:
- `numpy` (core dependency, always available)
- `pandas>=2.0.0` (optional, group: pm, all)
- `matplotlib>=3.7.0` (optional, group: hd, all)
- `seaborn` (optional, for enhanced charts)
- `openpyxl` (optional, for Excel export)
- `scipy` (optional, for advanced statistics)
- `scikit-learn>=1.3.0` (optional, group: hd, all)

## Quick Start

```python
from specify_cli.core.data_processing import MetricsDataProcessor
from specify_cli.core.reporting import create_performance_report

# Process metrics to DataFrame
processor = MetricsDataProcessor()
df = processor.metrics_to_dataframe("my_operation")

# Generate comprehensive report
report_path = create_performance_report("my_operation")
print(f"Report saved to: {report_path}")
```

## Data Processing

### MetricsDataProcessor

Convert performance metrics to pandas DataFrames for analysis:

```python
from specify_cli.core.data_processing import MetricsDataProcessor

processor = MetricsDataProcessor()

# Get metrics for specific operation
df = processor.metrics_to_dataframe(operation="ggen_sync")

# Get all metrics
df_all = processor.metrics_to_dataframe()

# Aggregate by operation
agg_df = processor.aggregate_by_operation(df_all)

# Resample time series (hourly averages)
hourly = processor.resample_timeseries(df, freq="1h", agg_func="mean")

# Calculate comprehensive statistics
stats = processor.calculate_statistics(df["duration_seconds"])
print(f"Mean: {stats.mean:.4f}s")
print(f"P95: {stats.p95:.4f}s")
print(f"P99: {stats.p99:.4f}s")
```

### Time Series Analysis

Analyze trends and patterns in performance metrics:

```python
from specify_cli.core.data_processing import TimeSeriesAnalyzer

analyzer = TimeSeriesAnalyzer(df)

# Detect trends
trend = analyzer.detect_trends()
print(f"Trend: {trend.trend_type}")
print(f"Slope: {trend.slope:.6f}")
print(f"R²: {trend.r_squared:.3f}")

# Moving averages
ma = analyzer.calculate_moving_average(window=10)
ema = analyzer.calculate_exponential_moving_average(span=10)

# Detect peaks (performance spikes)
peaks = analyzer.detect_peaks(prominence=0.5)
print(f"Peaks detected: {peaks['peak_count']}")
```

### Outlier Detection

Identify anomalous performance metrics:

```python
from specify_cli.core.data_processing import OutlierDetector

detector = OutlierDetector(threshold=3.0)

# Z-score method (statistical)
zscore_report = detector.detect_zscore(df["duration_seconds"])
print(f"Outliers: {zscore_report.outlier_count} ({zscore_report.outlier_percentage:.2f}%)")

# IQR method (robust to distribution)
iqr_report = detector.detect_iqr(df["duration_seconds"], multiplier=1.5)

# Isolation Forest (ML-based, multi-dimensional)
iso_report = detector.detect_isolation_forest(df[["duration_seconds", "memory_mb"]])
```

### Correlation Analysis

Analyze relationships between metrics:

```python
from specify_cli.core.data_processing import CorrelationAnalyzer

analyzer = CorrelationAnalyzer(df)

# Correlation matrices
pearson = analyzer.pearson_correlation()
spearman = analyzer.spearman_correlation()

# Find strong correlations
strong = analyzer.find_strong_correlations(threshold=0.7)
for corr in strong:
    print(f"{corr['variable1']} <-> {corr['variable2']}: {corr['correlation']:.3f}")
```

## Report Generation

### Pre-built Reports

Generate comprehensive reports with a single function call:

```python
from specify_cli.core.reporting import (
    create_performance_report,
    create_comparison_report,
)

# Performance report for single operation
report_path = create_performance_report("ggen_sync")

# Performance report for all operations
report_path = create_performance_report()

# Comparison report
comparison_path = create_comparison_report("fast_op", "slow_op")
```

### Custom Reports

Build custom reports with charts and tables:

```python
from specify_cli.core.reporting import ReportGenerator, ChartBuilder

# Initialize report
report = ReportGenerator(title="Custom Performance Report", theme="light")

# Add text section
report.add_section("Overview", """
<p>This report analyzes performance trends over the past week.</p>
<p>Key findings: Performance improved by 15%.</p>
""", "html")

# Add table
report.add_section("Statistics", df.describe(), "table")

# Add chart
builder = ChartBuilder()
chart = builder.line_chart(df, y="duration_seconds", title="Performance Over Time")
report.add_section("Trend Analysis", chart, "chart")

# Save report
output_path = report.save_html("custom_report.html")
```

### Chart Types

Generate various chart types:

```python
from specify_cli.core.reporting import ChartBuilder

builder = ChartBuilder(figsize=(12, 6))

# Line chart
line = builder.line_chart(df, x="timestamp", y="duration_seconds")

# Bar chart
bar = builder.bar_chart(agg_df, x="operation", y="mean_duration")

# Histogram
hist = builder.histogram(df["duration_seconds"], bins=30)

# Scatter plot
scatter = builder.scatter_plot(df, x="memory_mb", y="duration_seconds")

# Heatmap (correlation matrix)
heatmap = builder.heatmap(correlation_matrix, title="Correlation Heatmap")
```

## Data Export

Export data in multiple formats:

```python
processor = MetricsDataProcessor()

# CSV
csv_path = processor.export_to_csv(df, "metrics.csv")

# JSON
json_path = processor.export_to_json(df, "metrics.json", orient="records")

# Excel (single sheet)
excel_path = processor.export_to_excel(df, "metrics.xlsx")

# Excel (multiple sheets)
excel_path = processor.export_to_excel({
    "Raw Data": df,
    "Aggregated": agg_df,
    "Statistics": stats_df,
}, "comprehensive_metrics.xlsx")
```

## Performance Optimization

The data processing layer is optimized for performance:

### Vectorized Operations

All computations use vectorized numpy/pandas operations:

```python
# Fast: Vectorized operation
mean_duration = df["duration_seconds"].mean()

# Slow: Loop-based operation (avoid)
mean_duration = sum(df["duration_seconds"]) / len(df)
```

### Chunked Processing

Process large datasets in chunks:

```python
processor = MetricsDataProcessor(chunk_size=10000)

# Automatically processes in 10k-row chunks
large_df = processor.metrics_to_dataframe()
```

### Memory Efficiency

Optimize memory usage with proper dtypes:

```python
# Automatically uses appropriate dtypes
df = processor.metrics_to_dataframe()

# Check memory usage
print(df.memory_usage(deep=True))
```

## Performance Comparison

### Raw NumPy vs Pandas

```python
import time
import numpy as np
import pandas as pd

data = np.random.normal(0.05, 0.01, 100000)

# NumPy (baseline)
start = time.time()
np_mean = np.mean(data)
np_std = np.std(data)
np_p95 = np.percentile(data, 95)
numpy_time = time.time() - start

# Pandas
series = pd.Series(data)
start = time.time()
pd_mean = series.mean()
pd_std = series.std()
pd_p95 = series.quantile(0.95)
pandas_time = time.time() - start

print(f"NumPy:  {numpy_time*1000:.3f}ms")
print(f"Pandas: {pandas_time*1000:.3f}ms")
print(f"Overhead: {(pandas_time/numpy_time - 1)*100:.1f}%")
```

**Typical Results** (100k samples):
- NumPy: ~1-2ms
- Pandas: ~2-4ms
- Overhead: ~50-100%

Pandas provides rich functionality with acceptable overhead for most use cases.

## Integration with Observability

Seamless integration with advanced_observability.py:

```python
from specify_cli.core.advanced_observability import PerformanceTracker
from specify_cli.core.data_processing import MetricsDataProcessor

# Track performance
for i in range(100):
    with PerformanceTracker("my_operation"):
        # Your code here
        pass

# Analyze with pandas
processor = MetricsDataProcessor()
df = processor.metrics_to_dataframe("my_operation")
stats = processor.calculate_statistics(df["duration_seconds"])

print(f"Mean duration: {stats.mean:.4f}s")
print(f"P95 duration: {stats.p95:.4f}s")
```

## Complete Example

```python
from specify_cli.core.advanced_observability import PerformanceTracker
from specify_cli.core.data_processing import (
    MetricsDataProcessor,
    TimeSeriesAnalyzer,
    OutlierDetector,
)
from specify_cli.core.reporting import ReportGenerator, ChartBuilder

# 1. Collect metrics
for i in range(1000):
    with PerformanceTracker("api_request"):
        # Simulate API request
        time.sleep(random.uniform(0.01, 0.1))

# 2. Process data
processor = MetricsDataProcessor()
df = processor.metrics_to_dataframe("api_request")

# 3. Analyze
stats = processor.calculate_statistics(df["duration_seconds"])
analyzer = TimeSeriesAnalyzer(df)
trend = analyzer.detect_trends()
detector = OutlierDetector()
outliers = detector.detect_zscore(df["duration_seconds"])

# 4. Generate report
report = ReportGenerator(title="API Performance Analysis")

report.add_section("Overview", f"""
<p><strong>Total Requests:</strong> {stats.count}</p>
<p><strong>Mean Duration:</strong> {stats.mean:.3f}s</p>
<p><strong>P95 Duration:</strong> {stats.p95:.3f}s</p>
<p><strong>Trend:</strong> {trend.trend_type}</p>
<p><strong>Outliers:</strong> {outliers.outlier_count} ({outliers.outlier_percentage:.2f}%)</p>
""", "html")

builder = ChartBuilder()
chart = builder.line_chart(df, y="duration_seconds", title="Request Duration Over Time")
report.add_section("Performance Trend", chart, "chart")

report.save_html("api_performance_report.html")
```

## Best Practices

1. **Use vectorized operations**: Avoid loops, use pandas/numpy vectorized methods
2. **Filter early**: Filter DataFrames before expensive operations
3. **Choose appropriate methods**: Z-score for normal distributions, IQR for skewed data
4. **Monitor memory**: Use `df.memory_usage()` to track memory consumption
5. **Export regularly**: Save intermediate results to avoid recomputation
6. **Generate reports**: Use pre-built report templates for common analyses
7. **Validate results**: Cross-check statistical results with baseline expectations

## Troubleshooting

### Import Errors

```python
# Check availability
from specify_cli.core.data_processing import (
    PANDAS_AVAILABLE,
    SCIPY_AVAILABLE,
    SKLEARN_AVAILABLE,
)

print(f"Pandas: {PANDAS_AVAILABLE}")
print(f"SciPy: {SCIPY_AVAILABLE}")
print(f"Scikit-learn: {SKLEARN_AVAILABLE}")
```

### Performance Issues

```python
# Profile operations
import time

start = time.time()
df = processor.metrics_to_dataframe()
print(f"DataFrame conversion: {time.time() - start:.3f}s")

start = time.time()
stats = processor.calculate_statistics(df["duration_seconds"])
print(f"Statistics calculation: {time.time() - start:.3f}s")
```

### Memory Issues

```python
# Monitor memory usage
print(df.memory_usage(deep=True).sum() / 1024**2, "MB")

# Use chunked processing
processor = MetricsDataProcessor(chunk_size=5000)
```

## API Reference

### MetricsDataProcessor

- `metrics_to_dataframe(operation, include_custom_attrs)` - Convert metrics to DataFrame
- `aggregate_by_operation(df, agg_funcs)` - Aggregate by operation
- `resample_timeseries(df, freq, agg_func)` - Resample time series
- `calculate_statistics(series)` - Calculate comprehensive statistics
- `export_to_csv(df, filename, path)` - Export to CSV
- `export_to_json(df, filename, path, orient)` - Export to JSON
- `export_to_excel(df, filename, path)` - Export to Excel

### TimeSeriesAnalyzer

- `detect_trends(column)` - Detect trends using linear regression
- `calculate_moving_average(column, window)` - Calculate moving average
- `calculate_exponential_moving_average(column, span)` - Calculate EMA
- `detect_peaks(column, prominence)` - Detect peaks (spikes)

### OutlierDetector

- `detect_zscore(series)` - Z-score outlier detection
- `detect_iqr(series, multiplier)` - IQR outlier detection
- `detect_isolation_forest(df, contamination)` - ML-based outlier detection

### CorrelationAnalyzer

- `pearson_correlation()` - Pearson correlation matrix
- `spearman_correlation()` - Spearman correlation matrix
- `find_strong_correlations(threshold)` - Find strong correlations

### ChartBuilder

- `line_chart(df, x, y, title, xlabel, ylabel)` - Line chart
- `bar_chart(df, x, y, title, horizontal)` - Bar chart
- `histogram(series, bins, title, xlabel)` - Histogram
- `scatter_plot(df, x, y, title, hue)` - Scatter plot
- `heatmap(df, title, cmap, annot)` - Heatmap

### ReportGenerator

- `add_section(title, content, section_type)` - Add section
- `add_metadata(key, value)` - Add metadata
- `generate_html()` - Generate HTML
- `save_html(filename, path)` - Save HTML report

## See Also

- [Advanced Observability Guide](ADVANCED_OBSERVABILITY.md)
- [Advanced Testing Guide](ADVANCED_TESTING_GUIDE.md)
- [Advanced Cache Guide](ADVANCED_CACHE_GUIDE.md)
