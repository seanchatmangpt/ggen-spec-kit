# Complete ggen Workflow Example

This document walks through a complete end-to-end example of using ggen to generate code, tests, and documentation from RDF specifications.

## Scenario: Adding a New "validate" CLI Command

Let's say we want to add a new `validate` CLI command that validates RDF specifications.

### Step 1: Define Command in RDF

**File**: `ontology/cli-commands.ttl`

Add this RDF specification:

```turtle
@prefix sk: <http://spec-kit.io/ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Command Definition
sk:validate a sk:Command ;
    rdfs:label "validate" ;
    sk:description "Validate RDF specification files" ;
    sk:longDescription "Validates RDF ontology files against SHACL shapes and checks for semantic consistency" ;
    sk:category "validation" ;
    sk:hasArgument sk:validate_file_arg ;
    sk:hasArgument sk:validate_strict_arg ;
    sk:hasOption sk:validate_output_opt ;
    sk:returnsExitCode 0 ;
    sk:returnsExitCode 1 .

# Arguments
sk:validate_file_arg a sk:Argument ;
    sk:argumentName "file" ;
    sk:isRequired true ;
    sk:type "Path" ;
    sk:description "RDF file to validate" ;
    sk:help "Path to .ttl, .rdf, or .owl file" .

sk:validate_strict_arg a sk:Argument ;
    sk:argumentName "strict" ;
    sk:isRequired false ;
    sk:type "Bool" ;
    sk:defaultValue false ;
    sk:description "Enable strict validation mode" .

# Options
sk:validate_output_opt a sk:Option ;
    sk:optionName "output" ;
    sk:shortName "o" ;
    sk:type "Path" ;
    sk:description "Output file for validation report" ;
    sk:defaultValue null .
```

### Step 2: Create SPARQL Query

**File**: `sparql/command-query.rq`

The query extracts command metadata from RDF:

```sparql
PREFIX sk: <http://spec-kit.io/ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT
  ?commandName
  ?description
  ?longDescription
  ?category
  (GROUP_CONCAT(?argName; separator=", ") AS ?arguments)
  (GROUP_CONCAT(?optName; separator=", ") AS ?options)
  (GROUP_CONCAT(?exitCode; separator=", ") AS ?exitCodes)
WHERE {
  ?cmd a sk:Command ;
       rdfs:label ?commandName ;
       sk:description ?description .

  OPTIONAL {
    ?cmd sk:longDescription ?longDescription .
  }
  OPTIONAL {
    ?cmd sk:category ?category .
  }

  OPTIONAL {
    ?cmd sk:hasArgument ?arg .
    ?arg sk:argumentName ?argName .
  }

  OPTIONAL {
    ?cmd sk:hasOption ?opt .
    ?opt sk:optionName ?optName .
  }

  OPTIONAL {
    ?cmd sk:returnsExitCode ?exitCode .
  }
}
GROUP BY ?commandName ?description ?longDescription ?category
ORDER BY ?commandName
```

### Step 3: Create Command Template

**File**: `templates/command.tera`

The template generates Python code:

```python
# GENERATED: {{ commandName }}
# DO NOT EDIT MANUALLY - Run `ggen sync` to regenerate
# Source: ontology/cli-commands.ttl
# Generated: {{ "now" | date(format="%Y-%m-%d %H:%M:%S UTC") }}

\"\"\"CLI command: {{ commandName }}

{{ description }}

{% if longDescription %}
Detailed Description:
  {{ longDescription }}
{% endif %}
\"\"\"

import typer
from pathlib import Path
from typing import Optional
from specify_cli.core.telemetry import span
from specify_cli.ops import {{ commandName }}

app = typer.Typer()


@app.command()
def main(
    file: Path = typer.Argument(..., help="RDF file to validate"),
    strict: bool = typer.Option(False, help="Enable strict validation mode"),
    output: Optional[Path] = typer.Option(None, help="Output file for validation report"),
) -> int:
    \"\"\"{{ description }}\"\"\"
    with span("command.{{ commandName }}", {"file": str(file), "strict": strict}):
        result = {{ commandName }}.execute(
            file=file,
            strict=strict,
            output=output,
        )

        if result.success:
            typer.echo(f"✓ Validation passed: {file}")
            return 0
        else:
            typer.echo(f"✗ Validation failed: {file}")
            if result.errors:
                for error in result.errors:
                    typer.echo(f"  Error: {error}", err=True)
            return 1


if __name__ == "__main__":
    exit(main())
```

### Step 4: Create Test Template

**File**: `templates/command-test.tera`

The template generates pytest tests:

```python
# GENERATED: tests for {{ commandName }} command
# DO NOT EDIT MANUALLY - Run `ggen sync` to regenerate

\"\"\"Tests for {{ commandName }} CLI command.

{{ description }}
\"\"\"

import pytest
from pathlib import Path
from specify_cli.commands import {{ commandName }}


class TestValidateCommand:
    \"\"\"Test suite for {{ commandName }} command.\"\"\"

    def test_validate_valid_file(self, tmp_path: Path):
        \"\"\"Test validation of a valid RDF file.\"\"\"
        # Create a valid RDF file
        rdf_file = tmp_path / "valid.ttl"
        rdf_file.write_text("""
            @prefix ex: <http://example.com/> .
            ex:Person a rdfs:Class ;
                rdfs:label "Person" .
        """)

        result = {{ commandName }}.execute(file=rdf_file, strict=False)
        assert result.success, f"Validation should pass: {result.errors}"

    def test_validate_invalid_file(self, tmp_path: Path):
        \"\"\"Test validation of an invalid RDF file.\"\"\"
        # Create an invalid RDF file (bad syntax)
        rdf_file = tmp_path / "invalid.ttl"
        rdf_file.write_text("@prefix ex: <http://example.com/ .")  # Missing >

        result = {{ commandName }}.execute(file=rdf_file, strict=False)
        assert not result.success, "Validation should fail for invalid RDF"

    def test_validate_strict_mode(self, tmp_path: Path):
        \"\"\"Test validation in strict mode.\"\"\"
        rdf_file = tmp_path / "test.ttl"
        rdf_file.write_text("""
            @prefix ex: <http://example.com/> .
            ex:Person a rdfs:Class .  # Warning: no label
        """)

        result = {{ commandName }}.execute(file=rdf_file, strict=True)
        # Strict mode should fail on warnings
        assert not result.success, "Strict mode should fail on warnings"

    def test_validate_with_output(self, tmp_path: Path):
        \"\"\"Test validation with output report.\"\"\"
        rdf_file = tmp_path / "test.ttl"
        rdf_file.write_text("""
            @prefix ex: <http://example.com/> .
            ex:Person a rdfs:Class ;
                rdfs:label "Person" .
        """)

        output_file = tmp_path / "report.json"
        result = {{ commandName }}.execute(
            file=rdf_file,
            strict=False,
            output=output_file
        )

        assert result.success
        assert output_file.exists(), "Output report should be created"
        report = output_file.read_text()
        assert "validate" in report.lower()
```

### Step 5: Update ggen.toml Configuration

**File**: `docs/ggen.toml`

Add transformations for the new command (already exists - this is what the configuration manages):

```toml
[[transformations.code]]
name = "cli-validate-command"
description = "Generate validate.py command from CLI ontology"
input_files = ["ontology/cli-commands.ttl"]
schema_files = ["ontology/spec-kit-schema.ttl", "ontology/cli-schema.ttl"]
sparql_query = "sparql/command-query.rq"
sparql_params = { command_name = "validate" }
template = "templates/command.tera"
output_file = "src/specify_cli/commands/validate.py"
deterministic = true

[[transformations.code]]
name = "cli-validate-tests"
description = "Generate validate command tests from CLI ontology"
input_files = ["ontology/cli-commands.ttl"]
schema_files = ["ontology/spec-kit-schema.ttl", "ontology/cli-schema.ttl"]
sparql_query = "sparql/command-query.rq"
sparql_params = { command_name = "validate" }
template = "templates/command-test.tera"
output_file = "tests/e2e/test_commands_validate.py"
deterministic = true
```

### Step 6: Run ggen to Generate Code

```bash
cd /home/user/ggen-spec-kit

# Preview what will be generated
ggen sync --dry-run

# Generate the command, tests, and other artifacts
ggen sync --verbose
```

### Step 7: Generated Output

**Generated File**: `src/specify_cli/commands/validate.py`

```python
# GENERATED: validate
# DO NOT EDIT MANUALLY - Run `ggen sync` to regenerate
# Source: ontology/cli-commands.ttl
# Generated: 2025-01-01 14:30:00 UTC

"""CLI command: validate

Validate RDF specification files

Detailed Description:
  Validates RDF ontology files against SHACL shapes and checks for semantic consistency
"""

import typer
from pathlib import Path
from typing import Optional
from specify_cli.core.telemetry import span
from specify_cli.ops import validate

app = typer.Typer()


@app.command()
def main(
    file: Path = typer.Argument(..., help="RDF file to validate"),
    strict: bool = typer.Option(False, help="Enable strict validation mode"),
    output: Optional[Path] = typer.Option(None, help="Output file for validation report"),
) -> int:
    """Validate RDF specification files"""
    with span("command.validate", {"file": str(file), "strict": strict}):
        result = validate.execute(
            file=file,
            strict=strict,
            output=output,
        )

        if result.success:
            typer.echo(f"✓ Validation passed: {file}")
            return 0
        else:
            typer.echo(f"✗ Validation failed: {file}")
            if result.errors:
                for error in result.errors:
                    typer.echo(f"  Error: {error}", err=True)
            return 1


if __name__ == "__main__":
    exit(main())
```

**Generated Test File**: `tests/e2e/test_commands_validate.py`

```python
# GENERATED: tests for validate command
# DO NOT EDIT MANUALLY - Run `ggen sync` to regenerate

"""Tests for validate CLI command.

Validate RDF specification files
"""

import pytest
from pathlib import Path
from specify_cli.commands import validate


class TestValidateCommand:
    """Test suite for validate command."""

    def test_validate_valid_file(self, tmp_path: Path):
        """Test validation of a valid RDF file."""
        # Create a valid RDF file
        rdf_file = tmp_path / "valid.ttl"
        rdf_file.write_text("""
            @prefix ex: <http://example.com/> .
            ex:Person a rdfs:Class ;
                rdfs:label "Person" .
        """)

        result = validate.execute(file=rdf_file, strict=False)
        assert result.success, f"Validation should pass: {result.errors}"

    # ... other tests ...
```

**Receipt File**: `src/specify_cli/commands/validate.py.receipt.json`

```json
{
  "file": "src/specify_cli/commands/validate.py",
  "source": "ontology/cli-commands.ttl",
  "sparql_query": "sparql/command-query.rq",
  "template": "templates/command.tera",
  "hash": "sha256:a3c8f2e9d1b4c6f8e2a4b6d8f1a3c5e7f9a1b3d5",
  "timestamp": "2025-01-01T14:30:00Z",
  "pipeline": ["normalize", "extract", "emit", "canonicalize", "receipt"],
  "deterministic": true,
  "proof": "spec.md = μ(specification.ttl)"
}
```

### Step 8: Implement Business Logic (Manual Code)

Now we implement the actual business logic in the `ops/` layer:

**File**: `src/specify_cli/ops/validate.py`

```python
"""Validation operation layer.

Pure business logic for RDF validation.
No side effects - returns structured data.
"""

from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ValidationResult:
    """Result of validation operation."""

    success: bool
    errors: List[str]
    warnings: List[str]
    report: Optional[dict] = None


def execute(
    file: Path,
    strict: bool = False,
    output: Optional[Path] = None,
) -> ValidationResult:
    """Validate RDF specification.

    Parameters
    ----------
    file : Path
        RDF file to validate
    strict : bool, optional
        Enable strict validation mode
    output : Path, optional
        Output file for validation report

    Returns
    -------
    ValidationResult
        Validation result with errors and warnings
    """
    errors: List[str] = []
    warnings: List[str] = []

    # Check file exists
    if not file.exists():
        errors.append(f"File not found: {file}")
        return ValidationResult(success=False, errors=errors, warnings=warnings)

    # Parse RDF
    try:
        from rdflib import Graph
        graph = Graph()
        graph.parse(file, format="turtle")
    except Exception as e:
        errors.append(f"Invalid RDF syntax: {e}")
        return ValidationResult(success=False, errors=errors, warnings=warnings)

    # Validate against SHACL shapes
    try:
        # Load SHACL shapes
        shapes_graph = Graph()
        shapes_graph.parse("ontology/spec-kit-schema.ttl", format="turtle")

        # Run SHACL validation
        from pyshacl import validate
        conforms, report_graph, report_text = validate(graph, shapesgraph=shapes_graph)

        if not conforms:
            errors.append(f"SHACL validation failed:\n{report_text}")
    except Exception as e:
        errors.append(f"SHACL validation error: {e}")

    # Success if no errors (or just warnings in non-strict mode)
    success = len(errors) == 0
    if strict and warnings:
        success = False

    return ValidationResult(
        success=success,
        errors=errors,
        warnings=warnings,
        report={
            "file": str(file),
            "conforms": success,
            "errors": errors,
            "warnings": warnings,
        }
    )
```

### Step 9: Run Tests

```bash
# Run generated tests
uv run pytest tests/e2e/test_commands_validate.py -v

# All tests
uv run pytest tests/ -v
```

### Step 10: Commit Both RDF and Generated Code

```bash
# Stage RDF source
git add ontology/cli-commands.ttl

# Stage generated code
git add src/specify_cli/commands/validate.py
git add tests/e2e/test_commands_validate.py

# Stage manual implementation
git add src/specify_cli/ops/validate.py

# Commit with message explaining the change
git commit -m "feat(validate): add RDF validation command

- Added validate command to CLI specification (ontology/cli-commands.ttl)
- Generated command interface and tests via ggen sync
- Implemented validation logic in ops layer

Implements constitutional equation:
  command.py = μ(cli-commands.ttl)
  test_command.py = μ(cli-commands.ttl)

Verified: SHA256 receipts prove deterministic generation"
```

## Key Takeaways

1. **RDF is the Source** - All changes start with editing RDF specifications
2. **SPARQL Extracts Data** - Queries pull relevant facts from RDF
3. **Templates Generate Code** - Tera produces Python, tests, docs
4. **ggen Automates** - Single command regenerates everything
5. **Manual Code is Minimal** - Only business logic layer (ops/) is manual
6. **Receipts Prove Correctness** - SHA256 verifies `code.py = μ(spec.ttl)`

## Verification

Verify the transformation is correct:

```bash
# Check receipt
cat src/specify_cli/commands/validate.py.receipt.json

# Verify determinism (rerun ggen)
ggen sync

# Files should be identical
git diff --quiet && echo "✓ Deterministic generation verified"

# Run tests
uv run pytest tests/e2e/test_commands_validate.py

# Check type hints
mypy src/specify_cli/commands/validate.py

# Lint
ruff check src/specify_cli/commands/validate.py
```

## Summary

This example shows the complete workflow:

```
1. Edit RDF             ontology/cli-commands.ttl
                              ↓
2. Create SPARQL        sparql/command-query.rq
                              ↓
3. Create Template      templates/command.tera
                              ↓
4. Run ggen sync    ← μ₁ Normalize
                       μ₂ Extract (SPARQL)
                       μ₃ Emit (Tera)
                       μ₄ Canonicalize
                       μ₅ Receipt (SHA256)
                              ↓
5. Generated Code       src/specify_cli/commands/validate.py
                        tests/e2e/test_commands_validate.py
                        receipt.json
                              ↓
6. Manual Logic         src/specify_cli/ops/validate.py
                              ↓
7. Test & Commit        git commit with proof
```

This is the **spec-driven development** workflow powered by ggen!
