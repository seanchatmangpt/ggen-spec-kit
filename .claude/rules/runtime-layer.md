---
paths:
  - "src/specify_cli/runtime/**/*.py"
---

# Runtime Layer Rules

All I/O, subprocess, network. Side effects only here.

## DO
- Use `run_logged()` for ALL subprocess calls
- Use context managers for file I/O
- Use `httpx` for HTTP (async preferred)
- Log external interactions
- Handle errors with cleanup

## DON'T
- Import from `commands` or `ops` layers
- Contain business logic
- Use `shell=True` in subprocess
- Call without error handling
- Assume paths/URLs are valid

## Subprocess
```python
from specify_cli.core.process import run_logged

result = run_logged(
    ["command", "arg1", "arg2"],  # List, not string
    check=True,
    capture_output=True,
    text=True
)
```

## File I/O
```python
def read_file(path: Path) -> str:
    """Read file contents."""
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return path.read_text(encoding="utf-8")

def write_file(path: Path, content: str) -> None:
    """Write content to file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
```

## HTTP
```python
async def fetch_data(url: str) -> dict:
    """Fetch from URL."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
```
