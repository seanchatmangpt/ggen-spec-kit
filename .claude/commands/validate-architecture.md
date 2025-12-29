# Validate Architecture

Validate three-tier architecture compliance, layer boundaries, and separation of concerns.

## Description
Performs automated checks to ensure codebase follows the three-tier architecture pattern with proper separation between CLI interface (commands), business logic (ops), and side effects (runtime).

## Usage
```bash
/validate-architecture
```

## No Arguments Required
Scans entire `src/specify_cli/` directory for architecture violations.

## Examples
```bash
# Full architecture validation
/validate-architecture

# Run before PR submission
/lint && /validate-architecture && /run-tests
```

## What This Command Does

Validates the three-tier architecture:

```
┌─────────────────────────────────────────────┐
│ Commands Layer (CLI Interface)             │
│ - Parse arguments                           │
│ - Format output                             │
│ - Delegate to ops                           │
│ ❌ NO side effects                          │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ Operations Layer (Business Logic)          │
│ - Pure functions                            │
│ - Return structured data                    │
│ - Validate inputs                           │
│ ❌ NO side effects                          │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ Runtime Layer (Side Effects)               │
│ - Subprocess execution                      │
│ - File I/O                                  │
│ - HTTP requests                             │
│ ✅ ALL side effects                         │
└─────────────────────────────────────────────┘
```

## Architecture Rules

### Commands Layer Rules
**Location**: `src/specify_cli/commands/`

**Allowed**:
- ✅ Parse CLI arguments with Typer
- ✅ Format output with Rich
- ✅ Call operations layer functions
- ✅ Handle user interaction (prompts)
- ✅ Exit codes and error messages

**Forbidden**:
- ❌ NO `subprocess` module usage
- ❌ NO file operations (`open`, `Path.write_text`, etc.)
- ❌ NO HTTP requests (`httpx`, `requests`)
- ❌ NO database access
- ❌ NO environment variable writes
- ❌ NO business logic implementation

### Operations Layer Rules
**Location**: `src/specify_cli/ops/`

**Allowed**:
- ✅ Pure business logic functions
- ✅ Data validation and transformation
- ✅ Algorithm implementation
- ✅ Return structured data (dicts, dataclasses)
- ✅ Raise exceptions for validation errors
- ✅ Call other ops functions
- ✅ Call runtime layer for side effects

**Forbidden**:
- ❌ NO `subprocess` module usage
- ❌ NO file operations (`open`, `Path.write_text`, etc.)
- ❌ NO HTTP requests (`httpx`, `requests`)
- ❌ NO database access
- ❌ NO environment variable writes
- ❌ NO state mutation (except local variables)

### Runtime Layer Rules
**Location**: `src/specify_cli/runtime/`

**Allowed**:
- ✅ All subprocess via `run_logged()`
- ✅ All file I/O operations
- ✅ All HTTP requests
- ✅ Database connections
- ✅ Environment variable access
- ✅ External system integration

**Forbidden**:
- ❌ NO imports from `commands` layer
- ❌ NO imports from `ops` layer
- ❌ NO business logic (delegate to ops)
- ❌ NO direct `subprocess.run` (use `run_logged`)

## Validation Checks

### Check 1: Side Effects in Commands Layer

```bash
# Search for forbidden patterns in commands/
grep -rn "subprocess\|\.open(\|\.write_text\|\.read_text\|httpx\|requests" \
  src/specify_cli/commands/
```

**Expected**: No matches

### Check 2: Side Effects in Operations Layer

```bash
# Search for forbidden patterns in ops/
grep -rn "subprocess\|\.open(\|\.write_text\|\.read_text\|httpx\|requests" \
  src/specify_cli/ops/
```

**Expected**: No matches (except imports of runtime layer)

### Check 3: Improper Imports in Runtime Layer

```bash
# Search for upward imports in runtime/
grep -rn "from specify_cli.commands\|from specify_cli.ops" \
  src/specify_cli/runtime/
```

**Expected**: No matches

### Check 4: Direct subprocess Usage

```bash
# Search for direct subprocess.run (should use run_logged)
grep -rn "subprocess\.run\|subprocess\.Popen\|subprocess\.call" \
  src/specify_cli/ --exclude-dir=core
```

**Expected**: Only in `core/process.py`

### Check 5: Shell=True Usage

```bash
# Search for dangerous shell=True
grep -rn "shell=True" src/specify_cli/
```

**Expected**: No matches (security violation)

### Check 6: Circular Dependencies

```bash
# Build import graph and check for cycles
python scripts/check_circular_imports.py
```

**Expected**: No circular dependencies

## Output Format

### Clean Architecture
```
✅ Architecture Validation: PASSED

Three-Tier Compliance:
  Commands Layer    ✓  (0 violations)
  Operations Layer  ✓  (0 violations)
  Runtime Layer     ✓  (0 violations)

Security:
  No shell=True     ✓
  No hardcoded secrets  ✓

Dependencies:
  No circular imports   ✓
  Proper layer isolation ✓

Summary: All architecture rules followed
```

### Violations Found
```
❌ Architecture Validation: FAILED (3 violations)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 CRITICAL: Side Effect in Operations Layer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

File: src/specify_cli/ops/export_ops.py
Line: 23
Code: path.write_text(data)

Violation: File I/O in operations layer
Layer: ops (should be pure)

Fix:
  # Current (WRONG)
  def export_data(data: str, path: Path):
      path.write_text(data)  # ❌ Side effect in ops

  # Corrected
  # ops/export_ops.py (return data)
  def export_data(data: str) -> str:
      return format_data(data)  # ✅ Pure function

  # runtime/export_runtime.py (handle I/O)
  def write_export(data: str, path: Path):
      path.write_text(data)  # ✅ I/O in runtime

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟡 MAJOR: Direct subprocess Usage
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

File: src/specify_cli/runtime/ggen_runtime.py
Line: 45
Code: subprocess.run(["ggen", "sync"])

Violation: Direct subprocess.run instead of run_logged
Layer: runtime

Fix:
  # Current (WRONG)
  subprocess.run(["ggen", "sync"])  # ❌ Not instrumented

  # Corrected
  from specify_cli.core.process import run_logged
  run_logged(["ggen", "sync"])  # ✅ Logged and instrumented

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 CRITICAL: Security Violation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

File: src/specify_cli/runtime/tool_runner.py
Line: 67
Code: subprocess.run(cmd, shell=True)

Violation: shell=True is forbidden (security risk)
Layer: runtime

Fix:
  # Current (WRONG - Security risk!)
  subprocess.run(f"tool {arg}", shell=True)  # ❌ Command injection risk

  # Corrected
  run_logged(["tool", arg])  # ✅ Safe, list-based

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Summary:
  🔴 Critical: 2 violations (must fix before merge)
  🟡 Major: 1 violation (should fix)
  🔵 Minor: 0 violations

Next Steps:
  1. Fix critical violations immediately
  2. Run /validate-architecture again
  3. Run /run-tests to ensure fixes work
  4. Review architecture guidelines in CLAUDE.md
```

## Validation Checklist

### Layer Separation
- [ ] Commands layer has no side effects
- [ ] Operations layer has no side effects
- [ ] Runtime layer isolated (no upward imports)
- [ ] Each layer has clear responsibility

### Security
- [ ] No `shell=True` in subprocess calls
- [ ] No hardcoded secrets or credentials
- [ ] Proper input validation
- [ ] Path validation before file ops

### Best Practices
- [ ] All subprocess via `run_logged()`
- [ ] List-based command construction
- [ ] Type hints on all functions
- [ ] Proper error handling

### Dependencies
- [ ] No circular imports
- [ ] Proper dependency direction (commands → ops → runtime)
- [ ] Core utilities properly shared

## Common Violations and Fixes

### Violation 1: I/O in Operations Layer
```python
# ❌ WRONG: File I/O in ops
# File: ops/config_ops.py
def save_config(config: dict, path: Path):
    path.write_text(json.dumps(config))  # Side effect!

# ✅ CORRECT: Split into ops + runtime
# File: ops/config_ops.py
def serialize_config(config: dict) -> str:
    return json.dumps(config, indent=2)  # Pure function

# File: runtime/config_runtime.py
def write_config(content: str, path: Path):
    path.write_text(content)  # I/O in runtime
```

### Violation 2: Subprocess in Operations Layer
```python
# ❌ WRONG: Subprocess in ops
# File: ops/ggen_ops.py
def sync_rdf():
    subprocess.run(["ggen", "sync"])  # Side effect!

# ✅ CORRECT: Delegate to runtime
# File: ops/ggen_ops.py
def prepare_sync() -> dict:
    return {"command": "sync"}  # Pure logic

# File: runtime/ggen_runtime.py
def execute_sync():
    run_logged(["ggen", "sync"])  # Subprocess in runtime
```

### Violation 3: Runtime Imports Ops
```python
# ❌ WRONG: Upward import
# File: runtime/tool_runner.py
from specify_cli.ops.validation import validate  # Violation!

# ✅ CORRECT: Runtime doesn't import ops
# Operations call runtime, not vice versa
```

### Violation 4: Direct subprocess Usage
```python
# ❌ WRONG: Direct subprocess.run
subprocess.run(["tool", "arg"])  # Not instrumented

# ✅ CORRECT: Use run_logged
from specify_cli.core.process import run_logged
run_logged(["tool", "arg"])  # Logged, instrumented, safe
```

## Integration

Works with:
- `/lint` - Code quality checks
- `/run-tests` - Test execution
- `/review-pr` - PR reviews
- `grep` - Pattern searching
- Python AST analysis - Import graph

## Automated Validation Script

Create `scripts/validate_architecture.py`:

```python
#!/usr/bin/env python3
"""Automated architecture validation."""

import re
from pathlib import Path
from typing import List, Tuple

def find_violations() -> List[Tuple[Path, int, str]]:
    """Find architecture violations."""
    violations = []

    # Check commands layer
    for file in Path("src/specify_cli/commands").rglob("*.py"):
        content = file.read_text()
        for i, line in enumerate(content.splitlines(), 1):
            if re.search(r"subprocess|\.open\(|\.write_text|httpx|requests", line):
                violations.append((file, i, "Side effect in commands layer"))

    # Check ops layer
    for file in Path("src/specify_cli/ops").rglob("*.py"):
        content = file.read_text()
        for i, line in enumerate(content.splitlines(), 1):
            if re.search(r"subprocess|\.open\(|\.write_text|httpx|requests", line):
                if "from specify_cli.runtime" not in line:  # Allow runtime imports
                    violations.append((file, i, "Side effect in ops layer"))

    # Check runtime layer
    for file in Path("src/specify_cli/runtime").rglob("*.py"):
        content = file.read_text()
        for i, line in enumerate(content.splitlines(), 1):
            if "from specify_cli.commands" in line or "from specify_cli.ops" in line:
                violations.append((file, i, "Upward import in runtime layer"))

    # Check shell=True usage
    for file in Path("src/specify_cli").rglob("*.py"):
        content = file.read_text()
        for i, line in enumerate(content.splitlines(), 1):
            if "shell=True" in line:
                violations.append((file, i, "Security: shell=True forbidden"))

    return violations

if __name__ == "__main__":
    violations = find_violations()
    if not violations:
        print("✅ Architecture validation passed")
        exit(0)
    else:
        print(f"❌ Found {len(violations)} violations")
        for file, line, msg in violations:
            print(f"{file}:{line} - {msg}")
        exit(1)
```

## Notes
- Run this check before every PR
- Architecture violations are PR blockers
- Layer separation enables better testing
- Pure functions (ops) are easier to test than I/O (runtime)
- Commands layer should be thin wrappers
- All subprocess must use `run_logged()` for instrumentation
- shell=True is always forbidden (security risk)
- Generated files (commands/*.py) should already be compliant
- Manual implementations (ops/, runtime/) need validation
