# How-to: Run Tests

**Goal:** Execute your test suite and monitor coverage
**Time:** 15-20 minutes | **Level:** Intermediate

---

## Quick Start

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/unit/test_hello_ops.py -v

# Show coverage
uv run pytest tests/ --cov=src/specify_cli --cov-report=term-missing
```

---

## Running Tests

### Run All Tests
```bash
uv run pytest tests/ -v
```

Output shows:
```
tests/unit/test_hello_ops.py::TestHello::test_returns_greeting PASSED
tests/e2e/test_commands_hello.py::test_hello_command PASSED
===== 2 passed in 0.15s =====
```

### Run Specific Test File
```bash
uv run pytest tests/unit/test_hello_ops.py -v
```

### Run Specific Test Method
```bash
uv run pytest tests/unit/test_hello_ops.py::TestHello::test_returns_greeting -v
```

### Run with Print Output Visible
```bash
uv run pytest tests/ -v -s
# Shows any print() statements during tests
```

### Stop on First Failure
```bash
uv run pytest tests/ -x
# Useful for debugging - stops at first error
```

---

## Coverage Reporting

### Check Coverage
```bash
uv run pytest tests/ --cov=src/specify_cli
```

Output:
```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
src/specify_cli/__init__.py                 1      0   100%
src/specify_cli/ops/hello.py               10      2    80%
src/specify_cli/commands/hello.py           5      0   100%
-----------------------------------------------------------
TOTAL                                      16      2    88%
```

### Coverage with Missing Lines
```bash
uv run pytest tests/ --cov=src/specify_cli --cov-report=term-missing
```

Shows which lines aren't covered:
```
src/specify_cli/ops/hello.py                10      2    80%   (15-16)
# Lines 15-16 are not covered
```

### Coverage Targets

Spec Kit aims for:
- ✅ Unit tests: >80% coverage
- ✅ Critical paths: 100% coverage
- ✅ Total project: >80% coverage

---

## Test Organization

```
tests/
├── unit/              # Unit tests for functions
│   ├── test_hello_ops.py
│   ├── test_build_ops.py
│   └── conftest.py    # Shared fixtures
│
└── e2e/               # End-to-end tests
    ├── test_commands_hello.py
    ├── test_commands_build.py
    └── conftest.py
```

---

## Test Patterns

### Pattern: Unit Test
```python
def test_operation_returns_result():
    """Test operation returns expected result."""
    result = operation("input")
    assert "expected" in result
```

### Pattern: Parameterized Test
```python
@pytest.mark.parametrize("input_val,expected", [
    ("alice", "Hello, alice"),
    ("bob", "Hello, bob"),
])
def test_operation_with_names(input_val, expected):
    result = operation(input_val)
    assert result == expected
```

### Pattern: Exception Testing
```python
def test_operation_raises_on_empty():
    """Test operation raises when given empty string."""
    with pytest.raises(ValueError):
        operation("")
```

### Pattern: Fixture Usage
```python
@pytest.fixture
def sample_data():
    return {"name": "alice", "age": 30}

def test_with_fixture(sample_data):
    result = process(sample_data)
    assert result is not None
```

---

## Common Commands

| Command | Purpose |
|---------|---------|
| `pytest tests/` | Run all tests silently |
| `pytest tests/ -v` | Run all tests with verbose output |
| `pytest tests/ -x` | Stop on first failure |
| `pytest tests/ -k "hello"` | Run only tests matching pattern |
| `pytest tests/ --tb=short` | Shorter error messages |
| `pytest tests/ --collect-only` | List all tests without running |
| `pytest tests/ --cov` | Show coverage report |

---

## Debugging Tests

### Print Debugging
```bash
# Show print() statements
uv run pytest tests/unit/test_hello_ops.py -v -s

# In your test:
def test_something():
    result = operation("input")
    print(f"Result: {result}")  # This shows with -s
    assert result == expected
```

### Drop into Debugger
```python
def test_something():
    result = operation("input")
    import pdb; pdb.set_trace()  # Pauses execution here
    assert result == expected
```

### Run One Test at a Time
```bash
# Get list of all tests
uv run pytest tests/ --collect-only -q

# Run specific test
uv run pytest tests/unit/test_hello_ops.py::test_specific_thing -v
```

---

## Continuous Testing

### Watch Mode (requires pytest-watch)
```bash
# Install first:
pip install pytest-watch

# Run tests on file changes:
ptw tests/
```

### Before Commit
```bash
# Run full test suite with coverage
uv run pytest tests/ --cov=src/specify_cli

# Fix lint issues
uv run ruff check src/

# Type checking
uv run mypy src/
```

---

## Test Verification Checklist

When adding a command:

```
[ ] Wrote unit tests for operations logic
[ ] Wrote E2E tests for CLI command
[ ] Achieved >80% coverage
[ ] All tests pass: uv run pytest tests/ -v
[ ] Coverage looks good: uv run pytest --cov
[ ] No lint errors: uv run ruff check
[ ] Type checking passes: uv run mypy src/
[ ] Can run command manually without errors
```

---

## Troubleshooting

**Test imports fail**
```bash
# Ensure dependencies are installed
uv sync

# Check Python path
export PYTHONPATH=src/:$PYTHONPATH
```

**Coverage is too low**
- Add more test cases
- Test edge cases (empty input, None, large values)
- Test error paths (exceptions)

**Tests fail with CLI error**
- Check imports in test file
- Verify mock objects if using mocks
- Run with `-s` to see print output

**pytest not found**
```bash
# Install dev dependencies
uv sync --group dev
```

---

## See Also

- [Tutorial 4: Your First Test](../../tutorials/04-first-test.md)
- [Pattern Examples](../../examples/ai-learning/test-patterns.py)
- [Reference: Quality Metrics](../../reference/quality-metrics.md)
