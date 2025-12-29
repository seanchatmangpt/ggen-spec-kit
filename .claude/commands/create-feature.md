# Create Feature (RDF-First)

Create a new feature following the RDF-first spec-driven approach and constitutional equation.

## Description
Scaffolds a complete feature by starting with RDF specification, generating code via ggen, then implementing business logic in appropriate layers.

## Usage
```bash
/create-feature FEATURE_NAME
```

## Arguments
- `FEATURE_NAME` (required) - Feature name (e.g., "validate", "export", "analyze")

## Examples
```bash
# Create validation feature
/create-feature validate

# Create export feature
/create-feature export

# Create analysis feature
/create-feature analyze
```

## CRITICAL: RDF-First Development

**Never create Python files directly!**

Follow the constitutional equation: `commands/*.py = μ(cli-commands.ttl)`

## Step-by-Step Process

### 1. Create RDF Specification

Edit `ontology/cli-commands.ttl`:

```turtle
sk:validate
    a sk:Command ;
    rdfs:label "validate" ;
    sk:description "Validate RDF specifications against SHACL shapes" ;
    sk:hasArgument [
        a sk:Argument ;
        sk:name "file" ;
        sk:type "Path" ;
        sk:required true ;
        sk:help "Path to RDF/Turtle file to validate"
    ] ;
    sk:hasOption [
        a sk:Option ;
        sk:name "shapes" ;
        sk:type "Path" ;
        sk:required false ;
        sk:help "Custom SHACL shapes file"
    ] .
```

### 2. Create SPARQL Query (if needed)

For data extraction, create `sparql/validate-extract.rq`:

```sparql
PREFIX sk: <http://schema.org/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?command ?description ?arg_name ?arg_type
WHERE {
    ?command a sk:Command ;
             rdfs:label "validate" ;
             sk:description ?description ;
             sk:hasArgument ?arg .

    ?arg sk:name ?arg_name ;
         sk:type ?arg_type .
}
```

### 3. Create Tera Template (if needed)

For custom code generation, create `templates/validate-command.tera`:

```python
"""{{ description }}"""

import typer
from pathlib import Path
from specify_cli.ops.validate_ops import validate_file

def validate(
    file: Path = typer.Argument(..., help="{{ arg_help }}"),
) -> None:
    result = validate_file(file)
    typer.echo(result)
```

### 4. Run ggen Transformation

Generate Python code from RDF:

```bash
ggen sync  # Uses ggen v5.0.2
```

This generates:
- `src/specify_cli/commands/validate_cmd.py` - CLI command (DO NOT EDIT)
- `tests/e2e/test_commands_validate.py` - E2E tests (DO NOT EDIT)

### 5. Implement Operations Layer

Create `src/specify_cli/ops/validate_ops.py`:

```python
"""Validation operations (pure business logic)."""

from pathlib import Path
from typing import Dict, Any

def validate_file(file: Path) -> Dict[str, Any]:
    """Validate RDF file against SHACL shapes.

    Args:
        file: Path to RDF file

    Returns:
        Validation results

    Note:
        Pure function - no side effects, delegates I/O to runtime layer
    """
    # Pure business logic only
    # Delegate actual file reading to runtime layer
    from specify_cli.runtime.rdf_runtime import read_rdf_file, validate_shapes

    rdf_data = read_rdf_file(file)
    return validate_shapes(rdf_data)
```

### 6. Implement Runtime Layer (if needed)

Create `src/specify_cli/runtime/rdf_runtime.py`:

```python
"""RDF runtime operations (side effects only)."""

from pathlib import Path
from specify_cli.core.process import run_logged

def read_rdf_file(file: Path) -> str:
    """Read RDF file from disk.

    Args:
        file: Path to RDF file

    Returns:
        RDF file contents

    Note:
        Runtime layer handles all file I/O
    """
    return file.read_text()

def validate_shapes(rdf_data: str) -> dict:
    """Validate RDF data using external tool.

    Args:
        rdf_data: RDF content

    Returns:
        Validation results

    Note:
        Runtime layer handles subprocess execution
    """
    result = run_logged(
        ["shacl", "validate", "-"],
        input_data=rdf_data
    )
    return result
```

### 7. Run Tests

Verify the complete feature:

```bash
# Run generated tests
uv run pytest tests/e2e/test_commands_validate.py -v

# Run all tests
uv run pytest tests/ -v

# Check coverage
uv run pytest --cov=src/specify_cli --cov-report=term-missing
```

### 8. Add to Changelog

Document the new feature:

```bash
/changelog added "validate command for RDF SHACL validation"
```

## Output Format

After successful feature creation:

1. **RDF Specification**: Shows created/edited TTL entries
2. **Generated Files**: Lists files created by ggen sync
3. **Implementation Stubs**: Shows created ops/runtime files
4. **Test Results**: Reports test execution status
5. **Next Steps**: Suggests documentation and examples

## Three-Tier Architecture

Ensure proper layer separation:

| Layer | Location | Purpose | Constraints |
|-------|----------|---------|-------------|
| Commands | `commands/validate_cmd.py` | CLI interface | Generated - DO NOT EDIT |
| Operations | `ops/validate_ops.py` | Business logic | Pure functions, no I/O |
| Runtime | `runtime/rdf_runtime.py` | Side effects | All I/O, subprocess, HTTP |

## Integration

Works with:
- `ontology/cli-commands.ttl` - Command specifications
- `ggen sync` - Code generation (v5.0.2)
- `sparql/*.rq` - Data extraction queries
- `templates/*.tera` - Code generation templates
- `uv run pytest` - Test execution
- `/changelog` - Documentation

## Verification Checklist

After creating feature:

- [ ] RDF specification in `ontology/cli-commands.ttl`
- [ ] Generated command file exists and compiles
- [ ] Operations layer has pure business logic (no I/O)
- [ ] Runtime layer handles all side effects
- [ ] Tests pass and cover edge cases
- [ ] Type hints on all functions
- [ ] Docstrings on public APIs
- [ ] Changelog entry added
- [ ] No architecture violations

## Common Patterns

### Simple Command (No Side Effects)
```
RDF Spec → ggen sync → commands/ + ops/
```

### Command with I/O
```
RDF Spec → ggen sync → commands/ + ops/ + runtime/
```

### Command with External Tool
```
RDF Spec → ggen sync → commands/ + ops/ + runtime/ (using run_logged)
```

## Notes
- Always start with RDF specification
- Never manually edit generated Python files in commands/
- Operations layer must be pure (testable without I/O)
- Runtime layer uses `run_logged()` for all subprocess calls
- All features should have 80%+ test coverage
- Document new features in changelog
