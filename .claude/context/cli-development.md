# CLI Development Context

## Active When
Working with files in `src/specify_cli/commands/` or the CLI.

## Architecture Rules

### Commands Layer ONLY Does
- Parse arguments with Typer decorators
- Format output with Rich
- Delegate to ops layer immediately
- Return exit codes

### Commands Layer NEVER Does
- File I/O (`open()`, `Path.read_text()`)
- Subprocess calls
- HTTP requests
- Business logic

## Command Pattern

```python
import typer
from rich.console import Console
from rich.panel import Panel

from specify_cli.ops import feature_ops

app = typer.Typer()
console = Console()

@app.command()
def my_command(
    argument: str = typer.Argument(..., help="Description"),
    option: bool = typer.Option(False, "--opt", "-o", help="Description"),
) -> None:
    """Command description shown in --help."""
    # Delegate to ops immediately
    result = feature_ops.process(argument, option)

    # Format and display
    if result["status"] == "success":
        console.print(Panel(result["message"], title="Success"))
    else:
        console.print(f"[red]Error:[/red] {result['error']}")
        raise typer.Exit(1)
```

## Rich Formatting

```python
# Tables
from rich.table import Table
table = Table(title="Results")
table.add_column("Name")
table.add_row("value")
console.print(table)

# Panels
from rich.panel import Panel
console.print(Panel("Content", title="Title"))

# Syntax highlighting
from rich.syntax import Syntax
syntax = Syntax(code, "python")
console.print(syntax)

# Progress
from rich.progress import track
for item in track(items, description="Processing..."):
    process(item)
```

## Testing Commands

```python
from typer.testing import CliRunner

runner = CliRunner()
result = runner.invoke(app, ["command", "arg"])
assert result.exit_code == 0
assert "expected" in result.stdout
```
