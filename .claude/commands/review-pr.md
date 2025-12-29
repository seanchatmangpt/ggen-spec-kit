# Review Pull Request

Comprehensive PR review for code quality, architecture compliance, security, and best practices.

## Description
Performs structured code review using GitHub CLI, checking for architectural violations, security issues, test coverage, and RDF-first compliance.

## Usage
```bash
/review-pr PR_NUMBER
```

## Arguments
- `PR_NUMBER` (required) - Pull request number to review

## Examples
```bash
# Review PR #42
/review-pr 42

# Review with specific focus
/review-pr 15  # Then ask: "Focus on security"
```

## What This Command Does

### 1. Fetch PR Details (Parallel)

```bash
# Execute in parallel for speed
gh pr view PR_NUMBER --json title,body,author,additions,deletions,files,labels
gh pr diff PR_NUMBER
gh pr checks PR_NUMBER
```

### 2. Review Checklist

#### Code Quality
- ✅ Type hints present and accurate on all functions
- ✅ Docstrings on public APIs (NumPy style)
- ✅ No code smells or anti-patterns
- ✅ Follows PEP 8 style (via ruff)
- ✅ No unused imports or variables
- ✅ Appropriate error handling

#### Architecture Compliance (Three-Tier)
- ✅ **Commands layer** (`commands/`):
  - Only parses arguments and formats output
  - Delegates immediately to ops layer
  - NO subprocess, file I/O, or HTTP
- ✅ **Operations layer** (`ops/`):
  - Pure business logic only
  - Returns structured data (dicts)
  - NO subprocess, file I/O, or HTTP
- ✅ **Runtime layer** (`runtime/`):
  - All side effects isolated here
  - Uses `run_logged()` for subprocess
  - Handles all file I/O and HTTP
  - Does NOT import from commands/ops

#### Security
- ✅ No hardcoded secrets or credentials
- ✅ No `shell=True` in subprocess calls
- ✅ Proper input validation on user input
- ✅ Path validation before file operations
- ✅ Temporary files with 0o600 permissions
- ✅ No SQL injection vectors
- ✅ Dependencies are pinned

#### Testing
- ✅ Adequate test coverage (80%+ target)
- ✅ Tests for edge cases
- ✅ Tests follow naming conventions (`test_*.py`, `Test*`)
- ✅ No skipped tests without good reason
- ✅ Tests are deterministic (no random failures)
- ✅ Mock external dependencies appropriately

#### RDF-First Compliance
- ✅ Generated files NOT manually edited
- ✅ RDF source matches generated code
- ✅ If command added, TTL source included
- ✅ `ggen sync` was run after TTL changes
- ✅ Both RDF and generated files committed together

#### Documentation
- ✅ Changelog entry for user-facing changes
- ✅ README updated if behavior changed
- ✅ Inline comments for complex logic
- ✅ Commit messages are clear

### 3. Automated Checks

```bash
# Run in parallel
uv run ruff check [changed_files]
uv run mypy [changed_files]
uv run pytest tests/ -v --cov=[changed_modules]
```

## Review Process

### Phase 1: Overview (Parallel Fetch)
```bash
# Get PR metadata
gh pr view PR_NUMBER --json title,body,additions,deletions,files

# Get diff
gh pr diff PR_NUMBER

# Get CI status
gh pr checks PR_NUMBER
```

### Phase 2: File-by-File Review

For each changed file:

1. **Identify Layer**
   - `commands/` → CLI interface
   - `ops/` → Business logic
   - `runtime/` → Side effects
   - `tests/` → Test code

2. **Check Layer Rules**
   ```bash
   # Search for violations
   grep -n "subprocess\|open\|httpx\|requests" commands/*.py
   grep -n "subprocess\|open\|httpx\|requests" ops/*.py
   ```

3. **Review Logic**
   - Read changed functions
   - Check type hints
   - Verify error handling
   - Look for edge cases

### Phase 3: Testing Review

```bash
# Check test coverage of changes
uv run pytest --cov=src/specify_cli --cov-report=term-missing

# Run specific tests for changed modules
uv run pytest tests/unit/test_[module].py -v
```

### Phase 4: RDF-First Verification

```bash
# If TTL files changed, verify sync
git diff --name-only | grep "\.ttl$"

# Check if generated files also changed
git diff --name-only | grep "commands/.*\.py$"

# Verify they were generated together
git log --oneline -1
```

## Output Format

### Review Summary

```markdown
## PR Review: #42 - Add validation command

**Author**: @username
**Changes**: +234 -15 lines across 8 files
**Status**: ⚠️ Request Changes

### Summary
Adds new RDF validation command with SHACL support. Good architecture compliance but needs test coverage improvements.

### Issues Found

#### 🔴 Critical (Must Fix)
1. **Security**: `ops/validate_ops.py:23` - No input validation on file path
   ```python
   # Line 23
   - def validate_file(path: str):
   + def validate_file(path: Path):
   +     if not path.exists():
   +         raise FileNotFoundError(f"File not found: {path}")
   ```

#### 🟡 Major (Should Fix)
1. **Testing**: Missing edge case tests for malformed TTL files
   - Add `tests/unit/test_validate_ops_malformed.py`
   - Test cases: empty file, invalid syntax, missing prefixes

2. **Type Hints**: `runtime/rdf_runtime.py:45` - Missing return type
   ```python
   - def run_shacl(data):
   + def run_shacl(data: str) -> dict[str, Any]:
   ```

#### 🔵 Minor (Consider)
1. **Documentation**: Add docstring to `validate_file()`
2. **Performance**: Consider caching SHACL shapes parsing

### Architecture Compliance ✅
- Commands layer: Clean, delegates to ops ✓
- Operations layer: Pure functions ✓
- Runtime layer: All I/O isolated ✓
- No layer violations detected ✓

### Security Review ✅ (with fixes)
- ✅ No shell=True usage
- ✅ No hardcoded secrets
- ⚠️ Needs path validation (see Critical #1)
- ✅ subprocess uses run_logged()

### Test Coverage: 75% → Target: 80%+
```
src/specify_cli/ops/validate_ops.py     75%   Missing lines: 45-48, 62-65
src/specify_cli/runtime/rdf_runtime.py  80%   Missing lines: 89-91
```

### RDF-First Compliance ✅
- ✅ TTL source added: `ontology/cli-commands.ttl`
- ✅ Generated file: `commands/validate_cmd.py`
- ✅ Both committed together
- ✅ ggen sync was run

### Recommendations
1. Add path validation (critical security issue)
2. Increase test coverage to 80%+ with edge cases
3. Add type hints to all functions
4. Consider adding integration test with real SHACL file
5. Update changelog entry

### Approval Status
**⚠️ REQUEST CHANGES**

Needs critical security fix and improved test coverage before merging.
```

## GitHub CLI Commands

### Useful gh Commands
```bash
# View PR details
gh pr view PR_NUMBER

# Get PR as JSON
gh pr view PR_NUMBER --json title,body,files,additions,deletions

# View diff
gh pr diff PR_NUMBER

# Check CI status
gh pr checks PR_NUMBER

# View specific file from PR
gh pr diff PR_NUMBER -- path/to/file.py

# Leave review comment
gh pr review PR_NUMBER --comment -b "Review comments"

# Request changes
gh pr review PR_NUMBER --request-changes -b "Please address security issues"

# Approve
gh pr review PR_NUMBER --approve -b "LGTM!"

# View PR comments
gh api repos/{owner}/{repo}/pulls/PR_NUMBER/comments
```

## Common Violations

### Layer Boundary Violation
```python
# ❌ BAD: Side effect in ops layer
# File: ops/export_ops.py
def export_data(path: Path):
    path.write_text(data)  # I/O in ops layer!

# ✅ GOOD: Return data, let runtime handle I/O
# File: ops/export_ops.py
def export_data() -> str:
    return format_data()

# File: runtime/export_runtime.py
def write_export(data: str, path: Path):
    path.write_text(data)  # I/O in runtime layer
```

### RDF-First Violation
```python
# ❌ BAD: Manually editing generated file
# File: commands/validate_cmd.py (generated)
# [manual edits here]

# ✅ GOOD: Edit RDF source
# File: ontology/cli-commands.ttl
sk:validate
    sk:description "Updated description" .

# Then: ggen sync
```

### Security Violation
```python
# ❌ BAD: Unsafe subprocess
subprocess.run(f"tool {user_input}", shell=True)

# ✅ GOOD: Safe subprocess
run_logged(["tool", user_input])
```

## Integration

Works with:
- `gh pr` - GitHub CLI for PR operations
- `/lint` - Code quality checks
- `/run-tests` - Test execution
- `/validate-architecture` - Layer boundary checks
- Git history - Change analysis

## Notes
- Always check BOTH RDF source and generated files
- Security issues are critical blockers
- Layer violations should be requested changes
- Missing tests are major issues
- Type hints are required, not optional
- Use parallel gh commands to fetch data quickly
- Be constructive and specific in feedback
- Suggest fixes, don't just identify problems
