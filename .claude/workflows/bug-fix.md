# Bug Fix Workflow

## Overview
Systematic workflow for diagnosing and fixing bugs.

## Phases

### Phase 1: Reproduce
```yaml
mode: investigation
tools: [Read, Bash]
output: Reproducible test case
```

Steps:
1. Understand the reported issue
2. Create minimal reproduction
3. Write a failing test that demonstrates the bug
4. Document reproduction steps

### Phase 2: Diagnose
```yaml
mode: investigation
tools: [Read, Grep, Glob]
output: Root cause identification
```

Steps:
1. Trace execution path
2. Identify the layer (commands/ops/runtime)
3. Find the exact code causing the issue
4. Understand why it fails

### Phase 3: Fix
```yaml
mode: implementation
tools: [Edit]
output: Corrected code
```

Steps:
1. Implement minimal fix
2. Ensure fix is in correct layer
3. Avoid introducing new issues
4. Consider edge cases

### Phase 4: Verify
```yaml
mode: verification
tools: [Bash]
output: All tests passing
```

Steps:
1. Run the failing test (should pass now)
2. Run full test suite
3. Run lint and type checks
4. Manual verification if needed

### Phase 5: Document
```yaml
mode: implementation
tools: [Edit]
output: Updated documentation
```

Steps:
1. Update changelog (via RDF if applicable)
2. Add comments if logic is non-obvious
3. Update tests if behavior changed

## Debugging Tools

```bash
# Run specific test with verbose output
uv run pytest tests/path/to/test.py -v -s

# Run with debugging
uv run pytest tests/path/to/test.py --pdb

# Check coverage for specific file
uv run pytest --cov=src/specify_cli/ops/file.py tests/
```

## Common Bug Patterns

### Layer Violation
- Symptom: Import error or side effect in wrong layer
- Fix: Move code to appropriate layer

### Missing Validation
- Symptom: Unexpected input causes crash
- Fix: Add input validation in ops layer

### Subprocess Error
- Symptom: Command execution fails
- Fix: Check command construction, ensure list-based

### Type Error
- Symptom: Type mismatch at runtime
- Fix: Add proper type hints and validation
