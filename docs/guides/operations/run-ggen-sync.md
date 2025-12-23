# How-to: Run ggen Sync

**Goal:** Transform RDF specifications into code and documentation
**Time:** 10-15 minutes | **Level:** Intermediate

---

## Overview

```
RDF Specs → ggen sync → Python Code + Tests + Docs
```

**The ggen transformation pipeline (μ):**
1. **Normalize** - Validate RDF against SHACL shapes
2. **Extract** - Execute SPARQL queries
3. **Emit** - Render Tera templates
4. **Canonicalize** - Format output
5. **Receipt** - Create SHA256 hash proof

---

## Quick Start

```bash
# Run the transformation
ggen sync

# That's it! Check what was generated:
ls -la src/specify_cli/commands/
ls -la docs/commands/
ls -la tests/e2e/test_commands_*.py
```

---

## What ggen sync Does

### Input
- `ontology/*.ttl` - RDF schemas
- `memory/*.ttl` - RDF specifications
- `docs/ggen.toml` - transformation config

### Process
1. **Loads RDF** from `docs/ggen.toml` configuration
2. **Validates** against SHACL shapes
3. **Extracts data** using SPARQL queries
4. **Renders templates** with Tera
5. **Generates files** (Python, tests, docs)
6. **Creates receipt** for verification

### Output
- ✓ `src/specify_cli/commands/*.py` (generated)
- ✓ `tests/e2e/test_commands_*.py` (generated)
- ✓ `docs/commands/*.md` (generated)
- ✓ `.ggen-receipt.json` (proof file)

---

## Running ggen sync

### Basic Usage
```bash
ggen sync
```

Expected output:
```
ggen v5.0.2 - RDF Transformation Pipeline
================================================

Loading configuration from: docs/ggen.toml
Processing: ontology/cli-commands.ttl

Stage 1: Normalize
  ✓ Validating SHACL shapes
  ✓ Valid RDF document

Stage 2: Extract
  ✓ Executing SPARQL query
  ✓ Extracted 12 commands

Stage 3: Emit
  ✓ Rendering templates
  ✓ Generated 12 command files

Stage 4: Canonicalize
  ✓ Formatting output
  ✓ All files valid

Stage 5: Receipt
  ✓ Computing SHA256 receipt

================================================
Transformation complete! Generated 24 files.
```

### With Verbose Output
```bash
ggen sync --verbose
# Shows more details about each stage
```

### Check Configuration
```bash
cat docs/ggen.toml
```

Typical content:
```toml
[transformation]
source = "ontology/cli-commands.ttl"
sparql = "sparql/command-extract.rq"
template = "templates/command.tera"
output = "src/specify_cli/commands/{name}.py"
```

---

## The Workflow

```
1. You edit RDF spec
   │
   ├─ ontology/cli-commands.ttl
   │  sk:hello a sk:Command ;
   │      rdfs:label "hello" ;
   │      sk:description "Greet user" .
   │
2. Run: ggen sync
   │
   ├─ SPARQL extracts: name="hello", description="Greet user"
   ├─ Tera template renders Python code
   │
3. Generated files created
   │
   ├─ src/specify_cli/commands/hello.py
   ├─ tests/e2e/test_commands_hello.py
   ├─ docs/commands/hello.md
   │
4. You implement ops layer
   │
   ├─ src/specify_cli/ops/hello.py
   │  def hello_operation() -> str: ...
   │
5. Update generated command to use ops
   │
   ├─ src/specify_cli/commands/hello.py
   │  def hello(): hello_operation()
   │
6. Run tests to verify
   │
   ├─ uv run pytest tests/ -v
```

---

## Verification

### Check What Was Generated
```bash
# List all generated commands
ls -la src/specify_cli/commands/

# View generated documentation
cat docs/commands/hello.md

# View generated test
cat tests/e2e/test_commands_hello.py
```

### Verify Receipt (Proof)
```bash
# View the transformation receipt
cat .ggen-receipt.json

# Contents include:
# - SHA256 hash of inputs
# - List of generated files
# - Timestamp
# - Version information
```

### Confirm Idempotency
```bash
# Run twice - output should be identical
ggen sync
cp .ggen-receipt.json receipt-1.json

ggen sync
cp .ggen-receipt.json receipt-2.json

# Compare receipts
diff receipt-1.json receipt-2.json
# Should show no differences (except maybe timestamp)
```

---

## After ggen sync

### Step 1: Review Generated Code
```bash
# Look at generated skeleton
cat src/specify_cli/commands/hello.py

# Should be empty placeholder:
# def hello(): pass  # TODO: Implement
```

### Step 2: Implement Ops Layer
```bash
# Create business logic file
cat > src/specify_cli/ops/hello.py << 'EOF'
def hello_operation() -> str:
    return "Hello, World!"
EOF
```

### Step 3: Update Command
```python
# Edit src/specify_cli/commands/hello.py
from specify_cli.ops.hello import hello_operation

@app.command()
def hello():
    """Greet the user."""
    result = hello_operation()
    typer.echo(result)
```

### Step 4: Run Tests
```bash
uv run pytest tests/e2e/test_commands_hello.py -v
```

---

## Troubleshooting

### ggen: command not found
```bash
# Install ggen
uv tool install ggen

# Or if in a project with ggen dependency
uv sync
```

### RDF syntax error
```
Error: Invalid Turtle syntax
  Line 15: Unexpected character
```

Fix:
- Check for missing `;` before properties
- Check for missing `.` at end of definition
- Validate: `ggen validate ontology/cli-commands.ttl`

### SHACL validation error
```
Error: SHACL validation failed
  Missing required property: sk:hasModule
```

Fix:
- Add missing properties to RDF spec
- Check SHACL shape definition in schema
- Ensure all required properties are present

### Template rendering error
```
Error: Template error in command.tera
  Undefined variable: {description}
```

Fix:
- Check SPARQL query is extracting the variable
- Verify template syntax
- Ensure data exists in RDF

### Generated code won't import
```
ImportError: No module named 'specify_cli.ops.hello'
```

Fix:
- Create the ops module: `src/specify_cli/ops/hello.py`
- Ensure __init__.py files exist
- Run: `uv sync`

---

## Configuration

**File:** `docs/ggen.toml`

```toml
[transformation]
# Which RDF file to process
source = "ontology/cli-commands.ttl"

# SPARQL query to extract data
sparql = "sparql/command-extract.rq"

# Tera template to generate code
template = "templates/command.tera"

# Where to save generated files
output = "src/specify_cli/commands/{name}.py"

[validation]
# SHACL shapes for validation
shapes = "ontology/spec-kit-schema.ttl"

[receipt]
# Generate proof file
enabled = true
format = "json"
algorithm = "sha256"
```

---

## Advanced: Custom Transformations

### Add New Output Type

1. **Create SPARQL query** to extract data
2. **Create Tera template** to generate output
3. **Update ggen.toml** with new transformation

Example: Generate documentation from RDF

```toml
[[transformation]]
source = "memory/documentation.ttl"
sparql = "sparql/docs-extract.rq"
template = "templates/docs.tera"
output = "docs/generated/{title}.md"
```

---

## Best Practices

✅ **Do:**
- Run `ggen sync` after editing RDF specs
- Check generated files before implementing
- Verify tests pass after implementing
- Keep receipt files for verification
- Track generated files in git

❌ **Don't:**
- Edit generated files (they'll be overwritten)
- Run ggen sync in production
- Ignore SHACL validation errors
- Delete receipt files

---

## See Also

- [Tutorial 5: Running ggen Sync](../../tutorials/05-ggen-sync-first-time.md)
- [Explanation: Constitutional Equation](../../explanation/constitutional-equation.md)
- [Explanation: ggen Pipeline](../../explanation/ggen-pipeline.md)
- [Reference: ggen Configuration](../../reference/ggen-config.md)
