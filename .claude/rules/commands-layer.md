---
paths:
  - "src/specify_cli/commands/**/*.py"
---

# Commands Layer Rules

## Purpose
The commands layer is the CLI interface using Typer. It should be a thin wrapper.

## MUST DO
- Parse CLI arguments using Typer decorators
- Format output using Rich (tables, panels, syntax highlighting)
- Delegate ALL business logic to ops layer immediately
- Return exit codes (0 for success, non-zero for errors)

## MUST NOT
- Import `subprocess` or use `subprocess.run()`
- Open files with `open()` or `Path.read_text()`
- Make HTTP requests with `httpx`, `requests`, or `urllib`
- Contain business logic beyond argument validation
- Access environment variables directly (use config)

## Pattern
```python
@app.command()
def my_command(arg: str = typer.Argument(...)) -> None:
    """Command description."""
    # Delegate immediately to ops
    result = my_ops.process(arg)
    # Format and display
    console.print(Panel(result["message"]))
```

## Imports Allowed
- `typer`
- `rich` and submodules
- `specify_cli.ops.*`
- `specify_cli.core.config`

## Imports Forbidden
- `subprocess`
- `httpx`, `requests`
- `specify_cli.runtime.*` (ops should call runtime)
