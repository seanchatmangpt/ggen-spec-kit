# Explanation: Three-Tier Architecture

**Time to understand:** 15-20 minutes

## Why Separate Code Into Layers?

**Problem with mixed code:**
```python
@app.command()
def hello(name: str):
    # Argument parsing (CLI layer)
    if not name:
        return "Error: name required"

    # Business logic (operations layer)
    greeting = f"Hello, {name}"

    # File I/O (runtime layer)
    with open("output.txt", "w") as f:
        f.write(greeting)

    return "Done"
```

**Problems:**
- ❌ Hard to test (can't test logic without I/O)
- ❌ Hard to reuse (mixed concerns)
- ❌ Hard to understand (too much happening)
- ❌ Tight coupling (dependencies everywhere)

## The Three Tiers

### Tier 1: Commands (Interface)
**Responsibility:** CLI argument parsing and output formatting

**What's allowed:**
- ✅ Parse arguments with Typer
- ✅ Format output with Rich
- ✅ Display errors

**What's forbidden:**
- ❌ Business logic
- ❌ File I/O
- ❌ Subprocess calls

**Example:**
```python
@app.command()
def hello(name: str = typer.Option("World")):
    """Greet the user."""
    result = hello_operation(name)  # Delegate to ops
    typer.echo(result)  # Format output
```

### Tier 2: Operations (Logic)
**Responsibility:** Pure business logic

**What's allowed:**
- ✅ Validation
- ✅ Calculation
- ✅ Data transformation
- ✅ Decision making

**What's forbidden:**
- ❌ File I/O
- ❌ Subprocess calls
- ❌ HTTP requests
- ❌ Database access

**Example:**
```python
def hello_operation(name: str) -> str:
    """Pure business logic (no side effects)."""
    if not name:
        raise ValueError("Name cannot be empty")
    return f"Hello, {name}"
```

### Tier 3: Runtime (Effects)
**Responsibility:** I/O and all side effects

**What's allowed:**
- ✅ File I/O
- ✅ Subprocess
- ✅ HTTP requests
- ✅ Database calls
- ✅ Network operations

**What's forbidden:**
- ❌ Business logic
- ❌ CLI parsing

**Example:**
```python
def write_greeting(greeting: str) -> None:
    """Side effect: write to file."""
    with open("output.txt", "w") as f:
        f.write(greeting)
```

## Benefits

### Testability
```python
# Can test logic without I/O
result = hello_operation("World")
assert "World" in result  # ✅ No file I/O needed!
```

### Reusability
```python
# Can use logic from different interfaces
# CLI command, API endpoint, scheduled task
result = hello_operation("World")
```

### Clarity
```python
# Each layer has one responsibility
# Easy to understand each piece
```

### Independence
```python
# Can test each layer separately
# Can change I/O without affecting logic
# Can refactor safely
```

## The Flow

```
User Input
    ↓
Commands Layer (parse, validate)
    ↓
Operations Layer (business logic)
    ↓
Runtime Layer (I/O, effects)
    ↓
Output
```

**Key rule:** Always flow downward (commands → ops → runtime)
**Never go up:** Runtime can't call commands

## Example: File Processing

### Commands
```python
@app.command()
def process(file: Path = typer.Argument(...)):
    """Process a file."""
    content = runtime_read_file(file)
    result = process_operation(content)
    typer.echo(f"Result: {result}")
```

### Operations
```python
def process_operation(content: str) -> str:
    """Pure processing logic."""
    lines = content.split("\n")
    processed = [line.upper() for line in lines]
    return "\n".join(processed)
```

### Runtime
```python
def runtime_read_file(path: Path) -> str:
    """Read from disk."""
    with open(path) as f:
        return f.read()
```

## Validation Checklist

✅ Commands layer:
- [ ] Only imports from ops
- [ ] No file I/O
- [ ] No subprocess
- [ ] Uses Typer

✅ Operations layer:
- [ ] No imports from commands/runtime
- [ ] Pure functions
- [ ] All inputs validated
- [ ] Clear contracts (inputs/outputs)

✅ Runtime layer:
- [ ] Only handles I/O
- [ ] Error handling for side effects
- [ ] Clear responsibilities
- [ ] Logs all operations

## See Also
- [How-to: Three-Tier Architecture](../guides/architecture/implement-three-tier.md)
- [CLAUDE.md](../../CLAUDE.md) - Architecture rules
