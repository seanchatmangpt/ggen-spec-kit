# 24. Template Emission

★★

*Data alone is not output. Template emission (μ₃) renders extracted data through templates, producing human-readable artifacts—code, documentation, configuration. This is the creative transformation where abstract data becomes concrete artifact.*

---

## The Creative Act

After **[Extraction](./extraction-query.md)**, you have structured data. But data isn't the artifact users consume. Users need Python code they can execute, Markdown documentation they can read, YAML configurations they can deploy.

Template emission bridges this gap. Templates define the shape and structure of output; data fills in the specifics. The combination produces artifacts that are both consistent (from templates) and specific (from data).

Consider what happens when you have this data:

```json
{
  "name": "validate",
  "description": "Validate RDF files against SHACL shapes",
  "arguments": [
    {"name": "file", "type": "Path", "required": true, "help": "File to validate"},
    {"name": "output", "type": "Path", "required": false, "help": "Output location"}
  ]
}
```

A Python template transforms it into:

```python
@app.command()
def validate(
    file: Path = typer.Argument(..., help="File to validate"),
    output: Path = typer.Option(None, help="Output location"),
) -> None:
    """Validate RDF files against SHACL shapes"""
    ...
```

A Markdown template transforms the same data into:

```markdown
## validate

Validate RDF files against SHACL shapes

### Arguments

| Name | Type | Required | Description |
|------|------|----------|-------------|
| file | Path | Yes | File to validate |
| output | Path | No | Output location |
```

Same data, different templates, different artifacts. This is the power of template emission.

---

## The Rendering Problem

**The fundamental challenge: Extracted data must be rendered into various output formats. Hardcoded generation is inflexible and unmaintainable. Templates provide controlled flexibility while maintaining consistency.**

Let us examine why templates matter:

### The Hardcoded Trap

Without templates, you write generation code:

```python
def generate_command(data: dict) -> str:
    code = f"@app.command()\n"
    code += f"def {data['name']}(\n"
    for arg in data['arguments']:
        if arg['required']:
            code += f"    {arg['name']}: {arg['type']} = typer.Argument(..., help=\"{arg['help']}\"),\n"
        else:
            code += f"    {arg['name']}: {arg['type']} = typer.Option(None, help=\"{arg['help']}\"),\n"
    code += f") -> None:\n"
    code += f"    \"\"\"{data['description']}\"\"\"\n"
    return code
```

This approach has problems:
- **Readability:** The output format is obscured by string manipulation
- **Maintainability:** Changing output format requires modifying Python code
- **Separation:** Generation logic mixes with format details
- **Escaping:** String escaping becomes a nightmare

### The Template Advantage

Templates separate concerns:

```jinja
{# template.py.tera #}
@app.command()
def {{ name }}(
    {% for arg in arguments %}
    {{ arg.name }}: {{ arg.type }} = {% if arg.required %}typer.Argument(...{% else %}typer.Option(None{% endif %}, help="{{ arg.help }}"),
    {% endfor %}
) -> None:
    """{{ description }}"""
```

Benefits:
- **Readability:** The output format is visible in the template
- **Maintainability:** Change the template, not the code
- **Separation:** Data extraction is separate from rendering
- **Escaping:** Template engines handle escaping

### The Consistency Guarantee

Templates guarantee that all generated artifacts follow the same patterns:

- All commands have the same structure
- All docstrings follow the same format
- All imports are organized the same way
- All files have consistent headers

This consistency makes generated code feel hand-crafted while being automatically maintained.

---

## The Forces

Several tensions shape template design:

### Force: Consistency vs. Expressiveness

*Templates should enforce consistency. But different specifications need different expressions.*

Every command should have imports at the top. But some commands need `datetime`, others need `json`, others need neither. How do you maintain consistency while allowing variation?

```
    Consistency
         │
   Fixed │ Variable
  format │ content
         │
         ├────────────────────────────►
         │                    Expressiveness
         │
   Template structure      Data-driven variation
```

**Resolution:** Templates provide structure; data drives variation. Conditionals and loops in templates handle variation within consistent structure.

### Force: Simplicity vs. Power

*Simple templates are easy to maintain. But powerful features enable richer generation.*

A simple template:
```jinja
# {{ name }}
{{ description }}
```

A powerful template:
```jinja
{% if annotations %}
{% for annotation in annotations %}
@{{ annotation.name }}({% for arg in annotation.args %}{{ arg }}{% if not loop.last %}, {% endif %}{% endfor %})
{% endfor %}
{% endif %}
def {{ name | to_snake_case }}(
    {% for arg in arguments | sort(attribute='position') %}
    {{ arg.name }}: {{ arg.type | python_type }}{% if arg.default %} = {{ arg.default | python_literal }}{% endif %},
    {% endfor %}
) -> {{ return_type | python_type }}:
```

**Resolution:** Start simple. Add complexity only when needed. Document complex constructs.

### Force: Maintainability vs. DRY

*Templates should avoid repetition (DRY). But excessive abstraction creates unmaintainable template hierarchies.*

Aggressive DRY:
```jinja
{% include "partials/header.tera" %}
{% include "partials/imports.tera" %}
{% include "partials/class-definition.tera" %}
{% include "partials/methods.tera" %}
{% include "partials/footer.tera" %}
```

Now you need to understand five files to understand one output. Changes ripple unpredictably.

**Resolution:** Balance DRY with readability. Duplicate for clarity when abstraction would obscure.

### Force: Format Fidelity vs. Generation Flexibility

*Generated code should match project coding standards. But templates don't know about every project's standards.*

**Resolution:** Generate "close enough" and let canonicalization handle final formatting. Or use format-specific post-processing (black for Python, prettier for JavaScript).

---

## Therefore

**Implement emission (μ₃) using a template engine (Tera, Jinja2, Handlebars) that renders extracted data into target format. Design templates for readability and maintainability, using template features (conditionals, loops, filters) to handle variation.**

The emission pipeline:

```
┌────────────────────────────────────────────────────────────────────┐
│  μ₃ EMIT                                                            │
│                                                                     │
│  1. LOAD template                                                   │
│     ├── Resolve template path from configuration                   │
│     ├── Parse template syntax                                      │
│     ├── Resolve includes and partials                              │
│     └── Validate template structure                                │
│                                                                     │
│  2. PREPARE context                                                 │
│     ├── Structured data from extraction                            │
│     ├── Add metadata (source file, timestamp, generator)           │
│     └── Add computed values (counters, flags)                      │
│                                                                     │
│  3. RENDER template                                                 │
│     ├── Execute template with context                              │
│     ├── Handle errors gracefully                                   │
│     └── Produce raw output                                         │
│                                                                     │
│  4. OUTPUT rendered content                                         │
│     └── Pass to canonicalization (μ₄)                              │
│                                                                     │
│  Input: structured_data.json + template.tera                       │
│  Output: raw_artifact (to be canonicalized)                        │
└────────────────────────────────────────────────────────────────────┘
```

---

## Template Design

### Template Structure

Every template should follow a consistent structure:

```jinja
{# ═══════════════════════════════════════════════════════════════════
   Template: command.py.tera
   Purpose:  Generate Python CLI command implementation

   Input data structure:
   {
     "name": "string",
     "description": "string",
     "arguments": [...],
     "options": [...]
   }

   Output: Python file with Typer command
═══════════════════════════════════════════════════════════════════ #}

{# ─────────────────────────────────────────────────────────────────
   PROVENANCE HEADER
   ───────────────────────────────────────────────────────────────── #}
"""{{ description }}

⚠️  AUTO-GENERATED FILE - DO NOT EDIT MANUALLY  ⚠️

Source: {{ source_file }}
Template: {{ template_name }}
Generated: {{ generated_at }}

To modify: Edit {{ source_file }}, then run: ggen sync
"""

{# ─────────────────────────────────────────────────────────────────
   IMPORTS
   ───────────────────────────────────────────────────────────────── #}
import typer
from pathlib import Path
from typing import Optional
{% if needs_datetime %}
from datetime import datetime
{% endif %}

from specify_cli.core.instrumentation import instrument_command
from specify_cli import ops

{# ─────────────────────────────────────────────────────────────────
   COMMAND DEFINITION
   ───────────────────────────────────────────────────────────────── #}
app = typer.Typer(help="{{ description }}")


@app.command()
@instrument_command("{{ name }}")
def {{ name | to_snake_case }}(
    {# ───── Arguments ───── #}
    {% for arg in arguments %}
    {{ arg.name }}: {{ arg.type | python_type }} = typer.Argument(
        {% if arg.required %}...{% else %}None{% endif %},
        help="{{ arg.help | escape_quotes }}"
    ),
    {% endfor %}
    {# ───── Options ───── #}
    {% for opt in options %}
    {{ opt.name }}: {{ opt.type | python_type }} = typer.Option(
        {{ opt.default | python_literal }},
        "--{{ opt.name | to_kebab_case }}",
        help="{{ opt.help | escape_quotes }}"
    ),
    {% endfor %}
) -> None:
    """{{ description }}"""
    result = ops.{{ name | to_snake_case }}.execute(
        {% for arg in arguments %}
        {{ arg.name }}={{ arg.name }},
        {% endfor %}
        {% for opt in options %}
        {{ opt.name }}={{ opt.name }},
        {% endfor %}
    )
    _display_result(result)
```

### Template Features

#### Conditionals

Handle variation based on data:

```jinja
{% if arg.required %}
{{ arg.name }}: {{ arg.type }} = typer.Argument(..., help="{{ arg.help }}")
{% else %}
{{ arg.name }}: Optional[{{ arg.type }}] = typer.Option(None, help="{{ arg.help }}")
{% endif %}
```

Complex conditionals:

```jinja
{% if arg.type == "Path" and arg.must_exist %}
{{ arg.name }}: Path = typer.Argument(..., exists=True)
{% elif arg.type == "Path" %}
{{ arg.name }}: Path = typer.Argument(...)
{% elif arg.type == "int" and arg.min is defined %}
{{ arg.name }}: int = typer.Argument(..., min={{ arg.min }})
{% else %}
{{ arg.name }}: {{ arg.type }} = typer.Argument(...)
{% endif %}
```

#### Loops

Iterate over collections:

```jinja
{% for arg in arguments %}
- {{ arg.name }}: {{ arg.help }}
{% endfor %}
```

With loop metadata:

```jinja
{% for arg in arguments %}
{{ arg.name }}{% if not loop.last %}, {% endif %}
{% endfor %}
```

Produces: `file, output, strict`

#### Filters

Transform values:

```jinja
{{ name | upper }}           {# VALIDATE #}
{{ name | lower }}           {# validate #}
{{ name | to_snake_case }}   {# validate_schema #}
{{ name | to_kebab_case }}   {# validate-schema #}
{{ name | capitalize }}      {# Validate #}

{{ description | truncate(length=80) }}
{{ description | escape_quotes }}
{{ code | indent(width=4) }}
```

Custom filters for domain-specific transformations:

```python
def python_type(rdf_type: str) -> str:
    """Convert RDF type to Python type annotation."""
    type_map = {
        "Path": "Path",
        "str": "str",
        "int": "int",
        "bool": "bool",
        "float": "float",
        "datetime": "datetime",
        "list": "list",
    }
    return type_map.get(rdf_type, "Any")

def python_literal(value) -> str:
    """Convert value to Python literal."""
    if value is None:
        return "None"
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, str):
        return f'"{value}"'
    return str(value)
```

#### Includes

Modularize templates:

```jinja
{% include "partials/header.tera" %}
{% include "partials/imports.tera" %}

{# Main content #}
...

{% include "partials/footer.tera" %}
```

With context passing:

```jinja
{% include "partials/argument-list.tera" with arguments=command.arguments %}
```

#### Macros

Reusable template fragments:

```jinja
{% macro render_argument(arg) %}
{{ arg.name }}: {{ arg.type | python_type }}{% if arg.default is defined %} = {{ arg.default | python_literal }}{% endif %}
{% endmacro %}

{% for arg in arguments %}
{{ self::render_argument(arg=arg) }},
{% endfor %}
```

---

## Template Organization

### Directory Structure

```
templates/
├── python/
│   ├── command.py.tera           # CLI command implementation
│   ├── command-test.py.tera      # Pytest tests for command
│   ├── ops-module.py.tera        # Ops layer implementation
│   └── partials/
│       ├── header.tera           # Standard file header
│       ├── imports.tera          # Common imports
│       └── docstring.tera        # Docstring format
├── markdown/
│   ├── command.md.tera           # Command documentation
│   ├── index.md.tera             # Command index
│   └── partials/
│       ├── argument-table.tera   # Argument table format
│       └── example.tera          # Usage example format
├── yaml/
│   ├── api-schema.yaml.tera      # OpenAPI schema
│   └── config.yaml.tera          # Configuration file
└── shared/
    ├── provenance.tera           # Provenance header (all formats)
    └── timestamp.tera            # Timestamp formatting
```

### Template Naming

Consistent naming conventions:

```
{artifact-type}.{output-extension}.tera

Examples:
  command.py.tera          # Python command
  command.md.tera          # Markdown documentation
  command-test.py.tera     # Python test
  api-schema.yaml.tera     # YAML schema
  completion.bash.tera     # Bash completion
```

### Template Documentation

Every template should have internal documentation:

```jinja
{# ═══════════════════════════════════════════════════════════════════
   Template: command.py.tera
   ═══════════════════════════════════════════════════════════════════

   PURPOSE:
   Generate Python CLI command implementation file.

   INPUT DATA STRUCTURE:
   {
     "name": "command-name",
     "description": "What the command does",
     "arguments": [
       {
         "name": "arg_name",
         "type": "Path|str|int|bool",
         "required": true|false,
         "help": "Argument help text",
         "default": "optional default value"
       }
     ],
     "options": [
       {
         "name": "option_name",
         "type": "Path|str|int|bool",
         "help": "Option help text",
         "default": "default value"
       }
     ]
   }

   OUTPUT:
   Python file with:
   - Provenance header
   - Imports
   - Typer command definition
   - Delegation to ops layer

   USED BY:
   - ggen.toml target: python-commands

   DEPENDENCIES:
   - partials/header.tera
   - partials/imports.tera

   CHANGELOG:
   - 2025-01-15: Initial version
   - 2025-02-01: Added instrumentation decorator
═══════════════════════════════════════════════════════════════════ #}
```

---

## Context Preparation

### Standard Context

Every template receives standard metadata:

```python
def prepare_context(data: dict, config: Config) -> dict:
    """Prepare template context with standard metadata."""
    return {
        # Extracted data
        **data,

        # Source information
        "source_file": config.source_path,
        "source_hash": compute_hash(config.source_path),

        # Template information
        "template_name": config.template_path.name,
        "template_hash": compute_hash(config.template_path),

        # Generation information
        "generated_at": datetime.now(UTC).isoformat(),
        "generator": f"ggen v{__version__}",
        "generator_version": __version__,

        # Environment
        "project_name": config.project_name,
        "base_url": config.base_url,
    }
```

### Computed Values

Add computed values that templates need:

```python
def add_computed_values(context: dict) -> dict:
    """Add computed values to context."""
    commands = context.get('commands', [])

    return {
        **context,

        # Counts
        "command_count": len(commands),
        "total_arguments": sum(len(c.get('arguments', [])) for c in commands),

        # Flags
        "has_admin_commands": any(c.get('admin') for c in commands),
        "needs_datetime": any(
            a.get('type') == 'datetime'
            for c in commands
            for a in c.get('arguments', [])
        ),

        # Grouped data
        "commands_by_category": group_by(commands, 'category'),
    }
```

---

## Error Handling

### Template Errors

Handle template syntax errors gracefully:

```python
def render_template(template_path: Path, context: dict) -> str:
    """Render template with comprehensive error handling."""
    try:
        template = load_template(template_path)
        return template.render(context)

    except TemplateSyntaxError as e:
        raise TemplateError(
            f"Syntax error in template {template_path}",
            line=e.lineno,
            details=str(e),
            template_source=show_context(template_path, e.lineno)
        )

    except UndefinedVariableError as e:
        raise TemplateError(
            f"Undefined variable in template {template_path}",
            variable=e.variable,
            available=list(context.keys()),
            suggestion=suggest_variable(e.variable, context.keys())
        )

    except FilterError as e:
        raise TemplateError(
            f"Filter error in template {template_path}",
            filter_name=e.filter,
            input_value=e.input,
            details=str(e)
        )
```

### Missing Data Handling

Handle missing optional data:

```jinja
{# Option 1: Default value #}
{{ description | default(value="No description provided") }}

{# Option 2: Conditional rendering #}
{% if description %}
{{ description }}
{% else %}
[No description]
{% endif %}

{# Option 3: Silent ignore #}
{% if examples %}
## Examples
{% for example in examples %}
{{ example }}
{% endfor %}
{% endif %}
```

### Strict Mode

In production, use strict mode:

```python
# Fail on undefined variables
env = Environment(undefined=StrictUndefined)
```

In development, use lenient mode with warnings:

```python
# Warn but continue
env = Environment(undefined=LoggingUndefined)
```

---

## Configuration

```toml
# ggen.toml

[emission]
template_dir = "templates"
strict_undefined = true
auto_reload = false  # true for development

# Custom filters
[emission.filters]
python_type = "transformers:python_type"
python_literal = "transformers:python_literal"
escape_quotes = "transformers:escape_quotes"
to_snake_case = "transformers:to_snake_case"
to_kebab_case = "transformers:to_kebab_case"

# Template engine configuration
[emission.engine]
name = "tera"  # tera | jinja2 | handlebars
comment_start = "{#"
comment_end = "#}"
variable_start = "{{"
variable_end = "}}"

# Per-target template configuration
[[targets]]
name = "python-commands"
template = "templates/python/command.py.tera"
output = "src/commands/{{ name }}.py"

[[targets]]
name = "command-docs"
template = "templates/markdown/command.md.tera"
output = "docs/commands/{{ name }}.md"
```

---

## Case Study: The Template Library

*A team builds a comprehensive template library for their CLI.*

### The Situation

The DevOps team at Nexus Corp needed to generate:
- 156 Python CLI commands
- Pytest tests for each command
- Markdown documentation for each command
- Man pages for Unix systems
- PowerShell completions for Windows
- Bash/Zsh completions for Unix
- OpenAPI schema for REST API exposure

All from the same RDF specifications.

### The Template Development

**Phase 1: Core Templates**

Started with the three essential templates:

```
templates/
├── python/command.py.tera
├── python/command-test.py.tera
└── markdown/command.md.tera
```

**Phase 2: Shared Partials**

Extracted common elements:

```
templates/
├── shared/
│   ├── provenance-header.tera
│   ├── argument-signature.tera
│   └── type-annotation.tera
├── python/
│   └── partials/
│       ├── imports.tera
│       └── docstring.tera
└── markdown/
    └── partials/
        ├── argument-table.tera
        └── example-block.tera
```

**Phase 3: Platform-Specific Templates**

Added platform support:

```
templates/
├── completions/
│   ├── bash.tera
│   ├── zsh.tera
│   ├── fish.tera
│   └── powershell.tera
├── manpages/
│   └── command.1.tera
└── openapi/
    └── paths.yaml.tera
```

**Phase 4: Custom Filters**

Built domain-specific filters:

```python
# transformers.py

def man_escape(text: str) -> str:
    """Escape text for man page format."""
    return text.replace("-", "\\-").replace(".", "\\.")

def powershell_type(rdf_type: str) -> str:
    """Convert RDF type to PowerShell type."""
    return {"Path": "[string]", "int": "[int]", "bool": "[switch]"}.get(rdf_type, "[string]")

def completion_description(text: str) -> str:
    """Format description for shell completion."""
    return text[:50].replace("'", "\\'") if text else ""
```

### The Results

- **7 template families** serving different platforms
- **23 template files** total
- **Single source** generates all artifacts
- **100% consistency** across platforms
- **Easy updates:** Change template once, regenerate everywhere

---

## Anti-Patterns

### Anti-Pattern: Logic in Templates

*"I'll put the business logic in the template for flexibility."*

```jinja
{% if arg.type == "Path" %}
  {% if arg.must_exist %}
    {% if arg.is_file %}
      {% set validation = "file_exists" %}
    {% elif arg.is_dir %}
      {% set validation = "dir_exists" %}
    {% endif %}
  {% endif %}
{% endif %}
```

Templates become unmaintainable when they contain complex logic.

**Resolution:** Move logic to extraction or post-processing. Templates should be mostly structural.

### Anti-Pattern: Template Sprawl

*"Each command type gets its own template."*

```
templates/
├── admin-command.py.tera
├── read-command.py.tera
├── write-command.py.tera
├── query-command.py.tera
├── transform-command.py.tera
└── ... 20 more similar templates
```

**Resolution:** One template with conditionals, not twenty templates with duplication.

### Anti-Pattern: Invisible Whitespace

*"The indentation looks right..."*

Template whitespace handling is tricky. What looks right in the template may produce wrong output:

```jinja
{% for arg in arguments %}
    {{ arg.name }}
{% endfor %}
```

May produce extra blank lines or wrong indentation.

**Resolution:** Use whitespace control:

```jinja
{%- for arg in arguments %}
{{ arg.name }}
{%- endfor %}
```

### Anti-Pattern: Hardcoded Values

*"I'll just hardcode this version number."*

```jinja
# Generated by ggen v5.0.2  {# Hardcoded! #}
```

**Resolution:** All values should come from context:

```jinja
# Generated by {{ generator }}
```

---

## Implementation Checklist

### Template Development

- [ ] Document template purpose and data requirements
- [ ] Use consistent naming conventions
- [ ] Extract shared elements to partials
- [ ] Test templates with edge cases
- [ ] Handle missing optional data gracefully
- [ ] Use whitespace control for clean output

### Filter Development

- [ ] Create domain-specific filters
- [ ] Document filter behavior
- [ ] Test filters with edge cases
- [ ] Handle null inputs gracefully
- [ ] Register filters in configuration

### Context Preparation

- [ ] Include standard metadata
- [ ] Add computed values as needed
- [ ] Validate required data before rendering
- [ ] Document context structure

### Error Handling

- [ ] Report syntax errors with line numbers
- [ ] Report undefined variables with suggestions
- [ ] Support strict/lenient modes
- [ ] Log warnings for potential issues

---

## Exercises

### Exercise 1: First Template

Create your first template:

1. Design a simple data structure for a "person" (name, email, bio)
2. Create a Markdown template for a profile page
3. Create a JSON template for an API response
4. Render both from the same data
5. Compare outputs

### Exercise 2: Template with Logic

Add conditional logic:

1. Extend person data with optional "social_links"
2. Modify template to show social links only if present
3. Add loop to render multiple links
4. Handle empty links list gracefully

### Exercise 3: Custom Filter

Create and use a custom filter:

1. Design a filter to format phone numbers
2. Implement the filter in Python
3. Register in template configuration
4. Use in template
5. Test with various inputs

### Exercise 4: Template Refactoring

Refactor for maintainability:

1. Create a complex template with duplication
2. Extract common parts to partials
3. Create a macro for repeated structures
4. Verify output is identical after refactoring

---

## Resulting Context

After implementing this pattern, you have:

- **Artifacts generated** from data through templates
- **Consistent structure** across all generated files
- **Maintainable templates** separate from extraction logic
- **Clear provenance** in generated output
- **Reusable partials** for common elements
- **Custom filters** for domain-specific transformations

The emission stage is where abstract data becomes concrete artifact. Templates define the shape; data fills the content. Together they produce the files users actually consume.

---

## Code References

The following spec-kit source files implement the template emission stage (μ₃):

| Reference | Description |
|-----------|-------------|
| `templates/command.tera:1-367` | Complete Tera template for Python command generation |
| `templates/command.tera:5-32` | Template metadata extraction and imports |
| `templates/command.tera:87-225` | Subcommand generation with argument handling |
| `templates/command.tera:229-366` | Main command generation for commands without subcommands |
| `src/specify_cli/runtime/receipt.py:136` | Stage "emit" in pipeline |

---

## Related Patterns

- **Part of:** **[21. Constitutional Equation](./constitutional-equation.md)** — Stage μ₃
- **Follows:** **[23. Extraction Query](./extraction-query.md)** — Receives structured data
- **Precedes:** **[25. Canonicalization](./canonicalization.md)** — Output needs normalizing
- **Supports:** **[29. Multi-Target Emission](./multi-target-emission.md)** — Multiple formats

---

## Philosophical Note

> *"Content is king, but context is God."*
> — Gary Vaynerchuk

In template emission, data is content and templates are context. Data provides what to say; templates provide how to say it. Neither alone produces the artifact—only together do they create something useful.

The template is not just formatting. It's the embodiment of your project's standards, conventions, and style. When you change a template, you change how your project presents itself. This is power that deserves careful stewardship.

---

**Next:** The raw output flows to **[25. Canonicalization](./canonicalization.md)**, where formatting is normalized for consistency across platforms.
