"""
Advanced testing infrastructure for specify-cli.

This module provides hyper-advanced pytest plugins and testing utilities:
- Performance regression detection
- Mutation testing integration
- Coverage gap analysis
- Flaky test detection
- Test categorization and reporting
- Automated test generation
- Property-based testing utilities
"""

from __future__ import annotations

__all__ = [
    "CoverageAnalysisPlugin",
    "FlakyTestDetector",
    "MutationTestingPlugin",
    "PerformanceRegressionPlugin",
    "TestCategoryPlugin",
    "TestReporterPlugin",
]

from specify_cli.testing.pytest_plugins import (
    CoverageAnalysisPlugin,
    FlakyTestDetector,
    MutationTestingPlugin,
    PerformanceRegressionPlugin,
    TestCategoryPlugin,
    TestReporterPlugin,
)
