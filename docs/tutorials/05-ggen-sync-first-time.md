# Tutorial 5: Running ggen Sync for the First Time

**Time to complete:** 10-15 minutes
**Prerequisites:** Complete [Tutorial 3: Write Your First RDF Specification](./03-first-rdf-spec.md)
**What you'll learn:** How to use ggen to transform RDF specifications

---

## Overview

`ggen sync` is the command that transforms your RDF specifications into Python code, tests, and documentation. It's the engine that powers Spec Kit.

In this tutorial, we'll understand what `ggen sync` does and how to use it effectively.

---

## Step 1: Verify ggen is Installed

First, make sure you have ggen installed:

```bash
ggen --version
```

You should see:
```
ggen version 5.0.2
```

If ggen is not installed, follow the installation instructions at https://github.com/seanchatmangpt/ggen

---

## Step 2: Understand What ggen Does

`ggen sync` is the primary ggen command available in v5.0.2. It:

```
RDF Specifications → Validation → Extraction → Template Rendering → Output Files
```

In detail:

1. **μ₁ Normalize** - Validate RDF against SHACL shapes
2. **μ₂ Extract** - Execute SPARQL queries to extract data
3. **μ₃ Emit** - Render Tera templates with extracted data
4. **μ₄ Canonicalize** - Format and validate output
5. **μ₅ Receipt** - Create SHA256 hash for verification

---

## Step 3: Examine Your ggen Configuration

Your project has a ggen configuration file that tells it what to transform:

```bash
cat docs/ggen.toml
```

This file defines:
- What RDF files to process
- What SPARQL queries to run
- What templates to render
- Where to output generated files

Example configuration:

```toml
[transformation]
source = "ontology/cli-commands.ttl"
sparql = "sparql/command-extract.rq"
template = "templates/command.tera"
output = "src/specify_cli/commands/{name}.py"
```

This says:
- Read RDF from `ontology/cli-commands.ttl`
- Extract data with `sparql/command-extract.rq`
- Generate code using `templates/command.tera`
- Save to `src/specify_cli/commands/{name}.py`

---

## Step 4: Run ggen sync

From your project directory, run:

```bash
ggen sync
```

You'll see output like:

```
ggen v5.0.2 - RDF Transformation Pipeline
================================================

Loading configuration from: docs/ggen.toml
Processing: ontology/cli-commands.ttl

Stage 1: Normalize
  ✓ Validating SHACL shapes
  ✓ Valid RDF document

Stage 2: Extract
  ✓ Executing SPARQL query: sparql/command-extract.rq
  ✓ Extracted 12 commands

Stage 3: Emit
  ✓ Rendering templates
  ✓ Generated 12 command files
  ✓ Generated 12 test files

Stage 4: Canonicalize
  ✓ Formatting output
  ✓ All files valid

Stage 5: Receipt
  ✓ Computing SHA256 receipt
  ✓ Receipt saved: .ggen-receipt.json

================================================
Transformation complete! Generated 24 files.
```

---

## Step 5: Understand the Output

After `ggen sync` completes, check what was generated:

### Generated Files

```bash
# See all generated Python command files
ls -la src/specify_cli/commands/

# See all generated tests
ls -la tests/e2e/

# See generated documentation
ls -la docs/commands/
```

Each command you defined in your RDF has:
- `src/specify_cli/commands/{command}.py` - The CLI command
- `tests/e2e/test_commands_{command}.py` - The test file
- `docs/commands/{command}.md` - The documentation

---

## Step 6: Check the Receipt

ggen creates a receipt file that proves the transformation:

```bash
cat .ggen-receipt.json
```

This file contains:
- SHA256 hash of inputs
- Timestamp of transformation
- List of generated files
- Version information

The receipt allows you to verify:
- ✅ No files were manually modified
- ✅ Transformation is reproducible
- ✅ Generated code matches specifications

---

## Step 7: Run Tests After Transformation

After ggen generates code, run tests to ensure everything works:

```bash
# Run all tests
uv run pytest tests/ -v

# Or just the generated tests
uv run pytest tests/e2e/ -v
```

This verifies:
- ✅ Generated code is syntactically valid
- ✅ Generated tests pass
- ✅ Your RDF specifications are correctly transformed

---

## Step 8: Implement Generated Skeletons

After `ggen sync` generates Python code, you need to implement the business logic:

For example, if you have a generated command `commands/build.py`:

```python
# Generated skeleton
@app.command()
def build():
    """Build the project"""
    pass  # TODO: Implement
```

You implement it by:

1. Adding a function to `ops/build.py`
2. Updating the command to call it

```python
# ops/build.py
def build_operation() -> str:
    """Execute the build process."""
    # Your implementation here
    return "Build successful!"

# commands/build.py
@app.command()
def build():
    """Build the project"""
    result = build_operation()
    typer.echo(result)
```

---

## Step 9: Workflow: Edit RDF → ggen sync → Implement

The typical workflow is:

```
1. Edit RDF spec (ontology/ or memory/)
   ↓
2. Run: ggen sync
   ↓
3. View generated code
   ↓
4. Implement business logic (ops/ and runtime/)
   ↓
5. Run tests to verify
   ↓
6. Commit changes
   ↓
7. Repeat for next feature
```

This cycle repeats throughout development.

---

## Step 10: Handle Transformation Errors

If ggen sync fails, check:

### RDF Syntax Errors

```
Error: Invalid Turtle syntax in ontology/cli-commands.ttl
  Line 15: Unexpected character '€'
```

Fix: Correct the Turtle syntax in your `.ttl` file.

### SHACL Validation Errors

```
Error: SHACL validation failed
  Shape sk:CommandShape violation
  Message: Missing required property sk:hasModule
```

Fix: Add the missing property to your RDF spec.

### Template Errors

```
Error: Template rendering failed in command.tera
  Undefined variable: {description}
```

Fix: Check your Tera template syntax and SPARQL query extraction.

---

## Step 11: Verify Reproducibility

One of ggen's key features is reproducibility. Run ggen sync twice and verify it produces identical output:

```bash
# First run
ggen sync

# Save the receipt
cp .ggen-receipt.json .ggen-receipt-1.json

# Make a minor change to RDF and revert
# Then run again
ggen sync

# Compare receipts
diff .ggen-receipt-1.json .ggen-receipt.json
```

If the files are identical (or near-identical, ignoring timestamps), the transformation is reproducible.

---

## Step 12: Advanced: Custom Transformations

You can customize ggen behavior by:

1. **Creating custom SPARQL queries** in `sparql/`
2. **Creating custom Tera templates** in `templates/`
3. **Updating RDF specifications** in `ontology/`

For example, to generate a new type of file:

1. Write SPARQL query to extract data
2. Write Tera template to render it
3. Update `docs/ggen.toml` to define the transformation
4. Run `ggen sync`

---

## Next Steps

You now understand:
- ✅ What ggen sync does
- ✅ How to run it
- ✅ What it generates
- ✅ How to verify the output

**Next tutorial:** [Tutorial 6: Exploring JTBD Framework](./06-exploring-jtbd.md)

Or explore:
- **[How-to: Run ggen Sync](../guides/operations/run-ggen-sync.md)** - Advanced usage
- **[How-to: Troubleshoot ggen](../guides/operations/troubleshoot-ggen.md)** - Common issues
- **[Explanation: ggen Transformation Pipeline](../explanation/ggen-pipeline.md)** - Deep dive

---

## Quick Reference

```bash
# Run ggen sync (ONLY command available in v5.0.2)
ggen sync

# Check ggen version
ggen --version

# Show ggen help
ggen --help

# View ggen configuration
cat docs/ggen.toml

# Check the receipt
cat .ggen-receipt.json

# Compare old and new receipts
diff .ggen-receipt-old.json .ggen-receipt.json
```

---

## Summary

`ggen sync` is the bridge between your RDF specifications and generated code. It:
- Validates RDF syntax
- Extracts data with SPARQL
- Renders templates
- Generates code, tests, and docs
- Creates cryptographic receipts for verification

This cycle of "Edit RDF → ggen sync → Implement → Test" is the heart of specification-driven development!
