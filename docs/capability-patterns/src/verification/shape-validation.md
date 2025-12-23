# 34. Shape Validation

★★

*Before transformation, validation. Shape validation uses SHACL to verify that specifications conform to their structural requirements—catching errors at the earliest possible point in the pipeline.*

---

## The Gatekeeper

Shape validation is the gatekeeper of the transformation pipeline. It stands at the entrance, examining every specification before processing begins. Only conformant specifications pass through; invalid ones are turned away with clear feedback.

The **[Normalization Stage](../transformation/normalization-stage.md)** described how validation works within transformation. Shape Validation is the verification practice that ensures validation happens consistently, comprehensively, and helpfully—not just as a pipeline step, but as a development discipline.

Without shape validation, invalid specifications can:
- Produce silent errors in generated code
- Cause cryptic template failures
- Generate artifacts that don't match expectations
- Propagate problems downstream where they're harder to diagnose

Shape validation catches these problems at the source—before they multiply.

---

## The Validation Problem

**The fundamental problem: Invalid specifications can produce subtle errors that propagate through the transformation pipeline. Shape validation catches structural problems before they cause downstream failures.**

Let us examine how invalid specifications cause problems:

### The Missing Required Field

```turtle
# Specification missing required 'name' field
cli:NewCommand a cli:Command ;
    cli:description "Does something" ;
    cli:hasArgument [ cli:type "Path" ] .  # Missing sk:name
```

Without validation, this might:
- Generate code with `None` where a name is expected
- Cause a template error when rendering `{{ command.name }}`
- Produce documentation with blank headings

With validation:
```
VIOLATION: Command must have a name
  Shape: sk:CommandShape
  Focus: cli:NewCommand
  Path: rdfs:label
  Fix: Add 'rdfs:label "command-name"' to cli:NewCommand
```

### The Wrong Type

```turtle
# Specification with wrong type
cli:ValidateCommand a cli:Command ;
    rdfs:label "validate" ;
    cli:acceptsArgument [
        sk:name "file" ;
        cli:type 42 ;  # Should be string, not integer
    ] .
```

Without validation, this might:
- Generate code that treats `42` as a type name
- Crash when the template expects a string
- Produce incorrect type annotations

### The Invalid Cardinality

```turtle
# Specification with multiple values where one expected
cli:CheckCommand a cli:Command ;
    rdfs:label "check" ;
    rdfs:label "verify" ;  # Only one label allowed!
    cli:description "Check tools" .
```

Without validation, templates might:
- Use the wrong label
- Generate duplicate entries
- Behave unpredictably

---

## The Forces

Several tensions shape validation practice:

### Force: Strictness vs. Flexibility

*Strict validation catches all errors. But strict validation blocks experimentation.*

During early development, you might want to iterate quickly without perfect specifications. Strict validation slows you down.

**Resolution:** Severity levels. Violations block transformation. Warnings inform but allow proceeding. Info messages provide guidance without blocking.

### Force: Early Detection vs. Development Flow

*Catching errors early is valuable. But validation interruptions disrupt flow.*

Running validation manually before every transformation is tedious. Forgetting to validate leads to late error discovery.

**Resolution:** Automatic validation. Integrate validation into `ggen sync`. Make validation invisible when specifications are correct, visible when they're not.

### Force: Helpful Feedback vs. Information Overload

*Detailed error messages help correction. But too much detail overwhelms.*

Showing 100 violations at once is unhelpful. But hiding details makes fixing difficult.

**Resolution:** Progressive disclosure. Show summary first (5 violations, 3 warnings). Allow drilling into details. Prioritize most critical issues.

### Force: Stable Shapes vs. Evolving Requirements

*Shapes should be stable for consistent validation. But requirements evolve.*

Changing shapes might invalidate existing specifications. Not changing shapes prevents improvement.

**Resolution:** Shape versioning. Backward-compatible additions don't break existing specs. Breaking changes require migration. Deprecation warnings before removal.

---

## Therefore

**Implement comprehensive shape validation with clear feedback, severity levels, and evolution support. Validation runs automatically before transformation, catching errors at the earliest possible point.**

Shape validation architecture:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  SHAPE VALIDATION ARCHITECTURE                                           │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ ENTRY POINT                                                         │ │
│  │                                                                     │ │
│  │  specify validate ontology/*.ttl                                   │ │
│  │  ggen sync (implicit validation)                                   │ │
│  │  Pre-commit hook                                                   │ │
│  └──────────────────────┬─────────────────────────────────────────────┘ │
│                         │                                                │
│                         ▼                                                │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ SHAPE LOADING                                                       │ │
│  │                                                                     │ │
│  │  Load shapes from shapes/ directory                                │ │
│  │  Merge with built-in shapes                                        │ │
│  │  Validate shapes themselves                                        │ │
│  └──────────────────────┬─────────────────────────────────────────────┘ │
│                         │                                                │
│                         ▼                                                │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ VALIDATION                                                          │ │
│  │                                                                     │ │
│  │  For each specification:                                           │ │
│  │    • Find applicable shapes (by sh:targetClass, sh:targetNode)     │ │
│  │    • Evaluate constraints                                          │ │
│  │    • Collect results by severity                                   │ │
│  └──────────────────────┬─────────────────────────────────────────────┘ │
│                         │                                                │
│                         ▼                                                │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ REPORTING                                                           │ │
│  │                                                                     │ │
│  │  Summary: N violations, M warnings, K info                         │ │
│  │  Details: Each violation with context and fix suggestion           │ │
│  │  Exit code: 0 if valid, 1 if violations                            │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## SHACL Shape Design

### Shape Structure

```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix sk: <https://spec-kit.org/ontology#> .
@prefix cli: <https://spec-kit.org/cli#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# ═══════════════════════════════════════════════════════════════════════════
# COMMAND SHAPE
# Validates CLI command specifications
# ═══════════════════════════════════════════════════════════════════════════

sk:CommandShape a sh:NodeShape ;
    sh:targetClass cli:Command ;

    # ─────────────────────────────────────────────────────────────────────────
    # Required: Command must have a name
    # ─────────────────────────────────────────────────────────────────────────
    sh:property [
        sh:path rdfs:label ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:datatype xsd:string ;
        sh:pattern "^[a-z][a-z0-9-]*$" ;
        sh:severity sh:Violation ;
        sh:message "Command must have exactly one name (rdfs:label) matching pattern [a-z][a-z0-9-]*"
    ] ;

    # ─────────────────────────────────────────────────────────────────────────
    # Recommended: Command should have a description
    # ─────────────────────────────────────────────────────────────────────────
    sh:property [
        sh:path sk:description ;
        sh:minCount 1 ;
        sh:datatype xsd:string ;
        sh:minLength 10 ;
        sh:severity sh:Warning ;
        sh:message "Command should have a description of at least 10 characters"
    ] ;

    # ─────────────────────────────────────────────────────────────────────────
    # Optional: Command may have examples
    # ─────────────────────────────────────────────────────────────────────────
    sh:property [
        sh:path sk:example ;
        sh:severity sh:Info ;
        sh:message "Consider adding usage examples for documentation"
    ] ;

    # ─────────────────────────────────────────────────────────────────────────
    # Arguments must be valid
    # ─────────────────────────────────────────────────────────────────────────
    sh:property [
        sh:path cli:acceptsArgument ;
        sh:node sk:ArgumentShape ;
        sh:severity sh:Violation ;
        sh:message "Invalid argument specification"
    ] .


# ═══════════════════════════════════════════════════════════════════════════
# ARGUMENT SHAPE
# Validates argument specifications
# ═══════════════════════════════════════════════════════════════════════════

sk:ArgumentShape a sh:NodeShape ;

    # Required: name
    sh:property [
        sh:path sk:name ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:datatype xsd:string ;
        sh:severity sh:Violation ;
        sh:message "Argument must have a name"
    ] ;

    # Required: type
    sh:property [
        sh:path cli:type ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:datatype xsd:string ;
        sh:in ("Path" "str" "int" "float" "bool") ;
        sh:severity sh:Violation ;
        sh:message "Argument must have a valid type (Path, str, int, float, bool)"
    ] ;

    # Optional but validated: description
    sh:property [
        sh:path sk:description ;
        sh:maxCount 1 ;
        sh:datatype xsd:string ;
        sh:severity sh:Warning ;
        sh:message "Argument should have a description"
    ] .
```

### Severity Levels

```turtle
# ═══════════════════════════════════════════════════════════════════════════
# SEVERITY LEVELS
# ═══════════════════════════════════════════════════════════════════════════

# sh:Violation (MUST fix)
# - Blocks transformation
# - Indicates non-conformant specification
# - Must be resolved before proceeding
# Example: Missing required field, wrong type

# sh:Warning (SHOULD fix)
# - Does not block transformation
# - Indicates best practice violation
# - Should be resolved for quality
# Example: Missing description, deprecated feature

# sh:Info (MAY fix)
# - Does not block transformation
# - Informational guidance
# - Optional improvements
# Example: Missing examples, documentation suggestions
```

---

## Validation Pipeline

### Validation Modes

```toml
# ggen.toml

[validation]
# Mode determines behavior on violations
# strict: Violations and warnings block transformation
# normal: Only violations block transformation (default)
# relaxed: Only violations block, warnings suppressed
# permissive: Nothing blocks, all logged
# off: No validation (dangerous!)
mode = "normal"

# Shapes to use
[validation.shapes]
paths = ["shapes/*.ttl"]
builtin = true  # Include built-in shapes

# Severity overrides
[validation.severity]
# Promote specific messages to violations
promote_to_violation = [
    "Missing description",  # Treat as violation
]

# Demote specific messages to info
demote_to_info = [
    "Consider adding examples",  # Treat as info only
]
```

### Validation Command

```python
# src/specify_cli/commands/validate.py
"""Validate command implementation."""

import typer
from pathlib import Path
from typing import Optional, List
from rich.console import Console
from rich.table import Table

from specify_cli import ops

app = typer.Typer()
console = Console()


@app.command()
def validate(
    files: List[Path] = typer.Argument(..., help="Files to validate"),
    shapes: Optional[Path] = typer.Option(None, "--shapes", "-s", help="Custom shapes"),
    strict: bool = typer.Option(False, "--strict", help="Treat warnings as errors"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Summary only"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """Validate RDF specifications against SHACL shapes.

    Examples:
        # Validate single file
        specify validate ontology/cli-commands.ttl

        # Validate with custom shapes
        specify validate ontology/*.ttl --shapes shapes/

        # Strict mode (warnings are errors)
        specify validate --strict ontology/*.ttl
    """
    result = ops.validate.execute(
        files=files,
        shapes_path=shapes,
        strict=strict,
    )

    if json_output:
        console.print_json(data=result)
        return

    # Display summary
    violations = len(result["violations"])
    warnings = len(result["warnings"])
    info = len(result["info"])

    if violations > 0:
        console.print(f"[red]✗ {violations} violation(s)[/red]", end=" ")
    if warnings > 0:
        console.print(f"[yellow]⚠ {warnings} warning(s)[/yellow]", end=" ")
    if info > 0:
        console.print(f"[blue]ℹ {info} info[/blue]", end=" ")

    if violations == 0 and (not strict or warnings == 0):
        console.print("[green]✓ Valid[/green]")

    console.print()

    # Display details unless quiet
    if not quiet:
        for v in result["violations"]:
            display_violation(v, "red", "✗")

        for w in result["warnings"]:
            display_violation(w, "yellow", "⚠")

        if not strict:
            for i in result["info"]:
                display_violation(i, "blue", "ℹ")

    # Exit code
    if violations > 0:
        raise typer.Exit(1)
    if strict and warnings > 0:
        raise typer.Exit(1)


def display_violation(violation: dict, color: str, symbol: str) -> None:
    """Display a single violation with context."""
    console.print(f"[{color}]{symbol}[/{color}] {violation['message']}")
    console.print(f"  Shape: {violation['shape']}")
    console.print(f"  Focus: {violation['focus_node']}")
    if violation.get('path'):
        console.print(f"  Path:  {violation['path']}")
    if violation.get('line'):
        console.print(f"  Line:  {violation['line']}")
    if violation.get('fix'):
        console.print(f"  [dim]Fix: {violation['fix']}[/dim]")
    console.print()
```

---

## Error Reporting

### Human-Readable Output

```
$ specify validate ontology/cli-commands.ttl

Validation Report: ontology/cli-commands.ttl
═══════════════════════════════════════════════════════════════════════════

✗ 2 violations  ⚠ 1 warning  ℹ 3 info

───────────────────────────────────────────────────────────────────────────
VIOLATION 1 of 2
───────────────────────────────────────────────────────────────────────────
  Shape:   sk:CommandShape
  Focus:   cli:NewCommand
  Path:    rdfs:label
  Line:    42

  Message: Command must have exactly one name (rdfs:label) matching
           pattern [a-z][a-z0-9-]*

  Fix:     Add 'rdfs:label "new-command"' to cli:NewCommand

───────────────────────────────────────────────────────────────────────────
VIOLATION 2 of 2
───────────────────────────────────────────────────────────────────────────
  Shape:   sk:ArgumentShape
  Focus:   _:b0 (argument of cli:NewCommand)
  Path:    cli:type
  Line:    47

  Message: Argument must have a valid type (Path, str, int, float, bool)

  Current: cli:type 42
  Fix:     Change to 'cli:type "Path"' or other valid type

───────────────────────────────────────────────────────────────────────────
WARNING 1 of 1
───────────────────────────────────────────────────────────────────────────
  Shape:   sk:CommandShape
  Focus:   cli:ValidateCommand
  Path:    sk:description

  Message: Command should have a description of at least 10 characters

  Current: sk:description "Validate"
  Fix:     Expand description to explain what the command does

═══════════════════════════════════════════════════════════════════════════

Validation failed with 2 violations.
Fix violations and run again.
```

### JSON Output

```json
{
  "valid": false,
  "violations": [
    {
      "shape": "sk:CommandShape",
      "focus_node": "cli:NewCommand",
      "path": "rdfs:label",
      "message": "Command must have exactly one name",
      "severity": "Violation",
      "line": 42,
      "fix": "Add 'rdfs:label \"new-command\"' to cli:NewCommand"
    }
  ],
  "warnings": [...],
  "info": [...],
  "summary": {
    "violations": 2,
    "warnings": 1,
    "info": 3
  }
}
```

---

## CI Integration

### GitHub Actions

```yaml
# .github/workflows/validate.yml
name: Validate Specifications

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install specify-cli
        run: pip install specify-cli

      - name: Validate RDF specifications
        run: |
          specify validate ontology/*.ttl --shapes shapes/

      - name: Upload validation report
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: validation-report
          path: validation-report.json
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: validate-rdf
        name: Validate RDF specifications
        entry: specify validate
        language: system
        files: '\.ttl$'
        args: ['--strict']
```

---

## Case Study: The Schema Evolution

*A team evolves their shapes while maintaining backward compatibility.*

### The Situation

The PlatformAPI team had hundreds of command specifications. They needed to add new validation rules without breaking existing specifications.

### The Challenge

New rule: Commands must specify their category (e.g., "admin", "user", "debug").

```turtle
# New shape rule
sh:property [
    sh:path sk:category ;
    sh:minCount 1 ;
    sh:in ("admin" "user" "debug" "internal") ;
    sh:severity sh:Violation ;
    sh:message "Command must specify a category"
] .
```

But existing commands don't have categories. Adding this as a violation would fail validation for 200+ commands.

### The Solution

**Phase 1: Add as Info**
```turtle
sh:property [
    sh:path sk:category ;
    sh:minCount 1 ;
    sh:severity sh:Info ;  # Start as info
    sh:message "Commands will require a category in v3.0"
] .
```

**Phase 2: Promote to Warning**
```turtle
sh:property [
    sh:path sk:category ;
    sh:minCount 1 ;
    sh:severity sh:Warning ;  # Now a warning
    sh:message "Command should specify a category (required in v3.0)"
] .
```

**Phase 3: Promote to Violation**
```turtle
sh:property [
    sh:path sk:category ;
    sh:minCount 1 ;
    sh:severity sh:Violation ;  # Now required
    sh:message "Command must specify a category"
] .
```

### The Results

| Phase | Duration | Compliance Rate |
|-------|----------|-----------------|
| Info (v2.8) | 2 weeks | 0% → 45% |
| Warning (v2.9) | 4 weeks | 45% → 95% |
| Violation (v3.0) | Release | 100% |

Gradual enforcement allowed teams to adapt without breaking builds.

---

## Anti-Patterns

### Anti-Pattern: All Violations

*"Everything must be validated strictly."*

Making all rules violations blocks development. Minor issues prevent any progress.

**Resolution:** Use appropriate severity. Violations for structural requirements. Warnings for best practices. Info for suggestions.

### Anti-Pattern: No Validation

*"Validation slows us down."*

Skipping validation allows invalid specifications to accumulate. Problems surface late.

**Resolution:** Automatic validation integrated into workflow. Fast validation doesn't slow development.

### Anti-Pattern: Vague Messages

*"Validation error in specification."*

Unhelpful messages make fixing difficult.

**Resolution:** Clear messages with:
- What's wrong
- Where it is (shape, focus node, path, line)
- How to fix it

### Anti-Pattern: Static Shapes

*"Shapes are set once."*

Requirements evolve. Static shapes become outdated or prevent improvement.

**Resolution:** Shape evolution process. Add rules gradually. Deprecate before removing. Version shapes.

---

## Implementation Checklist

### Shape Design

- [ ] Define shapes for all specification types
- [ ] Set appropriate severity levels
- [ ] Write clear error messages
- [ ] Include fix suggestions
- [ ] Document shape purpose

### Validation Pipeline

- [ ] Integrate validation into ggen sync
- [ ] Create validate command
- [ ] Support multiple output formats
- [ ] Configure severity overrides

### CI Integration

- [ ] Add validation to CI pipeline
- [ ] Configure pre-commit hooks
- [ ] Archive validation reports
- [ ] Block merges on violations

### Evolution Support

- [ ] Plan severity progression for new rules
- [ ] Deprecate before removing
- [ ] Document shape versions
- [ ] Migrate existing specifications

---

## Resulting Context

After implementing this pattern, you have:

- **Early detection of specification errors** before transformation
- **Clear feedback guiding corrections** with context and fix suggestions
- **Configurable severity for different contexts** supporting development and production
- **CI enforcement of specification quality** preventing invalid specs from merging
- **Evolution path for shapes** allowing improvement without breaking builds

Shape validation is the quality gate that ensures only valid specifications enter the transformation pipeline.

---

## Related Patterns

- **Implements:** **[12. Shape Constraint](../specification/shape-constraint.md)** — Shapes enforced
- **Part of:** **[22. Normalization Stage](../transformation/normalization-stage.md)** — Validation in pipeline
- **Enables:** **[37. Continuous Validation](./continuous-validation.md)** — CI validation
- **Supports:** **[35. Drift Detection](./drift-detection.md)** — Shapes prevent drift

---

## Philosophical Note

> *"The best error message is the one that never shows up."*

Shape validation catches errors before they cause problems. The earlier the detection, the cheaper the fix. An error caught during editing costs seconds. The same error caught in production costs hours.

But when errors do appear, the message matters. A clear message—what's wrong, where, why, how to fix—transforms frustration into resolution. Unclear messages multiply the cost of every error.

Shape validation invests in both: preventing errors through structural constraints, and clarifying errors when they occur.

---

**Next:** Learn how **[35. Drift Detection](./drift-detection.md)** identifies when generated artifacts diverge from their source specifications.
