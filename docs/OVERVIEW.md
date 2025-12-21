# Specify CLI - Project Overview

**Version**: 0.0.25
**License**: MIT
**Python**: 3.11+

Specify CLI is an RDF-first specification development toolkit implementing the constitutional equation `spec.md = μ(feature.ttl)` with a strict three-tier architecture, comprehensive OpenTelemetry instrumentation, and Jobs-to-be-Done (JTBD) framework integration.

---

## Table of Contents

1. [What is Specify?](#what-is-specify)
2. [The Constitutional Equation](#the-constitutional-equation)
3. [Ten Development Phases](#ten-development-phases)
4. [Core Features](#core-features)
5. [Architecture](#architecture)
6. [Quick Start](#quick-start)
7. [Documentation Index](#documentation-index)
8. [Contributing](#contributing)

---

## What is Specify?

Specify CLI is a **spec-driven development toolkit** that transforms RDF/Turtle specifications into production-ready code, documentation, and tests. It combines:

- **RDF-First Development**: All specifications written in Turtle (`.ttl`)
- **Three-Tier Architecture**: Clean separation of CLI, business logic, and I/O
- **OpenTelemetry**: Full observability from day one
- **JTBD Framework**: Outcome-driven feature prioritization
- **Hyperdimensional Computing**: Information-theoretic quality metrics

### Key Capabilities

| Capability | Description |
|------------|-------------|
| **RDF Transformation** | `spec.md = μ(feature.ttl)` - SPARQL + Tera templates |
| **Project Management** | 13 commands for deps, build, test, lint, docs |
| **Process Mining** | Discover, validate, and optimize workflows |
| **Workflow Automation** | BPMN 2.0 via SpiffWorkflow |
| **Quality Metrics** | JTBD outcomes + hyperdimensional entropy |
| **Observability** | OTEL spans, metrics, traces built-in |

---

## The Constitutional Equation

All specifications follow:

```
spec.md = μ(feature.ttl)
```

Where **μ** is the five-stage transformation:

1. **μ₁ Normalize**: Validate SHACL shapes
2. **μ₂ Extract**: Execute SPARQL queries
3. **μ₃ Emit**: Render Tera templates
4. **μ₄ Canonicalize**: Format output
5. **μ₅ Receipt**: SHA256 hash proof

### Example Workflow

```bash
# 1. Write specification in RDF/Turtle
cat > memory/feature.ttl <<EOF
@prefix spec: <http://example.org/spec#> .

spec:UserAuthentication a spec:Feature ;
    spec:job "authenticate users securely" ;
    spec:outcome "users log in within 3 seconds" ;
    spec:priority "high" .
EOF

# 2. Transform to Markdown via ggen
ggen sync --config docs/ggen.toml

# 3. Generated output includes:
# - docs/features/user-authentication.md
# - src/auth/login.py (if code templates exist)
# - tests/test_auth_login.py (if test templates exist)
# - SHA256 receipt for verification
```

**Benefits**:
- Single source of truth (RDF)
- Automatic documentation generation
- Verifiable transformations (SHA256 receipts)
- Semantic queries via SPARQL

See [CONSTITUTIONAL_EQUATION.md](./CONSTITUTIONAL_EQUATION.md) for details.

---

## Ten Development Phases

Specify CLI supports a structured 10-phase development workflow:

### Phase 1-2: Foundation
1. **Project Initialization** - `specify init my-project`
2. **Dependency Setup** - `specify deps add typer rich`

### Phase 3-4: Specification
3. **RDF Ontology** - Define schemas in `ontology/`
4. **SPARQL Queries** - Extract data in `sparql/`

### Phase 5-6: Implementation
5. **Code Generation** - `ggen sync --config docs/ggen.toml`
6. **Test Development** - `specify tests run`

### Phase 7-8: Quality
7. **Linting & Typing** - `specify lint check`
8. **JTBD Metrics** - `specify jtbd measure`

### Phase 9-10: Delivery
9. **Documentation** - `specify docs generate`
10. **Build & Deploy** - `specify build wheel`

See individual phase guides in `docs/guides/`.

---

## Core Features

### 1. RDF-First Development

```bash
# Generate code from RDF specs
specify ggen sync --config docs/ggen.toml

# Validate RDF syntax
specify ggen validate ontology/

# Create RDF documentation
specify ggen docs --output docs/
```

### 2. Project Management (13 Commands)

| Command | Purpose |
|---------|---------|
| `deps` | Dependency management (uv) |
| `build` | Package building (wheel/sdist/exe) |
| `tests` | Test execution (pytest) |
| `cache` | Cache management |
| `lint` | Code quality (ruff, mypy) |
| `otel` | OpenTelemetry validation |
| `guides` | Development guides |
| `worktree` | Git worktree management |
| `infodesign` | Information design |
| `mermaid` | Diagram generation |
| `dod` | Definition of Done |
| `docs` | API documentation |
| `terraform` | Infrastructure as code |

### 3. Process Mining (Optional)

```bash
# Discover process model from event logs
specify pm discover event-log.csv

# Validate process conformance
specify pm validate model.bpmn log.csv

# Optimize bottlenecks
specify pm optimize model.bpmn
```

Requires: `uv sync --group pm`

### 4. Workflow Automation (Optional)

```bash
# Execute BPMN workflows
specify wf execute workflow.bpmn

# Validate BPMN syntax
specify wf validate workflow.bpmn
```

Requires: `uv sync --group wf`

### 5. JTBD Framework

```bash
# Measure outcome satisfaction
specify jtbd measure --job "generate docs"

# Calculate opportunity scores
specify jtbd opportunity --feature auth

# List all jobs
specify jtbd list
```

See [JTBD_INDEX.md](./JTBD_INDEX.md) for full documentation.

### 6. Hyperdimensional Analysis

```bash
# Measure specification entropy
specify hd entropy memory/feature.ttl

# Calculate information gain
specify hd info-gain before.ttl after.ttl

# Feature similarity
specify hd similarity feature1.ttl feature2.ttl
```

Requires: `uv sync --group hd`

See [HYPERDIMENSIONAL_QUICKSTART.md](./HYPERDIMENSIONAL_QUICKSTART.md).

---

## Architecture

### Three-Tier Design

```
┌──────────────────────────────────────────┐
│  CLI Layer (commands/)                   │
│  • Typer command handlers                │
│  • Rich output formatting                │
│  • @instrument_command decorators        │
└──────────────────┬───────────────────────┘
                   │
┌──────────────────▼───────────────────────┐
│  Operations Layer (ops/)                 │
│  • Pure business logic                   │
│  • No side effects                       │
│  • Return structured data (dicts)        │
└──────────────────┬───────────────────────┘
                   │
┌──────────────────▼───────────────────────┐
│  Runtime Layer (runtime/)                │
│  • All subprocess execution              │
│  • All file I/O                          │
│  • All HTTP requests                     │
└──────────────────────────────────────────┘
```

**Benefits**:
- Testable: Each layer tested independently
- Maintainable: Clear separation of concerns
- Observable: OTEL spans at every layer

See [ARCHITECTURE.md](./ARCHITECTURE.md) for details.

### Project Structure

```
src/specify_cli/
├── app.py                # Main Typer application
├── commands/             # CLI Layer (24 commands)
├── ops/                  # Operations Layer (19 modules)
├── runtime/              # Runtime Layer (20 modules)
├── core/                 # Shared utilities
│   ├── telemetry.py     # OpenTelemetry setup
│   ├── process.py       # Subprocess execution
│   ├── config.py        # Configuration
│   └── ...
└── cli/                  # CLI utilities
```

---

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/github/spec-kit.git
cd spec-kit

# Install with uv (recommended)
uv sync

# Or install with pip
pip install -e .

# Install optional features
uv sync --group pm    # Process mining
uv sync --group wf    # Workflows
uv sync --group hd    # Hyperdimensional
uv sync --group all   # Everything
```

### External Dependencies

```bash
# ggen v5.0.2 (required for RDF transformations)
brew install seanchatmangpt/ggen/ggen
# Or: cargo install ggen-cli-lib
# Or: docker pull seanchatman/ggen:5.0.2
```

### First Steps

```bash
# 1. Check tool availability
specify check

# 2. Initialize new project
specify init my-spec-project
cd my-spec-project

# 3. Add dependencies
specify deps add typer rich

# 4. Run tests
specify tests run

# 5. Generate docs
specify docs generate
```

---

## Documentation Index

### Getting Started
- [Installation Guide](./installation.md)
- [Quick Start](./quickstart.md)
- [Local Development](./local-development.md)

### Architecture & Design
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Three-tier architecture
- **[CONSTITUTIONAL_EQUATION.md](./CONSTITUTIONAL_EQUATION.md)** - RDF transformations
- **[RDF_DOCUMENTATION_SYSTEM.md](./RDF_DOCUMENTATION_SYSTEM.md)** - RDF/SPARQL/Tera

### Commands
- **[COMMANDS.md](./COMMANDS.md)** - Command index
- [Command Test System](./COMMAND_TEST_SYSTEM.md)
- [Command Test Quickstart](./COMMAND_TEST_QUICKSTART.md)

### JTBD Framework (10 docs)
- **[JTBD_INDEX.md](./JTBD_INDEX.md)** - Complete JTBD documentation
- [JTBD Quick Reference](./JTBD_QUICK_REFERENCE.md)
- [JTBD Framework Research](./JTBD_FRAMEWORK_RESEARCH.md)
- [JTBD Architecture](./JTBD_ARCHITECTURE.md)
- [JTBD User Guide](./JTBD_USER_GUIDE.md)
- [JTBD API Reference](./JTBD_API_REFERENCE.md)
- [JTBD Examples](./JTBD_EXAMPLES.md)

### Hyperdimensional Computing
- **[HYPERDIMENSIONAL_QUICKSTART.md](./HYPERDIMENSIONAL_QUICKSTART.md)** - Quick start
- [Hyperdimensional Dashboards](./HYPERDIMENSIONAL_DASHBOARDS.md)
- [Hyperdimensional Observability](./hyperdimensional-observability.md)

### Implementation Guides
- [UVMGR Usage Guide](./UVMGR_USAGE_GUIDE.md)
- [RDF Workflow Guide](./RDF_WORKFLOW_GUIDE.md)
- [CI/CD Workflows](./CI_CD_WORKFLOWS.md)
- [Definition of Done](./DEFINITION_OF_DONE.md)

### Development
- [Upgrade Guide](./upgrade.md)
- [Coverage Analysis](./COVERAGE_ANALYSIS.md)
- [Verification Proof](./VERIFICATION_PROOF.md)

**Total Documentation**: 50+ guides, 100+ pages

---

## Contributing

We welcome contributions! Please:

1. Read [ARCHITECTURE.md](./ARCHITECTURE.md) for design principles
2. Follow three-tier architecture (commands/ops/runtime)
3. Add OTEL instrumentation (`@instrument_command`)
4. Write tests for all three layers
5. Update RDF specifications in `ontology/`
6. Generate docs via `ggen sync`

### Development Workflow

```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Write RDF specification
vim ontology/my-feature.ttl

# 3. Generate code
ggen sync --config docs/ggen.toml

# 4. Implement three layers
vim src/specify_cli/commands/my_feature.py
vim src/specify_cli/ops/my_feature.py
vim src/specify_cli/runtime/my_feature.py

# 5. Add tests
vim tests/unit/test_ops_my_feature.py
vim tests/integration/test_runtime_my_feature.py
vim tests/e2e/test_commands_my_feature.py

# 6. Validate
specify lint check
specify tests run
specify otel validate

# 7. Commit
git add .
git commit -m "feat(my-feature): add new capability"
```

---

## License

MIT License - See [LICENSE](../LICENSE) for details.

---

## Support

- **Documentation**: https://github.com/github/spec-kit#readme
- **Issues**: https://github.com/github/spec-kit/issues
- **Discussions**: https://github.com/github/spec-kit/discussions

---

**Generated with**: Specify CLI v0.0.25
**Last Updated**: 2025-12-21
