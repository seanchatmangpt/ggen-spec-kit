---
name: doc-generator
description: Generate documentation from RDF specifications using ggen transformations. Use when creating Markdown from TTL files, managing Tera templates, or running ggen sync for documentation.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Documentation Generator

Generate Markdown documentation from RDF specifications using ggen.

## Trigger Conditions

- Creating/updating Markdown docs from RDF
- Managing documentation.ttl specifications
- Implementing ggen transformations
- Validating idempotent output

## Key Capabilities

- RDF → Markdown via ggen sync
- Tera template management
- SPARQL query alignment
- Idempotence verification (μ∘μ = μ)

## Integration

**ggen v5.0.2**: Orchestrates docs generation via ggen sync (only available command)
**Architecture**: Ops layer (no side effects until runtime output)

## Instructions

1. Run ggen sync for RDF-to-Markdown
2. Create and maintain Tera templates
3. Write SPARQL queries for extraction
4. Validate generated output
5. Ensure consistency

## Constitutional Equation

```
documentation.md = μ(documentation.ttl)
```

## Workflow

### 1. Create RDF
```turtle
sk:Guide a sk:Guide ;
    sk:documentTitle "Title" ;
    sk:documentDescription "Description" .
```

### 2. Write SPARQL
```sparql
PREFIX sk: <http://github.com/github/spec-kit#>
SELECT ?title ?description
WHERE {
    ?guide a sk:Guide ;
        sk:documentTitle ?title ;
        sk:documentDescription ?description .
}
```

### 3. Create Template
```tera
# {{ title }}

{{ description }}
```

### 4. Configure ggen.toml
```toml
[[transformations.specs]]
name = "guide"
input_files = ["docs/guide.ttl"]
sparql_query = "sparql/guide-query.rq"
template = "templates/guide.tera"
output = "docs/guide.md"
```

### 5. Generate
```bash
# ggen sync reads ggen.toml from current directory
ggen sync
```

## Template Patterns

```tera
{# Variables #}
{{ title }}
{{ description | default(value="None") }}

{# Conditionals #}
{% if status == "completed" %}✅{% endif %}

{# Loops #}
{% for item in items %}
- {{ item.title }}
{% endfor %}

{# Filters #}
{{ text | upper }}
{{ text | truncate(length=100) }}
```

## Validation

```bash
# Dry run
ggen sync --config docs/ggen.toml --dry-run

# Verify idempotence
ggen sync && HASH1=$(sha256sum output.md)
ggen sync && HASH2=$(sha256sum output.md)
[ "$HASH1" = "$HASH2" ] && echo "✅ Idempotent"
```

## Output Format

```markdown
## Documentation Generation Report

### Configuration
- Spec: `guide`
- Output: `docs/guide.md`

### Pipeline
- μ₁ Normalize: ✅
- μ₂ Extract: ✅ (12 bindings)
- μ₃ Emit: ✅ (156 lines)
- μ₄ Canonicalize: ✅
- μ₅ Receipt: ✅

### Validation
- Idempotent: ✅
```
