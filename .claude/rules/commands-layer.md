---
paths:
  - "src/specify_cli/commands/**/*.py"
---

# Commands Layer Rules

Thin CLI wrapper. Zero side effects. Parse args → delegate → format.

## DO
- Parse args with Typer decorators
- Delegate immediately to ops layer
- Format output with Rich (table, panel, syntax)
- Return exit codes (0=success)

## DON'T
- Use subprocess, file I/O, or HTTP
- Contain business logic
- Import `runtime` (ops → runtime only)
- Access env vars directly (use config)

## Pattern
```python
@app.command()
def process(file: str = typer.Argument(...)) -> None:
    """Process a file."""
    result = my_ops.execute(file)
    console.print(Panel(result["message"]))
```

## Imports
- ✅ typer, rich, specify_cli.ops.*, specify_cli.core.config
- ❌ subprocess, httpx, specify_cli.runtime
