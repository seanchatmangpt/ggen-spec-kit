---
paths:
  - "**/*.py"
  - "**/*.sh"
---

# Security Guardrails

## Absolute Rules

### Never Use shell=True
```python
# WRONG - Command injection risk
subprocess.run(command, shell=True)

# CORRECT - Safe execution
subprocess.run(["command", "arg1", "arg2"])
```

### Never Hardcode Secrets
```python
# WRONG
api_key = "sk-1234567890abcdef"

# CORRECT
api_key = os.environ.get("API_KEY")
```

### Never Use eval/exec with User Input
```python
# WRONG
eval(user_input)

# CORRECT
# Use structured parsing instead
```

## Protected Files

Never read or expose:
- `.env*` files
- `*credentials*` files
- `*.pem` / `*.key` files
- `~/.ssh/*`
- `~/.aws/*`

## Input Validation

All external input must be validated:
```python
def process_input(data: dict) -> dict:
    # Validate required fields
    if not data.get("required_field"):
        raise ValueError("required_field is missing")

    # Validate types
    if not isinstance(data["count"], int):
        raise TypeError("count must be integer")

    # Validate ranges
    if data["count"] < 0 or data["count"] > 1000:
        raise ValueError("count must be 0-1000")

    # Sanitize strings
    data["name"] = data["name"].strip()[:100]

    return data
```

## Path Validation

```python
from pathlib import Path

def safe_read(filepath: Path, allowed_dir: Path) -> str:
    # Resolve to absolute path
    resolved = filepath.resolve()

    # Ensure within allowed directory
    if not str(resolved).startswith(str(allowed_dir.resolve())):
        raise ValueError("Path traversal detected")

    return resolved.read_text()
```

## Subprocess Safety

Always use `run_logged()` from runtime:
```python
from specify_cli.core.process import run_logged

result = run_logged(
    ["command", "arg"],
    check=True,
    capture_output=True,
    text=True
)
```
