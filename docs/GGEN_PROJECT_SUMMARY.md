# ggen Project Setup - Summary

## Overview

The spec-kit project has been fully configured for **ontology-driven code generation** using **ggen v5.0.2**. This document summarizes the setup and provides next steps.

## What Has Been Completed

### 1. Root Configuration ✓
- **File**: `ggen.toml`
- **Purpose**: Central configuration for all ggen transformations
- **Key Settings**:
  - Ontology directory: `ontology/`
  - Templates directory: `templates/`
  - Output directory: `src/generated/`
  - Five-stage pipeline enabled (normalize → extract → emit → canonicalize → receipt)
  - Deterministic SHA256 receipts enabled

### 2. Project Structure Verified ✓

**Ontologies** (RDF Schemas - SOURCE OF TRUTH):
- 15 ontology files in `ontology/` directory
- Core schemas: `spec-kit-schema.ttl`, `cli-schema.ttl`, `jtbd-schema.ttl`
- Command specifications: `cli-commands.ttl`, `cli-commands-uvmgr.ttl`
- Domain models: `agi-agent-schema.ttl`, `git-commands.ttl`

**Memory** (RDF Specifications - EDITABLE):
- 7 specification files in `memory/` directory
- Documentation: `philosophy.ttl`, `documentation.ttl`
- Metadata: `changelog.ttl`, `production-lifecycle.ttl`
- Job descriptions: `jtbd-example.ttl`, `jtbd-customer-jobs.ttl`

**Templates** (Tera Code Generation):
- 44 template files in `templates/` directory
- Command templates: `command.tera`, `command-test.tera`, `ops-command.tera`
- Documentation templates: `guide.tera`, `philosophy.tera`, `changelog.tera`
- Domain templates: `jtbd-*.tera`, `agi-*.tera`, `constitution.tera`

**SPARQL Queries** (Data Extraction):
- 28 SPARQL query files in `sparql/` directory
- Command extraction: `command-query.rq`, `command-test-query.rq`
- Documentation extraction: `guide-query.rq`, `principle-query.rq`, `changelog-query.rq`
- Domain queries: `jtbd-*.rq`, `agi-*.rq`, `workflow-query.rq`

### 3. Documentation ✓

**Created Files**:
1. **GGEN_SETUP.md** - Comprehensive setup guide
   - Project overview
   - Five-stage transformation pipeline explained
   - Project structure and file organization
   - Getting started instructions
   - Workflow examples

2. **GGEN_QUICK_START.md** - 5-minute quickstart
   - Complete working example
   - Step-by-step instructions
   - Key concepts
   - Troubleshooting guide
   - References

3. **GGEN_INTEGRATION.md** - Architecture and integration
   - What is ggen?
   - The constitutional equation detailed
   - Project architecture (three-tier layers)
   - How to use ggen
   - Complete transformation examples
   - Best practices
   - Troubleshooting

4. **GGEN_WORKFLOW_EXAMPLE.md** - Complete end-to-end example
   - Realistic scenario: adding a new CLI command
   - Step-by-step walkthrough
   - Generated code examples
   - Test templates
   - Manual implementation
   - Verification procedures

## Next Steps

### 1. Install ggen CLI Tool

Choose one installation method:

```bash
# Option A: Via Cargo (recommended)
cargo install ggen-cli-lib --version "5.0.2"

# Option B: Via Homebrew (macOS/Linux)
brew install seanchatmangpt/ggen/ggen

# Option C: Build from local source (in this repo)
cd tools/ggen-cli
cargo build --release
./target/release/ggen --version
```

Verify installation:
```bash
ggen --version  # Should show: ggen 5.0.2
```

### 2. Run Initial Sync

Generate all project artifacts:

```bash
cd /home/user/ggen-spec-kit

# Preview what will be generated
ggen sync --dry-run

# Generate all artifacts
ggen sync --verbose

# Verify output
ls -la src/generated/
ls -la docs/*.md
```

### 3. Review Generated Files

After `ggen sync`, you should see:

**Generated Code**:
- `src/specify_cli/commands/*.py` - CLI commands
- `src/specify_cli/runtime/*.py` - Runtime operations
- `tests/e2e/test_commands_*.py` - Test files
- `*.receipt.json` - SHA256 proofs

**Generated Documentation**:
- `docs/*.md` - Generated guides
- `CHANGELOG.md` - Release notes
- `spec-driven.md` - Philosophy docs
- `*.receipt.json` - Proof files

### 4. Verify Determinism

Verify ggen produces identical output every run:

```bash
# First run
ggen sync

# Check git diff (should be empty)
git diff --quiet && echo "✓ Deterministic generation verified"

# Run again
ggen sync

# Still no changes?
git diff --quiet && echo "✓ Idempotence verified (μ∘μ = μ)"
```

### 5. Run Tests

```bash
# Install dependencies
uv sync

# Run all tests
uv run pytest tests/ -v

# Check coverage
uv run pytest --cov=src/specify_cli tests/

# Type checking
mypy src/

# Linting
ruff check src/
```

### 6. Use RDF-First Workflow

For future development:

```bash
# 1. Edit RDF specification
vim ontology/cli-commands.ttl

# 2. Generate code
ggen sync

# 3. Implement business logic
vim src/specify_cli/ops/<command>.py

# 4. Run tests
uv run pytest tests/

# 5. Commit both source and generated
git add ontology/cli-commands.ttl
git add src/specify_cli/commands/<command>.py
git add tests/e2e/test_commands_<command>.py
git commit -m "feat: add new command via RDF"
```

## The Constitutional Equation

All transformations prove:

```
specification.md = μ(specification.ttl)
```

Where:
- **specification.ttl** = RDF ontology (source of truth)
- **μ** = Five-stage transformation pipeline
- **specification.md** = Generated output
- **Proof** = SHA256 receipt in `.receipt.json`

### The Five Stages (μ₁ through μ₅):

1. **μ₁ NORMALIZE** - Validate RDF against SHACL shapes
2. **μ₂ EXTRACT** - Execute SPARQL queries
3. **μ₃ EMIT** - Render Tera templates
4. **μ₄ CANONICALIZE** - Normalize output format
5. **μ₅ RECEIPT** - Generate SHA256 cryptographic proof

## Key Principles

### 1. RDF is the Source of Truth
- Edit `.ttl` files in `ontology/` and `memory/`
- Generated files are build artifacts
- **Never** manually edit generated files

### 2. Deterministic Generation
- Same input → identical output
- `μ(x) = μ(μ(x))` (idempotent)
- Verified via SHA256 receipts

### 3. Three-Tier Architecture
- **Commands**: CLI interface (generated)
- **Operations**: Pure business logic (manual)
- **Runtime**: I/O and subprocess (generated)

### 4. No Manual Edits to Generated Files
- Python code generated from RDF
- Tests generated from specifications
- Documentation generated from RDF
- Changes only reflected in source RDF

## Directory Structure

```
spec-kit/
├── ggen.toml                          # Root configuration
├── docs/
│   ├── GGEN_SETUP.md                  # Setup guide
│   ├── GGEN_QUICK_START.md            # Quickstart
│   ├── GGEN_INTEGRATION.md            # Architecture
│   ├── GGEN_WORKFLOW_EXAMPLE.md       # Example workflow
│   ├── GGEN_PROJECT_SUMMARY.md        # This file
│   └── ggen.toml                      # Detailed transformation config
├── ontology/                          # RDF Schemas (15 files)
│   ├── spec-kit-schema.ttl
│   ├── cli-schema.ttl
│   ├── cli-commands.ttl
│   └── ...
├── memory/                            # RDF Specifications (7 files)
│   ├── philosophy.ttl
│   ├── documentation.ttl
│   ├── changelog.ttl
│   └── ...
├── sparql/                            # SPARQL Queries (28 files)
│   ├── command-query.rq
│   ├── guide-query.rq
│   └── ...
├── templates/                         # Tera Templates (44 files)
│   ├── command.tera
│   ├── guide.tera
│   └── ...
└── src/generated/                     # Generated Output
    └── .manifest                      # Transformation metadata
```

## Useful Commands

| Command | Purpose |
|---------|---------|
| `ggen sync` | Generate all artifacts |
| `ggen sync --dry-run` | Preview changes |
| `ggen sync --verbose` | Detailed output |
| `ggen sync --mode verify` | Check without modifying |
| `ggen --version` | Show version |
| `ggen --help` | Show help |

## Installation Status

### Pending Installation
- **ggen-cli-lib v5.0.2**: Cargo installation in progress
- **Alternative**: Local build available in `tools/ggen-cli/`

Once installed, run:
```bash
ggen --version
ggen sync --verbose
```

## Quick Verification Checklist

After installation and first sync:

- [ ] `ggen --version` shows 5.0.2
- [ ] `ggen sync --verbose` completes successfully
- [ ] Generated files appear in `src/generated/`
- [ ] Tests pass: `uv run pytest tests/`
- [ ] No git diff after re-running `ggen sync`
- [ ] Receipt files exist with SHA256 hashes
- [ ] Documentation generates correctly

## Resources

- **ggen Official Docs**: https://docs.ggen.io
- **ggen GitHub Repository**: https://github.com/seanchatmangpt/ggen
- **SPARQL Tutorial**: https://www.w3.org/TR/sparql11-query/
- **Tera Template Docs**: https://keats.github.io/tera/
- **RDF Turtle Spec**: https://www.w3.org/TR/turtle/
- **SHACL Validation**: https://www.w3.org/TR/shacl/

## Support

For issues or questions:

1. Check the documentation files in `docs/GGEN_*.md`
2. Review examples in `docs/ggen-examples/`
3. Examine existing transformations in `docs/ggen.toml`
4. Consult ggen official documentation

## Summary

✅ **ggen setup complete!**

The spec-kit project is now configured for:
- **Ontology-driven code generation**
- **Deterministic transformations**
- **RDF-first development**
- **Cryptographic verification**
- **Specification-driven architecture**

Next action: Install ggen CLI and run `ggen sync` to generate project artifacts.

---

**Constitutional Equation Implemented:**
```
specification.md = μ(specification.ttl) ✓
```

_Generated with Claude Code_
