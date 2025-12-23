# How-to: Setup Test Infrastructure

**Goal:** Initialize and configure test suite
**Time:** 15-20 minutes | **Level:** Intermediate

## Project Structure

```
tests/
├── __init__.py
├── conftest.py           # Shared fixtures
├── unit/
│   ├── __init__.py
│   ├── test_ops_*.py     # Unit tests
│   └── conftest.py
└── e2e/
    ├── __init__.py
    ├── test_commands_*.py # E2E tests
    └── conftest.py
```

## Setup pytest

**pyproject.toml:**
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = """
    -v
    --strict-markers
    --cov=src/specify_cli
    --cov-report=term-missing
    --cov-report=html
"""

[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError"
]
```

## Create Fixtures

**tests/conftest.py:**
```python
import pytest
from click.testing import CliRunner

@pytest.fixture
def cli_runner():
    return CliRunner()

@pytest.fixture
def sample_data():
    return {"name": "test", "value": 42}
```

## Run Tests

```bash
# All tests
uv run pytest tests/

# Specific file
uv run pytest tests/unit/test_hello_ops.py -v

# With coverage
uv run pytest tests/ --cov --cov-report=html
```

## GitHub Actions

```yaml
- name: Run tests
  run: uv run pytest tests/ --cov
```

## See Also
- [How-to: Run Tests](./run-tests.md)
- [How-to: Debug Tests](./debug-tests.md)
