# Tutorial 2: Create Your First Project

**Time to complete:** 15-20 minutes
**Prerequisites:** Complete [Tutorial 1: Getting Started](./01-getting-started.md)
**What you'll learn:** How to initialize a Spec Kit project and explore its structure

---

## Overview

Now that you have Specify CLI installed, let's create your first project. We'll initialize a new project, explore the generated structure, and understand how everything fits together.

---

## Step 1: Choose Your Project Name and Location

Pick a name for your project. Project names should be lowercase with hyphens (not spaces or underscores).

Good examples:
- `my-photo-app`
- `inventory-system`
- `user-auth-service`

Create a workspace directory to keep your projects organized:

```bash
# Create a projects directory (optional but recommended)
mkdir ~/projects
cd ~/projects
```

---

## Step 2: Initialize Your Project

Use the Specify CLI to initialize a new project:

```bash
specify init my-first-app
```

Replace `my-first-app` with your chosen project name.

This command will:
- Create a new directory with your project name
- Generate the complete project structure
- Initialize a git repository (optional)
- Create placeholder ontology and specification files

### Installation Options

If you already have a directory and want to initialize it in place:

```bash
# Initialize in current directory
specify init . --ai claude

# Or initialize existing project
cd existing-project
specify init --here --ai claude
```

The `--ai` flag tells Specify which AI assistant to use (claude, gemini, copilot, etc.).

---

## Step 3: Explore Your Project Structure

Navigate into your new project:

```bash
cd my-first-app
```

List the files to see what was created:

```bash
ls -la
```

You should see:

```
my-first-app/
├── README.md                  # Your project description
├── CLAUDE.md                  # Developer guide (for AI agents)
├── CONTRIBUTING.md            # Contribution guidelines
├── .gitignore                 # Git ignore rules
├── .github/                   # GitHub configuration
│   └── workflows/             # CI/CD workflows
│
├── ontology/                  # RDF SCHEMAS (source of truth)
│   ├── spec-kit-schema.ttl    # Core schema definitions
│   └── cli-commands.ttl       # CLI command specifications
│
├── memory/                    # RDF SPECIFICATIONS
│   ├── documentation.ttl      # Documentation specs
│   └── changelog.ttl          # Changelog specifications
│
├── sparql/                    # SPARQL QUERIES
│   ├── command-extract.rq     # Extract CLI commands
│   ├── docs-extract.rq        # Extract documentation
│   └── changelog-extract.rq   # Extract changelog
│
├── templates/                 # TERA TEMPLATES (for generation)
│   ├── command.tera           # Python command template
│   ├── command-test.tera      # Pytest test template
│   └── docs/                  # Documentation templates
│
├── src/                       # GENERATED PYTHON CODE
│   └── specify_cli/
│       ├── commands/          # Generated CLI commands
│       ├── ops/               # Business logic (you write)
│       ├── runtime/           # I/O operations (you write)
│       └── core/              # Shared utilities
│
├── tests/                     # TESTS
│   ├── unit/                  # Unit tests
│   ├── e2e/                   # End-to-end tests
│   └── conftest.py            # Pytest configuration
│
├── docs/                      # GENERATED DOCUMENTATION
│   ├── ggen.toml              # ggen transformation config
│   └── *.md                   # Generated markdown docs
│
├── pyproject.toml             # Python project configuration
├── uv.lock                    # Dependency lock file
└── .pre-commit-config.yaml    # Pre-commit hooks config
```

---

## Step 4: Understand the Directory Layout

### Directories Organized by Purpose

**RDF Specifications (What you edit):**
- `ontology/` - Domain schemas and type definitions
- `memory/` - Specifications for documentation and features

**Generation Configuration:**
- `sparql/` - SPARQL queries that extract data from RDF
- `templates/` - Tera templates that generate code/docs
- `docs/ggen.toml` - Configuration for the ggen tool

**Generated Code & Docs (Built artifacts):**
- `src/` - Generated Python code + code you write
- `docs/` - Generated documentation
- `tests/` - Generated and hand-written tests

---

## Step 5: Check Your Installation

From within your project directory, verify everything is set up:

```bash
specify check
```

This should show all tools as installed and ready.

Also check your Python environment:

```bash
# See Python version
python --version

# See installed dependencies
uv pip list
```

---

## Step 6: Review the Key Files

Let's look at the important files that guide development:

### README.md
This describes your project to users:

```bash
cat README.md
```

Edit it to describe what your project does.

### CLAUDE.md
This is special guidance for AI assistants and developers about your project's architecture:

```bash
cat CLAUDE.md
```

This file documents:
- Your three-tier architecture (commands/ops/runtime)
- Your RDF-first workflow
- Key commands to use

### pyproject.toml
Python project configuration:

```bash
cat pyproject.toml
```

This defines:
- Your project name and version
- Dependencies
- Test configuration
- Build settings

---

## Step 7: Initialize Git (Recommended)

If you didn't use `--no-git` during initialization, git is already set up:

```bash
# Check git status
git status

# See initial commit
git log --oneline
```

This is useful for tracking changes to your specifications and code.

If you need to initialize git manually:

```bash
git init
git add .
git commit -m "Initial Spec Kit project"
```

---

## Step 8: Understand the RDF-First Workflow

Your project uses RDF as the source of truth. Here's how it works:

```
1. You write RDF specifications
   ↓
2. Run 'ggen sync' to transform them
   ↓
3. RDF → Python code + Markdown docs + Tests
   ↓
4. You implement business logic (ops/ and runtime/)
   ↓
5. All tests pass and documentation stays in sync
```

### Example: Adding a CLI Command

To add a new command, you would:

1. **Edit RDF** (`ontology/cli-commands.ttl`)
   ```turtle
   sk:hello a sk:Command ;
       rdfs:label "hello" ;
       sk:description "Greet the user" .
   ```

2. **Run ggen sync** to generate Python code
   ```bash
   ggen sync
   ```

3. **Implement business logic** in `src/specify_cli/ops/hello.py`

4. **Run tests** to verify everything works

We'll cover this in detail in later tutorials.

---

## Step 9: Tour Your First Run

Let's see if everything is working by running a simple command:

```bash
# Show help
specify --help

# Show version
specify --version

# Check configuration
specify check
```

These commands should work without errors.

---

## Step 10: Next Steps

Congratulations! You've created your first Spec Kit project.

Next, you'll learn:

**[Tutorial 3: Your First RDF Specification](./03-first-rdf-spec.md)**
- Write your first RDF specification
- Understand turtle syntax
- Create a simple specification

**Or jump to:**
- **[Tutorial 4: Your First Test](./04-first-test.md)** - Create and run tests
- **[How-to: Add a CLI Command](../guides/rdf/add-cli-command.md)** - Add new functionality

---

## Troubleshooting

### `specify init` failed
- Ensure you have write permissions in the current directory
- Try creating a new directory: `mkdir test-project && cd test-project && specify init . --here`

### Missing files after initialization
- Check that the command completed without errors
- Try reinitializing: `specify init --force my-project`

### Git initialization issues
- Use `--no-git` flag if git is not available
- Initialize git manually afterward: `git init && git add . && git commit -m "Initial commit"`

### Python import errors
- Ensure all dependencies are installed: `uv sync`
- Check Python version: `python --version` (should be 3.11+)

---

## Summary

You've learned:
- ✅ How to initialize a new Spec Kit project
- ✅ The directory structure and what each folder contains
- ✅ How the RDF-first workflow works
- ✅ Key files and their purposes
- ✅ How to verify your installation

**Ready to write your first specification?** → [Continue to Tutorial 3](./03-first-rdf-spec.md)
