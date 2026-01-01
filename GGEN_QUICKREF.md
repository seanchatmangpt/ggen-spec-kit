# ggen Quick Reference

**Fast lookup for ggen v5.0.2 setup in spec-kit**

## Installation

```bash
# Recommended: Cargo
cargo install ggen-cli-lib --version "5.0.2"

# Alternative: Homebrew
brew install seanchatmangpt/ggen/ggen

# Alternative: Build locally
cd tools/ggen-cli && cargo build --release
```

Verify:
```bash
ggen --version  # Should show: ggen 5.0.2
```

## Essential Commands

| Command | What It Does |
|---------|---|
| `ggen sync` | Generate all artifacts from RDF |
| `ggen sync --dry-run` | Preview changes first |
| `ggen sync --verbose` | Show detailed output |
| `ggen sync --mode verify` | Check consistency (CI/CD) |
| `ggen --version` | Show version |
| `ggen --help` | Show full help |

## Five-Stage Pipeline

```
Input: RDF (.ttl files)
  ↓
μ₁ NORMALIZE    → Validate against SHACL shapes
  ↓
μ₂ EXTRACT      → Execute SPARQL queries
  ↓
μ₃ EMIT         → Render Tera templates
  ↓
μ₄ CANONICALIZE → Normalize format
  ↓
μ₅ RECEIPT      → Generate SHA256 proof
  ↓
Output: Generated code + .receipt.json
```

## RDF-First Workflow

1. Edit RDF source
   ```bash
   vim ontology/cli-commands.ttl
   ```

2. Generate code from RDF
   ```bash
   ggen sync
   ```

3. Implement business logic
   ```bash
   vim src/specify_cli/ops/<command>.py
   ```

4. Test and commit both
   ```bash
   uv run pytest tests/
   git add ontology/ src/specify_cli/
   git commit -m "feat: add new command"
   ```

## Key Files

| File | Purpose |
|------|---------|
| `ggen.toml` | Root configuration |
| `ontology/*.ttl` | RDF schemas (SOURCE OF TRUTH) |
| `memory/*.ttl` | RDF specifications (EDITABLE) |
| `sparql/*.rq` | SPARQL queries (DATA EXTRACTION) |
| `templates/*.tera` | Code generation templates |
| `src/generated/` | Generated output (BUILD ARTIFACTS) |
| `.receipt.json` | SHA256 proofs |

## Project Structure

```
spec-kit/
├── ggen.toml              ← Root config
├── docs/
│   ├── GGEN_SETUP.md      ← Full setup guide
│   ├── GGEN_QUICK_START.md
│   ├── GGEN_INTEGRATION.md
│   ├── GGEN_WORKFLOW_EXAMPLE.md
│   └── GGEN_PROJECT_SUMMARY.md
├── ontology/              ← RDF schemas (15 files)
├── memory/                ← RDF specs (7 files)
├── sparql/                ← SPARQL queries (28 files)
├── templates/             ← Tera templates (44 files)
└── src/generated/         ← Generated output
```

## Constitutional Equation

```
specification.md = μ(specification.ttl)
```

- **Left side**: Generated output (markdown, code, tests)
- **μ**: Five-stage transformation pipeline
- **Right side**: RDF specification source
- **Proof**: SHA256 receipt in `.receipt.json`

## The Golden Rule

> **RDF is the source of truth. Generated files are build artifacts.**

**NEVER** manually edit:
- ❌ `src/specify_cli/commands/*.py` (generated)
- ❌ `tests/e2e/test_commands_*.py` (generated)
- ❌ `docs/*.md` (generated)
- ❌ Any file with `.receipt.json`

**ALWAYS** edit:
- ✅ `ontology/*.ttl` (RDF schemas)
- ✅ `memory/*.ttl` (RDF specs)
- ✅ `src/specify_cli/ops/*.py` (business logic)
- ✅ `src/specify_cli/runtime/*.py` (I/O operations)

## Verification Checklist

After running `ggen sync`:

```bash
# Check version
ggen --version

# Run sync with verbose output
ggen sync --verbose

# Verify determinism (should show no changes)
ggen sync
git diff --quiet && echo "✓ Deterministic"

# Run tests
uv run pytest tests/ -v

# Type check
mypy src/

# Lint
ruff check src/
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ggen: command not found` | Run `cargo install ggen-cli-lib --version "5.0.2"` |
| `Failed to load ontology` | Check file exists and has valid Turtle syntax |
| `SPARQL error` | Verify query syntax and predicates match ontology |
| `Template error` | Check Tera syntax and variable names match SPARQL |
| `SHA256 mismatch` | Don't manually edit generated files - run `ggen sync` |

## Documentation Files

| File | Topic |
|------|-------|
| `docs/GGEN_SETUP.md` | Complete setup guide & concepts |
| `docs/GGEN_QUICK_START.md` | 5-minute working example |
| `docs/GGEN_INTEGRATION.md` | Architecture & best practices |
| `docs/GGEN_WORKFLOW_EXAMPLE.md` | End-to-end workflow tutorial |
| `docs/GGEN_PROJECT_SUMMARY.md` | Setup summary & checklist |
| `GGEN_QUICKREF.md` | This quick reference |

## Next Steps

1. **Install ggen**
   ```bash
   cargo install ggen-cli-lib --version "5.0.2"
   ```

2. **Run sync**
   ```bash
   ggen sync --verbose
   ```

3. **Verify output**
   ```bash
   ls -la src/generated/
   ggen sync --mode verify
   ```

4. **Run tests**
   ```bash
   uv run pytest tests/ -v
   ```

5. **Start development**
   - Edit RDF in `ontology/`
   - Run `ggen sync`
   - Implement in `ops/` layer
   - Commit both source and generated

## Resources

- **ggen Docs**: https://docs.ggen.io
- **ggen GitHub**: https://github.com/seanchatmangpt/ggen
- **SPARQL**: https://www.w3.org/TR/sparql11-query/
- **Tera**: https://keats.github.io/tera/
- **Turtle RDF**: https://www.w3.org/TR/turtle/

## One-Liners

```bash
# Install and verify
cargo install ggen-cli-lib --version "5.0.2" && ggen --version

# Generate everything
ggen sync

# Check determinism
ggen sync && git diff --quiet && echo "✓ Deterministic"

# Full pipeline
ggen sync --verbose && uv run pytest tests/ -v && mypy src/

# Dry run before committing
ggen sync --dry-run && git diff

# Verify CI/CD style
ggen sync --mode verify || exit 1
```

## Key Concept: Three Tiers

```
┌─────────────────────────────────────────┐
│ COMMANDS LAYER (generated)              │
│ CLI interface, argument parsing         │
│ → src/specify_cli/commands/*.py         │
└──────────────┬──────────────────────────┘
               ↓ (calls)
┌──────────────────────────────────────────┐
│ OPERATIONS LAYER (manual)                │
│ Pure business logic, no side effects     │
│ → src/specify_cli/ops/*.py               │
└──────────────┬───────────────────────────┘
               ↓ (calls)
┌──────────────────────────────────────────┐
│ RUNTIME LAYER (generated + manual)       │
│ Subprocess, file I/O, HTTP               │
│ → src/specify_cli/runtime/*.py           │
└──────────────────────────────────────────┘
```

**Remember**: Edit RDF, generate code, implement logic!

---

_Generated with Claude Code | ggen v5.0.2 | Spec-Kit RDF-First Architecture_
