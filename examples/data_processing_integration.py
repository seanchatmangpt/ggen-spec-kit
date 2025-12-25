"""
Data Processing Integration Example
====================================

This example demonstrates the hyper-advanced data processing capabilities
using pandas and numpy with the specify-cli observability infrastructure.

Run with:
    uv sync --group pm --group hd
    uv run python examples/data_processing_integration.py
"""

from __future__ import annotations

import time
from pathlib import Path

# Import observability components
from specify_cli.core.advanced_observability import PerformanceTracker, _GLOBAL_STORE

# Import data processing components
from specify_cli.core.data_processing import (
    CorrelationAnalyzer,
    MetricsDataProcessor,
    OutlierDetector,
    TimeSeriesAnalyzer,
)

# Import reporting components
from specify_cli.core.reporting import (
    ChartBuilder,
    ReportGenerator,
    create_comparison_report,
    create_performance_report,
)


def simulate_operations():
    """Simulate various operations with different performance characteristics."""
    print("=" * 80)
    print("SIMULATING OPERATIONS")
    print("=" * 80)

    # Simulate fast operation
    print("\n1. Simulating fast_operation (100 samples)...")
    for i in range(100):
        with PerformanceTracker("fast_operation"):
            time.sleep(0.01 + 0.005 * (i % 10))  # 10-15ms

    # Simulate slow operation
    print("2. Simulating slow_operation (100 samples)...")
    for i in range(100):
        with PerformanceTracker("slow_operation"):
            time.sleep(0.05 + 0.01 * (i % 5))  # 50-100ms

    # Simulate operation with outliers
    print("3. Simulating operation_with_outliers (100 samples)...")
    for i in range(100):
        with PerformanceTracker("operation_with_outliers"):
            if i % 20 == 0:
                time.sleep(0.5)  # Outlier: 500ms
            else:
                time.sleep(0.02)  # Normal: 20ms

    # Simulate operation with increasing trend
    print("4. Simulating increasing_trend (50 samples)...")
    for i in range(50):
        with PerformanceTracker("increasing_trend"):
            time.sleep(0.01 + 0.001 * i)  # Gradually increasing

    print("\nAll operations simulated successfully!")


def demonstrate_data_processing():
    """Demonstrate data processing capabilities."""
    print("\n" + "=" * 80)
    print("DATA PROCESSING DEMONSTRATION")
    print("=" * 80)

    processor = MetricsDataProcessor()

    # Convert metrics to DataFrame
    print("\n1. Converting metrics to DataFrame...")
    df_all = processor.metrics_to_dataframe()
    print(f"   Total metrics: {len(df_all)}")
    print(f"   Columns: {', '.join(df_all.columns)}")
    print(f"\n   First 5 rows:")
    print(df_all.head())

    # Aggregate by operation
    print("\n2. Aggregating by operation...")
    agg_df = processor.aggregate_by_operation(df_all)
    print(agg_df)

    # Time series resampling
    print("\n3. Resampling time series (1-minute intervals)...")
    resampled = processor.resample_timeseries(df_all, freq="1min")
    print(f"   Resampled shape: {resampled.shape}")
    print(resampled.head())

    # Calculate statistics
    print("\n4. Calculating comprehensive statistics...")
    stats = processor.calculate_statistics(df_all["duration_seconds"])
    print(f"   Count: {stats.count}")
    print(f"   Mean: {stats.mean:.4f}s")
    print(f"   Std: {stats.std:.4f}s")
    print(f"   Min: {stats.min:.4f}s")
    print(f"   Max: {stats.max:.4f}s")
    print(f"   P50 (Median): {stats.p50:.4f}s")
    print(f"   P95: {stats.p95:.4f}s")
    print(f"   P99: {stats.p99:.4f}s")
    print(f"   IQR: {stats.iqr:.4f}s")
    print(f"   CV: {stats.cv:.4f}" if stats.cv else "   CV: N/A")

    # Export data
    print("\n5. Exporting data...")
    export_path = Path(".specify/exports")
    csv_path = processor.export_to_csv(df_all, "metrics_export.csv")
    print(f"   CSV exported to: {csv_path}")

    json_path = processor.export_to_json(df_all, "metrics_export.json")
    print(f"   JSON exported to: {json_path}")

    try:
        excel_path = processor.export_to_excel(
            {
                "All Metrics": df_all,
                "Aggregated": agg_df,
                "Resampled": resampled,
            },
            "metrics_export.xlsx",
        )
        print(f"   Excel exported to: {excel_path}")
    except ImportError:
        print("   Excel export skipped (openpyxl not installed)")


def demonstrate_time_series_analysis():
    """Demonstrate time series analysis."""
    print("\n" + "=" * 80)
    print("TIME SERIES ANALYSIS")
    print("=" * 80)

    processor = MetricsDataProcessor()

    # Analyze increasing trend operation
    print("\n1. Analyzing 'increasing_trend' operation...")
    df_trend = processor.metrics_to_dataframe(operation="increasing_trend")

    if not df_trend.empty:
        analyzer = TimeSeriesAnalyzer(df_trend)

        # Detect trends
        trend = analyzer.detect_trends()
        print(f"   Trend Type: {trend.trend_type.upper()}")
        print(f"   Slope: {trend.slope:.6f}")
        print(f"   R²: {trend.r_squared:.4f}")
        print(f"   Volatility: {trend.volatility:.4f}")
        if trend.p_value:
            print(f"   P-value: {trend.p_value:.6f}")
        if trend.prediction_next:
            print(f"   Next Prediction: {trend.prediction_next:.4f}s")

        # Calculate moving averages
        ma = analyzer.calculate_moving_average(window=5)
        print(f"\n   Moving Average (window=5): {len(ma)} points")
        print(f"   Last 5 values: {ma.tail().values}")

        ema = analyzer.calculate_exponential_moving_average(span=5)
        print(f"\n   EMA (span=5): {len(ema)} points")
        print(f"   Last 5 values: {ema.tail().values}")

        # Detect peaks (if scipy available)
        try:
            peaks = analyzer.detect_peaks(prominence=0.01)
            print(f"\n   Peaks detected: {peaks['peak_count']}")
            if peaks["peak_count"] > 0:
                print(f"   Peak values: {peaks['peak_values'][:5]}")  # First 5
        except ImportError:
            print("\n   Peak detection skipped (scipy not installed)")


def demonstrate_outlier_detection():
    """Demonstrate outlier detection."""
    print("\n" + "=" * 80)
    print("OUTLIER DETECTION")
    print("=" * 80)

    processor = MetricsDataProcessor()
    detector = OutlierDetector(threshold=3.0)

    # Analyze operation with outliers
    print("\n1. Analyzing 'operation_with_outliers'...")
    df_outliers = processor.metrics_to_dataframe(operation="operation_with_outliers")

    if not df_outliers.empty:
        # Z-score method
        print("\n   Z-Score Method:")
        zscore_report = detector.detect_zscore(df_outliers["duration_seconds"])
        print(f"   Outliers found: {zscore_report.outlier_count} ({zscore_report.outlier_percentage:.2f}%)")
        print(f"   Threshold: [{zscore_report.threshold_lower:.4f}, {zscore_report.threshold_upper:.4f}]")
        if zscore_report.outlier_count > 0:
            print(f"   Sample outlier values: {zscore_report.outlier_values[:3]}")

        # IQR method
        print("\n   IQR Method:")
        iqr_report = detector.detect_iqr(df_outliers["duration_seconds"])
        print(f"   Outliers found: {iqr_report.outlier_count} ({iqr_report.outlier_percentage:.2f}%)")
        print(f"   Threshold: [{iqr_report.threshold_lower:.4f}, {iqr_report.threshold_upper:.4f}]")

        # Isolation Forest (if sklearn available)
        try:
            print("\n   Isolation Forest Method:")
            iso_report = detector.detect_isolation_forest(df_outliers[["duration_seconds"]])
            print(f"   Outliers found: {iso_report.outlier_count} ({iso_report.outlier_percentage:.2f}%)")
        except ImportError:
            print("\n   Isolation Forest skipped (scikit-learn not installed)")


def demonstrate_correlation_analysis():
    """Demonstrate correlation analysis."""
    print("\n" + "=" * 80)
    print("CORRELATION ANALYSIS")
    print("=" * 80)

    processor = MetricsDataProcessor()

    # Get all metrics
    df_all = processor.metrics_to_dataframe()

    if not df_all.empty and len(df_all.select_dtypes(include=["number"]).columns) > 1:
        analyzer = CorrelationAnalyzer(df_all)

        # Pearson correlation
        print("\n1. Pearson Correlation Matrix:")
        pearson = analyzer.pearson_correlation()
        print(pearson)

        # Spearman correlation
        print("\n2. Spearman Correlation Matrix:")
        spearman = analyzer.spearman_correlation()
        print(spearman)

        # Find strong correlations
        strong = analyzer.find_strong_correlations(threshold=0.5)
        print(f"\n3. Strong Correlations (|r| >= 0.5): {len(strong)}")
        for corr in strong[:5]:  # Show top 5
            print(f"   {corr['variable1']} <-> {corr['variable2']}: {corr['correlation']:.3f} ({corr['strength']})")


def demonstrate_chart_generation():
    """Demonstrate chart generation."""
    print("\n" + "=" * 80)
    print("CHART GENERATION")
    print("=" * 80)

    try:
        processor = MetricsDataProcessor()
        chart_builder = ChartBuilder()

        # Get data
        df_all = processor.metrics_to_dataframe()

        if not df_all.empty:
            # Line chart
            print("\n1. Generating line chart...")
            line_chart = chart_builder.line_chart(
                df_all.reset_index(),
                x="timestamp",
                y="duration_seconds",
                title="Performance Over Time",
            )
            print(f"   Chart generated: {len(line_chart)} bytes")

            # Histogram
            print("\n2. Generating histogram...")
            histogram = chart_builder.histogram(
                df_all["duration_seconds"],
                title="Duration Distribution",
            )
            print(f"   Chart generated: {len(histogram)} bytes")

            # Bar chart (aggregated by operation)
            print("\n3. Generating bar chart...")
            agg_df = processor.aggregate_by_operation(df_all)
            agg_df = agg_df.reset_index()
            if ("operation" in agg_df.columns and
                ("duration_seconds", "mean") in agg_df.columns):
                bar_chart = chart_builder.bar_chart(
                    agg_df,
                    x="operation",
                    y=("duration_seconds", "mean"),
                    title="Average Duration by Operation",
                )
                print(f"   Chart generated: {len(bar_chart)} bytes")

            print("\n   All charts generated successfully!")
    except ImportError as e:
        print(f"\n   Chart generation skipped: {e}")


def demonstrate_report_generation():
    """Demonstrate comprehensive report generation."""
    print("\n" + "=" * 80)
    print("REPORT GENERATION")
    print("=" * 80)

    try:
        # Generate performance report
        print("\n1. Generating comprehensive performance report...")
        report_path = create_performance_report(operation="fast_operation")
        print(f"   Report saved to: {report_path}")

        # Generate comparison report
        print("\n2. Generating comparison report...")
        comparison_path = create_comparison_report(
            "fast_operation",
            "slow_operation",
        )
        print(f"   Report saved to: {comparison_path}")

        # Custom report
        print("\n3. Generating custom report...")
        processor = MetricsDataProcessor()
        df_all = processor.metrics_to_dataframe()

        report = ReportGenerator(title="Custom Data Processing Report")

        # Add overview
        stats = processor.calculate_statistics(df_all["duration_seconds"])
        report.add_section("Overview", f"""
        <p>This report demonstrates the hyper-advanced data processing capabilities.</p>
        <p><strong>Total Metrics:</strong> {stats.count}</p>
        <p><strong>Time Range:</strong> {df_all.index.min()} to {df_all.index.max()}</p>
        """, "html")

        # Add statistics table
        agg_df = processor.aggregate_by_operation(df_all)
        report.add_section("Performance by Operation", agg_df, "table")

        # Save custom report
        custom_path = report.save_html("custom_report.html")
        print(f"   Report saved to: {custom_path}")

        print("\n   All reports generated successfully!")
        print(f"\n   Open the reports in your browser:")
        print(f"   - {report_path}")
        print(f"   - {comparison_path}")
        print(f"   - {custom_path}")

    except ImportError as e:
        print(f"\n   Report generation skipped: {e}")


def main():
    """Run all demonstrations."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "DATA PROCESSING INTEGRATION DEMO" + " " * 26 + "║")
    print("╚" + "=" * 78 + "╝")

    # Step 1: Simulate operations
    simulate_operations()

    # Step 2: Demonstrate data processing
    demonstrate_data_processing()

    # Step 3: Time series analysis
    demonstrate_time_series_analysis()

    # Step 4: Outlier detection
    demonstrate_outlier_detection()

    # Step 5: Correlation analysis
    demonstrate_correlation_analysis()

    # Step 6: Chart generation
    demonstrate_chart_generation()

    # Step 7: Report generation
    demonstrate_report_generation()

    print("\n" + "=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)
    print("\nCheck the following directories for outputs:")
    print("  - .specify/exports/  (CSV, JSON, Excel)")
    print("  - .specify/reports/  (HTML reports)")


if __name__ == "__main__":
    main()
