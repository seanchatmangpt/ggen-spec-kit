# ggen Quick Start - 5-Minute Example

Learn ggen by generating a working feature in 5 minutes.

## Prerequisites

```bash
# Install ggen CLI
cargo install ggen-cli-lib --version "5.0.2"

# Verify installation
ggen --version  # Should show: ggen 5.0.2
```

## Complete Example: Generate a User Feature

### Step 1: Create RDF Specification

Create a new file `docs/examples/user-feature.ttl`:

```turtle
@prefix : <http://spec-kit.io/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Feature Definition
:UserAuthentication a :Feature ;
    :featureName "User Authentication" ;
    :description "Implement user registration and login" ;
    :priority "P0" ;
    :status "in-progress" ;
    :hasRequirement :Req001, :Req002, :Req003 .

# Requirements
:Req001 a :Requirement ;
    :requirementText "System MUST validate email format" ;
    :priority "P0" ;
    :category "validation" .

:Req002 a :Requirement ;
    :requirementText "System MUST hash passwords with bcrypt" ;
    :priority "P0" ;
    :category "security" .

:Req003 a :Requirement ;
    :requirementText "System MUST support OAuth 2.0 providers" ;
    :priority "P1" ;
    :category "integration" .
```

### Step 2: Create SPARQL Query

Create `sparql/user-feature-query.rq`:

```sparql
PREFIX : <http://spec-kit.io/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?featureName ?description ?priority ?status
       (GROUP_CONCAT(?requirement; separator="\n  - ") AS ?requirements)
WHERE {
  ?feature a :Feature ;
           :featureName ?featureName ;
           :description ?description ;
           :priority ?priority ;
           :status ?status .

  OPTIONAL {
    ?feature :hasRequirement ?req .
    ?req :requirementText ?requirement ;
         :category ?category .
  }
}
GROUP BY ?featureName ?description ?priority ?status
```

### Step 3: Create Template

Create `templates/user-feature.tera`:

```tera
# Feature: {{ featureName }}

**Priority**: {{ priority }}
**Status**: {{ status }}

## Description

{{ description }}

## Requirements

  - {{ requirements }}

## Implementation

This feature was generated from RDF via:
```
spec.md = μ(user-feature.ttl)
```

Where μ is the five-stage transformation:
1. **Normalize**: Validate RDF against SHACL
2. **Extract**: Execute SPARQL queries
3. **Emit**: Render Tera templates
4. **Canonicalize**: Normalize output format
5. **Receipt**: Generate SHA256 proof

**Verification**: Check `user-feature.md.receipt.json`

_Generated: {{ "now" | date(format="%Y-%m-%d %H:%M:%S UTC") }}_
```

### Step 4: Create ggen Configuration

Create `docs/examples/ggen-user-feature.toml`:

```toml
[metadata]
name = "user-feature-example"
description = "Generate user authentication feature documentation"
version = "1.0"

[validation]
shacl_shapes = ["ontology/spec-kit-schema.ttl"]
fail_on_warning = true

[[transformations.specs]]
name = "user-auth-feature"
description = "Generate user authentication feature spec"
input_files = ["docs/examples/user-feature.ttl"]
schema_files = ["ontology/spec-kit-schema.ttl"]
sparql_query = "sparql/user-feature-query.rq"
template = "templates/user-feature.tera"
output_file = "docs/examples/USER_FEATURE.md"
deterministic = true

[pipeline]
stages = ["normalize", "extract", "emit", "canonicalize", "receipt"]

[pipeline.normalize]
enabled = true
fail_on_validation_error = true

[pipeline.extract]
enabled = true
timeout_seconds = 30

[pipeline.emit]
enabled = true
template_engine = "tera"

[pipeline.canonicalize]
enabled = true
line_ending = "lf"
trim_trailing_whitespace = true
ensure_final_newline = true

[pipeline.receipt]
enabled = true
hash_algorithm = "sha256"
write_manifest = true
```

### Step 5: Generate Feature

Run ggen with the example configuration:

```bash
cd /home/user/ggen-spec-kit

# Preview changes
ggen sync --from docs/examples/ggen-user-feature.toml --dry-run

# Generate the feature documentation
ggen sync --from docs/examples/ggen-user-feature.toml --verbose
```

### Step 6: Check Output

The generated file `docs/examples/USER_FEATURE.md` will contain:

```markdown
# Feature: User Authentication

**Priority**: P0
**Status**: in-progress

## Description

Implement user registration and login

## Requirements

  - System MUST validate email format
  - System MUST hash passwords with bcrypt
  - System MUST support OAuth 2.0 providers

## Implementation

This feature was generated from RDF via:
```
spec.md = μ(user-feature.ttl)
```

...
```

Plus `USER_FEATURE.md.receipt.json` containing SHA256 proof.

## Running Spec-Kit's Full Generation

To generate ALL spec-kit artifacts:

```bash
# From root directory
cd /home/user/ggen-spec-kit

# Full sync with all transformations
ggen sync --verbose

# Check what was generated
ls -la src/generated/
ls -la docs/*.md
```

## Key Concepts

### 1. RDF is the Source

```turtle
# ontology/cli-commands.ttl (SOURCE OF TRUTH)
sk:init a sk:Command ;
    rdfs:label "init" ;
    sk:description "Initialize a spec-kit project" .
```

### 2. SPARQL Extracts Data

```sparql
# sparql/command-query.rq
SELECT ?commandName ?description
WHERE {
  ?cmd a sk:Command ;
       rdfs:label ?commandName ;
       sk:description ?description .
}
```

### 3. Templates Render Output

```tera
# templates/command.tera
# {{ commandName }}

{{ description }}
```

### 4. ggen Transforms End-to-End

```
feature.ttl
    ↓ (μ₁ normalize)
[RDF validation]
    ↓ (μ₂ extract)
[SPARQL queries]
    ↓ (μ₃ emit)
[Template rendering]
    ↓ (μ₄ canonicalize)
[Format normalization]
    ↓ (μ₅ receipt)
feature.md + SHA256 proof
```

## Common Workflow

```bash
# 1. Edit RDF specification
vim ontology/cli-commands.ttl

# 2. Generate code and tests from RDF
ggen sync

# 3. Verify output
ls src/specify_cli/commands/
ls tests/e2e/test_commands_*.py

# 4. Run tests
uv run pytest tests/e2e/ -v

# 5. Commit both RDF source AND generated files
git add ontology/cli-commands.ttl
git add src/specify_cli/commands/
git add tests/e2e/
git commit -m "feat: add new CLI command via RDF specification"
```

## Troubleshooting

### "ggen command not found"
```bash
cargo install ggen-cli-lib --version "5.0.2"
```

### "Failed to load ontology"
- Check file exists in `ontology/` directory
- Validate Turtle syntax: https://www.w3.org/TR/turtle/
- Ensure `@prefix` declarations are present

### "SPARQL error: Variable binding failed"
- Check query uses correct predicates from ontology
- Verify query syntax with SPARQL validator: https://www.w3.org/2009/sparql/query-validator
- Add `OPTIONAL` for fields that might not exist

### "Template rendering failed"
- Check Tera syntax: https://keats.github.io/tera/
- Verify variable names match SPARQL SELECT clause
- Use `{% for %}` for list iteration, `{{ var }}` for output

## Next Steps

1. Review existing transformations in `docs/ggen.toml`
2. Study SPARQL queries in `sparql/` directory
3. Examine Tera templates in `templates/` directory
4. Try creating your own transformation
5. Run `ggen sync` to generate complete project

## References

- **ggen Docs**: https://docs.ggen.io
- **ggen GitHub**: https://github.com/seanchatmangpt/ggen
- **SPARQL 1.1**: https://www.w3.org/TR/sparql11-query/
- **Tera Templates**: https://keats.github.io/tera/
- **RDF/Turtle**: https://www.w3.org/TR/turtle/
