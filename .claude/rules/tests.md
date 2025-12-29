---
paths:
  - "tests/**/*.py"
---

# Test Rules

Unit (fast, isolated) → Integration (real deps) → E2E (CLI). 80%+ coverage on ops.

## Structure
```
tests/
├── unit/           # Fast, isolated ops tests
├── integration/    # Real dependencies
├── e2e/           # CLI end-to-end
├── conftest.py    # Shared fixtures
└── fixtures/      # Test data
```

## Naming
- Files: `test_<module>.py`
- Functions: `test_<scenario>_<expected>()`
- Classes: `Test<ClassName>`

## DO
- ✅ Test ops layer (pure logic)
- ✅ Use Arrange/Act/Assert pattern
- ✅ Test error cases and edge cases
- ✅ Use fixtures for setup
- ✅ Aim for 80%+ coverage
- ✅ Mock runtime for unit tests

## DON'T
- ❌ Test implementation details
- ❌ Use global state
- ❌ Mock ops layer functions
- ❌ Slow tests in unit suite
- ❌ Hardcoded test data
- ❌ Unnamed test fixtures

## Pattern
```python
class TestMyOps:
    """Tests for my_ops."""

    def test_valid_input_returns_success(self) -> None:
        """Test valid input produces success."""
        # Arrange
        input_data = {"key": "value"}

        # Act
        result = my_ops.process(input_data)

        # Assert
        assert result["status"] == "success"

    def test_invalid_input_raises_error(self) -> None:
        """Test invalid input raises ValueError."""
        with pytest.raises(ValueError):
            my_ops.process({})
```

## Fixtures
```python
@pytest.fixture
def sample_data() -> dict:
    """Provide sample test data."""
    return {"key": "value"}
```

## Coverage
- Minimum: 80% line coverage
- Focus: ops layer (pure logic)
- Run: `uv run pytest --cov=src/specify_cli`
