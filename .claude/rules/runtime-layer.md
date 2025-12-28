---
paths:
  - "src/specify_cli/runtime/**/*.py"
---

# Runtime Layer Rules

## Purpose
The runtime layer handles ALL side effects: subprocess, file I/O, HTTP.

## MUST DO
- Use `run_logged()` for ALL subprocess calls
- Handle file I/O with proper context managers
- Use `httpx` for HTTP requests (async preferred)
- Log all external interactions
- Handle errors gracefully with proper cleanup

## MUST NOT
- Import from `commands` or `ops` layers
- Contain business logic (just execution)
- Use `shell=True` in subprocess calls

## Subprocess Pattern
```python
from specify_cli.core.process import run_logged

def execute_command(args: list[str]) -> subprocess.CompletedProcess:
    """Execute a command with logging.

    Parameters
    ----------
    args : list[str]
        Command arguments as list (NOT string).

    Returns
    -------
    subprocess.CompletedProcess
        The completed process result.
    """
    return run_logged(
        args,
        check=True,
        capture_output=True,
        text=True
    )
```

## File I/O Pattern
```python
from pathlib import Path

def read_file(path: Path) -> str:
    """Read file contents with proper handling."""
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return path.read_text(encoding="utf-8")

def write_file(path: Path, content: str) -> None:
    """Write content to file safely."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
```

## HTTP Pattern
```python
import httpx

async def fetch_data(url: str) -> dict:
    """Fetch data from URL."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
```
