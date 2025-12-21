---
name: ggen-operator
description: Execute ggen sync operations and manage RDF-to-Markdown transformations. Use when running ggen sync commands, validating configurations, or debugging transformation failures.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# ggen Operator

Execute ggen transformations and manage the RDF-to-Markdown pipeline.

## Instructions

1. Run ggen sync for transformations
2. Validate configurations
3. Debug transformation failures
4. Verify idempotence (μ∘μ = μ)

## ggen v5.0.2 - Only sync Command

```bash
# Version check
ggen --version

# Run sync (reads ggen.toml from current directory)
ggen sync

# With watch mode (auto-regenerate on file changes)
ggen sync --watch

# Verbose output
ggen sync --verbose

# Dry run
ggen sync --dry-run
```

**Note**: ggen v5.0.2 only has the `sync` command. All configuration is done through `ggen.toml`.

## Configuration (ggen.toml)

```toml
[project]
name = "spec-kit"
version = "0.0.23"

[[transformations.specs]]
name = "specification-name"
input_files = ["specs/feature.ttl"]
sparql_query = "sparql/query.rq"
template = "templates/output.tera"
output = "docs/output.md"
```

## Five-Stage Pipeline (μ)

1. **μ₁ Normalize**: Load RDF, validate SHACL
2. **μ₂ Extract**: Execute SPARQL queries
3. **μ₃ Emit**: Render Tera templates
4. **μ₄ Canonicalize**: Format output
5. **μ₅ Receipt**: SHA256 hash proof

## Troubleshooting

### "File not found"
```bash
ls -la path/to/file.ttl
```

### "Invalid Turtle syntax"
```bash
uv run python -c "from rdflib import Graph; g = Graph(); g.parse('file.ttl')"
```

### Idempotence Verification
```bash
ggen sync --config docs/ggen.toml
HASH1=$(sha256sum docs/output.md)
ggen sync --config docs/ggen.toml
HASH2=$(sha256sum docs/output.md)
[ "$HASH1" = "$HASH2" ] && echo "✅ Idempotent"
```

## Output Format

```markdown
## ggen Operation Summary

### Command
```bash
ggen sync --config docs/ggen.toml --spec name
```

### Pipeline Stages
- μ₁ Normalize: ✅
- μ₂ Extract: ✅
- μ₃ Emit: ✅
- μ₄ Canonicalize: ✅
- μ₅ Receipt: ✅

### Verification
- Idempotent: ✅
```
