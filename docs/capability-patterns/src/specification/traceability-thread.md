# 20. Traceability Thread

★★

*Every artifact should trace to its source. Every decision should trace to its rationale. Traceability threads connect the web of specifications, enabling impact analysis and provenance tracking.*

---

Your system now has many artifacts:
- Customer jobs and outcomes
- Formal specifications
- Acceptance criteria
- Generated code
- Documentation
- Tests

These artifacts relate to each other. A test validates an acceptance criterion. The criterion addresses an outcome. The outcome belongs to a job. The job exists in a circumstance.

Without explicit traceability, these relationships are implicit—known to the person who created them, forgotten by everyone else. When something changes, impact is unclear. When something fails, root cause is obscure.

**The problem: Implicit relationships become lost knowledge. Changes have hidden impacts. Failures have unknown causes.**

---

**The forces at play:**

- *Completeness wants full traceability.* Every connection documented.

- *Effort wants efficiency.* Maintaining traceability has cost.

- *Automation wants machine-readable links.* Human-only traceability doesn't scale.

- *Understanding wants navigability.* Traces must be followable.

The tension: comprehensive traceability versus practical maintenance.

---

**Therefore:**

Create explicit traceability links in RDF, forming threads that connect related artifacts across all levels.

**Core traceability properties:**

```turtle
# Forward links
sk:addresses rdf:Property ;
    rdfs:comment "Links implementation to requirement" .

sk:satisfies rdf:Property ;
    rdfs:comment "Links test to acceptance criterion" .

sk:accomplishes rdf:Property ;
    rdfs:comment "Links capability to job" .

sk:delivers rdf:Property ;
    rdfs:comment "Links feature to outcome" .

sk:generatedFrom rdf:Property ;
    rdfs:comment "Links artifact to source specification" .

# Inverse links (computed or explicit)
sk:addressedBy owl:inverseOf sk:addresses .
sk:satisfiedBy owl:inverseOf sk:satisfies .
sk:accomplishedBy owl:inverseOf sk:accomplishes .
sk:deliveredBy owl:inverseOf sk:delivers .
sk:generates owl:inverseOf sk:generatedFrom .
```

**The traceability thread:**

```
Customer Need
    │
    ▼ [jtbd:hasJob]
Job To Be Done
    │
    ▼ [jtbd:hasOutcome]
Desired Outcome
    │
    ▼ [sk:addressedBy]
Acceptance Criterion
    │
    ▼ [sk:satisfiedBy]
Test Case
    │
    ▼ [sk:validates]
Generated Code
    │
    ▼ [sk:generatedFrom]
Specification (RDF)
```

**Example thread:**

```turtle
# The thread from need to implementation

jtbd:PreCommitValidation jtbd:hasJob jtbd:ValidateOntologyJob .

jtbd:ValidateOntologyJob jtbd:hasOutcome jtbd:MinimizeValidationTime .

jtbd:MinimizeValidationTime sk:addressedBy sk:AC_VAL_001 .

sk:AC_VAL_001 sk:satisfiedBy test:test_validate_valid_file .

test:test_validate_valid_file sk:validates cli:ValidateCommand .

cli:ValidateCommand sk:generatedFrom <ontology/cli-commands.ttl#ValidateCommand> .
```

**Impact analysis queries:**

```sparql
# What tests are affected if this outcome changes?
SELECT ?test WHERE {
    jtbd:MinimizeValidationTime sk:addressedBy ?criterion .
    ?criterion sk:satisfiedBy ?test .
}
```

```sparql
# What outcomes does this command affect?
SELECT ?outcome WHERE {
    cli:ValidateCommand sk:accomplishes/jtbd:hasOutcome ?outcome .
}
```

```sparql
# What is the full traceability thread for this test?
SELECT ?job ?outcome ?criterion ?command WHERE {
    test:test_validate_valid_file sk:satisfies ?criterion .
    ?criterion sk:addresses ?outcome .
    ?outcome ^jtbd:hasOutcome ?job .
    test:test_validate_valid_file sk:validates ?command .
}
```

**Provenance tracking:**

```turtle
# Link generated artifact to its source
<src/commands/validate.py>
    sk:generatedFrom <ontology/cli-commands.ttl> ;
    sk:generatedAt "2025-01-15T10:30:00Z"^^xsd:dateTime ;
    sk:generatedBy <ggen:v5.0.2> ;
    sk:sourceHash "a1b2c3d4..."^^xsd:string ;
    sk:artifactHash "e5f6g7h8..."^^xsd:string .
```

---

**Resulting context:**

After applying this pattern, you have:

- Explicit links connecting all artifacts
- Ability to perform impact analysis before changes
- Provenance tracking for generated artifacts
- Navigable threads from need to implementation

This completes the Specification Patterns and prepares for **[Part III: Transformation Patterns](../transformation/constitutional-equation.md)**.

---

**Related patterns:**

- *Links:* **[5. Outcome Desired](../context/outcome-desired.md)** ↔ **[19. Acceptance Criterion](./acceptance-criterion.md)**
- *Links:* **[19. Acceptance Criterion](./acceptance-criterion.md)** ↔ **[31. Test Before Code](../verification/test-before-code.md)**
- *Enables:* **[26. Receipt Generation](../transformation/receipt-generation.md)** — Receipts are traces
- *Supports:* **[35. Drift Detection](../verification/drift-detection.md)** — Detect broken traces

---

> *"You can't manage what you can't trace."*

Traceability threads make the implicit explicit, enabling understanding, impact analysis, and confident change.

---

## Transition to Part III

You've completed the Specification Patterns. You know how to:
- Establish a **[Semantic Foundation](./semantic-foundation.md)** with RDF
- Create a **[Single Source of Truth](./single-source-of-truth.md)**
- Make specifications **[Executable](./executable-specification.md)**
- Define **[Shape Constraints](./shape-constraint.md)** for validation
- Organize with **[Vocabulary Boundaries](./vocabulary-boundary.md)** and **[Layered Ontologies](./layered-ontology.md)**
- Add **[Narrative](./narrative-specification.md)** context
- Define **[Acceptance Criteria](./acceptance-criterion.md)**
- Create **[Traceability Threads](./traceability-thread.md)**

Now it's time to transform these specifications into artifacts. Turn to **[Part III: Transformation Patterns](../transformation/constitutional-equation.md)** to learn the art of faithful generation.
