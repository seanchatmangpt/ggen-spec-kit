# Tutorial 3: Write Your First RDF Specification

**Time to complete:** 20-25 minutes
**Prerequisites:** Complete [Tutorial 2: Create Your First Project](./02-first-project.md)
**What you'll learn:** How to write RDF specifications in Turtle format

---

## Overview

In this tutorial, we'll write a simple RDF specification and understand how it becomes code and documentation. RDF specifications are the heart of Spec Kit - they're the source of truth for everything else.

---

## Step 1: Understand Turtle Syntax

RDF specifications are written in **Turtle** format (`.ttl` files). Turtle is a human-readable syntax for RDF.

Here's a minimal example:

```turtle
@prefix sk: <http://example.org/spec-kit#> .

sk:hello
    a sk:Command ;
    rdfs:label "hello" ;
    sk:description "Greet the world" .
```

Breaking this down:

```turtle
@prefix sk: <http://example.org/spec-kit#> .
│        │   └─ Namespace URL (where terms are defined)
│        └─ Shorthand prefix (like an alias)
└─ Namespace declaration

sk:hello
│   └─ Resource name (the thing we're describing)
└─ Namespace prefix

    a sk:Command ;
    └─ "a" means "is a type of"

    rdfs:label "hello" ;
    └─ Property: the label of this resource

    sk:description "Greet the world" .
    └─ Property: description (ends with period)
```

### Key Turtle Concepts

| Concept | Example | Meaning |
|---------|---------|---------|
| **Prefix** | `@prefix sk: <http://...#>` | Define a namespace abbreviation |
| **Subject** | `sk:hello` | The thing you're describing |
| **Property** | `rdfs:label` | Attribute of the subject |
| **Value** | `"hello"` | The value for that property |
| **Triple** | `sk:hello rdfs:label "hello" .` | Subject-Property-Value tuple |

---

## Step 2: Examine Your Project's Ontology

First, let's look at your project's existing ontology:

```bash
# Open your schema file
cat ontology/spec-kit-schema.ttl
```

This file defines the **schema** - what types and properties are available.

Then look at your CLI commands ontology:

```bash
cat ontology/cli-commands.ttl
```

This file defines **existing CLI commands** in RDF. It's a good template for adding your own.

---

## Step 3: Create Your First Specification

Let's add a simple command specification. Open your CLI commands file:

```bash
# Edit with your favorite editor (or use cat to view)
cat ontology/cli-commands.ttl
```

Look for the existing command definitions. They look like:

```turtle
sk:build
    a sk:Command ;
    rdfs:label "build" ;
    sk:description "Build the project" ;
    sk:hasModule "specify_cli.commands.build" .
```

Now add your own simple command at the end of the file. Create a new specification:

```turtle
sk:hello
    a sk:Command ;
    rdfs:label "hello" ;
    sk:description "Greet the user with a friendly message" ;
    sk:hasModule "specify_cli.commands.hello" .
```

This specification says:
- **Subject:** `sk:hello` - this is our command named "hello"
- **Type:** `sk:Command` - it's a CLI command
- **Label:** "hello" - the command name
- **Description:** What it does
- **Module:** Where the Python code will be generated

---

## Step 4: Validate Your RDF Syntax

Before transforming, let's validate the RDF is correct:

```bash
# Validate the Turtle file
rdf-validate ontology/cli-commands.ttl
```

Or if you don't have `rdf-validate`, you can check with `ggen`:

```bash
ggen validate ontology/cli-commands.ttl
```

If there are syntax errors, the tool will show them. Fix them and try again.

---

## Step 5: Transform Your RDF with ggen

Now that your RDF is valid, transform it into Python code, tests, and documentation:

```bash
ggen sync
```

This command:
1. Reads your RDF specifications
2. Validates them against SHACL shapes
3. Executes SPARQL queries to extract data
4. Renders Tera templates to generate code
5. Creates a SHA256 receipt for verification

You should see output like:

```
INFO: Starting ggen sync...
INFO: Processing: ontology/cli-commands.ttl
INFO: Validating against SHACL shapes...
INFO: Extracting data with SPARQL...
INFO: Rendering templates...
INFO: Generated files:
  ✓ src/specify_cli/commands/hello.py
  ✓ tests/e2e/test_commands_hello.py
  ✓ docs/commands/hello.md
  ✓ receipt.json (SHA256 verification)
INFO: Transformation complete!
```

---

## Step 6: Explore What Was Generated

After `ggen sync` completes, let's see what was created:

### Generated Python Code

```bash
cat src/specify_cli/commands/hello.py
```

You'll see a skeleton Python command:

```python
import typer
from specify_cli.core.cli import app

@app.command()
def hello():
    """Greet the user with a friendly message"""
    typer.echo("Hello, world!")
```

### Generated Tests

```bash
cat tests/e2e/test_commands_hello.py
```

You'll see a test:

```python
def test_hello_command():
    """Test the hello command"""
    # Test implementation
```

### Generated Documentation

```bash
cat docs/commands/hello.md
```

You'll see generated documentation:

```markdown
# hello

Greet the user with a friendly message
```

---

## Step 7: Implement the Business Logic

The generated code is a skeleton. Now you implement the actual logic:

Open `src/specify_cli/ops/hello.py` and add the real implementation:

```python
def hello_operation(name: str = "World") -> str:
    """
    Generate a greeting message.

    Parameters:
    -----------
    name : str
        The name to greet (default: "World")

    Returns:
    --------
    str
        A personalized greeting message
    """
    return f"Hello, {name}! Welcome to Spec Kit."
```

Then update the command to use it:

```python
import typer
from specify_cli.core.cli import app
from specify_cli.ops.hello import hello_operation

@app.command()
def hello(name: str = typer.Option("World", help="Name to greet")):
    """Greet the user with a friendly message"""
    message = hello_operation(name)
    typer.echo(message)
```

---

## Step 8: Test Your Implementation

Run your new command to verify it works:

```bash
# Test with default name
python -m specify_cli.cli hello

# Test with a custom name
python -m specify_cli.cli hello --name "Alice"
```

You should see:
```
Hello, World! Welcome to Spec Kit.
Hello, Alice! Welcome to Spec Kit.
```

---

## Step 9: Run the Test Suite

Now run the tests to ensure your code works:

```bash
# Run tests for your command
uv run pytest tests/e2e/test_commands_hello.py -v

# Or run all tests
uv run pytest tests/ -v
```

Update the test in `tests/e2e/test_commands_hello.py` to match your implementation:

```python
def test_hello_command(runner):
    """Test the hello command"""
    result = runner.invoke(cli, ["hello"])
    assert result.exit_code == 0
    assert "Hello, World" in result.output

def test_hello_with_name(runner):
    """Test the hello command with custom name"""
    result = runner.invoke(cli, ["hello", "--name", "Alice"])
    assert result.exit_code == 0
    assert "Hello, Alice" in result.output
```

---

## Step 10: Verify Everything Works Together

Let's verify that RDF → Code → Docs all work in harmony:

```bash
# 1. Edit RDF specification
# (You already did this in Step 3)

# 2. Transform with ggen
ggen sync

# 3. Implement business logic (you did this in Step 7)

# 4. Run tests
uv run pytest tests/ -v

# 5. Check documentation was generated
ls -la docs/commands/hello.md
cat docs/commands/hello.md
```

Notice how:
- Your RDF specification describes what the command does
- ggen generates skeleton Python code
- You implement the business logic
- Tests verify it works
- Documentation is automatically generated

---

## Step 11: The Constitutional Equation in Action

You just experienced the constitutional equation:

```
spec.md = μ(feature.ttl)
```

What happened:
1. **You wrote RDF** - `feature.ttl` (the spec)
2. **ggen transformed it** - μ transformation pipeline
3. **Output includes documentation** - `spec.md` (generated docs)
4. **Plus code and tests** - bonus artifacts

All from a single RDF source of truth!

---

## Next Steps

You've successfully:
- ✅ Written your first RDF specification
- ✅ Understood Turtle syntax
- ✅ Transformed RDF into Python code
- ✅ Implemented business logic
- ✅ Tested your implementation
- ✅ Seen documentation generated automatically

**Next tutorial:** [Tutorial 4: Your First Test](./04-first-test.md)

Or explore:
- **[How-to: Write Complete RDF Specifications](../guides/rdf/write-rdf-spec.md)** - More complex specs
- **[How-to: Add CLI Command](../guides/rdf/add-cli-command.md)** - Add features to your project
- **[Explanation: Constitutional Equation](../explanation/constitutional-equation.md)** - Deep dive into the theory

---

## Summary

The key insight: **RDF specifications are the source of truth**. Everything else (code, tests, docs) is generated from them. This means:

- ✅ Your specification and implementation never drift
- ✅ Documentation always stays current
- ✅ Tests validate your specifications
- ✅ Changes to specs automatically update everything

This is the power of specification-driven development!
