# ggen Setup Guide - Spec-Kit

This document describes the ontology-driven code generation setup for Spec-Kit using **ggen v5.0.2**.

## Overview

Spec-Kit implements the **constitutional equation**:

```
spec.md = μ(specification.ttl)
```

Where:
- **spec.md** = Generated documentation output
- **μ** = Five-stage transformation pipeline
- **specification.ttl** = RDF source of truth

## Five-Stage Transformation Pipeline (μ₁ through μ₅)

The `ggen` tool implements a deterministic transformation pipeline:

### μ₁ **NORMALIZE**: RDF Validation
- Load RDF ontologies from `.ttl` files
- Validate against SHACL shapes
- Fail fast on validation errors
- Ensures data quality at input

### μ₂ **EXTRACT**: SPARQL Queries
- Execute SPARQL SELECT/CONSTRUCT queries
- Extract relevant data from RDF graph
- Materialize implicit relationships via inference
- Produce structured data for template rendering

### μ₃ **EMIT**: Template Rendering
- Render Tera templates with SPARQL results
- Generate code, docs, tests from templates
- Support Jinja2-like syntax
- Produce human-readable output

### μ₄ **CANONICALIZE**: Format Normalization
- Normalize line endings to LF
- Trim trailing whitespace
- Ensure final newline
- Consistent output across platforms

### μ₅ **RECEIPT**: Cryptographic Proof
- Generate SHA256 hash of output
- Create `.receipt.json` manifest
- Proves `spec.md = μ(feature.ttl)`
- Enable deterministic verification

## Project Structure

```
spec-kit/
├── ggen.toml                          # Root configuration (THIS FILE)
│
├── ontology/                          # RDF Schemas (SOURCE OF TRUTH)
│   ├── spec-kit-schema.ttl            # Core domain model
│   ├── spec-kit-docs-extension.ttl    # Documentation extensions
│   ├── cli-schema.ttl                 # CLI command schema
│   ├── cli-commands.ttl               # CLI command specifications
│   ├── cli-commands-uvmgr.ttl         # uvmgr command specifications
│   ├── cli-commands-uvmgr-full.ttl    # Full uvmgr runtime specs
│   ├── jtbd-schema.ttl                # Jobs-to-be-Done schema
│   ├── agi-agent-schema.ttl           # AGI agent specifications
│   └── ... (other domain schemas)
│
├── memory/                            # RDF Specifications (SOURCE OF TRUTH)
│   ├── philosophy.ttl                 # Philosophy principles
│   ├── documentation.ttl              # Documentation specs
│   ├── changelog.ttl                  # Release changelog
│   ├── production-lifecycle.ttl       # Production lifecycle
│   └── ... (other specifications)
│
├── sparql/                            # SPARQL Query Templates
│   ├── guide-query.rq                 # Extract guide documentation
│   ├── command-query.rq               # Extract CLI commands
│   ├── principle-query.rq             # Extract principles
│   ├── changelog-query.rq             # Extract changelog entries
│   └── ... (other SPARQL queries)
│
├── templates/                         # Tera Code Generation Templates
│   ├── guide.tera                     # Guide documentation template
│   ├── philosophy.tera                # Philosophy docs template
│   ├── command.tera                   # CLI command template
│   ├── command-test.tera              # Command test template
│   ├── changelog.tera                 # Changelog template
│   └── ... (other templates)
│
├── src/generated/                     # GENERATED OUTPUT (build artifacts)
│   ├── .manifest                      # Transformation manifest
│   └── ... (generated files)
│
└── docs/ggen-examples/               # Complete working example
    ├── ggen.toml                     # Example configuration
    ├── feature.ttl                   # Example RDF specification
    ├── feature-query.rq              # Example SPARQL query
    ├── feature.tera                  # Example template
    ├── README.md                     # Generated output
    └── README.md.receipt.json        # SHA256 proof
```

## Getting Started

### 1. Installation

**Option A: Via Cargo**
```bash
cargo install ggen-cli-lib --version "5.0.2"
```

**Option B: Via Homebrew** (macOS/Linux)
```bash
brew install seanchatmangpt/ggen/ggen
```

**Option C: Via Docker**
```bash
docker pull seanchatman/ggen:5.0.2
```

Verify installation:
```bash
ggen --version  # Should show: ggen 5.0.2
```

### 2. Configuration

The root-level `ggen.toml` defines:
- Project metadata (name, version, description)
- Ontology directory: `ontology/`
- Templates directory: `templates/`
- Output directory: `src/generated/`
- Pipeline stages (normalize → extract → emit → canonicalize → receipt)

### 3. Run Sync

Generate all project files from RDF specifications:

```bash
# Basic sync (full regeneration)
ggen sync

# Dry-run preview (no file writes)
ggen sync --dry-run

# Verbose output (detailed logging)
ggen sync --verbose

# Verify consistency without modifying files
ggen sync --mode verify

# Incremental sync (preserve manual edits marked with // MANUAL)
ggen sync --mode incremental
```

## Workflow: RDF-First Development

### To Add a New CLI Command

**NEVER** manually edit Python files. Instead:

1. **Edit RDF specification**:
   ```turtle
   # ontology/cli-commands.ttl
   sk:validate a sk:Command ;
       rdfs:label "validate" ;
       sk:description "Validate RDF specifications" ;
       sk:hasArgument [ ... ] .
   ```

2. **Generate Python code from RDF**:
   ```bash
   ggen sync
   ```

3. **The generated command appears at**:
   - `src/specify_cli/commands/validate.py`
   - `tests/e2e/test_commands_validate.py`

### To Update Documentation

**NEVER** manually edit Markdown files. Instead:

1. **Edit RDF specification**:
   ```turtle
   # memory/documentation.ttl
   doc:installation a sk:Guide ;
       sk:documentTitle "Installation Guide" ;
       ... .
   ```

2. **Generate Markdown from RDF**:
   ```bash
   ggen sync
   ```

3. **The output appears at**:
   - `docs/installation.md`
   - `docs/installation.md.receipt.json`

## Key Concepts

### 1. Source of Truth

RDF files are the **sole source of truth**:
- `ontology/*.ttl` - Schema definitions (immutable)
- `memory/*.ttl` - Specifications (editable)

Generated files (code, docs, tests) are **build artifacts**—never edit them manually.

### 2. Deterministic Output

ggen generates **identical output** from identical input:
```
μ(input) = μ(μ(input))  # Idempotent
input₁ = input₂ ⟹ μ(input₁) = μ(input₂)  # Deterministic
```

Proves correctness via SHA256 receipts.

### 3. SPARQL Queries Extract Data

SPARQL queries (`sparql/*.rq`) extract relevant facts from RDF:

```sparql
SELECT ?featureName ?description
WHERE {
  ?feature a :Feature ;
           :featureName ?featureName ;
           :description ?description .
}
```

Results populate template variables.

### 4. Tera Templates Generate Output

Jinja2-like syntax renders templates:

```tera
# Document: {{ title }}

{% for item in items %}
- {{ item.name }}: {{ item.description }}
{% endfor %}
```

Output can be Python, Markdown, JSON, YAML, etc.

## Three-Layer Architecture

Spec-Kit uses **three-tier separation**:

### Commands Layer (`src/specify_cli/commands/`)
- CLI interface using Typer
- Argument parsing and validation
- Format output with Rich
- Generated from RDF via ggen

### Operations Layer (`src/specify_cli/ops/`)
- Pure business logic
- No side effects
- Returns structured data
- Manual implementation

### Runtime Layer (`src/specify_cli/runtime/`)
- Subprocess execution
- File I/O and HTTP
- All side effects isolated here
- Generated from RDF via ggen

**Generated files live in Commands and Runtime layers.**
**Operations layer is manually coded.**

## Example: Complete Workflow

### Step 1: Define Feature in RDF

```turtle
# ontology/feature.ttl
@prefix sk: <http://spec-kit.io/ns#> .

sk:personModel a sk:Feature ;
    sk:name "Person Model" ;
    sk:description "Implement Person data type" ;
    sk:hasProperty [
        sk:propertyName "name" ;
        sk:propertyType "String"
    ] .
```

### Step 2: Write SPARQL Query

```sparql
# sparql/feature-query.rq
PREFIX sk: <http://spec-kit.io/ns#>

SELECT ?name ?description (GROUP_CONCAT(?prop) AS ?properties)
WHERE {
    ?feature sk:name ?name ;
             sk:description ?description ;
             sk:hasProperty ?propObj .
    ?propObj sk:propertyName ?prop .
}
GROUP BY ?name ?description
```

### Step 3: Create Tera Template

```tera
# templates/feature.tera
# {{ name }}

{{ description }}

## Properties

{% for prop in properties | split(pat=",") %}
- {{ prop }}
{% endfor %}
```

### Step 4: Run ggen

```bash
ggen sync
```

### Step 5: Output Generated

```markdown
# Person Model

Implement Person data type

## Properties

- name
```

Plus a `feature.md.receipt.json` SHA256 proof.

## Common Commands

```bash
# Generate all artifacts
ggen sync

# Preview changes
ggen sync --dry-run

# Verify without modifying
ggen sync --mode verify

# Incremental update (preserves manual code)
ggen sync --mode incremental

# Check ggen version
ggen --version

# Show help
ggen --help
```

## Troubleshooting

### "ggen command not found"

Install via Cargo:
```bash
cargo install ggen-cli-lib --version "5.0.2"
```

### "Failed to load ontology"

Check:
1. Ontology files exist in `ontology/` directory
2. File format is valid Turtle (.ttl)
3. RDF namespaces are declared with `@prefix`

### "SPARQL query error"

Check:
1. Query file exists at path in ggen.toml
2. SPARQL syntax is valid (SELECT/CONSTRUCT)
3. Query uses correct RDF predicates from ontology

### "Template rendering failed"

Check:
1. Template file exists at path in ggen.toml
2. Tera syntax is valid ({% ... %} blocks)
3. Variables from SPARQL match template variables

## References

- **ggen Documentation**: https://docs.ggen.io
- **ggen GitHub**: https://github.com/seanchatmangpt/ggen
- **SPARQL Tutorial**: https://www.w3.org/TR/sparql11-query/
- **Tera Templates**: https://keats.github.io/tera/
- **RDF/Turtle**: https://www.w3.org/TR/turtle/
- **Spec-Kit Philosophy**: See `memory/philosophy.ttl` (generates `spec-driven.md`)

## Constitutional Equation

The ggen transformation proves the constitutional equation mathematically:

```
GIVEN:    feature.ttl (RDF specification)
          command-query.rq (SPARQL query)
          command.tera (Tera template)

COMPUTE:  μ(feature.ttl) = (normalize → extract → emit → canonicalize → receipt)

PROVE:    SHA256(output) = μ₅(...)
          ⟹ command.py = μ(feature.ttl) ✓

VERIFY:   specify verify  # Check receipt integrity
          ⟹ Cryptographic proof of correctness
```

This ensures **spec-driven development**: specifications drive tests, code, and docs.
