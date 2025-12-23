# 13. Vocabulary Boundary

★★

*Every domain has its language. Mixing vocabularies creates confusion. Clear vocabulary boundaries separate concerns, enable reuse, and prevent conceptual pollution.*

---

As your specification grows, you accumulate concepts. Commands, arguments, options. Jobs, outcomes, circumstances. Shapes, queries, templates. Each concept belongs to a domain with its own terminology.

Without vocabulary boundaries, concepts bleed into each other:
- Is "description" from the CLI domain or the documentation domain?
- Is "required" about argument validation or about outcome importance?
- Does "type" mean data type, job type, or shape type?

This conceptual pollution creates ambiguity. The same term means different things in different contexts. Queries become complicated. Maintenance becomes hazardous.

**The problem: Unbounded vocabularies grow into tangled messes where the same terms mean different things and different terms mean the same thing.**

---

**The forces at play:**

- *Reuse wants sharing.* Common concepts (name, description, type) feel like they should be shared.

- *Precision wants separation.* Domain-specific meanings require domain-specific definitions.

- *Simplicity wants fewer prefixes.* Fewer namespaces feels cleaner.

- *Clarity wants explicit namespaces.* Explicit prefixes prevent ambiguity.

The tension: share common vocabulary for simplicity, or separate vocabulary for precision.

---

**Therefore:**

Define explicit vocabulary boundaries using namespaces. Each domain gets its own prefix and namespace.

**Core vocabulary organization:**

```turtle
# Shared foundation (truly universal concepts)
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .

# Spec-kit core (shared within spec-kit)
@prefix sk: <http://github.com/spec-kit#> .

# CLI domain
@prefix cli: <http://github.com/spec-kit/cli#> .

# Jobs To Be Done domain
@prefix jtbd: <http://github.com/spec-kit/jtbd#> .

# Documentation domain
@prefix docs: <http://github.com/spec-kit/docs#> .

# Transformation domain
@prefix ggen: <http://github.com/spec-kit/ggen#> .
```

**Boundary rules:**

**1. Own what you define**

Every concept is defined in exactly one namespace:
```turtle
# CLI domain owns command concepts
cli:Command a rdfs:Class .
cli:Argument a rdfs:Class .
cli:Option a rdfs:Class .

# JTBD domain owns job concepts
jtbd:Job a rdfs:Class .
jtbd:Outcome a rdfs:Class .
jtbd:Circumstance a rdfs:Class .
```

**2. Import, don't redefine**

When using concepts from another domain, import—don't redefine:
```turtle
# Good: Reference JTBD concept
cli:ValidateCommand jtbd:accomplishesJob jtbd:ValidateOntologyJob .

# Bad: Redefine in CLI namespace
cli:ValidateCommand cli:accomplishesJob cli:ValidateOntologyJob .
```

**3. Create bridging properties explicitly**

When domains connect, define explicit bridges:
```turtle
# Bridge between CLI and JTBD
cli:accomplishesJob a rdf:Property ;
    rdfs:domain cli:Command ;
    rdfs:range jtbd:Job ;
    rdfs:comment "Links a CLI command to the job it accomplishes" .
```

**4. Use qualified names consistently**

In queries and documentation, use full qualified names:
```sparql
# Clear: Qualified names show domains
SELECT ?cmd ?job WHERE {
    ?cmd a cli:Command ;
         cli:accomplishesJob ?job .
    ?job a jtbd:Job .
}
```

**Domain organization:**

```
ontology/
├── core/
│   └── spec-kit-schema.ttl      # sk: core concepts
├── cli/
│   ├── cli-schema.ttl           # cli: classes and properties
│   └── cli-commands.ttl         # cli: command instances
├── jtbd/
│   ├── jtbd-schema.ttl          # jtbd: classes and properties
│   └── jtbd-jobs.ttl            # jtbd: job instances
└── docs/
    ├── docs-schema.ttl          # docs: classes and properties
    └── docs-sections.ttl        # docs: section instances
```

---

**Resulting context:**

After applying this pattern, you have:

- Clear ownership of concepts
- Unambiguous term usage
- Reusable domain vocabularies
- Clean queries without confusion

This supports **[Layered Ontology](./layered-ontology.md)** and enables **[Traceability Thread](./traceability-thread.md)**.

---

**Related patterns:**

- *Organizes:* **[9. Semantic Foundation](./semantic-foundation.md)** — Foundation split into vocabularies
- *Enables:* **[16. Layered Ontology](./layered-ontology.md)** — Layers use distinct vocabularies
- *Supports:* **[20. Traceability Thread](./traceability-thread.md)** — Cross-vocabulary links are explicit
- *Shapes:* **[14. Property Path](./property-path.md)** — Paths cross vocabulary boundaries

---

> *"Good fences make good neighbors."*
>
> — Robert Frost

In ontologies, good namespaces make good vocabularies. They enable concepts to be neighbors without becoming confused.

---

**Common vocabulary patterns:**

**Shared descriptive properties:**
```turtle
# These live in sk: namespace, used everywhere
sk:name, sk:description, sk:version, sk:createdDate
```

**Domain-specific properties:**
```turtle
# Only meaningful in their domain
cli:hasArgument, cli:exitCode
jtbd:hasOutcome, jtbd:circumstance
docs:wordCount, docs:audience
```

**Cross-domain bridges:**
```turtle
# Explicit links between domains
cli:accomplishesJob    # cli → jtbd
cli:documentedIn       # cli → docs
jtbd:measuredBy        # jtbd → otel
```
