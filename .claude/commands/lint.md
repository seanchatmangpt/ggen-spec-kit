# Lint and Type Check

Run comprehensive code quality checks including linting, type checking, and auto-fixing.

## Description
Executes ruff (linting) and mypy (type checking) to ensure code quality, style consistency, and type safety across the codebase.

## Usage
```bash
/lint [PATH]
```

## Arguments
- `PATH` (optional) - Specific path to check (default: `src/`)

## Examples
```bash
# Lint entire source directory
/lint

# Lint specific module
/lint src/specify_cli/ops/

# Lint single file
/lint src/specify_cli/core/telemetry.py

# Lint tests
/lint tests/

# Lint everything (including tests)
/lint .
```

## What This Command Does

### 1. Ruff Linting

Checks for:
- Code style violations (PEP 8)
- Unused imports and variables
- Complexity issues
- Security vulnerabilities
- Best practice violations

```bash
uv run ruff check [PATH]
```

### 2. Type Checking (mypy)

Verifies:
- Type hint correctness
- Type consistency
- Return type accuracy
- Argument type matching

```bash
uv run mypy [PATH]
```

### 3. Auto-Fix (Optional)

For fixable issues:
```bash
uv run ruff check --fix [PATH]
```

## Output Format

### Clean Output (No Issues)
```
Linting with ruff... ✓
Type checking with mypy... ✓

All checks passed!
- 0 linting errors
- 0 type errors
- Coverage: 100%
```

### Issues Found
```
Linting with ruff...
❌ 3 errors, 2 warnings

src/specify_cli/ops/ggen_ops.py:15:1: F401 [*] `subprocess` imported but unused
src/specify_cli/ops/ggen_ops.py:42:5: E501 Line too long (95 > 88 characters)
src/specify_cli/runtime/process.py:23:10: B603 `subprocess.run` without `shell=True` is secure

Type checking with mypy...
❌ 1 error

src/specify_cli/ops/validate_ops.py:18: error: Argument 1 to "validate_file" has incompatible type "str"; expected "Path"

[*] = Auto-fixable with --fix
```

### Auto-Fix Results
```
Auto-fixing with ruff...
✓ Fixed 2 issues automatically

Remaining issues (manual fix required):
src/specify_cli/ops/ggen_ops.py:42:5: E501 Line too long (95 > 88 characters)
```

## Ruff Checks

### Error Categories

| Code | Category | Example |
|------|----------|---------|
| F | Pyflakes | F401 (unused import), F841 (unused variable) |
| E | pycodestyle errors | E501 (line too long), E711 (comparison to None) |
| W | pycodestyle warnings | W291 (trailing whitespace) |
| B | flake8-bugbear | B006 (mutable default argument) |
| S | flake8-bandit (security) | S603 (subprocess without shell check) |
| I | isort (imports) | I001 (unsorted imports) |

### Common Issues

**Unused Imports**
```python
# ❌ Before
import subprocess  # F401: imported but unused
from pathlib import Path

# ✅ After (auto-fixed)
from pathlib import Path
```

**Line Length**
```python
# ❌ Before (E501)
def very_long_function_name_that_exceeds_limit(argument1, argument2, argument3, argument4):

# ✅ After
def very_long_function_name_that_exceeds_limit(
    argument1, argument2, argument3, argument4
):
```

**Import Sorting**
```python
# ❌ Before (I001)
from pathlib import Path
import subprocess
from typing import Dict

# ✅ After (auto-fixed)
import subprocess
from pathlib import Path
from typing import Dict
```

## Mypy Type Checking

### Common Type Errors

**Incompatible Types**
```python
# ❌ Error: Argument 1 has incompatible type "str"; expected "Path"
def read_file(path: Path) -> str:
    ...

read_file("file.txt")  # str passed, Path expected

# ✅ Fixed
read_file(Path("file.txt"))
```

**Missing Return Type**
```python
# ❌ Warning: Function is missing a return type annotation
def process_data(data):
    return data.upper()

# ✅ Fixed
def process_data(data: str) -> str:
    return data.upper()
```

**Optional Handling**
```python
# ❌ Error: Item "None" has no attribute "read_text"
def read_config(path: Path | None) -> str:
    return path.read_text()  # path could be None

# ✅ Fixed
def read_config(path: Path | None) -> str:
    if path is None:
        return ""
    return path.read_text()
```

## Code Quality Standards

### Required (Must Pass)
- ✅ 100% type hints on all functions
- ✅ No unused imports or variables
- ✅ No security vulnerabilities (S-codes)
- ✅ Line length ≤ 88 characters
- ✅ Sorted imports

### Recommended (Should Pass)
- ✅ Docstrings on public APIs
- ✅ Complexity < 10 per function
- ✅ No mutable default arguments
- ✅ No bare except clauses

## Auto-Fix Workflow

When fixable issues are found:

```bash
# 1. Show issues
uv run ruff check src/

# 2. Auto-fix safe issues
uv run ruff check --fix src/

# 3. Review changes
git diff

# 4. Re-run to verify
uv run ruff check src/
```

## Integration

Works with:
- `uv run ruff` - Linting and auto-fixing
- `uv run mypy` - Type checking
- `pyproject.toml` - Configuration
- `/run-tests` - Pre-test quality checks
- `/review-pr` - PR quality validation

## Configuration

Configured in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "B", "I", "S"]
ignore = ["S101"]  # Allow assert in tests

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
```

## Common Workflows

### Pre-Commit Checks
```bash
# Run before committing
/lint
# Fix auto-fixable issues
uv run ruff check --fix src/
# Verify all clean
/lint
```

### PR Review Preparation
```bash
# Check entire codebase
/lint .

# Fix issues
uv run ruff check --fix .

# Re-verify
/lint .

# Run tests
/run-tests
```

### Continuous Quality
```bash
# Daily quality check
/lint src/ && /run-tests
```

## Parallel Execution

For comprehensive checks:

```bash
# ✅ GOOD: Run ruff and mypy in parallel
[Single Message]:
  Bash("uv run ruff check src/")
  Bash("uv run mypy src/")

# Results come back together
```

## Notes
- Ruff is much faster than traditional linters (10-100x)
- Auto-fix is safe - it only applies guaranteed-safe transformations
- Type hints are REQUIRED on all public functions
- Docstrings are REQUIRED on public APIs (NumPy style)
- Security checks (S-codes) should never be ignored
- Line length of 88 characters (Black-compatible)
- Always run linting before committing
- Fix type errors immediately - they indicate real bugs
