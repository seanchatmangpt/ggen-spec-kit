# Tutorial 1: Getting Started with ggen Spec Kit

**Time to complete:** 10-15 minutes
**Prerequisites:** Python 3.11+ and `uv` package manager
**What you'll learn:** How to install Spec Kit and verify it works

---

## Overview

ggen Spec Kit is an RDF-first specification-driven development toolkit. In this tutorial, we'll install it, verify the installation, and see what it can do.

By the end of this tutorial, you'll have:
- ✅ Installed the Specify CLI tool
- ✅ Verified your installation
- ✅ Understood the three core concepts

---

## Step 1: Install the Specify CLI Tool

The Specify CLI is the command-line interface for ggen Spec Kit. We'll install it persistently so you can use it anywhere.

### Prerequisites Check

First, make sure you have Python and `uv` installed:

```bash
# Check Python version (should be 3.11 or higher)
python --version

# Check uv is installed
uv --version
```

If you don't have `uv`, install it:
```bash
pip install uv
```

### Install Specify

Install the Specify CLI from GitHub:

```bash
uv tool install specify-cli --from git+https://github.com/seanchatmangpt/ggen-spec-kit.git
```

This command:
- Downloads the latest version of Specify
- Installs it in your Python environment
- Makes the `specify` command available globally

### Verify Installation

Test that installation worked:

```bash
specify --version
```

You should see output like:
```
Specify CLI version 0.0.25
```

---

## Step 2: Check Your System

Specify needs several tools to work properly. Let's verify your system has them installed:

```bash
specify check
```

This checks for:
- ✅ `git` - Version control
- ✅ `ggen` - RDF transformation engine
- ✅ `uv` - Python package manager
- ⚠️ AI assistants (Claude, Gemini, etc.) - optional but recommended

### What Each Tool Does

| Tool | Purpose |
|------|---------|
| **git** | Track changes to your specifications and code |
| **ggen** | Transform RDF specifications into code and docs |
| **uv** | Manage Python dependencies and environments |
| **AI Assistant** | Help you write specifications and implement features |

If a tool is missing, follow the prompts in the output.

---

## Step 3: Understand the Three Core Concepts

Before we create our first project, let's understand what makes Spec Kit unique:

### 1. RDF-First Development

Instead of writing code first, you write **specifications in RDF** (Resource Description Framework). RDF is a semantic format that describes your domain in a way machines can understand.

**The Constitutional Equation:**
```
spec.md = μ(feature.ttl)
```

This means: "Markdown documentation is generated from RDF specifications."

### 2. The Three-Tier Architecture

Spec Kit organizes code into three clean layers:

```
Commands       ← CLI interface (user-facing)
    ↓
Operations     ← Pure business logic (no side effects)
    ↓
Runtime        ← I/O, subprocess, HTTP (all side effects)
```

This separation keeps code clean and testable.

### 3. Transformation Pipeline

When you write RDF specifications, the `ggen` tool transforms them through five stages:

```
RDF → Normalize → Extract → Emit → Canonicalize → Document + Receipt
```

Each stage is deterministic and verifiable.

---

## Step 4: Tour the Project Structure

When you initialize a Spec Kit project (next tutorial), you'll see this structure:

```
my-project/
├── ontology/              # RDF schemas (SOURCE OF TRUTH)
│   └── cli-commands.ttl   # Your CLI commands in RDF
│
├── memory/                # RDF specifications
│   └── documentation.ttl  # Your documentation specs
│
├── sparql/                # SPARQL query templates
│   └── command-extract.rq # Extract commands from RDF
│
├── templates/             # Tera code generation templates
│   └── command.tera       # Template to generate Python code
│
├── src/                   # Generated Python code
│   └── specify_cli/
│       ├── commands/      # CLI commands (GENERATED)
│       ├── ops/           # Business logic (you write)
│       └── runtime/       # I/O and subprocess (you write)
│
├── tests/                 # Tests (some generated)
│
├── docs/                  # Documentation (GENERATED)
│   └── ggen.toml          # ggen transformation config
│
├── CLAUDE.md              # Developer guide
└── README.md              # Project description
```

**Key insight:** Everything flows from the RDF specifications (ontology/ and memory/). Code and docs are generated from them.

---

## Step 5: Explore the Specification Philosophy

Spec Kit uses a **specification-driven development** approach. Instead of traditional development:

### Traditional Approach
```
Design → Code → Test → Document → Deploy
```

### Specification-Driven Approach
```
RDF Specification → Generate Code/Tests/Docs → Deploy
```

With Spec Kit:
- **RDF is your specification** - machine-readable and executable
- **Code is generated** - from your RDF specifications
- **Tests are generated** - validating your specifications
- **Docs are generated** - from the same RDF

This means:
- ✅ Your code always matches your documentation (no drift!)
- ✅ Tests validate your specifications
- ✅ Changes to specs automatically update everything
- ✅ Type-safe across multiple languages

---

## Step 6: Next Steps

Now that you understand the basics, you're ready to:

**Next Tutorial:** [Creating Your First Project](./02-first-project.md)
- Initialize a new Spec Kit project
- Explore the generated structure
- Understand how everything connects

---

## Troubleshooting

### `specify` command not found
- Ensure installation completed: `uv tool list | grep specify`
- If missing, reinstall: `uv tool install specify-cli --force --from git+https://github.com/seanchatmangpt/ggen-spec-kit.git`

### Python version too old
- Upgrade Python to 3.11+: https://www.python.org/downloads/
- Check version: `python --version`

### `ggen` not found
- Install ggen: https://github.com/seanchatmangpt/ggen
- Or use with your AI assistant (they have ggen available)

### Other tools missing
- Follow the prompts from `specify check` for each tool

---

## Summary

You've learned:
- ✅ How to install Specify CLI
- ✅ How to verify your installation
- ✅ The three core concepts (RDF-first, three-tier architecture, transformation pipeline)
- ✅ The philosophy behind specification-driven development

**Ready to create your first project?** → [Continue to Tutorial 2](./02-first-project.md)
