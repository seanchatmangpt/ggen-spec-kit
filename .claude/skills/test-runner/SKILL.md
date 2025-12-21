---
name: test-runner
description: Run tests, analyze failures, and fix issues systematically. Use when running pytest, diagnosing test failures, checking coverage, or fixing broken tests.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, LSP
---

# Test Runner

Run tests, diagnose failures, and implement fixes for the spec-kit test suite.

## Instructions

1. Run tests with appropriate pytest options
2. Analyze output to identify root causes
3. Implement fixes for failing tests
4. Verify 80%+ code coverage

## Test Commands

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=src/specify_cli --cov-report=term-missing

# Run specific test
uv run pytest tests/unit/test_ops_init.py::test_function -v

# Run with verbose output
uv run pytest tests/ -v --tb=long
```

## Test Organization

```
tests/
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests (fast, isolated)
│   ├── test_core_process.py
│   ├── test_ops_init.py
│   └── test_ops_check.py
├── integration/             # Integration tests (real IO)
│   ├── test_runtime_git.py
│   └── test_commands_init.py
└── e2e/                     # End-to-end tests
    └── test_cli.py
```

## Diagnosis Process

1. **Run Tests**: `uv run pytest tests/ -v 2>&1 | head -100`
2. **Identify Pattern**: ImportError, AssertionError, AttributeError, etc.
3. **Read Code**: Test file, source file, conftest.py
4. **Implement Fix**: Fix root cause, update mocks
5. **Verify**: Run failing test again

## Common Fixes

### Mock Path Issues
```python
# ❌ Wrong: Mocking where defined
@patch('specify_cli.runtime.github.fetch_release')

# ✅ Right: Mock where imported
@patch('specify_cli.ops.init.github.fetch_release')
```

## Output Format

```markdown
## Test Run Summary

### Execution
- Total: X, Passed: X, Failed: X, Duration: X.XXs

### Coverage
- Overall: XX%

### Failures (if any)
1. `test_file.py::test_name` - [Root cause and fix]

### Fixes Applied
1. [File:line - Description]

### Verification
- All tests passing: ✅/❌
- Coverage target met: ✅/❌
```
