# Reference: Python API

Core Python APIs for Spec Kit operations.

## Telemetry API

```python
from specify_cli.core.telemetry import timed, span, get_logger, meter

# Decorator for timing
@timed
def my_operation():
    ...

# Context manager for spans
with span("operation_name", attributes={"key": "value"}):
    ...

# Logging
logger = get_logger(__name__)
logger.info("Message", extra={"key": "value"})
logger.error("Error", exc_info=True)

# Metrics
counter = meter.create_counter("operation.count")
counter.add(1)

histogram = meter.create_histogram("operation.duration_ms")
histogram.record(123)
```

## Process API

```python
from specify_cli.core.process import run_logged

# Run command with logging
result = run_logged(
    ["command", "arg"],
    cwd="/working/dir",
    timeout=30
)

# Returns: CompletedProcess
result.returncode
result.stdout
result.stderr
```

## CLI API

```python
from specify_cli.core.cli import app
import typer

@app.command()
def my_command(
    arg: str = typer.Argument(..., help="Help text"),
    opt: str = typer.Option(None, help="Help text")
):
    """Command description."""
    typer.echo("Output")

# Run
if __name__ == "__main__":
    app()
```

## Types

```python
from pathlib import Path
from typing import Dict, List, Optional

# Use type hints
def operation(
    path: Path,
    items: List[str],
    config: Optional[Dict] = None
) -> str:
    ...
```

See: `src/specify_cli/` for full API
