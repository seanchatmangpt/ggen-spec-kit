# Project Context Memory

## Constitutional Equation
```
spec.md = μ(feature.ttl)
```

The μ transformation pipeline:
1. **μ₁ Normalize**: Validate SHACL shapes
2. **μ₂ Extract**: Execute SPARQL queries
3. **μ₃ Emit**: Render Tera templates
4. **μ₄ Canonicalize**: Format output
5. **μ₅ Receipt**: SHA256 hash proof

## Architecture State

### Three-Tier Structure
- **Commands**: CLI interface (Typer) - thin wrappers
- **Operations**: Pure business logic - NO side effects
- **Runtime**: Subprocess, I/O, HTTP - ALL side effects

### Current File Counts
- Commands: `src/specify_cli/commands/`
- Operations: `src/specify_cli/ops/`
- Runtime: `src/specify_cli/runtime/`
- Core: `src/specify_cli/core/`

## Key Decisions

### RDF-First Development
- RDF files are the source of truth
- Generated files are build artifacts
- Edit `.ttl` files, not generated `.py` files
- Run `ggen sync` after RDF changes

### Tool Versions
- Python: 3.11+
- ggen: v5.0.2 (sync command only)
- uv: package manager
- pytest: test framework

## Common Pitfalls
1. Editing generated files instead of RDF source
2. Using `shell=True` in subprocess calls
3. Putting side effects in ops layer
4. Importing runtime from commands
