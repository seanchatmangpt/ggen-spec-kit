---
paths:
  - "tests/**/*.py"
---

# Test Rules

## Structure
```
tests/
├── unit/           # Fast, isolated unit tests
├── integration/    # Tests with real dependencies
├── e2e/           # End-to-end CLI tests
├── conftest.py    # Shared fixtures
└── fixtures/      # Test data files
```

## Naming
- Test files: `test_<module>.py`
- Test functions: `test_<scenario>_<expected_result>`
- Test classes: `Test<ClassName>`

## Pattern
```python
import pytest
from specify_cli.ops import my_ops

class TestMyOperation:
    """Tests for my_ops module."""

    def test_valid_input_returns_success(self) -> None:
        """Test that valid input produces success result."""
        # Arrange
        input_data = {"key": "value"}

        # Act
        result = my_ops.process(input_data)

        # Assert
        assert result["status"] == "success"
        assert "data" in result

    def test_invalid_input_raises_value_error(self) -> None:
        """Test that invalid input raises ValueError."""
        with pytest.raises(ValueError, match="required_field"):
            my_ops.process({})
```

## Fixtures
```python
@pytest.fixture
def sample_data() -> dict:
    """Provide sample test data."""
    return {"key": "value"}

@pytest.fixture
def temp_file(tmp_path: Path) -> Path:
    """Create a temporary test file."""
    file_path = tmp_path / "test.txt"
    file_path.write_text("test content")
    return file_path
```

## Coverage
- Minimum: 80% line coverage
- Run with: `uv run pytest --cov=src/specify_cli`
- Focus on ops layer (highest value)

## Mocking
- Mock runtime layer for unit tests
- Use real runtime for integration tests
- Never mock ops layer
