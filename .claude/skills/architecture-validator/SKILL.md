---
name: architecture-validator
description: Validate three-tier architecture compliance and layer boundaries. Use when checking layer separation, detecting circular dependencies, or ensuring side effects are isolated in runtime layer.
allowed-tools: Read, Glob, Grep, Bash, LSP
---

# Architecture Validator

Validate three-tier architecture compliance and ensure proper layer separation.

## Instructions

1. Verify Commands → Ops → Runtime flow
2. Check for circular dependencies
3. Ensure ops layer is pure (no side effects)
4. Verify interface contracts
5. Detect anti-patterns

## Three-Tier Architecture

```
Commands Layer (src/specify_cli/commands/)
  │ • Typer CLI handlers only
  │ • Argument parsing & output formatting
  ↓
Operations Layer (src/specify_cli/ops/)
  │ • Pure business logic
  │ • NO side effects
  ↓
Runtime Layer (src/specify_cli/runtime/)
    • Subprocess execution
    • File I/O, HTTP requests
    • ALL side effects here
```

## Validation Commands

```bash
# Check commands for side effects (should find none)
grep -rn "subprocess\|httpx\|open\(" src/specify_cli/commands/

# Check ops for side effects (should find none)
grep -rn "subprocess\|os\.system\|open\(" src/specify_cli/ops/

# Check for circular deps
grep -rn "from specify_cli.commands" src/specify_cli/ops/
grep -rn "from specify_cli.commands\|from specify_cli.ops" src/specify_cli/runtime/
```

## Layer Rules

### Commands (allowed)
```python
from typer import Typer
from rich.console import Console
from specify_cli.ops import init_ops
```

### Ops (allowed)
```python
from specify_cli.runtime import github, git
from specify_cli.core.telemetry import span
# NO subprocess, NO open(), NO httpx
```

### Runtime (allowed)
```python
import subprocess
import httpx
from pathlib import Path
# NO imports from commands or ops
```

## Anti-Pattern Detection

```python
# ❌ WRONG: Subprocess in ops
def initialize_project(name: str):
    subprocess.run(["git", "init"])

# ✅ RIGHT: Delegate to runtime
def initialize_project(name: str):
    from specify_cli.runtime import git
    return git.init_repo(name)
```

## Output Format

```markdown
## Architecture Validation Report

### Layer Structure
- Commands: ✅ X modules
- Operations: ✅ X modules
- Runtime: ✅ X modules

### Side Effect Analysis
- Commands: ✅ No side effects
- Operations: ✅ Pure logic
- Runtime: ✅ Side effects isolated

### Circular Dependencies
- None found ✅

### Overall: ✅ COMPLIANT / ❌ VIOLATIONS
```
