# RDF-First Development Guide

**Principle**: All specifications are written in RDF/Turtle (`.ttl`) files and transformed into code, documentation, and tests via the constitutional equation `spec.md = μ(feature.ttl)`.

---

## Table of Contents

1. [What is RDF-First Development?](#what-is-rdf-first-development)
2. [The Constitutional Equation](#the-constitutional-equation)
3. [RDF Ontology](#rdf-ontology)
4. [Five-Stage Transformation](#five-stage-transformation)
5. [Practical Examples](#practical-examples)
6. [Tools & Commands](#tools--commands)
7. [Best Practices](#best-practices)

---

## What is RDF-First Development?

**Traditional Development**:
```
User Story → Code → Documentation → Tests
```

**RDF-First Development**:
```
RDF Specification → μ transformation → Code + Docs + Tests
```

### Benefits

| Benefit | Description |
|---------|-------------|
| **Single Source of Truth** | RDF specs are canonical, everything else generated |
| **Semantic Queries** | Use SPARQL to analyze specifications |
| **Automatic Documentation** | Markdown generated from RDF via Tera templates |
| **Verifiable** | SHA256 receipts prove transformation correctness |
| **Machine-Readable** | Tools can reason about specifications |

### Why RDF/Turtle?

- **W3C Standard**: Decades of tooling and best practices
- **Human-Readable**: More readable than XML or JSON-LD
- **Graph-Based**: Natural for relationships and dependencies
- **SHACL Validation**: Built-in constraint validation
- **SPARQL Queries**: Powerful query language

---

## The Constitutional Equation

```
spec.md = μ(feature.ttl)
```

Where:
- **spec.md**: Generated documentation (Markdown)
- **μ**: Five-stage transformation (normalize → extract → emit → canonicalize → receipt)
- **feature.ttl**: Source specification (RDF/Turtle)

### Mathematical Formulation

```
μ = μ₅ ∘ μ₄ ∘ μ₃ ∘ μ₂ ∘ μ₁
```

Each stage is a pure function:
- **μ₁**: RDF → Validated RDF
- **μ₂**: Validated RDF → SPARQL Results
- **μ₃**: SPARQL Results → Rendered Templates
- **μ₄**: Rendered Templates → Formatted Output
- **μ₅**: Formatted Output → (Output, SHA256)

See [CONSTITUTIONAL_EQUATION.md](./CONSTITUTIONAL_EQUATION.md) for mathematical details.

---

## RDF Ontology

### Core Namespaces

```turtle
@prefix spec: <http://spec-kit.org/spec#> .
@prefix jtbd: <http://spec-kit.org/jtbd#> .
@prefix cmd:  <http://spec-kit.org/command#> .
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sh:   <http://www.w3.org/ns/shacl#> .
```

### Spec-Kit Schema

```turtle
# Feature specification
spec:Feature a rdfs:Class ;
    rdfs:label "Feature" ;
    rdfs:comment "A system feature or capability" .

spec:hasJob a rdf:Property ;
    rdfs:domain spec:Feature ;
    rdfs:range jtbd:Job .

spec:hasOutcome a rdf:Property ;
    rdfs:domain spec:Feature ;
    rdfs:range jtbd:Outcome .

spec:priority a rdf:Property ;
    rdfs:domain spec:Feature ;
    rdfs:range xsd:string .  # "high" | "medium" | "low"
```

### JTBD Extension

```turtle
# Jobs-to-be-Done ontology
jtbd:Job a rdfs:Class ;
    rdfs:label "Job to be Done" ;
    rdfs:comment "A job that users want to accomplish" .

jtbd:Outcome a rdfs:Class ;
    rdfs:label "Desired Outcome" ;
    rdfs:comment "Measurable outcome for a job" .

jtbd:importance a rdf:Property ;
    rdfs:domain jtbd:Outcome ;
    rdfs:range xsd:decimal .  # 1-10 scale

jtbd:satisfaction a rdf:Property ;
    rdfs:domain jtbd:Outcome ;
    rdfs:range xsd:decimal .  # 1-10 scale

jtbd:opportunityScore a rdf:Property ;
    rdfs:domain jtbd:Outcome ;
    rdfs:range xsd:decimal .  # importance + max(importance - satisfaction, 0)
```

See `ontology/spec-kit-schema.ttl` for full schema.

---

## Five-Stage Transformation

### Stage 1: μ₁ Normalize (SHACL Validation)

**Purpose**: Validate RDF against SHACL shapes

**Example**:
```turtle
# memory/feature.ttl
@prefix spec: <http://spec-kit.org/spec#> .

spec:UserAuth a spec:Feature ;
    spec:name "User Authentication" ;
    spec:priority "high" .
```

```turtle
# ontology/shapes.ttl
@prefix sh: <http://www.w3.org/ns/shacl#> .

spec:FeatureShape a sh:NodeShape ;
    sh:targetClass spec:Feature ;
    sh:property [
        sh:path spec:name ;
        sh:minCount 1 ;
        sh:datatype xsd:string ;
    ] ;
    sh:property [
        sh:path spec:priority ;
        sh:pattern "^(high|medium|low)$" ;
    ] .
```

**Command**:
```bash
ggen validate --config docs/ggen.toml
```

**Output**: Validation report or errors

### Stage 2: μ₂ Extract (SPARQL Queries)

**Purpose**: Extract structured data from RDF

**Example**:
```sparql
# sparql/features.rq
PREFIX spec: <http://spec-kit.org/spec#>

SELECT ?name ?priority
WHERE {
    ?feature a spec:Feature ;
             spec:name ?name ;
             spec:priority ?priority .
}
ORDER BY ?priority
```

**Command**:
```bash
ggen query --sparql sparql/features.rq memory/feature.ttl
```

**Output** (JSON):
```json
{
  "results": {
    "bindings": [
      {"name": "User Authentication", "priority": "high"}
    ]
  }
}
```

### Stage 3: μ₃ Emit (Tera Templates)

**Purpose**: Render templates with SPARQL results

**Template** (`templates/feature.md.tera`):
```markdown
# {{ name }}

**Priority**: {{ priority }}

## Description

This feature implements {{ name | lower }}.

## Requirements

{% for req in requirements %}
- {{ req }}
{% endfor %}
```

**Command**:
```bash
ggen sync --config docs/ggen.toml
```

**Output** (`docs/features/user-authentication.md`):
```markdown
# User Authentication

**Priority**: high

## Description

This feature implements user authentication.
```

### Stage 4: μ₄ Canonicalize (Format)

**Purpose**: Format output (e.g., Markdown, Python, JSON)

**Example**:
```bash
# Format generated Markdown
ggen format --input docs/features/*.md

# Or use prettier/black for code
prettier --write docs/**/*.md
black src/**/*.py
```

### Stage 5: μ₅ Receipt (SHA256 Proof)

**Purpose**: Generate cryptographic proof of transformation

**Example**:
```bash
ggen receipt --output receipts/feature-auth.json
```

**Output** (`receipts/feature-auth.json`):
```json
{
  "input": {
    "file": "memory/feature.ttl",
    "sha256": "abc123..."
  },
  "output": {
    "file": "docs/features/user-authentication.md",
    "sha256": "def456..."
  },
  "transformation": {
    "sparql": "sparql/features.rq",
    "template": "templates/feature.md.tera",
    "ggen_version": "5.0.2"
  },
  "timestamp": "2025-12-21T12:00:00Z"
}
```

**Verification**:
```bash
ggen verify receipts/feature-auth.json
```

---

## Practical Examples

### Example 1: Feature Specification

**Input** (`memory/auth-feature.ttl`):
```turtle
@prefix spec: <http://spec-kit.org/spec#> .
@prefix jtbd: <http://spec-kit.org/jtbd#> .

spec:UserAuthentication a spec:Feature ;
    spec:name "User Authentication" ;
    spec:description "Secure user login system" ;
    spec:priority "high" ;
    spec:hasJob jtbd:AuthenticateUser ;
    spec:hasOutcome [
        jtbd:description "Users log in within 3 seconds" ;
        jtbd:importance 9.5 ;
        jtbd:satisfaction 7.0 ;
        jtbd:opportunityScore 12.0
    ] .

jtbd:AuthenticateUser a jtbd:Job ;
    jtbd:statement "When I want to access my account, I want to log in securely, so I can protect my data" .
```

**SPARQL Query** (`sparql/features.rq`):
```sparql
PREFIX spec: <http://spec-kit.org/spec#>
PREFIX jtbd: <http://spec-kit.org/jtbd#>

SELECT ?name ?description ?priority ?jobStatement ?outcomeDesc ?opportunity
WHERE {
    ?feature a spec:Feature ;
             spec:name ?name ;
             spec:description ?description ;
             spec:priority ?priority ;
             spec:hasJob ?job ;
             spec:hasOutcome ?outcome .

    ?job jtbd:statement ?jobStatement .

    ?outcome jtbd:description ?outcomeDesc ;
             jtbd:opportunityScore ?opportunity .
}
```

**Template** (`templates/feature.md.tera`):
```markdown
# {{ name }}

**Priority**: {{ priority }}

## Job Story

{{ jobStatement }}

## Description

{{ description }}

## Success Criteria

{{ outcomeDesc }}

**Opportunity Score**: {{ opportunity }} (High Priority)

## Implementation Notes

- Implement OAuth2/OpenID Connect
- Session timeout: 30 minutes
- Rate limiting: 5 attempts per minute
```

**Command**:
```bash
ggen sync --config docs/ggen.toml
```

**Generated Output** (`docs/features/user-authentication.md`):
```markdown
# User Authentication

**Priority**: high

## Job Story

When I want to access my account, I want to log in securely, so I can protect my data

## Description

Secure user login system

## Success Criteria

Users log in within 3 seconds

**Opportunity Score**: 12.0 (High Priority)

## Implementation Notes

- Implement OAuth2/OpenID Connect
- Session timeout: 30 minutes
- Rate limiting: 5 attempts per minute
```

### Example 2: Command Specification

**Input** (`ontology/cli-commands-deps.ttl`):
```turtle
@prefix cmd: <http://spec-kit.org/command#> .

cmd:DepsAdd a cmd:Command ;
    cmd:name "deps add" ;
    cmd:description "Add dependencies to project" ;
    cmd:arguments [
        cmd:name "packages" ;
        cmd:type "list[str]" ;
        cmd:required true
    ] ;
    cmd:options [
        cmd:name "dev" ;
        cmd:type "bool" ;
        cmd:flag "--dev" ;
        cmd:default false
    ] .
```

**Generated Code** (`src/specify_cli/commands/deps.py`):
```python
import typer
from specify_cli.core.instrumentation import instrument_command

app = typer.Typer(help="Dependency management")

@app.command("add")
@instrument_command("deps.add")
def add_command(
    packages: list[str],
    dev: bool = typer.Option(False, "--dev", "-D", help="Add as dev dependency")
) -> None:
    """Add dependencies to project."""
    # Generated from RDF specification
    # See: ontology/cli-commands-deps.ttl
    ...
```

---

## Tools & Commands

### ggen Commands

```bash
# Validate RDF syntax and SHACL shapes
ggen validate --config docs/ggen.toml

# Execute SPARQL query
ggen query --sparql sparql/features.rq memory/*.ttl

# Sync: validate + query + render templates
ggen sync --config docs/ggen.toml

# Generate SHA256 receipt
ggen receipt --output receipts/transform.json

# Verify transformation
ggen verify receipts/transform.json

# Show ggen version
ggen --version
```

### Specify CLI Commands

```bash
# Generate docs from RDF specs
specify ggen sync --config docs/ggen.toml

# Validate RDF files
specify ggen validate ontology/

# Query RDF with SPARQL
specify ggen query sparql/features.rq memory/*.ttl
```

---

## Best Practices

### 1. Use Prefixes Consistently

**Good**:
```turtle
@prefix spec: <http://spec-kit.org/spec#> .

spec:Feature123 a spec:Feature .
```

**Bad**:
```turtle
<http://spec-kit.org/spec#Feature123> a <http://spec-kit.org/spec#Feature> .
```

### 2. Define SHACL Shapes

Validate all RDF specifications:

```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .

spec:FeatureShape a sh:NodeShape ;
    sh:targetClass spec:Feature ;
    sh:property [
        sh:path spec:name ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:datatype xsd:string ;
    ] .
```

### 3. Use Blank Nodes for Inline Data

**Good** (inline outcome):
```turtle
spec:Feature123 spec:hasOutcome [
    jtbd:description "Fast login" ;
    jtbd:importance 9.0
] .
```

**Also Good** (named outcome):
```turtle
spec:Feature123 spec:hasOutcome spec:OutcomeFastLogin .

spec:OutcomeFastLogin a jtbd:Outcome ;
    jtbd:description "Fast login" ;
    jtbd:importance 9.0 .
```

### 4. Write Reusable SPARQL Queries

Use `CONSTRUCT` for transformations:

```sparql
PREFIX spec: <http://spec-kit.org/spec#>

CONSTRUCT {
    ?feature spec:summary ?summary .
}
WHERE {
    ?feature a spec:Feature ;
             spec:name ?name ;
             spec:description ?desc .

    BIND(CONCAT(?name, ": ", ?desc) AS ?summary)
}
```

### 5. Organize Files by Domain

```
ontology/
├── spec-kit-schema.ttl       # Core schema
├── jtbd-extension.ttl         # JTBD ontology
└── cli-commands-*.ttl         # Command specs

memory/
├── features/                  # Feature specs
├── jobs/                      # JTBD job stories
└── outcomes/                  # Outcome metrics

sparql/
├── features.rq               # Feature queries
├── jobs.rq                   # Job queries
└── metrics.rq                # Metrics queries

templates/
├── feature.md.tera           # Feature doc template
├── job.md.tera               # Job doc template
└── command.py.tera           # Command code template
```

### 6. Version Your Receipts

```bash
receipts/
├── v1.0.0/
│   ├── feature-auth.json
│   └── feature-search.json
└── v1.1.0/
    ├── feature-auth.json
    └── feature-search.json
```

### 7. Use Git for RDF Specifications

```bash
# Track all RDF files
git add ontology/ memory/ sparql/ templates/

# Commit with meaningful messages
git commit -m "feat(rdf): add user authentication specification"

# Tag releases
git tag -a v1.0.0 -m "Release 1.0.0"
```

---

## Next Steps

- [CONSTITUTIONAL_EQUATION.md](./CONSTITUTIONAL_EQUATION.md) - Mathematical details
- [RDF_DOCUMENTATION_SYSTEM.md](./RDF_DOCUMENTATION_SYSTEM.md) - Full RDF workflow
- [JTBD_INDEX.md](./JTBD_INDEX.md) - JTBD integration
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Three-tier architecture

---

**Generated with**: Specify CLI v0.0.25
**Last Updated**: 2025-12-21
