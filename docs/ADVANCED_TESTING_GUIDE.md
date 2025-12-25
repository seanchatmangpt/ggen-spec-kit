# Advanced Testing Infrastructure Guide

This guide provides comprehensive documentation for the hyper-advanced testing infrastructure in ggen-spec-kit.

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Testing Infrastructure](#testing-infrastructure)
4. [Property-Based Testing](#property-based-testing)
5. [Mutation Testing](#mutation-testing)
6. [Performance Benchmarking](#performance-benchmarking)
7. [Coverage Analysis](#coverage-analysis)
8. [Flaky Test Detection](#flaky-test-detection)
9. [Test Reporting](#test-reporting)
10. [Best Practices](#best-practices)

## Overview

The ggen-spec-kit project features a hyper-advanced testing infrastructure with:

- **Custom pytest plugins** for performance regression detection, mutation testing, coverage analysis, and flaky test detection
- **Property-based testing** using Hypothesis for mathematical property verification
- **Mutation testing** with mutmut for test quality assessment
- **Performance benchmarking** with pytest-benchmark for tracking performance trends
- **Comprehensive reporting** with HTML dashboards and JSON metrics

## Installation

### Basic Testing Dependencies

```bash
# Install development dependencies
uv sync --group dev
```

### Advanced Testing Dependencies

```bash
# Install all advanced testing tools
uv sync --group testing

# Or install all features
uv sync --group all
```

### Individual Tools

```bash
# Property-based testing
uv pip install hypothesis

# Mutation testing
uv pip install mutmut

# Performance benchmarking
uv pip install pytest-benchmark

# Parallel execution
uv pip install pytest-xdist

# HTML reports
uv pip install pytest-html pytest-json-report
```

## Testing Infrastructure

### Custom Pytest Plugins

The project includes six custom pytest plugins:

1. **PerformanceRegressionPlugin**: Detects performance slowdowns
2. **MutationTestingPlugin**: Integrates with mutmut
3. **CoverageAnalysisPlugin**: Identifies coverage gaps
4. **FlakyTestDetector**: Tracks unreliable tests
5. **TestCategoryPlugin**: Categorizes tests automatically
6. **TestReporterPlugin**: Enhanced test reporting

### Plugin Registration

Plugins are automatically registered via `pytest_plugins` in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
plugins = ["specify_cli.testing.pytest_plugins"]
```

### Test Categories

Tests are automatically categorized by:

- **Location**: `unit/`, `integration/`, `e2e/`
- **Markers**: `@pytest.mark.unit`, `@pytest.mark.slow`, etc.

Available markers:
- `unit`: Fast unit tests (no I/O)
- `integration`: Integration tests (may have I/O)
- `e2e`: End-to-end tests (full system)
- `slow`: Slow-running tests
- `benchmark`: Performance benchmarks
- `property`: Property-based tests
- `mutation`: Mutation testing targets
- `requires_docker`: Needs Docker
- `requires_git`: Needs Git
- `requires_network`: Needs network access

## Property-Based Testing

### Overview

Property-based testing uses Hypothesis to generate randomized test cases that verify mathematical properties and invariants.

### Example: Hyperdimensional Vector Properties

```python
from hypothesis import given, strategies as st
import numpy as np
import pytest

@pytest.mark.property
class TestVectorProperties:
    @given(dim=st.integers(min_value=100, max_value=1000))
    def test_dimension_preservation(self, dim: int):
        """Test that operations preserve dimensionality."""
        v1 = np.random.choice([-1.0, 1.0], size=dim)
        v2 = np.random.choice([-1.0, 1.0], size=dim)

        bound = v1 * v2
        assert bound.shape == (dim,)

    @given(seed=st.integers(min_value=0, max_value=10000))
    def test_binding_commutativity(self, seed: int):
        """Test that binding is commutative: A ⊗ B = B ⊗ A."""
        np.random.seed(seed)
        dim = 500

        v1 = np.random.choice([-1.0, 1.0], size=dim)
        v2 = np.random.choice([-1.0, 1.0], size=dim)

        forward = v1 * v2
        backward = v2 * v1

        np.testing.assert_array_equal(forward, backward)
```

### Running Property-Based Tests

```bash
# Run all property-based tests
pytest -m property

# Increase test case generation
pytest -m property --hypothesis-seed=42 --hypothesis-verbosity=verbose

# Save failing examples
pytest -m property  # Examples saved to .hypothesis/examples
```

### Hypothesis Configuration

Configuration in `pyproject.toml`:

```toml
[tool.hypothesis]
max_examples = 100          # Number of test cases
derandomize = false         # Allow randomization
verbosity = "normal"        # Output verbosity
database_file = ".hypothesis/examples"  # Example storage
```

## Mutation Testing

### Overview

Mutation testing modifies your code to verify that tests catch bugs. A high mutation score indicates effective tests.

### Running Mutation Tests

```bash
# Run mutation testing
pytest --mutation-test

# Target specific directory
pytest --mutation-test --mutation-target=src/specify_cli/ops/

# Run directly with mutmut
mutmut run --paths-to-mutate src/specify_cli/

# View results
mutmut results
mutmut html  # Generate HTML report
```

### Configuration

```toml
[tool.mutmut]
paths_to_mutate = "src/specify_cli/"
backup = false
runner = "pytest -x --tb=short"
tests_dir = "tests/"
```

### Interpreting Results

- **Killed**: Mutation caught by tests ✓
- **Survived**: Mutation not caught by tests ✗
- **Timeout**: Test took too long
- **Suspicious**: Unusual behavior

**Target Mutation Score**: >80%

## Performance Benchmarking

### Overview

pytest-benchmark tracks performance of critical operations and detects regressions.

### Example Benchmark

```python
import pytest
import numpy as np

@pytest.mark.benchmark
class TestPerformanceBenchmarks:
    def test_benchmark_vector_binding(self, benchmark):
        """Benchmark vector binding operation."""
        v1 = np.random.choice([-1.0, 1.0], size=10000)
        v2 = np.random.choice([-1.0, 1.0], size=10000)

        def bind_vectors():
            return v1 * v2

        result = benchmark(bind_vectors)
        assert result.shape == v1.shape
```

### Running Benchmarks

```bash
# Run benchmarks (disabled by default)
pytest --benchmark-enable tests/benchmark/

# Save baseline
pytest --benchmark-enable --benchmark-save=baseline

# Compare against baseline
pytest --benchmark-enable --benchmark-compare=baseline

# Generate histogram
pytest --benchmark-enable --benchmark-histogram
```

### Configuration

```toml
[tool.pytest.benchmark]
disable = true              # Disabled by default
min_rounds = 5              # Statistical significance
timer = "time.perf_counter" # High precision timer
warmup = true               # Warmup iterations
```

## Coverage Analysis

### Overview

Advanced coverage analysis identifies:
- Uncovered code blocks
- Partial branch coverage
- Critical gaps prioritized by importance

### Running Coverage Analysis

```bash
# Run with coverage
pytest --cov=src/specify_cli

# Generate HTML report
pytest --cov=src/specify_cli --cov-report=html

# Generate JSON for gap analysis
pytest --cov=src/specify_cli --cov-report=json

# View coverage gaps
cat reports/coverage_gaps.json
```

### Coverage Gaps Plugin

The `CoverageAnalysisPlugin` automatically:
1. Analyzes coverage data
2. Groups consecutive uncovered lines
3. Prioritizes gaps by file
4. Generates actionable reports

### Configuration

```toml
[tool.coverage.run]
source = ["src/specify_cli"]
branch = true               # Branch coverage
omit = ["*/tests/*"]        # Exclude tests

[tool.coverage.report]
fail_under = 80             # Minimum coverage
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
]
```

## Flaky Test Detection

### Overview

Flaky tests pass and fail intermittently, indicating instability. The FlakyTestDetector tracks:
- Test outcome history
- Flakiness score (0-1)
- Pass rate trends
- Outcome patterns

### How It Works

1. **Track Outcomes**: Records pass/fail for each test run
2. **Calculate Score**: Based on variance and alternation frequency
3. **Detect Flakiness**: Score >0.3 indicates flaky test
4. **Generate Report**: Lists flaky tests with metrics

### Viewing Flaky Tests

```bash
# Run tests (detector runs automatically)
pytest

# View flaky test report
cat reports/flaky_tests.json

# View history
cat .pytest_flaky_history.json
```

### Flakiness Score

Score calculation:
- **0.0**: Perfectly stable (all pass or all fail)
- **0.3-0.5**: Moderately flaky
- **>0.5**: Highly flaky
- **1.0**: Maximum instability (alternating pass/fail)

## Test Reporting

### Comprehensive Reports

The testing infrastructure generates multiple reports:

1. **HTML Test Report**: Visual test results (`reports/test_report.html`)
2. **JSON Test Results**: Machine-readable data (`reports/test_results.json`)
3. **Coverage Report**: HTML coverage (`reports/coverage/`)
4. **Performance Results**: Regression tracking (`reports/performance_results.json`)
5. **Flaky Tests**: Stability analysis (`reports/flaky_tests.json`)
6. **Mutation Results**: Test quality (`reports/mutation_results.json`)

### Generating Reports

```bash
# Run tests with all reporting
pytest

# Generate comprehensive report
python -m specify_cli.testing.reporting

# View HTML report
open reports/comprehensive_report.html
```

### Report Contents

Comprehensive report includes:
- Test metrics (pass rate, coverage, mutation score)
- Coverage gaps with file/line details
- Flaky tests with scores and trends
- Performance regressions with slowdown %
- Summary and quality assessment

## Best Practices

### 1. Test Organization

```
tests/
├── unit/                  # Fast, isolated tests
├── integration/           # Component integration
├── e2e/                   # End-to-end scenarios
├── property/              # Property-based tests
└── benchmark/             # Performance benchmarks
```

### 2. Writing Good Property Tests

```python
# DO: Test mathematical properties
@given(x=st.integers(), y=st.integers())
def test_commutativity(x, y):
    assert add(x, y) == add(y, x)

# DON'T: Test implementation details
@given(x=st.integers())
def test_specific_value(x):
    assert add(x, 5) == x + 5  # Too specific
```

### 3. Performance Baselines

```bash
# Establish baseline
pytest --benchmark-enable --benchmark-save=v1.0.0

# Compare after changes
pytest --benchmark-enable --benchmark-compare=v1.0.0

# Update baseline if improvement
pytest --benchmark-enable --benchmark-save=v1.0.1
```

### 4. Continuous Integration

```yaml
# .github/workflows/test.yml
- name: Run tests with coverage
  run: pytest --cov=src/specify_cli --cov-report=xml

- name: Run mutation tests
  run: mutmut run --paths-to-mutate src/

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

### 5. Test Quality Metrics

Target metrics:
- **Test Coverage**: >80%
- **Mutation Score**: >80%
- **Pass Rate**: >95%
- **Flaky Tests**: 0
- **Performance Regressions**: 0

## Command Reference

### Running Tests

```bash
# All tests
pytest

# Specific category
pytest -m unit
pytest -m integration
pytest -m e2e

# Specific file/test
pytest tests/unit/test_ops.py
pytest tests/unit/test_ops.py::test_specific_function

# Parallel execution
pytest -n auto  # Use all CPUs

# With coverage
pytest --cov=src/specify_cli

# With benchmarks
pytest --benchmark-enable

# With mutation testing
pytest --mutation-test
```

### Reporting

```bash
# HTML reports
pytest --html=reports/test_report.html --self-contained-html

# JSON reports
pytest --json-report --json-report-file=reports/test_results.json

# Coverage reports
pytest --cov-report=html --cov-report=json

# Comprehensive report
python -m specify_cli.testing.reporting
```

### Debugging

```bash
# Verbose output
pytest -vv

# Show print statements
pytest -s

# Stop at first failure
pytest -x

# Drop to debugger on failure
pytest --pdb

# Show locals on failure
pytest -l
```

## Troubleshooting

### Common Issues

**Issue**: Plugins not loading
```bash
# Verify plugin registration
pytest --trace-config
```

**Issue**: Hypothesis examples failing
```bash
# Clear example database
rm -rf .hypothesis/
pytest -m property
```

**Issue**: Mutation testing timeout
```bash
# Increase timeout
mutmut run --timeout-multiplier=2.0
```

**Issue**: Benchmark variance
```bash
# Increase rounds for stability
pytest --benchmark-enable --benchmark-min-rounds=10
```

## Advanced Usage

### Custom Hypothesis Strategies

```python
from hypothesis import strategies as st

@st.composite
def hyperdimensional_vector(draw, dimensions=10000):
    """Generate random HD vector."""
    return draw(st.lists(
        st.sampled_from([-1.0, 1.0]),
        min_size=dimensions,
        max_size=dimensions
    ))
```

### Custom Benchmark Fixtures

```python
@pytest.fixture
def large_dataset():
    """Generate large dataset for benchmarking."""
    return np.random.rand(100000, 100)

def test_benchmark_processing(benchmark, large_dataset):
    result = benchmark(process_data, large_dataset)
    assert result is not None
```

### Conditional Test Execution

```python
@pytest.mark.skipif(not has_gpu(), reason="Requires GPU")
@pytest.mark.benchmark
def test_gpu_acceleration(benchmark):
    result = benchmark(gpu_compute)
    assert result.device == "cuda"
```

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [mutmut Documentation](https://mutmut.readthedocs.io/)
- [pytest-benchmark Documentation](https://pytest-benchmark.readthedocs.io/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)

## Metrics Dashboard

The comprehensive report provides a dashboard with:

- ✓ **Test Quality**: Pass rate, failure analysis
- ✓ **Coverage**: Line/branch coverage, gaps
- ✓ **Mutation Score**: Test effectiveness
- ✓ **Performance**: Regression tracking, trends
- ✓ **Stability**: Flaky test detection
- ✓ **Trends**: Historical metrics

Access at: `reports/comprehensive_report.html`

---

**Remember**: High-quality tests are as important as high-quality code. Use this infrastructure to maintain excellent test coverage, detect regressions early, and ensure code reliability.
