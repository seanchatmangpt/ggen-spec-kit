# CLAUDE.md - Spec-Kit Developer Guide

This file provides guidance for Claude Code and AI agents working with spec-kit.

## Project Overview

Spec-kit is an RDF-first specification development toolkit implementing the constitutional equation:

```
spec.md = μ(feature.ttl)
```

Built with a three-tier architecture:
- **Commands**: CLI interface using Typer
- **Operations**: Pure business logic (no side effects)
- **Runtime**: Subprocess execution and I/O

## 🚨 CRITICAL: MAXIMUM CONCURRENCY

**THE GOLDEN RULE: 1 MESSAGE = ALL PARALLEL OPERATIONS**

Claude Code supports parallel tool execution. You MUST batch ALL independent operations into a SINGLE message to maximize performance.

### Parallel Patterns (MANDATORY)

#### ✅ CORRECT: Parallel Tool Calls
```javascript
// Single message with multiple independent tool calls
[Single Message]:
  Read("src/file1.py")           // Independent reads in parallel
  Read("src/file2.py")
  Read("tests/test_file.py")
  Glob("**/*.ttl")               // Independent searches in parallel
  Grep("pattern", "src/")
  Bash("git status")             // Independent commands in parallel
  Bash("uv run pytest --co -q")
```

#### ✅ CORRECT: Parallel Agent Spawning
```javascript
// Single message spawning multiple agents
[Single Message]:
  Task("Research API patterns", "researcher", "Analyze REST patterns...")
  Task("Implement endpoints", "coder", "Build API routes...")
  Task("Write tests", "tester", "Create test suite...")
  Task("Review architecture", "architect", "Validate design...")
```

#### ✅ CORRECT: Parallel File Operations
```javascript
// Single message with multiple writes (if files are independent)
[Single Message]:
  Write("src/module1.py", content1)
  Write("src/module2.py", content2)
  Write("tests/test_module1.py", testContent1)
  Write("tests/test_module2.py", testContent2)
```

#### ❌ WRONG: Sequential Messages
```javascript
// DON'T DO THIS - wastes time
Message 1: Read("file1.py")
Message 2: Read("file2.py")    // Should have been parallel!
Message 3: Grep("pattern")     // Should have been parallel!
```

### When to Use Sequential vs Parallel

**PARALLEL** (same message, no dependencies):
- Multiple file reads
- Multiple grep/glob searches
- Multiple independent bash commands
- Multiple agent spawns
- Multiple file writes to different files

**SEQUENTIAL** (separate messages, has dependencies):
- Read file → Edit based on contents
- Git add → Git commit → Git push
- Create directory → Write files into it
- Run tests → Fix failures based on output

### Concurrency Decision Tree

```
Is operation B dependent on output of A?
├── NO → Run A and B in PARALLEL (same message)
└── YES → Run A first, then B SEQUENTIALLY
```

## Agent Skills (Available)

Claude will automatically use these Skills when relevant:

| Skill | Triggers |
|-------|----------|
| `code-reviewer` | Reviewing PRs, code quality, architecture compliance |
| `test-runner` | Running pytest, fixing test failures |
| `debugger` | Diagnosing errors, tracing issues |
| `spec-writer` | Writing RDF/Turtle specifications |
| `ggen-operator` | Running ggen sync, RDF transformations |
| `otel-analyst` | OpenTelemetry traces, metrics analysis |
| `architecture-validator` | Three-tier compliance, layer boundaries |
| `rdf-validator` | Turtle syntax, SHACL validation |
| `ontology-designer` | Creating RDF classes, properties, shapes |
| `sparql-analyst` | Writing SPARQL queries |
| `performance-profiler` | Profiling, optimization |
| `doc-generator` | Generating docs from RDF |
| `changelog-writer` | Semantic changelog entries |

## Architecture

### Three-Tier Layer Structure

```
src/specify_cli/
├── commands/        # CLI interface (Typer) - thin wrappers
├── ops/             # Pure business logic - NO side effects
├── runtime/         # Subprocess, I/O, HTTP - ALL side effects
├── core/            # Shared utilities (telemetry, process, config)
└── cli/             # Banner, helpers
```

### Layer Rules

**Commands Layer** (`commands/`):
- ✅ Parse arguments, format output with Rich
- ✅ Delegate immediately to ops layer
- ❌ NO subprocess, NO file I/O, NO HTTP

**Operations Layer** (`ops/`):
- ✅ Pure business logic, validation
- ✅ Return structured data (dicts)
- ❌ NO subprocess, NO file I/O, NO HTTP

**Runtime Layer** (`runtime/`):
- ✅ All subprocess calls via `run_logged()`
- ✅ All file I/O, HTTP requests
- ❌ NO imports from commands or ops

## Key Commands

```bash
# Development
uv sync                              # Install dependencies
uv run pytest tests/ -v              # Run tests
uv run pytest --cov=src/specify_cli  # With coverage
uv run ruff check src/               # Lint
uv run mypy src/                     # Type check

# ggen Operations (ggen v5.0.2 - sync only)
ggen --version                    # Check ggen v5.0.2
ggen sync                         # Transform RDF to Markdown (reads ggen.toml from CWD)

# CLI
specify --help                       # Show CLI help
specify check                        # Check tool availability
specify init project-name            # Initialize project
```

## 🧬 RDF-First Development: The Constitutional Equation

### CRITICAL: Spec-Driven Development Principles

**THE GOLDEN RULE:**
```
spec.md = μ(feature.ttl)
```

**What This Means:**
1. **RDF is the source of truth** - NOT Python, NOT Markdown
2. **Generated files are build artifacts** - NEVER edit them manually
3. **CLI commands are generated from RDF** - Edit ontology/cli-commands.ttl, not src/specify_cli/commands/*.py
4. **Documentation is generated from RDF** - Edit memory/*.ttl, not docs/*.md
5. **Tests are generated from RDF** - Specifications drive test cases

### The μ Transformation Pipeline

```
feature.ttl → μ₁ → μ₂ → μ₃ → μ₄ → μ₅ → spec.md + receipt.json
               │     │     │     │     │
               │     │     │     │     └─ RECEIPT (SHA256 proof)
               │     │     │     └─ CANONICALIZE (format)
               │     │     └─ EMIT (Tera template)
               │     └─ EXTRACT (SPARQL query)
               └─ NORMALIZE (SHACL validation)
```

**Five Stages:**
1. **μ₁ Normalize**: Validate SHACL shapes
2. **μ₂ Extract**: Execute SPARQL queries
3. **μ₃ Emit**: Render Tera templates
4. **μ₄ Canonicalize**: Format output
5. **μ₅ Receipt**: SHA256 hash proof

**See:** `/Users/sac/ggen-spec-kit/docs/CONSTITUTIONAL_EQUATION.md` for complete reference

### Spec-Driven Workflow

```bash
# 1. Edit RDF specification (source of truth)
vim ontology/cli-commands.ttl

# 2. Validate RDF syntax and SHACL constraints
specify ggen validate-rdf ontology/cli-commands.ttl

# 3. Generate Python code, docs, tests from RDF
ggen sync  # Reads ggen.toml from CWD

# 4. Verify cryptographic receipts
specify ggen verify

# 5. Check idempotence (μ∘μ = μ)
specify ggen check-idempotence

# 6. Run generated tests
uv run pytest tests/
```

### File Structure (RDF-First)

```
ontology/                    # Ontology schemas (SOURCE OF TRUTH)
├── spec-kit-schema.ttl      # Core schema definitions
├── spec-kit-docs-extension.ttl  # Documentation extensions
└── cli-commands.ttl         # CLI command specifications → generates commands/*.py

memory/                      # Specifications (SOURCE OF TRUTH)
├── philosophy.ttl           # Philosophy docs → generates docs/spec-driven.md
├── documentation.ttl        # General docs → generates README.md
└── changelog.ttl            # Changelog → generates CHANGELOG.md

sparql/                      # SPARQL query templates
├── command-extract.rq       # Extract CLI command metadata
├── docs-extract.rq          # Extract documentation
└── changelog-extract.rq     # Extract changelog entries

templates/                   # Tera code generation templates
├── command.tera             # Python command template
├── command-test.tera        # Pytest test template
├── philosophy.tera          # Philosophy doc template
└── changelog.tera           # Changelog template

docs/ggen.toml              # ggen transformation configuration

# GENERATED FILES (Do not edit manually!)
src/specify_cli/commands/    # Generated from ontology/cli-commands.ttl
tests/e2e/test_commands_*.py # Generated from ontology/cli-commands.ttl
docs/*.md                    # Generated from memory/*.ttl
```

### When to Edit RDF vs Python

**✅ EDIT RDF (ontology/cli-commands.ttl) FOR:**
- Adding new CLI commands
- Changing command arguments/options
- Updating command descriptions
- Modifying command behavior specifications
- Adding new features to be generated

**✅ EDIT PYTHON (src/specify_cli/ops/*.py, runtime/*.py) FOR:**
- Business logic implementation
- Runtime operations
- Integration with external tools
- Core utilities and helpers

**❌ NEVER EDIT THESE (they are generated):**
- `src/specify_cli/commands/*.py` (except custom logic in ops/runtime)
- `tests/e2e/test_commands_*.py`
- `docs/*.md` (generated from memory/*.ttl)
- `CHANGELOG.md` (generated from memory/changelog.ttl)

### Example: Adding a New CLI Command

**WRONG APPROACH:**
```python
# ❌ DON'T manually create src/specify_cli/commands/validate.py
# This violates the constitutional equation!
```

**CORRECT APPROACH:**
```turtle
# ✅ Edit ontology/cli-commands.ttl
sk:validate
    a sk:Command ;
    rdfs:label "validate" ;
    sk:description "Validate RDF specifications" ;
    sk:hasArgument [
        a sk:Argument ;
        sk:name "file" ;
        sk:type "Path" ;
        sk:required true
    ] .
```

Then run:
```bash
ggen sync  # Generates Python code, tests, docs
```

### Verification Commands

```bash
# Check if generated files match RDF source
specify ggen verify

# Verify idempotence (running twice produces identical output)
specify ggen check-idempotence

# Validate RDF against SHACL shapes
specify ggen validate-rdf ontology/cli-commands.ttl

# Full verification pipeline
specify ggen sync && specify ggen verify && uv run pytest tests/
```

### Constitutional Violations

**The equation is violated when:**
- Generated files are manually edited
- RDF source and Python code diverge
- Receipts don't match current files
- Transformation is not idempotent (μ∘μ ≠ μ)

**How to fix violations:**
1. Edit the RDF source, not the generated file
2. Run `ggen sync` to regenerate
3. Run `specify ggen verify` to check consistency
4. Commit both RDF source AND generated files together

## OpenTelemetry

All operations are instrumented:

```python
from specify_cli.core.telemetry import span, timed

@timed
def operation():
    with span("operation.step", key="value"):
        # instrumented code
```

Graceful degradation when OTEL unavailable.

## Code Quality Standards

### Required
- 100% type hints on all functions
- Docstrings on public APIs (NumPy style)
- 80%+ test coverage
- No `shell=True` in subprocess calls
- List-based command construction only

### Security
- No hardcoded secrets
- Path validation before file operations
- Temporary files with 0o600 permissions

## File Organization

**NEVER save files to root folder. Use:**
- `/src` - Source code
- `/tests` - Test files
- `/docs` - Documentation
- `/scripts` - Utility scripts
- `/ontology` - RDF schemas
- `/memory` - RDF specifications
- `/sparql` - SPARQL queries
- `/templates` - Tera templates

## Git Workflow

```bash
# Commit format (via HEREDOC)
git commit -m "$(cat <<'EOF'
feat(component): Brief description

Detailed explanation if needed.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Rules:**
- NEVER use `git rebase`, only merge
- NEVER skip hooks (--no-verify)
- NEVER force push to main

## Performance Targets

- Command startup: < 500ms
- Simple operations: < 100ms
- Complex transformations: < 5s
- Memory usage: < 100MB

## Dependencies

### Core
```
typer, rich, httpx, platformdirs, readchar
opentelemetry-sdk (OTEL)
```

### Optional (dependency groups)
```bash
uv sync --group pm    # pm4py for process mining
uv sync --group wf    # SpiffWorkflow for workflows
uv sync --group dev   # pytest, ruff, mypy
uv sync --group all   # Everything
```

## Quick Concurrency Reference

| Scenario | Pattern |
|----------|---------|
| Read multiple files | Parallel Read calls |
| Search codebase | Parallel Grep + Glob |
| Run independent tests | Parallel Bash calls |
| Spawn research agents | Parallel Task calls |
| Git operations | Sequential (add → commit → push) |
| Create then write | Sequential (mkdir → write) |
| Read then edit | Sequential (read → edit) |

---

**Remember: Maximize parallelism. One message, all independent operations.**
