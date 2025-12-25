"""
Tests for reporting module.

Run with:
    uv sync --group pm --group hd --group dev
    uv run pytest tests/unit/test_reporting.py -v
"""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pytest

# Import components to test
from specify_cli.core.advanced_observability import PerformanceTracker, _GLOBAL_STORE
from specify_cli.core.reporting import (
    MATPLOTLIB_AVAILABLE,
    PANDAS_AVAILABLE,
    ChartBuilder,
    HTMLTableFormatter,
    ReportGenerator,
    create_comparison_report,
    create_performance_report,
)

# Skip all tests if required dependencies not available
pytestmark = pytest.mark.skipif(
    not PANDAS_AVAILABLE or not MATPLOTLIB_AVAILABLE,
    reason="pandas or matplotlib not installed",
)

if PANDAS_AVAILABLE:
    import pandas as pd


@pytest.fixture
def sample_dataframe():
    """Create sample DataFrame for testing."""
    dates = pd.date_range("2024-01-01", periods=100, freq="1h")
    return pd.DataFrame(
        {
            "duration_seconds": np.random.normal(0.05, 0.01, 100),
            "memory_mb": np.random.uniform(50, 150, 100),
            "cpu_percent": np.random.uniform(10, 90, 100),
            "operation": ["test_op"] * 100,
        },
        index=dates,
    )


@pytest.fixture
def sample_metrics():
    """Create sample metrics for testing."""
    # Clear existing metrics
    _GLOBAL_STORE._metrics.clear()

    # Generate sample metrics
    for i in range(50):
        with PerformanceTracker("fast_operation"):
            time.sleep(0.001)

    for i in range(50):
        with PerformanceTracker("slow_operation"):
            time.sleep(0.002)

    yield

    # Cleanup
    _GLOBAL_STORE._metrics.clear()


class TestChartBuilder:
    """Test ChartBuilder class."""

    def test_initialization(self):
        """Test chart builder initialization."""
        builder = ChartBuilder(figsize=(12, 8))
        assert builder.figsize == (12, 8)

    def test_line_chart(self, sample_dataframe):
        """Test line chart generation."""
        builder = ChartBuilder()
        chart_bytes = builder.line_chart(
            sample_dataframe.reset_index(),
            x="timestamp",
            y="duration_seconds",
            title="Test Line Chart",
        )

        assert isinstance(chart_bytes, bytes)
        assert len(chart_bytes) > 0
        # PNG signature
        assert chart_bytes[:8] == b"\x89PNG\r\n\x1a\n"

    def test_line_chart_multiple_y(self, sample_dataframe):
        """Test line chart with multiple Y columns."""
        builder = ChartBuilder()
        chart_bytes = builder.line_chart(
            sample_dataframe,
            y=["duration_seconds", "memory_mb"],
            title="Multi-line Chart",
        )

        assert isinstance(chart_bytes, bytes)
        assert len(chart_bytes) > 0

    def test_bar_chart(self, sample_dataframe):
        """Test bar chart generation."""
        builder = ChartBuilder()

        # Aggregate data for bar chart
        agg_df = sample_dataframe.groupby("operation").agg({"duration_seconds": "mean"}).reset_index()

        chart_bytes = builder.bar_chart(
            agg_df,
            x="operation",
            y="duration_seconds",
            title="Test Bar Chart",
        )

        assert isinstance(chart_bytes, bytes)
        assert len(chart_bytes) > 0

    def test_bar_chart_horizontal(self, sample_dataframe):
        """Test horizontal bar chart."""
        builder = ChartBuilder()
        agg_df = sample_dataframe.groupby("operation").agg({"duration_seconds": "mean"}).reset_index()

        chart_bytes = builder.bar_chart(
            agg_df,
            x="operation",
            y="duration_seconds",
            horizontal=True,
        )

        assert isinstance(chart_bytes, bytes)
        assert len(chart_bytes) > 0

    def test_histogram(self, sample_dataframe):
        """Test histogram generation."""
        builder = ChartBuilder()
        chart_bytes = builder.histogram(
            sample_dataframe["duration_seconds"],
            bins=20,
            title="Test Histogram",
        )

        assert isinstance(chart_bytes, bytes)
        assert len(chart_bytes) > 0

    def test_scatter_plot(self, sample_dataframe):
        """Test scatter plot generation."""
        builder = ChartBuilder()
        chart_bytes = builder.scatter_plot(
            sample_dataframe,
            x="memory_mb",
            y="duration_seconds",
            title="Test Scatter Plot",
        )

        assert isinstance(chart_bytes, bytes)
        assert len(chart_bytes) > 0

    @pytest.mark.skipif(
        not PANDAS_AVAILABLE or not MATPLOTLIB_AVAILABLE,
        reason="seaborn not installed"
    )
    def test_heatmap(self):
        """Test heatmap generation."""
        try:
            import seaborn as sns  # noqa: F401

            builder = ChartBuilder()

            # Create correlation matrix
            df = pd.DataFrame(
                {
                    "a": [1, 2, 3, 4, 5],
                    "b": [2, 4, 6, 8, 10],
                    "c": [1, 3, 5, 7, 9],
                }
            )
            corr_matrix = df.corr()

            chart_bytes = builder.heatmap(corr_matrix, title="Test Heatmap")

            assert isinstance(chart_bytes, bytes)
            assert len(chart_bytes) > 0
        except ImportError:
            pytest.skip("seaborn not available")


class TestHTMLTableFormatter:
    """Test HTMLTableFormatter class."""

    def test_format_table(self, sample_dataframe):
        """Test basic table formatting."""
        html = HTMLTableFormatter.format_table(sample_dataframe.head(10), title="Test Table")

        assert isinstance(html, str)
        assert "<table" in html
        assert "<h3>Test Table</h3>" in html
        assert "duration_seconds" in html

    def test_format_table_with_highlighting(self, sample_dataframe):
        """Test table with highlighting."""
        html = HTMLTableFormatter.format_table(
            sample_dataframe.head(10),
            highlight_max=True,
            highlight_min=True,
        )

        assert isinstance(html, str)
        assert "lightgreen" in html or "lightcoral" in html

    def test_format_summary_table(self):
        """Test summary table formatting."""
        stats = {
            "count": 100,
            "mean": 0.05123,
            "std": 0.01234,
            "min": 0.01,
            "max": 0.09,
        }

        html = HTMLTableFormatter.format_summary_table(stats)

        assert isinstance(html, str)
        assert "<table" in html
        assert "count" in html
        assert "100" in html
        assert "0.051" in html  # Formatted float


class TestReportGenerator:
    """Test ReportGenerator class."""

    def test_initialization(self):
        """Test report generator initialization."""
        report = ReportGenerator(title="Test Report", theme="dark")
        assert report.title == "Test Report"
        assert report.theme == "dark"
        assert len(report.sections) == 0

    def test_add_text_section(self):
        """Test adding text section."""
        report = ReportGenerator()
        report.add_section("Overview", "This is a test section.", "text")

        assert len(report.sections) == 1
        assert report.sections[0].title == "Overview"
        assert report.sections[0].content == "This is a test section."

    def test_add_table_section(self, sample_dataframe):
        """Test adding table section."""
        report = ReportGenerator()
        report.add_section("Data Table", sample_dataframe.head(10), "table")

        assert len(report.sections) == 1
        assert "<table" in report.sections[0].content

    def test_add_chart_section(self, sample_dataframe):
        """Test adding chart section."""
        builder = ChartBuilder()
        chart_bytes = builder.line_chart(sample_dataframe, y="duration_seconds")

        report = ReportGenerator()
        report.add_section("Performance Chart", chart_bytes, "chart")

        assert len(report.sections) == 1
        assert "data:image/png;base64," in report.sections[0].content

    def test_add_metadata(self):
        """Test adding metadata."""
        report = ReportGenerator()
        report.add_metadata("author", "Test User")
        report.add_metadata("version", "1.0.0")

        assert report.metadata["author"] == "Test User"
        assert report.metadata["version"] == "1.0.0"

    def test_generate_html(self):
        """Test HTML generation."""
        report = ReportGenerator(title="Test Report")
        report.add_section("Section 1", "Content 1", "text")
        report.add_section("Section 2", "Content 2", "html")

        html = report.generate_html()

        assert isinstance(html, str)
        assert "<!DOCTYPE html>" in html
        assert "Test Report" in html
        assert "Section 1" in html
        assert "Content 1" in html
        assert "Section 2" in html
        assert "Content 2" in html

    def test_generate_html_dark_theme(self):
        """Test HTML generation with dark theme."""
        report = ReportGenerator(title="Dark Report", theme="dark")
        report.add_section("Test", "Content", "text")

        html = report.generate_html()

        assert "#1e1e1e" in html  # Dark background color
        assert "#e0e0e0" in html  # Light text color

    def test_save_html(self, tmp_path):
        """Test saving HTML report."""
        report = ReportGenerator(title="Test Report")
        report.add_section("Test Section", "Test Content", "text")

        output_path = report.save_html("test_report.html", path=tmp_path)

        assert output_path.exists()
        assert output_path.suffix == ".html"

        # Verify content
        content = output_path.read_text()
        assert "Test Report" in content
        assert "Test Section" in content


class TestPrebuiltReports:
    """Test pre-built report templates."""

    def test_create_performance_report(self, sample_metrics, tmp_path):
        """Test performance report creation."""
        report_path = create_performance_report(
            operation="fast_operation",
            output_path=tmp_path,
        )

        assert report_path.exists()
        assert report_path.suffix == ".html"

        # Verify content
        content = report_path.read_text()
        assert "Performance Report" in content
        assert "fast_operation" in content

    def test_create_performance_report_all_operations(self, sample_metrics, tmp_path):
        """Test performance report for all operations."""
        report_path = create_performance_report(output_path=tmp_path)

        assert report_path.exists()
        content = report_path.read_text()
        assert "Performance Report" in content

    def test_create_comparison_report(self, sample_metrics, tmp_path):
        """Test comparison report creation."""
        report_path = create_comparison_report(
            "fast_operation",
            "slow_operation",
            output_path=tmp_path,
        )

        assert report_path.exists()
        assert report_path.suffix == ".html"

        # Verify content
        content = report_path.read_text()
        assert "Comparison Report" in content
        assert "fast_operation" in content
        assert "slow_operation" in content


class TestIntegration:
    """Integration tests."""

    def test_complete_report_workflow(self, sample_metrics, tmp_path):
        """Test complete reporting workflow."""
        from specify_cli.core.data_processing import MetricsDataProcessor

        # Process data
        processor = MetricsDataProcessor()
        df = processor.metrics_to_dataframe()

        # Create custom report
        report = ReportGenerator(title="Integration Test Report")

        # Add overview
        report.add_section(
            "Overview",
            f"<p>Total metrics: {len(df)}</p>",
            "html",
        )

        # Add table
        agg_df = processor.aggregate_by_operation(df)
        report.add_section("Aggregated Data", agg_df, "table")

        # Add chart
        builder = ChartBuilder()
        chart_bytes = builder.histogram(df["duration_seconds"], title="Duration Distribution")
        report.add_section("Duration Distribution", chart_bytes, "chart")

        # Save report
        output_path = report.save_html("integration_report.html", path=tmp_path)

        assert output_path.exists()

        # Verify all sections are present
        content = output_path.read_text()
        assert "Integration Test Report" in content
        assert "Overview" in content
        assert "Aggregated Data" in content
        assert "Duration Distribution" in content
        assert "data:image/png;base64," in content

    def test_multi_format_export(self, sample_dataframe, tmp_path):
        """Test exporting data and reports in multiple formats."""
        from specify_cli.core.data_processing import MetricsDataProcessor

        processor = MetricsDataProcessor()

        # Export data
        csv_path = processor.export_to_csv(sample_dataframe, "data.csv", path=tmp_path)
        json_path = processor.export_to_json(sample_dataframe, "data.json", path=tmp_path)

        # Create report
        report = ReportGenerator(title="Multi-Format Export Test")
        report.add_section("Data Preview", sample_dataframe.head(10), "table")
        html_path = report.save_html("report.html", path=tmp_path)

        # Verify all exports exist
        assert csv_path.exists()
        assert json_path.exists()
        assert html_path.exists()
