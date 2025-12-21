# Coverage Gap Analysis - ggen-spec-kit v1.0

**Date**: 2025-12-20
**Baseline**: 26% overall coverage
**Target**: 80%+ coverage
**Gap**: 54 percentage points

## Overview

Comprehensive analysis of test coverage gaps by layer, module, and test type to inform prioritized testing strategy for reaching 80%+ coverage target.

## What's Tested Well (60%+ coverage)

### Excellent Coverage (90%+ coverage)

1. **`ops/init.py`** - 92%
   - Comprehensive unit tests for project initialization
   - All validation paths tested
   - Error handling covered
   - AI assistant selection logic tested

2. **`ops/check.py`** - 89%
   - Tool availability checking thoroughly tested
   - Version extraction logic covered
   - Environment info collection tested

3. **`core/semconv.py`** - 96%
   - OpenTelemetry semantic conventions fully tested
   - All constant definitions verified

4. **`core/process.py`** - 95%
   - Subprocess execution logic well-tested
   - Error handling paths covered
   - Security features verified

### Good Coverage (60-89% coverage)

1. **`commands/check.py`** - 63%
   - CLI interface tested via integration tests
   - JSON output format verified
   - Verbose mode tested

2. **`runtime/git.py`** - 63%
   - Git repository operations tested
   - Init and commit operations covered
   - Dry-run mode verified

3. **`core/shell.py`** - 66%
   - Interactive shell features tested
   - User input handling covered

## What's Missing (< 60% coverage)

### Critical Gaps (0-20% coverage)

#### Zero Coverage (0%)

1. **`dspy_commands.py`** (311 statements)
   - **Impact**: HIGH - Entire DSpy integration untested
   - **Priority**: HIGH
   - **Reason**: New feature, no tests written yet
   - **Risk**: DSpy commands could fail in production
   - **Tests Needed**:
     - DSpy initialization
     - Model configuration
     - Prompt execution
     - Error handling

2. **`spiff/runtime.py`** (170 statements)
   - **Impact**: HIGH - Spiff workflow execution untested
   - **Priority**: HIGH
   - **Reason**: Runtime operations isolated, no integration tests
   - **Risk**: BPMN workflow execution could fail
   - **Tests Needed**:
     - Workflow file operations
     - BPMN execution
     - Task handling
     - State management

#### Very Low Coverage (1-10%)

3. **`spiff_automation.py`** - 2% (146 statements)
   - **Impact**: MEDIUM - Spiff automation features untested
   - **Priority**: MEDIUM
   - **Reason**: Complex automation logic, minimal tests
   - **Tests Needed**:
     - Workflow automation
     - Task scheduling
     - Event handling

4. **`ops/process_mining.py`** - 5% (144 statements)
   - **Impact**: MEDIUM - PM4Py integration untested
   - **Priority**: MEDIUM
   - **Reason**: Optional feature, low test priority
   - **Tests Needed**:
     - Event log parsing
     - Process discovery
     - Conformance checking

5. **`utils/templates.py`** - 5% (202 statements)
   - **Impact**: MEDIUM - Template rendering untested
   - **Priority**: MEDIUM
   - **Reason**: Complex Jinja2 integration
   - **Tests Needed**:
     - Template loading
     - Variable substitution
     - Error handling

6. **`runtime/tools.py`** - 6% (77 statements)
   - **Impact**: MEDIUM - Tool detection untested
   - **Priority**: HIGH (quick win)
   - **Reason**: Small module, easy to test
   - **Tests Needed**:
     - Tool version extraction
     - Availability checking

7. **`core/github.py`** - 9% (136 statements)
   - **Impact**: LOW - GitHub integration optional
   - **Priority**: LOW
   - **Reason**: Requires GitHub API mocking
   - **Tests Needed**:
     - API authentication
     - Repository operations
     - Error handling

8. **`commands/spiff.py`** - 10% (216 statements)
   - **Impact**: HIGH - Spiff CLI commands untested
   - **Priority**: HIGH
   - **Reason**: Complex command set, no integration tests
   - **Tests Needed**:
     - Command parsing
     - Workflow execution
     - Output formatting

#### Low Coverage (11-20%)

9. **`runtime/template.py`** - 11% (151 statements)
10. **`runtime/ggen.py`** - 13% (94 statements)
11. **`runtime/github.py`** - 13% (154 statements)
12. **`utils/progress.py`** - 12% (125 statements)
13. **`core/git.py`** - 15% (38 statements)
14. **`utils/commands.py`** - 18% (34 statements)
15. **`core/cache.py`** - 19% (89 statements)

### Moderate Gaps (21-59% coverage)

16. **`core/config.py`** - 21% (81 statements)
17. **`ops/version.py`** - 30% (81 statements)
18. **`spiff/__init__.py`** - 32% (22 statements)
19. **`core/error_handling.py`** - 36% (157 statements)
20. **`spiff/ops/otel_validation.py`** - 42% (159 statements)
21. **`commands/__init__.py`** - 42% (12 statements)
22. **`core/telemetry.py`** - 50% (125 statements)
23. **`core/instrumentation.py`** - 54% (96 statements)
24. **`commands/version.py`** - 58% (60 statements)
25. **`spiff/ops/external_projects.py`** - 58% (210 statements)
26. **`commands/init.py`** - 59% (91 statements)

## Test Organization by Layer and File

### Commands Layer

```
tests/integration/test_commands_init.py (18 tests)
├── TestInitCommand (7 tests) ✓
├── TestCheckCommand (5 tests) ✓
├── TestVersionCommand (3 tests) ✓
└── TestMainApp (3 tests) ✓

MISSING:
└── tests/integration/test_commands_spiff.py (0 tests) ✗
    ├── TestSpiffValidate
    ├── TestSpiffRun
    └── TestSpiffWorkflow
```

### Operations Layer

```
tests/unit/test_ops_init.py (22 tests) ✓
tests/unit/test_ops_check.py (18 tests) ✓

MISSING:
├── tests/unit/test_ops_version.py (0 tests) ✗
├── tests/unit/test_ops_process_mining.py (0 tests) ✗
└── tests/unit/test_ops_dspy.py (0 tests) ✗
```

### Runtime Layer

```
tests/integration/test_runtime_git.py (13 tests) ✓

MISSING:
├── tests/integration/test_runtime_ggen.py (0 tests) ✗
├── tests/integration/test_runtime_github.py (0 tests) ✗
├── tests/integration/test_runtime_template.py (0 tests) ✗
└── tests/integration/test_runtime_tools.py (0 tests) ✗
```

### Core Layer

```
tests/unit/test_core_process.py (24 tests) ✓
tests/unit/test_core_telemetry.py (17 tests) ✓

MISSING:
├── tests/unit/test_core_config.py (0 tests) ✗
├── tests/unit/test_core_cache.py (0 tests) ✗
├── tests/unit/test_core_error_handling.py (0 tests) ✗
├── tests/unit/test_core_github.py (0 tests) ✗
├── tests/unit/test_core_git.py (0 tests) ✗
└── tests/unit/test_core_shell.py (0 tests) ✗
```

### Spiff Layer

```
tests/test_spiff_otel_validation.py (12 tests) ✓
tests/test_spiff_external_projects.py (15 tests) ✓

MISSING:
├── tests/test_spiff_runtime.py (0 tests) ✗
└── tests/test_spiff_automation.py (0 tests) ✗
```

### DSpy Layer

```
MISSING:
└── tests/test_dspy_commands.py (0 tests) ✗
```

## Strategy for Reaching 80%+

### Phase 1: Quick Wins (26% → 40%)

**Target**: Add ~700 covered statements
**Effort**: LOW
**Timeline**: Week 1

1. **Core utilities** (200 statements)
   - `core/config.py`: 21% → 80%
   - `core/cache.py`: 19% → 80%
   - `core/git.py`: 15% → 80%

2. **Runtime tools** (300 statements)
   - `runtime/tools.py`: 6% → 80%
   - `runtime/ggen.py`: 13% → 60%
   - `runtime/template.py`: 11% → 50%

3. **Operations layer** (200 statements)
   - `ops/version.py`: 30% → 80%
   - `commands/__init__.py`: 42% → 80%

### Phase 2: Runtime Coverage (40% → 60%)

**Target**: Add ~1000 covered statements
**Effort**: MEDIUM
**Timeline**: Week 2

1. **Integration tests for runtime** (600 statements)
   - `runtime/github.py`: 13% → 60%
   - `runtime/template.py`: 50% → 80%
   - `runtime/ggen.py`: 60% → 80%

2. **Spiff operations** (300 statements)
   - `spiff/ops/otel_validation.py`: 42% → 80%
   - `spiff/__init__.py`: 32% → 80%

3. **Error handling** (100 statements)
   - `core/error_handling.py`: 36% → 70%

### Phase 3: Advanced Features (60% → 80%)

**Target**: Add ~1000 covered statements
**Effort**: HIGH
**Timeline**: Week 3-4

1. **DSpy commands** (250 statements)
   - `dspy_commands.py`: 0% → 80%

2. **Spiff automation** (250 statements)
   - `spiff_automation.py`: 2% → 80%
   - `spiff/runtime.py`: 0% → 80%

3. **Commands layer** (200 statements)
   - `commands/spiff.py`: 10% → 80%

4. **Process mining** (100 statements)
   - `ops/process_mining.py`: 5% → 70%

5. **Templates and utils** (200 statements)
   - `utils/templates.py`: 5% → 70%
   - `utils/progress.py`: 12% → 60%

## Test Type Recommendations

### Unit Tests (Fast, Isolated)

**Add for:**
- All `ops/` modules (pure logic)
- All `core/` utilities
- Data validation
- Business logic
- Type conversions

**Pattern:**
```python
def test_function_name_scenario():
    # Arrange
    input_data = {...}
    # Act
    result = function(input_data)
    # Assert
    assert result == expected
```

### Integration Tests (I/O, Subprocess)

**Add for:**
- All `runtime/` modules
- All `commands/` modules
- File operations
- Subprocess execution
- API calls

**Pattern:**
```python
def test_integration_scenario(tmp_path):
    # Setup real filesystem
    project_dir = tmp_path / "project"
    # Execute with real I/O
    result = execute_operation(project_dir)
    # Verify filesystem state
    assert (project_dir / "expected.txt").exists()
```

### End-to-End Tests (Full Workflow)

**Add for:**
- CLI command sequences
- Multi-step workflows
- Real-world scenarios
- Performance benchmarks

**Pattern:**
```python
def test_e2e_workflow(tmp_path):
    # Run full CLI workflow
    subprocess.run(["specify", "init", "myproject"])
    subprocess.run(["specify", "check"])
    # Verify end state
    assert validate_project_structure()
```

## Coverage Enforcement Strategy

### Pre-commit Hooks

```yaml
# Minimum coverage for new code: 80%
- id: coverage-check
  args: [--cov-fail-under=50]  # Start at 50%, increase gradually
```

### CI/CD Quality Gates

1. **PR checks**:
   - Minimum 50% coverage (baseline)
   - No coverage decrease allowed
   - All new code must have tests

2. **Release checks**:
   - Minimum 80% coverage
   - All critical paths tested
   - No uncovered error paths

### Coverage Metrics Dashboard

Track weekly:
- Overall coverage percentage
- Coverage by layer
- New vs. old code coverage
- Critical path coverage

## Risk Assessment

### High-Risk Uncovered Code

1. **`dspy_commands.py`** (0%)
   - Impact: Users can't use DSpy features
   - Mitigation: Add comprehensive test suite

2. **`spiff/runtime.py`** (0%)
   - Impact: Workflow execution could fail silently
   - Mitigation: Add workflow integration tests

3. **`commands/spiff.py`** (10%)
   - Impact: CLI commands could fail
   - Mitigation: Add command integration tests

### Medium-Risk Uncovered Code

1. **`ops/process_mining.py`** (5%)
   - Impact: PM4Py features unusable
   - Mitigation: Optional feature, document requirements

2. **`runtime/ggen.py`** (13%)
   - Impact: RDF transformations could fail
   - Mitigation: Add ggen integration tests

3. **`core/error_handling.py`** (36%)
   - Impact: Errors not handled gracefully
   - Mitigation: Add error path tests

### Low-Risk Uncovered Code

1. **`core/github.py`** (9%)
   - Impact: GitHub integration optional
   - Mitigation: Document as experimental

2. **`utils/progress.py`** (12%)
   - Impact: UI/UX issue, not functionality
   - Mitigation: Manual testing sufficient

## Next Steps

### Week 1 (Foundation)
- [ ] Fix failing test: `test_detect_python_project_with_pyproject`
- [ ] Add unit tests for `core/config.py`, `core/cache.py`, `core/git.py`
- [ ] Add unit tests for `ops/version.py`
- [ ] Add integration tests for `runtime/tools.py`
- [ ] Target: 40% coverage

### Week 2 (Runtime)
- [ ] Add integration tests for `runtime/ggen.py`, `runtime/github.py`, `runtime/template.py`
- [ ] Expand `spiff/ops/otel_validation.py` tests
- [ ] Add error handling tests
- [ ] Target: 60% coverage

### Week 3-4 (Advanced)
- [ ] Create DSpy test suite
- [ ] Create spiff automation tests
- [ ] Add command integration tests
- [ ] Create E2E test suite
- [ ] Target: 80% coverage

---

**Baseline**: 26% (2025-12-20)
**Target**: 80%+ (end of Week 2)
**Strategy**: Phased approach (Quick Wins → Runtime → Advanced)
**Enforcement**: Pre-commit hooks + CI/CD gates
