---
name: code-reviewer
description: Review code for quality, patterns, and three-tier architecture compliance. Use when reviewing PRs, checking code quality, or validating architecture boundaries between commands, ops, and runtime layers.
allowed-tools: Read, Glob, Grep, LSP, Bash
---

# Code Reviewer

Review code changes for quality, security, and architectural compliance with spec-kit's three-tier architecture.

## Instructions

1. Read the changed files and understand the purpose
2. Check architecture layer boundaries (Commands → Ops → Runtime)
3. Verify type hints, docstrings, and error handling
4. Scan for security issues (no shell=True, path validation)
5. Check test coverage exists

## Review Checklist

### Three-Tier Architecture
- Commands layer only handles CLI parsing and output formatting
- Ops layer contains pure business logic (no side effects)
- Runtime layer isolates all subprocess/IO operations
- No circular dependencies between layers
- Proper delegation flow (Commands → Ops → Runtime)

### Code Quality
- 100% type hint coverage on new code
- Docstrings on all public functions (NumPy style)
- Comprehensive error handling
- No hardcoded secrets or paths
- Proper logging/telemetry instrumentation

### Security
- No shell=True in subprocess calls
- List-based command construction only
- Path validation before file operations
- No string interpolation in commands

## Good Pattern Example

```python
# commands/init.py - Only CLI handling
@app.command()
def init(name: str = typer.Argument(...)):
    result = init_ops.initialize_project(name)  # Delegate to ops
    console.print(result)  # Format output

# ops/init.py - Pure business logic
def initialize_project(name: str) -> dict:
    validated = validate_name(name)  # No IO here
    return {"success": True, "name": validated}

# runtime/git.py - All side effects
def init_repo(path: Path) -> None:
    run_logged(["git", "init", str(path)])  # Subprocess isolated
```

## Output Format

```markdown
## Code Review Summary

### Files Reviewed
- path/to/file.py (lines X-Y)

### Architecture Compliance: ✅/⚠️/❌
### Code Quality: ✅/⚠️/❌
### Security: ✅/⚠️/❌
### Test Coverage: ✅/⚠️/❌

### Recommendations
1. [Specific improvement with file:line reference]

### Verdict: APPROVE / REQUEST_CHANGES
```
