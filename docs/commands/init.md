# specify init

Initialize a new ggen spec-kit project with directory structure and configuration.

## Usage

```bash
specify init PROJECT_NAME [OPTIONS]
```

## Description

The `init` command creates a new ggen spec-kit project with:
- Project directory structure
- Default configuration files
- Optional: Test setup
- Optional: OpenTelemetry observability setup
- Optional: CI/CD workflow configuration

## Arguments

### PROJECT_NAME (required)

**Format:** Lowercase alphanumeric with hyphens allowed
**Pattern:** `^[a-z][a-z0-9-]*$`
**Examples:** `my-project`, `spec-kit-fork`, `awesome-tool`

Invalid names will be rejected with suggestions:
```bash
$ specify init MyProject
❌ ProjectNameError: Name must be lowercase with hyphens only

   Received: MyProject
   Invalid characters: [A-Z]

💡 Did you mean: my-project
```

## Options

### --template, -t
**Type:** String
**Default:** `default`
**Options:** `default`, `monorepo`, `minimal`

Choose project template:
- `default`: Standard three-tier architecture with full setup
- `monorepo`: Multi-package monorepo structure
- `minimal`: Bare minimum (for experienced users)

```bash
specify init my-project --template minimal
```

### --with-tests
**Type:** Flag
**Default:** false

Include pytest configuration and example tests:

```bash
specify init my-project --with-tests
# Creates: tests/ directory with pytest.ini, conftest.py, example tests
```

### --with-observability
**Type:** Flag
**Default:** false

Include OpenTelemetry setup:

```bash
specify init my-project --with-observability
# Creates: OTEL configuration, example instrumentation, docker-compose.yml for Jaeger
```

### --with-ci-cd
**Type:** Flag
**Default:** false

Include GitHub Actions workflows:

```bash
specify init my-project --with-ci-cd
# Creates: .github/workflows/ with lint, test, and release workflows
```

### --description, -d
**Type:** String
**Default:** Empty

Project description for pyproject.toml:

```bash
specify init my-project --description "A powerful RDF specification tool"
```

### --author, -a
**Type:** String
**Default:** Git config user.name

Project author:

```bash
specify init my-project --author "Alice Smith <alice@example.com>"
```

### --license, -l
**Type:** String
**Default:** `MIT`
**Options:** `MIT`, `Apache-2.0`, `GPL-3.0`, `BSD-3-Clause`

Project license:

```bash
specify init my-project --license Apache-2.0
```

### --python, -p
**Type:** String
**Default:** `3.11`

Minimum Python version requirement:

```bash
specify init my-project --python 3.12
```

### --git
**Type:** Flag
**Default:** true

Initialize git repository:

```bash
specify init my-project --git
# Creates: .git/ and initial commit

specify init my-project --no-git
# No git initialization
```

### --verbose, -v
**Type:** Flag

Show detailed initialization output:

```bash
specify init my-project --verbose
# Shows each directory created, file written, etc.
```

## Examples

### Basic Project
```bash
$ specify init my-project
✓ Created directory: my-project/
✓ Created: pyproject.toml
✓ Created: src/my_project/
✓ Created: ontology/
✓ Created: memory/
✓ Created: docs/
✓ Initialized git repository
✓ Made initial commit

$ cd my-project
$ tree -L 2
my-project/
├── src/
│   └── my_project/
│       ├── __init__.py
│       └── cli.py
├── ontology/
│   ├── spec-kit-schema.ttl
│   └── README.md
├── memory/
│   └── README.md
├── docs/
│   └── README.md
├── pyproject.toml
├── ggen.toml
└── .gitignore
```

### Full-Featured Project
```bash
$ specify init awesome-tool \
  --with-tests \
  --with-observability \
  --with-ci-cd \
  --description "An awesome tool for RDF processing" \
  --license Apache-2.0 \
  --python 3.12

✓ Created project: awesome-tool/
✓ Added: pytest configuration
✓ Added: OpenTelemetry setup with Jaeger compose file
✓ Added: GitHub Actions workflows
✓ Initialized git repository
✓ Made initial commit

$ cd awesome-tool
```

### Monorepo Project
```bash
$ specify init my-monorepo --template monorepo
✓ Created monorepo structure
✓ Created: packages/core/
✓ Created: packages/cli/
✓ Created: packages/sdk/
✓ Created: pyproject.toml (root)
```

## Generated Structure

### Default Template
```
my-project/
├── src/my_project/           # Source code
│   ├── __init__.py
│   ├── commands/             # CLI commands (generated)
│   ├── ops/                  # Operations (pure logic)
│   ├── runtime/              # Runtime (I/O, side effects)
│   └── core/                 # Shared utilities
├── tests/                    # Test suite (if --with-tests)
│   ├── unit/
│   ├── e2e/
│   └── conftest.py
├── ontology/                 # RDF schemas (source of truth)
│   ├── spec-kit-schema.ttl
│   ├── my-schema.ttl
│   └── cli-commands.ttl
├── memory/                   # RDF specifications (source of truth)
│   └── philosophy.ttl
├── templates/                # Tera templates for code generation
├── sparql/                   # SPARQL query templates
├── docs/                     # Documentation
│   ├── README.md
│   ├── tutorials/
│   ├── guides/
│   ├── reference/
│   └── explanation/
├── .github/workflows/        # CI/CD (if --with-ci-cd)
│   ├── test.yml
│   ├── lint.yml
│   └── release.yml
├── pyproject.toml            # Python project config
├── ggen.toml                 # ggen transformation config
├── .pre-commit-config.yaml   # Pre-commit hooks
├── docker-compose.yml        # Jaeger (if --with-observability)
├── .gitignore
├── LICENSE
└── README.md
```

### Monorepo Template
```
my-monorepo/
├── packages/
│   ├── core/                 # Core library
│   ├── cli/                  # CLI interface
│   └── sdk/                  # Python SDK
├── docs/                     # Shared documentation
├── pyproject.toml            # Root config
└── .pre-commit-config.yaml
```

## Configuration Files Created

### pyproject.toml
```toml
[project]
name = "my-project"
version = "0.1.0"
description = "Project description"
requires-python = ">=3.11"
authors = [{name = "Author", email = "author@example.com"}]
license = {text = "MIT"}
dependencies = ["typer>=0.9", "rich>=13.0"]

[project.scripts]
specify = "my_project.cli:app"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=src/my_project --cov-report=term-missing"
```

### ggen.toml
```toml
[ggen]
version = "5.0.2"

[[transformation]]
name = "cli-commands"
rdf_source = "ontology/cli-commands.ttl"
sparql_queries = ["sparql/command-extract.rq"]
templates = ["templates/command.tera"]
output_dir = "src/my_project/commands"
```

## What Happens Next

After initialization:

1. **Create specifications** - Edit `.ttl` files in `ontology/` and `memory/`
2. **Run ggen sync** - `specify ggen sync` to generate code/docs
3. **Implement operations** - Edit `src/my_project/ops/` with business logic
4. **Write tests** - Create tests in `tests/`
5. **Run tests** - `uv run pytest tests/`
6. **Commit** - `git add . && git commit`

See: [Getting Started Tutorial](../tutorials/01-getting-started.md)

## Troubleshooting

### Directory Already Exists
```bash
$ specify init my-project
❌ InitError: Directory 'my-project' already exists

💡 Fix: Use a different project name or remove existing directory
  specify init another-project
  rm -rf my-project && specify init my-project
```

### Invalid Project Name
```bash
$ specify init My-Project
❌ ProjectNameError: Name must be lowercase with hyphens only

💡 Fix: Use only lowercase letters and hyphens
  specify init my-project
```

### Permission Denied
```bash
$ specify init /root/project
❌ PermissionError: Cannot create directory in /root

💡 Fix: Use a directory you have write permission for
  specify init ~/my-project
```

## See Also

- [Getting Started Tutorial](../tutorials/01-getting-started.md) - Step-by-step guide
- [First Project Tutorial](../tutorials/02-first-project.md) - Explore generated structure
- [check.md](./check.md) - Verify environment after init
- `/docs/guides/` - How-to guides for working in your project
