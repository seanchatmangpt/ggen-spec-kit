# 13. Vocabulary Boundary

★★

*Every domain has its language. Mixing vocabularies creates confusion. Clear vocabulary boundaries separate concerns, enable reuse, and prevent conceptual pollution. Good fences make good ontologies.*

---

## The Language of Domains

As your specification grows, you accumulate concepts. Commands, arguments, options. Jobs, outcomes, circumstances. Shapes, queries, templates. Each concept belongs to a domain with its own terminology, its own rules, its own experts.

Domains are linguistic communities. CLI developers speak of commands, flags, and exit codes. JTBD practitioners speak of jobs, outcomes, and progress. Documentation authors speak of sections, audiences, and reading levels. Each community has developed precise terms for their concerns.

Without vocabulary boundaries, these communities collide:

- Is "description" from the CLI domain or the documentation domain?
- Is "required" about argument validation or about outcome importance?
- Does "type" mean data type, job type, or shape type?
- Is "name" the command name, the argument name, or the user's name?

This conceptual pollution creates ambiguity. The same term means different things in different contexts. Queries become complicated. Maintenance becomes hazardous. New team members are confused by overloaded terminology.

---

## The Namespace Solution

Namespaces solve this problem by giving each domain its own linguistic territory. Within that territory, terms have clear meanings. Between territories, relationships are explicit.

Consider the difference:

**Without namespaces (ambiguous):**
```turtle
:validate :type "command" .
:validate :description "Validate files" .
:file :type "path" .
:file :required true .
```

Is `:type` the same property in both cases? Is `:required` related to `:type`? The relationships are unclear.

**With namespaces (clear):**
```turtle
cli:validate a cli:Command .
cli:validate cli:type cli:CommandType .
cli:validate sk:description "Validate files" .

cli:file a cli:Argument .
cli:file cli:type "path" .
cli:file cli:required true .
```

Now it's clear: `cli:type` is specific to CLI arguments, `sk:description` is a shared property.

---

## The Problem Statement

**Unbounded vocabularies grow into tangled messes where the same terms mean different things and different terms mean the same thing. Queries become ambiguous. Maintenance becomes dangerous. Knowledge becomes confused.**

The symptoms:

1. **Property collision**: Using the same property name for different purposes
2. **Class collision**: Using the same class name in different domains
3. **Semantic blur**: Unclear whether two uses of a term are the same concept
4. **Query confusion**: Queries return unexpected results due to term ambiguity
5. **Import chaos**: Importing one domain brings unexpected concepts from another

---

## The Forces at Play

### Force 1: Reuse vs. Precision

**Reuse wants sharing.** Common concepts (name, description, type) feel like they should be shared. Why define "description" five times?

**Precision wants separation.** Domain-specific meanings require domain-specific definitions. A command description and a job description may have different constraints.

```
Reuse ←──────────────────────────────────→ Precision
(share common concepts)                    (domain-specific definitions)
```

### Force 2: Simplicity vs. Clarity

**Simplicity wants fewer prefixes.** Fewer namespaces feels cleaner. Less typing, fewer imports.

**Clarity wants explicit namespaces.** Explicit prefixes prevent ambiguity. You always know which domain you're in.

```
Simplicity ←────────────────────────────→ Clarity
(fewer namespaces)                        (explicit domains)
```

### Force 3: Independence vs. Integration

**Independence wants isolation.** Each domain should be self-contained, changeable without affecting others.

**Integration wants connection.** Domains must work together. Commands accomplish jobs. Jobs have outcomes.

```
Independence ←────────────────────────→ Integration
(isolated domains)                      (connected domains)
```

### Resolution: Bounded Vocabularies with Explicit Bridges

Share what's truly universal. Separate what's domain-specific. Connect domains through explicit bridging properties.

---

## Therefore: Define Explicit Vocabulary Boundaries

Define explicit vocabulary boundaries using namespaces. Each domain gets its own prefix and namespace.

### Core Vocabulary Organization

```turtle
# ============================================================
# Layer 0: External Standards (truly universal)
# ============================================================
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

# ============================================================
# Layer 1: Spec-kit Core (shared within spec-kit)
# ============================================================
@prefix sk: <https://spec-kit.io/ontology#> .

# ============================================================
# Layer 2: Domain Vocabularies
# ============================================================
@prefix cli: <https://spec-kit.io/ontology/cli#> .      # CLI domain
@prefix jtbd: <https://spec-kit.io/ontology/jtbd#> .    # Jobs To Be Done
@prefix docs: <https://spec-kit.io/ontology/docs#> .    # Documentation
@prefix ggen: <https://spec-kit.io/ontology/ggen#> .    # Transformation
@prefix otel: <https://spec-kit.io/ontology/otel#> .    # Observability
```

### Boundary Rules

#### Rule 1: Own What You Define

Every concept is defined in exactly one namespace. No concept lives in two places.

```turtle
# ============================================================
# CLI domain owns command concepts
# ============================================================
cli:Command a rdfs:Class ;
    rdfs:label "CLI Command" ;
    rdfs:comment "An executable command in the CLI interface" ;
    rdfs:isDefinedBy <https://spec-kit.io/ontology/cli#> .

cli:Argument a rdfs:Class ;
    rdfs:label "Command Argument" ;
    rdfs:comment "A positional argument to a CLI command" ;
    rdfs:isDefinedBy <https://spec-kit.io/ontology/cli#> .

cli:Option a rdfs:Class ;
    rdfs:label "Command Option" ;
    rdfs:comment "A named option (flag) for a CLI command" ;
    rdfs:isDefinedBy <https://spec-kit.io/ontology/cli#> .

cli:hasArgument a rdf:Property ;
    rdfs:label "has argument" ;
    rdfs:domain cli:Command ;
    rdfs:range cli:Argument ;
    rdfs:isDefinedBy <https://spec-kit.io/ontology/cli#> .

# ============================================================
# JTBD domain owns job concepts
# ============================================================
jtbd:Job a rdfs:Class ;
    rdfs:label "Customer Job" ;
    rdfs:comment "The progress a customer is trying to make" ;
    rdfs:isDefinedBy <https://spec-kit.io/ontology/jtbd#> .

jtbd:Outcome a rdfs:Class ;
    rdfs:label "Desired Outcome" ;
    rdfs:comment "A measurable result customers seek" ;
    rdfs:isDefinedBy <https://spec-kit.io/ontology/jtbd#> .

jtbd:Circumstance a rdfs:Class ;
    rdfs:label "Circumstance of Struggle" ;
    rdfs:comment "The context in which a job arises" ;
    rdfs:isDefinedBy <https://spec-kit.io/ontology/jtbd#> .

jtbd:hasOutcome a rdf:Property ;
    rdfs:label "has outcome" ;
    rdfs:domain jtbd:Job ;
    rdfs:range jtbd:Outcome ;
    rdfs:isDefinedBy <https://spec-kit.io/ontology/jtbd#> .
```

#### Rule 2: Import, Don't Redefine

When using concepts from another domain, import them—don't redefine them.

```turtle
# ============================================================
# GOOD: Reference JTBD concept
# ============================================================
cli:ValidateCommand a cli:Command ;
    jtbd:accomplishesJob jtbd:ValidateOntologyJob .

# ============================================================
# BAD: Redefine in CLI namespace
# ============================================================
# cli:ValidateCommand a cli:Command ;
#     cli:accomplishesJob cli:ValidateOntologyJob .
#     # ^ Wrong! This implies CLI owns job concepts
```

#### Rule 3: Create Bridging Properties Explicitly

When domains connect, define explicit bridges:

```turtle
# ============================================================
# Bridge between CLI and JTBD domains
# ============================================================
cli:accomplishesJob a rdf:Property ;
    rdfs:label "accomplishes job" ;
    rdfs:comment "Links a CLI command to the job it accomplishes" ;
    rdfs:domain cli:Command ;
    rdfs:range jtbd:Job ;
    rdfs:isDefinedBy <https://spec-kit.io/ontology/cli#> .
    # Note: Defined in CLI because CLI "reaches out" to JTBD

# Bridge between CLI and Documentation domains
cli:documentedIn a rdf:Property ;
    rdfs:label "documented in" ;
    rdfs:comment "Links a CLI command to its documentation section" ;
    rdfs:domain cli:Command ;
    rdfs:range docs:Section ;
    rdfs:isDefinedBy <https://spec-kit.io/ontology/cli#> .

# Bridge between JTBD and Observability domains
jtbd:measuredBy a rdf:Property ;
    rdfs:label "measured by" ;
    rdfs:comment "Links an outcome to its measuring metric" ;
    rdfs:domain jtbd:Outcome ;
    rdfs:range otel:Metric ;
    rdfs:isDefinedBy <https://spec-kit.io/ontology/jtbd#> .
```

#### Rule 4: Use Qualified Names Consistently

In queries and documentation, use full qualified names:

```sparql
# ============================================================
# Clear: Qualified names show domains
# ============================================================
PREFIX cli: <https://spec-kit.io/ontology/cli#>
PREFIX jtbd: <https://spec-kit.io/ontology/jtbd#>

SELECT ?cmd ?cmdName ?job ?jobName WHERE {
    ?cmd a cli:Command ;
         rdfs:label ?cmdName ;
         cli:accomplishesJob ?job .
    ?job a jtbd:Job ;
         rdfs:label ?jobName .
}
```

---

## Domain Organization

Organize your ontology files to reflect domain boundaries:

```
ontology/
├── core/
│   └── spec-kit-schema.ttl      # sk: core concepts
│                                 # - sk:Entity, sk:description
│                                 # - Truly universal properties
│
├── cli/
│   ├── cli-schema.ttl           # cli: classes and properties
│   │                             # - cli:Command, cli:Argument
│   │                             # - cli:hasArgument, cli:exitCode
│   ├── cli-shapes.ttl           # cli: SHACL shapes
│   └── cli-instances.ttl        # cli: command definitions
│
├── jtbd/
│   ├── jtbd-schema.ttl          # jtbd: classes and properties
│   │                             # - jtbd:Job, jtbd:Outcome
│   │                             # - jtbd:hasOutcome, jtbd:importance
│   ├── jtbd-shapes.ttl          # jtbd: SHACL shapes
│   └── jtbd-instances.ttl       # jtbd: job definitions
│
├── docs/
│   ├── docs-schema.ttl          # docs: classes and properties
│   │                             # - docs:Section, docs:Page
│   │                             # - docs:audience, docs:wordCount
│   └── docs-instances.ttl       # docs: documentation structure
│
└── bridges/
    ├── cli-jtbd-bridge.ttl      # Bridge properties between CLI and JTBD
    ├── cli-docs-bridge.ttl      # Bridge properties between CLI and Docs
    └── jtbd-otel-bridge.ttl     # Bridge properties between JTBD and OTEL
```

---

## Shared vs. Domain-Specific Properties

### Truly Shared Properties (sk: namespace)

These live in the core namespace because they're genuinely universal:

```turtle
# ============================================================
# Shared descriptive properties (used everywhere)
# ============================================================
sk:description a rdf:Property ;
    rdfs:label "description" ;
    rdfs:comment "A human-readable description of any entity" ;
    rdfs:range xsd:string .

sk:version a rdf:Property ;
    rdfs:label "version" ;
    rdfs:comment "Semantic version of any versioned entity" ;
    rdfs:range xsd:string .

sk:createdDate a rdf:Property ;
    rdfs:label "created date" ;
    rdfs:comment "When any entity was created" ;
    rdfs:range xsd:dateTime .

sk:modifiedDate a rdf:Property ;
    rdfs:label "modified date" ;
    rdfs:comment "When any entity was last modified" ;
    rdfs:range xsd:dateTime .

sk:deprecated a rdf:Property ;
    rdfs:label "deprecated" ;
    rdfs:comment "Whether any entity is deprecated" ;
    rdfs:range xsd:boolean .
```

### Domain-Specific Properties

These are only meaningful in their domain:

```turtle
# ============================================================
# CLI-specific properties
# ============================================================
cli:hasArgument a rdf:Property ;
    rdfs:domain cli:Command ;
    rdfs:range cli:Argument .

cli:exitCode a rdf:Property ;
    rdfs:domain cli:Command ;
    rdfs:range xsd:integer .

cli:required a rdf:Property ;
    rdfs:domain cli:Argument ;
    rdfs:range xsd:boolean .

# ============================================================
# JTBD-specific properties
# ============================================================
jtbd:hasOutcome a rdf:Property ;
    rdfs:domain jtbd:Job ;
    rdfs:range jtbd:Outcome .

jtbd:importance a rdf:Property ;
    rdfs:domain jtbd:Outcome ;
    rdfs:range xsd:string .  # "high", "medium", "low"

jtbd:satisfaction a rdf:Property ;
    rdfs:domain jtbd:Outcome ;
    rdfs:range xsd:string .  # "high", "medium", "low"

# ============================================================
# Documentation-specific properties
# ============================================================
docs:wordCount a rdf:Property ;
    rdfs:domain docs:Section ;
    rdfs:range xsd:integer .

docs:audience a rdf:Property ;
    rdfs:domain docs:Page ;
    rdfs:range xsd:string .

docs:readingLevel a rdf:Property ;
    rdfs:domain docs:Section ;
    rdfs:range xsd:string .
```

### Cross-Domain Bridges

Properties that connect domains:

```turtle
# ============================================================
# Cross-domain bridges
# ============================================================

# CLI → JTBD: Commands accomplish jobs
cli:accomplishesJob a rdf:Property ;
    rdfs:domain cli:Command ;
    rdfs:range jtbd:Job ;
    rdfs:comment "Links a CLI command to the customer job it helps accomplish" .

# CLI → Docs: Commands have documentation
cli:documentedIn a rdf:Property ;
    rdfs:domain cli:Command ;
    rdfs:range docs:Section ;
    rdfs:comment "Links a CLI command to its documentation section" .

# JTBD → OTEL: Outcomes are measured by metrics
jtbd:measuredBy a rdf:Property ;
    rdfs:domain jtbd:Outcome ;
    rdfs:range otel:Metric ;
    rdfs:comment "Links a desired outcome to the metric that measures it" .

# Docs → CLI: Documentation references commands
docs:documents a rdf:Property ;
    rdfs:domain docs:Section ;
    rdfs:range cli:Command ;
    rdfs:comment "Links a documentation section to the command it documents" .
```

---

## Query Patterns Across Boundaries

### Navigating Within a Domain

```sparql
# All commands and their arguments (within CLI domain)
PREFIX cli: <https://spec-kit.io/ontology/cli#>

SELECT ?cmd ?cmdName ?arg ?argName ?argType WHERE {
    ?cmd a cli:Command ;
         rdfs:label ?cmdName ;
         cli:hasArgument ?arg .
    ?arg rdfs:label ?argName ;
         cli:type ?argType .
}
```

### Crossing Domain Boundaries

```sparql
# Commands and the jobs they accomplish (crossing CLI → JTBD)
PREFIX cli: <https://spec-kit.io/ontology/cli#>
PREFIX jtbd: <https://spec-kit.io/ontology/jtbd#>

SELECT ?cmd ?cmdName ?job ?jobName WHERE {
    ?cmd a cli:Command ;
         rdfs:label ?cmdName ;
         cli:accomplishesJob ?job .
    ?job a jtbd:Job ;
         rdfs:label ?jobName .
}
```

### Multi-Domain Navigation

```sparql
# Complete thread: Commands → Jobs → Outcomes → Metrics
PREFIX cli: <https://spec-kit.io/ontology/cli#>
PREFIX jtbd: <https://spec-kit.io/ontology/jtbd#>
PREFIX otel: <https://spec-kit.io/ontology/otel#>

SELECT ?cmd ?job ?outcome ?metric WHERE {
    ?cmd a cli:Command ;
         cli:accomplishesJob ?job .
    ?job jtbd:hasOutcome ?outcome .
    ?outcome jtbd:measuredBy ?metric .
}
```

---

## Case Study: The Namespace Refactoring

### Before: Tangled Vocabulary

A team started with a single namespace for everything:

```turtle
@prefix spec: <http://example.org/spec#> .

spec:validate a spec:Command .
spec:validate spec:type "cli" .
spec:validate spec:description "Validate ontology files" .

spec:validateJob a spec:Job .
spec:validateJob spec:type "functional" .
spec:validateJob spec:description "Ensure ontology is valid" .

# Problem: spec:type and spec:description are overloaded
# Query for "all types" returns a mix of CLI types and job types
```

**Problems:**
- `spec:type` means different things (CLI type vs. job type)
- `spec:description` has different constraints in different contexts
- Queries return unexpected results
- Changes to CLI break job processing

### After: Clear Boundaries

Refactored with domain namespaces:

```turtle
@prefix sk: <https://spec-kit.io/ontology#> .
@prefix cli: <https://spec-kit.io/ontology/cli#> .
@prefix jtbd: <https://spec-kit.io/ontology/jtbd#> .

cli:validate a cli:Command ;
    sk:description "Validate ontology files" ;
    cli:type "validation" ;
    cli:accomplishesJob jtbd:ValidateOntologyJob .

jtbd:ValidateOntologyJob a jtbd:Job ;
    sk:description "Ensure ontology is valid" ;
    jtbd:dimension jtbd:Functional ;
    jtbd:hasOutcome jtbd:MinimizeValidationErrors .
```

**Benefits:**
- Clear ownership: `cli:type` is CLI-specific, `jtbd:dimension` is JTBD-specific
- Shared where appropriate: `sk:description` is universal
- Explicit bridge: `cli:accomplishesJob` connects domains
- Queries are unambiguous

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: The Mega-Namespace

Putting everything in one namespace:

```turtle
@prefix app: <http://example.org/app#> .

app:Command, app:Argument, app:Job, app:Outcome,
app:Section, app:Metric, app:Shape, app:Query...
```

**Problem:** No boundaries. Everything can touch everything. Changes ripple unpredictably.

### Anti-Pattern 2: The Micro-Namespace

Creating a namespace per entity:

```turtle
@prefix validate: <http://example.org/commands/validate#> .
@prefix sync: <http://example.org/commands/sync#> .
@prefix check: <http://example.org/commands/check#> .
```

**Problem:** Too many namespaces. No coherent vocabulary. Import chaos.

### Anti-Pattern 3: Implicit Bridges

Connecting domains without explicit properties:

```turtle
cli:validate jtbd:hasOutcome jtbd:FastValidation .
# jtbd:hasOutcome shouldn't be used with cli:Command
```

**Problem:** Domain semantics violated. Confusion about what properties apply where.

### Anti-Pattern 4: Duplicate Definitions

Defining the same concept in multiple domains:

```turtle
cli:description a rdf:Property .
jtbd:description a rdf:Property .
docs:description a rdf:Property .
# All mean the same thing!
```

**Problem:** Queries must check all three. Updates must happen in all three.

---

## Implementation Checklist

### Vocabulary Design

- [ ] Identify distinct domains in your problem space
- [ ] Assign namespace prefix and URI to each domain
- [ ] Determine which concepts are truly universal (core namespace)
- [ ] Define domain-specific concepts in domain namespaces
- [ ] Identify cross-domain relationships
- [ ] Create explicit bridge properties

### File Organization

- [ ] Create directory per domain
- [ ] Separate schema (classes/properties) from instances
- [ ] Create bridge files for cross-domain properties
- [ ] Document namespace conventions

### Query Patterns

- [ ] Use qualified names in all queries
- [ ] Test queries across domain boundaries
- [ ] Document common cross-domain queries
- [ ] Verify queries don't accidentally mix domains

---

## Resulting Context

After applying this pattern, you have:

- **Clear ownership** of concepts—each belongs to one namespace
- **Unambiguous term usage**—no overloaded meanings
- **Reusable domain vocabularies**—import what you need
- **Clean queries** without confusion about term meanings
- **Controlled integration**—domains connect through explicit bridges
- **Independent evolution**—domain changes don't affect other domains

This supports **[Layered Ontology](./layered-ontology.md)** and enables **[Traceability Thread](./traceability-thread.md)**.

---

## Related Patterns

- *Organizes:* **[9. Semantic Foundation](./semantic-foundation.md)** — Foundation split into vocabularies
- *Enables:* **[16. Layered Ontology](./layered-ontology.md)** — Layers use distinct vocabularies
- *Supports:* **[20. Traceability Thread](./traceability-thread.md)** — Cross-vocabulary links are explicit
- *Shapes:* **[14. Property Path](./property-path.md)** — Paths cross vocabulary boundaries

---

## Philosophical Coda

> *"Good fences make good neighbors."*
>
> — Robert Frost

In ontologies, good namespaces make good vocabularies. They enable concepts to be neighbors without becoming confused. Each domain can develop its terminology precisely, knowing that clear boundaries prevent collision.

The fence is not a barrier—it's a contract. It says: "This is mine to define. That is yours. Here is how we connect." With this clarity, both domains can evolve independently while maintaining their relationship.

---

## Exercises

### Exercise 1: Domain Discovery

For a system you know well:
1. List all the concepts used
2. Group them by domain (clusters of related concepts)
3. Identify shared concepts that cross domains
4. Design namespace structure

### Exercise 2: Boundary Definition

For an existing tangled vocabulary:
1. Find overloaded terms (same term, different meanings)
2. Determine which domain each meaning belongs to
3. Refactor with domain-specific terms
4. Create bridges where needed

### Exercise 3: Bridge Design

For two related domains:
1. Identify all points of connection
2. Determine which domain "owns" each bridge property
3. Document the semantics of each bridge
4. Write test queries that cross the bridge

---

## Further Reading

- *Namespaces in XML* — W3C Recommendation
- *URI Best Practices* — W3C TAG
- *Domain-Driven Design* — Eric Evans (Bounded Contexts)
- *Linked Data Principles* — Tim Berners-Lee

