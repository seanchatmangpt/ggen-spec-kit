# Testing Context

## Active When
Working with files in `tests/` or running test commands.

## Test Structure

```
tests/
├── unit/           # Fast, isolated unit tests
├── integration/    # Tests with real dependencies
├── e2e/           # End-to-end CLI tests
├── conftest.py    # Shared fixtures
└── fixtures/      # Test data files
```

## Running Tests

```bash
# All tests
uv run pytest tests/ -v

# With coverage
uv run pytest --cov=src/specify_cli tests/

# Specific test file
uv run pytest tests/unit/test_ops.py -v

# Specific test function
uv run pytest tests/unit/test_ops.py::test_function_name -v

# Stop on first failure
uv run pytest tests/ -x

# With debugging
uv run pytest tests/ --pdb
```

## Test Patterns

### Unit Test (ops layer)
```python
def test_operation_returns_expected_result():
    # Arrange
    input_data = {"key": "value"}

    # Act
    result = operation(input_data)

    # Assert
    assert result["status"] == "success"
```

### Mocking Runtime
```python
from unittest.mock import patch

def test_with_mocked_runtime():
    with patch("specify_cli.runtime.module.function") as mock:
        mock.return_value = {"result": "mocked"}
        result = operation()
        assert result["result"] == "mocked"
```

### CLI Test
```python
from typer.testing import CliRunner
from specify_cli.cli import app

runner = CliRunner()

def test_cli_command():
    result = runner.invoke(app, ["command", "arg"])
    assert result.exit_code == 0
```

## Coverage Goals
- Minimum: 80% line coverage
- Focus on ops layer (highest value)
- E2E tests for critical paths
