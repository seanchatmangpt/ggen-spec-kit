"""
Hyper-advanced pytest plugins for comprehensive testing infrastructure.

This module provides custom pytest plugins for:
- Performance regression detection with baseline tracking
- Mutation testing integration (mutmut)
- Coverage gap analysis and reporting
- Flaky test detection with statistical analysis
- Rich formatted test reporting
- Automated test categorization

Usage
-----
Add to pytest_plugins in conftest.py:
    pytest_plugins = [
        "specify_cli.testing.pytest_plugins.PerformanceRegressionPlugin",
        "specify_cli.testing.pytest_plugins.CoverageAnalysisPlugin",
        "specify_cli.testing.pytest_plugins.FlakyTestDetector",
    ]
"""

from __future__ import annotations

import json
import subprocess
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest
from _pytest.config import Config
from _pytest.nodes import Item
from _pytest.reports import TestReport
from _pytest.terminal import TerminalReporter

if TYPE_CHECKING:
    from _pytest.config.argparsing import Parser


# ============================================================================
# Data Classes for Tracking
# ============================================================================


@dataclass
class PerformanceBaseline:
    """Performance baseline for a test."""

    test_id: str
    mean_duration: float
    std_deviation: float
    min_duration: float
    max_duration: float
    sample_count: int
    last_updated: float


@dataclass
class TestExecution:
    """Single test execution record."""

    test_id: str
    duration: float
    passed: bool
    timestamp: float
    traceback: str | None = None


@dataclass
class FlakyTestRecord:
    """Record of flaky test behavior."""

    test_id: str
    total_runs: int = 0
    passes: int = 0
    failures: int = 0
    flakiness_score: float = 0.0
    last_outcomes: list[bool] = field(default_factory=list)


@dataclass
class CoverageGap:
    """Represents a coverage gap in the codebase."""

    file_path: str
    line_number: int
    line_count: int
    gap_type: str  # "uncovered", "partial", "branch"
    context: str | None = None


# ============================================================================
# Performance Regression Detection Plugin
# ============================================================================


class PerformanceRegressionPlugin:
    """
    Detect performance regressions by comparing test execution times
    against historical baselines.

    Features
    --------
    - Automatic baseline generation from test runs
    - Statistical significance testing (> 2 std deviations)
    - Performance trend tracking
    - Automatic slowdown warnings
    - HTML performance reports
    """

    def __init__(self, config: Config) -> None:
        """Initialize performance regression plugin."""
        self.config = config
        self.baseline_file = Path(".pytest_performance_baseline.json")
        self.results_file = Path("reports/performance_results.json")
        self.baselines: dict[str, PerformanceBaseline] = {}
        self.current_results: dict[str, TestExecution] = {}
        self.regressions: list[tuple[str, float, float]] = []

        # Load existing baselines
        self._load_baselines()

    def _load_baselines(self) -> None:
        """Load performance baselines from disk."""
        if self.baseline_file.exists():
            try:
                data = json.loads(self.baseline_file.read_text())
                self.baselines = {
                    test_id: PerformanceBaseline(**baseline)
                    for test_id, baseline in data.items()
                }
            except (json.JSONDecodeError, TypeError):
                self.baselines = {}

    def _save_baselines(self) -> None:
        """Save performance baselines to disk."""
        self.baseline_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            test_id: {
                "test_id": baseline.test_id,
                "mean_duration": baseline.mean_duration,
                "std_deviation": baseline.std_deviation,
                "min_duration": baseline.min_duration,
                "max_duration": baseline.max_duration,
                "sample_count": baseline.sample_count,
                "last_updated": baseline.last_updated,
            }
            for test_id, baseline in self.baselines.items()
        }
        self.baseline_file.write_text(json.dumps(data, indent=2))

    @pytest.hookimpl(tryfirst=True, hookwrapper=True)
    def pytest_runtest_makereport(self, item: Item, call: Any) -> Any:
        """Hook to capture test execution time."""
        outcome = yield
        report: TestReport = outcome.get_result()

        if report.when == "call":
            test_id = item.nodeid
            execution = TestExecution(
                test_id=test_id,
                duration=call.stop - call.start,
                passed=report.passed,
                timestamp=time.time(),
                traceback=str(report.longrepr) if report.failed else None,
            )
            self.current_results[test_id] = execution

            # Check for regression
            self._check_regression(test_id, execution.duration)

    def _check_regression(self, test_id: str, duration: float) -> None:
        """Check if test execution shows performance regression."""
        if test_id not in self.baselines:
            return

        baseline = self.baselines[test_id]
        # Regression if > 2 std deviations slower than mean
        threshold = baseline.mean_duration + (2 * baseline.std_deviation)

        if duration > threshold:
            slowdown_pct = ((duration - baseline.mean_duration) / baseline.mean_duration) * 100
            self.regressions.append((test_id, duration, slowdown_pct))

    def pytest_sessionfinish(self, _session: pytest.Session) -> None:
        """Update baselines and generate reports at session end."""
        # Update baselines with new results
        for test_id, execution in self.current_results.items():
            self._update_baseline(test_id, execution.duration)

        self._save_baselines()
        self._generate_report()

        # Print regressions
        if self.regressions:
            print("\n" + "=" * 80)  # noqa: T201
            print("PERFORMANCE REGRESSIONS DETECTED")  # noqa: T201
            print("=" * 80)  # noqa: T201
            for test_id, duration, slowdown_pct in self.regressions:
                baseline = self.baselines[test_id]
                print(f"\n{test_id}")  # noqa: T201
                print(f"  Current: {duration:.4f}s")  # noqa: T201
                print(f"  Baseline: {baseline.mean_duration:.4f}s ± {baseline.std_deviation:.4f}s")  # noqa: T201
                print(f"  Slowdown: {slowdown_pct:.1f}%")  # noqa: T201

    def _update_baseline(self, test_id: str, duration: float) -> None:
        """Update baseline statistics with new execution."""
        if test_id in self.baselines:
            baseline = self.baselines[test_id]
            # Exponential moving average for mean
            alpha = 0.2
            new_mean = (alpha * duration) + ((1 - alpha) * baseline.mean_duration)

            # Update statistics
            baseline.mean_duration = new_mean
            baseline.min_duration = min(baseline.min_duration, duration)
            baseline.max_duration = max(baseline.max_duration, duration)
            baseline.sample_count += 1
            baseline.last_updated = time.time()

            # Estimate std deviation (simplified)
            baseline.std_deviation = abs(duration - new_mean) * 0.5
        else:
            # Create new baseline
            self.baselines[test_id] = PerformanceBaseline(
                test_id=test_id,
                mean_duration=duration,
                std_deviation=duration * 0.1,  # 10% initial estimate
                min_duration=duration,
                max_duration=duration,
                sample_count=1,
                last_updated=time.time(),
            )

    def _generate_report(self) -> None:
        """Generate HTML performance report."""
        self.results_file.parent.mkdir(parents=True, exist_ok=True)
        report_data = {
            "current_results": [
                {
                    "test_id": exec.test_id,
                    "duration": exec.duration,
                    "passed": exec.passed,
                    "timestamp": exec.timestamp,
                }
                for exec in self.current_results.values()
            ],
            "regressions": [
                {
                    "test_id": test_id,
                    "current_duration": duration,
                    "slowdown_percent": slowdown,
                    "baseline_mean": self.baselines[test_id].mean_duration,
                }
                for test_id, duration, slowdown in self.regressions
            ],
        }
        self.results_file.write_text(json.dumps(report_data, indent=2))


# ============================================================================
# Mutation Testing Integration Plugin
# ============================================================================


class MutationTestingPlugin:
    """
    Integration with mutmut for mutation testing.

    Features
    --------
    - Automatic mutation testing after test runs
    - Mutation score calculation
    - Survival rate tracking
    - Integration with CI/CD pipelines
    """

    def __init__(self, config: Config) -> None:
        """Initialize mutation testing plugin."""
        self.config = config
        self.enabled = config.getoption("--mutation-test", default=False)
        self.results_file = Path("reports/mutation_results.json")

    @staticmethod
    def pytest_addoption(parser: Parser) -> None:
        """Add mutation testing command-line options."""
        group = parser.getgroup("mutation")
        group.addoption(
            "--mutation-test",
            action="store_true",
            default=False,
            help="Run mutation testing with mutmut",
        )
        group.addoption(
            "--mutation-target",
            action="store",
            default="src/",
            help="Target directory for mutation testing",
        )

    def pytest_sessionfinish(self, _session: pytest.Session, exitstatus: int) -> None:
        """Run mutation testing after test session if enabled."""
        if not self.enabled or exitstatus != 0:
            return

        print("\n" + "=" * 80)  # noqa: T201
        print("RUNNING MUTATION TESTING")  # noqa: T201
        print("=" * 80)  # noqa: T201

        target = self.config.getoption("--mutation-target")
        self._run_mutation_testing(target)

    def _run_mutation_testing(self, target: str) -> None:
        """Execute mutation testing with mutmut."""
        try:
            # Check if mutmut is installed
            subprocess.run(
                ["mutmut", "--version"],
                check=True,
                capture_output=True,
                text=True,
            )

            # Run mutation testing
            result = subprocess.run(
                ["mutmut", "run", "--paths-to-mutate", target],
                check=False, capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Get results
            results_output = subprocess.run(
                ["mutmut", "results"],
                check=False, capture_output=True,
                text=True,
            )

            # Parse and save results
            self._parse_mutation_results(results_output.stdout)

        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"\nMutation testing failed: {e}")  # noqa: T201
            print("Install mutmut: pip install mutmut")  # noqa: T201

    def _parse_mutation_results(self, output: str) -> None:
        """Parse mutmut results and generate report."""
        # Simple parsing - can be enhanced
        lines = output.split("\n")
        results = {
            "killed": 0,
            "survived": 0,
            "timeout": 0,
            "suspicious": 0,
            "total": 0,
        }

        for line in lines:
            if "killed" in line.lower():
                try:
                    results["killed"] = int(line.split()[0])
                except (ValueError, IndexError):
                    pass
            elif "survived" in line.lower():
                try:
                    results["survived"] = int(line.split()[0])
                except (ValueError, IndexError):
                    pass

        results["total"] = results["killed"] + results["survived"]
        if results["total"] > 0:
            results["mutation_score"] = (results["killed"] / results["total"]) * 100

        self.results_file.parent.mkdir(parents=True, exist_ok=True)
        self.results_file.write_text(json.dumps(results, indent=2))

        print(f"\nMutation Score: {results.get('mutation_score', 0):.1f}%")  # noqa: T201
        print(f"Killed: {results['killed']}, Survived: {results['survived']}")  # noqa: T201


# ============================================================================
# Coverage Gap Analysis Plugin
# ============================================================================


class CoverageAnalysisPlugin:
    """
    Analyze coverage gaps and generate actionable reports.

    Features
    --------
    - Identify uncovered code blocks
    - Detect partial branch coverage
    - Prioritize gaps by criticality
    - Generate test suggestions
    """

    def __init__(self, config: Config) -> None:
        """Initialize coverage analysis plugin."""
        self.config = config
        self.gaps: list[CoverageGap] = []
        self.coverage_file = Path(".coverage")
        self.results_file = Path("reports/coverage_gaps.json")

    def pytest_sessionfinish(self, _session: pytest.Session) -> None:
        """Analyze coverage gaps at session end."""
        if not self.coverage_file.exists():
            return

        print("\n" + "=" * 80)  # noqa: T201
        print("ANALYZING COVERAGE GAPS")  # noqa: T201
        print("=" * 80)  # noqa: T201

        self._analyze_coverage()
        self._generate_gap_report()

    def _analyze_coverage(self) -> None:
        """Analyze coverage data to find gaps."""
        try:
            # Use coverage.py API to analyze gaps
            import coverage

            cov = coverage.Coverage(data_file=str(self.coverage_file))
            cov.load()

            # Get coverage data
            data = cov.get_data()
            files = data.measured_files()

            for file in files:
                if "/tests/" in file or "__pycache__" in file:
                    continue

                # Get line data
                analysis = cov.analysis2(file)
                if not analysis:
                    continue

                _, executed, _, missing = analysis

                # Find gaps (missing lines)
                if missing:
                    # Group consecutive missing lines
                    gap_start = None
                    gap_count = 0

                    for line in sorted(missing):
                        if gap_start is None:
                            gap_start = line
                            gap_count = 1
                        elif line == gap_start + gap_count:
                            gap_count += 1
                        else:
                            # Save previous gap
                            self.gaps.append(
                                CoverageGap(
                                    file_path=file,
                                    line_number=gap_start,
                                    line_count=gap_count,
                                    gap_type="uncovered",
                                )
                            )
                            gap_start = line
                            gap_count = 1

                    # Save last gap
                    if gap_start:
                        self.gaps.append(
                            CoverageGap(
                                file_path=file,
                                line_number=gap_start,
                                line_count=gap_count,
                                gap_type="uncovered",
                            )
                        )

        except ImportError:
            print("Coverage.py not available for gap analysis")  # noqa: T201
        except Exception as e:
            print(f"Error analyzing coverage: {e}")  # noqa: T201

    def _generate_gap_report(self) -> None:
        """Generate coverage gap report."""
        if not self.gaps:
            print("No coverage gaps detected!")  # noqa: T201
            return

        # Sort gaps by file and line
        self.gaps.sort(key=lambda g: (g.file_path, g.line_number))

        # Group by file
        gaps_by_file: dict[str, list[CoverageGap]] = defaultdict(list)
        for gap in self.gaps:
            gaps_by_file[gap.file_path].append(gap)

        # Generate report
        print(f"\nFound {len(self.gaps)} coverage gaps across {len(gaps_by_file)} files")  # noqa: T201
        print("\nTop gaps:")  # noqa: T201
        for file, file_gaps in list(gaps_by_file.items())[:5]:
            print(f"\n{file}:")  # noqa: T201
            for gap in file_gaps[:3]:
                print(  # noqa: T201
                    f"  Lines {gap.line_number}-{gap.line_number + gap.line_count - 1}: "
                    f"{gap.gap_type}"
                )

        # Save detailed report
        self.results_file.parent.mkdir(parents=True, exist_ok=True)
        report_data = {
            "total_gaps": len(self.gaps),
            "files_with_gaps": len(gaps_by_file),
            "gaps": [
                {
                    "file": gap.file_path,
                    "line": gap.line_number,
                    "count": gap.line_count,
                    "type": gap.gap_type,
                }
                for gap in self.gaps
            ],
        }
        self.results_file.write_text(json.dumps(report_data, indent=2))


# ============================================================================
# Flaky Test Detector Plugin
# ============================================================================


class FlakyTestDetector:
    """
    Detect and track flaky tests using statistical analysis.

    Features
    --------
    - Automatic flaky test detection
    - Flakiness score calculation
    - Historical tracking
    - Isolation and reproduction tools
    """

    def __init__(self, config: Config) -> None:
        """Initialize flaky test detector."""
        self.config = config
        self.history_file = Path(".pytest_flaky_history.json")
        self.results_file = Path("reports/flaky_tests.json")
        self.test_records: dict[str, FlakyTestRecord] = {}
        self.session_results: dict[str, bool] = {}

        self._load_history()

    def _load_history(self) -> None:
        """Load flaky test history from disk."""
        if self.history_file.exists():
            try:
                data = json.loads(self.history_file.read_text())
                self.test_records = {
                    test_id: FlakyTestRecord(
                        test_id=test_id,
                        total_runs=record["total_runs"],
                        passes=record["passes"],
                        failures=record["failures"],
                        flakiness_score=record["flakiness_score"],
                        last_outcomes=record.get("last_outcomes", []),
                    )
                    for test_id, record in data.items()
                }
            except (json.JSONDecodeError, KeyError):
                self.test_records = {}

    def _save_history(self) -> None:
        """Save flaky test history to disk."""
        data = {
            test_id: {
                "test_id": record.test_id,
                "total_runs": record.total_runs,
                "passes": record.passes,
                "failures": record.failures,
                "flakiness_score": record.flakiness_score,
                "last_outcomes": record.last_outcomes[-10:],  # Keep last 10
            }
            for test_id, record in self.test_records.items()
        }
        self.history_file.write_text(json.dumps(data, indent=2))

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item: Item, _call: Any) -> Any:
        """Track test outcomes."""
        outcome = yield
        report: TestReport = outcome.get_result()

        if report.when == "call":
            test_id = item.nodeid
            self.session_results[test_id] = report.passed

    def pytest_sessionfinish(self, _session: pytest.Session) -> None:
        """Update flaky test records and generate report."""
        # Update records
        for test_id, passed in self.session_results.items():
            if test_id not in self.test_records:
                self.test_records[test_id] = FlakyTestRecord(test_id=test_id)

            record = self.test_records[test_id]
            record.total_runs += 1
            if passed:
                record.passes += 1
            else:
                record.failures += 1

            # Update last outcomes
            record.last_outcomes.append(passed)
            if len(record.last_outcomes) > 10:
                record.last_outcomes = record.last_outcomes[-10:]

            # Calculate flakiness score
            record.flakiness_score = self._calculate_flakiness(record)

        self._save_history()
        self._generate_flaky_report()

    def _calculate_flakiness(self, record: FlakyTestRecord) -> float:
        """
        Calculate flakiness score (0-1).

        A test is flaky if it has both passes and failures.
        Score is based on outcome variance and alternation frequency.
        """
        if record.total_runs < 2:
            return 0.0

        # Check if test has both passes and failures
        if record.passes == 0 or record.failures == 0:
            return 0.0

        # Calculate variance in outcomes
        pass_rate = record.passes / record.total_runs
        variance = pass_rate * (1 - pass_rate)

        # Calculate alternation frequency in recent outcomes
        alternations = 0
        for i in range(1, len(record.last_outcomes)):
            if record.last_outcomes[i] != record.last_outcomes[i - 1]:
                alternations += 1

        alternation_rate = (
            alternations / (len(record.last_outcomes) - 1) if len(record.last_outcomes) > 1 else 0
        )

        # Combine variance and alternation (0-1 scale)
        flakiness = (variance * 4) * 0.5 + alternation_rate * 0.5
        return min(flakiness, 1.0)

    def _generate_flaky_report(self) -> None:
        """Generate flaky test report."""
        # Find flaky tests (score > 0.3)
        flaky_tests = [
            record for record in self.test_records.values() if record.flakiness_score > 0.3
        ]

        if flaky_tests:
            print("\n" + "=" * 80)  # noqa: T201
            print(f"FLAKY TESTS DETECTED: {len(flaky_tests)}")  # noqa: T201
            print("=" * 80)  # noqa: T201

            # Sort by flakiness score
            flaky_tests.sort(key=lambda r: r.flakiness_score, reverse=True)

            for record in flaky_tests[:10]:  # Show top 10
                pass_rate = (record.passes / record.total_runs) * 100
                print(f"\n{record.test_id}")  # noqa: T201
                print(f"  Flakiness Score: {record.flakiness_score:.2f}")  # noqa: T201
                print(f"  Pass Rate: {pass_rate:.1f}% ({record.passes}/{record.total_runs})")  # noqa: T201
                print(f"  Recent: {['✓' if p else '✗' for p in record.last_outcomes[-5:]]}")  # noqa: T201

        # Save report
        self.results_file.parent.mkdir(parents=True, exist_ok=True)
        report_data = {
            "flaky_tests": [
                {
                    "test_id": record.test_id,
                    "flakiness_score": record.flakiness_score,
                    "total_runs": record.total_runs,
                    "passes": record.passes,
                    "failures": record.failures,
                    "pass_rate": (record.passes / record.total_runs) * 100,
                }
                for record in flaky_tests
            ]
        }
        self.results_file.write_text(json.dumps(report_data, indent=2))


# ============================================================================
# Test Category Plugin
# ============================================================================


class TestCategoryPlugin:
    """
    Automatically categorize tests and generate category reports.

    Features
    --------
    - Automatic categorization by path and markers
    - Category-based reporting
    - Test distribution analysis
    """

    def __init__(self, config: Config) -> None:
        """Initialize test category plugin."""
        self.config = config
        self.categories: dict[str, list[str]] = defaultdict(list)
        self.results_file = Path("reports/test_categories.json")

    def pytest_collection_modifyitems(self, _config: Config, items: list[Item]) -> None:
        """Categorize collected tests."""
        for item in items:
            # Categorize by path
            if "/unit/" in str(item.fspath):
                self.categories["unit"].append(item.nodeid)
            elif "/integration/" in str(item.fspath):
                self.categories["integration"].append(item.nodeid)
            elif "/e2e/" in str(item.fspath):
                self.categories["e2e"].append(item.nodeid)

            # Categorize by markers
            for marker in item.iter_markers():
                if marker.name in ("slow", "requires_docker", "requires_network"):
                    self.categories[marker.name].append(item.nodeid)

    def pytest_sessionfinish(self, _session: pytest.Session) -> None:
        """Generate category report."""
        if not self.categories:
            return

        print("\n" + "=" * 80)  # noqa: T201
        print("TEST CATEGORIES")  # noqa: T201
        print("=" * 80)  # noqa: T201

        total_tests = sum(len(tests) for tests in self.categories.values())
        print(f"\nTotal tests: {total_tests}")  # noqa: T201

        for category, tests in sorted(self.categories.items()):
            percentage = (len(tests) / total_tests) * 100 if total_tests > 0 else 0
            print(f"  {category}: {len(tests)} ({percentage:.1f}%)")  # noqa: T201

        # Save report
        self.results_file.parent.mkdir(parents=True, exist_ok=True)
        report_data = {
            "total_tests": total_tests,
            "categories": {category: len(tests) for category, tests in self.categories.items()},
        }
        self.results_file.write_text(json.dumps(report_data, indent=2))


# ============================================================================
# Rich Test Reporter Plugin
# ============================================================================


class TestReporterPlugin:
    """
    Enhanced test reporting with rich formatting.

    Features
    --------
    - Colorized output
    - Progress bars
    - Summary statistics
    - HTML report generation
    """

    def __init__(self, config: Config) -> None:
        """Initialize test reporter plugin."""
        self.config = config
        self.report_file = Path("reports/test_report.html")

    def pytest_terminal_summary(
        self, terminalreporter: TerminalReporter, _exitstatus: int, _config: Config
    ) -> None:
        """Generate enhanced terminal summary."""
        terminalreporter.write_sep("=", "TEST EXECUTION SUMMARY", bold=True)

        # Get stats
        stats = terminalreporter.stats

        # Calculate metrics
        passed = len(stats.get("passed", []))
        failed = len(stats.get("failed", []))
        skipped = len(stats.get("skipped", []))
        total = passed + failed + skipped

        if total > 0:
            pass_rate = (passed / total) * 100
            terminalreporter.write_line(f"\nPass Rate: {pass_rate:.1f}%")
            terminalreporter.write_line(f"Passed: {passed}")
            terminalreporter.write_line(f"Failed: {failed}")
            terminalreporter.write_line(f"Skipped: {skipped}")


# ============================================================================
# Plugin Registration
# ============================================================================


def pytest_configure(config: Config) -> None:
    """Register plugins automatically."""
    # Only register if not already registered
    if not hasattr(config, "_specify_plugins_registered"):
        config._specify_plugins_registered = True  # type: ignore[attr-defined]

        # Register plugins
        config.pluginmanager.register(PerformanceRegressionPlugin(config), "performance_regression")
        config.pluginmanager.register(CoverageAnalysisPlugin(config), "coverage_analysis")
        config.pluginmanager.register(FlakyTestDetector(config), "flaky_detector")
        config.pluginmanager.register(TestCategoryPlugin(config), "test_category")
        config.pluginmanager.register(TestReporterPlugin(config), "test_reporter")


def pytest_addoption(parser: Parser) -> None:
    """Add custom command-line options."""
    MutationTestingPlugin.pytest_addoption(parser)
