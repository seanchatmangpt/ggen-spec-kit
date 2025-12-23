# 30. Human-Readable Artifact

★★

*Machines generate, but humans read. Human-readable artifacts are designed for human consumption—clear, well-structured, and helpful even when generated.*

---

Generation doesn't excuse poor readability. A generated Python file is still read by developers. A generated Markdown file is still read by users. If generation produces unreadable output, you've saved writing time but created reading time.

Human-readable artifacts are designed for their human consumers:
- Clear code structure, not minimized mess
- Helpful comments explaining non-obvious elements
- Consistent formatting that follows conventions
- Useful error messages, not stack traces
- Generated headers that explain provenance

**The problem: Generated artifacts that ignore human readers create frustration. Humans must understand, debug, and extend generated code.**

---

**The forces at play:**

- *Generation wants efficiency.* Minimal templates, fast output.

- *Reading wants clarity.* Humans need understandable output.

- *Maintenance wants stability.* Changes should be minimal and meaningful.

- *Debugging wants transparency.* Where did this come from? Why is it like this?

The tension: generate efficiently while producing artifacts that humans can comfortably work with.

---

**Therefore:**

Design templates to produce human-readable output with clear structure, helpful comments, and explicit provenance.

**Provenance header:**

Every generated file should declare its origin:

```python
"""Validate RDF files against SHACL shapes.

⚠️  AUTO-GENERATED FILE - DO NOT EDIT MANUALLY  ⚠️

This file was generated from RDF specifications.
Source: ontology/cli-commands.ttl
Template: templates/command.py.tera
Generated: 2025-01-15T10:30:00Z (ggen v5.0.2)

To modify this file:
1. Edit the source specification (ontology/cli-commands.ttl)
2. Run: ggen sync
3. Commit both source and generated files together

See: docs/RDF_WORKFLOW_GUIDE.md for details
"""
```

**Clear code structure:**

```python
# ─────────────────────────────────────────────────────────────
# Imports (standard library, then third-party, then local)
# ─────────────────────────────────────────────────────────────
import typer
from pathlib import Path
from typing import Optional

from specify_cli.core.instrumentation import instrument_command
from specify_cli import ops

# ─────────────────────────────────────────────────────────────
# Command Definition
# ─────────────────────────────────────────────────────────────
app = typer.Typer(help="Validate RDF files against SHACL shapes")


@app.command()
@instrument_command("validate")
def validate(
    file: Path = typer.Argument(..., help="File to validate"),
    output: Optional[Path] = typer.Option(None, help="Output file"),
    strict: bool = typer.Option(False, "--strict", help="Strict mode"),
) -> None:
    """Validate RDF files against SHACL shapes.

    Examples:
        specify validate ontology.ttl
        specify validate --strict schema.ttl
    """
    result = ops.validate.execute(file=file, output=output, strict=strict)
    _display_result(result)
```

**Helpful documentation:**

```markdown
# validate

Validate RDF files against SHACL shapes.

> **Generated Documentation** - This page is generated from [cli-commands.ttl](../ontology/cli-commands.ttl).
> To update, edit the source and run `ggen sync`.

## Usage

```bash
specify validate <file> [options]
```

## Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `file` | Path | Yes | File to validate |

## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--output` | Path | None | Output file |
| `--strict` | bool | false | Enable strict mode |

## Examples

```bash
# Basic validation
specify validate ontology.ttl

# Strict mode validation
specify validate --strict schema.ttl

# With output file
specify validate data.ttl --output results.json
```

## Why This Command Exists

[Rationale from specification...]

## See Also

- [check](./check.md) - Quick validation check
- [RDF Workflow Guide](../RDF_WORKFLOW_GUIDE.md)
```

**Formatting standards:**

- Follow language conventions (PEP 8 for Python, Google style for Markdown)
- Consistent indentation (4 spaces for Python, 2 for YAML)
- Logical grouping with section comments
- No excessively long lines (80-100 characters)

---

**Resulting context:**

After applying this pattern, you have:

- Generated artifacts that humans can comfortably read
- Clear provenance showing artifact origin
- Consistent structure across generated files
- Documentation that's actually helpful

This completes the Transformation Patterns and prepares for **[Part IV: Verification Patterns](../verification/test-before-code.md)**.

---

**Related patterns:**

- *Product of:* **[24. Template Emission](./template-emission.md)** — Templates produce readable output
- *Supports:* **[18. Narrative Specification](../specification/narrative-specification.md)** — Narrative in output
- *Enables:* **[45. Living Documentation](../evolution/living-documentation.md)** — Readable docs
- *Verified by:* **[35. Drift Detection](../verification/drift-detection.md)** — Check not edited

---

## Transition to Part IV

You've completed the Transformation Patterns. You know how to:
- Apply the **[Constitutional Equation](./constitutional-equation.md)** (spec.md = μ(feature.ttl))
- **[Normalize](./normalization-stage.md)** specifications with SHACL validation
- **[Extract](./extraction-query.md)** data with SPARQL queries
- **[Emit](./template-emission.md)** artifacts through templates
- **[Canonicalize](./canonicalization.md)** for consistent formatting
- Generate **[Receipts](./receipt-generation.md)** for verification
- Ensure **[Idempotence](./idempotent-transform.md)**
- Optimize with **[Partial Regeneration](./partial-regeneration.md)**
- Generate **[Multi-Target](./multi-target-emission.md)** outputs
- Produce **[Human-Readable Artifacts](./human-readable-artifact.md)**

Now it's time to verify that everything works correctly. Turn to **[Part IV: Verification Patterns](../verification/test-before-code.md)** to ensure your capabilities are correct, consistent, and trustworthy.
