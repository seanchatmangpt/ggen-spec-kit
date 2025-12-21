# uvmgr Usage Guide

Complete user guide for all 13 uvmgr commands integrated into the specify-cli toolkit.

## Overview

The uvmgr command suite provides comprehensive Python project management capabilities, from dependency management to infrastructure automation. All commands are RDF-first, meaning they're generated from semantic specifications in Turtle format.

## Installation

```bash
# Install specify-cli with all uvmgr commands
uv sync --group all

# Or install selectively
uv sync --group deps  # Just dependency management
uv sync --group dev   # Development tools
```

## Command Reference

### 1. deps - Dependency Management

Manage project dependencies using uv's fast package manager.

#### Subcommands

**add** - Add packages to project dependencies

```bash
# Add single package
specify deps add requests

# Add multiple packages
specify deps add requests pandas numpy

# Add to development dependencies
specify deps add --dev pytest ruff mypy

# Add with specific version
specify deps add "fastapi>=0.100.0"
```

**remove** - Remove packages from dependencies

```bash
# Remove single package
specify deps remove requests

# Remove multiple packages
specify deps remove requests pandas numpy
```

**upgrade** - Upgrade packages to latest versions

```bash
# Upgrade all packages
specify deps upgrade --all

# Upgrade specific packages
specify deps upgrade requests pandas

# Upgrade with verbose output
specify deps upgrade --all --verbose
```

**list** - List installed packages

```bash
# List all installed packages
specify deps list

# With JSON output
specify deps list --format json
```

**lock** - Generate or update lock file

```bash
# Update lock file
specify deps lock

# With verbose output
specify deps lock --verbose
```

---

### 2. build - Package Building

Build Python distributions and executables.

#### Subcommands

**dist** - Build wheel and source distribution

```bash
# Build to default dist/ directory
specify build dist

# Build to custom directory
specify build dist --outdir ./releases

# Build and upload to PyPI
specify build dist --upload
```

**wheel** - Build wheel distribution only

```bash
specify build wheel

# To custom directory
specify build wheel --outdir ./dist
```

**sdist** - Build source distribution only

```bash
specify build sdist
```

**exe** - Build standalone executable with PyInstaller

```bash
# Build single-file executable
specify build exe

# Custom executable name
specify build exe --name myapp

# Build as directory (not single file)
specify build exe --onefile false

# Skip cleanup
specify build exe --clean false
```

**spec** - Generate PyInstaller spec file

```bash
# Generate default spec file
specify build spec

# Custom output path
specify build spec --outfile myapp.spec
```

**dogfood** - Build uvmgr itself (dogfooding)

```bash
# Build uvmgr executable
specify build dogfood

# Include version in name
specify build dogfood --version

# Skip post-build testing
specify build dogfood --test false
```

---

### 3. tests - Test Execution

Run comprehensive test suites with pytest and coverage.

#### Subcommands

**run** - Run test suite

```bash
# Run all tests
specify tests run

# With verbose output
specify tests run --verbose

# Sequential execution (no parallelism)
specify tests run --parallel false

# Without coverage
specify tests run --coverage false
```

**coverage** - Generate coverage reports

```bash
# Generate HTML and terminal reports
specify tests coverage

# Verbose mode
specify tests coverage --verbose

# With JSON output
specify tests coverage --format json
```

**ci** - Comprehensive CI verification

```bash
# Run full CI pipeline
specify tests ci

# With custom timeout
specify tests ci --timeout 600

# CI with JSON output
specify tests ci --format json
```

---

### 4. cache - Cache Management

Manage uv cache and build artifacts.

```bash
# Show cache status
specify cache --status

# Clear cache
specify cache --clear

# Clear with confirmation
specify cache --clear --confirm
```

---

### 5. lint - Code Quality

Run code quality checks with ruff, black, and mypy.

```bash
# Check code without fixing
specify lint --check

# Auto-fix issues
specify lint --fix

# Check and fix in one pass
specify lint --check --fix

# With JSON output
specify lint --format json
```

---

### 6. otel - OpenTelemetry

Validate and manage OpenTelemetry instrumentation.

```bash
# Validate OTEL configuration
specify otel --validate

# Check OTEL status
specify otel --status

# Show OTEL endpoints
specify otel --show-endpoints
```

---

### 7. guides - Development Guides

Access development guides and documentation.

```bash
# Show available guides
specify guides

# Show specific guide
specify guides --topic testing
specify guides --topic architecture
specify guides --topic contributing

# List all topics
specify guides --list
```

---

### 8. worktree - Git Worktree Management

Manage git worktrees for parallel development.

```bash
# Create new worktree
specify worktree --create feature-branch

# Create at specific path
specify worktree --create feature-branch --path ../worktrees/feature

# Remove worktree
specify worktree --remove feature-branch

# List worktrees
specify worktree --list
```

---

### 9. infodesign - Information Design

Tools for documentation and information architecture.

```bash
# Analyze documentation structure
specify infodesign --analyze

# Generate documentation metrics
specify infodesign --metrics

# Validate documentation completeness
specify infodesign --validate
```

---

### 10. mermaid - Diagram Generation

Generate Mermaid diagrams from code and specifications.

```bash
# Generate from Python code
specify mermaid --input src/mymodule.py

# Generate from RDF specification
specify mermaid --input ontology/schema.ttl

# Custom output path
specify mermaid --input src/ --output docs/diagrams.md

# Generate specific diagram type
specify mermaid --input src/ --type flowchart
specify mermaid --input src/ --type sequence
```

---

### 11. dod - Definition of Done

Automate Definition of Done checklists and validation.

```bash
# Check project against DoD criteria
specify dod --check

# Generate DoD report
specify dod --report

# Different output formats
specify dod --check --format text
specify dod --check --format markdown
specify dod --check --format json

# Validate specific criteria
specify dod --check --criteria "tests,coverage,docs"
```

---

### 12. docs - API Documentation

Generate and serve API documentation.

```bash
# Generate documentation
specify docs --generate

# Serve documentation locally
specify docs --serve

# Custom port
specify docs --serve --port 8080

# Generate and serve
specify docs --generate --serve

# Build for production
specify docs --generate --production
```

---

### 13. terraform - Infrastructure as Code

Terraform support and infrastructure automation.

```bash
# Initialize Terraform
specify terraform --init

# Plan changes
specify terraform --plan

# Apply changes
specify terraform --apply

# Show current state
specify terraform --show

# Validate configuration
specify terraform --validate
```

---

## Common Patterns

### Development Workflow

```bash
# 1. Add dependencies
specify deps add fastapi uvicorn

# 2. Run tests
specify tests run --verbose

# 3. Check code quality
specify lint --fix

# 4. Generate documentation
specify docs --generate

# 5. Build distribution
specify build dist
```

### CI/CD Pipeline

```bash
# Complete CI verification
specify tests ci --timeout 600

# Lint and type check
specify lint --check

# Build and verify
specify build dist
specify build exe --test
```

### Release Workflow

```bash
# 1. Ensure clean state
specify cache --clear
specify deps lock

# 2. Run full test suite
specify tests ci

# 3. Check definition of done
specify dod --check

# 4. Build distributions
specify build dist
specify build exe

# 5. Generate documentation
specify docs --generate --production

# 6. Upload to PyPI
specify build dist --upload
```

## Output Formats

Most commands support multiple output formats:

```bash
# Text (human-readable, default)
specify <command> --format text

# JSON (machine-readable)
specify <command> --format json

# Markdown (for documentation)
specify <command> --format markdown
```

## Environment Variables

Configure command behavior with environment variables:

```bash
# Enable dry-run mode (show commands without executing)
export SPECIFY_DRY=1
specify deps add requests  # Shows command but doesn't execute

# Quiet mode (suppress output)
export SPECIFY_QUIET=1
specify tests run  # Minimal output

# OpenTelemetry configuration
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
export OTEL_SERVICE_NAME=my-app
export SPECIFY_OTEL_ENABLED=true
```

## Error Handling

All commands provide comprehensive error messages:

```bash
# Exit codes
0   # Success
1   # General error
2   # Command not found
127 # Tool not available
```

Example error handling in scripts:

```bash
#!/bin/bash
set -e  # Exit on error

specify deps add requests || {
    echo "Failed to add dependency"
    exit 1
}

specify tests run || {
    echo "Tests failed"
    exit 1
}
```

## Integration with CI/CD

### GitHub Actions

```yaml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1

      - name: Install dependencies
        run: uv sync --group all

      - name: Run CI verification
        run: uv run specify tests ci

      - name: Check code quality
        run: uv run specify lint --check

      - name: Check DoD
        run: uv run specify dod --check
```

### GitLab CI

```yaml
test:
  image: python:3.12
  script:
    - pip install uv
    - uv sync --group all
    - uv run specify tests ci
    - uv run specify lint --check
```

## Telemetry

All commands emit OpenTelemetry spans and metrics when configured:

```bash
# Enable OTEL
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
export OTEL_SERVICE_NAME=specify-cli

# Commands automatically emit:
# - Spans for operation tracing
# - Metrics for operation counts
# - Events for key milestones
```

View telemetry:
- Use Jaeger for distributed tracing
- Use Prometheus for metrics
- Use Grafana for visualization

## Troubleshooting

### Command not found

```bash
# Ensure specify-cli is installed
uv sync

# Check PATH
which specify

# Run via uv
uv run specify --help
```

### Missing dependencies

```bash
# Install optional command groups
uv sync --group deps    # deps commands
uv sync --group pm      # process mining
uv sync --group wf      # workflow commands
uv sync --group all     # everything
```

### Permission errors

```bash
# Use proper permissions for cache
chmod -R u+w ~/.cache/uv

# Clean and retry
specify cache --clear
uv sync
```

### OTEL connection issues

```bash
# Check OTEL endpoint
curl http://localhost:4317

# Disable OTEL temporarily
export SPECIFY_OTEL_ENABLED=false

# Verify configuration
specify otel --validate
```

## Best Practices

1. **Use lock files**: Always commit `uv.lock` for reproducible builds
2. **Run tests locally**: Use `specify tests run` before pushing
3. **Check DoD**: Run `specify dod --check` before releasing
4. **Document changes**: Update docs with `specify docs --generate`
5. **Monitor telemetry**: Enable OTEL in development for debugging
6. **Use dry-run**: Test commands with `SPECIFY_DRY=1` first
7. **Automate CI**: Integrate `specify tests ci` in pipelines
8. **Version control**: Use `specify build dist` for releases

## Getting Help

```bash
# Global help
specify --help

# Command help
specify deps --help

# Subcommand help
specify deps add --help

# Show version
specify --version

# Show build info
specify version --build-info
```

## Next Steps

- See [ARCHITECTURE.md](./ARCHITECTURE.md) for system design
- See [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md) for adding commands
- See [RDF_SPECIFICATION.md](./RDF_SPECIFICATION.md) for RDF ontology
- See [TESTING_GUIDE.md](./TESTING_GUIDE.md) for testing
- See [TELEMETRY_GUIDE.md](./TELEMETRY_GUIDE.md) for observability
