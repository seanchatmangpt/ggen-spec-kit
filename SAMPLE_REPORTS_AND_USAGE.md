# Sample Reports and Usage Patterns

This document provides real-world usage patterns and sample outputs from the hyper-advanced data processing layer.

## Sample Report 1: Performance Analysis Dashboard

```python
from specify_cli.core.advanced_observability import PerformanceTracker
from specify_cli.core.data_processing import MetricsDataProcessor, TimeSeriesAnalyzer, OutlierDetector
from specify_cli.core.reporting import ReportGenerator, ChartBuilder
import time
import random

# Simulate 1000 API requests
print("Simulating API requests...")
for i in range(1000):
    with PerformanceTracker("api_request"):
        time.sleep(random.uniform(0.01, 0.15))  # 10-150ms response time

# Process data
processor = MetricsDataProcessor()
df = processor.metrics_to_dataframe("api_request")

# Create comprehensive report
report = ReportGenerator(title="API Performance Analysis Dashboard")

# Section 1: Executive Summary
stats = processor.calculate_statistics(df["duration_seconds"])
report.add_section("Executive Summary", f"""
<div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
    <h3>Performance Metrics</h3>
    <table style="width: 100%; border-collapse: collapse;">
        <tr>
            <td><strong>Total Requests:</strong></td>
            <td>{stats.count:,}</td>
            <td><strong>Time Range:</strong></td>
            <td>{df.index.min()} to {df.index.max()}</td>
        </tr>
        <tr>
            <td><strong>Mean Latency:</strong></td>
            <td>{stats.mean*1000:.2f}ms</td>
            <td><strong>Median Latency:</strong></td>
            <td>{stats.p50*1000:.2f}ms</td>
        </tr>
        <tr>
            <td><strong>P95 Latency:</strong></td>
            <td style="color: {'green' if stats.p95*1000 < 100 else 'orange'};">
                <strong>{stats.p95*1000:.2f}ms</strong>
            </td>
            <td><strong>P99 Latency:</strong></td>
            <td style="color: {'green' if stats.p99*1000 < 150 else 'orange'};">
                <strong>{stats.p99*1000:.2f}ms</strong>
            </td>
        </tr>
        <tr>
            <td><strong>Std Deviation:</strong></td>
            <td>{stats.std*1000:.2f}ms</td>
            <td><strong>Success Rate:</strong></td>
            <td>100%</td>
        </tr>
    </table>
</div>
""", "html")

# Section 2: Performance Trend
builder = ChartBuilder(figsize=(14, 6))
trend_chart = builder.line_chart(
    df.reset_index(),
    x="timestamp",
    y="duration_seconds",
    title="API Response Time Over Time",
    ylabel="Duration (seconds)"
)
report.add_section("Performance Trend", trend_chart, "chart")

# Section 3: Distribution Analysis
dist_chart = builder.histogram(
    df["duration_seconds"],
    bins=50,
    title="Response Time Distribution",
    xlabel="Duration (seconds)"
)
report.add_section("Distribution Analysis", dist_chart, "chart")

# Section 4: Trend Analysis
analyzer = TimeSeriesAnalyzer(df)
trend = analyzer.detect_trends()
report.add_section("Trend Analysis", f"""
<div style="background: {'#d4edda' if trend.trend_type in ['stable', 'decreasing'] else '#fff3cd'};
     padding: 20px; border-radius: 8px;">
    <h4>Statistical Trend Analysis</h4>
    <p><strong>Trend Type:</strong> <span style="font-size: 1.2em; font-weight: bold;">
        {trend.trend_type.upper()}</span></p>
    <p><strong>Slope:</strong> {trend.slope:.6f} (
        {'improving' if trend.slope < 0 else 'degrading' if trend.slope > 0 else 'stable'}
        )</p>
    <p><strong>R² (Goodness of Fit):</strong> {trend.r_squared:.3f}</p>
    <p><strong>Volatility:</strong> {trend.volatility*1000:.2f}ms</p>
    {f"<p><strong>Predicted Next:</strong> {trend.prediction_next*1000:.2f}ms</p>" if trend.prediction_next else ""}
</div>
""", "html")

# Section 5: Outlier Detection
detector = OutlierDetector(threshold=3.0)
outliers = detector.detect_zscore(df["duration_seconds"])
report.add_section("Outlier Detection", f"""
<div style="background: {'#d4edda' if outliers.outlier_percentage < 5 else '#f8d7da'};
     padding: 20px; border-radius: 8px;">
    <h4>Anomaly Detection Results (Z-Score Method)</h4>
    <p><strong>Outliers Detected:</strong> {outliers.outlier_count} out of {stats.count}
       ({outliers.outlier_percentage:.2f}%)</p>
    <p><strong>Normal Range:</strong>
       [{outliers.threshold_lower*1000:.2f}ms, {outliers.threshold_upper*1000:.2f}ms]</p>
    <p><strong>Status:</strong>
       <span style="font-weight: bold;">
           {'✓ HEALTHY' if outliers.outlier_percentage < 5 else '⚠ ATTENTION NEEDED'}
       </span>
    </p>
</div>
""", "html")

# Section 6: Performance Breakdown
agg_df = processor.aggregate_by_operation(df)
report.add_section("Detailed Statistics", agg_df, "table")

# Save report
output_path = report.save_html("api_performance_dashboard.html")
print(f"\n✓ Report generated: {output_path}")
```

**Sample Output:**
```
✓ Report generated: .specify/reports/api_performance_dashboard.html

Open in browser to view:
- Executive summary with key metrics
- Interactive time series chart
- Distribution histogram
- Trend analysis with predictions
- Outlier detection results
- Detailed statistics table
```

## Sample Report 2: Before/After Performance Comparison

```python
from specify_cli.core.data_processing import MetricsDataProcessor
from specify_cli.core.reporting import create_comparison_report

# Generate comparison report
report_path = create_comparison_report(
    "before_optimization",
    "after_optimization"
)

print(f"Comparison report: {report_path}")
```

**Sample Output:**
```
Comparison Report: before_optimization vs after_optimization

Statistical Comparison:
┌─────────┬────────────────────┬───────────────────┐
│ Metric  │ before_optimization│ after_optimization│
├─────────┼────────────────────┼───────────────────┤
│ Mean    │ 0.125s             │ 0.045s (-64%)     │
│ Median  │ 0.118s             │ 0.042s (-64%)     │
│ Std Dev │ 0.032s             │ 0.012s (-63%)     │
│ P95     │ 0.178s             │ 0.065s (-63%)     │
│ P99     │ 0.201s             │ 0.078s (-61%)     │
└─────────┴────────────────────┴───────────────────┘

Improvement: 64% faster (mean latency)
```

## Sample Report 3: Custom Analysis Pipeline

```python
from specify_cli.core.data_processing import (
    MetricsDataProcessor,
    TimeSeriesAnalyzer,
    CorrelationAnalyzer
)
from specify_cli.core.reporting import ReportGenerator, ChartBuilder

# Process data
processor = MetricsDataProcessor()
df = processor.metrics_to_dataframe()

# Custom analysis pipeline
report = ReportGenerator(title="Custom Analysis Pipeline")

# 1. Time series resampling
hourly_df = processor.resample_timeseries(df, freq="1h", agg_func="mean")
report.add_section("Hourly Averages", hourly_df.head(24), "table")

# 2. Correlation analysis (if multiple metrics available)
if len(df.select_dtypes(include=['number']).columns) > 1:
    analyzer = CorrelationAnalyzer(df)
    corr_matrix = analyzer.pearson_correlation()

    builder = ChartBuilder()
    heatmap = builder.heatmap(corr_matrix, title="Metric Correlations")
    report.add_section("Correlation Analysis", heatmap, "chart")

    strong_corr = analyzer.find_strong_correlations(threshold=0.7)
    corr_html = "<ul>"
    for corr in strong_corr:
        corr_html += f"<li>{corr['variable1']} ↔ {corr['variable2']}: {corr['correlation']:.3f}</li>"
    corr_html += "</ul>"
    report.add_section("Strong Correlations", corr_html, "html")

# 3. Moving average analysis
if "duration_seconds" in df.columns:
    analyzer = TimeSeriesAnalyzer(df)
    ma = analyzer.calculate_moving_average(window=10)
    ema = analyzer.calculate_exponential_moving_average(span=10)

    # Combine for chart
    ma_df = df.copy()
    ma_df["MA(10)"] = ma
    ma_df["EMA(10)"] = ema

    builder = ChartBuilder(figsize=(14, 6))
    ma_chart = builder.line_chart(
        ma_df.reset_index(),
        x="timestamp",
        y=["duration_seconds", "MA(10)", "EMA(10)"],
        title="Performance with Moving Averages"
    )
    report.add_section("Smoothed Trends", ma_chart, "chart")

# Save report
output_path = report.save_html("custom_analysis.html")
print(f"Custom analysis report: {output_path}")
```

## Sample Export Formats

### CSV Export

```python
processor = MetricsDataProcessor()
df = processor.metrics_to_dataframe()

# Export to CSV
csv_path = processor.export_to_csv(df, "metrics_export.csv")
print(f"CSV exported: {csv_path}")
```

**Sample CSV Output:**
```csv
timestamp,operation,duration_seconds,success,error_type
2024-01-01 10:00:00,api_request,0.045,True,
2024-01-01 10:00:01,api_request,0.052,True,
2024-01-01 10:00:02,api_request,0.038,True,
...
```

### JSON Export

```python
json_path = processor.export_to_json(df, "metrics_export.json", orient="records")
```

**Sample JSON Output:**
```json
[
    {
        "timestamp": "2024-01-01T10:00:00",
        "operation": "api_request",
        "duration_seconds": 0.045,
        "success": true,
        "error_type": null
    },
    {
        "timestamp": "2024-01-01T10:00:01",
        "operation": "api_request",
        "duration_seconds": 0.052,
        "success": true,
        "error_type": null
    }
]
```

### Excel Export (Multi-Sheet)

```python
# Create comprehensive Excel workbook
excel_path = processor.export_to_excel({
    "Raw Data": df,
    "Hourly Averages": processor.resample_timeseries(df, "1h"),
    "Statistics": processor.aggregate_by_operation(df),
}, "comprehensive_metrics.xlsx")

print(f"Excel workbook exported: {excel_path}")
```

**Sample Excel Output:**
- Sheet 1: "Raw Data" - All metrics with timestamps
- Sheet 2: "Hourly Averages" - Resampled time series
- Sheet 3: "Statistics" - Aggregated statistics by operation

## Performance Analysis Patterns

### Pattern 1: Baseline Establishment

```python
# Establish performance baseline
processor = MetricsDataProcessor()
df = processor.metrics_to_dataframe("production_api")
stats = processor.calculate_statistics(df["duration_seconds"])

baseline = {
    "mean": stats.mean,
    "p95": stats.p95,
    "p99": stats.p99,
    "std": stats.std
}

# Save baseline
import json
with open(".specify/baselines/api_baseline.json", "w") as f:
    json.dump(baseline, f, indent=2)

print("Baseline established:")
print(f"  Mean: {stats.mean*1000:.2f}ms")
print(f"  P95:  {stats.p95*1000:.2f}ms")
print(f"  P99:  {stats.p99*1000:.2f}ms")
```

### Pattern 2: Performance Regression Detection

```python
# Compare current performance against baseline
import json

with open(".specify/baselines/api_baseline.json") as f:
    baseline = json.load(f)

processor = MetricsDataProcessor()
df = processor.metrics_to_dataframe("production_api")
current_stats = processor.calculate_statistics(df["duration_seconds"])

# Check for regressions
regressions = []
if current_stats.mean > baseline["mean"] * 1.1:  # 10% threshold
    regressions.append(f"Mean latency increased by {((current_stats.mean/baseline['mean']-1)*100):.1f}%")

if current_stats.p95 > baseline["p95"] * 1.15:  # 15% threshold
    regressions.append(f"P95 latency increased by {((current_stats.p95/baseline['p95']-1)*100):.1f}%")

if regressions:
    print("⚠ PERFORMANCE REGRESSIONS DETECTED:")
    for regression in regressions:
        print(f"  - {regression}")
else:
    print("✓ Performance within baseline thresholds")
```

### Pattern 3: Capacity Planning

```python
# Analyze capacity and predict scaling needs
processor = MetricsDataProcessor()
df = processor.metrics_to_dataframe()

# Resample to hourly throughput
hourly = processor.resample_timeseries(df, "1h", "count")

# Analyze trends
analyzer = TimeSeriesAnalyzer(df)
trend = analyzer.detect_trends()

if trend.trend_type == "increasing":
    print(f"⚠ Increasing load detected (slope: {trend.slope:.6f})")
    if trend.prediction_next:
        print(f"  Predicted throughput next hour: {trend.prediction_next:.0f} requests")
else:
    print(f"✓ Load trend: {trend.trend_type}")

# Identify peak hours
peak_hour = hourly.idxmax()
peak_count = hourly.max()
print(f"\nPeak hour: {peak_hour} ({peak_count:.0f} requests)")
```

## Real-World Use Cases

### Use Case 1: API Performance Monitoring

```python
# Continuous monitoring with automatic reporting
from specify_cli.core.reporting import create_performance_report

# Generate daily report
report = create_performance_report("api_endpoint")
print(f"Daily API report: {report}")

# Automated email/slack notification (pseudo-code)
# send_notification(report_path=report)
```

### Use Case 2: Database Query Optimization

```python
# Compare query performance before/after optimization
from specify_cli.core.reporting import create_comparison_report

report = create_comparison_report(
    "db_query_before",
    "db_query_after"
)
print(f"Query optimization report: {report}")
```

### Use Case 3: Load Testing Analysis

```python
# Analyze load test results
processor = MetricsDataProcessor()
df = processor.metrics_to_dataframe("load_test")

# Calculate percentiles
stats = processor.calculate_statistics(df["duration_seconds"])

# Generate load test report
report = ReportGenerator(title="Load Test Results")
report.add_section("Summary", f"""
<h3>Load Test Summary</h3>
<p><strong>Total Requests:</strong> {stats.count:,}</p>
<p><strong>Requests/sec:</strong> {stats.count / (df.index.max() - df.index.min()).total_seconds():.2f}</p>
<p><strong>Mean Latency:</strong> {stats.mean*1000:.2f}ms</p>
<p><strong>P95 Latency:</strong> {stats.p95*1000:.2f}ms</p>
<p><strong>P99 Latency:</strong> {stats.p99*1000:.2f}ms</p>
<p><strong>Success Rate:</strong> 100%</p>
""", "html")

report.save_html("load_test_results.html")
```

## Tips and Best Practices

### 1. Efficient Data Processing

```python
# ✓ Good: Process once, analyze multiple times
processor = MetricsDataProcessor()
df = processor.metrics_to_dataframe()

stats = processor.calculate_statistics(df["duration_seconds"])
analyzer = TimeSeriesAnalyzer(df)
trend = analyzer.detect_trends()

# ✗ Bad: Reprocessing each time
stats = processor.calculate_statistics(
    processor.metrics_to_dataframe()["duration_seconds"]
)
```

### 2. Memory Management

```python
# For large datasets, use chunked processing
processor = MetricsDataProcessor(chunk_size=10000)

# Export incrementally
csv_path = processor.export_to_csv(df, "large_export.csv")
```

### 3. Visualization Best Practices

```python
# Use appropriate figure sizes
builder = ChartBuilder(figsize=(14, 6))  # Wide for time series
builder = ChartBuilder(figsize=(10, 8))  # Square for heatmaps

# Use meaningful titles and labels
chart = builder.line_chart(
    df,
    y="duration_seconds",
    title="API Response Time - Last 24 Hours",
    ylabel="Latency (seconds)"
)
```

## Conclusion

The hyper-advanced data processing layer provides:

- ✅ Comprehensive metrics analysis with pandas
- ✅ Statistical analysis and trend detection
- ✅ Multiple outlier detection methods
- ✅ Professional report generation
- ✅ Multi-format data export
- ✅ Real-world usage patterns

For complete documentation, see:
- `/docs/DATA_PROCESSING_GUIDE.md` - Complete user guide
- `/examples/data_processing_integration.py` - Full integration example
- `/examples/data_processing_benchmark.py` - Performance benchmarks
