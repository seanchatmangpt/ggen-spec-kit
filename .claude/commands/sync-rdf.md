# Sync RDF to Generated Files

Execute the constitutional equation transformation pipeline using ggen v5.0.2.

## Description
Transforms RDF specifications into generated Python code, documentation, and tests via the μ transformation pipeline. This is the core of the RDF-first development approach.

## Usage
```bash
/sync-rdf
```

## No Arguments Required
This command runs `ggen sync` which reads configuration from `ggen.toml` in the current directory.

## Examples
```bash
# Standard sync after RDF changes
/sync-rdf

# Typical workflow
# 1. Edit RDF source
# 2. Run sync
/sync-rdf
# 3. Verify tests
/run-tests
```

## What This Command Does

Implements the constitutional equation:
```
spec.md = μ(feature.ttl)
```

### The μ Transformation Pipeline

```
feature.ttl → μ₁ → μ₂ → μ₃ → μ₄ → μ₅ → spec.md + receipt.json
               │     │     │     │     │
               │     │     │     │     └─ μ₅ RECEIPT (SHA256 proof)
               │     │     │     └─ μ₄ CANONICALIZE (format)
               │     │     └─ μ₃ EMIT (Tera template)
               │     └─ μ₂ EXTRACT (SPARQL query)
               └─ μ₁ NORMALIZE (SHACL validation)
```

### Five Transformation Stages

1. **μ₁ Normalize**: Validate RDF against SHACL shapes
2. **μ₂ Extract**: Execute SPARQL queries to extract data
3. **μ₃ Emit**: Render Tera templates with extracted data
4. **μ₄ Canonicalize**: Format and prettify output
5. **μ₅ Receipt**: Generate SHA256 hash proof of transformation

## Execution Steps

### 1. Run ggen sync

```bash
ggen sync  # Uses ggen v5.0.2
```

Reads configuration from `ggen.toml`:
```toml
[project]
name = "spec-kit"
ontology_path = "ontology/"
output_path = "src/specify_cli/"

[transformations]
# CLI Commands: TTL → Python
[[transformations.spec]]
source = "ontology/cli-commands.ttl"
query = "sparql/command-extract.rq"
template = "templates/command.tera"
output = "src/specify_cli/commands/{name}_cmd.py"

# Documentation: TTL → Markdown
[[transformations.spec]]
source = "memory/philosophy.ttl"
query = "sparql/docs-extract.rq"
template = "templates/philosophy.tera"
output = "docs/spec-driven.md"
```

### 2. Report Generated Files

```
Transforming RDF specifications...

μ₁ NORMALIZE: Validating SHACL shapes... ✓
μ₂ EXTRACT:   Executing SPARQL queries... ✓
μ₃ EMIT:      Rendering Tera templates... ✓
μ₄ CANONICALIZE: Formatting output... ✓
μ₅ RECEIPT:   Generating SHA256 proofs... ✓

Generated Files:
  src/specify_cli/commands/validate_cmd.py
  src/specify_cli/commands/export_cmd.py
  tests/e2e/test_commands_validate.py
  tests/e2e/test_commands_export.py
  docs/CHANGELOG.md
  docs/spec-driven.md

Receipts:
  .ggen/receipts/validate_cmd.json
  .ggen/receipts/export_cmd.json
```

### 3. Verify Transformation

```bash
# Run tests to verify generated code
uv run pytest tests/ -v
```

### 4. Check for Errors

Common issues:
- SHACL validation failures (μ₁)
- SPARQL query errors (μ₂)
- Tera template errors (μ₃)
- File permission issues (μ₄)

## Output Format

### Successful Sync
```
✅ RDF Sync Complete

Transformation Pipeline:
  μ₁ NORMALIZE    ✓  (0.12s)
  μ₂ EXTRACT      ✓  (0.08s)
  μ₃ EMIT         ✓  (0.15s)
  μ₄ CANONICALIZE ✓  (0.05s)
  μ₅ RECEIPT      ✓  (0.03s)

Generated: 6 files
Updated: 2 files
Receipts: 8 files

Next Steps:
1. Review generated files
2. Run tests: /run-tests
3. Commit RDF source + generated files together
```

### Sync with Errors
```
❌ RDF Sync Failed

μ₁ NORMALIZE: SHACL validation errors

Error in ontology/cli-commands.ttl:
  Line 23: Missing required property rdfs:label
  Shape: sk:CommandShape
  Focus node: sk:validate

Fix: Add rdfs:label to command definition
```

## What Gets Generated

### From ontology/cli-commands.ttl
```turtle
sk:validate
    a sk:Command ;
    rdfs:label "validate" ;
    sk:description "Validate RDF specifications" .
```

**Generates:**
- `src/specify_cli/commands/validate_cmd.py` - CLI command
- `tests/e2e/test_commands_validate.py` - E2E test

### From memory/changelog.ttl
```turtle
:entry-2025-12-29-1
    a :ChangelogEntry ;
    :changeType "added" ;
    :description "RDF validation command" .
```

**Generates:**
- `CHANGELOG.md` - Formatted changelog

### From memory/philosophy.ttl
```turtle
:spec-driven-development
    a :DocumentationSection ;
    :title "Spec-Driven Development" ;
    :content "..." .
```

**Generates:**
- `docs/spec-driven.md` - Documentation

## File Relationships

### Source Files (Edit These)
```
ontology/cli-commands.ttl     → SOURCE OF TRUTH
memory/changelog.ttl          → SOURCE OF TRUTH
memory/philosophy.ttl         → SOURCE OF TRUTH
sparql/*.rq                   → Query templates
templates/*.tera              → Code templates
ggen.toml                     → Transformation config
```

### Generated Files (DO NOT EDIT)
```
src/specify_cli/commands/*.py    → Generated from ontology/
tests/e2e/test_commands_*.py     → Generated from ontology/
docs/*.md                        → Generated from memory/
CHANGELOG.md                     → Generated from memory/
```

### Receipt Files (Build Artifacts)
```
.ggen/receipts/*.json         → SHA256 proofs
```

## CRITICAL: Constitutional Equation Rules

### ✅ CORRECT Workflow
```bash
# 1. Edit RDF source
vim ontology/cli-commands.ttl

# 2. Run transformation
ggen sync

# 3. Verify
uv run pytest tests/ -v

# 4. Commit BOTH source and generated
git add ontology/cli-commands.ttl
git add src/specify_cli/commands/validate_cmd.py
git commit -m "feat: add validate command"
```

### ❌ WRONG Workflow
```bash
# DON'T edit generated files directly!
vim src/specify_cli/commands/validate_cmd.py  # ❌ VIOLATION

# This breaks the constitutional equation
# Source and generated files will diverge
```

## Verification Commands

### Check RDF-Python Consistency
```bash
# Run sync
ggen sync

# Check for uncommitted changes to generated files
git status

# If files changed, source and generated were out of sync
```

### Verify Receipts
```bash
# Receipts contain SHA256 hashes proving:
# 1. What RDF source was used
# 2. What template was used
# 3. What output was generated
# 4. When transformation occurred

cat .ggen/receipts/validate_cmd.json
```

## Integration

Works with:
- `ggen v5.0.2` - RDF transformation engine
- `ggen.toml` - Configuration file
- `/run-tests` - Post-sync verification
- `/lint` - Code quality checks
- `/changelog` - Changelog management
- `/create-feature` - Feature scaffolding

## Transformation Configuration

Located in `ggen.toml`:

```toml
[project]
name = "spec-kit"

[rdf]
ontology_paths = ["ontology/"]
memory_paths = ["memory/"]

[sparql]
query_path = "sparql/"

[templates]
template_path = "templates/"

[output]
receipt_path = ".ggen/receipts/"
```

## Common Issues and Solutions

### Issue: SHACL Validation Fails
```
μ₁ NORMALIZE: SHACL validation error
```

**Solution**: Fix RDF source to match SHACL shapes
```bash
# Check SHACL shapes
cat ontology/spec-kit-schema.ttl

# Fix RDF source
vim ontology/cli-commands.ttl
```

### Issue: SPARQL Query Fails
```
μ₂ EXTRACT: SPARQL syntax error
```

**Solution**: Fix SPARQL query
```bash
# Check query
cat sparql/command-extract.rq

# Test query independently
# Fix syntax
```

### Issue: Template Rendering Fails
```
μ₃ EMIT: Tera template error
```

**Solution**: Fix Tera template
```bash
# Check template
cat templates/command.tera

# Fix template syntax
```

### Issue: Generated Files Not Created
```
ggen sync completed but no files changed
```

**Solution**: Check ggen.toml configuration
```bash
# Verify paths
cat ggen.toml

# Check output paths exist
ls -la src/specify_cli/commands/
```

## Performance

Typical transformation times:
- Small changes: < 1s
- Full rebuild: < 5s
- Large codebase: < 10s

## Notes
- Always run after editing any `.ttl` file
- Commit RDF source and generated files together (atomicity)
- Never edit generated files manually
- Receipts provide audit trail of transformations
- Transformation is idempotent: μ∘μ = μ
- ggen v5.0.2 only supports `sync` command
- Configuration is read from `ggen.toml` in CWD
- Generated files are deterministic (same input → same output)
