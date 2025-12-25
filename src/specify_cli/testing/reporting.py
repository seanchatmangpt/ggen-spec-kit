"""
Advanced test reporting and analysis utilities.

This module provides utilities for generating comprehensive test reports,
analyzing test results, and producing actionable insights.

Features
--------
- HTML report generation with Rich formatting
- Test metrics aggregation
- Coverage gap analysis
- Performance trend analysis
- Flaky test identification
- Mutation testing summaries
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any



# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class TestMetrics:
    """Aggregated test metrics."""

    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: int = 0
    duration: float = 0.0
    pass_rate: float = 0.0
    coverage_percent: float = 0.0
    mutation_score: float = 0.0
    flaky_tests: int = 0
    performance_regressions: int = 0


@dataclass
class TestReport:
    """Comprehensive test report."""

    timestamp: str
    metrics: TestMetrics
    coverage_gaps: list[dict[str, Any]] = field(default_factory=list)
    flaky_tests: list[dict[str, Any]] = field(default_factory=list)
    performance_regressions: list[dict[str, Any]] = field(default_factory=list)
    benchmark_results: list[dict[str, Any]] = field(default_factory=list)
    mutation_results: dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Report Generation
# ============================================================================


class TestReportGenerator:
    """Generate comprehensive test reports from multiple sources."""

    def __init__(self, reports_dir: Path = Path("reports")) -> None:
        """
        Initialize test report generator.

        Parameters
        ----------
        reports_dir : Path
            Directory containing test reports.
        """
        self.reports_dir = reports_dir
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def load_test_results(self) -> dict[str, Any]:
        """Load test results from JSON report."""
        results_file = self.reports_dir / "test_results.json"
        if not results_file.exists():
            return {}

        return json.loads(results_file.read_text())

    def load_coverage_results(self) -> dict[str, Any]:
        """Load coverage results from JSON report."""
        coverage_file = self.reports_dir / "coverage.json"
        if not coverage_file.exists():
            return {}

        return json.loads(coverage_file.read_text())

    def load_performance_results(self) -> dict[str, Any]:
        """Load performance results."""
        perf_file = self.reports_dir / "performance_results.json"
        if not perf_file.exists():
            return {}

        return json.loads(perf_file.read_text())

    def load_flaky_results(self) -> dict[str, Any]:
        """Load flaky test results."""
        flaky_file = self.reports_dir / "flaky_tests.json"
        if not flaky_file.exists():
            return {}

        return json.loads(flaky_file.read_text())

    def load_mutation_results(self) -> dict[str, Any]:
        """Load mutation testing results."""
        mutation_file = self.reports_dir / "mutation_results.json"
        if not mutation_file.exists():
            return {}

        return json.loads(mutation_file.read_text())

    def load_coverage_gaps(self) -> dict[str, Any]:
        """Load coverage gap analysis."""
        gaps_file = self.reports_dir / "coverage_gaps.json"
        if not gaps_file.exists():
            return {}

        return json.loads(gaps_file.read_text())

    def generate_metrics(self) -> TestMetrics:
        """Generate aggregated test metrics."""
        test_results = self.load_test_results()
        coverage_results = self.load_coverage_results()
        mutation_results = self.load_mutation_results()
        flaky_results = self.load_flaky_results()
        perf_results = self.load_performance_results()

        # Extract metrics from test results
        summary = test_results.get("summary", {})
        total = summary.get("total", 0)
        passed = summary.get("passed", 0)
        failed = summary.get("failed", 0)
        skipped = summary.get("skipped", 0)

        # Calculate pass rate
        pass_rate = (passed / total * 100) if total > 0 else 0

        # Extract coverage
        coverage_percent = coverage_results.get("totals", {}).get("percent_covered", 0)

        # Extract mutation score
        mutation_score = mutation_results.get("mutation_score", 0)

        # Count flaky tests
        flaky_count = len(flaky_results.get("flaky_tests", []))

        # Count performance regressions
        perf_regressions = len(perf_results.get("regressions", []))

        return TestMetrics(
            total_tests=total,
            passed=passed,
            failed=failed,
            skipped=skipped,
            duration=summary.get("duration", 0),
            pass_rate=pass_rate,
            coverage_percent=coverage_percent,
            mutation_score=mutation_score,
            flaky_tests=flaky_count,
            performance_regressions=perf_regressions,
        )

    def generate_report(self) -> TestReport:
        """Generate comprehensive test report."""
        metrics = self.generate_metrics()
        coverage_gaps = self.load_coverage_gaps().get("gaps", [])
        flaky_tests = self.load_flaky_results().get("flaky_tests", [])
        perf_regressions = self.load_performance_results().get("regressions", [])
        mutation_results = self.load_mutation_results()

        return TestReport(
            timestamp=datetime.now().isoformat(),
            metrics=metrics,
            coverage_gaps=coverage_gaps,
            flaky_tests=flaky_tests,
            performance_regressions=perf_regressions,
            mutation_results=mutation_results,
        )

    def generate_html_report(self, output_file: Path | None = None) -> str:
        """Generate HTML test report."""
        if output_file is None:
            output_file = self.reports_dir / "comprehensive_report.html"

        report = self.generate_report()

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comprehensive Test Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #555;
            margin-top: 30px;
            border-bottom: 2px solid #ddd;
            padding-bottom: 5px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #4CAF50;
        }}
        .metric-card.warning {{
            border-left-color: #FF9800;
        }}
        .metric-card.error {{
            border-left-color: #f44336;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        .metric-label {{
            color: #777;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .timestamp {{
            color: #999;
            font-size: 0.9em;
        }}
        .status-passed {{
            color: #4CAF50;
            font-weight: bold;
        }}
        .status-failed {{
            color: #f44336;
            font-weight: bold;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        .badge-success {{
            background-color: #4CAF50;
            color: white;
        }}
        .badge-warning {{
            background-color: #FF9800;
            color: white;
        }}
        .badge-error {{
            background-color: #f44336;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Comprehensive Test Report</h1>
        <p class="timestamp">Generated: {report.timestamp}</p>

        <h2>Test Metrics</h2>
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{report.metrics.total_tests}</div>
                <div class="metric-label">Total Tests</div>
            </div>
            <div class="metric-card {'error' if report.metrics.failed > 0 else ''}">
                <div class="metric-value status-passed">{report.metrics.passed}</div>
                <div class="metric-label">Passed</div>
            </div>
            <div class="metric-card {'error' if report.metrics.failed > 0 else ''}">
                <div class="metric-value status-failed">{report.metrics.failed}</div>
                <div class="metric-label">Failed</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{report.metrics.pass_rate:.1f}%</div>
                <div class="metric-label">Pass Rate</div>
            </div>
            <div class="metric-card {'warning' if report.metrics.coverage_percent < 80 else ''}">
                <div class="metric-value">{report.metrics.coverage_percent:.1f}%</div>
                <div class="metric-label">Coverage</div>
            </div>
            <div class="metric-card {'warning' if report.metrics.mutation_score < 80 else ''}">
                <div class="metric-value">{report.metrics.mutation_score:.1f}%</div>
                <div class="metric-label">Mutation Score</div>
            </div>
            <div class="metric-card {'warning' if report.metrics.flaky_tests > 0 else ''}">
                <div class="metric-value">{report.metrics.flaky_tests}</div>
                <div class="metric-label">Flaky Tests</div>
            </div>
            <div class="metric-card {'warning' if report.metrics.performance_regressions > 0 else ''}">
                <div class="metric-value">{report.metrics.performance_regressions}</div>
                <div class="metric-label">Perf Regressions</div>
            </div>
        </div>

        <h2>Coverage Gaps</h2>
        <p>Found {len(report.coverage_gaps)} coverage gaps</p>
        {self._generate_gaps_table(report.coverage_gaps[:10])}

        <h2>Flaky Tests</h2>
        <p>Detected {len(report.flaky_tests)} flaky tests</p>
        {self._generate_flaky_table(report.flaky_tests[:10])}

        <h2>Performance Regressions</h2>
        <p>Found {len(report.performance_regressions)} performance regressions</p>
        {self._generate_perf_table(report.performance_regressions[:10])}

        <h2>Summary</h2>
        <ul>
            <li><strong>Test Quality:</strong> {'<span class="status-passed">EXCELLENT</span>' if report.metrics.pass_rate >= 95 else '<span class="status-failed">NEEDS IMPROVEMENT</span>'}</li>
            <li><strong>Coverage:</strong> {'<span class="status-passed">GOOD</span>' if report.metrics.coverage_percent >= 80 else '<span class="status-failed">LOW</span>'}</li>
            <li><strong>Mutation Score:</strong> {'<span class="status-passed">GOOD</span>' if report.metrics.mutation_score >= 80 else '<span class="status-failed">LOW</span>'}</li>
            <li><strong>Stability:</strong> {'<span class="status-passed">STABLE</span>' if report.metrics.flaky_tests == 0 else '<span class="status-failed">UNSTABLE</span>'}</li>
        </ul>
    </div>
</body>
</html>
"""

        output_file.write_text(html)
        return str(output_file)

    def _generate_gaps_table(self, gaps: list[dict[str, Any]]) -> str:
        """Generate HTML table for coverage gaps."""
        if not gaps:
            return "<p>No coverage gaps found!</p>"

        rows = ""
        for gap in gaps:
            rows += f"""
            <tr>
                <td>{gap.get('file', 'N/A')}</td>
                <td>{gap.get('line', 'N/A')}</td>
                <td>{gap.get('count', 'N/A')}</td>
                <td><span class="badge badge-warning">{gap.get('type', 'N/A')}</span></td>
            </tr>
            """

        return f"""
        <table>
            <thead>
                <tr>
                    <th>File</th>
                    <th>Line</th>
                    <th>Lines</th>
                    <th>Type</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        """

    def _generate_flaky_table(self, flaky: list[dict[str, Any]]) -> str:
        """Generate HTML table for flaky tests."""
        if not flaky:
            return "<p>No flaky tests detected!</p>"

        rows = ""
        for test in flaky:
            rows += f"""
            <tr>
                <td>{test.get('test_id', 'N/A')}</td>
                <td>{test.get('flakiness_score', 0):.2f}</td>
                <td>{test.get('pass_rate', 0):.1f}%</td>
                <td>{test.get('total_runs', 0)}</td>
            </tr>
            """

        return f"""
        <table>
            <thead>
                <tr>
                    <th>Test</th>
                    <th>Flakiness Score</th>
                    <th>Pass Rate</th>
                    <th>Total Runs</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        """

    def _generate_perf_table(self, regressions: list[dict[str, Any]]) -> str:
        """Generate HTML table for performance regressions."""
        if not regressions:
            return "<p>No performance regressions detected!</p>"

        rows = ""
        for reg in regressions:
            rows += f"""
            <tr>
                <td>{reg.get('test_id', 'N/A')}</td>
                <td>{reg.get('current_duration', 0):.4f}s</td>
                <td>{reg.get('baseline_mean', 0):.4f}s</td>
                <td><span class="badge badge-error">{reg.get('slowdown_percent', 0):.1f}%</span></td>
            </tr>
            """

        return f"""
        <table>
            <thead>
                <tr>
                    <th>Test</th>
                    <th>Current</th>
                    <th>Baseline</th>
                    <th>Slowdown</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        """

    def generate_summary_json(self, output_file: Path | None = None) -> str:
        """Generate JSON summary of all test metrics."""
        if output_file is None:
            output_file = self.reports_dir / "test_summary.json"

        report = self.generate_report()

        summary = {
            "timestamp": report.timestamp,
            "metrics": {
                "total_tests": report.metrics.total_tests,
                "passed": report.metrics.passed,
                "failed": report.metrics.failed,
                "skipped": report.metrics.skipped,
                "pass_rate": report.metrics.pass_rate,
                "coverage_percent": report.metrics.coverage_percent,
                "mutation_score": report.metrics.mutation_score,
                "flaky_tests": report.metrics.flaky_tests,
                "performance_regressions": report.metrics.performance_regressions,
            },
            "coverage_gaps_count": len(report.coverage_gaps),
            "flaky_tests_count": len(report.flaky_tests),
            "performance_regressions_count": len(report.performance_regressions),
        }

        output_file.write_text(json.dumps(summary, indent=2))
        return str(output_file)


# ============================================================================
# CLI Interface
# ============================================================================


def generate_comprehensive_report() -> None:
    """Generate comprehensive test report from command line."""
    generator = TestReportGenerator()
    html_report = generator.generate_html_report()
    json_summary = generator.generate_summary_json()

    print("\nComprehensive Test Report Generated")  # noqa: T201
    print("=" * 80)  # noqa: T201
    print(f"HTML Report: {html_report}")  # noqa: T201
    print(f"JSON Summary: {json_summary}")  # noqa: T201
    print("\nMetrics:")  # noqa: T201
    report = generator.generate_report()
    print(f"  Total Tests: {report.metrics.total_tests}")  # noqa: T201
    print(f"  Pass Rate: {report.metrics.pass_rate:.1f}%")  # noqa: T201
    print(f"  Coverage: {report.metrics.coverage_percent:.1f}%")  # noqa: T201
    print(f"  Mutation Score: {report.metrics.mutation_score:.1f}%")  # noqa: T201
    print(f"  Flaky Tests: {report.metrics.flaky_tests}")  # noqa: T201
    print(f"  Performance Regressions: {report.metrics.performance_regressions}")  # noqa: T201


if __name__ == "__main__":
    generate_comprehensive_report()
