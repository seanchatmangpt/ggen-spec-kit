# Command Test Generation from RDF

**Constitutional Equation**: `test_commands_*.py = μ(cli-commands.ttl)`

This document explains how to automatically generate comprehensive pytest test files from RDF command specifications using the ggen ontology compiler.

## Overview

The command test generation system follows the constitutional equation where:
- **Source of Truth**: RDF command specification (`.ttl` files)
- **Transformation**: Five-stage μ operator (ggen pipeline)
- **Output**: Production-ready pytest test files with 100% type hints

### The μ Transformation

```
μ₁: Validate RDF with SHACL shapes
μ₂: Execute SPARQL query (command-test-query.rq)
μ₃: Render Tera template (command-test.tera)
μ₄: Format with Ruff (Python formatter)
μ₅: Verify with pytest --collect-only
```

## File Structure

```
ggen-spec-kit/
├── ontology/
│   └── cli-commands.ttl          # Command specifications (source of truth)
├── sparql/
│   └── command-test-query.rq     # SPARQL query to extract test data
├── templates/
│   └── command-test.tera          # Tera template for test generation
├── tests/e2e/
│   ├── test_commands_check.py    # Generated test file ✨
│   └── test_commands_init.py     # Generated test file ✨
└── docs/
    ├── ggen.toml                  # ggen configuration
    └── examples/
        └── cli-command-spec-example.ttl  # Example specification
```

## Quick Start

### 1. Create RDF Command Specification

Create `ontology/cli-commands.ttl`:

```turtle
@prefix sk: <http://github.com/github/spec-kit#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Define the command
sk:CheckCommand a sk:CLICommand ;
    sk:commandName "check" ;
    sk:commandGroup "tools" ;
    sk:commandDescription "Check for required and optional tools" ;

    # Add options
    sk:hasOption sk:CheckVerboseOption ;
    sk:hasOption sk:CheckJsonOption ;

    # Add error cases
    sk:hasErrorCase sk:CheckMissingToolsError .

# Define an option
sk:CheckVerboseOption a sk:CommandOption ;
    sk:optionName "--verbose" ;
    sk:optionShortFlag "-v" ;
    sk:optionType "flag" ;
    sk:optionDescription "Show detailed information" .

# Define an error case
sk:CheckMissingToolsError a sk:CommandErrorCase ;
    sk:errorId "missing-tools" ;
    sk:errorScenario "Required tools not installed" ;
    sk:errorExpectedExitCode 1 ;
    sk:errorExpectedOutput "required tool(s) missing" .
```

### 2. Generate Tests

```bash
# Generate tests from RDF specification
ggen sync --config docs/ggen.toml

# Verify generated tests
pytest tests/e2e/test_commands_check.py --collect-only

# Run generated tests
pytest tests/e2e/test_commands_check.py -v -m e2e
```

### 3. Generated Output

The system generates production-ready test files like:

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
    assert "check" in result.stdout.lower()


@pytest.mark.e2e
def test_check_option_verbose() -> None:
    """Test check with --verbose option."""
    # ... generated test code
```

## RDF Vocabulary Reference

### Command Definition

```turtle
sk:MyCommand a sk:CLICommand ;
    sk:commandName "command-name" ;           # Required: CLI command name
    sk:commandGroup "group" ;                 # Optional: Command category
    sk:commandDescription "Description" ;     # Required: Brief description
    sk:commandPurpose "Purpose text" .        # Optional: Detailed purpose
```

### Arguments (Positional Parameters)

```turtle
sk:MyCommand sk:hasArgument sk:MyArgument .

sk:MyArgument a sk:CommandArgument ;
    sk:argumentName "arg_name" ;              # Required: Argument name
    sk:argumentType "string" ;                # Required: Type (string, path, int)
    sk:argumentRequired "true" ;              # Required: Boolean string
    sk:argumentPosition 0 ;                   # Required: Position (0-indexed)
    sk:argumentDescription "Description" ;    # Optional: Help text
    sk:argumentDefaultTestValue "test-val" .  # Optional: Test value
```

### Options (Flags and Named Parameters)

```turtle
sk:MyCommand sk:hasOption sk:MyOption .

sk:MyOption a sk:CommandOption ;
    sk:optionName "--option" ;                # Required: Full option name
    sk:optionShortFlag "-o" ;                 # Optional: Short flag
    sk:optionType "flag" ;                    # Required: flag, string, int, etc.
    sk:optionDefault "false" ;                # Optional: Default value
    sk:optionDescription "Description" ;      # Optional: Help text
    sk:optionTestValue "test" ;               # Optional: Test value
    sk:optionExpectedBehavior "What it does" . # Optional: Behavior description
```

### Error Cases

```turtle
sk:MyCommand sk:hasErrorCase sk:MyError .

sk:MyError a sk:CommandErrorCase ;
    sk:errorId "error-id" ;                   # Required: Unique error ID
    sk:errorScenario "Scenario description" ; # Required: What causes error
    sk:errorTrigger "How to trigger" ;        # Optional: Trigger condition
    sk:errorExpectedBehavior "Expected" ;     # Required: Expected behavior
    sk:errorExpectedExitCode 1 ;              # Optional: Exit code (default: 1)
    sk:errorException "RuntimeError" ;        # Optional: Exception class
    sk:errorExceptionModule "module.path" ;   # Optional: Exception module
    sk:errorMessage "Error message" ;         # Optional: Error message text
    sk:errorCommandArgs '["cmd", "arg"]' ;    # Optional: Command args as JSON
    sk:errorExpectedOutput "expected text" ;  # Optional: Output substring
    sk:errorMockSetup "mock code" .           # Optional: Mock setup code
```

### Expected Output Fields

```turtle
sk:MyCommand sk:hasExpectedOutputField sk:MyField .

sk:MyField a sk:OutputField ;
    sk:fieldName "field_name" ;               # Required: Field name
    sk:fieldTestValue "test_value" .          # Required: Test value
```

## Generated Test Coverage

Each command specification generates comprehensive tests:

### ✅ Automatically Generated Tests

1. **Help and Documentation**
   - `test_{command}_help()` - Verifies --help output

2. **Basic Execution**
   - `test_{command}_basic_execution()` - Tests minimal valid invocation

3. **Arguments** (one test per argument)
   - `test_{command}_argument_{arg_name}()` - Tests each argument
   - `test_{command}_argument_{arg_name}_invalid_path()` - For path arguments

4. **Options** (one test per option)
   - `test_{command}_option_{opt_name}()` - Tests each option
   - Parametrized tests for multiple flags

5. **Error Cases** (one test per error case)
   - `test_{command}_error_{error_id}()` - Tests each error scenario
   - `test_{command}_keyboard_interrupt()` - Ctrl+C handling
   - `test_{command}_unexpected_exception()` - Unexpected errors

6. **Output Formats**
   - `test_{command}_json_output()` - JSON format validation
   - `test_{command}_verbose_output()` - Verbose mode tests

7. **Integration**
   - `test_{command}_full_workflow()` - End-to-end workflow
   - `test_{command}_respects_environment_variables()` - Environment tests

## Test Quality Standards

All generated tests comply with Lean Six Sigma standards:

- ✅ **100% Type Hints**: All functions fully typed
- ✅ **NumPy Docstrings**: Complete documentation
- ✅ **Pytest Markers**: `@pytest.mark.e2e` for all tests
- ✅ **CliRunner**: E2E testing via Typer's CliRunner
- ✅ **Mocking**: Proper mocking of ops and runtime layers
- ✅ **Exit Codes**: Verifies 0=success, 1=failure, 130=interrupt
- ✅ **Error Messages**: Validates error output
- ✅ **JSON Validation**: Tests JSON output structure

## Workflow Examples

### Example 1: Add New Command Option

**Step 1**: Add option to RDF specification
```turtle
sk:CheckCommand sk:hasOption sk:CheckQuietOption .

sk:CheckQuietOption a sk:CommandOption ;
    sk:optionName "--quiet" ;
    sk:optionShortFlag "-q" ;
    sk:optionType "flag" ;
    sk:optionDescription "Suppress output" .
```

**Step 2**: Regenerate tests
```bash
ggen sync --config docs/ggen.toml
```

**Step 3**: Verify new test exists
```bash
pytest tests/e2e/test_commands_check.py::test_check_option_quiet -v
```

### Example 2: Add New Error Case

**Step 1**: Add error case to RDF
```turtle
sk:CheckCommand sk:hasErrorCase sk:CheckTimeoutError .

sk:CheckTimeoutError a sk:CommandErrorCase ;
    sk:errorId "timeout" ;
    sk:errorScenario "Tool check times out" ;
    sk:errorExpectedExitCode 1 ;
    sk:errorException "TimeoutError" ;
    sk:errorExpectedOutput "timeout" .
```

**Step 2**: Regenerate tests
```bash
ggen sync
```

**Step 3**: Run new error test
```bash
pytest tests/e2e/test_commands_check.py::test_check_error_timeout -v
```

## Benefits of RDF-First Testing

### 1. Single Source of Truth
- Command specification in RDF is canonical
- Tests are derived, never manually edited
- Changes to spec automatically update tests

### 2. Consistency
- All commands tested identically
- Uniform test structure across codebase
- Standard error handling patterns

### 3. Coverage
- Every argument automatically tested
- Every option automatically tested
- Every error case automatically tested
- Zero manual test writing

### 4. Maintainability
- Edit RDF once, regenerate all tests
- No manual test sync required
- Tests always match specification

### 5. Documentation
- RDF specification documents command behavior
- Generated tests serve as executable documentation
- Specifications are machine-readable and human-readable

## Configuration (ggen.toml)

Add test generation to your `docs/ggen.toml`:

```toml
[project]
name = "spec-kit-test-generation"
version = "0.1.0"

[generation]
ontology_dir = "ontology/"
templates_dir = "templates/"
output_dir = "tests/e2e/"

# Test generation configuration
[[generation.templates]]
name = "command-test"
template = "command-test.tera"
query = "sparql/command-test-query.rq"
output_pattern = "test_commands_{command_name}.py"
format_with = "ruff"
```

## Validation

The μ₅ stage validates generated tests:

```bash
# Collect tests (validates syntax and imports)
pytest tests/e2e/test_commands_*.py --collect-only

# Run all generated tests
pytest tests/e2e/test_commands_*.py -v -m e2e

# Check test coverage
pytest tests/e2e/test_commands_*.py --cov=src/specify_cli/commands
```

## Troubleshooting

### Problem: Generated tests fail to import

**Solution**: Check that:
1. Command name matches actual command module
2. Ops module exists: `src/specify_cli/ops/{command_name}.py`
3. Command is registered in `src/specify_cli/app.py`

### Problem: SPARQL query returns no results

**Solution**: Verify:
1. RDF syntax is valid: `rapper -i turtle ontology/cli-commands.ttl`
2. Required properties are present (commandName, commandDescription)
3. SPARQL query PREFIX declarations match ontology

### Problem: Template rendering fails

**Solution**: Check:
1. All SPARQL variables are defined in query
2. Template filters are valid (Tera syntax)
3. Template variables match SPARQL results

## Best Practices

### 1. Comprehensive Error Cases
Always specify common error scenarios:
- Missing required arguments
- Invalid argument values
- Conflicting options
- Keyboard interrupt
- Unexpected exceptions

### 2. Realistic Test Values
Provide meaningful `argumentDefaultTestValue` and `optionTestValue`:
```turtle
sk:argumentDefaultTestValue "test-project" .  # ✅ Realistic
sk:argumentDefaultTestValue "test-value" .    # ❌ Generic
```

### 3. Document Expected Behavior
Use `optionExpectedBehavior` and `errorExpectedBehavior`:
```turtle
sk:optionExpectedBehavior "Shows version info and paths" .
sk:errorExpectedBehavior "Exit with code 1 and show installation instructions" .
```

### 4. Complete Option Specifications
Always include:
- Option name (--option)
- Short flag if available (-o)
- Type (flag, string, int, path)
- Description
- Expected behavior

### 5. Verify Generated Tests
Always run generated tests before committing:
```bash
ggen sync && pytest tests/e2e/ -v -m e2e
```

## Advanced Usage

### Custom Tera Filters

Extend the template with custom filters:

```tera
{# Custom filter for snake_case to CamelCase #}
{{ command_name | title | replace("-", "") }}

{# Custom filter for default values #}
{{ arg.default_test_value | default(value="test-value") }}

{# Custom filter for lowercase matching #}
assert "{{ description[:50] | lower }}" in result.stdout.lower()
```

### Parametrized Tests

Generate parametrized tests for multiple scenarios:

```tera
@pytest.mark.parametrize(
    ("option_flag", "expected_behavior"),
    [
        {% for opt in options | filter(attribute="type", value="flag") %}
        ("{{ opt.name }}", "{{ opt.expected_behavior }}"),
        {% endfor %}
    ],
)
def test_options_parametrized(option_flag: str, expected_behavior: str) -> None:
    # Test implementation
```

### Mock Setup Code

Provide complex mock setups in RDF:

```turtle
sk:errorMockSetup """
with patch('specify_cli.runtime.tools.which_tool') as mock_which, \\
     patch('specify_cli.ops.check.get_tool_versions') as mock_versions:
    mock_which.return_value = None
    mock_versions.return_value = {}
""" .
```

## See Also

- [ggen Documentation](templates/ggen/README.md)
- [SPARQL Reference](https://www.w3.org/TR/sparql11-query/)
- [Tera Template Syntax](https://tera.netlify.app/docs/)
- [Example Specification](examples/cli-command-spec-example.ttl)

---

**Constitutional Equation**: `test_commands_*.py = μ(cli-commands.ttl)`

*Generated documentation adheres to spec.md = μ(feature.ttl)*
