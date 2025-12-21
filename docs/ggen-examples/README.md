# ggen Examples - Constitutional Equation in Action

This directory contains complete examples of the five-stage transformation pipeline (μ₁-μ₅).

## Files

### Input Files (RDF Source of Truth)

- **feature.ttl** - RDF feature specification
  - Defines Feature001 with requirements
  - Uses spec-kit ontology vocabulary
  - Source of truth for specification

### Transformation Files

- **feature-query.rq** - SPARQL query for data extraction
  - Extracts features and requirements
  - Groups by priority and due date

- **feature.tera** - Tera template for markdown rendering
  - Renders feature specification
  - Includes constitutional equation notice

- **ggen.toml** - Configuration for ggen sync
  - Defines transformation pipeline
  - Configures all five stages (μ₁-μ₅)

### Output Files (Generated Artifacts)

- **FEATURE_SPEC.md** - Generated markdown (created by `specify sync`)
- **README.md.receipt.json** - Example receipt file with SHA256 hashes

## Running the Example

### Step 1: Validate RDF Input

```bash
# Validate RDF syntax and SHACL constraints
specify validate-rdf docs/ggen-examples/feature.ttl

# Expected output:
# ✓ docs/ggen-examples/feature.ttl
#   - 1 feature
#   - 5 requirements
#   - 0 SHACL violations
```

### Step 2: Run Full Pipeline

```bash
# Run μ₁-μ₅ transformation
ggen sync --from docs/ggen-examples --to docs/ggen-examples --config docs/ggen-examples/ggen.toml --verbose

# Or use specify wrapper:
specify sync --config docs/ggen-examples/ggen.toml --verbose
```

**Expected Output**:

```
🚀 ggen sync - Constitutional Equation Pipeline
   Config: docs/ggen-examples/ggen.toml
   Transformations: 1

[1/1] feature-spec ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%
  μ₁ Normalize ✓
     - Loaded 1 TTL file
     - Validated SHACL constraints
     - 1 feature, 5 requirements
  μ₂ Extract ✓
     - Executed SPARQL query
     - 1 feature extracted
  μ₃ Emit ✓
     - Rendered Tera template
     - Output: 2.3 KB
  μ₄ Canonicalize ✓
     - Normalized line endings (LF)
     - Trimmed trailing whitespace
     - Added final newline
  μ₅ Receipt ✓
     - Generated SHA256 hashes
     - Saved receipt: FEATURE_SPEC.md.receipt.json

✅ Sync complete! 1 transformation, 1 receipt generated
   Duration: 0.8s
   Constitutional equation verified: spec.md = μ(feature.ttl)
```

### Step 3: Verify Receipts

```bash
# Verify that FEATURE_SPEC.md was generated correctly
specify verify --receipt docs/ggen-examples/FEATURE_SPEC.md.receipt.json

# Expected output:
# ✓ FEATURE_SPEC.md
#   Receipt: FEATURE_SPEC.md.receipt.json
#   Input hash: a3f5b1c9e2d8... ✓
#   Output hash: c8b3f2e1a9d7... ✓
#
# Constitutional equation verified: spec.md = μ(feature.ttl)
```

### Step 4: Test Idempotence

```bash
# Run sync 10 times and verify identical output
for i in {1..10}; do
  specify sync --config docs/ggen-examples/ggen.toml
done

# Check hash is identical every time
sha256sum docs/ggen-examples/FEATURE_SPEC.md

# Expected: Same hash every run (idempotence: μ∘μ = μ)
```

### Step 5: Detect Manual Edits

```bash
# Manually edit generated file
echo "<!-- Manual edit -->" >> docs/ggen-examples/FEATURE_SPEC.md

# Verify again
specify verify --receipt docs/ggen-examples/FEATURE_SPEC.md.receipt.json

# Expected:
# ✗ FEATURE_SPEC.md
#   Receipt: FEATURE_SPEC.md.receipt.json
#   Input hash: a3f5b1c9e2d8... ✓
#   Output hash: c8b3f2e1a9d7... ✗ MISMATCH
#
#   Manual edits detected. Regenerate with:
#     specify sync --config docs/ggen-examples/ggen.toml
```

## Understanding the Pipeline

### μ₁ NORMALIZE: RDF Validation

**Input**: `feature.ttl`
**Process**: Load RDF, validate SHACL shapes
**Output**: In-memory RDF graph

```turtle
:Feature001 a :Feature ;
    :featureName "Constitutional Equation Implementation" ;
    :priority "P0" .
```

Validates:
- Turtle syntax correct
- Required properties present (featureName, priority)
- Value constraints satisfied (priority ∈ {P0, P1, P2})

### μ₂ EXTRACT: SPARQL Query

**Input**: RDF graph
**Process**: Execute `feature-query.rq`
**Output**: Structured data

```sparql
SELECT ?feature ?name ?description ?priority
WHERE {
  ?feature a :Feature ;
           :featureName ?name ;
           :priority ?priority .
}
```

Results:
```json
{
  "feature": "Feature001",
  "name": "Constitutional Equation Implementation",
  "priority": "P0"
}
```

### μ₃ EMIT: Template Rendering

**Input**: SPARQL results
**Process**: Render `feature.tera`
**Output**: Markdown

```jinja2
## {{ feature.name }}

**Priority**: {{ feature.priority }}
```

Renders to:
```markdown
## Constitutional Equation Implementation

**Priority**: P0
```

### μ₄ CANONICALIZE: Output Normalization

**Input**: Rendered markdown
**Process**: Normalize line endings, trim whitespace
**Output**: Canonical markdown

Before:
```
Line 1\r\n
Line 2   \r\n
```

After:
```
Line 1\n
Line 2\n
```

### μ₅ RECEIPT: Proof Generation

**Input**: All input files, canonical output
**Process**: Compute SHA256 hashes
**Output**: Receipt JSON

```json
{
  "inputs": {
    "rdf": { "feature.ttl": "a3f5b1c9..." },
    "sparql": { "feature-query.rq": "7d4e2f1a..." },
    "template": { "feature.tera": "9e1f3a5b..." }
  },
  "output": {
    "FEATURE_SPEC.md": "c8b3f2e1..."
  }
}
```

## Customizing the Example

### Add a New Requirement

Edit `feature.ttl`:

```turtle
:Req006 a :Requirement ;
    :requirementText "System MUST support incremental sync" ;
    :priority "P2" ;
    :category "performance" .

:Feature001 :hasRequirement :Req001, :Req002, :Req003, :Req004, :Req005, :Req006 .
```

Run sync:

```bash
specify sync --config docs/ggen-examples/ggen.toml
```

Verify output updated:

```bash
diff docs/ggen-examples/FEATURE_SPEC.md.old docs/ggen-examples/FEATURE_SPEC.md

# Expected: New requirement appears in generated markdown
```

### Change Priority

Edit `feature.ttl`:

```turtle
:Feature001 :priority "P1" .  # Changed from P0
```

Run sync:

```bash
specify sync --config docs/ggen-examples/ggen.toml
```

Verify hash changed:

```bash
sha256sum docs/ggen-examples/FEATURE_SPEC.md

# Expected: Different hash because input changed
```

### Customize Template

Edit `feature.tera`:

```jinja2
## {{ feature.name }} ({{ feature.status | upper }})
```

Run sync:

```bash
specify sync --config docs/ggen-examples/ggen.toml
```

Output changes:

```markdown
## Constitutional Equation Implementation (IN-PROGRESS)
```

## Testing the Example

Run the example test suite:

```bash
# Unit tests
uv run pytest tests/unit/test_ggen_example.py -v

# Integration tests
uv run pytest tests/integration/test_ggen_sync.py -v

# All tests
uv run pytest tests/ -v --cov=src/specify_cli
```

## Troubleshooting

### Error: SHACL Validation Failed

```
✗ feature.ttl
  - Missing required property :featureName
```

**Fix**: Add missing property to `feature.ttl`:

```turtle
:Feature001 :featureName "Your Feature Name" .
```

### Error: SPARQL Query Timeout

```
✗ feature-query.rq
  - Query exceeded 30s timeout
```

**Fix**: Simplify query or increase timeout in `ggen.toml`:

```toml
[pipeline.extract]
timeout_seconds = 60
```

### Error: Template Rendering Failed

```
✗ feature.tera
  - Variable 'feature.description' not found
```

**Fix**: Add variable to SPARQL query or make it optional in template:

```jinja2
{% if feature.description %}
{{ feature.description }}
{% endif %}
```

## Next Steps

1. **Read the roadmap**: See `/Users/sac/ggen-spec-kit/GGEN_INTEGRATION_ROADMAP.md`
2. **Explore templates**: Check `/Users/sac/ggen-spec-kit/templates/`
3. **Study ontology**: Review `/Users/sac/ggen-spec-kit/ontology/spec-kit-schema.ttl`
4. **Write specs**: Create your own RDF specifications
5. **Run sync**: Generate markdown with `specify sync`

## Constitutional Equation

Remember:

```
spec.md = μ(feature.ttl)
```

RDF is the source of truth. Markdown is the generated artifact.

**Never edit the generated markdown directly. Edit the RDF, run sync.**
