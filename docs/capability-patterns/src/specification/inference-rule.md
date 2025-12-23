# 15. Inference Rule

★

*Not all knowledge needs to be explicitly stated. Inference rules derive new facts from existing ones, keeping specifications DRY while enabling rich querying.*

---

Your specifications contain explicit knowledge: "Command X has argument Y." But they also imply knowledge that isn't stated: "Command X has at least one required argument" (implied by the arguments' properties).

Without inference, you must either:
1. State everything explicitly (verbose, error-prone, hard to maintain)
2. Compute derived facts in application code (logic scattered, hard to query)

Inference rules offer a third path: declare the rules by which new facts derive from existing facts. The reasoner computes implications automatically.

**The problem: Explicitly stating all facts is verbose and error-prone. Computing derived facts in code scatters logic and prevents querying derived knowledge.**

---

**The forces at play:**

- *Completeness wants all facts stated.* Queries work best with explicit data.

- *DRY wants minimal redundancy.* Redundant facts can become inconsistent.

- *Performance wants less computation.* Inference can be expensive.

- *Transparency wants visible logic.* Inference can make behavior mysterious.

The tension: infer enough to reduce redundancy, but not so much that behavior becomes opaque.

---

**Therefore:**

Use RDFS and OWL inference rules judiciously, and supplement with SPARQL CONSTRUCT rules for domain-specific inference.

**Built-in RDFS inference:**

```turtle
# Class hierarchy
cli:ValidateCommand a cli:Command .
cli:Command rdfs:subClassOf sk:CLIElement .

# Inferred: cli:ValidateCommand a sk:CLIElement .
```

```turtle
# Property domains and ranges
cli:hasArgument rdfs:domain cli:Command .
cli:hasArgument rdfs:range cli:Argument .

cli:ValidateCommand cli:hasArgument cli:FileArg .

# Inferred: cli:ValidateCommand a cli:Command .
# Inferred: cli:FileArg a cli:Argument .
```

**OWL inference (use sparingly):**

```turtle
# Inverse properties
cli:argumentOf owl:inverseOf cli:hasArgument .

cli:ValidateCommand cli:hasArgument cli:FileArg .
# Inferred: cli:FileArg cli:argumentOf cli:ValidateCommand .
```

```turtle
# Transitive properties
rdfs:subClassOf a owl:TransitiveProperty .

cli:Command rdfs:subClassOf sk:CLIElement .
sk:CLIElement rdfs:subClassOf sk:Entity .
# Inferred: cli:Command rdfs:subClassOf sk:Entity .
```

**SPARQL CONSTRUCT for domain rules:**

When built-in inference isn't enough, use SPARQL CONSTRUCT:

```sparql
# Rule: Commands with all optional arguments are "relaxed"
CONSTRUCT {
    ?cmd cli:strictness "relaxed" .
}
WHERE {
    ?cmd a cli:Command .
    FILTER NOT EXISTS {
        ?cmd cli:hasArgument ?arg .
        ?arg cli:required true .
    }
}
```

```sparql
# Rule: Jobs with high-importance, low-satisfaction outcomes are "opportunity"
CONSTRUCT {
    ?job jtbd:status "opportunity" .
}
WHERE {
    ?job a jtbd:Job ;
         jtbd:hasOutcome ?outcome .
    ?outcome jtbd:importance "high" ;
             jtbd:satisfaction "low" .
}
```

**Inference layering:**

```
Layer 1: Explicit facts (stated in .ttl files)
    │
    ▼
Layer 2: RDFS inference (class/property hierarchies)
    │
    ▼
Layer 3: OWL inference (inverses, transitivity)
    │
    ▼
Layer 4: SPARQL rules (domain-specific derivations)
    │
    ▼
Complete knowledge base (for querying)
```

---

**Resulting context:**

After applying this pattern, you have:

- Reduced redundancy in explicit specifications
- Rich derived facts available for querying
- Clear separation of explicit and derived knowledge
- Maintainable inference rules

This supports **[Executable Specification](./executable-specification.md)** and enhances **[Extraction Query](../transformation/extraction-query.md)**.

---

**Related patterns:**

- *Enhances:* **[11. Executable Specification](./executable-specification.md)** — Inference executes rules
- *Supports:* **[23. Extraction Query](../transformation/extraction-query.md)** — Queries see inferred facts
- *Leverages:* **[16. Layered Ontology](./layered-ontology.md)** — Inference respects layers

---

> *"The best code is no code at all."*
>
> — Jeff Atwood

The best facts are the ones you don't have to state—because they're derived.

---

**Inference hygiene:**

1. **Document rules:** Each rule should have rdfs:comment explaining its purpose
2. **Test inference:** Verify derived facts are correct
3. **Limit depth:** Deep inference chains are hard to debug
4. **Make derivation visible:** Consider adding provenance to inferred facts
5. **Profile performance:** Inference can be expensive—measure impact

---

**When not to infer:**

Some knowledge should be explicit:
- Security-sensitive facts (don't infer permissions)
- Facts that might be wrong (explicit is safer)
- Facts users need to see and understand (transparency)

Inference is powerful but not free. Use it for patterns that genuinely reduce maintenance burden and improve query expressiveness.
