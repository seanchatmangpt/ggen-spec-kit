# Run Tests

Execute test suite with filtering, coverage analysis, and failure diagnosis.

## Description
Runs pytest test suites with various options for filtering, coverage, and debugging. Provides detailed failure analysis and fix suggestions.

## Usage
```bash
/run-tests [PATH] [OPTIONS]
```

## Arguments
- `PATH` (optional) - Test path or pattern (default: `tests/`)
- `OPTIONS` (optional) - Additional pytest options

## Examples
```bash
# Run all tests
/run-tests

# Run specific test directory
/run-tests tests/unit/

# Run specific test file
/run-tests tests/unit/test_ggen_ops.py

# Run specific test function
/run-tests tests/unit/test_ggen_ops.py::test_sync_creates_files

# Run with coverage
/run-tests tests/ --cov=src/specify_cli

# Run with detailed coverage
/run-tests --cov=src/specify_cli --cov-report=term-missing

# Stop on first failure
/run-tests -x

# Run only failed tests from last run
/run-tests --lf

# Filter tests by name pattern
/run-tests -k "test_ggen"

# Run with verbose output
/run-tests -vv

# Run in parallel (fast)
/run-tests -n auto

# Combination
/run-tests tests/unit/ -x -v --cov=src/specify_cli
```

## What This Command Does

### 1. Execute Tests

```bash
uv run pytest [PATH] [OPTIONS] -v
```

### 2. Report Results

- Pass/fail summary
- Execution time
- Coverage percentage (if requested)
- Failed test details

### 3. Analyze Failures (if any)

- Stack trace analysis
- Root cause identification
- Suggested fixes
- Related code examination

### 4. Coverage Report (if requested)

- Overall coverage percentage
- Per-file coverage breakdown
- Missing lines identification
- Coverage diff from baseline

## Test Organization

```
tests/
├── unit/                    # Fast, isolated tests
│   ├── test_ggen_ops.py     # Operations layer tests
│   ├── test_process.py      # Core utilities tests
│   └── test_telemetry.py    # Telemetry tests
└── e2e/                     # End-to-end integration tests
    ├── test_commands_*.py   # Generated CLI tests
    └── test_workflows.py    # Full workflow tests
```

## Common Test Patterns

### Unit Tests (Fast, Isolated)
```bash
# Test specific module
/run-tests tests/unit/test_ggen_ops.py -v

# Expected: < 1s execution time
```

### E2E Tests (Slower, Integrated)
```bash
# Test actual CLI commands
/run-tests tests/e2e/ -v

# Expected: < 10s execution time
```

### Coverage-Driven Testing
```bash
# Find untested code
/run-tests --cov=src/specify_cli --cov-report=term-missing

# Target: 80%+ coverage
```

## Pytest Options Reference

| Option | Description | Example |
|--------|-------------|---------|
| `-v` | Verbose output | `-v` |
| `-vv` | Very verbose (show test names) | `-vv` |
| `-x` | Stop on first failure | `-x` |
| `-s` | Show print statements | `-s` |
| `--lf` | Run last failed tests | `--lf` |
| `--ff` | Run failed first, then rest | `--ff` |
| `-k` | Filter by test name pattern | `-k "test_sync"` |
| `-m` | Run tests with specific marker | `-m "slow"` |
| `-n auto` | Run in parallel (pytest-xdist) | `-n auto` |
| `--cov` | Measure coverage | `--cov=src/specify_cli` |
| `--cov-report` | Coverage report format | `--cov-report=term-missing` |
| `--tb=short` | Short traceback format | `--tb=short` |
| `--tb=line` | One-line traceback | `--tb=line` |
| `--pdb` | Drop into debugger on failure | `--pdb` |

## Output Format

### All Tests Pass
```
======================== test session starts =========================
collected 42 items

tests/unit/test_ggen_ops.py::test_sync_creates_files PASSED    [  2%]
tests/unit/test_ggen_ops.py::test_sync_validates PASSED        [  4%]
tests/unit/test_process.py::test_run_logged PASSED            [  7%]
...
tests/e2e/test_commands_init.py::test_init_creates_dir PASSED [100%]

========================= 42 passed in 2.34s =========================

✅ All tests passed!
- Duration: 2.34s
- Tests: 42 passed
- Coverage: 85%
```

### Test Failures
```
======================== test session starts =========================
collected 42 items

tests/unit/test_ggen_ops.py::test_sync_creates_files FAILED    [  2%]
tests/unit/test_ggen_ops.py::test_sync_validates PASSED        [  4%]
...

============================== FAILURES ==============================
_________________ test_sync_creates_files _________________

def test_sync_creates_files():
    result = ggen_ops.sync_rdf()
>   assert result["files_created"] == ["README.md"]
E   AssertionError: assert ['README.md', 'CHANGELOG.md'] == ['README.md']
E     Left contains one more item: 'CHANGELOG.md'

tests/unit/test_ggen_ops.py:23: AssertionError
========================= short test summary =========================
FAILED tests/unit/test_ggen_ops.py::test_sync_creates_files
====================== 1 failed, 41 passed in 2.45s ==================

❌ 1 test failed

Failure Analysis:
- Test: test_sync_creates_files
- File: tests/unit/test_ggen_ops.py:23
- Cause: Assertion mismatch - expected 1 file, got 2
- Fix: Update test expectation to include CHANGELOG.md
```

### Coverage Report
```
---------- coverage: platform linux, python 3.11.5 -----------
Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
src/specify_cli/ops/ggen_ops.py           45      7    84%   23-25, 42-45
src/specify_cli/runtime/ggen_runtime.py   32      2    94%   67-68
src/specify_cli/core/process.py           28      0   100%
src/specify_cli/core/telemetry.py         41      8    80%   45-52
---------------------------------------------------------------------
TOTAL                                     146     17    88%

Coverage: 88% (Target: 80%+)
Missing Coverage:
- ggen_ops.py:23-25 (error handling)
- ggen_ops.py:42-45 (edge case)
- telemetry.py:45-52 (OTEL unavailable path)
```

## Failure Diagnosis Workflow

### 1. Identify Failure Type

| Type | Indicator | Action |
|------|-----------|--------|
| AssertionError | Expected vs actual mismatch | Check test expectations |
| FileNotFoundError | Missing file/directory | Check path construction |
| ImportError | Missing module | Check dependencies (`uv sync`) |
| CalledProcessError | Subprocess failed | Check command construction |
| TypeError | Type mismatch | Check type hints and conversions |
| AttributeError | Missing attribute | Check object structure |

### 2. Read Failure Context

```bash
# Get full traceback
/run-tests tests/unit/test_failing.py -vv --tb=long

# Read the failing test
Read tests/unit/test_failing.py

# Read the code under test
Read src/specify_cli/ops/module.py
```

### 3. Reproduce and Debug

```bash
# Run single failing test
/run-tests tests/unit/test_failing.py::test_name -vv -s

# Drop into debugger on failure
/run-tests tests/unit/test_failing.py::test_name --pdb
```

### 4. Fix and Verify

```bash
# Fix the issue (edit code or test)
# Re-run the specific test
/run-tests tests/unit/test_failing.py::test_name -v

# Run related tests
/run-tests tests/unit/ -v

# Run full suite
/run-tests
```

## Coverage Targets

### Minimum Requirements
- Overall: 80%+
- Operations layer: 90%+ (pure functions are easy to test)
- Runtime layer: 70%+ (I/O is harder to test)
- Commands layer: 60%+ (CLI integration)

### Coverage Gaps Strategy
```bash
# Identify untested code
/run-tests --cov=src/specify_cli --cov-report=term-missing

# Focus on high-value gaps
# Priority: ops > runtime > commands
```

## Integration

Works with:
- `uv run pytest` - Test runner
- `pytest-cov` - Coverage plugin
- `/debug` - Failure diagnosis
- `/lint` - Pre-test quality checks
- CI/CD - Automated testing

## Performance Targets

- Unit tests: < 1s total
- E2E tests: < 10s total
- Full suite: < 15s total
- Parallel execution: Use `-n auto` for speed

## Common Workflows

### Pre-Commit Testing
```bash
# Fast unit tests only
/run-tests tests/unit/ -v

# Expected: < 1s
```

### Pre-Push Testing
```bash
# Full suite with coverage
/run-tests --cov=src/specify_cli --cov-report=term-missing

# Expected: < 15s, 80%+ coverage
```

### Debug Failing Test
```bash
# Run with verbose output
/run-tests tests/unit/test_failing.py::test_name -vv -s

# Use /debug for systematic diagnosis
/debug "test_name failing with AssertionError"
```

### Coverage Improvement
```bash
# Find gaps
/run-tests --cov=src/specify_cli --cov-report=term-missing

# Write tests for missing lines

# Re-check
/run-tests --cov=src/specify_cli
```

## Notes
- Always run tests before committing
- Unit tests should be fast (< 1s total)
- E2E tests can be slower but should stay under 10s
- 80%+ coverage is required for PR approval
- Use `-x` to stop on first failure for faster debugging
- Use `--lf` to re-run only failed tests
- Generated tests (e2e/test_commands_*.py) should not be edited manually
- All operations layer functions should have 90%+ coverage (they're pure)
- Runtime layer coverage may be lower due to I/O complexity
