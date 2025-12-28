---
paths:
  - "src/specify_cli/**/*.py"
---

# Layer Boundary Guardrails

## The Three Tiers

```
┌─────────────────────────────────────┐
│  COMMANDS (src/specify_cli/commands/)│
│  - Typer CLI                        │
│  - Rich formatting                  │
│  - NO side effects                  │
├─────────────────────────────────────┤
│  OPERATIONS (src/specify_cli/ops/)  │
│  - Pure business logic              │
│  - Return structured data           │
│  - NO side effects                  │
├─────────────────────────────────────┤
│  RUNTIME (src/specify_cli/runtime/) │
│  - ALL subprocess calls             │
│  - ALL file I/O                     │
│  - ALL HTTP requests                │
└─────────────────────────────────────┘
```

## Forbidden Patterns

### In Commands Layer
```python
# FORBIDDEN
import subprocess
open("file.txt")
httpx.get(url)
Path.read_text()
os.system()

# ALLOWED
import typer
from rich.console import Console
from specify_cli.ops import module
```

### In Operations Layer
```python
# FORBIDDEN
import subprocess
open("file.txt")
httpx.get(url)
from specify_cli.runtime import module

# ALLOWED
from specify_cli.ops import other_ops
# Pure function definitions only
```

### In Runtime Layer
```python
# FORBIDDEN
from specify_cli.commands import module
from specify_cli.ops import module

# ALLOWED
import subprocess
from pathlib import Path
import httpx
```

## Violation Detection

Search for violations:
```bash
# Check for subprocess in commands/ops
grep -r "subprocess" src/specify_cli/commands/ src/specify_cli/ops/

# Check for file I/O in commands/ops
grep -r "open(" src/specify_cli/commands/ src/specify_cli/ops/
grep -r "\.read_text()" src/specify_cli/commands/ src/specify_cli/ops/

# Check for HTTP in commands/ops
grep -r "httpx" src/specify_cli/commands/ src/specify_cli/ops/
```

## How to Fix Violations

### Move to Runtime
1. Create function in `runtime/`
2. Call from ops via dependency injection
3. Remove side effect from ops

### Ops Should Return Data
```python
# Instead of writing file in ops:
def process() -> dict:
    return {"content": generated_content, "path": target_path}

# Runtime writes the file:
def write_result(result: dict) -> None:
    Path(result["path"]).write_text(result["content"])
```
