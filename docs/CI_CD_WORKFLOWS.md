# CI/CD Workflows Documentation

## Overview

ggen-spec-kit enforces **Lean Six Sigma quality standards** through automated GitHub Actions workflows. Every push and pull request triggers comprehensive quality gates to ensure zero-defect code delivery.

## Workflows

### 1. Quality Gates (`quality.yml`)

**Trigger:** Push to `main`, Pull Requests to `main`

**Jobs:** 3 parallel jobs

#### Job 1: Quality Checks
- **Ruff Lint**: 400+ code quality rules
- **Ruff Format**: Code formatting validation
- **MyPy**: Type checking (gradual strict mode)
- **Bandit**: Security vulnerability scanning

**Runtime:** ~3-5 minutes

```bash
# Run locally before pushing
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run mypy src/ tests/
uv run bandit -r src/ -ll
```

#### Job 2: Test Suite
- **Matrix Testing**: Python 3.11, 3.12
- **Coverage Enforcement**: Minimum 50% (increasing to 80%)
- **Unit + Integration Tests**: Full test suite
- **Coverage Reports**: XML, HTML, Term output
- **Codecov Integration**: Automated coverage tracking

**Runtime:** ~5-10 minutes per Python version

```bash
# Run locally
uv run pytest tests/ \
  --cov=src/specify_cli \
  --cov-report=term-missing \
  --cov-fail-under=50 \
  -v
```

#### Job 3: Integration Tests
- **Docker Support**: Testcontainers-based tests
- **Integration Markers**: Tests marked with `@pytest.mark.integration`
- **Full System Tests**: End-to-end validation

**Runtime:** ~5-15 minutes

```bash
# Run locally
uv run pytest tests/integration/ -m integration -v
```

#### Job 4: Quality Summary
- **Status Aggregation**: All jobs must pass
- **Fail Fast**: Any job failure blocks merge
- **Clear Reporting**: Detailed pass/fail status

### 2. Markdown Linting (`lint.yml`)

**Trigger:** Push to `main`, Pull Requests

**Jobs:** 1 job

- **markdownlint-cli2**: Validates README.md and docs/
- **Rules:** Consistent formatting, proper headers, link validation

**Runtime:** ~1-2 minutes

```bash
# Run locally (if installed)
npx markdownlint-cli2 "**/*.md"
```

### 3. Documentation (`docs.yml`)

**Trigger:** Push to `main`

Builds and deploys project documentation.

### 4. Release (`release.yml`)

**Trigger:** Tag creation (`v*`)

Automated release process for PyPI publishing.

## Coverage Configuration

### Current Thresholds (v0.0.25)
- **Minimum Coverage:** 50%
- **Target Coverage:** 80%+
- **Codecov Precision:** 2 decimal places
- **Rounding:** Down

### Coverage Targets (v1.0.0)
- **Minimum Coverage:** 80%
- **Target Coverage:** 90%+
- **Branch Coverage:** Enabled
- **Comprehensive Reports:** HTML, XML, Terminal

## Artifacts

All workflows upload artifacts for debugging and analysis:

### Quality Job
- `bandit-results`: JSON report of security findings (30 days retention)

### Test Job
- `test-results-3.11`: JUnit XML, Coverage reports for Python 3.11 (30 days)
- `test-results-3.12`: JUnit XML, Coverage reports for Python 3.12 (30 days)

### Integration Job
- `integration-results`: JUnit XML for integration tests (30 days)

## Local Development Workflow

### Before Committing

```bash
# 1. Run all quality checks
uv run ruff check src/ tests/
uv run ruff format src/ tests/
uv run mypy src/ tests/

# 2. Run tests with coverage
uv run pytest tests/ --cov=src/specify_cli --cov-report=term-missing

# 3. Security scan
uv run bandit -r src/ -ll

# 4. Pre-commit hooks (if installed)
pre-commit run --all-files
```

### Pre-commit Hooks

Install hooks for automatic validation:

```bash
# Install pre-commit hooks (when available)
pre-commit install
```

Hooks will run automatically on `git commit`:
- Ruff linting
- Ruff formatting
- Type checking (fast)
- Security scanning

## Debugging Failed Workflows

### Quality Checks Failed

```bash
# Download artifacts from GitHub Actions
# View Bandit report: reports/bandit.json

# Fix locally
uv run ruff check src/ tests/ --fix
uv run ruff format src/ tests/
uv run mypy src/ --show-error-codes
```

### Tests Failed

```bash
# Download test artifacts
# View JUnit XML: reports/junit.xml
# View coverage: reports/coverage/index.html

# Run failed test locally
uv run pytest tests/path/to/test_file.py::test_function -v
```

### Integration Tests Failed

```bash
# Ensure Docker is running
docker info

# Run integration tests locally
uv run pytest tests/integration/ -m integration -v --tb=long
```

## Codecov Integration

### Coverage Reporting

Codecov automatically receives coverage reports on every push:

- **Project Coverage:** Overall codebase coverage
- **Patch Coverage:** Coverage of changed lines in PR
- **Changes Coverage:** Impact of changes on overall coverage

### Coverage Comments

Pull requests receive automated coverage comments:
- Coverage change percentage
- Files with coverage changes
- Uncovered lines in diff

### Configuration

See `codecov.yml` for detailed configuration:
- Coverage precision: 2 decimal places
- Round down coverage percentages
- Project status checks enabled
- Patch coverage minimum: 50%

## Quality Gates Checklist

Before merge, ALL of these must pass:

- [ ] Ruff lint: 0 violations
- [ ] Ruff format: All files formatted
- [ ] MyPy: 0 type errors
- [ ] Bandit: 0 high/medium security issues
- [ ] Tests: 100% passing
- [ ] Coverage: >= 50% (increasing to 80%)
- [ ] Integration: All Docker tests passing
- [ ] Markdown: All docs properly formatted

## Performance Optimizations

### Parallel Jobs
All jobs run in parallel for maximum speed:
- Quality checks: ~5 minutes
- Tests (both Python versions): ~10 minutes (parallel)
- Integration: ~15 minutes

**Total CI time:** ~15 minutes (not 30+ minutes if sequential)

### Dependency Caching
- `uv` cache enabled via `astral-sh/setup-uv@v5`
- Cache key: `uv.lock` content hash
- Typical cache hit: 30-60 seconds faster

### Matrix Strategy
- `fail-fast: false`: All Python versions tested even if one fails
- Early feedback on version-specific issues

## Troubleshooting

### Workflow Not Triggering

**Check:**
- Branch name matches trigger (main)
- PR target branch is `main`
- Workflow file is valid YAML

### Codecov Upload Failed

**Common causes:**
- Missing `CODECOV_TOKEN` secret (public repos don't need it)
- Coverage report not generated
- Network issues (non-blocking: `fail_ci_if_error: false`)

### Bandit False Positives

**Options:**
1. Add `# nosec` comment with justification
2. Configure in `pyproject.toml` (planned)
3. Update Bandit baseline (planned)

## Future Enhancements (v1.0+)

- [ ] Pre-commit hook automation
- [ ] Strict MyPy mode enforcement
- [ ] 80%+ coverage requirement
- [ ] Performance benchmarking in CI
- [ ] Security scanning with multiple tools
- [ ] Dependency vulnerability scanning (Dependabot/Safety)
- [ ] SAST/DAST scanning
- [ ] Docker image scanning

## Support

**Documentation:** See project README.md
**Issues:** https://github.com/seanchatmangpt/ggen-spec-kit/issues
**Workflow Logs:** GitHub Actions tab in repository

---

**Remember:** Quality gates exist to maintain **Lean Six Sigma standards**. Every check has a purpose. Don't skip or bypass them - fix the root cause.
