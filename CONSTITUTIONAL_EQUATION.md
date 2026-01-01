# The Constitutional Equation: spec.md = μ(feature.ttl)

The Spec-Kit system is built on a single principle: **RDF is the source of truth**.

## The Equation

```
specification.md = μ(feature.ttl)
implementation.py = μ(feature.ttl)
tests.py = μ(feature.ttl)
```

Where `μ` is the transformation pipeline: Normalize → Extract → Emit → Canonicalize → Receipt

## Why This Matters

Normally, when you write code, you have:
- The spec (maybe a document, maybe not)
- The code (the actual implementation)
- Tests (maybe)

These drift apart. Over time, the spec becomes lies, the code becomes the truth, and you lose track of *why* things work the way they do.

The constitutional equation fixes this by making the RDF specification the source of truth and **generating everything else from it**:

- Python code is generated from RDF
- Tests are generated from RDF
- Documentation is generated from RDF
- CLI commands are generated from RDF

This is not theoretical. It's enforced by the `ggen sync` transformation pipeline.

## The Three Layers

```
┌─────────────────────────────────────────┐
│  Commands Layer (typer CLI)             │
│  Generated from: ontology/cli-*.ttl     │
└─────────────────────────────────────────┘
           ↓ delegates to
┌─────────────────────────────────────────┐
│  Operations Layer (pure business logic) │
│  Generated from: memory/*.ttl            │
└─────────────────────────────────────────┘
           ↓ delegates to
┌─────────────────────────────────────────┐
│  Runtime Layer (I/O, subprocesses)      │
│  Generated from: ontology/runtime-*.ttl │
└─────────────────────────────────────────┘
```

Each layer is **generated from RDF**. The generation is **deterministic and reproducible**.

## RDF as Source of Truth

All system knowledge lives in RDF:

```
ontology/
├── spec-kit-schema.ttl          # Core vocabulary
├── spec-kit-docs-extension.ttl  # Documentation extension
├── cli-commands.ttl             # CLI command specifications → generates src/specify_cli/commands/*.py
└── runtime-clustering.ttl       # Runtime module specifications → generates src/specify_cli/runtime/*.py

memory/
├── philosophy.ttl               # Philosophy → generates CONTRIBUTING.md
├── changelog.ttl                # Changelog → generates CHANGELOG.md
└── documentation.ttl            # Documentation → generates README.md
```

## The Transformation Pipeline

```
                feature.ttl
                    ↓
        ┌───────────────────────┐
        │ μ₁: NORMALIZE (SHACL) │  Validate RDF with SHACL shapes
        └───────────────────────┘
                    ↓
        ┌───────────────────────┐
        │ μ₂: EXTRACT (SPARQL)  │  Run SPARQL queries to extract data
        └───────────────────────┘
                    ↓
        ┌───────────────────────┐
        │ μ₃: EMIT (Tera)       │  Render Tera templates with results
        └───────────────────────┘
                    ↓
        ┌───────────────────────┐
        │ μ₄: CANONICALIZE      │  Format output (line endings, whitespace)
        └───────────────────────┘
                    ↓
        ┌───────────────────────┐
        │ μ₅: RECEIPT (SHA256)  │  Generate hash proof: spec.md = μ(feature.ttl)
        └───────────────────────┘
                    ↓
        specification.md + receipt.json
```

**Five stages, verified by hash receipt.**

## The Distributed Clustering Implementation

The runtime clustering system demonstrates the constitutional equation in practice:

### RDF Specification Layer
- **File**: `ontology/runtime-clustering.ttl`
- **Defines**: Raft consensus, cluster management, distributed task execution, fault tolerance
- **Classes**: ConsensusAlgorithm, ClusterManagement, DistributedTaskExecution, FaultTolerance
- **Enums**: NodeState, NodeHealth, TaskSchedulingStrategy, RecoveryStrategy
- **Properties**: election timeouts, heartbeat intervals, health thresholds, retry policies

### Code Generation Layer
- **SPARQL Query**: `sparql/extract-runtime-clustering.rq`
- **Tera Template**: `templates/runtime-module.tera`
- **Generates**: Python modules from RDF specification

### Validation Layer
- **Spec Validator**: `src/specify_cli/core/spec_validator.py`
- **Checks**: @timed decorators, span() calls, error handling, type hints
- **Validates**: That generated code matches specification requirements

### Self-Observation
- **Command**: `specify validate specs`
- **Purpose**: Check that all code implements its RDF specification
- **Result**: Exit code 0 if valid, 1 if code diverges from spec

## Breaking the Equation (Constitutional Violation)

The constitutional equation is violated when:

```python
# ❌ VIOLATION: Hand-writing commands instead of generating from RDF
# File: src/specify_cli/commands/foo.py (NOT in generated files list)
def my_command():
    pass

# Why: This command exists without corresponding RDF specification
# The specification is incomplete/incorrect/missing
```

**Fix**: Write the specification in RDF first, then run `ggen sync`

```turtle
# ✅ CORRECT: Define in RDF first
# File: ontology/cli-commands.ttl

cli:FooCommand a owl:Class ;
    rdfs:subClassOf cli:Command ;
    rdfs:label "foo"@en ;
    rdfs:comment "Description of foo command"@en .
```

Then run:
```bash
ggen sync
```

## Verification Process

To verify the constitutional equation holds:

```bash
# 1. Extract current state
git status

# 2. Run generation
ggen sync

# 3. Check for changes
git diff

# 4. Validate all modules
specify validate specs

# 5. Run tests
uv run pytest tests/

# 6. Verify receipt
cat receipt.json  # SHA256 hash proving spec.md = μ(feature.ttl)
```

If `ggen sync` produces no changes, the equation holds. If it does, the RDF was out of sync with the code.

## When to Edit What

### Edit RDF When:
- Adding new CLI commands
- Changing command arguments
- Updating command descriptions
- Modifying runtime module specifications
- Adding new feature specifications

### Edit Python When:
- Implementing business logic in ops/ layer
- Runtime integration in runtime/ layer
- But ONLY for logic, not for signatures
- Method signatures must match RDF

### NEVER Edit Directly:
- `src/specify_cli/commands/*.py` (generate from RDF)
- `tests/e2e/test_commands_*.py` (generate from RDF)
- `README.md` (generate from RDF)
- `CHANGELOG.md` (generate from RDF)

## The Four Layers of Spec-Kit

### Layer 1: Ontology (RDF Schema)
```
ontology/spec-kit-schema.ttl
↓ defines vocabulary for
Layer 2
```

### Layer 2: Specifications (RDF Data)
```
ontology/cli-commands.ttl
memory/documentation.ttl
↓ transformed by ggen via μ₁→μ₅ to
Layer 3
```

### Layer 3: Generated Artifacts
```
src/specify_cli/commands/*.py
src/specify_cli/ops/*.py
README.md, CHANGELOG.md
↓ organized by
Layer 4
```

### Layer 4: System Observation
```
core/spec_validator.py
commands/validate_specs.py
↓ verifies
constitutional_equation.md (this file)
```

## Invariants

These properties must always hold:

1. **Idempotence**: `μ(μ(X)) = μ(X)` - Running ggen sync twice produces identical output
2. **Determinism**: Same RDF input always produces same code output
3. **Completeness**: All generated code can be traced back to RDF specification
4. **Verifiability**: `specify validate specs` proves code matches spec
5. **Traceability**: Every line of generated code has a comment pointing to RDF source

## Future Extensions

The constitutional equation can be extended to:

- **Database schemas**: `schema.sql = μ(data-model.ttl)`
- **API documentation**: `openapi.json = μ(api-spec.ttl)`
- **Infrastructure**: `terraform.tf = μ(infra-spec.ttl)`
- **Deployment**: `docker-compose.yml = μ(deployment.ttl)`

Each follows the same pattern: RDF is the source of truth, everything else is generated.

## Reading This in Context

- **CLAUDE.md**: Developer workflow guide
- **spec-kit-schema.ttl**: RDF vocabulary definitions
- **ggen.toml**: Transformation pipeline configuration
- **sparql/*.rq**: Data extraction queries
- **templates/*.tera**: Code generation templates

Together, these files implement the constitutional equation: **spec.md = μ(feature.ttl)**.

---

**Last Updated**: Generated from constitutional_equation.md specification
**Source of Truth**: `memory/constitutional-equation.ttl` (when it exists)
