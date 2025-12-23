# Reference: Quality Metrics & Targets

Quality standards and performance targets for Spec Kit.

## Test Coverage

**Target:** >80% code coverage

**Measurement:**
```bash
uv run pytest tests/ --cov=src/specify_cli --cov-report=term-missing
```

**Acceptance:**
- Unit test coverage: >80%
- Critical paths: 100%
- Total project: >80%

## Code Quality

**Linting:** No errors
```bash
uv run ruff check src/
```

**Type Checking:** No errors
```bash
uv run mypy src/
```

**Formatting:** Consistent
```bash
uv run ruff format src/
```

## Performance Targets

| Operation | Target | Actual |
|-----------|--------|--------|
| Command startup | < 500ms | ~300ms ✓ |
| Simple operation | < 100ms | ~50ms ✓ |
| ggen sync | < 5s | ~2s ✓ |
| Memory usage | < 100MB | ~50MB ✓ |

## Documentation

**Target:** All public APIs documented

**Standard:** NumPy docstring style
```python
def operation(arg: str) -> str:
    """Brief description.

    Longer description if needed.

    Parameters
    ----------
    arg : str
        Description of arg

    Returns
    -------
    str
        What it returns

    Raises
    ------
    ValueError
        When it raises
    """
```

## Security

**Requirements:**
- ✓ No hardcoded secrets
- ✓ No SQL injection
- ✓ No command injection
- ✓ Path validation
- ✓ Temp files: 0o600 permissions

## Verification

Run before commit:
```bash
# Tests
uv run pytest tests/ -v

# Coverage
uv run pytest tests/ --cov

# Lint
uv run ruff check src/

# Type check
uv run mypy src/

# Format
uv run ruff format --check src/
```

All must pass ✓
