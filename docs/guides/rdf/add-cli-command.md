# How-to: Add a CLI Command

**Goal:** Add a new CLI command to your Specify CLI project
**Time:** 20-25 minutes | **Level:** Intermediate

---

## Quick Overview

```
1. Edit RDF → 2. Run ggen sync → 3. Implement logic → 4. Write tests
```

---

## Step 1: Edit RDF Specification

**File:** `ontology/cli-commands.ttl`

Add your command definition:

```turtle
sk:mycommand
    a sk:Command ;
    rdfs:label "mycommand" ;
    sk:description "Brief description of what it does" ;
    sk:hasModule "specify_cli.commands.mycommand" .
```

**For commands with arguments:**
```turtle
sk:validate
    a sk:Command ;
    rdfs:label "validate" ;
    sk:description "Validate RDF specifications" ;
    sk:hasModule "specify_cli.commands.validate" ;
    sk:hasArgument [
        a sk:Argument ;
        sk:name "file" ;
        sk:description "File to validate" ;
        sk:required true ;
        sk:type "str"
    ] .
```

**For commands with options:**
```turtle
sk:lint
    a sk:Command ;
    rdfs:label "lint" ;
    sk:description "Check code quality" ;
    sk:hasModule "specify_cli.commands.lint" ;
    sk:hasOption [
        a sk:Option ;
        sk:name "strict" ;
        sk:description "Strict mode" ;
        sk:flag true
    ] .
```

---

## Step 2: Run ggen Sync

Transform your RDF to Python code:

```bash
ggen sync
```

This generates:
- ✓ `src/specify_cli/commands/mycommand.py` (skeleton)
- ✓ `tests/e2e/test_commands_mycommand.py` (skeleton)
- ✓ `docs/commands/mycommand.md` (documentation)

---

## Step 3: Implement Business Logic

**File:** `src/specify_cli/ops/mycommand.py`

```python
"""Business logic for mycommand."""

def mycommand_operation(arg: str) -> str:
    """Implement the command logic.

    Parameters
    ----------
    arg : str
        Input argument

    Returns
    -------
    str
        Result
    """
    return f"Result: {arg}"
```

**Update the generated command** (`src/specify_cli/commands/mycommand.py`):

```python
import typer
from specify_cli.core.cli import app
from specify_cli.ops.mycommand import mycommand_operation

@app.command()
def mycommand(arg: str = typer.Argument(..., help="Input")):
    """Brief description of what it does."""
    result = mycommand_operation(arg)
    typer.echo(result)
```

---

## Step 4: Write Tests

**File:** `tests/unit/test_mycommand_ops.py`

```python
"""Tests for mycommand operations."""

import pytest
from specify_cli.ops.mycommand import mycommand_operation

def test_mycommand_returns_result():
    """Test mycommand_operation returns expected result."""
    result = mycommand_operation("test")
    assert "Result" in result

def test_mycommand_with_empty_string():
    """Test with empty input."""
    with pytest.raises(ValueError):
        mycommand_operation("")
```

**File:** `tests/e2e/test_commands_mycommand.py`

```python
"""End-to-end tests for mycommand."""

from click.testing import CliRunner
from specify_cli.cli import app

def test_mycommand_command():
    """Test mycommand CLI command."""
    runner = CliRunner()
    result = runner.invoke(app, ["mycommand", "test"])
    assert result.exit_code == 0
    assert "Result" in result.output
```

---

## Step 5: Verify

```bash
# Run tests
uv run pytest tests/ -v

# Test the command manually
python -m specify_cli.cli mycommand "test argument"

# Check documentation was generated
cat docs/commands/mycommand.md
```

---

## Pattern Reference

| Command Type | Pattern | Files |
|--------------|---------|-------|
| Simple (no args) | See Step 1 first example | docs/examples/ai-learning/rdf-patterns.ttl #1 |
| With arguments | See Step 1 second example | docs/examples/ai-learning/rdf-patterns.ttl #2 |
| With options | See Step 1 third example | docs/examples/ai-learning/rdf-patterns.ttl #4 |

---

## Common Patterns

**Pattern: Command that validates input**
```python
def mycommand_operation(name: str) -> str:
    if not name:
        raise ValueError("Name cannot be empty")
    return f"Hello, {name}"
```

**Pattern: Command with logging**
```python
from specify_cli.core.telemetry import get_logger

logger = get_logger(__name__)

def mycommand_operation(arg: str) -> str:
    logger.info("Processing argument", extra={"arg": arg})
    # ... logic ...
    return result
```

**Pattern: Command with observability**
```python
from specify_cli.core.telemetry import timed

@timed
def mycommand_operation(arg: str) -> str:
    # Timing is automatically recorded
    return f"Result: {arg}"
```

---

## Troubleshooting

**Syntax error in RDF**
- Check for missing `;` before properties
- Check for missing `.` at end of definition
- Validate with: `ggen validate ontology/cli-commands.ttl`

**ggen sync fails**
- Ensure RDF syntax is valid
- Check SHACL shapes match specification
- Run: `ggen sync --verbose` for details

**Import error when running**
- Ensure ops module exists: `src/specify_cli/ops/mycommand.py`
- Check Python imports in command file
- Run: `uv sync` to update dependencies

**Tests fail**
- Verify implementation matches specification
- Check assertions are correct
- Run: `uv run pytest tests/ -v -s` for output

---

## Files Checklist

- [ ] Added RDF spec in `ontology/cli-commands.ttl`
- [ ] Ran `ggen sync`
- [ ] Implemented ops function in `src/specify_cli/ops/[name].py`
- [ ] Updated generated command in `src/specify_cli/commands/[name].py`
- [ ] Added unit tests in `tests/unit/test_[name]_ops.py`
- [ ] Added E2E tests in `tests/e2e/test_commands_[name].py`
- [ ] All tests pass: `uv run pytest tests/ -v`
- [ ] Command works: `python -m specify_cli.cli [name]`
- [ ] Documentation generated: `docs/commands/[name].md`

---

## See Also

- [Tutorial 3: Write Your First RDF Specification](../../tutorials/03-first-rdf-spec.md)
- [Reference: RDF Ontology](../../reference/rdf-ontology.md)
- [Explanation: Constitutional Equation](../../explanation/constitutional-equation.md)
- [Examples: RDF Patterns](../../examples/ai-learning/rdf-patterns.ttl)
