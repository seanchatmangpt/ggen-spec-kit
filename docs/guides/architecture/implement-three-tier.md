# How-to: Implement Three-Tier Architecture

**Goal:** Organize your code into Commands/Ops/Runtime layers
**Time:** 20-25 minutes | **Level:** Intermediate

---

## The Pattern

```
Commands Layer          ← CLI (user-facing)
    ↓ (calls)
Operations Layer        ← Business logic (pure, no side effects)
    ↓ (calls)
Runtime Layer           ← I/O, subprocess, HTTP (all side effects)
```

---

## Layer Responsibilities

### Commands Layer (`src/specify_cli/commands/`)
**What:** CLI interface using Typer
**Responsibility:** Parse arguments, call ops, format output
**What's allowed:** ✅ Argument parsing, ✅ Rich formatting, ✅ Error display
**What's forbidden:** ❌ Subprocess, ❌ File I/O, ❌ Business logic

```python
# src/specify_cli/commands/hello.py
import typer
from specify_cli.ops.hello import hello_operation

@app.command()
def hello(name: str = typer.Option("World")):
    """Greet the user."""
    # Call ops layer
    result = hello_operation(name)
    # Format and display
    typer.echo(result)
```

### Operations Layer (`src/specify_cli/ops/`)
**What:** Pure business logic
**Responsibility:** Implement the actual feature
**What's allowed:** ✅ Calculation, ✅ Validation, ✅ Data transformation
**What's forbidden:** ❌ Subprocess, ❌ File I/O, ❌ HTTP calls, ❌ Database access

```python
# src/specify_cli/ops/hello.py
def hello_operation(name: str) -> str:
    """Generate greeting (pure function).

    Parameters
    ----------
    name : str
        Person to greet

    Returns
    -------
    str
        Greeting message

    Raises
    ------
    ValueError
        If name is empty
    """
    if not name:
        raise ValueError("Name cannot be empty")
    return f"Hello, {name}! Welcome to Spec Kit."
```

**Key rule:** Operations are **pure functions**
- Same input → same output
- No side effects
- Easy to test
- Easy to reason about

### Runtime Layer (`src/specify_cli/runtime/`)
**What:** I/O and side effects
**Responsibility:** File I/O, subprocess, HTTP, database
**What's allowed:** ✅ Everything that has side effects
**What's forbidden:** ❌ Business logic, ❌ CLI parsing

```python
# src/specify_cli/runtime/file_ops.py
def read_file(path: str) -> str:
    """Read file from disk."""
    with open(path, 'r') as f:
        return f.read()

def write_file(path: str, content: str) -> None:
    """Write file to disk."""
    with open(path, 'w') as f:
        f.write(content)

# src/specify_cli/runtime/subprocess_runner.py
def run_command(command: List[str]) -> str:
    """Run subprocess command."""
    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )
    return result.stdout
```

---

## Example: Build Feature

### Commands Layer
```python
# src/specify_cli/commands/build.py
import typer
from specify_cli.ops.build import build_operation

@app.command()
def build(
    target: str = typer.Option("wheel", help="wheel or sdist"),
    verbose: bool = typer.Option(False, help="Verbose output")
):
    """Build project artifacts."""
    result = build_operation(target, verbose)

    for artifact in result["artifacts"]:
        typer.echo(f"Built: {artifact}")

    if verbose:
        typer.echo(f"Time: {result['time_seconds']}s")
```

### Operations Layer
```python
# src/specify_cli/ops/build.py
def build_operation(target: str = "wheel", verbose: bool = False) -> dict:
    """Plan and execute build.

    Pure logic: what to build and how to organize it.
    Does NOT do the actual building.
    """
    if target not in ["wheel", "sdist"]:
        raise ValueError(f"Unknown target: {target}")

    build_plan = {
        "artifacts": [f"dist/package-{target}.tar.gz"],
        "time_seconds": 2.5
    }
    return build_plan
```

### Runtime Layer
```python
# src/specify_cli/runtime/build_runner.py
def execute_build(target: str) -> bool:
    """Actually run the build subprocess."""
    command = ["python", "-m", "build", f"--{target}"]
    result = subprocess.run(command)
    return result.returncode == 0
```

---

## Implementation Steps

### Step 1: Create Layer Files

```bash
# Commands are auto-generated from RDF
# But create ops and runtime files:

touch src/specify_cli/ops/myfeature.py
touch src/specify_cli/runtime/myfeature_runner.py
```

### Step 2: Implement Operations (Pure Logic)

```python
# src/specify_cli/ops/myfeature.py
def myfeature_operation(input_data: str) -> dict:
    """Pure business logic.

    Parameters
    ----------
    input_data : str
        Input to process

    Returns
    -------
    dict
        Processing result with "success" and "data"

    Raises
    ------
    ValueError
        If input is invalid
    """
    # Validate
    if not input_data:
        raise ValueError("Input cannot be empty")

    # Transform
    result = {"success": True, "data": f"Processed: {input_data}"}
    return result
```

**Key characteristics:**
- ✅ Type hints on inputs and outputs
- ✅ Docstring explaining the logic
- ✅ Validation of inputs
- ✅ Return structured data
- ✅ Raise exceptions on errors
- ✅ No file I/O, subprocess, HTTP

### Step 3: Update Generated Command

```python
# src/specify_cli/commands/myfeature.py
import typer
from specify_cli.ops.myfeature import myfeature_operation
from specify_cli.runtime.myfeature_runner import execute_myfeature

@app.command()
def myfeature(input_arg: str = typer.Argument(...)):
    """Implement my feature."""
    # Call ops layer (pure logic)
    plan = myfeature_operation(input_arg)

    if not plan["success"]:
        typer.echo("Error processing input", err=True)
        raise typer.Exit(1)

    # Call runtime layer (do the actual work)
    result = execute_myfeature(plan)

    # Format output
    typer.echo(f"Success: {result}")
```

### Step 4: Implement Runtime (I/O)

```python
# src/specify_cli/runtime/myfeature_runner.py
import subprocess
from pathlib import Path

def execute_myfeature(plan: dict) -> str:
    """Execute the planned feature.

    This is where file I/O, subprocess, HTTP happen.
    """
    # File I/O is OK here
    output_file = Path("output.txt")
    output_file.write_text(plan["data"])

    # Subprocess is OK here
    result = subprocess.run(["cat", "output.txt"])

    return "Done"
```

### Step 5: Write Tests

```python
# tests/unit/test_myfeature_ops.py
import pytest
from specify_cli.ops.myfeature import myfeature_operation

def test_myfeature_with_valid_input():
    """Test ops layer with valid input."""
    result = myfeature_operation("test")
    assert result["success"] is True
    assert "Processed" in result["data"]

def test_myfeature_with_empty_raises():
    """Test ops layer validates input."""
    with pytest.raises(ValueError):
        myfeature_operation("")
```

**Important:** Test the ops layer directly (no mocking needed because it's pure)

---

## Validation Checklist

### Commands Layer
- [ ] Only imports from ops layer
- [ ] No file I/O
- [ ] No subprocess calls
- [ ] Uses Typer for argument parsing
- [ ] Catches exceptions from ops layer

### Operations Layer
- [ ] No imports from commands/runtime
- [ ] Pure functions (no side effects)
- [ ] Full type hints
- [ ] Docstrings with Parameters/Returns/Raises
- [ ] Validates inputs
- [ ] Raises exceptions on errors

### Runtime Layer
- [ ] Only I/O, subprocess, HTTP
- [ ] No business logic
- [ ] May import from ops (but not vice versa)
- [ ] Error handling for I/O failures

---

## Anti-Patterns to Avoid

❌ **Business logic in commands layer**
```python
# WRONG
@app.command()
def bad():
    # Don't do logic here!
    result = do_calculation()
```

✅ **Business logic in ops layer**
```python
# RIGHT
@app.command()
def good():
    result = ops.do_calculation()
```

---

❌ **I/O in ops layer**
```python
# WRONG
def operation():
    with open("file.txt") as f:  # NO!
        return f.read()
```

✅ **I/O in runtime layer**
```python
# RIGHT
def operation(data: str) -> str:
    return f"Processed: {data}"

def runtime_execute(data: str) -> str:
    with open("file.txt") as f:  # OK here
        return operation(f.read())
```

---

## See Also

- [Explanation: Three-Tier Architecture](../../explanation/three-tier-architecture.md)
- [How-to: Add a CLI Command](../rdf/add-cli-command.md)
- [Tutorial 2: Create Your First Project](../../tutorials/02-first-project.md)
- [CLAUDE.md](../../../CLAUDE.md) - Architecture rules
