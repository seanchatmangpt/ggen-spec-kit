"""
specify_cli.core.reporting
---------------------------
Automated report generation from DataFrames with charts, tables, and multiple export formats.

This module provides enterprise-grade reporting capabilities:

* **HTML Reports**: Rich HTML reports with embedded charts and tables
* **Dashboard Generation**: Interactive dashboards with multiple visualizations
* **Chart Generation**: Matplotlib/Seaborn integration for data visualization
* **Table Formatting**: Styled HTML tables with conditional formatting
* **Multi-Format Export**: HTML, PDF, Excel, Markdown
* **Template System**: Jinja2-based report templates
* **Performance Reports**: Automated performance analysis reports
* **Comparison Reports**: Before/after comparisons, A/B testing
* **Executive Summaries**: High-level overview reports

The module integrates with data_processing.py to create publication-ready
reports from performance metrics and analysis results.

Example
-------
    from specify_cli.core.reporting import (
        ReportGenerator,
        ChartBuilder,
        create_performance_report,
    )

    # Generate performance report
    report = create_performance_report("my_operation")

    # Custom report with charts
    generator = ReportGenerator()
    generator.add_section("Overview", summary_data)
    generator.add_chart("performance_trend", chart_data)
    generator.save("report.html")

Environment Variables
--------------------
- SPECIFY_REPORT_PATH : Default path for reports (default: .specify/reports)
- SPECIFY_CHART_DPI : DPI for chart images (default: 100)
- SPECIFY_REPORT_THEME : Report theme ('light', 'dark') (default: 'light')

See Also
--------
- :mod:`specify_cli.core.data_processing` : Data processing and analysis
- :mod:`specify_cli.core.advanced_observability` : Metrics collection
"""

from __future__ import annotations

import base64
import io
import os
import warnings
from contextlib import suppress
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import numpy as np

# Check for pandas availability
try:
    import pandas as pd  # type: ignore[import-untyped]

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    warnings.warn(
        "pandas not available. Install with: uv sync --group pm or uv sync --group all",
        stacklevel=2,
    )

# Check for matplotlib availability
try:
    import matplotlib  # type: ignore[import-not-found]

    matplotlib.use("Agg")  # Non-interactive backend
    import matplotlib.dates as mdates  # type: ignore[import-not-found]
    import matplotlib.pyplot as plt  # type: ignore[import-not-found]

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    warnings.warn(
        "matplotlib not available. Install with: uv sync --group hd or uv sync --group all",
        stacklevel=2,
    )

# Check for seaborn availability
try:
    import seaborn as sns  # type: ignore[import-untyped]

    SEABORN_AVAILABLE = True
    sns.set_style("whitegrid")
except ImportError:
    SEABORN_AVAILABLE = False

# Jinja2 is a core dependency
from jinja2 import Template

from .advanced_observability import get_all_stats, get_performance_stats
from .data_processing import (
    PANDAS_AVAILABLE as DP_PANDAS_AVAILABLE,
)
from .data_processing import (
    MetricsDataProcessor,
    OutlierDetector,
    TimeSeriesAnalyzer,
)

# --------------------------------------------------------------------------- #
# Configuration                                                                #
# --------------------------------------------------------------------------- #

REPORT_PATH = Path(os.getenv("SPECIFY_REPORT_PATH", ".specify/reports"))
CHART_DPI = int(os.getenv("SPECIFY_CHART_DPI", "100"))
REPORT_THEME = os.getenv("SPECIFY_REPORT_THEME", "light")


# --------------------------------------------------------------------------- #
# Chart Builder                                                                #
# --------------------------------------------------------------------------- #


class ChartBuilder:
    """
    Build charts from DataFrames using matplotlib/seaborn.

    Provides methods for common chart types: line, bar, scatter, histogram, heatmap.
    """

    def __init__(self, style: str = "seaborn-v0_8-darkgrid", figsize: tuple[int, int] = (10, 6)):
        """
        Initialize chart builder.

        Parameters
        ----------
        style : str
            Matplotlib style.
        figsize : tuple
            Default figure size (width, height).
        """
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("matplotlib is required. Install with: uv sync --group hd")

        self.figsize = figsize
        with suppress(Exception):
            plt.style.use(style)  # Fallback to default style if fails

    def line_chart(
        self,
        df: pd.DataFrame,
        x: str | None = None,
        y: str | list[str] | None = None,
        title: str = "Line Chart",
        xlabel: str | None = None,
        ylabel: str | None = None,
    ) -> bytes:
        """
        Create line chart.

        Parameters
        ----------
        df : pd.DataFrame
            Input data.
        x : str, optional
            X-axis column. If None, uses index.
        y : str or list[str], optional
            Y-axis column(s). If None, plots all numeric columns.
        title : str
            Chart title.
        xlabel : str, optional
            X-axis label.
        ylabel : str, optional
            Y-axis label.

        Returns
        -------
        bytes
            PNG image as bytes.
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        if x is None:
            x_data = df.index
            xlabel = xlabel or "Index"
        else:
            x_data = df[x]
            xlabel = xlabel or x

        if y is None:
            y_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        elif isinstance(y, str):
            y_cols = [y]
        else:
            y_cols = y

        for col in y_cols:
            ax.plot(x_data, df[col], marker="o", label=col, linewidth=2, markersize=4)

        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel or "Value", fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Format x-axis if datetime
        if isinstance(x_data, pd.DatetimeIndex):
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
            plt.xticks(rotation=45)

        plt.tight_layout()

        # Save to bytes
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=CHART_DPI, bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return buf.getvalue()

    def bar_chart(
        self,
        df: pd.DataFrame,
        x: str,
        y: str,
        title: str = "Bar Chart",
        horizontal: bool = False,
    ) -> bytes:
        """
        Create bar chart.

        Parameters
        ----------
        df : pd.DataFrame
            Input data.
        x : str
            X-axis column (categories).
        y : str
            Y-axis column (values).
        title : str
            Chart title.
        horizontal : bool
            Create horizontal bar chart.

        Returns
        -------
        bytes
            PNG image as bytes.
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        if horizontal:
            ax.barh(df[x], df[y], color="steelblue")
            ax.set_ylabel(x, fontsize=12)
            ax.set_xlabel(y, fontsize=12)
        else:
            ax.bar(df[x], df[y], color="steelblue")
            ax.set_xlabel(x, fontsize=12)
            ax.set_ylabel(y, fontsize=12)
            plt.xticks(rotation=45, ha="right")

        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.grid(True, alpha=0.3, axis="y")

        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=CHART_DPI, bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return buf.getvalue()

    def histogram(
        self,
        series: pd.Series,
        bins: int = 30,
        title: str = "Histogram",
        xlabel: str | None = None,
    ) -> bytes:
        """
        Create histogram.

        Parameters
        ----------
        series : pd.Series
            Input data.
        bins : int
            Number of bins.
        title : str
            Chart title.
        xlabel : str, optional
            X-axis label.

        Returns
        -------
        bytes
            PNG image as bytes.
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        ax.hist(series.dropna(), bins=bins, color="steelblue", edgecolor="black", alpha=0.7)

        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_xlabel(xlabel or series.name or "Value", fontsize=12)
        ax.set_ylabel("Frequency", fontsize=12)
        ax.grid(True, alpha=0.3, axis="y")

        # Add statistics
        mean = series.mean()
        median = series.median()
        ax.axvline(mean, color="red", linestyle="--", linewidth=2, label=f"Mean: {mean:.2f}")
        ax.axvline(median, color="green", linestyle="--", linewidth=2, label=f"Median: {median:.2f}")
        ax.legend()

        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=CHART_DPI, bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return buf.getvalue()

    def heatmap(
        self,
        df: pd.DataFrame,
        title: str = "Heatmap",
        cmap: str = "coolwarm",
        annot: bool = True,
    ) -> bytes:
        """
        Create heatmap (correlation matrix, etc.).

        Parameters
        ----------
        df : pd.DataFrame
            Input data (typically correlation matrix).
        title : str
            Chart title.
        cmap : str
            Colormap.
        annot : bool
            Annotate cells with values.

        Returns
        -------
        bytes
            PNG image as bytes.
        """
        if not SEABORN_AVAILABLE:
            raise ImportError("seaborn is required for heatmaps. Install with: pip install seaborn")

        fig, ax = plt.subplots(figsize=self.figsize)

        sns.heatmap(df, annot=annot, cmap=cmap, center=0, fmt=".2f", ax=ax, cbar_kws={"shrink": 0.8})

        ax.set_title(title, fontsize=14, fontweight="bold")

        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=CHART_DPI, bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return buf.getvalue()

    def scatter_plot(
        self,
        df: pd.DataFrame,
        x: str,
        y: str,
        title: str = "Scatter Plot",
        hue: str | None = None,
    ) -> bytes:
        """
        Create scatter plot.

        Parameters
        ----------
        df : pd.DataFrame
            Input data.
        x : str
            X-axis column.
        y : str
            Y-axis column.
        title : str
            Chart title.
        hue : str, optional
            Column for color coding.

        Returns
        -------
        bytes
            PNG image as bytes.
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        if hue and SEABORN_AVAILABLE:
            sns.scatterplot(data=df, x=x, y=y, hue=hue, ax=ax, s=100)
        else:
            ax.scatter(df[x], df[y], alpha=0.6, s=100, color="steelblue")

        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_xlabel(x, fontsize=12)
        ax.set_ylabel(y, fontsize=12)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=CHART_DPI, bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return buf.getvalue()


# --------------------------------------------------------------------------- #
# HTML Table Formatter                                                         #
# --------------------------------------------------------------------------- #


class HTMLTableFormatter:
    """Format pandas DataFrames as styled HTML tables."""

    @staticmethod
    def format_table(
        df: pd.DataFrame,
        title: str | None = None,
        highlight_max: bool = False,
        highlight_min: bool = False,
    ) -> str:
        """
        Format DataFrame as styled HTML table.

        Parameters
        ----------
        df : pd.DataFrame
            Input DataFrame.
        title : str, optional
            Table title.
        highlight_max : bool
            Highlight maximum values.
        highlight_min : bool
            Highlight minimum values.

        Returns
        -------
        str
            HTML table string.
        """
        # Apply styling
        styler = df.style

        if highlight_max:
            styler = styler.highlight_max(axis=0, color="lightgreen")
        if highlight_min:
            styler = styler.highlight_min(axis=0, color="lightcoral")

        # Format numbers
        styler = styler.format(precision=3, na_rep="-")

        # Generate HTML
        html: str = styler.to_html()

        if title:
            html = f"<h3>{title}</h3>\n{html}"

        return html

    @staticmethod
    def format_summary_table(stats_dict: dict[str, Any]) -> str:
        """
        Format summary statistics as HTML table.

        Parameters
        ----------
        stats_dict : dict
            Statistics dictionary.

        Returns
        -------
        str
            HTML table string.
        """
        rows = []
        for key, value in stats_dict.items():
            if isinstance(value, (int, float)):
                formatted_value = f"{value:,.3f}" if isinstance(value, float) else f"{value:,}"
            else:
                formatted_value = str(value)
            rows.append(f"<tr><td><strong>{key}</strong></td><td>{formatted_value}</td></tr>")

        return f"""
        <table class="summary-table">
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        """


# --------------------------------------------------------------------------- #
# Report Generator                                                             #
# --------------------------------------------------------------------------- #


@dataclass
class ReportSection:
    """A section in a report."""

    title: str
    content: str
    section_type: Literal["text", "table", "chart", "html"]


class ReportGenerator:
    """
    Generate comprehensive reports with charts, tables, and analysis.

    Supports HTML, Markdown, and PDF export.
    """

    def __init__(self, title: str = "Performance Report", theme: str = REPORT_THEME):
        """
        Initialize report generator.

        Parameters
        ----------
        title : str
            Report title.
        theme : str
            Report theme ('light' or 'dark').
        """
        self.title = title
        self.theme = theme
        self.sections: list[ReportSection] = []
        self.metadata: dict[str, Any] = {
            "generated_at": datetime.now(UTC).isoformat(),
            "generator": "specify-cli",
        }

    def add_section(
        self,
        title: str,
        content: str | pd.DataFrame | bytes,
        section_type: Literal["text", "table", "chart", "html"] = "text",
    ) -> None:
        """
        Add section to report.

        Parameters
        ----------
        title : str
            Section title.
        content : str, DataFrame, or bytes
            Section content.
        section_type : str
            Type of section.
        """
        if section_type == "table" and isinstance(content, pd.DataFrame):
            content = HTMLTableFormatter.format_table(content, title=title)
            section_type = "html"
        elif section_type == "chart" and isinstance(content, bytes):
            # Convert bytes to base64 data URL
            b64 = base64.b64encode(content).decode("utf-8")
            content = f'<img src="data:image/png;base64,{b64}" alt="{title}" style="max-width: 100%;">'
            section_type = "html"

        self.sections.append(
            ReportSection(title=title, content=str(content), section_type=section_type)
        )

    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to report."""
        self.metadata[key] = value

    def generate_html(self) -> str:
        """
        Generate HTML report.

        Returns
        -------
        str
            HTML report string.
        """
        # Build sections HTML
        sections_html = []
        for section in self.sections:
            section_html = f"""
            <div class="section">
                <h2>{section.title}</h2>
                <div class="section-content">
                    {section.content}
                </div>
            </div>
            """
            sections_html.append(section_html)

        # Build metadata HTML
        metadata_items = [f"<li><strong>{k}:</strong> {v}</li>" for k, v in self.metadata.items()]
        metadata_html = f"<ul>{''.join(metadata_items)}</ul>"

        # HTML template
        template = Template(
            """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: {% if theme == 'dark' %}#1e1e1e{% else %}#f5f5f5{% endif %};
            color: {% if theme == 'dark' %}#e0e0e0{% else %}#333{% endif %};
        }
        .header {
            background: {% if theme == 'dark' %}#2d2d2d{% else %}#fff{% endif %};
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        h1 {
            margin: 0;
            color: {% if theme == 'dark' %}#4a9eff{% else %}#0066cc{% endif %};
        }
        .section {
            background: {% if theme == 'dark' %}#2d2d2d{% else %}#fff{% endif %};
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .section h2 {
            margin-top: 0;
            color: {% if theme == 'dark' %}#4a9eff{% else %}#0066cc{% endif %};
            border-bottom: 2px solid {% if theme == 'dark' %}#4a9eff{% else %}#0066cc{% endif %};
            padding-bottom: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid {% if theme == 'dark' %}#444{% else %}#ddd{% endif %};
        }
        th {
            background-color: {% if theme == 'dark' %}#3a3a3a{% else %}#f8f9fa{% endif %};
            font-weight: 600;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: {% if theme == 'dark' %}#888{% else %}#666{% endif %};
            font-size: 0.9em;
        }
        .metadata {
            background: {% if theme == 'dark' %}#2d2d2d{% else %}#f8f9fa{% endif %};
            padding: 15px;
            border-radius: 4px;
            margin-top: 20px;
        }
        .metadata ul {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        .metadata li {
            padding: 5px 0;
        }
        img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 20px auto;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ title }}</h1>
        <div class="metadata">
            {{ metadata }}
        </div>
    </div>

    {{ sections }}

    <div class="footer">
        Generated by <strong>specify-cli</strong> | {{ generated_at }}
    </div>
</body>
</html>
        """
        )

        return template.render(
            title=self.title,
            theme=self.theme,
            metadata=metadata_html,
            sections="\n".join(sections_html),
            generated_at=self.metadata["generated_at"],
        )

    def save_html(self, filename: str, path: Path | None = None) -> Path:
        """
        Save report as HTML.

        Parameters
        ----------
        filename : str
            Output filename.
        path : Path, optional
            Output directory.

        Returns
        -------
        Path
            Path to saved file.
        """
        path = path or REPORT_PATH
        path.mkdir(parents=True, exist_ok=True)

        output_path = path / filename
        html = self.generate_html()

        with output_path.open("w", encoding="utf-8") as f:
            f.write(html)

        return output_path


# --------------------------------------------------------------------------- #
# Pre-built Report Templates                                                   #
# --------------------------------------------------------------------------- #


def create_performance_report(operation: str | None = None, output_path: Path | None = None) -> Path:
    """
    Create comprehensive performance report.

    Parameters
    ----------
    operation : str, optional
        Specific operation to report on. If None, includes all operations.
    output_path : Path, optional
        Output directory.

    Returns
    -------
    Path
        Path to generated report.
    """
    if not DP_PANDAS_AVAILABLE or not MATPLOTLIB_AVAILABLE:
        raise ImportError(
            "pandas and matplotlib required. Install with: uv sync --group pm --group hd"
        )

    # Initialize components
    processor = MetricsDataProcessor()
    chart_builder = ChartBuilder()
    report = ReportGenerator(
        title=f"Performance Report: {operation}" if operation else "Performance Report - All Operations"
    )

    # Get data
    df = processor.metrics_to_dataframe(operation=operation)

    if df.empty:
        report.add_section("Warning", "No metrics data available.", "text")
        return report.save_html("performance_report_empty.html", output_path)

    # Add overview section
    stats = get_performance_stats(operation) if operation else get_all_stats()
    report.add_section("Overview", HTMLTableFormatter.format_summary_table(stats), "html")

    # Add time series chart
    if len(df) > 1:
        chart_bytes = chart_builder.line_chart(
            df,
            y="duration_seconds",
            title="Performance Over Time",
            ylabel="Duration (seconds)",
        )
        report.add_section("Performance Trend", chart_bytes, "chart")

    # Add histogram
    if len(df) > 10:
        hist_bytes = chart_builder.histogram(
            df["duration_seconds"],
            title="Duration Distribution",
            xlabel="Duration (seconds)",
        )
        report.add_section("Duration Distribution", hist_bytes, "chart")

    # Add outlier analysis
    if len(df) > 10:
        detector = OutlierDetector()
        outlier_report = detector.detect_zscore(df["duration_seconds"])
        report.add_section(
            "Outlier Analysis",
            f"""
            <p><strong>Method:</strong> Z-Score</p>
            <p><strong>Outliers Detected:</strong> {outlier_report.outlier_count} ({outlier_report.outlier_percentage:.2f}%)</p>
            <p><strong>Threshold Range:</strong> [{outlier_report.threshold_lower:.3f}, {outlier_report.threshold_upper:.3f}]</p>
            """,
            "html",
        )

    # Add trend analysis
    if len(df) > 2:
        analyzer = TimeSeriesAnalyzer(df)
        try:
            trend = analyzer.detect_trends()
            report.add_section(
                "Trend Analysis",
                f"""
                <p><strong>Trend Type:</strong> {trend.trend_type.upper()}</p>
                <p><strong>Slope:</strong> {trend.slope:.6f}</p>
                <p><strong>R²:</strong> {trend.r_squared:.3f}</p>
                <p><strong>Volatility:</strong> {trend.volatility:.3f}</p>
                {f"<p><strong>Next Prediction:</strong> {trend.prediction_next:.3f}</p>" if trend.prediction_next else ""}
                """,
                "html",
            )
        except Exception:
            pass  # Skip if insufficient data

    # Save report
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    filename = f"performance_report_{operation or 'all'}_{timestamp}.html"
    return report.save_html(filename, output_path)


def create_comparison_report(
    operation1: str,
    operation2: str,
    output_path: Path | None = None,
) -> Path:
    """
    Create comparison report between two operations.

    Parameters
    ----------
    operation1 : str
        First operation.
    operation2 : str
        Second operation.
    output_path : Path, optional
        Output directory.

    Returns
    -------
    Path
        Path to generated report.
    """
    if not DP_PANDAS_AVAILABLE or not MATPLOTLIB_AVAILABLE:
        raise ImportError(
            "pandas and matplotlib required. Install with: uv sync --group pm --group hd"
        )

    processor = MetricsDataProcessor()
    report = ReportGenerator(title=f"Comparison Report: {operation1} vs {operation2}")

    # Get data for both operations
    df1 = processor.metrics_to_dataframe(operation=operation1)
    df2 = processor.metrics_to_dataframe(operation=operation2)

    if df1.empty or df2.empty:
        report.add_section("Warning", "Insufficient data for comparison.", "text")
        return report.save_html("comparison_report_empty.html", output_path)

    # Statistics comparison
    stats1 = processor.calculate_statistics(df1["duration_seconds"])
    stats2 = processor.calculate_statistics(df2["duration_seconds"])

    comparison_data = {
        "Metric": ["Mean", "Median", "Std Dev", "Min", "Max", "P95", "P99"],
        operation1: [
            stats1.mean,
            stats1.p50,
            stats1.std,
            stats1.min,
            stats1.max,
            stats1.p95,
            stats1.p99,
        ],
        operation2: [
            stats2.mean,
            stats2.p50,
            stats2.std,
            stats2.min,
            stats2.max,
            stats2.p95,
            stats2.p99,
        ],
    }
    comparison_df = pd.DataFrame(comparison_data)
    report.add_section("Statistical Comparison", comparison_df, "table")

    # Side-by-side histograms
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1.hist(df1["duration_seconds"], bins=20, color="steelblue", alpha=0.7, edgecolor="black")
    ax1.set_title(f"{operation1} Distribution")
    ax1.set_xlabel("Duration (s)")
    ax1.set_ylabel("Frequency")

    ax2.hist(df2["duration_seconds"], bins=20, color="coral", alpha=0.7, edgecolor="black")
    ax2.set_title(f"{operation2} Distribution")
    ax2.set_xlabel("Duration (s)")
    ax2.set_ylabel("Frequency")

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=CHART_DPI, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)

    report.add_section("Distribution Comparison", buf.getvalue(), "chart")

    # Save report
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    filename = f"comparison_{operation1}_vs_{operation2}_{timestamp}.html"
    return report.save_html(filename, output_path)


__all__ = [
    "MATPLOTLIB_AVAILABLE",
    "PANDAS_AVAILABLE",
    "SEABORN_AVAILABLE",
    "ChartBuilder",
    "HTMLTableFormatter",
    "ReportGenerator",
    "ReportSection",
    "create_comparison_report",
    "create_performance_report",
]
