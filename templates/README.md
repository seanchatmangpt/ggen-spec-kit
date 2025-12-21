# Spec-Kit Templates

This directory contains Tera templates for RDF-driven code generation using the ggen ontology compiler.

## Overview

Templates transform RDF specifications into production-ready code following the constitutional equation:

```
output = μ(specification.ttl)
```

Where μ is the five-stage transformation pipeline implemented by ggen.

## Available Templates

### Documentation Templates

| Template | Purpose | Input | Output |
|----------|---------|-------|--------|
| `changelog.tera` | Generate CHANGELOG.md | `changelog.ttl` | `CHANGELOG.md` |
| `philosophy.tera` | Generate philosophy docs | `philosophy.ttl` | `spec-driven.md` |
| `constitution.tera` | Generate project constitution | `constitution.ttl` | `constitution.md` |
| `guide.tera` | Generate user guides | `guide.ttl` | `docs/*.md` |
| `plan.tera` | Generate implementation plans | `tasks.ttl` | `plan.md` |
| `tasks.tera` | Generate task breakdowns | `tasks.ttl` | `tasks.md` |

### Code Generation Templates

| Template | Purpose | Input | Output |
|----------|---------|-------|--------|
| `ggen/python-dataclass.tera` | Python dataclasses | `schema/*.ttl` | `src/generated/*.py` |
| `ggen/rust-struct.tera` | Rust structs | `schema/*.ttl` | `src/generated/*.rs` |
| `ggen/typescript-interface.tera` | TypeScript interfaces | `schema/*.ttl` | `src/generated/*.ts` |

### Test Generation Templates

| Template | Purpose | Input | Output |
|----------|---------|-------|--------|
| **`command-test.tera`** | **Pytest CLI tests** | **`cli-commands.ttl`** | **`tests/e2e/test_commands_*.py`** |

## Command Test Template

### Purpose

Automatically generates comprehensive E2E tests for CLI commands from RDF specifications.

### Constitutional Equation

```
test_commands_*.py = μ(cli-commands.ttl)
```

### Features

✅ **Comprehensive Test Coverage**
- Help command tests
- Argument validation tests
- Option/flag tests
- Error case tests
- Output format tests (JSON, verbose)
- Integration tests
- Environment variable tests

✅ **Quality Standards**
- 100% type hints
- NumPy-style docstrings
- Pytest markers (@pytest.mark.e2e)
- CliRunner for E2E testing
- Proper mocking (ops/runtime layers)
- Exit code validation

✅ **Error Handling**
- Keyboard interrupt (Ctrl+C)
- Missing required arguments
- Invalid argument values
- Conflicting options
- Unexpected exceptions

### Quick Start

**1. Create RDF specification** (`ontology/cli-commands.ttl`):

```turtle
@prefix sk: <http://github.com/github/spec-kit#> .

sk:CheckCommand a sk:CLICommand ;
    sk:commandName "check" ;
    sk:commandDescription "Check for required and optional tools" ;
    sk:hasOption sk:VerboseOption ;
    sk:hasErrorCase sk:MissingToolsError .

sk:VerboseOption a sk:CommandOption ;
    sk:optionName "--verbose" ;
    sk:optionType "flag" ;
    sk:optionDescription "Show detailed information" .

sk:MissingToolsError a sk:CommandErrorCase ;
    sk:errorId "missing-tools" ;
    sk:errorScenario "Required tools not installed" ;
    sk:errorExpectedExitCode 1 .
```

**2. Generate tests**:

```bash
ggen sync --config docs/ggen.toml
```

**3. Run generated tests**:

```bash
pytest tests/e2e/test_commands_check.py -v -m e2e
```

### Generated Test Structure

```python
"""E2E tests for specify check command.

Auto-generated from: ontology/cli-commands.ttl
⚠️  DO NOT EDIT MANUALLY
"""

from __future__ import annotations
import pytest
from typer.testing import CliRunner
from specify_cli.app import app

runner = CliRunner()


@pytest.mark.e2e
def test_check_help() -> None:
    """Test check --help shows usage information."""
    result = runner.invoke(app, ["check", "--help"])
    assert result.exit_code == 0


@pytest.mark.e2e
def test_check_option_verbose() -> None:
    """Test check with --verbose option."""
    # Generated test implementation
    pass


@pytest.mark.e2e
def test_check_error_missing_tools() -> None:
    """Test check handles missing tools error."""
    # Generated test implementation
    pass
```

### RDF Vocabulary

#### Command Definition
```turtle
sk:MyCommand a sk:CLICommand ;
    sk:commandName "command-name" ;           # Required
    sk:commandDescription "Description" ;     # Required
    sk:commandGroup "group" ;                 # Optional
    sk:hasArgument sk:MyArg ;                 # Optional
    sk:hasOption sk:MyOpt ;                   # Optional
    sk:hasErrorCase sk:MyError .              # Optional
```

#### Arguments (Positional)
```turtle
sk:MyArg a sk:CommandArgument ;
    sk:argumentName "arg_name" ;              # Required
    sk:argumentType "string" ;                # Required: string, int, path, etc.
    sk:argumentRequired "true" ;              # Required: "true" or "false"
    sk:argumentPosition 0 ;                   # Required: 0-indexed
    sk:argumentDescription "Help text" ;      # Optional
    sk:argumentDefaultTestValue "test" .      # Optional
```

#### Options (Flags/Named)
```turtle
sk:MyOpt a sk:CommandOption ;
    sk:optionName "--option" ;                # Required
    sk:optionShortFlag "-o" ;                 # Optional
    sk:optionType "flag" ;                    # Required: flag, string, int, etc.
    sk:optionDefault "false" ;                # Optional
    sk:optionDescription "Help text" ;        # Optional
    sk:optionTestValue "test" ;               # Optional
    sk:optionExpectedBehavior "Does X" .      # Optional
```

#### Error Cases
```turtle
sk:MyError a sk:CommandErrorCase ;
    sk:errorId "error-id" ;                   # Required: unique ID
    sk:errorScenario "What causes it" ;       # Required: description
    sk:errorExpectedBehavior "Expected" ;     # Required: behavior
    sk:errorExpectedExitCode 1 ;              # Optional: exit code
    sk:errorException "RuntimeError" ;        # Optional: exception class
    sk:errorExpectedOutput "error text" .     # Optional: output substring
```

### Files

| File | Purpose |
|------|---------|
| `templates/command-test.tera` | Test generation template |
| `sparql/command-test-query.rq` | SPARQL query to extract data |
| `ontology/cli-command-shapes.ttl` | SHACL validation shapes |
| `docs/examples/cli-command-spec-example.ttl` | Example specification |
| `docs/COMMAND_TEST_GENERATION.md` | Complete documentation |

### Validation (μ₁)

SHACL shapes validate RDF specifications:

```bash
# Validate command specifications
shacl validate \
  -s ontology/cli-command-shapes.ttl \
  -d ontology/cli-commands.ttl
```

**Validation Rules:**
- ✓ Command name is lowercase with hyphens
- ✓ Command description is at least 10 characters
- ✓ Argument types are valid (string, int, path, etc.)
- ✓ Option names start with `--`
- ✓ Error IDs are unique and lowercase
- ✓ Exit codes are between 0-255

### SPARQL Query (μ₂)

Extract command metadata with `sparql/command-test-query.rq`:

```sparql
PREFIX sk: <http://github.com/github/spec-kit#>

SELECT ?command_name ?command_description
       ?arg_name ?arg_type ?arg_required
       ?opt_name ?opt_type
       ?error_id ?error_scenario
WHERE {
    ?command a sk:CLICommand ;
        sk:commandName ?command_name ;
        sk:commandDescription ?command_description .
    # ... additional patterns
}
```

### Template Rendering (μ₃)

Tera template with control flow and filters:

```tera
{# Generate test for each option #}
{% for opt in options %}
@pytest.mark.e2e
def test_{{ command_name }}_option_{{ opt.name | replace("-", "_") }}() -> None:
    """Test {{ command_name }} with {{ opt.name }} option."""
    # Generated test code
{% endfor %}
```

**Available Filters:**
- `replace(from, to)` - String replacement
- `lower` - Convert to lowercase
- `title` - Convert to title case
- `trim_start_matches(pat)` - Remove prefix
- `default(value)` - Default value
- `length` - Get length
- `filter(attribute, value)` - Filter arrays
- `sort(attribute)` - Sort arrays
- `unique(attribute)` - Remove duplicates

### Formatting (μ₄)

Generated code is formatted with Ruff:

```bash
# Automatic formatting
ruff format tests/e2e/test_commands_*.py

# Check formatting
ruff check tests/e2e/test_commands_*.py
```

### Verification (μ₅)

Validate generated tests:

```bash
# Collect tests (validates syntax)
pytest tests/e2e/test_commands_*.py --collect-only

# Run tests
pytest tests/e2e/test_commands_*.py -v -m e2e

# Check coverage
pytest tests/e2e/ --cov=src/specify_cli/commands --cov-report=term-missing
```

## Template Development

### Best Practices

1. **Use Comments**
   ```tera
   {# Explain complex logic #}
   {% for item in items %}
       {# Process each item #}
   {% endfor %}
   ```

2. **Provide Defaults**
   ```tera
   {{ value | default(value="default-value") }}
   ```

3. **Filter and Sort**
   ```tera
   {% set required_args = arguments | filter(attribute="required", value="true") %}
   {% set sorted_opts = options | sort(attribute="name") %}
   ```

4. **Generate Clean Output**
   ```tera
   {# Remove trailing whitespace #}
   {% for item in items -%}
       {{ item.name }}
   {%- endfor %}
   ```

5. **Type Safety**
   ```tera
   def function(arg: {{ arg.type | default(value="Any") }}) -> None:
   ```

### Testing Templates

1. **Create minimal RDF spec**
2. **Generate output with `ggen sync`**
3. **Verify output structure**
4. **Run generated code**
5. **Iterate on template**

### Debugging

**Problem: Template syntax error**
```bash
ggen sync --config docs/ggen.toml --debug
```

**Problem: SPARQL returns no results**
```bash
# Test SPARQL query
oxigraph query --file ontology/cli-commands.ttl sparql/command-test-query.rq
```

**Problem: Generated code has syntax errors**
```bash
# Validate generated Python
ruff check tests/e2e/test_commands_*.py --show-source
```

## Configuration

### ggen.toml

```toml
[project]
name = "spec-kit-templates"
version = "0.1.0"

[generation]
ontology_dir = "ontology/"
templates_dir = "templates/"
output_dir = "."

# Test generation
[[generation.templates]]
name = "command-test"
template = "command-test.tera"
query = "sparql/command-test-query.rq"
output_pattern = "tests/e2e/test_commands_{command_name}.py"
format_with = "ruff"
validate_with = "pytest --collect-only"
```

## Examples

### Generate All Documentation

```bash
# Generate from all TTL files
ggen sync --config docs/ggen.toml

# Outputs:
# - CHANGELOG.md
# - constitution.md
# - spec-driven.md
# - tasks.md
# - tests/e2e/test_commands_*.py
```

### Generate Single Template

```bash
# Generate only command tests
ggen sync \
  --template templates/command-test.tera \
  --query sparql/command-test-query.rq \
  --data ontology/cli-commands.ttl \
  --output tests/e2e/
```

### Watch Mode (Development)

```bash
# Auto-regenerate on file changes
ggen watch --config docs/ggen.toml
```

## Resources

- [ggen Documentation](ggen/README.md)
- [Command Test Generation Guide](../docs/COMMAND_TEST_GENERATION.md)
- [Example Specifications](../docs/examples/)
- [Tera Template Syntax](https://tera.netlify.app/docs/)
- [SPARQL Tutorial](https://www.w3.org/TR/sparql11-query/)
- [SHACL Validation](https://www.w3.org/TR/shacl/)

## See Also

- [Spec-Kit Philosophy](../docs/spec-driven.md)
- [Constitutional Equation](../docs/constitution.md)
- [Three-Tier Architecture](../CLAUDE.md)

---

**Constitutional Equation**: `output = μ(specification.ttl)`

*Templates are the μ operator that transforms RDF knowledge into executable code.*
