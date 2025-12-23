# Explanation: The Constitutional Equation

**Time to understand:** 10-15 minutes

---

## The Core Principle

```
spec.md = μ(feature.ttl)
```

Read this as: **"Markdown documentation is generated from RDF specifications."**

This is the constitutional equation of Spec Kit.

---

## What It Means

### 1. RDF is the Source of Truth

You don't write documentation directly. You write **RDF specifications** and documentation is generated from them.

```
Traditional:
  Write code → Write docs (separately) → Hope they stay in sync ❌

Spec-Kit:
  Write RDF → Generate code + docs (together) → Perfect sync ✓
```

### 2. μ is a Transformation Function

The `μ` (mu) symbol represents the **five-stage transformation pipeline**:

```
feature.ttl → μ₁ → μ₂ → μ₃ → μ₄ → μ₅ → spec.md
                │   │   │   │   │
                │   │   │   │   └─ μ₅ Receipt (SHA256 proof)
                │   │   │   └─ μ₄ Canonicalize (format)
                │   │   └─ μ₃ Emit (Tera templates)
                │   └─ μ₂ Extract (SPARQL queries)
                └─ μ₁ Normalize (SHACL validation)
```

**Each stage is pure and deterministic:**
- Same input → Always same output
- Running μ twice = same result
- Transformation is verifiable
- Results have cryptographic proofs (SHA256)

### 3. Generated Code Matches Specification

Because the equation holds:
- ✅ Code exactly matches documentation
- ✅ Tests validate specifications
- ✅ Changes to specs update everything
- ✅ No drift between spec and code

---

## The Five Stages

### Stage 1: Normalize (μ₁)

**Input:** RDF file
**Output:** Validated RDF
**Process:** Check against SHACL shapes

```
Your RDF:
sk:hello a sk:Command ;
    rdfs:label "hello" ;
    sk:description "Greet user" .

SHACL Validation:
✓ Has required properties
✓ No type violations
✓ All constraints satisfied
```

If validation fails → Stop (don't generate bad code)

### Stage 2: Extract (μ₂)

**Input:** Valid RDF
**Output:** JSON data
**Process:** Run SPARQL queries

```
SPARQL Query:
SELECT ?label ?description WHERE {
    ?command a sk:Command ;
             rdfs:label ?label ;
             sk:description ?description .
}

Result (JSON):
{
  "commands": [
    {"label": "hello", "description": "Greet user"}
  ]
}
```

### Stage 3: Emit (μ₃)

**Input:** Extracted JSON
**Output:** Generated files
**Process:** Render Tera templates

```
Template (command.tera):
@app.command()
def {{ label }}():
    """{{ description }}"""
    pass

Output:
@app.command()
def hello():
    """Greet user"""
    pass
```

### Stage 4: Canonicalize (μ₄)

**Input:** Generated files
**Output:** Formatted files
**Process:** Apply style rules

```
Before canonicalization:
def hello():"""Greet user"""
pass

After canonicalization:
def hello():
    """Greet user"""
    pass
```

### Stage 5: Receipt (μ₅)

**Input:** All files
**Output:** SHA256 proof
**Process:** Hash everything

```
receipt.json:
{
  "spec_hash": "abc123...",
  "code_hash": "def456...",
  "docs_hash": "ghi789...",
  "timestamp": "2024-01-15T10:30:45Z",
  "version": "5.0.2"
}
```

This proves the transformation is legitimate and verifiable.

---

## Why This Matters

### Traditional Development

```
Specification → Code
                 ↓
            Documentation

Problem: When spec changes, code AND docs both need updating.
Result: Drift happens. Spec ≠ Code ≠ Docs ❌
```

### Spec-Kit (Constitutional Equation)

```
RDF Specification
    ↓ (μ transformation)
Code + Documentation

Guarantee: Code always matches Documentation ✓
Proof: SHA256 receipt
```

---

## Examples

### Example 1: Add a CLI Command

```
BEFORE: specification.ttl
sk:hello a sk:Command ;
    rdfs:label "hello" ;
    sk:description "Greet user" .

RUN: ggen sync
    (executes μ transformation)

AFTER: Generated files
- src/specify_cli/commands/hello.py
- tests/e2e/test_commands_hello.py
- docs/commands/hello.md

PROOF: receipt.json (SHA256 hash)

GUARANTEE: spec.md (hello.md) exactly matches specification
```

### Example 2: Update Documentation

```
If you edit hello.md manually:
hello.md ≠ specification.ttl
Receipt verification FAILS ❌

Correct approach:
1. Edit specification.ttl (source of truth)
2. Run ggen sync
3. hello.md regenerates (always matches spec)
Receipt verification PASSES ✓
```

---

## Key Consequences

### 1. Never Edit Generated Files

Generated files are build artifacts:
- ❌ Never edit `src/specify_cli/commands/hello.py` (auto-generated)
- ❌ Never edit `docs/commands/hello.md` (auto-generated)
- ✅ Always edit `ontology/cli-commands.ttl` (source)

### 2. Specifications Are Executable

RDF specs directly generate code:
- No manual implementation needed (skeleton is auto-generated)
- Tests are auto-generated
- Documentation is auto-generated

### 3. Perfect Documentation Sync

Because docs are generated from specs:
- Documentation always current
- No drift possible
- Changes propagate everywhere

### 4. Verifiable Transformation

Receipt files prove:
- Transformation happened
- No manual file edits
- Complete history of changes

---

## The Math

The equation `spec.md = μ(feature.ttl)` guarantees:

1. **Determinism:** `μ(x) = μ(x)` (always same output)
2. **Totality:** `μ` produces valid output or fails
3. **Idempotency:** `μ(μ(x)) = μ(x)` (running twice = once)
4. **Verifiability:** `sha256(spec.md) = sha256(μ(feature.ttl))`

This makes the system:
- ✅ Predictable
- ✅ Reproducible
- ✅ Verifiable
- ✅ Debuggable

---

## How It Scales

### Single Feature
```
feature.ttl → μ → feature.md + code + tests + docs
```

### Multiple Features
```
features.ttl (n features)
    → μ
→ n code files + n test files + n doc files + proof
```

### Entire System
```
ontology/*.ttl (schemas)
memory/*.ttl (specifications)
    → μ
→ Complete system (code + tests + docs)
```

---

## Verification

You can verify the equation holds:

```bash
# 1. Check proof file exists
cat .ggen-receipt.json

# 2. Check hashes match
ggen verify --receipts .ggen-receipt.json

# 3. Check files weren't edited
if hash(feature.ttl) == receipt["spec_hash"]:
    print("✓ Specification unchanged")
if hash(hello.md) == receipt["docs_hash"]:
    print("✓ Documentation matches spec")
```

---

## The Implication

When the constitutional equation holds:

> **You can never have mismatched spec and code**

Because:
1. Code is generated from spec
2. Docs are generated from spec
3. Tests are generated from spec
4. Everything comes from the same source

Changes to spec → Everything updates together

This is the power of specification-driven development.

---

## See Also

- [Explanation: RDF-First Development](./rdf-first-development.md)
- [Explanation: Three-Tier Architecture](./three-tier-architecture.md)
- [Explanation: ggen Pipeline](./ggen-pipeline.md)
- [Tutorial 3: Write Your First RDF Spec](../tutorials/03-first-rdf-spec.md)
- [Tutorial 5: Running ggen Sync](../tutorials/05-ggen-sync-first-time.md)
