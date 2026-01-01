# ggen Integration - Spec-Kit RDF-First Architecture

This document explains how ggen integrates with spec-kit to implement **ontology-driven code generation** and the **constitutional equation**:

```
specification.md = μ(specification.ttl)
```

## Table of Contents

1. [What is ggen?](#what-is-ggen)
2. [The Constitutional Equation](#the-constitutional-equation)
3. [Project Architecture](#project-architecture)
4. [How to Use ggen](#how-to-use-ggen)
5. [Example Transformations](#example-transformations)
6. [Best Practices](#best-practices)

## What is ggen?

**ggen** is a deterministic code generator that transforms RDF ontologies into code and documentation through SPARQL queries and Tera templates.

**Key Features:**
- **Ontology-Driven**: Define your domain once in RDF, generate everywhere
- **Deterministic**: Same input → identical output (reproducible builds)
- **Verifiable**: Cryptographic SHA256 receipts prove correctness
- **Five-Stage Pipeline**: Normalize → Extract → Emit → Canonicalize → Receipt
- **No Manual Edits**: Generated files are build artifacts, not source

**Why Use ggen?**
- **Single Source of Truth**: RDF is the authority, code/docs are derived
- **Semantic Validation**: OWL constraints catch domain violations early
- **Multi-Language**: Same ontology generates Rust, Python, TypeScript, etc.
- **Deterministic Builds**: `μ(x) = μ(μ(x))` - idempotent transformations
- **Verification**: SHA256 receipts cryptographically prove `spec.md = μ(feature.ttl)`

## The Constitutional Equation

The **constitutional equation** is a mathematical statement:

```
spec.md = μ(specification.ttl)
```

**What this means:**
- `specification.ttl` = RDF ontology (source)
- `μ` = Deterministic transformation function
- `spec.md` = Generated output (build artifact)
- **Proof**: SHA256 receipt in `spec.md.receipt.json`

**The Five-Stage Transformation (μ₁ through μ₅):**

### μ₁ **NORMALIZE** - RDF Validation
```
Input: RDF ontology files (.ttl, .rdf, .owl)
Process: Load RDF and validate against SHACL shapes
Output: Validated RDF graph
Proves: Input integrity via SHACL constraints
```

### μ₂ **EXTRACT** - SPARQL Queries
```
Input: Validated RDF graph
Process: Execute SPARQL SELECT/CONSTRUCT queries
Output: Structured query results (bindings, graphs)
Proves: Data extraction correctness via SPARQL semantics
```

### μ₃ **EMIT** - Template Rendering
```
Input: SPARQL query results
Process: Render Tera templates with query variables
Output: Generated code, markdown, JSON, YAML, etc.
Proves: Template correctness via side-effect-free rendering
```

### μ₄ **CANONICALIZE** - Format Normalization
```
Input: Raw generated output
Process: Normalize line endings (LF), trim whitespace, ensure final newline
Output: Formatted output (platform-independent)
Proves: Determinism via canonical formatting
```

### μ₅ **RECEIPT** - Cryptographic Proof
```
Input: Canonicalized output
Process: Compute SHA256 hash of output
Output: `.receipt.json` file with hash + metadata
Proves: spec.md = μ(specification.ttl) ✓
```

**Idempotence Property:**
```
μ(x) = μ(μ(x)) = μ(μ(μ(x))) = ...
```
Running ggen twice produces identical output.

**Determinism Property:**
```
x₁ = x₂ ⟹ μ(x₁) = μ(x₂)
```
Same input always produces same output.

## Project Architecture

### Three-Tier Layer Separation

Spec-Kit implements a **three-tier architecture** for clean separation of concerns:

```
spec_kit/
├── commands/         # CLI Interface (Generated from RDF)
│   ├── init.py       # ← Generated from ontology/cli-commands.ttl
│   ├── check.py      # ← Generated from ontology/cli-commands.ttl
│   └── ggen.py       # ← Generated from ontology/cli-commands.ttl
│
├── ops/              # Pure Business Logic (Manual Code)
│   ├── init.py       # Pure functions, no side effects
│   ├── check.py      # Return structured data (dicts)
│   └── ggen.py       # Can be tested without I/O
│
└── runtime/          # Subprocess & I/O (Generated + Manual)
    ├── process.py    # Execute subprocesses via run_logged()
    ├── http.py       # HTTP requests
    └── files.py      # File I/O operations
```

**Layer Rules:**

| Layer | Role | Side Effects | Generated? |
|-------|------|---|---|
| **Commands** | CLI interface (Typer) | Parse args, format output | ✅ Yes |
| **Operations** | Business logic | None (pure functions) | ❌ No |
| **Runtime** | I/O & subprocess | All side effects here | ✅ Yes |

### RDF Files (Source of Truth)

```
ontology/                        # Schemas (Immutable)
├── spec-kit-schema.ttl          # Core domain model
├── cli-schema.ttl               # CLI command schema
├── cli-commands.ttl             # CLI command specifications
├── jtbd-schema.ttl              # Jobs-to-be-Done model
└── agi-agent-schema.ttl         # AGI agent specifications

memory/                          # Specifications (Editable)
├── philosophy.ttl               # Philosophy principles
├── documentation.ttl            # Documentation specs
├── changelog.ttl                # Release information
└── production-lifecycle.ttl     # Production lifecycle
```

## How to Use ggen

### Installation

Choose one:

```bash
# Option 1: Via Cargo (official package)
cargo install ggen-cli-lib --version "5.0.2"

# Option 2: Via Homebrew (macOS/Linux)
brew install seanchatmangpt/ggen/ggen

# Option 3: Via Docker (no installation)
docker pull seanchatman/ggen:5.0.2
docker run --rm -v $(pwd):/workspace seanchatman/ggen:5.0.2 sync

# Option 4: Build from local source
cd /home/user/ggen-spec-kit/tools/ggen-cli
cargo build --release
./target/release/ggen --version
```

### Common Commands

```bash
# Generate all artifacts from RDF specifications
ggen sync

# Preview changes without writing files
ggen sync --dry-run

# Verbose output with detailed logging
ggen sync --verbose

# Verify consistency without modifying files (CI/CD)
ggen sync --mode verify

# Incremental sync (preserve manual edits marked with // MANUAL)
ggen sync --mode incremental

# Show version
ggen --version

# Show help
ggen --help
```

### Configuration

Root `ggen.toml` defines:

```toml
[generation]
ontology_dir = "ontology/"    # Where to load RDF files
templates_dir = "templates/"  # Where to find Tera templates
output_dir = "src/generated/" # Where to write generated files

[pipeline]
stages = ["normalize", "extract", "emit", "canonicalize", "receipt"]

[pipeline.receipt]
hash_algorithm = "sha256"     # Cryptographic proof
write_manifest = true         # Generate .receipt.json
```

## Example Transformations

### Example 1: Generate CLI Command from RDF

**RDF Specification** (`ontology/cli-commands.ttl`):
```turtle
sk:init a sk:Command ;
    rdfs:label "init" ;
    sk:description "Initialize a new spec-kit project" ;
    sk:hasArgument [
        sk:argumentName "project_name" ;
        sk:isRequired true ;
        sk:type "String"
    ] ;
    sk:hasArgument [
        sk:argumentName "template" ;
        sk:isRequired false ;
        sk:type "String" ;
        sk:defaultValue "default"
    ] .
```

**SPARQL Query** (`sparql/command-query.rq`):
```sparql
PREFIX sk: <http://spec-kit.io/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?commandName ?description ?arguments
WHERE {
    ?cmd a sk:Command ;
         rdfs:label ?commandName ;
         sk:description ?description ;
         sk:hasArgument ?arg .
    ?arg sk:argumentName ?argName .
}
```

**Tera Template** (`templates/command.tera`):
```python
# Generated: {{ commandName }}
\"\"\"{{ description }}\"\"\"

import typer
from specify_cli.ops import {{ commandName | snake_case }}

@app.command()
def {{ commandName | snake_case }}({{ arguments }}):
    \"\"\"{{ description }}\"\"\"
    result = {{ commandName | snake_case }}.execute({{ arguments | join(", ") }})
    typer.echo(result)
```

**Generated Output** (`src/specify_cli/commands/init.py`):
```python
# Generated: init
"""Initialize a new spec-kit project"""

import typer
from specify_cli.ops import init

@app.command()
def init(project_name: str, template: str = "default"):
    """Initialize a new spec-kit project"""
    result = init.execute(project_name, template)
    typer.echo(result)
```

**Receipt** (`src/specify_cli/commands/init.py.receipt.json`):
```json
{
  "file": "src/specify_cli/commands/init.py",
  "hash": "sha256:a3c8f...",
  "source": "ontology/cli-commands.ttl",
  "timestamp": "2025-01-01T12:00:00Z",
  "pipeline": ["normalize", "extract", "emit", "canonicalize", "receipt"]
}
```

### Example 2: Generate Documentation from RDF

**RDF Specification** (`memory/philosophy.ttl`):
```turtle
doc:philosophy a doc:Principle ;
    dc:title "Specification-Driven Development" ;
    dc:description "RDF is the single source of truth" ;
    doc:content "..." .
```

**SPARQL Query** (`sparql/principle-query.rq`):
```sparql
SELECT ?principle ?title ?description ?content
WHERE {
    ?principle a doc:Principle ;
               dc:title ?title ;
               dc:description ?description ;
               doc:content ?content .
}
```

**Template** (`templates/philosophy.tera`):
```markdown
# {{ title }}

{{ description }}

## Details

{{ content }}

---

_Generated from RDF via μ(philosophy.ttl)_
```

**Generated Output** (`docs/spec-driven.md`):
```markdown
# Specification-Driven Development

RDF is the single source of truth

## Details

...

---

_Generated from RDF via μ(philosophy.ttl)_
```

## Best Practices

### 1. RDF-First Workflow

```
NEVER:  Manually edit generated files
        Edit src/specify_cli/commands/init.py
        Change docs/README.md directly

INSTEAD: Edit RDF source
         ontology/cli-commands.ttl
         memory/documentation.ttl
         Run: ggen sync
```

### 2. Commit Both Artifacts

Commit both source and generated files:

```bash
git add ontology/cli-commands.ttl      # Source (RDF)
git add src/specify_cli/commands/      # Generated (Python)
git add tests/e2e/test_commands_*.py   # Generated (Tests)
git commit -m "feat: add new CLI command"
```

### 3. SPARQL Query Tips

**Do:**
```sparql
# Use OPTIONAL for fields that might not exist
OPTIONAL { ?item :property ?value }

# Use GROUP_CONCAT for lists
GROUP_CONCAT(?tag; separator=", ") AS ?tags

# Use FILTER for validation
FILTER (lang(?label) = "en")
```

**Don't:**
```sparql
# Avoid nested queries (harder to debug)
SELECT ... WHERE { ... { ... } ... }

# Avoid complex UNION patterns
SELECT ... WHERE { { ... } UNION { ... } }
```

### 4. Template Best Practices

**Do:**
```tera
# Use clear variable names
{% for command in commands %}
  {{ command.name }}: {{ command.description }}
{% endfor %}

# Add comments explaining generated code
// This was generated from {{ sourceName }}
// DO NOT EDIT - run `ggen sync` to regenerate
```

**Don't:**
```tera
# Don't make templates too complex
{% for item in items %}
  {% if item.type == "A" %}
    {% for subitem in item.subitems %}
      {{ subitem | filter | map }}
    {% endfor %}
  {% endif %}
{% endfor %}

# Avoid business logic in templates
{% if calculateComplexCondition() %}  # ✗ Bad
```

### 5. Validation Strategy

**Pre-sync validation:**
```bash
# Validate RDF syntax
rdflib --format turtle --check ontology/cli-commands.ttl

# Validate SPARQL query
SPARQL --query sparql/command-query.rq schema.rdf
```

**Post-sync validation:**
```bash
# Run generated tests
uv run pytest tests/e2e/

# Check type hints
mypy src/specify_cli/

# Lint generated code
ruff check src/specify_cli/
```

## Troubleshooting

### "ggen: command not found"

Install via Cargo:
```bash
cargo install ggen-cli-lib --version "5.0.2"
which ggen  # Should show path
```

### "Failed to load ontology"

Check:
1. File exists: `ls ontology/cli-commands.ttl`
2. Valid Turtle: Use https://www.w3.org/TR/turtle/
3. Namespaces declared: `@prefix sk: <...>`
4. URIs are valid: Start with `http://` or `https://`

### "SPARQL variable binding failed"

Check:
1. Query uses correct predicates from ontology
2. Variable names match ontology properties
3. Add `OPTIONAL` for fields that may not exist
4. Test query with: https://www.w3.org/2009/sparql/query-validator

### "Template rendering error"

Check:
1. Tera syntax valid: https://keats.github.io/tera/
2. Variables from SPARQL match template
3. Filters are available: `{{ value | uppercase }}`
4. Loops properly nested: `{% for %} ... {% endfor %}`

### "SHA256 receipt mismatch"

This means the file was modified after generation.

**Fix:**
1. Delete the generated file
2. Run `ggen sync` again
3. Don't manually edit generated files

## References

- **ggen Docs**: https://docs.ggen.io
- **ggen GitHub**: https://github.com/seanchatmangpt/ggen
- **SPARQL Tutorial**: https://www.w3.org/TR/sparql11-query/
- **Tera Template Engine**: https://keats.github.io/tera/
- **RDF/Turtle Spec**: https://www.w3.org/TR/turtle/
- **SHACL Validation**: https://www.w3.org/TR/shacl/
- **Spec-Kit CLAUDE.md**: See project guide

## Quick Reference

| Task | Command |
|------|---------|
| Generate all artifacts | `ggen sync` |
| Preview changes | `ggen sync --dry-run` |
| Verbose output | `ggen sync --verbose` |
| Verify without changes | `ggen sync --mode verify` |
| Incremental update | `ggen sync --mode incremental` |
| Show version | `ggen --version` |
| Show help | `ggen --help` |

## Architecture Diagram

```
RDF Ontologies            SPARQL Queries           Tera Templates
     ↓                          ↓                          ↓
┌─────────────┐          ┌──────────────┐        ┌──────────────┐
│   *.ttl     │          │  *.rq        │        │  *.tera      │
│             │          │              │        │              │
│ Schemas &   │          │ SELECT       │        │ {% for %}    │
│ Specs       │          │ CONSTRUCT    │        │ {{ vars }}   │
└──────┬──────┘          └──────┬───────┘        └──────┬───────┘
       │                        │                       │
       └────────────┬───────────┴───────────┬───────────┘
                    ↓
              ┌──────────────────────┐
              │   ggen sync          │
              │                      │
              │ μ₁ Normalize (SHACL) │
              │ μ₂ Extract (SPARQL)  │
              │ μ₃ Emit (Tera)       │
              │ μ₄ Canonicalize      │
              │ μ₅ Receipt (SHA256)  │
              └──────────┬───────────┘
                         ↓
            ┌────────────────────────┐
            │   Generated Artifacts  │
            │                        │
            │ - Code (Python, Rust)  │
            │ - Docs (Markdown)      │
            │ - Tests (pytest)       │
            │ - receipt.json         │
            └────────────────────────┘
```

---

**Remember: RDF is the source of truth. Generated files are build artifacts.**
