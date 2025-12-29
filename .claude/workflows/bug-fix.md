# Bug Fix Workflow

## Process

### 1. Reproduce Issue
**Agent/Skill**: Debugger
**Tools**: Read, Bash (pytest)
**Steps**:
- Understand reported issue details
- Write failing test that reproduces bug
- Document steps to trigger issue
- Confirm test fails

**Success**: Have a failing test that demonstrates the bug

---

### 2. Diagnose Root Cause
**Agent/Skill**: Debugger
**Tools**: Read, Grep, Glob
**Steps**:
1. Trace execution path from test
2. Identify affected layer (commands/ops/runtime)
3. Locate exact code causing failure
4. Analyze why it fails

**Success**: Clear understanding of root cause and location

---

### 3. Implement Fix
**Agent/Skill**: Code Reviewer
**Tools**: Edit
**Steps**:
- Apply minimal, focused fix
- Ensure fix is in correct layer
- Add edge case handling
- Avoid unrelated changes

**Success**: Fix is minimal and addresses root cause

---

### 4. Verify Fix
**Agent/Skill**: Test Runner
**Tools**: Bash
**Steps**:
1. Run failing test (should pass now)
2. Run full test suite
3. Run `uv run ruff check src/`
4. Run `uv run mypy src/`

**Success**: Original test passes, all other tests still pass, no lint/type errors

---

### 5. Document & Commit
**Agent/Skill**: Code Reviewer
**Tools**: Edit (memory/changelog.ttl)
**Steps**:
- Update changelog via RDF (memory/changelog.ttl)
- Add inline comments if logic is non-obvious
- Run `ggen sync` if RDF was modified

**Success**: Documentation updated, ready to commit

---

## Quick Debug Commands

```bash
# Run specific test with output
uv run pytest tests/path/to/test.py -v -s

# Run with debugger
uv run pytest tests/path/to/test.py --pdb

# Check coverage on specific file
uv run pytest --cov=src/specify_cli/ops/file.py tests/
```
