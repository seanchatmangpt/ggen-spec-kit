# 29. Multi-Target Emission

★★

*One specification, many artifacts. Multi-target emission generates different outputs from the same source—code, documentation, tests, schemas, completions. This is the multiplicative power of specification-driven development.*

---

## The One-to-Many Power

A single specification contains rich information about a capability:

```turtle
:validate a cli:Command ;
    rdfs:label "validate" ;
    cli:description "Validate RDF files against SHACL shapes" ;
    cli:rationale "Users need to verify specifications are correct before deployment" ;
    cli:hasArgument [
        cli:name "file" ;
        cli:type "Path" ;
        cli:required true ;
        cli:help "Path to the RDF file to validate"
    ] ;
    cli:hasOption [
        cli:name "strict" ;
        cli:type "bool" ;
        cli:default "false" ;
        cli:help "Enable strict validation mode"
    ] ;
    cli:example "specify validate ontology.ttl" ;
    cli:example "specify validate --strict schema.ttl" ;
    jtbd:accomplishesJob :VerifyCorrectness ;
    acc:hasAcceptanceCriteria :AC_ValidInput_Success, :AC_InvalidInput_Failure .
```

This single specification can generate:
- **Python implementation** — The actual command code
- **CLI documentation** — User-facing help text
- **API schema** — OpenAPI specification
- **Test stubs** — Pytest test cases
- **Shell completions** — Bash/Zsh/Fish completions
- **Man pages** — Unix manual pages
- **TypeScript types** — Client SDK types

Each artifact serves different consumers, but all derive from the same truth. When the specification changes, all artifacts update together, maintaining perfect consistency.

---

## The Consistency Challenge

**The fundamental challenge: Different consumers need different formats, but all must remain consistent. Manual synchronization fails at scale. Multi-target emission solves this by generating all formats from a single source.**

Let us examine the alternative:

### The Manual Synchronization Nightmare

Without multi-target emission, teams maintain parallel artifacts:

```
Developer A: Updates Python implementation
Developer B: Updates documentation
Developer C: Updates TypeScript types
Developer D: Updates tests

# Three weeks later:
- Python has new parameter `--verbose`
- Documentation still shows old parameters
- TypeScript types are missing three fields
- Tests cover outdated behavior
```

Synchronization debt accumulates. Eventually, artifacts describe different systems.

### The Single Source Promise

With multi-target emission:

```
Developer A: Updates specification
ggen sync: Regenerates ALL artifacts

# Result:
- Python reflects new specification
- Documentation reflects new specification
- TypeScript reflects new specification
- Tests reflect new specification
```

Change flows from source to all targets automatically.

---

## The Forces

Several tensions shape multi-target design:

### Force: Format Diversity vs. Source Unity

*Each format has unique requirements. But the source should be unified.*

Python needs type annotations. Markdown needs tables. YAML needs indentation. JSON needs quotes. Each format demands different rendering—but the underlying information is identical.

**Resolution:** Single source, format-specific templates. The specification provides data; templates provide format.

### Force: Consumer Optimization vs. Generation Simplicity

*Each consumer wants optimized output. But optimization complicates generation.*

Developers want minimal, clean code. Documentation readers want examples and explanations. Test frameworks want fixtures and assertions. Each has different optimization criteria.

**Resolution:** Consumer-focused templates. Each template optimizes for its consumers. The extraction query shapes data for each template's needs.

### Force: Query Reuse vs. Format Specificity

*Similar data is needed across formats. But each format needs slightly different data.*

Python code generation needs argument types. Documentation needs argument help text. Both need argument names. Should you run one query or many?

**Resolution:** Shared queries where possible, specialized queries where needed. Compose queries from common patterns.

### Force: Build Complexity vs. Unified Sync

*Many targets means complex builds. But users want simple commands.*

Managing 7 templates, 7 queries, 7 output patterns is complex. But users should be able to run `ggen sync` and have everything just work.

**Resolution:** Configuration-driven orchestration. Complexity lives in config; simplicity lives in commands.

---

## Therefore

**Configure multiple emission targets in the transformation pipeline, each producing different artifacts from the same source specification. Use format-specific templates and queries while maintaining a unified synchronization command.**

The multi-target architecture:

```
                       ┌─────────────────────────────────────────────┐
                       │           SPECIFICATION SOURCE              │
                       │         (cli-commands.ttl)                  │
                       └─────────────────┬───────────────────────────┘
                                         │
         ┌───────────┬──────────┬────────┼────────┬──────────┬───────────┐
         │           │          │        │        │          │           │
         ▼           ▼          ▼        ▼        ▼          ▼           ▼
    ┌─────────┐ ┌─────────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌─────────┐ ┌─────────┐
    │ Python  │ │ Docs    │ │ Test │ │ API  │ │ Shell│ │ Man     │ │ TS      │
    │ Query   │ │ Query   │ │ Query│ │ Query│ │ Query│ │ Query   │ │ Query   │
    └────┬────┘ └────┬────┘ └───┬──┘ └───┬──┘ └───┬──┘ └────┬────┘ └────┬────┘
         │           │          │        │        │          │           │
         ▼           ▼          ▼        ▼        ▼          ▼           ▼
    ┌─────────┐ ┌─────────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌─────────┐ ┌─────────┐
    │ Python  │ │ Markdown│ │Pytest│ │OpenAPI│ │ Bash │ │ Roff    │ │ TS      │
    │ Template│ │ Template│ │ Tmpl │ │ Tmpl │ │ Tmpl │ │ Template│ │ Template│
    └────┬────┘ └────┬────┘ └───┬──┘ └───┬──┘ └───┬──┘ └────┬────┘ └────┬────┘
         │           │          │        │        │          │           │
         ▼           ▼          ▼        ▼        ▼          ▼           ▼
    ┌─────────┐ ┌─────────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌─────────┐ ┌─────────┐
    │validate │ │validate │ │test_ │ │paths/│ │comp- │ │validate │ │validate │
    │.py      │ │.md      │ │val.py│ │val.ym│ │lete  │ │.1       │ │.d.ts    │
    └─────────┘ └─────────┘ └──────┘ └──────┘ └──────┘ └─────────┘ └─────────┘
```

---

## Configuration

### Multi-Target Configuration

```toml
# ggen.toml

[source]
default = "ontology/cli-commands.ttl"
shapes = ["shapes/command-shape.ttl"]

# ─────────────────────────────────────────────────────────────
# Target 1: Python Implementation
# ─────────────────────────────────────────────────────────────
[[targets]]
name = "python-commands"
description = "Python CLI command implementations"
query = "sparql/command-extract.rq"
template = "templates/python/command.py.tera"
output = "src/commands/{{ name | to_snake_case }}.py"
enabled = true

# ─────────────────────────────────────────────────────────────
# Target 2: Command Documentation
# ─────────────────────────────────────────────────────────────
[[targets]]
name = "command-docs"
description = "Markdown documentation for each command"
query = "sparql/command-docs-extract.rq"
template = "templates/markdown/command.md.tera"
output = "docs/commands/{{ name }}.md"
enabled = true

# ─────────────────────────────────────────────────────────────
# Target 3: Documentation Index
# ─────────────────────────────────────────────────────────────
[[targets]]
name = "docs-index"
description = "Command index page"
query = "sparql/command-list-extract.rq"
template = "templates/markdown/command-index.md.tera"
output = "docs/commands/index.md"
aggregate = true  # Single output from all commands

# ─────────────────────────────────────────────────────────────
# Target 4: Pytest Tests
# ─────────────────────────────────────────────────────────────
[[targets]]
name = "command-tests"
description = "Pytest test stubs for each command"
query = "sparql/command-test-extract.rq"
template = "templates/python/command-test.py.tera"
output = "tests/e2e/test_{{ name | to_snake_case }}.py"
enabled = true

# ─────────────────────────────────────────────────────────────
# Target 5: OpenAPI Schema
# ─────────────────────────────────────────────────────────────
[[targets]]
name = "openapi"
description = "OpenAPI specification for REST API"
query = "sparql/openapi-extract.rq"
template = "templates/openapi/paths.yaml.tera"
output = "api/openapi.yaml"
aggregate = true

# ─────────────────────────────────────────────────────────────
# Target 6: Shell Completions
# ─────────────────────────────────────────────────────────────
[[targets]]
name = "bash-completions"
description = "Bash shell completions"
query = "sparql/completions-extract.rq"
template = "templates/shell/bash-completion.tera"
output = "completions/specify.bash"
aggregate = true

[[targets]]
name = "zsh-completions"
description = "Zsh shell completions"
query = "sparql/completions-extract.rq"
template = "templates/shell/zsh-completion.tera"
output = "completions/_specify"
aggregate = true

# ─────────────────────────────────────────────────────────────
# Target 7: TypeScript Types
# ─────────────────────────────────────────────────────────────
[[targets]]
name = "typescript-types"
description = "TypeScript type definitions for SDK"
query = "sparql/typescript-extract.rq"
template = "templates/typescript/types.d.ts.tera"
output = "sdk/types.d.ts"
aggregate = true
enabled = false  # Disabled until SDK development starts
```

### Selective Generation

```bash
# Generate all enabled targets
ggen sync

# Generate specific target
ggen sync --target python-commands

# Generate multiple specific targets
ggen sync --target python-commands --target command-docs

# Generate by category
ggen sync --category docs  # All documentation targets
ggen sync --category code  # All code generation targets

# List available targets
ggen targets
```

---

## Query Specialization

Each target may need different data shapes:

### Code Generation Query

```sparql
# sparql/command-extract.rq
# For: Python implementation
# Focus: Types, defaults, validation

PREFIX cli: <http://spec-kit.dev/cli#>
PREFIX sk: <http://spec-kit.dev/ontology#>

SELECT ?name ?description ?argName ?argType ?argRequired ?argDefault ?optName ?optType ?optDefault
WHERE {
    ?cmd a cli:Command ;
         rdfs:label ?name ;
         sk:description ?description .

    OPTIONAL {
        ?cmd cli:hasArgument ?arg .
        ?arg cli:name ?argName ;
             cli:type ?argType .
        OPTIONAL { ?arg cli:required ?argRequired }
        OPTIONAL { ?arg cli:default ?argDefault }
    }

    OPTIONAL {
        ?cmd cli:hasOption ?opt .
        ?opt cli:name ?optName ;
             cli:type ?optType .
        OPTIONAL { ?opt cli:default ?optDefault }
    }
}
ORDER BY ?name ?argName ?optName
```

### Documentation Query

```sparql
# sparql/command-docs-extract.rq
# For: Markdown documentation
# Focus: Help text, examples, rationale

PREFIX cli: <http://spec-kit.dev/cli#>
PREFIX sk: <http://spec-kit.dev/ontology#>

SELECT ?name ?description ?rationale ?argName ?argHelp ?optName ?optHelp ?example
WHERE {
    ?cmd a cli:Command ;
         rdfs:label ?name ;
         sk:description ?description .

    OPTIONAL { ?cmd cli:rationale ?rationale }

    OPTIONAL {
        ?cmd cli:hasArgument ?arg .
        ?arg cli:name ?argName ;
             cli:help ?argHelp .
    }

    OPTIONAL {
        ?cmd cli:hasOption ?opt .
        ?opt cli:name ?optName ;
             cli:help ?optHelp .
    }

    OPTIONAL { ?cmd cli:example ?example }
}
ORDER BY ?name ?argName ?optName
```

### Test Generation Query

```sparql
# sparql/command-test-extract.rq
# For: Pytest test stubs
# Focus: Arguments, acceptance criteria

PREFIX cli: <http://spec-kit.dev/cli#>
PREFIX acc: <http://spec-kit.dev/acceptance#>

SELECT ?name ?argName ?argType ?argRequired ?criterionId ?given ?when ?then
WHERE {
    ?cmd a cli:Command ;
         rdfs:label ?name .

    OPTIONAL {
        ?cmd cli:hasArgument ?arg .
        ?arg cli:name ?argName ;
             cli:type ?argType .
        OPTIONAL { ?arg cli:required ?argRequired }
    }

    OPTIONAL {
        ?cmd acc:hasAcceptanceCriteria ?criterion .
        ?criterion acc:id ?criterionId ;
                   acc:given ?given ;
                   acc:when ?when ;
                   acc:then ?then .
    }
}
ORDER BY ?name ?argName ?criterionId
```

---

## Template Specialization

### Python Command Template

```jinja
{# templates/python/command.py.tera #}
"""{{ description }}

Auto-generated from RDF specification.
Source: {{ source_file }}
"""
import typer
from pathlib import Path
from typing import Optional

from specify_cli import ops

app = typer.Typer(help="{{ description }}")


@app.command()
def {{ name | to_snake_case }}(
    {% for arg in arguments %}
    {{ arg.name }}: {{ arg.type | python_type }} = typer.Argument(
        {% if arg.required %}...{% else %}{{ arg.default | python_literal }}{% endif %},
        help="{{ arg.help }}"
    ),
    {% endfor %}
    {% for opt in options %}
    {{ opt.name }}: {{ opt.type | python_type }} = typer.Option(
        {{ opt.default | python_literal }},
        "--{{ opt.name | to_kebab_case }}",
        help="{{ opt.help }}"
    ),
    {% endfor %}
) -> None:
    """{{ description }}"""
    result = ops.{{ name | to_snake_case }}.execute(
        {% for arg in arguments %}{{ arg.name }}={{ arg.name }}, {% endfor %}
        {% for opt in options %}{{ opt.name }}={{ opt.name }}, {% endfor %}
    )
    print(result)
```

### Markdown Documentation Template

```jinja
{# templates/markdown/command.md.tera #}
# {{ name }}

{{ description }}

> **Generated Documentation** - See [source specification]({{ source_file }}).

{% if rationale %}
## Why This Command Exists

{{ rationale }}
{% endif %}

## Usage

```bash
specify {{ name }}{% for arg in arguments %} <{{ arg.name }}>{% endfor %}{% for opt in options %} [--{{ opt.name | to_kebab_case }}]{% endfor %}
```

{% if arguments | length > 0 %}
## Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
{% for arg in arguments %}
| `{{ arg.name }}` | {{ arg.type }} | {{ "Yes" if arg.required else "No" }} | {{ arg.help }} |
{% endfor %}
{% endif %}

{% if options | length > 0 %}
## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
{% for opt in options %}
| `--{{ opt.name | to_kebab_case }}` | {{ opt.type }} | {{ opt.default | default(value="-") }} | {{ opt.help }} |
{% endfor %}
{% endif %}

{% if examples | length > 0 %}
## Examples

{% for example in examples %}
```bash
{{ example }}
```
{% endfor %}
{% endif %}

## See Also

{% for related in related_commands %}
- [{{ related.name }}](./{{ related.name }}.md){% if related.relationship %} - {{ related.relationship }}{% endif %}
{% endfor %}
```

### Bash Completion Template

```jinja
{# templates/shell/bash-completion.tera #}
# Bash completion for specify
# Auto-generated - do not edit

_specify_completion() {
    local cur prev commands
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    commands="{{ commands | map(attribute='name') | join(' ') }}"

    case "${prev}" in
        specify)
            COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
            return 0
            ;;
        {% for cmd in commands %}
        {{ cmd.name }})
            local {{ cmd.name }}_opts="{% for opt in cmd.options %}--{{ opt.name | to_kebab_case }} {% endfor %}"
            COMPREPLY=( $(compgen -W "${{'{'}}{{ cmd.name }}_opts}" -- ${cur}) )
            return 0
            ;;
        {% endfor %}
    esac
}

complete -F _specify_completion specify
```

---

## Case Study: The API Platform

*A team generates a complete API platform from specifications.*

### The Situation

The FinTech team was building a comprehensive API platform:
- 347 API endpoints
- REST API with OpenAPI documentation
- Python SDK
- TypeScript SDK
- Admin CLI
- Integration tests

Keeping everything synchronized was a full-time job.

### The Multi-Target Solution

They configured 9 emission targets:

```toml
[[targets]]
name = "python-handlers"
output = "backend/handlers/{{ name }}.py"

[[targets]]
name = "openapi-spec"
output = "api/openapi.yaml"
aggregate = true

[[targets]]
name = "python-sdk"
output = "sdk/python/{{ name }}.py"

[[targets]]
name = "typescript-sdk"
output = "sdk/typescript/{{ name }}.ts"

[[targets]]
name = "cli-commands"
output = "cli/commands/{{ name }}.py"

[[targets]]
name = "integration-tests"
output = "tests/integration/test_{{ name }}.py"

[[targets]]
name = "api-docs"
output = "docs/api/{{ name }}.md"

[[targets]]
name = "changelog"
output = "CHANGELOG.md"
aggregate = true

[[targets]]
name = "postman-collection"
output = "tools/postman/collection.json"
aggregate = true
```

### The Results

**Before multi-target emission:**
- 3 developers maintaining synchronization
- Average drift detection time: 2 weeks
- Documentation accuracy: ~70%
- SDK completeness: ~85%

**After multi-target emission:**
- 0 developers maintaining synchronization
- Drift is impossible (single source)
- Documentation accuracy: 100%
- SDK completeness: 100%

Time saved: **60+ developer-hours per week**

---

## Anti-Patterns

### Anti-Pattern: Target Sprawl

*"Every slight variation gets its own target."*

```toml
[[targets]]
name = "python-commands-verbose"
[[targets]]
name = "python-commands-compact"
[[targets]]
name = "python-commands-debug"
# ... endless variations
```

**Resolution:** Use configuration within templates, not target multiplication.

### Anti-Pattern: Query Duplication

*"Each target has its own completely separate query."*

Seven targets, seven queries, 90% overlap. Changes require updating all seven.

**Resolution:** Compose queries from shared patterns. Factor out common graph patterns.

### Anti-Pattern: Disabled-Forever Targets

*"We'll enable TypeScript generation someday."*

```toml
[[targets]]
name = "typescript"
enabled = false  # Has been false for 18 months
```

**Resolution:** Remove unused targets. Add them when actually needed.

### Anti-Pattern: Inconsistent Naming

*"Some targets use snake_case, some use kebab-case, some use..."*

```toml
[[targets]]
name = "python_commands"      # snake_case
[[targets]]
name = "command-docs"         # kebab-case
[[targets]]
name = "TypeScriptSDK"        # PascalCase
```

**Resolution:** Consistent naming convention across all targets.

---

## Implementation Checklist

### Configuration

- [ ] Define all required targets
- [ ] Configure source files
- [ ] Configure shape files
- [ ] Set up query paths
- [ ] Set up template paths
- [ ] Define output patterns
- [ ] Document each target

### Queries

- [ ] Create specialized queries for each target
- [ ] Factor out shared query patterns
- [ ] Test queries produce expected data
- [ ] Document query data shapes

### Templates

- [ ] Create templates for each format
- [ ] Factor out shared template partials
- [ ] Test templates with sample data
- [ ] Document template expectations

### Verification

- [ ] All targets generate without errors
- [ ] Generated artifacts are valid
- [ ] Cross-target consistency is maintained
- [ ] CI verifies all targets

---

## Exercises

### Exercise 1: Add a New Target

Add a Markdown changelog target:
1. Define the target in ggen.toml
2. Create a SPARQL query extracting version information
3. Create a Markdown template
4. Generate and verify output

### Exercise 2: Query Composition

Given two overlapping queries:
```sparql
# Query A extracts: name, description, arguments
# Query B extracts: name, description, options
```

Factor out the common pattern and create three composed queries.

### Exercise 3: Target Dependencies

Some targets depend on others (e.g., index depends on all pages). Design a system to:
1. Track target dependencies
2. Generate in correct order
3. Regenerate dependents when sources change

### Exercise 4: Format-Specific Validation

Implement validation for generated artifacts:
1. Python: syntax check with `py_compile`
2. YAML: parse with yaml library
3. Markdown: lint with markdownlint
4. TypeScript: compile with tsc

---

## Resulting Context

After implementing this pattern, you have:

- **Multiple output formats** from single specification
- **Guaranteed consistency** across all formats
- **Consumer-optimized artifacts** for each audience
- **Scalable generation** as targets are added
- **Simplified maintenance** through single-source changes
- **Unified synchronization** with one command

Multi-target emission is the multiplicative force of specification-driven development. One specification becomes many artifacts. One change propagates everywhere. This is the efficiency that makes the approach worthwhile.

---

## Related Patterns

- **Extends:** **[24. Template Emission](./template-emission.md)** — Multiple templates
- **Produces:** **[30. Human-Readable Artifact](./human-readable-artifact.md)** — Readable outputs
- **Uses:** **[23. Extraction Query](./extraction-query.md)** — Format-specific queries
- **Enables:** **[45. Living Documentation](../evolution/living-documentation.md)** — Docs stay synced

---

## Philosophical Note

> *"Don't Repeat Yourself—even across languages and formats."*

The DRY principle typically applies within a codebase. Multi-target emission extends DRY across the entire artifact space. The specification is written once; all representations derive from it.

This is more than convenience—it's correctness. When information exists in one place, it can be one truth. When information exists in many places, it becomes many truths that inevitably diverge.

---

**Next:** Complete the Transformation Patterns with **[30. Human-Readable Artifact](./human-readable-artifact.md)**, ensuring generated output is designed for human consumption.
