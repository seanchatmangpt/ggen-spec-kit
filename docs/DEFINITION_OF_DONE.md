# Definition of Done (DoD)

**Version:** 1.0.0
**Last Updated:** 2025-12-21
**Framework:** DFLSS (Design for Lean Six Sigma)

## Overview

This Definition of Done establishes the mandatory quality gates for all code changes in the spec-kit project. Following DFLSS principles, we target **99.99966% defect-free delivery** (3.4 DPMO - Defects Per Million Opportunities) through systematic verification at each stage.

**Core Principle:** ZERO DEFECTS BEFORE DELIVERY

---

## 1. Code Quality Gates

### 1.1 Type Safety (MANDATORY - 100% Coverage)

**Acceptance Criteria:**
- [ ] **100% type hints** on all functions, methods, and variables
- [ ] All parameters have explicit type annotations
- [ ] Return types are explicitly declared (no implicit `None`)
- [ ] Type aliases used for complex types
- [ ] No `Any` types without documented justification

**Verification Commands:**
```bash
# Must pass with ZERO errors
uv run mypy src/ --strict
uv run mypy tests/ --strict

# Expected output: "Success: no issues found"
```

**Target Metrics:**
- **Defect Rate:** 0 type errors per 1000 lines of code (DPMO: 0)
- **Coverage:** 100% (no untyped functions)

**DFLSS Gate:** STOP if type errors > 0. No exceptions.

---

### 1.2 Code Linting (MANDATORY - Ruff 400+ Rules)

**Acceptance Criteria:**
- [ ] **ALL Ruff rules enforced** (400+ checks)
- [ ] No `# noqa` suppressions without documented justification
- [ ] No `# type: ignore` without documented justification
- [ ] Import ordering follows isort conventions
- [ ] Line length ≤ 100 characters
- [ ] No debug print statements (`T20`)
- [ ] No commented-out code (`ERA`)
- [ ] No relative imports (`TID252`)

**Verification Commands:**
```bash
# Must pass with ZERO violations
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/

# Expected output: "All checks passed!"
```

**Suppression Justification Template:**
```python
# noqa: E501 - Justification: Long URL cannot be split
# type: ignore[attr-defined] - Third-party library missing stubs
```

**Target Metrics:**
- **Defect Rate:** 0 violations per 1000 lines (DPMO: 0)
- **Technical Debt:** 0 suppressions without justification

**DFLSS Gate:** STOP if violations > 0. Fix before proceeding.

---

### 1.3 Security Scanning (MANDATORY - Bandit Clean)

**Acceptance Criteria:**
- [ ] **No security vulnerabilities** detected
- [ ] No hardcoded secrets or credentials
- [ ] No `shell=True` in subprocess calls
- [ ] Path validation on all file operations
- [ ] Temporary files created with 0o600 permissions
- [ ] No SQL injection vectors
- [ ] No insecure random number generation

**Verification Commands:**
```bash
# Must pass with ZERO high/medium severity issues
uv run bandit -r src/ -ll  # Only high/medium severity

# Expected output: "No issues identified."
```

**Target Metrics:**
- **Critical Vulnerabilities:** 0 (DPMO: 0)
- **High Severity:** 0 (DPMO: 0)
- **Medium Severity:** 0 (DPMO: 0)

**DFLSS Gate:** STOP if high/medium severity > 0. No exceptions.

---

### 1.4 Documentation (MANDATORY - All Public APIs)

**Acceptance Criteria:**
- [ ] **NumPy-style docstrings** on all public functions/classes
- [ ] Module-level docstrings present
- [ ] Function docstrings include:
  - Short description (one line)
  - Extended description (if needed)
  - Parameters section with types
  - Returns section with type
  - Raises section (if applicable)
  - Examples section (for complex functions)
- [ ] Type hints match docstring descriptions

**Example:**
```python
def transform_rdf(source: Path, template: str, output: Path) -> dict[str, Any]:
    """Transform RDF specification to code using template.

    Implements the μ transformation pipeline (NORMALIZE → EXTRACT → EMIT).

    Parameters
    ----------
    source : Path
        Path to RDF/Turtle source file
    template : str
        Name of Tera template to use
    output : Path
        Destination path for generated output

    Returns
    -------
    dict[str, Any]
        Transformation metadata including SHA256 receipt

    Raises
    ------
    FileNotFoundError
        If source file or template not found
    ValidationError
        If RDF fails SHACL validation

    Examples
    --------
    >>> transform_rdf(Path("spec.ttl"), "python.tera", Path("out.py"))
    {"status": "success", "receipt": "sha256:abc123..."}
    """
```

**Verification Commands:**
```bash
# Check docstring coverage
uv run pydocstyle src/specify_cli/ --convention=numpy

# Expected output: No errors
```

**Target Metrics:**
- **Public API Coverage:** 100% (DPMO: 0)
- **Docstring Quality:** All sections present

**DFLSS Gate:** STOP if public APIs lack docstrings.

---

## 2. Testing Requirements

### 2.1 Test Coverage (MANDATORY - 80% Minimum)

**Acceptance Criteria:**
- [ ] **Overall coverage ≥ 80%** (current target, increasing to 90%)
- [ ] **Ops layer coverage ≥ 90%** (pure business logic)
- [ ] **Runtime layer coverage ≥ 75%** (I/O operations)
- [ ] **Commands layer coverage ≥ 85%** (CLI interface)
- [ ] Branch coverage enabled (not just line coverage)
- [ ] No untested critical paths

**Verification Commands:**
```bash
# Generate coverage report
uv run pytest --cov=src/specify_cli --cov-report=term-missing --cov-report=html:reports/coverage

# Check coverage threshold
uv run coverage report --fail-under=80

# View detailed HTML report
open reports/coverage/index.html
```

**Target Metrics:**
- **Overall Coverage:** ≥ 80% (increasing to 90% by v1.0.0)
- **Branch Coverage:** ≥ 75%
- **Uncovered Lines:** Documented in `coverage.report` exclude_lines

**DFLSS Gate:** STOP if coverage < 80%. Add tests before proceeding.

---

### 2.2 Unit Tests (MANDATORY - All Ops Layer)

**Acceptance Criteria:**
- [ ] **All ops layer functions have unit tests**
- [ ] Pure functions (no side effects)
- [ ] Fast execution (< 50ms per test)
- [ ] No external dependencies (no I/O, no subprocess)
- [ ] Arrange-Act-Assert pattern
- [ ] Edge cases tested (empty input, null, boundary values)
- [ ] Error paths tested (exceptions, validation errors)

**Test Structure:**
```python
# tests/unit/ops/test_transform.py
import pytest
from specify_cli.ops.transform import validate_rdf_syntax

class TestValidateRdfSyntax:
    """Unit tests for validate_rdf_syntax operation."""

    def test_valid_turtle_syntax(self) -> None:
        """Test valid Turtle syntax passes validation."""
        # Arrange
        content = "@prefix ex: <http://example.org/> . ex:foo a ex:Bar ."

        # Act
        result = validate_rdf_syntax(content, format="turtle")

        # Assert
        assert result["valid"] is True
        assert result["errors"] == []

    def test_invalid_turtle_syntax_raises_error(self) -> None:
        """Test invalid Turtle syntax raises ValidationError."""
        # Arrange
        content = "@prefix ex: <invalid syntax"

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            validate_rdf_syntax(content, format="turtle")

        assert "syntax error" in str(exc_info.value).lower()
```

**Verification Commands:**
```bash
# Run unit tests only
uv run pytest tests/unit/ -m unit -v

# Expected: 100% pass rate
```

**Target Metrics:**
- **Ops Layer Coverage:** ≥ 90%
- **Test Execution Time:** < 5 seconds total
- **Pass Rate:** 100% (0 failures)

**DFLSS Gate:** STOP if ops layer coverage < 90%.

---

### 2.3 Integration Tests (MANDATORY - All Runtime Layer)

**Acceptance Criteria:**
- [ ] **All runtime layer functions have integration tests**
- [ ] Real subprocess execution tested
- [ ] File I/O operations tested
- [ ] HTTP requests tested (with mocking)
- [ ] Temporary file cleanup verified
- [ ] Error handling tested (non-zero exit codes, timeouts)
- [ ] OTEL instrumentation verified

**Test Structure:**
```python
# tests/integration/runtime/test_ggen.py
import pytest
from pathlib import Path
from specify_cli.runtime.ggen import sync_ggen

class TestGgenSync:
    """Integration tests for ggen sync runtime."""

    def test_sync_generates_files(self, tmp_path: Path) -> None:
        """Test ggen sync generates output files."""
        # Arrange
        config_path = tmp_path / "ggen.toml"
        config_path.write_text('[transformation]\nname = "test"')

        # Act
        result = sync_ggen(config_path)

        # Assert
        assert result["status"] == "success"
        assert result["exit_code"] == 0
        assert len(result["generated_files"]) > 0

    def test_sync_fails_on_invalid_config(self, tmp_path: Path) -> None:
        """Test ggen sync fails gracefully on invalid config."""
        # Arrange
        invalid_config = tmp_path / "invalid.toml"
        invalid_config.write_text("invalid toml syntax {{{")

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            sync_ggen(invalid_config)

        assert "invalid configuration" in str(exc_info.value).lower()
```

**Verification Commands:**
```bash
# Run integration tests
uv run pytest tests/integration/ -m integration -v

# Expected: 100% pass rate
```

**Target Metrics:**
- **Runtime Layer Coverage:** ≥ 75%
- **Test Execution Time:** < 30 seconds total
- **Pass Rate:** 100% (0 failures)

**DFLSS Gate:** STOP if runtime layer coverage < 75%.

---

### 2.4 End-to-End Tests (MANDATORY - All CLI Commands)

**Acceptance Criteria:**
- [ ] **All CLI commands have E2E tests**
- [ ] Full command lifecycle tested (invoke → subprocess → output)
- [ ] Help text generation verified
- [ ] Exit codes verified (0 for success, non-zero for error)
- [ ] OTEL spans/traces verified
- [ ] Error messages user-friendly

**Test Structure:**
```python
# tests/e2e/test_commands_ggen.py
import pytest
from typer.testing import CliRunner
from specify_cli import app

class TestGgenCommands:
    """E2E tests for ggen CLI commands."""

    def test_ggen_sync_success(self, tmp_path: Path) -> None:
        """Test ggen sync command completes successfully."""
        # Arrange
        runner = CliRunner()

        # Act
        result = runner.invoke(app, ["ggen", "sync", "--config", str(tmp_path / "ggen.toml")])

        # Assert
        assert result.exit_code == 0
        assert "✓ Sync completed" in result.stdout

    def test_ggen_sync_help(self) -> None:
        """Test ggen sync --help displays usage."""
        # Arrange
        runner = CliRunner()

        # Act
        result = runner.invoke(app, ["ggen", "sync", "--help"])

        # Assert
        assert result.exit_code == 0
        assert "Transform RDF specifications" in result.stdout
```

**Verification Commands:**
```bash
# Run E2E tests
uv run pytest tests/e2e/ -m e2e -v

# Expected: 100% pass rate
```

**Target Metrics:**
- **Commands Layer Coverage:** ≥ 85%
- **CLI Help Coverage:** 100% (all commands have --help)
- **Pass Rate:** 100% (0 failures)

**DFLSS Gate:** STOP if E2E tests fail.

---

### 2.5 Test Quality Metrics

**Acceptance Criteria:**
- [ ] Test-to-code ratio ≥ 1.0 (equal or more test code than production code)
- [ ] No flaky tests (100% deterministic)
- [ ] No test interdependencies (each test runs independently)
- [ ] Fixtures properly scoped (function, class, module, session)
- [ ] Test data managed (no hardcoded paths)

**Verification Commands:**
```bash
# Count lines of code vs test code
tokei src/ tests/

# Run tests in random order (detect interdependencies)
uv run pytest tests/ --random-order

# Run tests in parallel (detect race conditions)
uv run pytest tests/ -n auto
```

**Target Metrics:**
- **Test-to-Code Ratio:** ≥ 1.0
- **Flaky Test Rate:** 0% (DPMO: 0)
- **Test Isolation:** 100%

**DFLSS Gate:** STOP if flaky tests detected.

---

## 3. Architecture Compliance

### 3.1 Three-Tier Separation (MANDATORY)

**Acceptance Criteria:**
- [ ] **Commands layer:** No subprocess, no file I/O, no HTTP
- [ ] **Ops layer:** No side effects, pure business logic
- [ ] **Runtime layer:** All I/O operations use `run_logged()`
- [ ] No circular dependencies between layers
- [ ] No imports from commands/ops in runtime

**Layer Rules:**
```python
# ✅ CORRECT: Commands layer
def ggen_sync_command(config: Path) -> None:
    """CLI command: delegates to ops layer."""
    result = ggen_sync_operation(config)  # ops layer
    display_result(result)  # Rich formatting

# ✅ CORRECT: Ops layer
def ggen_sync_operation(config: Path) -> dict[str, Any]:
    """Pure business logic: no I/O."""
    validated_config = validate_config(config)
    return {"status": "ready", "config": validated_config}

# ✅ CORRECT: Runtime layer
def execute_ggen_sync(config: Path) -> dict[str, Any]:
    """Runtime: subprocess execution."""
    from specify_cli.runtime.process import run_logged
    result = run_logged(["ggen", "sync", "--config", str(config)])
    return {"exit_code": result.returncode, "output": result.stdout}
```

**Verification Commands:**
```bash
# Check for forbidden imports in ops layer
uv run ruff check src/specify_cli/ops/ --select TID252

# Check for subprocess in commands layer
grep -r "subprocess" src/specify_cli/commands/
# Expected: No matches

# Check for subprocess in ops layer
grep -r "subprocess" src/specify_cli/ops/
# Expected: No matches
```

**Target Metrics:**
- **Layer Violation Rate:** 0 (DPMO: 0)
- **Circular Dependencies:** 0

**DFLSS Gate:** STOP if layer violations detected.

---

### 3.2 OpenTelemetry Instrumentation (MANDATORY)

**Acceptance Criteria:**
- [ ] **All operations instrumented** with OTEL spans
- [ ] Span names follow semantic conventions: `<layer>.<operation>`
- [ ] Key attributes attached: `file_path`, `operation`, `status`
- [ ] Error spans tagged with `error=true`
- [ ] Graceful degradation when OTEL unavailable
- [ ] No OTEL errors in production

**Instrumentation Pattern:**
```python
from specify_cli.core.telemetry import span, timed

@timed
def transform_rdf(source: Path, template: str) -> dict[str, Any]:
    """RDF transformation with OTEL instrumentation."""
    with span("ops.transform_rdf", source=str(source), template=template):
        # Business logic here
        result = perform_transformation(source, template)
        return result
```

**Verification Commands:**
```bash
# Run with OTEL enabled
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
uv run specify ggen sync

# Check for OTEL spans in logs
grep "span_id" /tmp/specify-otel.log

# Expected: Spans for all operations
```

**Target Metrics:**
- **Instrumentation Coverage:** 100% of critical paths
- **OTEL Error Rate:** 0% (graceful degradation)

**DFLSS Gate:** STOP if OTEL errors in production.

---

### 3.3 Dependency Injection (RECOMMENDED)

**Acceptance Criteria:**
- [ ] External dependencies injected (not hardcoded)
- [ ] Testable without mocking (where possible)
- [ ] Configuration passed as parameters
- [ ] No global state mutations

**Pattern:**
```python
# ✅ CORRECT: Dependency injection
def process_file(file_path: Path, processor: Callable[[str], str]) -> str:
    """Process file with injected processor."""
    content = file_path.read_text()
    return processor(content)

# ❌ WRONG: Hardcoded dependency
def process_file(file_path: Path) -> str:
    """Process file with hardcoded processor."""
    content = file_path.read_text()
    return hardcoded_processor(content)  # Cannot test without mocking
```

**DFLSS Gate:** Review required if hardcoded dependencies.

---

## 4. RDF-First Development (Constitutional Equation)

### 4.1 Spec-Driven Compliance (MANDATORY)

**Acceptance Criteria:**
- [ ] **RDF is source of truth** for CLI commands, docs, tests
- [ ] Generated files have corresponding TTL source
- [ ] No manual edits to generated files
- [ ] Cryptographic receipts match current files
- [ ] Transformation is idempotent: `μ ∘ μ = μ`

**Verification Commands:**
```bash
# Validate RDF syntax
specify ggen validate-rdf ontology/cli-commands.ttl

# Verify receipts match
specify ggen verify

# Check idempotence
specify ggen check-idempotence

# Expected: All checks pass
```

**Target Metrics:**
- **Constitutional Violations:** 0 (DPMO: 0)
- **Receipt Mismatches:** 0 (DPMO: 0)

**DFLSS Gate:** STOP if constitutional violations detected.

---

### 4.2 Generated Files (MANDATORY)

**Acceptance Criteria:**
- [ ] All generated files committed together with TTL source
- [ ] Generated files marked with header comment
- [ ] No manual edits to generated files
- [ ] CI verifies generation is up-to-date

**Generated File Header:**
```python
# AUTO-GENERATED FILE - DO NOT EDIT MANUALLY
# Source: ontology/cli-commands.ttl
# Generated: 2025-12-21T10:30:00Z
# Receipt: sha256:abc123def456...
```

**DFLSS Gate:** STOP if generated files edited manually.

---

## 5. Documentation

### 5.1 Updated Documentation (MANDATORY)

**Acceptance Criteria:**
- [ ] **CHANGELOG.md updated** with semantic versioning
- [ ] API documentation current
- [ ] Usage examples included
- [ ] Migration guides (if breaking changes)
- [ ] README.md updated (if new features)

**CHANGELOG Format (Keep a Changelog):**
```markdown
## [0.1.0] - 2025-12-21

### Added
- New `ggen verify` command for receipt validation (#42)
- OTEL instrumentation on all critical paths (#45)

### Changed
- Improved error messages for invalid RDF syntax (#43)

### Fixed
- Fixed subprocess timeout handling (#44)

### Security
- Added Bandit security scanning (#46)
```

**Verification Commands:**
```bash
# Check CHANGELOG has unreleased section
grep -A 5 "## \[Unreleased\]" CHANGELOG.md

# Expected: Current changes documented
```

**Target Metrics:**
- **Documentation Coverage:** 100% of public APIs
- **CHANGELOG Compliance:** 100%

**DFLSS Gate:** STOP if CHANGELOG not updated.

---

### 5.2 Usage Examples (RECOMMENDED)

**Acceptance Criteria:**
- [ ] CLI examples in README.md
- [ ] Code examples in docstrings
- [ ] Quickstart guide updated
- [ ] Troubleshooting section current

**DFLSS Gate:** Review required if no examples.

---

## 6. DFLSS Metrics & Process Capability

### 6.1 Defect Tracking

**Six Sigma Level:** Target 6σ (3.4 DPMO)

| Metric | Target | Current | Action |
|--------|--------|---------|--------|
| Type Errors | 0 DPMO | 0 DPMO | ✅ Maintain |
| Lint Violations | 0 DPMO | 0 DPMO | ✅ Maintain |
| Security Issues | 0 DPMO | 0 DPMO | ✅ Maintain |
| Test Failures | 0 DPMO | 0 DPMO | ✅ Maintain |
| Coverage Gaps | < 100 DPMO | TBD | 📊 Measure |
| Production Bugs | < 3.4 DPMO | TBD | 📊 Measure |

**DPMO Calculation:**
```
DPMO = (Defects / Opportunities) × 1,000,000

Example:
- 5 bugs in 100,000 lines of code
- DPMO = (5 / 100,000) × 1,000,000 = 50 DPMO
- Sigma Level: ~5σ (needs improvement to 6σ)
```

---

### 6.2 Cycle Time Tracking

**Acceptance Criteria:**
- [ ] Commit-to-deploy cycle time tracked
- [ ] Test execution time monitored
- [ ] Code review time measured
- [ ] Mean Time to Recovery (MTTR) tracked

**Target Metrics:**
| Metric | Target | Current |
|--------|--------|---------|
| Build Time | < 2 min | TBD |
| Test Execution | < 30 sec | TBD |
| Code Review | < 4 hours | TBD |
| MTTR | < 1 hour | TBD |

---

### 6.3 Process Capability Indices

**Cp & Cpk (Process Capability):**
```
Cp = (USL - LSL) / (6σ)
Cpk = min((USL - μ) / 3σ, (μ - LSL) / 3σ)

Target: Cp ≥ 1.33, Cpk ≥ 1.33 (capable process)
```

**Example - Test Coverage:**
```
- LSL (Lower Spec Limit) = 80%
- USL (Upper Spec Limit) = 100%
- μ (Mean) = 85%
- σ (Std Dev) = 3%

Cp = (100 - 80) / (6 × 3) = 1.11 (needs improvement)
Cpk = min((100 - 85) / 9, (85 - 80) / 9) = 0.56 (not capable)

Action: Increase mean coverage to 90% to achieve Cpk ≥ 1.33
```

---

## 7. Completion Checklist (MANDATORY)

### Pre-Commit Checklist

Before committing, verify ALL items:

**Code Quality:**
- [ ] `uv run mypy src/ tests/` → ZERO errors
- [ ] `uv run ruff check src/ tests/` → ZERO violations
- [ ] `uv run ruff format --check src/ tests/` → No formatting needed
- [ ] `uv run bandit -r src/ -ll` → ZERO high/medium issues

**Testing:**
- [ ] `uv run pytest tests/unit/` → 100% pass rate
- [ ] `uv run pytest tests/integration/` → 100% pass rate
- [ ] `uv run pytest tests/e2e/` → 100% pass rate
- [ ] `uv run pytest --cov=src/specify_cli --cov-report=term` → Coverage ≥ 80%

**Architecture:**
- [ ] Three-tier separation verified (no layer violations)
- [ ] OTEL instrumentation on new operations
- [ ] No circular dependencies

**RDF-First:**
- [ ] Generated files match TTL source
- [ ] `specify ggen verify` → All receipts match
- [ ] `specify ggen check-idempotence` → Idempotent

**Documentation:**
- [ ] CHANGELOG.md updated
- [ ] Docstrings on all new public APIs
- [ ] README.md updated (if needed)

---

### Pre-Push Checklist

Before pushing to remote:

**Integration:**
- [ ] All tests pass on clean checkout
- [ ] No merge conflicts
- [ ] Branch up-to-date with main

**Review:**
- [ ] Self-review completed (diff review)
- [ ] No debug statements left in code
- [ ] No commented-out code
- [ ] Commit message follows convention

---

### Pre-Release Checklist

Before creating a release:

**Quality Gates:**
- [ ] All Pre-Commit checks pass
- [ ] All Pre-Push checks pass
- [ ] Performance benchmarks run (no regressions)
- [ ] Security scan clean (Bandit, dependencies)

**Documentation:**
- [ ] CHANGELOG.md finalized
- [ ] Version bumped (semantic versioning)
- [ ] Migration guide (if breaking changes)
- [ ] Release notes drafted

**Deployment:**
- [ ] Staging deployment successful
- [ ] Smoke tests pass in staging
- [ ] Rollback plan documented

---

## 8. Continuous Improvement

### 8.1 Retrospectives

**Frequency:** After each sprint/release

**Review:**
- Defects escaped to production
- Test effectiveness (defects caught vs. missed)
- Coverage trends
- Cycle time trends
- Action items from previous retrospective

---

### 8.2 Quality Metrics Dashboard

**Track Weekly:**
- Code coverage percentage
- Defect density (bugs per 1000 LOC)
- Test execution time
- Build success rate
- MTTR (Mean Time to Recovery)

**Track Monthly:**
- DPMO (Defects Per Million Opportunities)
- Sigma level achievement
- Process capability (Cp/Cpk)
- Technical debt ratio

---

## 9. Escalation & Exceptions

### 9.1 Exception Process

**STOP CONDITIONS (No exceptions allowed):**
- Type errors (mypy)
- Lint violations (ruff)
- Security issues (Bandit high/medium)
- Test failures
- Coverage < 80%

**REVIEW REQUIRED (May proceed with justification):**
- Coverage 75-80% (must have plan to reach 80%)
- Suppression comments (must document why)
- Skipped tests (must have ticket to fix)

**Justification Template:**
```markdown
## Exception Request

**Rule:** [Which DoD rule is being bypassed]
**Justification:** [Why this exception is necessary]
**Risk Assessment:** [What could go wrong]
**Mitigation Plan:** [How risk is minimized]
**Remediation Ticket:** [Link to ticket for future fix]
**Approver:** [Lead engineer approval required]
```

---

### 9.2 Non-Negotiable Gates

**ZERO TOLERANCE (No exceptions, no workarounds):**
1. Security vulnerabilities (high/medium)
2. Hardcoded secrets
3. Test failures in main branch
4. Constitutional violations (RDF source mismatch)
5. Production bugs without hotfix process

**Violation Response:**
1. Revert commit immediately
2. Root cause analysis (5 Whys)
3. Corrective action plan
4. Preventive measures
5. Retrospective review

---

## 10. Summary

### The Golden Rule

**ZERO DEFECTS BEFORE DELIVERY**

Every commit must pass ALL mandatory gates:
- ✅ 100% type coverage (mypy strict)
- ✅ 0 lint violations (ruff 400+ rules)
- ✅ 0 security issues (Bandit high/medium)
- ✅ 100% test pass rate
- ✅ ≥ 80% code coverage
- ✅ Three-tier architecture compliance
- ✅ OTEL instrumentation on critical paths
- ✅ RDF-first constitutional compliance
- ✅ Documentation updated

**NO partial deliveries. NO shortcuts. NO exceptions.**

---

## Appendix A: Quick Reference Commands

```bash
# Full verification pipeline (run before commit)
uv run mypy src/ tests/ && \
uv run ruff check src/ tests/ && \
uv run ruff format --check src/ tests/ && \
uv run bandit -r src/ -ll && \
uv run pytest tests/ --cov=src/specify_cli --cov-report=term && \
specify ggen verify && \
specify ggen check-idempotence

# Expected: ALL commands pass with ZERO errors
```

---

## Appendix B: DFLSS Terminology

| Term | Definition |
|------|------------|
| **DPMO** | Defects Per Million Opportunities |
| **Sigma (σ)** | Standard deviation; 6σ = 3.4 DPMO |
| **Cp** | Process Capability (variation vs. spec range) |
| **Cpk** | Process Capability (centered + variation) |
| **LSL/USL** | Lower/Upper Specification Limit |
| **MTTR** | Mean Time to Recovery |
| **DoD** | Definition of Done |

---

**End of Definition of Done v1.0.0**
