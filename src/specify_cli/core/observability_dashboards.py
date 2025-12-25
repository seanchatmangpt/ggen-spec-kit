"""
specify_cli.core.observability_dashboards
-----------------------------------------
Dashboard generation for observability metrics and performance visualization.

This module provides comprehensive dashboard generation capabilities:

* **CLI Performance Dashboard**: Command execution metrics and trends
* **ggen Transformation Dashboard**: RDF transformation performance
* **Test Suite Dashboard**: Test execution health and coverage
* **Resource Dashboard**: CPU, memory, and I/O usage
* **Anomaly Dashboard**: Performance regression detection

Dashboards can be generated as:
- HTML reports with embedded charts
- PNG/SVG images for documentation
- JSON data for custom visualization

Example
-------
    from specify_cli.core.observability_dashboards import (
        generate_cli_dashboard,
        generate_all_dashboards,
    )

    # Generate CLI performance dashboard
    generate_cli_dashboard("./reports/cli-performance.html")

    # Generate all dashboards
    generate_all_dashboards("./reports")

See Also
--------
- :mod:`specify_cli.core.advanced_observability` : Metrics collection
- :mod:`specify_cli.core.telemetry` : Core telemetry
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import numpy as np

# Check for matplotlib
try:
    import matplotlib

    matplotlib.use("Agg")  # Non-interactive backend
    import matplotlib.pyplot as plt

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# Import advanced observability
try:
    from .advanced_observability import (
        detect_anomalies,
        get_all_stats,
        get_critical_path,
        get_performance_stats,
    )

    ADVANCED_OBS_AVAILABLE = True
except ImportError:
    ADVANCED_OBS_AVAILABLE = False


# --------------------------------------------------------------------------- #
# HTML Template                                                                #
# --------------------------------------------------------------------------- #

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: #f8f9fa;
            border-left: 4px solid #3498db;
            padding: 15px;
            border-radius: 4px;
        }}
        .metric-card.warning {{
            border-left-color: #f39c12;
        }}
        .metric-card.error {{
            border-left-color: #e74c3c;
        }}
        .metric-card.success {{
            border-left-color: #27ae60;
        }}
        .metric-label {{
            font-size: 12px;
            color: #7f8c8d;
            text-transform: uppercase;
            margin-bottom: 5px;
        }}
        .metric-value {{
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
        }}
        .metric-unit {{
            font-size: 14px;
            color: #95a5a6;
            margin-left: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ecf0f1;
        }}
        th {{
            background: #3498db;
            color: white;
            font-weight: 600;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .chart {{
            margin: 30px 0;
            text-align: center;
        }}
        .chart img {{
            max-width: 100%;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .timestamp {{
            color: #95a5a6;
            font-size: 14px;
            text-align: right;
            margin-top: 30px;
        }}
        .anomaly {{
            background: #fff3cd;
            border-left: 4px solid #f39c12;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
        }}
        code {{
            background: #ecf0f1;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: "Monaco", "Courier New", monospace;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        {content}
        <div class="timestamp">
            Generated at {timestamp}
        </div>
    </div>
</body>
</html>
"""


# --------------------------------------------------------------------------- #
# Dashboard Generation                                                         #
# --------------------------------------------------------------------------- #


def generate_cli_dashboard(output_path: str | Path) -> None:
    """Generate CLI performance dashboard.

    Parameters
    ----------
    output_path : str | Path
        Output path for the HTML dashboard.
    """
    if not ADVANCED_OBS_AVAILABLE:
        raise ImportError("Advanced observability not available")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Get all statistics
    all_stats = get_all_stats()

    # Build content
    content_parts = []

    # Summary metrics
    total_operations = len(all_stats)
    total_samples = sum(s["sample_count"] for s in all_stats.values() if "sample_count" in s)

    content_parts.append("<h2>Summary</h2>")
    content_parts.append('<div class="metric-grid">')
    content_parts.append(
        f'<div class="metric-card success">'
        f'<div class="metric-label">Total Operations</div>'
        f'<div class="metric-value">{total_operations}</div>'
        f'</div>'
    )
    content_parts.append(
        f'<div class="metric-card">'
        f'<div class="metric-label">Total Samples</div>'
        f'<div class="metric-value">{total_samples}</div>'
        f'</div>'
    )
    content_parts.append("</div>")

    # Anomalies section
    anomalies = detect_anomalies()
    if anomalies:
        content_parts.append("<h2>Performance Anomalies</h2>")
        for anomaly in anomalies[:10]:  # Show top 10
            content_parts.append(
                f'<div class="anomaly">'
                f'<strong>{anomaly.operation}</strong><br>'
                f'Duration: {anomaly.current_duration:.3f}s '
                f'(baseline: {anomaly.baseline_mean:.3f}s ± {anomaly.baseline_std:.3f}s)<br>'
                f'Deviation: {anomaly.deviation_pct:.1f}% '
                f'(z-score: {anomaly.z_score:.2f})'
                f'</div>'
            )

    # Operations table
    content_parts.append("<h2>Operation Performance</h2>")
    content_parts.append("<table>")
    content_parts.append(
        "<tr>"
        "<th>Operation</th>"
        "<th>Samples</th>"
        "<th>Mean</th>"
        "<th>P50</th>"
        "<th>P95</th>"
        "<th>P99</th>"
        "<th>Success Rate</th>"
        "</tr>"
    )

    for op, stats in sorted(all_stats.items()):
        if "error" in stats:
            continue

        success_rate = stats.get("success_rate", 1.0) * 100
        card_class = "success" if success_rate >= 95 else "warning" if success_rate >= 80 else "error"

        content_parts.append(
            f'<tr>'
            f'<td><code>{op}</code></td>'
            f'<td>{stats["sample_count"]}</td>'
            f'<td>{stats["mean"]:.3f}s</td>'
            f'<td>{stats["p50"]:.3f}s</td>'
            f'<td>{stats["p95"]:.3f}s</td>'
            f'<td>{stats["p99"]:.3f}s</td>'
            f'<td><span class="metric-card {card_class}" style="display:inline-block;padding:2px 8px">'
            f'{success_rate:.1f}%</span></td>'
            f'</tr>'
        )

    content_parts.append("</table>")

    # Generate HTML
    html = HTML_TEMPLATE.format(
        title="CLI Performance Dashboard",
        content="\n".join(content_parts),
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    output_path.write_text(html)


def generate_ggen_dashboard(output_path: str | Path) -> None:
    """Generate ggen transformation dashboard.

    Parameters
    ----------
    output_path : str | Path
        Output path for the HTML dashboard.
    """
    if not ADVANCED_OBS_AVAILABLE:
        raise ImportError("Advanced observability not available")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Get ggen-related statistics
    all_stats = get_all_stats()
    ggen_stats = {k: v for k, v in all_stats.items() if "ggen" in k.lower()}

    content_parts = []

    if not ggen_stats:
        content_parts.append("<p>No ggen transformation metrics available yet.</p>")
    else:
        content_parts.append("<h2>ggen Transformation Performance</h2>")
        content_parts.append("<table>")
        content_parts.append(
            "<tr>"
            "<th>Operation</th>"
            "<th>Mean Duration</th>"
            "<th>P95 Duration</th>"
            "<th>Success Rate</th>"
            "</tr>"
        )

        for op, stats in sorted(ggen_stats.items()):
            if "error" in stats:
                continue

            success_rate = stats.get("success_rate", 1.0) * 100
            content_parts.append(
                f'<tr>'
                f'<td><code>{op}</code></td>'
                f'<td>{stats["mean"]:.3f}s</td>'
                f'<td>{stats["p95"]:.3f}s</td>'
                f'<td>{success_rate:.1f}%</td>'
                f'</tr>'
            )

        content_parts.append("</table>")

    # Generate HTML
    html = HTML_TEMPLATE.format(
        title="ggen Transformation Dashboard",
        content="\n".join(content_parts),
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    output_path.write_text(html)


def generate_test_dashboard(output_path: str | Path) -> None:
    """Generate test suite health dashboard.

    Parameters
    ----------
    output_path : str | Path
        Output path for the HTML dashboard.
    """
    if not ADVANCED_OBS_AVAILABLE:
        raise ImportError("Advanced observability not available")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Get test-related statistics
    all_stats = get_all_stats()
    test_stats = {k: v for k, v in all_stats.items() if "test" in k.lower() or "pytest" in k.lower()}

    content_parts = []

    if not test_stats:
        content_parts.append("<p>No test execution metrics available yet.</p>")
    else:
        content_parts.append("<h2>Test Suite Health</h2>")

        # Summary metrics
        total_tests = sum(s["sample_count"] for s in test_stats.values() if "sample_count" in s)
        avg_success = np.mean([s.get("success_rate", 1.0) for s in test_stats.values() if "success_rate" in s]) * 100

        content_parts.append('<div class="metric-grid">')
        content_parts.append(
            f'<div class="metric-card">'
            f'<div class="metric-label">Test Executions</div>'
            f'<div class="metric-value">{total_tests}</div>'
            f'</div>'
        )
        content_parts.append(
            f'<div class="metric-card success">'
            f'<div class="metric-label">Average Success Rate</div>'
            f'<div class="metric-value">{avg_success:.1f}<span class="metric-unit">%</span></div>'
            f'</div>'
        )
        content_parts.append("</div>")

        # Test performance table
        content_parts.append("<table>")
        content_parts.append(
            "<tr>"
            "<th>Test Suite</th>"
            "<th>Runs</th>"
            "<th>Mean Duration</th>"
            "<th>P95 Duration</th>"
            "<th>Success Rate</th>"
            "</tr>"
        )

        for op, stats in sorted(test_stats.items()):
            if "error" in stats:
                continue

            success_rate = stats.get("success_rate", 1.0) * 100
            content_parts.append(
                f'<tr>'
                f'<td><code>{op}</code></td>'
                f'<td>{stats["sample_count"]}</td>'
                f'<td>{stats["mean"]:.2f}s</td>'
                f'<td>{stats["p95"]:.2f}s</td>'
                f'<td>{success_rate:.1f}%</td>'
                f'</tr>'
            )

        content_parts.append("</table>")

    # Generate HTML
    html = HTML_TEMPLATE.format(
        title="Test Suite Health Dashboard",
        content="\n".join(content_parts),
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    output_path.write_text(html)


def generate_resource_dashboard(output_path: str | Path) -> None:
    """Generate resource usage dashboard.

    Parameters
    ----------
    output_path : str | Path
        Output path for the HTML dashboard.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    content_parts = []
    content_parts.append("<h2>Resource Usage</h2>")
    content_parts.append(
        "<p>Resource tracking requires <code>psutil</code> package and "
        "<code>track_resources=True</code> in PerformanceTracker.</p>"
    )

    # Generate HTML
    html = HTML_TEMPLATE.format(
        title="Resource Usage Dashboard",
        content="\n".join(content_parts),
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    output_path.write_text(html)


def generate_all_dashboards(output_dir: str | Path) -> dict[str, Path]:
    """Generate all observability dashboards.

    Parameters
    ----------
    output_dir : str | Path
        Output directory for dashboards.

    Returns
    -------
    dict[str, Path]
        Mapping of dashboard names to their file paths.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    dashboards = {}

    # Generate each dashboard
    cli_path = output_dir / "cli-performance.html"
    generate_cli_dashboard(cli_path)
    dashboards["cli_performance"] = cli_path

    ggen_path = output_dir / "ggen-transformation.html"
    generate_ggen_dashboard(ggen_path)
    dashboards["ggen_transformation"] = ggen_path

    test_path = output_dir / "test-suite-health.html"
    generate_test_dashboard(test_path)
    dashboards["test_suite"] = test_path

    resource_path = output_dir / "resource-usage.html"
    generate_resource_dashboard(resource_path)
    dashboards["resource_usage"] = resource_path

    # Generate index
    index_content = []
    index_content.append("<h2>Available Dashboards</h2>")
    index_content.append('<div class="metric-grid">')

    for name, path in dashboards.items():
        display_name = name.replace("_", " ").title()
        index_content.append(
            f'<div class="metric-card">'
            f'<div class="metric-label">{display_name}</div>'
            f'<div class="metric-value">'
            f'<a href="{path.name}" style="text-decoration:none;color:#3498db">View →</a>'
            f'</div>'
            f'</div>'
        )

    index_content.append("</div>")

    index_html = HTML_TEMPLATE.format(
        title="Observability Dashboards",
        content="\n".join(index_content),
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    index_path = output_dir / "index.html"
    index_path.write_text(index_html)
    dashboards["index"] = index_path

    return dashboards


def export_metrics_json(output_path: str | Path) -> None:
    """Export all metrics as JSON.

    Parameters
    ----------
    output_path : str | Path
        Output path for JSON file.
    """
    if not ADVANCED_OBS_AVAILABLE:
        raise ImportError("Advanced observability not available")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Get all stats
    all_stats = get_all_stats()

    # Get anomalies
    anomalies = detect_anomalies()

    data = {
        "timestamp": datetime.now().isoformat(),
        "statistics": all_stats,
        "anomalies": [a.to_dict() for a in anomalies],
    }

    with Path(output_path).open("w") as f:
        json.dump(data, f, indent=2)


__all__ = [
    "export_metrics_json",
    "generate_all_dashboards",
    "generate_cli_dashboard",
    "generate_ggen_dashboard",
    "generate_resource_dashboard",
    "generate_test_dashboard",
]
