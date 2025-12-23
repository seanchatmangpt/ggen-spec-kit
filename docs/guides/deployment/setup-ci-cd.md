# How-to: Setup CI/CD Pipeline

**Goal:** Automate testing and deployment with GitHub Actions
**Time:** 30-40 minutes | **Level:** Advanced

## GitHub Actions Workflow

**File:** `.github/workflows/test.yml`

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          pip install uv
          uv sync --all-groups
      - name: Run tests
        run: uv run pytest tests/ --cov=src
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Lint and Type Checking

**File:** `.github/workflows/lint.yml`

```yaml
name: Quality

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          pip install uv
          uv sync --all-groups
      - name: Lint with ruff
        run: uv run ruff check src/
      - name: Type check with mypy
        run: uv run mypy src/
      - name: Format check
        run: uv run ruff format --check src/
```

## Build and Release

**File:** `.github/workflows/release.yml`

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Build distribution
        run: |
          pip install uv build
          python -m build
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
```

## Workflows

1. **On Push:** Run tests and lint
2. **On PR:** Check tests, coverage, types
3. **On Tag:** Build and publish to PyPI

## Configuration

Set up secrets in GitHub:
- `CODECOV_TOKEN` - for codecov
- `PYPI_API_TOKEN` - for publishing

## Best Practices

✅ Test on multiple Python versions
✅ Check coverage threshold
✅ Lint and type check
✅ Automate releases
✅ Fast feedback (< 5 minutes)

See: `.github/workflows/` directory
