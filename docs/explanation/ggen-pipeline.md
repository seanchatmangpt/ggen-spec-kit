# The ggen Transformation Pipeline

The **μ (mu) transformation pipeline** is the heart of ggen spec-kit. It converts RDF specifications into code, documentation, and tests through a mathematically-proven five-stage process.

## The Constitutional Equation

```
spec.md = μ(feature.ttl)
```

This equation means: **Markdown specification is the deterministic output of transforming an RDF specification through the μ function.**

This is not metaphorical - it's mathematical. The transformation is:
- **Deterministic**: Same input always produces same output
- **Idempotent**: μ(μ(x)) = μ(x) - applying twice gives same result as once
- **Verifiable**: SHA256 receipt proves the transformation
- **Reversible analysis**: You can trace any line of output back to its source in the RDF

## The Five-Stage Pipeline (μ₁ → μ₂ → μ₃ → μ₄ → μ₅)

### Stage 1: μ₁ Normalize (SHACL Validation)

**Input:** Raw RDF/Turtle specification
**Output:** Validated, normalized RDF

**What happens:**
1. Parse Turtle syntax into RDF graph
2. Apply SHACL shape constraints from ontology/
3. Validate that all required properties exist
4. Validate that property values match required types
5. Normalize formatting (consistent spacing, ordering)

**Why this matters:**
- Catches malformed specifications early
- Ensures specification conforms to ontology
- Prevents downstream transformation errors
- Guarantees data quality

**Example:**
```turtle
# ❌ FAILS at μ₁ - missing required property
my:command a sk:Command ;
    rdfs:label "mycommand" .
    # Error: missing sk:description

# ✅ PASSES at μ₁ - all required properties
my:command a sk:Command ;
    rdfs:label "mycommand" ;
    sk:description "Does something useful" ;
    sk:hasArgument [...] .
```

---

### Stage 2: μ₂ Extract (SPARQL Queries)

**Input:** Validated RDF graph
**Output:** Extracted data as JSON/structured objects

**What happens:**
1. Execute SPARQL queries from sparql/ folder
2. Query patterns: `command-extract.rq`, `docs-extract.rq`, etc.
3. Extract specific data structures (commands, docs, tests)
4. Convert RDF triples to JSON for templating

**Why this matters:**
- Separates RDF structure from output format
- Enables querying specific subsets
- Filters data for each output file
- Supports incremental generation

**Example SPARQL query:**
```sparql
# Extract all CLI commands with their arguments
PREFIX sk: <http://spec-kit.org/ontology#>
SELECT ?name ?label ?description
WHERE {
  ?cmd a sk:Command ;
    rdfs:label ?name ;
    rdfs:label ?label ;
    sk:description ?description .
}
ORDER BY ?name
```

**Output after μ₂:**
```json
{
  "commands": [
    {
      "name": "check",
      "label": "check",
      "description": "Check tool availability"
    },
    {
      "name": "init",
      "label": "init",
      "description": "Initialize new project"
    }
  ]
}
```

---

### Stage 3: μ₃ Emit (Tera Templating)

**Input:** Extracted JSON data
**Output:** Generated source code and documentation

**What happens:**
1. Load Tera templates from templates/ folder
2. Pass extracted data to templates as context
3. Render templates with conditions, loops, filters
4. Generate Python code, markdown docs, tests

**Why this matters:**
- Separates data from presentation
- Enables multiple output formats from same data
- Supports complex logic (conditionals, loops, formatting)
- Keeps generated code maintainable

**Example template (command.tera):**
```jinja2
def {{ cmd.name }}({{ cmd.args | join(", ") }}) -> None:
    """{{ cmd.description }}"""

    {% for arg in cmd.arguments %}
    # Validate {{ arg.name }}
    if not {{ arg.validate }}:
        raise ValueError("{{ arg.name }} is invalid")
    {% endfor %}

    # Delegate to ops layer
    return ops.{{ cmd.name }}_impl({{ cmd.args | join(", ") }})
```

**Output after μ₃:**
```python
def check() -> None:
    """Check tool availability"""

    # Delegate to ops layer
    return ops.check_impl()

def init(project_name: str) -> None:
    """Initialize new project"""

    # Validate project_name
    if not validate_project_name(project_name):
        raise ValueError("project_name is invalid")

    # Delegate to ops layer
    return ops.init_impl(project_name)
```

---

### Stage 4: μ₄ Canonicalize (Format & Normalize)

**Input:** Generated output from μ₃
**Output:** Formatted, normalized files

**What happens:**
1. Format code (run formatters: black, prettier)
2. Normalize markdown (consistent headings, links)
3. Sort imports and sections
4. Fix line endings and whitespace
5. Validate syntax (Python AST, YAML, JSON)

**Why this matters:**
- Ensures consistent code style
- Prevents formatting churn in git
- Catches syntax errors early
- Produces publication-ready output

**Example transformations:**
```python
# Before μ₄ (from template)
def check( ):  # Extra spaces
    """Check tool availability"""
    x=1  # Inconsistent spacing
    pass

# After μ₄ (canonicalized)
def check() -> None:
    """Check tool availability"""
    x = 1
    pass
```

---

### Stage 5: μ₅ Receipt (Verification Proof)

**Input:** All generated files
**Output:** SHA256 receipt file

**What happens:**
1. Compute SHA256 hash of all generated files
2. Create receipt.json with:
   - Timestamp of generation
   - ggen version used
   - RDF source file hash
   - Generated file hashes
   - Transformation metadata
3. Store receipt in .ggen/receipt.json

**Why this matters:**
- Proves which RDF specification produced which output
- Detects manual edits to generated files
- Enables verification of spec-code synchronization
- Supports reproducible builds

**Example receipt.json:**
```json
{
  "ggen_version": "5.0.2",
  "timestamp": "2025-12-23T14:30:00Z",
  "rdf_source": {
    "file": "ontology/cli-commands.ttl",
    "hash": "abc123def456..."
  },
  "generated_files": {
    "src/specify_cli/commands/check.py": "sha256:xyz789...",
    "src/specify_cli/commands/init.py": "sha256:uvw456...",
    "tests/e2e/test_commands.py": "sha256:rst123..."
  },
  "verification": {
    "idempotent": true,
    "all_files_match": true
  }
}
```

---

## Complete Pipeline Visualization

```
Turtle File (.ttl)
    ↓
[μ₁ Normalize - SHACL Validation]
    ↓
Validated RDF Graph
    ↓
[μ₂ Extract - SPARQL Queries]
    ↓
Extracted JSON Data
    ↓
[μ₃ Emit - Tera Templates]
    ↓
Generated Source Code & Docs
    ↓
[μ₄ Canonicalize - Format & Normalize]
    ↓
Final Formatted Output
    ↓
[μ₅ Receipt - SHA256 Verification]
    ↓
Generated Files + Receipt Proof
```

---

## Why Five Stages?

Each stage has a specific purpose that can't be combined:

| Stage | Purpose | Why Separate |
|-------|---------|--------------|
| μ₁ | Validate specification quality | Catch errors early, before expensive computation |
| μ₂ | Extract relevant data | Separate data from templates, enable querying |
| μ₃ | Transform to output format | Support multiple formats, complex logic |
| μ₄ | Normalize and canonicalize | Ensure consistent output, catch syntax errors |
| μ₅ | Verify and prove | Detect changes, verify reproducibility |

**Together they ensure:**
- ✅ Specifications are always valid
- ✅ Data is cleanly extracted
- ✅ Output is consistently formatted
- ✅ Transformations are verifiable
- ✅ Changes can be detected

---

## Idempotence Guarantee

The pipeline is **idempotent**: running it twice on the same input produces identical output.

```
ggen sync  # First run
# ✓ Generated 15 files

ggen sync  # Second run
# ✓ All files match (no changes)
```

This is mathematically guaranteed because:
1. SHACL validation is deterministic
2. SPARQL queries return same results
3. Tera templates produce same output
4. Formatting is deterministic
5. SHA256 is deterministic

You can run `ggen sync` as many times as you want - it never creates duplicate or conflicting output.

---

## Verification & Reproducibility

After each run, check the receipt:

```bash
cat .ggen/receipt.json | jq
```

This tells you:
- What ggen version created the output
- When it was created
- What RDF source was used
- Hash of every generated file

To verify current state matches specification:
```bash
specify ggen verify
# Compares current files against receipt hashes
```

---

## Integration with Development Workflow

```
1. Edit ontology/cli-commands.ttl (RDF source)
   ↓
2. ggen sync (run transformation pipeline)
   ↓
3. uv run pytest tests/ (test generated code)
   ↓
4. git add . && git commit
   ↓
5. Commit includes both RDF source AND generated files
```

**Key principle:** Never edit generated files directly. Always edit the RDF source, run `ggen sync`, then test.

---

## Common Transformations

### RDF → Python Code
```turtle
# Source
my:validate_email a sk:Function ;
    rdfs:label "validate_email" ;
    sk:input [ sk:name "email" ; sk:type "str" ] ;
    sk:output [ sk:type "bool" ] .
```

```python
# Output (generated by μ₃ + μ₄)
def validate_email(email: str) -> bool:
    """Validate email format"""
    return "@" in email and "." in email
```

### RDF → Documentation
```turtle
my:tutorial1 a doc:Tutorial ;
    rdfs:label "Getting Started" ;
    doc:title "Getting Started with ggen Spec Kit" ;
    doc:content "Learn the basics..." ;
    doc:duration "PT10M"^^xsd:duration .
```

```markdown
# Getting Started with ggen Spec Kit

*Duration: 10 minutes*

Learn the basics...
```

### RDF → Tests
```turtle
my:test_validate_email a sk:TestCase ;
    sk:function my:validate_email ;
    sk:input [ sk:value "user@example.com" ] ;
    sk:expected [ sk:result true ] .
```

```python
def test_validate_email():
    assert validate_email("user@example.com") is True
```

---

## See Also

- `constitutional-equation.md` - Why this approach matters
- `rdf-first-development.md` - Why RDF is the source of truth
- `/docs/guides/operations/run-ggen-sync.md` - How to run ggen sync
- `/docs/reference/ggen-config.md` - ggen configuration options
- `GAP_ANALYSIS.md` - Documentation gaps and roadmap
