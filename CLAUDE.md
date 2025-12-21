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

# ggen Operations
ggen --version                       # Check ggen v5.0.2
ggen sync --config docs/ggen.toml    # Transform RDF to Markdown
ggen validate --config docs/ggen.toml # Validate RDF

# CLI
specify --help                       # Show CLI help
specify check                        # Check tool availability
specify init project-name            # Initialize project
```

## RDF-First Development

### Constitutional Equation

All specifications follow:
```
spec.md = μ(feature.ttl)
```

Where μ is the five-stage transformation:
1. **μ₁ Normalize**: Validate SHACL shapes
2. **μ₂ Extract**: Execute SPARQL queries
3. **μ₃ Emit**: Render Tera templates
4. **μ₄ Canonicalize**: Format output
5. **μ₅ Receipt**: SHA256 hash proof

### Key Locations

```
ontology/                    # Ontology schemas
├── spec-kit-schema.ttl
└── spec-kit-docs-extension.ttl

memory/                      # Specifications
├── philosophy.ttl
├── documentation.ttl
└── changelog.ttl

sparql/                      # SPARQL queries
templates/                   # Tera templates
docs/ggen.toml              # ggen configuration
```

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
