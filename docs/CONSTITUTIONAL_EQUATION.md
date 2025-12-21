# The Constitutional Equation

## Core Principle

```
spec.md = μ(feature.ttl)
```

**Specifications in Markdown are generated artifacts of specifications in RDF.**

This equation is the foundation of Specification-Driven Development in spec-kit.

## What It Means

1. **RDF is the Source of Truth**
   - All specifications, commands, and documentation are defined in Turtle RDF
   - RDF files are the executable source code
   - Generated files (Markdown, Python) are build artifacts

2. **μ is the Transformation Function**
   - μ consists of 5 deterministic stages
   - Each stage is pure and reproducible
   - Running μ twice produces identical output (idempotent)

3. **Generated Code Matches Specification**
   - CLI commands are generated from cli-commands.ttl
   - Documentation is generated from memory/*.ttl
   - Tests are generated from the same specifications

## The μ Pipeline

```
feature.ttl → μ₁ → μ₂ → μ₃ → μ₄ → μ₅ → spec.md + receipt.json
               │     │     │     │     │
               │     │     │     │     └─ RECEIPT (SHA256 proof)
               │     │     │     └─ CANONICALIZE (format)
               │     │     └─ EMIT (Tera template)
               │     └─ EXTRACT (SPARQL query)
               └─ NORMALIZE (SHACL validation)
```

### μ₁ NORMALIZE
- Load RDF/Turtle file
- Validate against SHACL shapes
- Fail early if constraints violated

### μ₂ EXTRACT
- Execute SPARQL query against normalized RDF
- Materialize data in JSON format
- Apply any query parameters

### μ₃ EMIT
- Load Tera template
- Render with extracted data
- Produce Markdown or Python code

### μ₄ CANONICALIZE
- Normalize line endings (LF)
- Trim trailing whitespace
- Ensure final newline

### μ₅ RECEIPT
- Hash input file (SHA256)
- Hash each intermediate stage
- Hash output file
- Write receipt.json proving transformation

## Receipts

Each generated file has a corresponding receipt:

```json
{
  "timestamp": "2025-12-20T10:30:00Z",
  "input_file": "ontology/cli-commands.ttl",
  "output_file": "src/specify_cli/commands/init.py",
  "input_hash": "a1b2c3...",
  "output_hash": "d4e5f6...",
  "stages": [
    {"stage": "normalize", "input_hash": "a1b2c3", "output_hash": "a1b2c3"},
    {"stage": "extract", "input_hash": "a1b2c3", "output_hash": "b2c3d4"},
    {"stage": "emit", "input_hash": "b2c3d4", "output_hash": "c3d4e5"},
    {"stage": "canonicalize", "input_hash": "c3d4e5", "output_hash": "d4e5f6"}
  ],
  "idempotent": true
}
```

## Idempotence Verification

To verify μ∘μ = μ:

```bash
# Run transformation twice
ggen sync --config docs/ggen.toml
HASH1=$(sha256sum README.md)

ggen sync --config docs/ggen.toml
HASH2=$(sha256sum README.md)

# Verify identical
[ "$HASH1" = "$HASH2" ] && echo "IDEMPOTENT ✓"
```

## Violations

The equation is violated when:
- Generated files are manually edited
- RDF source and output diverge
- Receipts don't match current files
- μ∘μ ≠ μ (not idempotent)

## How to Fix Violations

1. **Never edit generated files** - Edit the RDF source
2. **Regenerate after RDF changes** - Run `ggen sync`
3. **Verify receipts** - Run `specify ggen verify`
4. **Check idempotence** - Run transformation twice, compare hashes

## Manifest of Transformations

All transformations are declared in `docs/ggen.toml`:

| Output | Source | Template |
|--------|--------|----------|
| README.md | docs/overview.ttl | templates/guide.tera |
| spec-driven.md | memory/philosophy.ttl | templates/philosophy.tera |
| CHANGELOG.md | memory/changelog.ttl | templates/changelog.tera |
| commands/init.py | ontology/cli-commands.ttl | templates/command.tera |
| commands/check.py | ontology/cli-commands.ttl | templates/command.tera |
| commands/ggen.py | ontology/cli-commands.ttl | templates/command.tera |
| tests/e2e/test_commands_*.py | ontology/cli-commands.ttl | templates/command-test.tera |

## Commands

```bash
# Generate all files from RDF sources
specify ggen sync

# Validate RDF against SHACL shapes
specify ggen validate-rdf ontology/cli-commands.ttl

# Verify receipts match current files
specify ggen verify

# Check idempotence
specify ggen check-idempotence
```

## The Promise

**When you edit cli-commands.ttl and run `ggen sync`, you get:**
- Updated Python commands with correct types and docstrings
- Updated tests that verify the specification
- Updated documentation that matches the code
- Cryptographic proof that everything is consistent

**This is Specification-Driven Development.**

## Examples

### Adding a New CLI Command

```turtle
# ontology/cli-commands.ttl
sk:validate
    a sk:Command ;
    rdfs:label "validate" ;
    sk:description "Validate RDF specifications against SHACL shapes" ;
    sk:hasArgument [
        a sk:Argument ;
        sk:name "file" ;
        sk:type "Path" ;
        sk:required true ;
        sk:help "RDF file to validate"
    ] ;
    sk:hasOption [
        a sk:Option ;
        sk:name "--strict" ;
        sk:type "bool" ;
        sk:default false ;
        sk:help "Enable strict validation mode"
    ] .
```

Run transformation:
```bash
ggen sync --config docs/ggen.toml
```

Generated files:
- `src/specify_cli/commands/validate.py` - Command implementation
- `tests/e2e/test_commands_validate.py` - Command tests
- `docs/commands/validate.md` - Command documentation

### Updating Documentation

```turtle
# memory/documentation.ttl
sk:GettingStarted
    a sk:Section ;
    rdfs:label "Getting Started" ;
    sk:content """
    Install spec-kit using uv:

    ```bash
    uv pip install specify-cli
    ```

    Initialize a new project:

    ```bash
    specify init my-project
    ```
    """ .
```

Run transformation:
```bash
ggen sync --config docs/ggen.toml
```

Generated: `docs/getting-started.md`

## Verification Workflow

```bash
# 1. Edit RDF source
vim ontology/cli-commands.ttl

# 2. Validate RDF syntax
specify ggen validate-rdf ontology/cli-commands.ttl

# 3. Generate artifacts
specify ggen sync

# 4. Verify receipts
specify ggen verify

# 5. Check idempotence
specify ggen check-idempotence

# 6. Run tests
uv run pytest tests/
```

## Philosophy

The constitutional equation enforces:

1. **Single Source of Truth** - RDF is authoritative
2. **Traceability** - Every artifact has provenance
3. **Consistency** - Code matches documentation matches tests
4. **Reproducibility** - Transformations are deterministic
5. **Verifiability** - Cryptographic receipts prove correctness

## Why This Matters

Traditional development:
```
Code → Documentation (manual, diverges)
      ↓
      Tests (manual, incomplete)
```

Spec-driven development:
```
RDF Specification
      ↓ μ
      ├─→ Code (generated, consistent)
      ├─→ Documentation (generated, consistent)
      └─→ Tests (generated, comprehensive)
```

Benefits:
- Zero drift between code and documentation
- Comprehensive test coverage by construction
- Architectural compliance enforced by SHACL
- Every change traceable to specification
- Auditable transformation pipeline

## Advanced: Custom Transformations

### Define Custom SPARQL Query

```sparql
# sparql/my-feature.rq
PREFIX sk: <https://spec-kit.org/schema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?name ?description ?type
WHERE {
  ?feature a sk:Feature ;
           sk:name ?name ;
           sk:description ?description ;
           sk:type ?type .
}
```

### Define Custom Tera Template

```tera
{# templates/my-feature.tera #}
# {{ name }}

{{ description }}

**Type:** {{ type }}
```

### Configure in ggen.toml

```toml
[[targets]]
output = "docs/features/{{ name }}.md"
query = "sparql/my-feature.rq"
template = "templates/my-feature.tera"
source = "memory/features.ttl"
```

### Run Transformation

```bash
ggen sync --config docs/ggen.toml
```

## Troubleshooting

### Generated file differs from source
```bash
# Regenerate from RDF
ggen sync --config docs/ggen.toml

# Verify receipts
specify ggen verify
```

### SHACL validation fails
```bash
# Check specific file
specify ggen validate-rdf ontology/cli-commands.ttl

# Fix violations in RDF source
vim ontology/cli-commands.ttl
```

### Idempotence check fails
```bash
# Run twice and compare
ggen sync --config docs/ggen.toml
cp README.md README.md.1

ggen sync --config docs/ggen.toml
cp README.md README.md.2

diff README.md.1 README.md.2
```

## References

- [Specification-Driven Development](/Users/sac/ggen-spec-kit/docs/spec-driven.md)
- [ggen Documentation](https://github.com/ruvnet/ggen)
- [RDF Primer](https://www.w3.org/TR/rdf11-primer/)
- [SHACL Specification](https://www.w3.org/TR/shacl/)
- [SPARQL 1.1 Query Language](https://www.w3.org/TR/sparql11-query/)
- [Tera Template Engine](https://keats.github.io/tera/)
