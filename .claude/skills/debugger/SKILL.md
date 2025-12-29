---
name: debugger
description: Debug issues systematically using traces, logs, and code analysis. Use when diagnosing errors, tracing execution flow, or fixing runtime issues.
allowed-tools: Read, Glob, Grep, Bash, LSP, Edit
---

# Debugger

Systematically diagnose and fix issues using traces, logs, and code analysis.

## Trigger Conditions

- Test failures requiring diagnosis
- Runtime errors in CLI execution
- Import/attribute errors
- OTEL trace analysis

## Key Capabilities

- Test failure diagnosis
- Code execution tracing via LSP
- Root cause identification
- Layer-specific error handling

## Integration

**ggen v5.0.2**: Debugs code generation failures during ggen sync
**Architecture**: Traces through Commands → Ops → Runtime call chain

## Instructions

1. Understand and reproduce the problem
2. Trace execution to identify failure points
3. Find the underlying root cause
4. Apply targeted fixes
5. Verify the issue is resolved

## Debugging Methodology

### Phase 1: Reproduce
```bash
uv run pytest tests/path/to/failing_test.py -v --tb=long 2>&1
git log --oneline -10
git diff HEAD~1
```

### Phase 2: Trace Execution
Use LSP for code navigation:
- Go to Definition
- Find References
- Call Hierarchy

### Phase 3: Isolate
Check files in order:
- `src/specify_cli/commands/` - CLI handling
- `src/specify_cli/ops/` - Business logic
- `src/specify_cli/runtime/` - Subprocess/IO
- `src/specify_cli/core/` - Utilities

### Phase 4: Fix and Verify
1. Apply fix to root cause
2. Run related tests
3. Run full test suite
4. Check for regressions

## Error Patterns

### ImportError
```python
# Check import paths, fix circular deps
```

### AttributeError
```python
# Check object type, add null checks
if result and hasattr(result, 'data'):
    return result.data
```

### SubprocessError
```python
# Check command exists, handle errors
try:
    result = run_logged(["command", "arg"])
except subprocess.CalledProcessError as e:
    raise CommandError(f"Failed: {e.stderr}")
```

## Debugging Commands

```bash
# Python debugging
uv run python -c "from specify_cli import x; print(x)"

# Verbose pytest
uv run pytest -v --tb=long --capture=no

# Type checking
uv run mypy src/specify_cli/
```

## Output Format

```markdown
## Debug Report

### Issue
[Description]

### Root Cause
[The actual problem]

### Fix Applied
- **File**: `path/to/file.py:line`
- **Change**: [Description]

### Verification
- Issue no longer reproduces: ✅
- Tests pass: ✅
```
