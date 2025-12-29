# Debug Issue

Systematically debug errors, failures, and unexpected behavior using structured analysis.

## Description
Applies systematic debugging methodology to diagnose and fix issues while maintaining architecture integrity and preventing regressions.

## Usage
```bash
/debug ERROR_OR_DESCRIPTION
```

## Arguments
- `ERROR_OR_DESCRIPTION` (required) - Error message, stack trace, or description of unexpected behavior

## Examples
```bash
# Debug test failure
/debug "TestGgenSync.test_sync_creates_files failing with FileNotFoundError"

# Debug runtime error
/debug "subprocess.CalledProcessError: Command 'ggen sync' returned non-zero exit status 1"

# Debug unexpected behavior
/debug "ggen sync not regenerating CHANGELOG.md after TTL edit"

# Debug type error
/debug "mypy error: Argument 1 has incompatible type Path; expected str"

# Debug performance issue
/debug "specify init command taking 3+ seconds to start"
```

## Systematic Debugging Process

### 1. Reproduce

**Goal**: Confirm and isolate the issue

```bash
# Get exact environment
uv --version
ggen --version
python --version

# Reproduce the error
uv run pytest tests/path/to/test.py::test_name -v

# Or reproduce CLI issue
specify command --option value
```

**Output**:
- Exact error message and stack trace
- Environment details
- Reproducible steps

### 2. Isolate

**Goal**: Find the failing component and layer

```bash
# Check git history for recent changes
git log --oneline -10

# Find relevant files
grep -r "error_pattern" src/

# Identify the layer
# Commands: src/specify_cli/commands/
# Operations: src/specify_cli/ops/
# Runtime: src/specify_cli/runtime/
```

**Questions**:
- Which layer is failing? (commands/ops/runtime)
- Is it generated code or manual implementation?
- Are there recent changes to this component?

### 3. Analyze

**Goal**: Understand the code path and context

```bash
# Read the failing code
# Use Read tool for relevant files

# Check test coverage
uv run pytest --cov=src/specify_cli --cov-report=term-missing

# Look for similar patterns
grep -r "similar_pattern" tests/
```

**Investigation**:
- Read source code of failing component
- Examine test cases (passing and failing)
- Check for edge cases and error handling
- Review related issues in git history

### 4. Diagnose

**Goal**: Form and verify hypothesis about root cause

**Common Root Causes**:

| Symptom | Likely Cause | Check |
|---------|--------------|-------|
| FileNotFoundError | Path handling, CWD issues | Path construction, working directory |
| CalledProcessError | Subprocess command format | Command list vs string, shell=True |
| Import errors | Circular imports, missing deps | Import graph, uv sync status |
| Type errors | Incorrect type hints | Mypy output, actual vs expected types |
| Test failures | Stale generated code | RDF-Python divergence, ggen sync needed |
| Performance issues | Missing caching, inefficient I/O | OTEL traces, profiling |

**Verification**:
```bash
# Test hypothesis with minimal reproduction
# Create isolated test case
# Check edge cases
```

### 5. Fix

**Goal**: Implement minimal, safe fix that maintains architecture

**Fix Patterns**:

#### Commands Layer Fix
```python
# Before (violates layer boundary)
def command():
    subprocess.run(["tool", "arg"])  # ❌ Side effect in command

# After (delegates to ops)
def command():
    result = ops.perform_operation()  # ✅ Delegates to ops
    display_result(result)
```

#### Operations Layer Fix
```python
# Before (side effect in ops)
def operation():
    file.write_text("data")  # ❌ I/O in ops layer
    return "done"

# After (pure function)
def operation() -> str:
    return "data"  # ✅ Returns data, runtime handles I/O
```

#### Runtime Layer Fix
```python
# Before (unsafe subprocess)
def run_tool():
    subprocess.run(f"tool {arg}", shell=True)  # ❌ shell=True

# After (safe subprocess)
def run_tool(arg: str):
    run_logged(["tool", arg])  # ✅ List-based, logged, safe
```

#### RDF-First Fix
```bash
# Before (manual edit of generated file)
# Editing src/specify_cli/commands/validate_cmd.py  # ❌

# After (edit RDF source)
# Edit ontology/cli-commands.ttl                     # ✅
ggen sync  # Regenerate Python
```

**Considerations**:
- Does fix maintain layer boundaries?
- Are there side effects on other components?
- Does fix address root cause or just symptoms?
- Is fix minimal and focused?

### 6. Verify

**Goal**: Confirm fix and prevent regression

```bash
# Run specific failing test
uv run pytest tests/path/to/test.py::test_name -v

# Run related tests
uv run pytest tests/path/to/ -v

# Run full test suite
uv run pytest tests/ -v

# Check for regressions
uv run pytest --cov=src/specify_cli --cov-report=term-missing

# Lint and type check
uv run ruff check src/
uv run mypy src/
```

**Regression Test**:
```python
# Add test to prevent future occurrence
def test_issue_123_regression():
    """Regression test for issue #123: FileNotFoundError in ggen sync.

    Ensures ggen sync handles missing directories gracefully.
    """
    # Test the fixed behavior
    assert expected_behavior()
```

## Output Format

Provides structured debugging report:

### Issue Summary
- Error type and message
- Affected component/layer
- Reproduction steps

### Root Cause Analysis
- Code location (file:line)
- Layer violation or architectural issue
- Underlying cause (not just symptoms)

### Fix Implementation
```python
# Changed files with diffs
# Layer: operations
# File: src/specify_cli/ops/ggen_ops.py

- old_code()
+ new_code()  # Explanation
```

### Verification Results
```bash
# Test execution results
pytest tests/ -v
======================== 15 passed in 2.3s ========================

# No new type errors
mypy src/
Success: no issues found

# Coverage maintained/improved
Coverage: 85% (+2%)
```

### Regression Prevention
- New test case added
- Documentation updated
- Architectural guideline reinforced

## Integration

Works with:
- `uv run pytest` - Test execution
- `git log` - Change history
- `uv run mypy` - Type checking
- `uv run ruff` - Linting
- OTEL traces - Performance analysis
- `/lint` - Code quality checks
- `/run-tests` - Test suite execution

## Common Debug Scenarios

### Test Failure
```bash
/debug "test_ggen_sync_creates_files failing"
# → Check if ggen sync was run
# → Verify RDF source matches expectations
# → Check file permissions
```

### Import Error
```bash
/debug "ImportError: cannot import name 'run_logged'"
# → Check circular imports
# → Verify uv sync completed
# → Check layer boundaries
```

### Subprocess Error
```bash
/debug "CalledProcessError in runtime layer"
# → Verify command list format
# → Check shell=True usage
# → Validate run_logged usage
```

### Type Error
```bash
/debug "mypy error in validate_ops.py"
# → Read mypy output carefully
# → Check type hints accuracy
# → Verify return types match
```

## Notes
- Always maintain three-tier architecture during fixes
- Never edit generated files (commands/*.py)
- Add regression tests for all fixes
- Document architectural decisions
- Consider using OTEL traces for performance issues
- Use parallel tool calls when investigating (Read multiple files at once)
